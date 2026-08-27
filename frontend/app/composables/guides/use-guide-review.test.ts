import { describe, expect, it } from "vitest";
import { guideReviewState } from "./use-guide-review";

describe("guideReviewState", () => {
  const now = new Date("2026-08-27T12:00:00Z");

  it("identifies guides that have never been reviewed", () => {
    expect(guideReviewState(null, now)).toBe("not_reviewed");
  });

  it("keeps a review current for one year", () => {
    expect(guideReviewState("2025-08-28", now)).toBe("current");
  });

  it("marks older reviews as stale", () => {
    expect(guideReviewState("2025-08-26", now)).toBe("stale");
  });
});
