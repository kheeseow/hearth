<template>
  <v-container class="lg-container guide-library-page">
    <header class="guide-library-header mb-6 mb-sm-8">
      <div class="guide-library-heading">
        <h1 class="guide-library-title">
          {{ $t("guide.find-guide") }}
        </h1>
        <p class="guide-library-intro text-medium-emphasis mb-0">
          {{ $t("guide.find-guide-description") }}
        </p>
      </div>

      <div class="guide-library-actions">
        <v-btn
          color="primary"
          variant="flat"
          :prepend-icon="$globals.icons.createAlt"
          :to="`/g/${groupSlug}/guides/create`"
        >
          {{ $t("guide.new-guide") }}
        </v-btn>
        <v-btn
          variant="outlined"
          :prepend-icon="$globals.icons.download"
          :aria-label="$t('guide.export-guides')"
          :loading="exporting"
          :disabled="loading || !guides.length"
          @click="exportGuides"
        >
          {{ $t("guide.export") }}
        </v-btn>
      </div>
    </header>

    <v-sheet
      class="guide-search-surface pa-3 pa-sm-4 mb-4"
      rounded="lg"
      :aria-busy="loading"
    >
      <v-form class="guide-search-form" role="search" @submit.prevent="applyCriteria">
        <v-text-field
          v-model="search"
          :label="$t('guide.search')"
          :placeholder="$t('guide.search-placeholder')"
          :prepend-inner-icon="$globals.icons.search"
          variant="outlined"
          bg-color="surface"
          clearable
          hide-details
          @click:clear="clearSearch"
        />
        <v-btn type="submit" color="primary" size="large" :loading="loading">
          {{ $t("search.search") }}
        </v-btn>
      </v-form>

      <div class="guide-search-feedback mt-3" aria-live="polite">
        <v-alert v-if="error" type="error" variant="tonal" density="compact">
          {{ error }}
          <template #append>
            <v-btn variant="text" size="small" @click="loadGuides">
              {{ $t("general.retry") }}
            </v-btn>
          </template>
        </v-alert>
        <div v-else-if="loading" class="d-flex align-center ga-2 text-body-2 text-medium-emphasis" role="status">
          <v-progress-circular indeterminate color="primary" size="18" width="2" />
          <span>{{ $t("guide.loading-guides") }}</span>
        </div>
        <p v-else class="text-body-2 text-medium-emphasis mb-0" role="status">
          {{ $t("guide.results-count", guides.length) }}
        </p>
      </div>
    </v-sheet>

    <section aria-labelledby="guide-library-heading" :aria-busy="loading">
      <div class="guide-library-toolbar mb-3">
        <div>
          <h2 id="guide-library-heading" class="text-h6 font-weight-bold mb-0">
            {{ $t("guide.browse-library") }}
          </h2>
          <p class="text-body-2 text-medium-emphasis mb-0 d-none d-sm-block">
            {{ $t("guide.page-description") }}
          </p>
        </div>

        <details ref="filtersDisclosure" class="guide-filter-disclosure" @toggle="handleFilterToggle">
          <summary role="button" :aria-label="filterButtonLabel">
            <v-icon size="20" aria-hidden="true">
              {{ $globals.icons.filter }}
            </v-icon>
            {{ $t("guide.filters") }}
            <span v-if="advancedFilterCount" class="guide-filter-count">
              {{ advancedFilterCount }}
            </span>
          </summary>
          <v-card class="guide-filter-panel pa-4" rounded="lg">
            <div class="d-flex align-center justify-space-between ga-4 mb-4">
              <h3 class="text-subtitle-1 font-weight-bold mb-0">
                {{ $t("guide.filters") }}
              </h3>
              <v-btn
                v-if="advancedFilterCount"
                variant="text"
                size="small"
                @click="clearAdvancedFilters"
              >
                {{ $t("guide.clear-filters") }}
              </v-btn>
            </div>

            <v-row density="compact">
              <v-col cols="12" sm="6">
                <v-select
                  v-model="draftGuideType"
                  :label="$t('guide.type')"
                  :items="guideTypeItems"
                  variant="outlined"
                  clearable
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="draftDifficulty"
                  :label="$t('guide.difficulty')"
                  :items="difficultyItems"
                  variant="outlined"
                  clearable
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="draftFrequency"
                  :label="$t('guide.frequency')"
                  :items="frequencyItems"
                  variant="outlined"
                  clearable
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="draftCategory"
                  :label="$t('guide.category')"
                  variant="outlined"
                  clearable
                  hide-details
                  @keyup.enter="applyFiltersAndClose"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="draftTag"
                  :label="$t('guide.tag')"
                  variant="outlined"
                  clearable
                  hide-details
                  @keyup.enter="applyFiltersAndClose"
                />
              </v-col>
            </v-row>

            <div class="d-flex justify-end mt-4">
              <v-btn color="primary" variant="flat" @click="applyFiltersAndClose">
                {{ $t("general.done") }}
              </v-btn>
            </div>
          </v-card>
        </details>
      </div>

      <div
        v-if="activeFilters.length"
        class="guide-active-filters mb-5"
        :aria-label="$t('guide.active-filters')"
      >
        <v-chip
          v-for="filter in activeFilters"
          :key="filter.key"
          color="primary"
          variant="tonal"
        >
          <span class="font-weight-medium">{{ filter.label }}:</span>&nbsp;{{ filter.value }}
          <v-btn
            class="ml-1"
            icon
            size="x-small"
            variant="text"
            :aria-label="$t('guide.remove-filter', { filter: filter.label, value: filter.value })"
            @click.stop="removeFilter(filter.key)"
          >
            <v-icon size="16">
              {{ $globals.icons.close }}
            </v-icon>
          </v-btn>
        </v-chip>
      </div>

      <v-row v-if="guides.length" class="guide-grid" role="list">
        <v-col
          v-for="guide in guides"
          :key="guide.id"
          cols="12"
          sm="6"
          lg="4"
          role="listitem"
        >
          <GuideCard :guide="guide" :to="`/g/${groupSlug}/guides/${guide.slug}`" />
        </v-col>
      </v-row>

      <v-empty-state
        v-else-if="!loading && !error"
        class="guide-empty-state"
        :title="hasCriteria ? $t('guide.no-matching-guides') : $t('guide.no-guides')"
        :text="hasCriteria ? $t('guide.no-matching-guides-description') : $t('guide.no-guides-description')"
        :icon="$globals.icons.book"
      >
        <template v-if="hasCriteria" #actions>
          <v-btn color="primary" variant="tonal" @click="clearCriteria">
            {{ $t("guide.clear-filters") }}
          </v-btn>
        </template>
        <template v-else #actions>
          <v-btn color="primary" :to="`/g/${groupSlug}/guides/create`">
            {{ $t("guide.new-guide") }}
          </v-btn>
        </template>
      </v-empty-state>
    </section>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import GuideCard from "~/components/Domain/Guide/GuideCard.vue";
