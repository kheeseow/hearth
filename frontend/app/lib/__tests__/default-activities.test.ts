import { describe, expect, it } from "vitest";
import type { AppCapabilities } from "~/lib/api/types/admin";
import { ActivityKey } from "~/lib/api/types/activity";
import { getAvailableActivities } from "~/composables/use-default-activity";

const freshHearth: AppCapabilities = {
  guides: true,
  legacyRecipes: false,
  mealPlanning: false,
  shoppingLists: false,
  nutrition: false,
};

describe("default activities", () => {
  it("does not offer disabled legacy activities on a fresh Hearth installation", () => {
    expect(getAvailableActivities(freshHearth)).toEqual([]);
  });

  it("preserves all Mealie activities for an upgraded installation", () => {
    const upgraded = {
      ...freshHearth,
      legacyRecipes: true,
      mealPlanning: true,
      shoppingLists: true,
      nutrition: true,
    };

    expect(getAvailableActivities(upgraded).map(activity => activity.key)).toEqual([
      ActivityKey.RECIPES,
      ActivityKey.MEALPLANNER,
      ActivityKey.SHOPPING_LIST,
    ]);
  });
});
