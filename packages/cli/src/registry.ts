import {
  hasModelInventoryForRoute,
  type AdapterRegistry,
  type HarnessAdapter,
} from "@claudexor/core";
import {
  ControlHarnessAccountModelsResponse,
  type ControlHarnessModelsResponse,
} from "@claudexor/schema";
import { HarnessGateway } from "@claudexor/gateway";
import { createAgyAdapter } from "@claudexor/harness-agy";
import { createClaudeAdapter } from "@claudexor/harness-claude";
import { createCodexAdapter } from "@claudexor/harness-codex";
import { createCursorAdapter } from "@claudexor/harness-cursor";
import { FAKE_KINDS, createFakeHarness } from "@claudexor/harness-fake";
import { createOpenCodeAdapter } from "@claudexor/harness-opencode";
import { createRawApiAdapter } from "@claudexor/harness-raw-api";
import {
  catalogProfiles,
  enumerateAccountCatalogs,
  type AccountCatalogContext,
} from "./account-catalog.js";

export interface RegistryOptions {
  /** Register the fake-harness suite (so `--harness fake-*` works). Default true. */
  includeFakes?: boolean;
}

/**
 * Build the adapter registry. All six real adapters are always registered;
 * the gateway only selects doctor-OK non-fake harnesses by default. Fakes are
 * registered for explicit `--harness`. An `openrouter` raw-API instance is the
 * direct-API path for explicitly requested auxiliary models when its key exists.
 */
export function buildRegistry(opts: RegistryOptions = {}): AdapterRegistry {
  const registry: AdapterRegistry = new Map();
  for (const adapter of [
    createCodexAdapter(),
    createAgyAdapter(),
    createClaudeAdapter(),
    createCursorAdapter(),
    createOpenCodeAdapter(),
    createRawApiAdapter(),
    createRawApiAdapter({
      id: "openrouter",
      providerFamily: "unknown",
      providerUsageCostUnit: "usd",
      baseUrl: process.env.CLAUDEXOR_OPENROUTER_BASE_URL ?? "https://openrouter.ai/api/v1",
      keyEnv: "OPENROUTER_API_KEY",
      defaultModel: process.env.CLAUDEXOR_OPENROUTER_MODEL ?? "openai/gpt-5.5",
    }),
  ]) {
    registry.set(adapter.id, adapter);
  }
  if (opts.includeFakes !== false) {
    for (const kind of FAKE_KINDS) registry.set(kind, createFakeHarness(kind));
  }
  return registry;
}

export function buildGateway(opts: RegistryOptions = {}): HarnessGateway {
  return new HarnessGateway(buildRegistry(opts));
}

/**
 * Resolve enumerable models for one harness (ADP4). The SSOT shared by the
 * control-api `harnessModels` service and the CLI `models` command, so both
 * surfaces report identical truth: `source: "api"` when the adapter has a real
 * models() producer, `"manifest"` when the manifest's known-good hint set is
 * the truth source (with the CLI version it was verified against), `"none"`
 * only when the harness has no truth source at all. Fails soft — adapter
 * models() already swallows network/auth errors and returns [].
 */
export async function harnessModels(
  harnessId: string,
  cwd: string,
  includeFakes = false,
  route?: "local_session" | "api_key",
): Promise<ControlHarnessModelsResponse> {
  const adapter = buildRegistry({ includeFakes }).get(harnessId);
  if (!adapter) {
    return { harnessId, models: [], source: "none", verifiedAgainst: null };
  }
  const manifest = await adapter.discover();
  if (
    hasModelInventoryForRoute(adapter, manifest.capabilities.model_inventory_routes, route ?? null)
  ) {
    // A live enumeration already reflects the credentials it ran under; the
    // route filter applies to manifest annotations only.
    const models = await adapter.models({
      cwd,
      ...(route
        ? { authPreference: route === "api_key" ? ("api_key" as const) : ("subscription" as const) }
        : {}),
    });
    return {
      harnessId,
      models: models.map(({ processing: _processing, ...model }) => ({
        ...model,
        routes: model.routes ?? null,
      })),
      source: "api",
      verifiedAgainst: null,
    };
  }
  const known = manifest.capabilities.known_models.filter((entry) =>
    // Route filter (one matcher shape with the governance gate): a bare string
    // is every-route; an annotated entry must include the requested route.
    typeof entry === "string" ? true : route === undefined || entry.routes.includes(route),
  );
  if (known.length === 0) {
    return { harnessId, models: [], source: "none", verifiedAgainst: null };
  }
  return {
    harnessId,
    models: known.map((entry) =>
      typeof entry === "string"
        ? { id: entry, label: null, context_window: null, routes: null }
        : { id: entry.id, label: null, context_window: null, routes: entry.routes },
    ),
    source: "manifest",
    verifiedAgainst: manifest.capabilities.known_models_verified_against,
  };
}

