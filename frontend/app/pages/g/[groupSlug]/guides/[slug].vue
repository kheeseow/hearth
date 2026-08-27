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
        :guide="guide"
        :loading="saving"
        :error="saveError"
        show-cancel
        @save="save"
        @cancel="cancelEdit"
        @guide-updated="updateGuideFromMedia"
      />
      <template v-else>
        <GuideMediaImage
          v-if="guide.coverImageVersion"
          :guide-slug="guide.slug"
          :version="guide.coverImageVersion"
          :alt="guide.title"
          size="original"
          class="guide-cover mb-5"
        />
        <div class="d-flex align-start ga-3">
          <div>
            <h1 class="text-h4 mb-2">
              {{ guide.title }}
            </h1>
            <p v-if="guide.description" class="text-body-1 text-medium-emphasis guide-description">
              {{ guide.description }}
            </p>
            <div class="d-flex flex-wrap ga-2 mt-3">
              <v-chip v-if="guide.guideType" color="primary" variant="tonal">
                {{ $t(`guide.types.${guide.guideType.replace('_', '-')}`) }}
              </v-chip>
              <v-chip v-if="guide.difficulty" variant="tonal">
                {{ $t(`guide.difficulties.${guide.difficulty}`) }}
              </v-chip>
              <v-chip v-if="guide.frequency" variant="tonal">
                {{ $t(`guide.frequencies.${guide.frequency.replace('_', '-')}`) }}
              </v-chip>
              <v-chip v-if="guide.category" variant="outlined">
                {{ guide.category.name }}
              </v-chip>
              <v-chip v-if="totalMinutes" variant="outlined" :prepend-icon="$globals.icons.clockOutline">
                {{ $t("guide.total-minutes", { count: totalMinutes }) }}
              </v-chip>
            </div>
            <div v-if="guide.tags?.length" class="d-flex flex-wrap ga-2 mt-3">
              <v-chip v-for="tag in guide.tags" :key="tag.id" size="small">
                {{ tag.name }}
              </v-chip>
            </div>
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

        <section v-if="guide.requirements?.length" class="mt-6" aria-labelledby="guide-requirements-heading">
          <h2 id="guide-requirements-heading" class="text-h5 mb-3">
            {{ $t("guide.requirements") }}
          </h2>
          <ol class="guide-requirements">
            <li v-for="requirement in guide.requirements" :key="requirement.id" class="mb-3 pl-2">
              <div class="d-flex flex-wrap align-center ga-2">
                <strong>{{ requirement.name }}</strong>
                <v-chip size="x-small" variant="tonal">
                  {{ $t(`guide.${requirement.kind}`) }}
                </v-chip>
              </div>
              <p v-if="requirement.note" class="text-body-2 text-medium-emphasis mt-1">
                {{ requirement.note }}
              </p>
            </li>
          </ol>
        </section>

        <section v-if="warnings.length || avoids.length" class="mt-6" aria-labelledby="guide-safety-heading">
          <h2 id="guide-safety-heading" class="text-h5 mb-3">
            {{ $t("guide.safety") }}
          </h2>
          <v-alert
            v-for="warning in warnings"
            :key="warning.id"
            type="warning"
            variant="tonal"
            class="mb-3 guide-callout"
          >
            <strong>{{ $t("guide.warning") }}:</strong> {{ warning.text }}
          </v-alert>
          <v-alert
            v-for="avoid in avoids"
            :key="avoid.id"
            type="error"
            variant="tonal"
            class="mb-3 guide-callout"
          >
            <strong>{{ $t("guide.thing-to-avoid") }}:</strong> {{ avoid.text }}
          </v-alert>
        </section>

        <v-divider class="my-6" />
        <h2 class="text-h5 mb-4">
          {{ $t("guide.steps") }}
        </h2>
        <ol v-if="guide.steps?.length" class="guide-steps">
          <li v-for="step in guide.steps" :key="step.id" class="mb-5 pl-2 text-body-1">
            <p>{{ step.text }}</p>
            <div v-if="step.images?.length" class="guide-step-images mt-3">
              <figure v-for="image in step.images || []" :key="image.id" class="ma-0">
                <GuideMediaImage
                  :guide-slug="guide.slug"
                  :step-id="step.id"
                  :image-id="image.id"
                  :version="image.version"
                  :alt="image.altText || image.caption || ''"
                  size="small"
                />
                <figcaption v-if="image.caption" class="text-body-2 text-medium-emphasis mt-1">
                  {{ image.caption }}
                </figcaption>
              </figure>
            </div>
            <v-alert v-if="step.tip" type="info" variant="tonal" density="compact" class="mt-3 guide-tip">
              <strong>{{ $t("guide.tip") }}:</strong> {{ step.tip }}
            </v-alert>
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
const draft = ref<GuideDraft>({
  title: "",
  description: "",
  guideType: null,
  difficulty: null,
  frequency: null,
  preparationMinutes: null,
  executionMinutes: null,
  category: null,
  tags: [],
  steps: [],
  callouts: [],
  requirements: [],
});
const loading = ref(true);
const saving = ref(false);
const editing = ref(false);
const deleteDialog = ref(false);
const error = ref("");
const saveError = ref("");
const canEdit = computed(() => guide.value?.householdId === auth.user.value?.householdId);
const warnings = computed(() => guide.value?.callouts?.filter(callout => callout.kind === "warning") || []);
const avoids = computed(() => guide.value?.callouts?.filter(callout => callout.kind === "avoid") || []);
const totalMinutes = computed(() =>
  (guide.value?.preparationMinutes || 0) + (guide.value?.executionMinutes || 0),
);

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
  max-width: 900px;
}

.guide-description,
.guide-steps li,
.guide-callout,
.guide-tip {
  white-space: pre-wrap;
}

.guide-steps,
.guide-requirements {
  padding-left: 2rem;
}

.guide-steps li::marker,
.guide-requirements li::marker {
  color: rgb(var(--v-theme-primary));
  font-size: 1.25rem;
  font-weight: 700;
}

.guide-cover {
  max-height: 460px;
  overflow: hidden;
  border-radius: 12px;
}

.guide-step-images {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}
</style>
