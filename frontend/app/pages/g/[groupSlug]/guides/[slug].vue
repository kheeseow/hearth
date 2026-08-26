<template>
  <v-container class="guide-container">
    <v-btn variant="text" :prepend-icon="$globals.icons.backArrow" :to="`/g/${groupSlug}/guides`">
      {{ $t("guide.back-to-guides") }}
    </v-btn>

    <div v-if="loading" class="d-flex justify-center py-12">
      <v-progress-circular indeterminate color="primary" />
    </div>
    <v-alert v-else-if="error" type="error" variant="tonal" class="mt-4">
      {{ error }}
    </v-alert>
    <v-card v-else-if="guide" class="mt-3 pa-5">
      <GuideEditor
        v-if="editing"
        v-model="draft"
        :loading="saving"
        :error="saveError"
        show-cancel
        @save="save"
        @cancel="cancelEdit"
      />
      <template v-else>
        <div class="d-flex align-start ga-3">
          <div>
            <h1 class="text-h4 mb-2">
              {{ guide.title }}
            </h1>
            <p v-if="guide.description" class="text-body-1 text-medium-emphasis guide-description">
              {{ guide.description }}
            </p>
          </div>
          <v-spacer />
          <v-btn
            v-if="canEdit"
            color="primary"
            variant="outlined"
            :prepend-icon="$globals.icons.edit"
            @click="editing = true"
          >
            {{ $t("general.edit") }}
          </v-btn>
        </div>

        <v-divider class="my-6" />
        <h2 class="text-h5 mb-4">
          {{ $t("guide.steps") }}
        </h2>
        <ol v-if="guide.steps?.length" class="guide-steps">
          <li v-for="step in guide.steps" :key="step.id" class="mb-5 pl-2 text-body-1">
            {{ step.text }}
          </li>
        </ol>
        <p v-else class="text-medium-emphasis">
          {{ $t("guide.no-steps") }}
        </p>

        <div v-if="canEdit" class="d-flex justify-end mt-8">
          <v-btn color="error" variant="text" :prepend-icon="$globals.icons.delete" @click="deleteDialog = true">
            {{ $t("general.delete") }}
          </v-btn>
        </div>
      </template>
    </v-card>

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
const draft = ref<GuideDraft>({ title: "", description: "", steps: [] });
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
    steps: (guide.value.steps || []).map(step => ({ id: step.id, text: step.text })),
  };
}

async function loadGuide() {
  loading.value = true;
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
  max-width: 900px;
}

.guide-description,
.guide-steps li {
  white-space: pre-wrap;
}

.guide-steps {
  padding-left: 2rem;
}

.guide-steps li::marker {
  color: rgb(var(--v-theme-primary));
  font-size: 1.25rem;
  font-weight: 700;
}
</style>
