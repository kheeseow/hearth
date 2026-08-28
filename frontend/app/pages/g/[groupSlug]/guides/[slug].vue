<template>
  <v-container class="guide-container">
    <v-btn
      class="d-print-none"
      variant="text"
      :prepend-icon="$globals.icons.backArrow"
      :to="`/g/${groupSlug}/guides`"
    >
      {{ $t("guide.back-to-guides") }}
    </v-btn>

    <div v-if="loading" class="d-flex justify-center py-12" role="status" aria-live="polite">
      <v-progress-circular indeterminate color="primary" :aria-label="$t('guide.loading-guide')" />
      <span class="d-sr-only">{{ $t("guide.loading-guide") }}</span>
    </div>
    <v-alert v-else-if="error" type="error" variant="tonal" class="mt-4">
      {{ error }}
      <template #append>
        <v-btn variant="text" @click="loadGuide">
          {{ $t("general.retry") }}
        </v-btn>
      </template>
    </v-alert>
    <v-card v-else-if="guide && editing" class="mt-3 pa-4 pa-sm-5">
      <h1 class="text-h5 mb-4">
        {{ $t("guide.edit-guide") }}
      </h1>
      <GuideEditor
        v-model="draft"
        :guide="guide"
        :loading="saving"
        :error="saveError"
        show-cancel
        @save="save"
        @cancel="cancelEdit"
        @guide-updated="updateGuideFromMedia"
      />
    </v-card>
    <GuideReader
      v-else-if="guide"
      class="mt-3"
      :guide="guide"
      :group-slug="groupSlug"
      :can-edit="canEdit"
      @edit="editing = true"
      @delete="deleteDialog = true"
    />

    <BaseDialog
      v-model="deleteDialog"
      :title="$t('guide.delete-guide')"
      :icon="$globals.icons.delete"
      color="error"
      can-confirm
      @confirm="remove"
    >
      <v-card-text>{{ $t("guide.delete-confirmation") }}</v-card-text>
    </BaseDialog>
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import GuideEditor, { type GuideDraft } from "~/components/Domain/Guide/GuideEditor.vue";
import GuideReader from "~/components/Domain/Guide/GuideReader.vue";
import type { GuideRead } from "~/lib/api/types/guide";

definePageMeta({ middleware: ["group-only"] });

const i18n = useI18n();
const route = useRoute();
const router = useRouter();
const auth = useMealieAuth();
const api = useUserApi();
const groupSlug = computed(() => route.params.groupSlug as string);
const slug = computed(() => route.params.slug as string);
const guide = ref<GuideRead | null>(null);
const draft = ref<GuideDraft>({
  title: "",
  description: "",
  guideType: null,
  difficulty: null,
  frequency: null,
  preparationMinutes: null,
  executionMinutes: null,
  notes: null,
  lastReviewed: null,
  category: null,
  tags: [],
  steps: [],
  callouts: [],
  requirements: [],
  sources: [],
  relatedGuideIds: [],
});
const loading = ref(true);
const saving = ref(false);
const editing = ref(false);
const deleteDialog = ref(false);
const error = ref("");
const saveError = ref("");
const canEdit = computed(() => guide.value?.householdId === auth.user.value?.householdId);

useSeoMeta({ title: computed(() => guide.value?.title || i18n.t("guide.guide")) });

function setDraft() {
  if (!guide.value) return;
  draft.value = {
    title: guide.value.title,
    description: guide.value.description,
    guideType: guide.value.guideType || null,
    difficulty: guide.value.difficulty || null,
    frequency: guide.value.frequency || null,
    preparationMinutes: guide.value.preparationMinutes ?? null,
    executionMinutes: guide.value.executionMinutes ?? null,
    notes: guide.value.notes || null,
    lastReviewed: guide.value.lastReviewed || null,
    category: guide.value.category?.name || null,
    tags: (guide.value.tags || []).map(tag => tag.name),
    steps: (guide.value.steps || []).map(step => ({ id: step.id, text: step.text, tip: step.tip || null })),
    callouts: (guide.value.callouts || []).map(callout => ({
      id: callout.id,
      kind: callout.kind,
      text: callout.text,
    })),
    requirements: (guide.value.requirements || []).map(requirement => ({
      id: requirement.id,
      kind: requirement.kind,
      name: requirement.name,
      note: requirement.note || null,
    })),
    sources: (guide.value.sources || []).map(source => ({
      id: source.id,
      label: source.label,
      url: source.url,
    })),
    relatedGuideIds: (guide.value.relatedGuides || []).map(related => related.id),
  };
}

async function loadGuide() {
  loading.value = true;
  error.value = "";
  const { data } = await api.guides.getOne(slug.value);
  if (data) {
    guide.value = data;
    setDraft();
  }
  else {
    error.value = i18n.t("guide.not-found");
  }
  loading.value = false;
}

function cancelEdit() {
  setDraft();
  editing.value = false;
  saveError.value = "";
}

async function save() {
  if (!guide.value) return;
  saving.value = true;
  saveError.value = "";
  const { data } = await api.guides.updateOne(guide.value.slug, draft.value);
  if (data) {
    guide.value = data;
    setDraft();
    editing.value = false;
  }
  else {
    saveError.value = i18n.t("guide.save-error");
  }
  saving.value = false;
}

function updateGuideFromMedia(updated: GuideRead) {
  guide.value = updated;
}

async function remove() {
  if (!guide.value) return;
  const { data } = await api.guides.deleteOne(guide.value.slug);
  if (data) {
    await router.push(`/g/${groupSlug.value}/guides`);
  }
  else {
    error.value = i18n.t("guide.delete-error");
  }
}

onMounted(loadGuide);
</script>

<style scoped>
.guide-container {
  max-width: 1160px;
}

@media print {
  .guide-container {
    max-width: none;
    padding: 0 !important;
  }
}

@media (max-width: 599px) {
  .guide-container {
    padding-inline: 12px;
  }
}
</style>
