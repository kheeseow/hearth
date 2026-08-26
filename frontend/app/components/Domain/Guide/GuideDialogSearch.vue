<template>
  <v-dialog
    v-model="dialog"
    max-width="988px"
    content-class="top-dialog"
    :scrollable="false"
  >
    <v-card :rounded="!$vuetify.display.xs" :loading="search.loading.value">
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

      <v-card-actions>
        <div class="mr-auto">
          {{ $t("search.results") }}
        </div>
      </v-card-actions>

      <v-alert v-if="search.error.value" type="error" variant="tonal" class="ma-3">
        {{ $t(search.error.value) }}
      </v-alert>
      <v-list v-else class="guide-search-results pa-1">
        <v-list-item
          v-for="(guide, index) in search.data.value"
          :key="guide.id"
          :to="`/g/${groupSlug}/guides/${guide.slug}`"
          :tabindex="index"
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
        <v-list-item v-if="!search.loading.value && !search.data.value.length">
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
