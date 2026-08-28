<template>
  <v-dialog
    v-model="dialog"
    max-width="988px"
    content-class="top-dialog"
    :scrollable="false"
    :aria-label="$t('guide.search')"
  >
    <v-card :rounded="!$vuetify.display.xs" :loading="search.loading.value" :aria-busy="search.loading.value">
      <v-toolbar color="primary-lighten-1">
        <v-text-field
          id="guide-arrow-search"
          v-model="search.query.value"
          autofocus
          variant="solo"
          flat
          autocomplete="off"
          bg-color="primary-lighten-1"
          color="white"
          density="compact"
          class="mx-2 arrow-search"
          hide-details
          single-line
          :placeholder="$t('guide.search')"
          :aria-label="$t('guide.search')"
          aria-controls="guide-search-results"
          :prepend-inner-icon="$globals.icons.search"
        />
        <v-btn
          v-if="$vuetify.display.xs"
          icon
          size="x-small"
          :aria-label="$t('general.close')"
          @click="close"
        >
          <v-icon>{{ $globals.icons.close }}</v-icon>
        </v-btn>
      </v-toolbar>

      <v-card-actions aria-live="polite">
        <div class="mr-auto" role="status">
          {{ search.loading.value
            ? $t("guide.loading-guides")
            : $t("guide.results-count", search.data.value.length) }}
        </div>
      </v-card-actions>

      <v-alert v-if="search.error.value" type="error" variant="tonal" class="ma-3">
        {{ $t(search.error.value) }}
      </v-alert>
      <v-list v-else id="guide-search-results" class="guide-search-results pa-1">
        <v-list-item
          v-for="guide in search.data.value"
          :key="guide.id"
          :to="`/g/${groupSlug}/guides/${guide.slug}`"
          class="ma-1 arrow-nav"
          rounded="lg"
          @click="close"
        >
          <template #prepend>
            <v-avatar color="primary" variant="tonal" rounded="lg">
              <v-icon>{{ $globals.icons.book }}</v-icon>
            </v-avatar>
          </template>
          <v-list-item-title>{{ guide.title }}</v-list-item-title>
          <v-list-item-subtitle v-if="guide.description">
            {{ guide.description }}
          </v-list-item-subtitle>
        </v-list-item>
        <v-list-item v-if="!search.loading.value && !search.data.value.length" role="status">
          <v-list-item-title class="text-medium-emphasis">
            {{ $t("search.no-results") }}
          </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { useGuideSearch } from "~/composables/guides/use-guide-search";

const auth = useMealieAuth();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const dialog = ref(false);
const search = useGuideSearch(useUserApi());

watch(dialog, (isOpen) => {
  if (isOpen) {
    search.trigger();
  }
  else {
    search.query.value = "";
    search.data.value = [];
  }
});

watch(route, close);

function open() {
  dialog.value = true;
}

function close() {
  dialog.value = false;
}

defineExpose({ open, close });
</script>

<style scoped>
.guide-search-results {
  max-height: 700px;
  overflow-y: auto;
}
</style>
