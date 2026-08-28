import type { AppCapabilities } from "~/lib/api/types/admin";

const RECIPE_PATH = /^\/g\/[^/]+\/(?:r|recipes|cookbooks)(?:\/|$)/;
const SHARED_RECIPE_PATH = /^\/g\/[^/]+\/shared\/r(?:\/|$)/;
const GROUP_HOME_PATH = /^\/g\/([^/]+)\/?$/;

export function getCapabilityRedirect(path: string, capabilities: AppCapabilities): string | undefined {
  const groupHome = path.match(GROUP_HOME_PATH);
  if (groupHome && !capabilities.legacyRecipes) {
    return `/g/${groupHome[1]}/guides`;
  }

  if (!capabilities.legacyRecipes && (RECIPE_PATH.test(path) || SHARED_RECIPE_PATH.test(path))) {
    const groupSlug = path.split("/")[2];
    return `/g/${groupSlug}/guides`;
  }

  if (!capabilities.mealPlanning && path.startsWith("/household/mealplan")) {
    return "/";
  }

  if (!capabilities.shoppingLists && path.startsWith("/shopping-lists")) {
    return "/";
  }

  if (!capabilities.legacyRecipes && /^\/user\/[^/]+\/favorites\/?$/.test(path)) {
    return "/user/profile";
  }

  return undefined;
}
