import { LOCALES } from "~/composables/use-locales/available-locales";

export function getLocaleDirection(locale: string): "ltr" | "rtl" {
  return LOCALES.find(item => item.value === locale)?.dir === "rtl" ? "rtl" : "ltr";
}
