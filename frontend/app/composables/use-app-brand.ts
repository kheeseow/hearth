import type { AppBrand } from "~/lib/api/types/admin";
import { defaultAppBrand } from "~/lib/app-brand";

export function useAppBrand() {
  const { $appInfo } = useNuxtApp();

  return computed<AppBrand>(() => $appInfo.brand ?? defaultAppBrand);
}
