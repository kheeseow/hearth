export const GUIDE_REVIEW_STALE_DAYS = 365;

export type GuideReviewState = "not_reviewed" | "current" | "stale";

export function guideReviewState(lastReviewed?: string | null, now = new Date()): GuideReviewState {
  if (!lastReviewed) {
    return "not_reviewed";
  }

  const reviewedAt = new Date(`${lastReviewed}T00:00:00Z`);
  if (Number.isNaN(reviewedAt.getTime())) {
    return "not_reviewed";
  }

  const staleAfter = reviewedAt.getTime() + GUIDE_REVIEW_STALE_DAYS * 24 * 60 * 60 * 1000;
  return now.getTime() > staleAfter ? "stale" : "current";
}
