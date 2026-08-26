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
import type { GuideSummary } from "~/lib/api/types/guide";

definePageMeta({ middleware: ["group-only"] });

const i18n = useI18n();
useSeoMeta({ title: i18n.t("guide.guides") });

const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string);
const api = useUserApi();
const search = ref("");
const guides = ref<GuideSummary[]>([]);
const loading = ref(false);
const error = ref("");

async function loadGuides() {
  loading.value = true;
  error.value = "";
  const { data } = await api.guides.getAll(1, -1, { search: search.value || undefined });
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
