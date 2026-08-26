<template>
  <v-container class="guide-container">
    <v-btn variant="text" :prepend-icon="$globals.icons.backArrow" :to="`/g/${groupSlug}/guides`">
      {{ $t("guide.back-to-guides") }}
    </v-btn>
    <v-card class="mt-3 pa-5">
      <v-card-title class="text-h5 px-0 mb-4">
        {{ $t("guide.new-guide") }}
      </v-card-title>
      <GuideEditor v-model="draft" :loading="loading" :error="error" @save="save" />
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import GuideEditor, { type GuideDraft } from "~/components/Domain/Guide/GuideEditor.vue";

definePageMeta({ middleware: ["group-only"] });

const i18n = useI18n();
useSeoMeta({ title: i18n.t("guide.new-guide") });

const route = useRoute();
const router = useRouter();
const groupSlug = computed(() => route.params.groupSlug as string);
const api = useUserApi();
const loading = ref(false);
const error = ref("");
const draft = ref<GuideDraft>({ title: "", description: "", steps: [{ text: "" }] });

async function save() {
  loading.value = true;
  error.value = "";
  const { data } = await api.guides.createOne(draft.value);
  if (data) {
    await router.push(`/g/${groupSlug.value}/guides/${data.slug}`);
  }
  else {
    error.value = i18n.t("guide.save-error");
  }
  loading.value = false;
}
</script>

<style scoped>
.guide-container {
  max-width: 900px;
}
</style>
