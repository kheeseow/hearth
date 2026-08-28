<template>
  <v-img
    v-if="source"
    :src="source"
    :alt="alt"
    :aspect-ratio="aspectRatio"
    cover
    class="guide-media-image"
  />
  <div v-else-if="loading" role="status" :aria-label="$t('general.loading')">
    <v-skeleton-loader type="image" />
    <span class="d-sr-only">{{ $t("general.loading") }}</span>
  </div>
  <div v-else class="d-flex align-center justify-center text-medium-emphasis guide-media-placeholder">
    <v-icon aria-hidden="true">
      {{ $globals.icons.fileImage }}
    </v-icon>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";

const props = withDefaults(defineProps<{
  guideSlug: string;
  version: string;
  alt?: string;
  stepId?: string;
  imageId?: string;
  size?: "original" | "small" | "tiny";
  aspectRatio?: number;
}>(), {
  alt: "",
  size: "small",
  aspectRatio: 16 / 9,
});

const api = useUserApi();
const source = ref("");
const loading = ref(false);

function releaseSource() {
  if (source.value) {
    URL.revokeObjectURL(source.value);
    source.value = "";
  }
}

async function load() {
  if (!import.meta.client || !props.version) return;
  loading.value = true;
  releaseSource();
  const response = props.stepId && props.imageId
    ? await api.guides.getStepImage(props.guideSlug, props.stepId, props.imageId, props.size)
    : await api.guides.getCoverImage(props.guideSlug, props.size);
  if (response.data) {
    source.value = URL.createObjectURL(response.data);
  }
  loading.value = false;
}

watch(
  () => [props.guideSlug, props.stepId, props.imageId, props.version, props.size],
  load,
  { immediate: true },
);
onBeforeUnmount(releaseSource);
</script>

<style scoped>
.guide-media-image,
.guide-media-placeholder {
  width: 100%;
  min-height: 150px;
  border-radius: 8px;
  background: rgb(var(--v-theme-surface-variant));
}
</style>
