import type { AppCapabilities } from "~/lib/api/types/admin";

export const legacyCompatibleCapabilities: AppCapabilities = {
  guides: true,
  legacyRecipes: true,
  mealPlanning: true,
  shoppingLists: true,
  nutrition: true,
};

export function useAppCapabilities() {
  const { $appInfo } = useNuxtApp();

  return computed<AppCapabilities>(() => $appInfo.capabilities ?? legacyCompatibleCapabilities);
}
