/** The process footprint as log-line fields (`rssMb=… heapUsedMb=… externalMb=…`,
 * whole mebibytes). The daemon's retained journal set lives on its heap, so
 * the lines that already exist — the normal-admission line and every journal
 * maintenance receipt — carry it, and the memory class stays observable on
 * every install without a new mechanism. */
export function processMemoryFields(
  usage: Pick<NodeJS.MemoryUsage, "rss" | "heapUsed" | "external"> = process.memoryUsage(),
): string {
  const mb = (bytes: number) => Math.round(bytes / (1024 * 1024));
  return `rssMb=${mb(usage.rss)} heapUsedMb=${mb(usage.heapUsed)} externalMb=${mb(usage.external)}`;
}
