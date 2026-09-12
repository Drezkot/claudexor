import { describe, expect, it, vi } from "vitest";
import type { HarnessAdapter, HarnessModelSpec } from "@claudexor/core";
import { createFakeHarness } from "@claudexor/harness-fake";
import { CredentialProfile, GlobalConfig } from "@claudexor/schema";
import { harnessAccountModels } from "./registry.js";

function fixture() {
  const harnessId = "fake-success";
  const profiles = ["a", "b"].map((id) =>
    CredentialProfile.parse({
      profile_id: id,
      harness_id: harnessId,
      display_name: id,
      credential_kind: "config_dir_login",
      isolation_locator: `/catalog-fixture/${id}`,
    }),
  );
  const config = GlobalConfig.parse({ credential_profiles: profiles });
  const models = vi.fn(async (spec?: HarnessModelSpec) => [
    {
      id: `model-${spec?.credentialProfile?.profile_id}`,
      label: null,
      context_window: spec?.credentialProfile?.profile_id === "b" ? 1000000 : 100000,
      routes: null,
    },
  ]);
  const adapter: HarnessAdapter = {
    ...createFakeHarness(harnessId),
    models,
    probeCredentialProfile: async (profile) => ({
      profile_id: profile.profile_id,
      harness_id: harnessId,
      availability: "available",
      verification: "passed",
      verification_source: "local_store",
      last_verified_at: null,
    }),
  };
  const input = {
    harnessId,
    cwd: "/catalog-fixture",
    config,
    quota: { snapshots: [], absences: [] },
    registry: new Map([[harnessId, adapter]]),
  };
  return { input, models, adapter };
}

describe("account-scoped harness model inventory", () => {
  it("preserves each account's model facts, scopes every query, and never invents a fresh timestamp", async () => {
    const f = fixture();
    const response = await harnessAccountModels(f.input);
    expect(response.partial).toBe(false);
    expect(response.accounts.map((row) => row.catalog?.models)).toEqual([
      [{ id: "model-a", label: null, context_window: 100000, routes: null }],
      [{ id: "model-b", label: null, context_window: 1000000, routes: null }],
    ]);
    expect(
      response.accounts.every(
        (row) => row.catalog?.observedAt === null && row.catalog.provenance === "adapter_models",
      ),
    ).toBe(true);
    expect(f.models.mock.calls.map(([spec]) => spec?.credentialProfile?.profile_id)).toEqual([
      "a",
      "b",
    ]);
    f.models.mockClear();
    const pinned = await harnessAccountModels({ ...f.input, credentialProfileId: "b" });
    expect(pinned.accounts.map((row) => row.credentialProfileId)).toEqual(["b"]);
    expect(f.models).toHaveBeenCalledTimes(1);
    await expect(
      harnessAccountModels({ ...f.input, credentialProfileId: "absent" }),
    ).rejects.toMatchObject({ code: "model_account_unavailable" });
  });

  it("keeps a network failure local to its row and never calls it missing authentication", async () => {
    const f = fixture();
    const original = f.models.getMockImplementation()!;
    f.models.mockImplementation(async (spec) => {
      if (spec?.credentialProfile?.profile_id === "a") throw new Error("transport timeout");
      return original(spec);
    });
    const response = await harnessAccountModels(f.input);
    expect(response.partial).toBe(true);
    expect(response.accounts[0]).toMatchObject({
      availability: "unknown",
      catalog: null,
      problem: { code: "model_catalog_unavailable" },
    });
    expect(response.accounts[1]).toMatchObject({
      availability: "available",
      problem: null,
      catalog: { models: [{ id: "model-b" }] },
    });
  });

  it("does not promote a swallowed models error into a confirmed empty inventory", async () => {
    const f = fixture();
    f.models.mockResolvedValue([]);
    const response = await harnessAccountModels(f.input);
    expect(response.partial).toBe(true);
    expect(
      response.accounts.every(
        (row) =>
          row.catalog === null &&
          row.availability === "unknown" &&
          row.problem?.code === "model_catalog_unavailable",
      ),
    ).toBe(true);
  });

  it("retains an unavailable row with honest manifest fallback without querying its credentials", async () => {
    const f = fixture();
    const manifest = await f.adapter.discover();
    manifest.capabilities.known_models = [
      { id: "subscription-hint", routes: ["local_session"] },
      { id: "paid-hint", routes: ["api_key"] },
    ];
    manifest.capabilities.known_models_verified_against = "fixture-1";
    f.adapter.discover = async () => manifest;
    f.adapter.probeCredentialProfile = async (profile) => ({
      profile_id: profile.profile_id,
      harness_id: profile.harness_id,
      availability: "unavailable",
      verification: "failed",
      verification_source: "local_store",
      last_verified_at: null,
    });
    const response = await harnessAccountModels(f.input);
    expect(response.accounts[0]).toMatchObject({
      availability: "unavailable",
      problem: { code: "auth_unavailable" },
      catalog: {
        source: "manifest",
        observedAt: null,
        provenance: "manifest",
        verifiedAgainst: "fixture-1",
        models: [{ id: "subscription-hint" }],
      },
    });
    expect(f.models).not.toHaveBeenCalled();
  });
});
