<template>
  <v-container class="lg-container">
    <v-sheet class="guide-library-hero pa-4 pa-sm-9 mb-7" rounded="xl">
      <div class="d-flex align-start justify-space-between ga-6 mb-7">
        <div>
          <div class="text-overline font-weight-bold mb-1">
            {{ brand.name }}
          </div>
          <h1 class="text-h4 text-sm-h2 font-weight-bold mb-3">
            {{ $t("guide.find-guide") }}
          </h1>
          <p class="text-body-1 text-sm-h6 guide-library-intro mb-0">
            {{ $t("guide.find-guide-description") }}
          </p>
        </div>
        <v-icon class="d-none d-sm-block guide-library-icon" aria-hidden="true">
          {{ $globals.icons.primary }}
        </v-icon>
      </div>

      <v-form class="d-flex flex-column flex-sm-row ga-3" role="search" @submit.prevent="loadGuides">
        <v-text-field
          v-model="search"
          :label="$t('guide.search')"
          :prepend-inner-icon="$globals.icons.search"
          variant="solo"
          bg-color="surface"
          clearable
          hide-details
          @click:clear="loadGuides"
        />
        <v-btn type="submit" color="primary" size="large" :loading="loading">
          {{ $t("search.search") }}
        </v-btn>
      </v-form>
    </v-sheet>

    <section aria-labelledby="guide-library-heading" :aria-busy="loading">
      <div class="d-flex flex-column flex-sm-row justify-space-between align-sm-center ga-3 mb-5">
        <div>
          <h2 id="guide-library-heading" class="text-h5 font-weight-bold">
            {{ $t("guide.browse-library") }}
          </h2>
          <p class="text-body-2 text-medium-emphasis mb-0">
            {{ $t("guide.page-description") }}
          </p>
        </div>
        <div class="d-flex flex-wrap ga-2">
          <v-btn
            v-if="hasActiveFilters"
            variant="text"
            @click="clearFilters"
          >
            {{ $t("guide.clear-filters") }}
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            :prepend-icon="$globals.icons.create"
            :to="`/g/${groupSlug}/guides/create`"
          >
            {{ $t("guide.new-guide") }}
          </v-btn>
          <v-btn
            color="info"
            variant="outlined"
            :prepend-icon="$globals.icons.download"
            :loading="exporting"
            :disabled="!guides.length"
            @click="exportGuides"
          >
            {{ $t("guide.export-guides") }}
          </v-btn>
        </div>
      </div>

      <v-row density="compact" class="mb-4">
        <v-col cols="12" sm="6" lg="3">
          <v-select
            v-model="guideType"
            :label="$t('guide.type')"
            :items="guideTypeItems"
            variant="outlined"
            clearable
            hide-details
            @update:model-value="loadGuides"
          />
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <v-select
            v-model="difficulty"
            :label="$t('guide.difficulty')"
            :items="difficultyItems"
            variant="outlined"
            clearable
            hide-details
            @update:model-value="loadGuides"
          />
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <v-select
            v-model="frequency"
            :label="$t('guide.frequency')"
            :items="frequencyItems"
            variant="outlined"
            clearable
            hide-details
            @update:model-value="loadGuides"
          />
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <v-text-field
            v-model="category"
            :label="$t('guide.category')"
            variant="outlined"
            clearable
            hide-details
            @keyup.enter="loadGuides"
            @click:clear="loadGuides"
          />
        </v-col>
        <v-col cols="12" sm="6" lg="3">
          <v-text-field
            v-model="tag"
            :label="$t('guide.tag')"
            variant="outlined"
            clearable
            hide-details
            @keyup.enter="loadGuides"
            @click:clear="loadGuides"
          />
        </v-col>
      </v-row>

      <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
        {{ error }}
        <template #append>
          <v-btn variant="text" @click="loadGuides">
            {{ $t("general.retry") }}
          </v-btn>
        </template>
      </v-alert>
      <p v-else-if="!loading" class="text-body-2 text-medium-emphasis mb-4" role="status" aria-live="polite">
        {{ $t("guide.results-count", guides.length) }}
      </p>
      <v-row v-if="guides.length">
        <v-col v-for="guide in guides" :key="guide.id" cols="12" sm="6" lg="4">
          <GuideCard :guide="guide" :to="`/g/${groupSlug}/guides/${guide.slug}`" />
        </v-col>
      </v-row>
      <v-empty-state
        v-else-if="!loading && !error"
        :title="hasActiveFilters ? $t('guide.no-matching-guides') : $t('guide.no-guides')"
        :text="hasActiveFilters ? $t('guide.no-matching-guides-description') : $t('guide.no-guides-description')"
        :icon="$globals.icons.book"
      />
      <div v-else-if="loading" class="d-flex justify-center py-12" role="status" aria-live="polite">
        <v-progress-circular indeterminate color="primary" :aria-label="$t('guide.loading-guides')" />
        <span class="d-sr-only">{{ $t("guide.loading-guides") }}</span>
      </div>
    </section>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import GuideCard from "~/components/Domain/Guide/GuideCard.vue";
import type { GuideSummary, GuideDifficulty, GuideFrequency, GuideType } from "~/lib/api/types/guide";
import { alert } from "~/composables/use-toast";

definePageMeta({ middleware: ["group-only"] });

const i18n = useI18n();
const brand = useAppBrand();
useSeoMeta({ title: i18n.t("guide.guides") });

const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string);
const api = useUserApi();
const search = ref("");
const guideType = ref<GuideType | null>(null);
const difficulty = ref<GuideDifficulty | null>(null);
const frequency = ref<GuideFrequency | null>(null);
const category = ref("");
const tag = ref("");
const guides = ref<GuideSummary[]>([]);
const loading = ref(false);
const exporting = ref(false);
const error = ref("");
const hasActiveFilters = computed(() => Boolean(
  search.value
  || guideType.value
  || difficulty.value
  || frequency.value
  || category.value
  || tag.value,
));
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

async function loadGuides() {
  loading.value = true;
  error.value = "";
  const { data } = await api.guides.getAll(1, -1, {
    search: search.value || undefined,
    guideType: guideType.value || undefined,
    difficulty: difficulty.value || undefined,
    frequency: frequency.value || undefined,
    category: category.value || undefined,
    tag: tag.value || undefined,
  });
  if (data) {
    guides.value = data.items;
  }
  else {
    guides.value = [];
    error.value = i18n.t("guide.load-error");
  }
  loading.value = false;
}

function clearFilters() {
  search.value = "";
  guideType.value = null;
  difficulty.value = null;
  frequency.value = null;
  category.value = "";
  tag.value = "";
  loadGuides();
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

onMounted(loadGuides);
</script>

<style scoped>
.guide-library-hero {
  background:
    radial-gradient(circle at top right, rgb(var(--v-theme-secondary), 0.28), transparent 36%),
    linear-gradient(135deg, rgb(var(--v-theme-primary), 0.16), rgb(var(--v-theme-accent), 0.12));
  border: 1px solid rgb(var(--v-theme-primary), 0.2);
}

.guide-library-intro {
  max-width: 42rem;
  line-height: 1.55;
}

.guide-library-icon {
  color: rgb(var(--v-theme-primary));
  font-size: clamp(5rem, 10vw, 8rem);
  opacity: 0.18;
}
</style>
