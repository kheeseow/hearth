import { getCapabilityRedirect } from "~/lib/app-capability-routes";

export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) {
    return;
  }

  const capabilities = useAppCapabilities();
  const redirect = getCapabilityRedirect(to.path, capabilities.value);

  if (redirect && redirect !== to.path) {
    return navigateTo(redirect, { replace: true });
  }
});
