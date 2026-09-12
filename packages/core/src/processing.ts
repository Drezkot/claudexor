import { ProcessingReceipt, ProcessingCostBasis } from "@claudexor/schema";
import type {
  HarnessAdapter,
  HarnessProcessingSpec,
  PreparedHarnessProcessing,
} from "./adapter.js";

/** Shared fallback for adapters without service controls. Never changes model,
 * effort, credential route, or output policy. Native observations stay unknown. */
export async function prepareHarnessProcessing(
  adapter: HarnessAdapter,
  spec: HarnessProcessingSpec,
): Promise<PreparedHarnessProcessing> {
  const prepared = adapter.prepareProcessing
    ? await adapter.prepareProcessing(spec)
    : {
        model: spec.model,
        receipt: {
          requested: spec.preference,
          submitted: null,
          submittedNative: null,
          observed: "unknown" as const,
          observedNative: [],
          reason: "processing_control_unavailable",
          source: "adapter-capability",
        },
        costBasis: { nativeMode: null, kind: "unknown" as const, source: "adapter-capability" },
      };
  const receipt = ProcessingReceipt.parse(prepared.receipt);
  return {
    model: prepared.model,
    receipt,
    costBasis: ProcessingCostBasis.parse(prepared.costBasis),
  };
}
