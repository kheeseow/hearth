import type { Activity, I18n, TranslationResult } from "~/lib/api/types/activity";
import { ActivityKey } from "~/lib/api/types/activity";
import type { AppCapabilities } from "~/lib/api/types/admin";

export const DEFAULT_ACTIVITY = "/g/home" as const;

type ActivityRegistry = {
  recipes: Activity;
  mealplanner: Activity;
  shopping_list: Activity;
};

const selectableActivities: ActivityRegistry = {
  recipes: {
    key: ActivityKey.RECIPES,
    route: groupSlug => groupSlug ? `/g/${groupSlug}` : DEFAULT_ACTIVITY,
    label: i18n => i18n.t("general.recipes"),
  },
  mealplanner: {
    key: ActivityKey.MEALPLANNER,
    route: () => "/household/mealplan/planner/view",
    label: i18n => i18n.t("meal-plan.meal-planner"),
  },
  shopping_list: {
    key: ActivityKey.SHOPPING_LIST,
    route: () => "/shopping-lists",
    label: i18n => i18n.t("shopping-list.shopping-lists"),
  },
};

export function getAvailableActivities(capabilities: AppCapabilities): Activity[] {
  return Object.values(selectableActivities).filter(({ key }) => {
    if (key === ActivityKey.RECIPES) return capabilities.legacyRecipes;
    if (key === ActivityKey.MEALPLANNER) return capabilities.mealPlanning;
    if (key === ActivityKey.SHOPPING_LIST) return capabilities.shoppingLists;
    return false;
  });
}

export default function useDefaultActivity() {
  const capabilities = useAppCapabilities();
  const availableActivities = computed(() => getAvailableActivities(capabilities.value));
  const fallbackActivity = computed(() => availableActivities.value[0]);

  function getDefaultActivityRoute(activityKey?: ActivityKey, groupSlug?: string): string {
    const activity = availableActivities.value.find(({ key }) => key === activityKey) ?? fallbackActivity.value;
    if (activity) return activity.route(groupSlug);
    if (capabilities.value.guides && groupSlug) return `/g/${groupSlug}/guides`;
    return DEFAULT_ACTIVITY;
  }

  function getDefaultActivityLabels(i18n: I18n): TranslationResult[] {
    return availableActivities.value.map(({ label }) => label(i18n));
  }

  function getActivityKey(i18n: I18n, target: TranslationResult = ""): ActivityKey | undefined {
    return availableActivities.value.find(({ label }) => label(i18n) === target)?.key;
  }

  function getActivityLabel(i18n: I18n, target?: ActivityKey): TranslationResult {
    const activity = availableActivities.value.find(({ key }) => key === target) ?? fallbackActivity.value;
    return activity?.label(i18n) ?? "";
  }

  return {
    availableActivities,
    getDefaultActivityRoute,
    getDefaultActivityLabels,
    getActivityKey,
    getActivityLabel,
    fallbackActivity,
  };
}
