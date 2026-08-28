import { describe, expect, test } from "vitest";
import {
  createLatestGuideRequest,
  emptyGuideLibraryFilters,
  guideLibraryAdvancedFilterCount,
  guideLibraryCanonicalQuery,
  guideLibraryFiltersFromQuery,
  guideLibraryHasCriteria,
  guideLibraryQuery,
} from "~/lib/guide-library";

describe("Guide library filters", () => {
  test("restores a valid shared search from the URL", () => {
    expect(guideLibraryFiltersFromQuery({
      search: "router reset",
      type: "troubleshooting",
      difficulty: "beginner",
      frequency: "as_needed",
      category: "Technology & Setup",
      tag: "wifi",
    })).toEqual({
      search: "router reset",
      guideType: "troubleshooting",
      difficulty: "beginner",
      frequency: "as_needed",
      category: "Technology & Setup",
      tag: "wifi",
    });
  });

  test("ignores malformed select values instead of sending them to the API", () => {
    expect(guideLibraryFiltersFromQuery({
      search: ["oil stain", "ignored"],
      type: "recipe",
      difficulty: "impossible",
      frequency: "hourly",
      category: null,
    })).toEqual({
      ...emptyGuideLibraryFilters(),
      search: "oil stain",
    });
  });

  test("removes invalid Guide criteria from the URL while preserving unrelated state", () => {
    expect(guideLibraryCanonicalQuery({
      type: "recipe",
      difficulty: "impossible",
      tab: "shared",
    })).toEqual({ tab: "shared" });
  });

  test("writes only active criteria to a stable, shareable URL", () => {
    expect(guideLibraryQuery({
      search: "  cooking oil fire  ",
      guideType: "emergency",
      difficulty: null,
      frequency: null,
      category: "",
      tag: "kitchen",
    })).toEqual({
      search: "cooking oil fire",
      type: "emergency",
      tag: "kitchen",
    });
  });

  test("counts disclosed filters separately from the main search", () => {
    const filters = {
      search: "router",
      guideType: "setup" as const,
      difficulty: "beginner" as const,
      frequency: null,
      category: "Technology",
      tag: "",
    };

    expect(guideLibraryAdvancedFilterCount(filters)).toBe(3);
    expect(guideLibraryHasCriteria(filters)).toBe(true);
    expect(guideLibraryHasCriteria(emptyGuideLibraryFilters())).toBe(false);
  });
});

describe("Guide library requests", () => {
  test("discards a slower response when a newer request finishes first", async () => {
    let finishFirst!: (value: string) => void;
    let finishSecond!: (value: string) => void;
    const first = new Promise<string>((resolve) => { finishFirst = resolve; });
    const second = new Promise<string>((resolve) => { finishSecond = resolve; });
    const runLatest = createLatestGuideRequest();

    const firstResult = runLatest(() => first);
    const secondResult = runLatest(() => second);
    finishSecond("new result");
    expect(await secondResult).toBe("new result");
    finishFirst("stale result");
    expect(await firstResult).toBeUndefined();
  });
});
