import type { GuideCalloutOut, GuideRead } from "~/lib/api/types/guide";

export function splitGuideCallouts(callouts?: GuideCalloutOut[] | null) {
  return {
    warnings: (callouts ?? []).filter(callout => callout.kind === "warning"),
    avoids: (callouts ?? []).filter(callout => callout.kind === "avoid"),
  };
}

export function getGuideTotalMinutes(
  guide?: Pick<GuideRead, "preparationMinutes" | "executionMinutes"> | null,
): number | null {
  if (!guide?.preparationMinutes && !guide?.executionMinutes) {
    return null;
  }

  return (guide.preparationMinutes ?? 0) + (guide.executionMinutes ?? 0);
}