/** Opt-in account inventory. The legacy unscoped CLI/model list above keeps its exact contract. */
export async function harnessAccountModels(
  input: AccountCatalogContext & {
    harnessId: string;
    cwd: string;
    credentialProfileId?: string;
    route?: "local_session" | "api_key";
    registry?: AdapterRegistry;
  },
): Promise<ControlHarnessAccountModelsResponse> {
  const adapter = (input.registry ?? buildRegistry({ includeFakes: false })).get(input.harnessId);
  const profiles = catalogProfiles(input, input.harnessId, input.credentialProfileId);
  // The account view is explicitly route-scoped. Keep the durable account
  // rows separate, but do not enumerate a credential from the other route.
  // A conflicting explicit pin is a typed unavailable account rather than a
  // silent cross-route fallback.
  const routeProfiles = input.route
    ? profiles.filter(
        (profile) =>
          (profile.credential_kind === "api_key" ? "api_key" : "local_session") === input.route,
      )
    : profiles;
  if (input.route && routeProfiles.length === 0 && input.credentialProfileId) {
    throw Object.assign(
      new Error("The pinned catalog account does not support the requested route"),
      {
        code: "model_account_unavailable",
        status: 409,
        retryable: false,
      },
    );
  }
  // Discovery is host-level capability data, shared by this request's rows.
  let manifestPromise: ReturnType<HarnessAdapter["discover"]> | undefined;
  const accounts = await enumerateAccountCatalogs({
    context: input,
    adapter,
    profiles: routeProfiles,
    read: async (profile, canReadCatalog) => {
      if (!adapter) return null;
      const manifest = await (manifestPromise ??= adapter.discover());
      const route = profile.credential_kind === "api_key" ? "api_key" : "local_session";
      if (
        canReadCatalog &&
        hasModelInventoryForRoute(adapter, manifest.capabilities.model_inventory_routes, route)
      ) {
        const models = await adapter.models({ cwd: input.cwd, credentialProfile: profile });
        // The legacy array API also returns [] on transport failures; it is
        // not a receipt proving this account has an empty vendor inventory.
        if (models.length === 0) return null;
        return {
          harnessId: input.harnessId,
          credentialProfileId: profile.profile_id,
          models: models.map((model) => ({ ...model, routes: model.routes ?? null })),
          source: "api" as const,
          verifiedAgainst: null,
          // models() may reuse a provider-owned cache and carries no observation receipt.
          observedAt: null,
          provenance: "adapter_models",
        };
      }
      const known = manifest.capabilities.known_models.filter(
        (entry) => typeof entry === "string" || entry.routes.includes(route),
      );
      if (known.length === 0) return null;
      return {
        harnessId: input.harnessId,
        credentialProfileId: profile.profile_id,
        models: known.map((entry) =>
          typeof entry === "string"
            ? { id: entry, label: null, context_window: null, routes: null }
            : { id: entry.id, label: null, context_window: null, routes: entry.routes },
        ),
        source: "manifest" as const,
        verifiedAgainst: manifest.capabilities.known_models_verified_against,
        observedAt: null,
        provenance: "manifest",
      };
    },
  });
  return ControlHarnessAccountModelsResponse.parse({
    harnessId: input.harnessId,
    accounts,
    partial: accounts.some((entry) => entry.catalog === null),
  });
}
