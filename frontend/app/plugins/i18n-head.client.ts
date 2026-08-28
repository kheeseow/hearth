import { getLocaleDirection } from "~/lib/locale-head";

export default defineNuxtPlugin((nuxtApp) => {
  const locale = computed(() => nuxtApp.$i18n.locale.value);
  const direction = computed(() => getLocaleDirection(locale.value));

  useHead(() => ({
    htmlAttrs: {
      dir: direction.value,
      lang: locale.value,
    },
  }));
});