import type { GuideSummary, GuideDifficulty, GuideFrequency, GuideType } from "~/lib/api/types/guide";
import {
  createLatestGuideRequest,
  emptyGuideLibraryFilters,
  guideLibraryAdvancedFilterCount,
  guideLibraryCanonicalQuery,
  guideLibraryFiltersFromQuery,
  guideLibraryHasCriteria,
  guideLibraryQueryWithExistingState,
  type GuideLibraryFilters,
} from "~/lib/guide-library";
import { alert } from "~/composables/use-toast";

definePageMeta({ middleware: ["group-only"] });

type AdvancedFilterKey = Exclude<keyof GuideLibraryFilters, "search">;

const i18n = useI18n();
useSeoMeta({ title: i18n.t("guide.guides") });

const route = useRoute();
const router = useRouter();
const groupSlug = computed(() => route.params.groupSlug as string);
const api = useUserApi();
const search = ref("");
const guideType = ref<GuideType | null>(null);
const difficulty = ref<GuideDifficulty | null>(null);
const frequency = ref<GuideFrequency | null>(null);
const category = ref("");
const tag = ref("");
const draftGuideType = ref<GuideType | null>(null);
const draftDifficulty = ref<GuideDifficulty | null>(null);
const draftFrequency = ref<GuideFrequency | null>(null);
const draftCategory = ref("");
const draftTag = ref("");
const guides = ref<GuideSummary[]>([]);
const loading = ref(false);
const exporting = ref(false);
const error = ref("");
const filtersDisclosure = ref<HTMLDetailsElement | null>(null);
const runLatestGuideRequest = createLatestGuideRequest();

const filters = computed<GuideLibraryFilters>(() => ({
  search: search.value,
  guideType: guideType.value,
  difficulty: difficulty.value,
  frequency: frequency.value,
  category: category.value,
  tag: tag.value,
}));
const advancedFilterCount = computed(() => guideLibraryAdvancedFilterCount(filters.value));
const hasCriteria = computed(() => guideLibraryHasCriteria(filters.value));
const filterButtonLabel = computed(() => advancedFilterCount.value
  ? i18n.t("guide.filters-active", { count: advancedFilterCount.value })
  : i18n.t("guide.filters"));
