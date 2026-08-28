import axios from "axios";
import type { AppInfo } from "~/lib/api/types/admin";

export default defineNuxtPlugin({
  async setup() {
    const { data } = await axios.get<AppInfo>("/api/app/about");

    useHead({
      titleTemplate: title => title ? `${title} · ${data.brand.name}` : data.brand.name,
    });
    useSeoMeta({
      description: data.brand.description,
      ogDescription: data.brand.description,
      ogSiteName: data.brand.name,
    });

    return {
      provide: {
        appInfo: data,
      },
    };
  },
});
