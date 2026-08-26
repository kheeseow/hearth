<template>
  <v-container class="lg-container">
    <BasePageTitle divider>
      <template #title>
        {{ $t("guide.guides") }}
      </template>
      {{ $t("guide.page-description") }}
    </BasePageTitle>

    <div class="d-flex flex-column flex-sm-row ga-3 my-6">
      <v-text-field
        v-model="search"
        :label="$t('guide.search')"
        :prepend-inner-icon="$globals.icons.search"
        variant="outlined"
        clearable
        hide-details
        @keyup.enter="loadGuides"
        @click:clear="loadGuides"
      />
      <v-btn color="primary" size="large" :loading="loading" @click="loadGuides">
        {{ $t("search.search") }}
      </v-btn>
      <v-btn
        color="primary"
        size="large"
        variant="outlined"
        :prepend-icon="$globals.icons.create"
        :to="`/g/${groupSlug}/guides/create`"
      >
        {{ $t("guide.new-guide") }}
      </v-btn>
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
    </v-alert>
    <v-row v-if="guides.length">
      <v-col v-for="guide in guides" :key="guide.id" cols="12" sm="6" lg="4">
        <GuideCard :guide="guide" :to="`/g/${groupSlug}/guides/${guide.slug}`" />
      </v-col>
    </v-row>
    <v-empty-state
      v-else-if="!loading && !error"
      :title="$t('guide.no-guides')"
      :text="$t('guide.no-guides-description')"
      :icon="$globals.icons.book"
    />
    <div v-else class="d-flex justify-center py-12">
      <v-progress-circular indeterminate color="primary" />
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import GuideCard from "~/components/Domain/Guide/GuideCard.vue";
import type { GuideSummary, GuideDifficulty, GuideFrequency, GuideType } from "~/lib/api/types/guide";

definePageMeta({ middleware: ["group-only"] });

const i18n = useI18n();
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
const error = ref("");
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
    error.value = i18n.t("guide.load-error");
  }
  loading.value = false;
}

onMounted(loadGuides);
</script>
