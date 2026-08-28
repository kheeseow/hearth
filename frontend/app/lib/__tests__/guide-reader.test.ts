import { describe, expect, it } from "vitest";
import { getGuideTotalMinutes, splitGuideCallouts } from "~/lib/guide-reader";

describe("Guide reader helpers", () => {
  it("keeps warning and avoid callouts in their original order", () => {
    const warningOne = { id: "1", kind: "warning" as const, text: "Unplug the machine" };
    const avoid = { id: "2", kind: "avoid" as const, text: "Do not mix cleaners" };
    const warningTwo = { id: "3", kind: "warning" as const, text: "Wear gloves" };

    expect(splitGuideCallouts([warningOne, avoid, warningTwo])).toEqual({
      warnings: [warningOne, warningTwo],
      avoids: [avoid],
    });
  });

  it("returns no duration when neither duration was supplied", () => {
    expect(getGuideTotalMinutes({ preparationMinutes: null, executionMinutes: null })).toBeNull();
  });

  it("adds preparation and execution durations when either is supplied", () => {
    expect(getGuideTotalMinutes({ preparationMinutes: 10, executionMinutes: 35 })).toBe(45);
    expect(getGuideTotalMinutes({ preparationMinutes: null, executionMinutes: 20 })).toBe(20);
  });
});