const guideTypeItems = computed(() => [
  { title: i18n.t("guide.types.cleaning"), value: "cleaning" },
  { title: i18n.t("guide.types.maintenance"), value: "maintenance" },
  { title: i18n.t("guide.types.setup"), value: "setup" },
  { title: i18n.t("guide.types.emergency"), value: "emergency" },
  { title: i18n.t("guide.types.troubleshooting"), value: "troubleshooting" },
  { title: i18n.t("guide.types.care-instructions"), value: "care_instructions" },
]);
const difficultyItems = computed(() => [
  { title: i18n.t("guide.difficulties.beginner"), value: "beginner" },
  { title: i18n.t("guide.difficulties.intermediate"), value: "intermediate" },
  { title: i18n.t("guide.difficulties.advanced"), value: "advanced" },
]);
const frequencyItems = computed(() => [
  { title: i18n.t("guide.frequencies.one-time"), value: "one_time" },
  { title: i18n.t("guide.frequencies.weekly"), value: "weekly" },
  { title: i18n.t("guide.frequencies.monthly"), value: "monthly" },
  { title: i18n.t("guide.frequencies.yearly"), value: "yearly" },
  { title: i18n.t("guide.frequencies.as-needed"), value: "as_needed" },
]);
const activeFilters = computed(() => {
  const values: { key: AdvancedFilterKey; label: string; value: string }[] = [];
  const typeLabel = guideTypeItems.value.find(item => item.value === guideType.value)?.title;
  const difficultyLabel = difficultyItems.value.find(item => item.value === difficulty.value)?.title;
  const frequencyLabel = frequencyItems.value.find(item => item.value === frequency.value)?.title;

  if (typeLabel) values.push({ key: "guideType", label: i18n.t("guide.type"), value: typeLabel });
  if (difficultyLabel) values.push({ key: "difficulty", label: i18n.t("guide.difficulty"), value: difficultyLabel });
  if (frequencyLabel) values.push({ key: "frequency", label: i18n.t("guide.frequency"), value: frequencyLabel });
  if (category.value.trim()) values.push({ key: "category", label: i18n.t("guide.category"), value: category.value.trim() });
  if (tag.value.trim()) values.push({ key: "tag", label: i18n.t("guide.tag"), value: tag.value.trim() });
  return values;
});

function setFilters(next: GuideLibraryFilters) {
  search.value = next.search;
  guideType.value = next.guideType;
  difficulty.value = next.difficulty;
  frequency.value = next.frequency;
  category.value = next.category;
  tag.value = next.tag;
  resetFilterDraft();
}

function resetFilterDraft() {
  draftGuideType.value = guideType.value;
  draftDifficulty.value = difficulty.value;
  draftFrequency.value = frequency.value;
  draftCategory.value = category.value;
  draftTag.value = tag.value;
}

function commitFilterDraft() {
  guideType.value = draftGuideType.value;
  difficulty.value = draftDifficulty.value;
  frequency.value = draftFrequency.value;
  category.value = draftCategory.value;
  tag.value = draftTag.value;
}

async function loadGuides() {
  loading.value = true;
  error.value = "";
  const criteria = { ...filters.value };
  const response = await runLatestGuideRequest(() => api.guides.getAll(1, -1, {
    search: criteria.search.trim() || undefined,
    guideType: criteria.guideType || undefined,
    difficulty: criteria.difficulty || undefined,
    frequency: criteria.frequency || undefined,
    category: criteria.category.trim() || undefined,
    tag: criteria.tag.trim() || undefined,
  }));
  if (!response) return;

  if (response.data && !response.error) {
    guides.value = response.data.items;
  }
  else {
    guides.value = [];
    error.value = i18n.t("guide.load-error");
  }
  loading.value = false;
}

function sameQuery(left: Record<string, string>, right: Record<string, string>) {
  const entries = (query: Record<string, string>) => Object.entries(query).sort(([leftKey], [rightKey]) => leftKey.localeCompare(rightKey));
  return JSON.stringify(entries(left)) === JSON.stringify(entries(right));
}

function queryStrings(query: Record<string, unknown>): Record<string, string> {
  const values: Record<string, string> = {};
  for (const [key, value] of Object.entries(query)) {
    const candidate = Array.isArray(value) ? value[0] : value;
    if (typeof candidate === "string" && candidate.trim()) values[key] = candidate.trim();
  }
  return values;
}

function applyCriteria() {
  const nextQuery = guideLibraryQueryWithExistingState(filters.value, route.query as Record<string, unknown>);
  const currentQuery = queryStrings(route.query as Record<string, unknown>);
  if (sameQuery(nextQuery, currentQuery)) {
    void loadGuides();
    return;
  }

  void router.replace({ query: nextQuery });
}

function clearSearch() {
  void nextTick(applyCriteria);
}

function clearAdvancedFilters() {
  draftGuideType.value = null;
  draftDifficulty.value = null;
  draftFrequency.value = null;
  draftCategory.value = "";
  draftTag.value = "";
  applyFiltersAndClose();
}

function clearCriteria() {
  setFilters(emptyGuideLibraryFilters());
  closeFilters();
  applyCriteria();
}

