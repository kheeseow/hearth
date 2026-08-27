<template>
  <section class="mb-6" aria-labelledby="guide-cover-heading">
    <h2 id="guide-cover-heading" class="text-h6 mb-2">
      {{ $t("guide.cover-image") }}
    </h2>
    <p class="text-body-2 text-medium-emphasis mb-3">
      {{ $t("guide.cover-image-hint") }}
    </p>
    <GuideMediaImage
      v-if="guide.coverImageVersion"
      :guide-slug="guide.slug"
      :version="guide.coverImageVersion"
      :alt="guide.title"
      size="small"
      class="mb-3"
    />
    <v-file-input
      :key="inputKey"
      accept="image/jpeg,image/png,image/webp,image/heic,image/avif"
      :label="guide.coverImageVersion ? $t('guide.replace-cover-image') : $t('guide.upload-cover-image')"
      variant="outlined"
      prepend-icon=""
      :prepend-inner-icon="$globals.icons.fileImage"
      :loading="busy"
      show-size
      @update:model-value="upload"
    />
    <v-btn
      v-if="guide.coverImageVersion"
      color="error"
      variant="text"
      :loading="busy"
      :prepend-icon="$globals.icons.delete"
      @click="remove"
    >
      {{ $t("guide.remove-cover-image") }}
    </v-btn>
    <v-alert v-if="error" type="error" variant="tonal" density="compact" class="mt-2">
      {{ error }}
    </v-alert>
  </section>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import type { GuideRead } from "~/lib/api/types/guide";

const props = defineProps<{ guide: GuideRead }>();
const emit = defineEmits<{ updated: [guide: GuideRead] }>();
const api = useUserApi();
const i18n = useI18n();
const busy = ref(false);
const error = ref("");
const inputKey = ref(0);

function firstFile(value: File | File[] | null): File | null {
  return Array.isArray(value) ? value[0] || null : value;
}

async function upload(value: File | File[] | null) {
  const file = firstFile(value);
  if (!file) return;
  busy.value = true;
  error.value = "";
  const { data } = await api.guides.updateCoverImage(props.guide.slug, file);
  if (data) emit("updated", data);
  else error.value = i18n.t("guide.image-save-error");
  busy.value = false;
  inputKey.value++;
}

async function remove() {
  busy.value = true;
  error.value = "";
  const { data } = await api.guides.deleteCoverImage(props.guide.slug);
  if (data) emit("updated", data);
  else error.value = i18n.t("guide.image-delete-error");
  busy.value = false;
}
</script>
