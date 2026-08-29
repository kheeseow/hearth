import { describe, expect, it } from "vitest";
import type { AppCapabilities } from "~/lib/api/types/admin";
import { getCapabilityRedirect } from "~/lib/app-capability-routes";

const freshHearth: AppCapabilities = {
  guides: true,
  legacyRecipes: false,
  mealPlanning: false,
  shoppingLists: false,
  nutrition: false,
};

describe("app capability routes", () => {
  it.each([
    ["/g/home", "/g/home/guides"],
    ["/g/home/r/create/new", "/g/home/guides"],
    ["/g/home/recipes/finder", "/g/home/guides"],
    ["/g/home/cookbooks", "/g/home/guides"],
    ["/household/mealplan/planner/view", "/"],
    ["/shopping-lists/123", "/"],
    ["/user/123/favorites", "/user/profile"],
    ["/group/data/foods", "/user/profile"],
    ["/group/migrations", "/user/profile"],
    ["/household/webhooks", "/user/profile"],
    ["/household", "/user/profile"],
    ["/admin/debug/parser", "/user/profile"],
  ])("redirects %s when its capability is disabled", (path, redirect) => {
    expect(getCapabilityRedirect(path, freshHearth)).toBe(redirect);
  });

  it("allows guide routes on a fresh Hearth installation", () => {
    expect(getCapabilityRedirect("/g/home/guides/router-reset", freshHearth)).toBeUndefined();
  });

  it("allows Guide notifier settings on a fresh Hearth installation", () => {
    expect(getCapabilityRedirect("/household/notifiers", freshHearth)).toBeUndefined();
  });

  it("keeps legacy routes available for upgraded Mealie installations", () => {
    const upgradedMealie: AppCapabilities = {
      ...freshHearth,
      legacyRecipes: true,
      mealPlanning: true,
      shoppingLists: true,
      nutrition: true,
    };

    expect(getCapabilityRedirect("/g/home", upgradedMealie)).toBeUndefined();
    expect(getCapabilityRedirect("/shopping-lists", upgradedMealie)).toBeUndefined();
    expect(getCapabilityRedirect("/group/data/foods", upgradedMealie)).toBeUndefined();
    expect(getCapabilityRedirect("/household/notifiers", upgradedMealie)).toBeUndefined();
    expect(getCapabilityRedirect("/household", upgradedMealie)).toBeUndefined();
    expect(getCapabilityRedirect("/admin/debug/parser", upgradedMealie)).toBeUndefined();
  });
});