function removeFilter(key: AdvancedFilterKey) {
  if (key === "guideType") guideType.value = null;
  else if (key === "difficulty") difficulty.value = null;
  else if (key === "frequency") frequency.value = null;
  else if (key === "category") category.value = "";
  else tag.value = "";
  resetFilterDraft();
  applyCriteria();
}

function applyFiltersAndClose() {
  commitFilterDraft();
  closeFilters();
  applyCriteria();
}

function handleFilterToggle() {
  resetFilterDraft();
}

function closeFilters() {
  if (filtersDisclosure.value) {
    filtersDisclosure.value.open = false;
  }
}

async function exportGuides() {
  exporting.value = true;
  try {
    const { data } = await api.guides.exportGuides(guides.value.map(guide => guide.id));
    if (!data) {
      alert.error(i18n.t("guide.export-error"));
      return;
    }

    await api.utils.download(api.guides.exportDownloadUrl(data.id));
  }
  catch {
    alert.error(i18n.t("guide.export-error"));
  }
  finally {
    exporting.value = false;
  }
}

watch(
  () => route.query,
  (query) => {
    const routeQuery = query as Record<string, unknown>;
    const canonicalQuery = guideLibraryCanonicalQuery(routeQuery);
    if (!sameQuery(canonicalQuery, queryStrings(routeQuery))) {
      void router.replace({ query: canonicalQuery });
      return;
    }
    setFilters(guideLibraryFiltersFromQuery(routeQuery));
    void loadGuides();
  },
  { immediate: true },
);
</script>

<style scoped>
.guide-library-page {
  padding-block: 32px 64px;
}

.guide-library-header,
.guide-library-toolbar,
.guide-library-actions,
.guide-search-form,
.guide-active-filters {
  display: flex;
}

.guide-library-header {
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.guide-library-heading {
  max-width: 65ch;
}

.guide-library-title {
  max-width: 18ch;
  margin-bottom: 8px;
  font-size: clamp(2rem, 1.72rem + 1.4vw, 3rem);
  font-weight: 750;
  line-height: 1.12;
  text-wrap: balance;
}

.guide-library-intro {
  max-width: 58ch;
  font-size: 17px;
  line-height: 1.6;
}

.guide-library-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.guide-search-surface {
  border: 1px solid rgb(var(--v-theme-primary), 0.24);
  background: rgb(var(--v-theme-surface));
  box-shadow: 0 1px 2px rgb(42 31 25 / 8%);
}

.guide-search-form {
  align-items: stretch;
  gap: 12px;
}

.guide-search-form :deep(.v-btn) {
  min-width: 112px;
}

.guide-search-feedback {
  min-height: 24px;
}

.guide-library-toolbar {
  min-height: 48px;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.guide-filter-count {
  display: inline-grid;
  min-width: 20px;
  height: 20px;
  place-items: center;
  border-radius: 999px;
  background: rgb(var(--v-theme-primary), 0.14);
  font-size: 12px;
  font-weight: 700;
}

.guide-filter-disclosure {
  position: relative;
}

.guide-filter-disclosure summary {
  display: flex;
  min-height: 44px;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  border-radius: 10px;
  color: rgb(var(--v-theme-primary));
  cursor: pointer;
  font-weight: 700;
  list-style: none;
}

.guide-filter-disclosure summary::-webkit-details-marker {
  display: none;
}

.guide-filter-disclosure summary:hover {
  background: rgb(var(--v-theme-primary), 0.08);
}

.guide-filter-disclosure summary:focus-visible {
  outline: 3px solid rgb(var(--v-theme-primary));
  outline-offset: 2px;
}

.guide-filter-panel {
  box-sizing: border-box;
  position: absolute;
  top: 52px;
  right: 0;
  z-index: 10;
  width: min(560px, calc(100vw - 32px));
  max-height: calc(100dvh - 96px);
  overflow-y: auto;
  border: 1px solid rgb(var(--v-theme-on-surface), 0.16);
  box-shadow: 0 12px 28px rgb(42 31 25 / 16%);
}

.guide-active-filters {
  min-height: 36px;
  flex-wrap: wrap;
  gap: 12px;
}

.guide-grid {
  row-gap: 20px;
}

.guide-empty-state {
  margin-top: 16px;
  border: 1px dashed rgb(var(--v-theme-on-surface), 0.22);
  border-radius: 16px;
}

@media (max-width: 599px) {
  .guide-library-page {
    padding-block: 20px 96px;
  }

  .guide-library-header {
    display: block;
  }

  .guide-library-intro {
    display: none;
  }

  .guide-library-actions {
    justify-content: flex-start;
    margin-top: 16px;
  }

  .guide-search-form {
    flex-direction: column;
  }

  .guide-search-form :deep(.v-btn) {
    width: 100%;
  }
}

@media (max-width: 360px) {
  .guide-library-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .guide-filter-disclosure {
    width: 100%;
  }
}
</style>
