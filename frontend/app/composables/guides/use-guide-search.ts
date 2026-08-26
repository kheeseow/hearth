import { watchDebounced } from "@vueuse/core";
import type { UserApi } from "~/lib/api";
import type { GuideSummary } from "~/lib/api/types/guide";

export function useGuideSearch(api: UserApi) {
  const query = ref("");
  const error = ref("");
  const loading = ref(false);
  const guides = ref<GuideSummary[]>([]);

  async function searchGuides(term: string) {
    loading.value = true;
    error.value = "";
    const result = await api.guides.getAll(1, 20, {
      search: term || undefined,
      orderBy: "title",
      orderDirection: "asc",
    });

    if (result.error || !result.data) {
      error.value = "guide.load-error";
      guides.value = [];
    }
    else {
      guides.value = result.data.items;
    }
    loading.value = false;
  }

  watchDebounced(query, searchGuides, { debounce: 300 });

  return {
    query,
    error,
    loading,
    data: guides,
    trigger: () => searchGuides(query.value),
  };
}
