import type { HarnessAdapter, HarnessModelSpec, HarnessProcessingSpec } from "@claudexor/core";
import type { HarnessRunSpec } from "@claudexor/schema";
import { canonicalCodexProfileHome } from "./profile.js";
import { defaultNativeCodexHome } from "./auth.js";
import {
  codexEffortsForEnv,
  type CodexEffortProbe,
  type CodexEffortCatalog,
} from "./effort-probe.js";
import {
  prepareCodexProcessing,
  codexProcessingCost,
  codexConfiguredTier,
  legacyCodexProcessing,
} from "./processing.js";
import { tomlBasicString } from "./toml.js";
type Env = Record<string, string | null | undefined>;
export function codexProcessingMethods(
  runtime: { probeEfforts: CodexEffortProbe; nowMs: () => number },
  envFor: (env?: Env, home?: string) => Env,
): Pick<HarnessAdapter, "models" | "prepareProcessing"> {
  return {
    async models(input?: HarnessModelSpec) {
      try {
        if (
          input?.credentialProfile
            ? input.credentialProfile.credential_kind !== "config_dir_login"
            : input?.authPreference === "api_key"
        )
          return [];
        const home = input?.credentialProfile
          ? canonicalCodexProfileHome(input.credentialProfile.isolation_locator ?? "")
          : defaultNativeCodexHome(input?.env);
        const result = await codexEffortsForEnv(runtime, envFor(input?.env, home));
        // A failure snapshot is not an account observation. Retain only the
        // selected account's last live model/list answer through its own cache.
        if (!result.live) return [];
        return (
          result.catalog.nativeModels ??
          Object.keys(result.catalog.models).map((id) => ({
            id,
            label: null,
            context_window: null,
            routes: null,
            ...(result.catalog.processing?.[id]
              ? { processing: result.catalog.processing[id] }
              : {}),
          }))
        );
      } catch {
        return [];
      }
    },
    async prepareProcessing(input: HarnessProcessingSpec) {
      const native = input.credentialProfile?.credential_kind === "config_dir_login";
      const home = native
        ? canonicalCodexProfileHome(input.credentialProfile!.isolation_locator ?? "")
        : undefined;
      const env = home ? envFor(input.env, home) : undefined;
      const catalog =
        native && input.preference ? (await codexEffortsForEnv(runtime, env)).catalog : undefined;
      let receipt = input.preference
        ? prepareCodexProcessing(
            input.preference,
            catalog?.processing?.[input.model ?? catalog.defaultModel ?? ""],
          )!
        : legacyCodexProcessing(codexConfiguredTier(home));
      if (input.allowPaid === false && receipt.submitted !== "standard")
        receipt = {
          ...prepareCodexProcessing("standard")!,
          requested: input.preference ?? null,
          reason: "paid_processing_disallowed; ordinary_service_requested",
        };
      return {
        model: input.model,
        receipt,
        costBasis: codexProcessingCost(
          receipt,
          native ? true : input.credentialProfile?.credential_kind === "api_key" ? false : null,
        ),
      };
    },
  };
}
export function codexProcessingArgs(
  spec: Pick<
    HarnessRunSpec,
    "model_hint" | "processing" | "processing_preference" | "processing_allow_paid"
  >,
  catalog?: CodexEffortCatalog,
): string[] {
  const processing =
    spec.processing ??
    prepareCodexProcessing(
      spec.processing_preference,
      catalog?.processing?.[spec.model_hint ?? catalog?.defaultModel ?? ""],
      undefined,
      spec.processing_allow_paid,
    );
  return processing?.submittedNative &&
    (spec.processing_preference !== undefined ||
      processing.requested !== null ||
      spec.processing_allow_paid === false)
    ? ["-c", `service_tier=${tomlBasicString(processing.submittedNative)}`]
    : [];
}
export function applyCodexRunProcessing(
  spec: HarnessRunSpec,
  catalog: CodexEffortCatalog,
  home: string | null | undefined,
  subscription: boolean,
): HarnessRunSpec {
  const inheritedTier =
    spec.processing_preference === undefined ? codexConfiguredTier(home) : undefined;
  const processing =
    spec.processing ??
    (spec.processing_preference !== undefined || spec.processing_allow_paid === false
      ? prepareCodexProcessing(
          spec.processing_preference,
          catalog.processing?.[spec.model_hint ?? catalog.defaultModel ?? ""],
          undefined,
          spec.processing_allow_paid,
        )
      : inheritedTier
        ? legacyCodexProcessing(inheritedTier)
        : undefined);
  if (processing)
    spec = {
      ...spec,
      processing,
      processing_cost_basis:
        spec.processing_cost_basis ?? codexProcessingCost(processing, subscription),
    };
  return spec;
}
