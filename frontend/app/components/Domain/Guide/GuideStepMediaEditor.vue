<template>
  <div class="guide-step-media-editor mt-4">
    <div class="d-flex flex-wrap align-center ga-2 mb-2">
      <strong>{{ $t("guide.step-images") }}</strong>
      <span class="text-body-2 text-medium-emphasis">{{ $t("guide.step-images-hint") }}</span>
    </div>
    <v-card
      v-for="(image, index) in images"
      :key="image.id"
      variant="tonal"
      class="mb-3 pa-3"
    >
      <v-row>
        <v-col cols="12" sm="5">
          <GuideMediaImage
            :guide-slug="guideSlug"
            :step-id="step.id"
            :image-id="image.id"
            :version="image.version"
            :alt="image.altText || ''"
            size="small"
          />
        </v-col>
        <v-col cols="12" sm="7">
          <v-text-field
            v-model="metadata[image.id].caption"
            :label="$t('guide.image-caption')"
            variant="outlined"
            density="compact"
            @blur="saveMetadata(image.id)"
          />
          <v-text-field
            v-model="metadata[image.id].altText"
            :label="$t('guide.image-alt-text')"
            :hint="$t('guide.image-alt-text-hint')"
            variant="outlined"
            density="compact"
            persistent-hint
            @blur="saveMetadata(image.id)"
          />
          <div class="d-flex flex-wrap ga-1 mt-2">
            <v-btn
              icon
              size="small"
              variant="text"
              :disabled="index === 0 || busy"
              :aria-label="$t('guide.move-image-left')"
              @click="move(index, -1)"
            >
              <v-icon>{{ $globals.icons.arrowLeftBold }}</v-icon>
            </v-btn>
            <v-btn
              icon
              size="small"
              variant="text"
              :disabled="index === images.length - 1 || busy"
              :aria-label="$t('guide.move-image-right')"
              @click="move(index, 1)"
            >
              <v-icon>{{ $globals.icons.arrowRightBold }}</v-icon>
            </v-btn>
            <v-file-input
              :key="`${image.id}-${inputKey}`"
              accept="image/jpeg,image/png,image/webp,image/heic,image/avif"
              :label="$t('guide.replace-image')"
              variant="outlined"
              density="compact"
              hide-details
              prepend-icon=""
              class="guide-replace-input"
              @update:model-value="value => replace(image.id, value)"
            />
            <v-btn
              icon
              size="small"
              color="error"
              variant="text"
              :disabled="busy"
              :aria-label="$t('guide.remove-image')"
              @click="remove(image.id)"
            >
              <v-icon>{{ $globals.icons.delete }}</v-icon>
            </v-btn>
          </div>
        </v-col>
      </v-row>
    </v-card>
    <v-file-input
      :key="`add-${inputKey}`"
      accept="image/jpeg,image/png,image/webp,image/heic,image/avif"
      :label="$t('guide.add-step-image')"
      variant="outlined"
      density="compact"
      prepend-icon=""
      :prepend-inner-icon="$globals.icons.fileImage"
      :loading="busy"
      :disabled="images.length >= 20"
      show-size
      @update:model-value="add"
    />
    <v-alert v-if="error" type="error" variant="tonal" density="compact">
      {{ error }}
    </v-alert>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import type { GuideRead, GuideStepOut } from "~/lib/api/types/guide";

const props = defineProps<{ guideSlug: string; step: GuideStepOut }>();
const emit = defineEmits<{ updated: [guide: GuideRead] }>();
const api = useUserApi();
const i18n = useI18n();
const busy = ref(false);
const error = ref("");
const inputKey = ref(0);
const metadata = reactive<Record<string, { caption: string; altText: string }>>({});
const images = computed(() => props.step.images || []);

watch(
  images,
  (images) => {
    for (const image of images) {
      metadata[image.id] = {
        caption: image.caption || "",
        altText: image.altText || "",
      };
    }
  },
  { immediate: true, deep: true },
);

function firstFile(value: File | File[] | null): File | null {
  return Array.isArray(value) ? value[0] || null : value;
}

function finish(data: GuideRead | null) {
  if (data) emit("updated", data);
  else error.value = i18n.t("guide.image-save-error");
  busy.value = false;
  inputKey.value++;
}

async function add(value: File | File[] | null) {
  const file = firstFile(value);
  if (!file) return;
  busy.value = true;
  error.value = "";
  const { data } = await api.guides.addStepImage(props.guideSlug, props.step.id, file);
  finish(data);
}

async function replace(imageId: string, value: File | File[] | null) {
  const file = firstFile(value);
  if (!file) return;
  busy.value = true;
  error.value = "";
  const { data } = await api.guides.replaceStepImage(props.guideSlug, props.step.id, imageId, file);
  finish(data);
}

async function saveMetadata(imageId: string) {
  const values = metadata[imageId];
  const original = images.value.find(image => image.id === imageId);
  if (!original || (values.caption === (original.caption || "") && values.altText === (original.altText || ""))) return;
  busy.value = true;
  error.value = "";
  const { data } = await api.guides.updateStepImage(props.guideSlug, props.step.id, imageId, values);
  finish(data);
}

async function move(index: number, direction: -1 | 1) {
  const ids = images.value.map(image => image.id);
  const [imageId] = ids.splice(index, 1);
  ids.splice(index + direction, 0, imageId);
  busy.value = true;
  error.value = "";
  const { data } = await api.guides.reorderStepImages(props.guideSlug, props.step.id, ids);
  finish(data);
}

async function remove(imageId: string) {
  busy.value = true;
  error.value = "";
  const { data } = await api.guides.deleteStepImage(props.guideSlug, props.step.id, imageId);
  if (data) emit("updated", data);
  else error.value = i18n.t("guide.image-delete-error");
  busy.value = false;
}
</script>

<style scoped>
.guide-replace-input {
  min-width: 190px;
  max-width: 260px;
}

@media (max-width: 599px) {
  .guide-step-media-editor :deep(.v-btn--icon.v-btn--size-small) {
    min-width: 44px;
    min-height: 44px;
  }

  .guide-replace-input {
    min-width: 0;
    max-width: none;
  }
}
</style>
