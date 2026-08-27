<template>
  <v-form @submit.prevent="emit('save')">
    <v-text-field
      v-model="model.title"
      :label="$t('guide.title')"
      :rules="[value => !!value?.trim() || $t('guide.title-required')]"
      variant="outlined"
      autofocus
    />
    <v-textarea
      v-model="model.description"
      :label="$t('guide.description')"
      variant="outlined"
      rows="3"
    />

    <GuideCoverMediaEditor v-if="guide" :guide="guide" @updated="emit('guide-updated', $event)" />

    <h2 class="text-h6 mb-3">
      {{ $t("guide.classification") }}
    </h2>
    <v-row density="compact">
      <v-col cols="12" sm="6">
        <v-select
          v-model="model.guideType"
          :label="$t('guide.type')"
          :items="guideTypeItems"
          variant="outlined"
          clearable
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-select
          v-model="model.difficulty"
          :label="$t('guide.difficulty')"
          :items="difficultyItems"
          variant="outlined"
          clearable
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-select
          v-model="model.frequency"
          :label="$t('guide.frequency')"
          :items="frequencyItems"
          variant="outlined"
          clearable
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field v-model="model.category" :label="$t('guide.category')" variant="outlined" clearable />
      </v-col>
      <v-col cols="12" sm="6">
        <v-combobox
          v-model="model.tags"
          :label="$t('guide.tags')"
          :hint="$t('guide.tags-hint')"
          variant="outlined"
          multiple
          chips
          closable-chips
          persistent-hint
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model.number="model.preparationMinutes"
          :label="$t('guide.preparation-minutes')"
          type="number"
          min="0"
          max="10080"
          variant="outlined"
          clearable
        />
      </v-col>
      <v-col cols="12" sm="6">
        <v-text-field
          v-model.number="model.executionMinutes"
          :label="$t('guide.execution-minutes')"
          type="number"
          min="0"
          max="10080"
          variant="outlined"
          clearable
        />
      </v-col>
    </v-row>

    <h2 class="text-h6 mb-1">
      {{ $t("guide.knowledge-upkeep") }}
    </h2>
    <p class="text-body-2 text-medium-emphasis mb-3">
      {{ $t("guide.knowledge-upkeep-description") }}
    </p>
    <v-row density="compact">
      <v-col cols="12" sm="6">
        <v-text-field
          v-model="model.lastReviewed"
          :label="$t('guide.last-reviewed')"
          type="date"
          variant="outlined"
          clearable
        />
      </v-col>
      <v-col cols="12">
        <v-textarea
          v-model="model.notes"
          :label="$t('guide.notes')"
          :hint="$t('guide.notes-hint')"
          variant="outlined"
          rows="3"
          persistent-hint
          class="mb-3"
        />
      </v-col>
      <v-col cols="12">
        <v-autocomplete
          v-model="model.relatedGuideIds"
          :label="$t('guide.related-guides')"
          :hint="$t('guide.related-guides-hint')"
          :items="relatedGuideItems"
          item-title="title"
          item-value="id"
          variant="outlined"
          multiple
          chips
          closable-chips
          persistent-hint
        />
      </v-col>
    </v-row>

    <div class="d-flex flex-wrap align-center ga-2 mb-2">
      <div>
        <h2 class="text-h6">
          {{ $t("guide.sources") }}
        </h2>
        <p class="text-body-2 text-medium-emphasis">
          {{ $t("guide.sources-description") }}
        </p>
      </div>
      <v-spacer />
      <v-btn color="primary" variant="text" :prepend-icon="$globals.icons.link" @click="addSource">
        {{ $t("guide.add-source") }}
      </v-btn>
    </div>
    <v-card
      v-for="(source, index) in model.sources"
      :key="source.id || index"
      variant="outlined"
      class="mb-3 pa-3"
    >
      <div class="d-flex flex-column flex-sm-row align-start ga-2">
        <div class="text-h6 pt-2 guide-source-number">
          {{ index + 1 }}
        </div>
        <div class="flex-grow-1 w-100">
          <v-text-field
            v-model="source.label"
            :label="$t('guide.source-label')"
            :rules="[value => !!value?.trim() || $t('guide.source-label-required')]"
            variant="outlined"
            hide-details="auto"
            class="mb-2"
          />
          <v-text-field
            v-model="source.url"
            :label="$t('guide.source-url')"
            :rules="[value => sourceUrlIsValid(value) || $t('guide.source-url-required')]"
            variant="outlined"
            hide-details="auto"
          />
        </div>
        <div class="d-flex flex-sm-column">
          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="index === 0"
            :aria-label="$t('guide.move-source-up')"
            @click="moveSource(index, -1)"
          >
            <v-icon>{{ $globals.icons.arrowUp }}</v-icon>
          </v-btn>
          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="index === model.sources.length - 1"
            :aria-label="$t('guide.move-source-down')"
            @click="moveSource(index, 1)"
          >
            <v-icon style="transform: rotate(180deg)">
              {{ $globals.icons.arrowUp }}
            </v-icon>
          </v-btn>
          <v-btn
            icon
            size="small"
            variant="text"
            color="error"
            :aria-label="$t('guide.remove-source')"
            @click="model.sources.splice(index, 1)"
          >
            <v-icon>{{ $globals.icons.delete }}</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card>

    <div class="d-flex flex-wrap align-center ga-2 mb-2">
      <div>
        <h2 class="text-h6">
          {{ $t("guide.requirements") }}
        </h2>
        <p class="text-body-2 text-medium-emphasis">
          {{ $t("guide.requirements-description") }}
        </p>
      </div>
      <v-spacer />
      <v-btn color="primary" variant="text" @click="addRequirement('tool')">
        {{ $t("guide.add-tool") }}
      </v-btn>
      <v-btn color="primary" variant="text" @click="addRequirement('material')">
        {{ $t("guide.add-material") }}
      </v-btn>
    </div>
    <v-card
      v-for="(requirement, index) in model.requirements"
      :key="requirement.id || index"
      variant="outlined"
      class="mb-3 pa-3"
    >
      <div class="d-flex flex-column flex-sm-row align-start ga-2">
        <div class="text-h6 pt-2 guide-requirement-number">
          {{ index + 1 }}
        </div>
        <v-select
          v-model="requirement.kind"
          :label="$t('guide.requirement-type')"
          :items="requirementKindItems"
          variant="outlined"
          hide-details="auto"
          class="guide-requirement-kind"
        />
        <div class="flex-grow-1 w-100">
          <v-text-field
            v-model="requirement.name"
            :label="requirement.kind === 'tool' ? $t('guide.tool') : $t('guide.material')"
            :rules="[value => !!value?.trim() || $t('guide.requirement-required')]"
            variant="outlined"
            hide-details="auto"
            class="mb-2"
          />
          <v-text-field
            v-model="requirement.note"
            :label="$t('guide.requirement-note')"
            :hint="$t('guide.requirement-note-hint')"
            variant="outlined"
            hide-details="auto"
          />
        </div>
        <div class="d-flex flex-sm-column">
          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="index === 0"
            :aria-label="$t('guide.move-requirement-up')"
            @click="moveRequirement(index, -1)"
          >
            <v-icon>{{ $globals.icons.arrowUp }}</v-icon>
          </v-btn>
          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="index === model.requirements.length - 1"
            :aria-label="$t('guide.move-requirement-down')"
            @click="moveRequirement(index, 1)"
          >
            <v-icon style="transform: rotate(180deg)">
              {{ $globals.icons.arrowUp }}
            </v-icon>
          </v-btn>
          <v-btn
            icon
            size="small"
            variant="text"
            color="error"
            :aria-label="$t('guide.remove-requirement')"
            @click="model.requirements.splice(index, 1)"
          >
            <v-icon>{{ $globals.icons.delete }}</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card>

    <div class="d-flex flex-wrap align-center ga-2 mb-2">
      <h2 class="text-h6">
        {{ $t("guide.safety") }}
      </h2>
      <v-spacer />
      <v-btn color="warning" variant="text" @click="addCallout('warning')">
        {{ $t("guide.add-warning") }}
      </v-btn>
      <v-btn color="error" variant="text" @click="addCallout('avoid')">
        {{ $t("guide.add-avoid") }}
      </v-btn>
    </div>
    <v-card
      v-for="(callout, index) in model.callouts"
      :key="callout.id || index"
      :color="callout.kind === 'warning' ? 'warning' : 'error'"
      variant="tonal"
      class="mb-3 pa-3"
    >
      <div class="d-flex flex-column flex-sm-row align-start ga-2">
        <v-select
          v-model="callout.kind"
          :label="$t('guide.safety-type')"
          :items="calloutKindItems"
          variant="outlined"
          hide-details="auto"
          class="guide-callout-kind"
        />
        <v-textarea
          v-model="callout.text"
          :label="callout.kind === 'warning' ? $t('guide.warning') : $t('guide.thing-to-avoid')"
          :rules="[value => !!value?.trim() || $t('guide.callout-required')]"
          variant="outlined"
          rows="2"
          hide-details="auto"
        />
        <v-btn
          icon
          size="small"
          variant="text"
          :aria-label="$t('guide.remove-callout')"
          @click="model.callouts.splice(index, 1)"
        >
          <v-icon>{{ $globals.icons.delete }}</v-icon>
        </v-btn>
      </div>
    </v-card>

    <div class="d-flex align-center mb-2">
      <h2 class="text-h6">
        {{ $t("guide.steps") }}
      </h2>
      <v-spacer />
      <v-btn
        color="primary"
        variant="text"
        :prepend-icon="$globals.icons.create"
        @click="addStep"
      >
        {{ $t("guide.add-step") }}
      </v-btn>
    </div>

    <v-card
      v-for="(step, index) in model.steps"
      :key="step.id || index"
      variant="outlined"
      class="mb-3 pa-3"
    >
      <div class="d-flex align-start ga-2">
        <div class="text-h6 pt-2 guide-step-number">
          {{ index + 1 }}
        </div>
        <div class="flex-grow-1">
          <v-textarea
            v-model="step.text"
            :label="$t('guide.step')"
            :rules="[value => !!value?.trim() || $t('guide.step-required')]"
            variant="outlined"
            rows="2"
            hide-details="auto"
            class="mb-2"
          />
          <v-textarea
            v-model="step.tip"
            :label="$t('guide.step-tip')"
            :hint="$t('guide.step-tip-hint')"
            variant="outlined"
            rows="2"
            hide-details="auto"
          />
          <GuideStepMediaEditor
            v-if="persistedStep(step.id)"
            :guide-slug="guide?.slug || ''"
            :step="persistedStep(step.id)!"
            @updated="emit('guide-updated', $event)"
          />
          <v-alert v-else-if="guide" type="info" variant="tonal" density="compact" class="mt-3">
            {{ $t("guide.save-before-adding-images") }}
          </v-alert>
        </div>
        <div class="d-flex flex-column">
          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="index === 0"
            :aria-label="$t('guide.move-up')"
            @click="moveStep(index, -1)"
          >
            <v-icon>{{ $globals.icons.arrowUp }}</v-icon>
          </v-btn>
          <v-btn
            icon
            size="small"
            variant="text"
            :disabled="index === model.steps.length - 1"
            :aria-label="$t('guide.move-down')"
            @click="moveStep(index, 1)"
          >
            <v-icon style="transform: rotate(180deg)">
              {{ $globals.icons.arrowUp }}
            </v-icon>
          </v-btn>
          <v-btn
            icon
            size="small"
            variant="text"
            color="error"
            :aria-label="$t('guide.remove-step')"
            @click="model.steps.splice(index, 1)"
          >
            <v-icon>{{ $globals.icons.delete }}</v-icon>
          </v-btn>
        </div>
      </div>
    </v-card>

    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
      {{ error }}
    </v-alert>
    <div class="d-flex justify-end ga-2">
      <v-btn v-if="showCancel" variant="text" @click="emit('cancel')">
        {{ $t("general.cancel") }}
      </v-btn>
      <v-btn
        type="submit"
        color="primary"
        :loading="loading"
        :disabled="!isValid"
        :prepend-icon="$globals.icons.save"
      >
        {{ $t("general.save") }}
      </v-btn>
    </div>
  </v-form>
</template>

<script setup lang="ts">
import type {
  GuideCalloutIn,
  GuideCalloutKind,
  GuideDifficulty,
  GuideFrequency,
  GuideRequirementIn,
  GuideRequirementKind,
  GuideRead,
  GuideSourceIn,
  GuideStepOut,
  GuideStepIn,
  GuideType,
} from "~/lib/api/types/guide";
import { useUserApi } from "~/composables/api";

export interface GuideDraft {
  title: string;
  description: string;
  guideType: GuideType | null;
  difficulty: GuideDifficulty | null;
  frequency: GuideFrequency | null;
  preparationMinutes: number | null;
  executionMinutes: number | null;
  notes: string | null;
  lastReviewed: string | null;
  category: string | null;
  tags: string[];
  steps: GuideStepIn[];
  callouts: GuideCalloutIn[];
  requirements: GuideRequirementIn[];
  sources: GuideSourceIn[];
  relatedGuideIds: string[];
}

const props = defineProps<{
  loading?: boolean;
  error?: string;
  showCancel?: boolean;
  guide?: GuideRead;
}>();

const emit = defineEmits<{
  "save": [];
  "cancel": [];
  "guide-updated": [guide: GuideRead];
}>();

const model = defineModel<GuideDraft>({ required: true });
const i18n = useI18n();
const api = useUserApi();
const relatedGuideItems = ref<Array<{ id: string; title: string }>>([]);
const guideTypeItems = computed(() => [
  { title: i18n.t("guide.types.cleaning"), value: "cleaning" },
  { title: i18n.t("guide.types.maintenance"), value: "maintenance" },
  { title: i18n.t("guide.types.setup"), value: "setup" },
  { title: i18n.t("guide.types.emergency"), value: "emergency" },
  { title: i18n.t("guide.types.troubleshooting"), value: "troubleshooting" },
  { title: i18n.t("guide.types.care-instructions"), value: "care_instructions" },
]);
const difficultyItems = computed(() => [
  { title: i18n.t("guide.difficulties.beginner"), value: "beginner" },
  { title: i18n.t("guide.difficulties.intermediate"), value: "intermediate" },
  { title: i18n.t("guide.difficulties.advanced"), value: "advanced" },
]);
const frequencyItems = computed(() => [
  { title: i18n.t("guide.frequencies.one-time"), value: "one_time" },
  { title: i18n.t("guide.frequencies.weekly"), value: "weekly" },
  { title: i18n.t("guide.frequencies.monthly"), value: "monthly" },
  { title: i18n.t("guide.frequencies.yearly"), value: "yearly" },
  { title: i18n.t("guide.frequencies.as-needed"), value: "as_needed" },
]);
const calloutKindItems = computed(() => [
  { title: i18n.t("guide.warning"), value: "warning" },
  { title: i18n.t("guide.thing-to-avoid"), value: "avoid" },
]);
const requirementKindItems = computed(() => [
  { title: i18n.t("guide.tool"), value: "tool" },
  { title: i18n.t("guide.material"), value: "material" },
]);
const isValid = computed(() =>
  model.value.title.trim()
  && model.value.steps.every(step => step.text.trim())
  && model.value.callouts.every(callout => callout.text.trim())
  && model.value.requirements.every(requirement => requirement.name.trim())
  && model.value.sources.every(source => source.label.trim() && sourceUrlIsValid(source.url)),
);

function addStep() {
  model.value.steps.push({ text: "" });
}

function addCallout(kind: GuideCalloutKind) {
  model.value.callouts.push({ kind, text: "" });
}

function addRequirement(kind: GuideRequirementKind) {
  model.value.requirements.push({ kind, name: "", note: null });
}

function addSource() {
  model.value.sources.push({ label: "", url: "" });
}

function moveStep(index: number, direction: -1 | 1) {
  const target = index + direction;
  if (target < 0 || target >= model.value.steps.length) {
    return;
  }
  const [step] = model.value.steps.splice(index, 1);
  model.value.steps.splice(target, 0, step);
}

function moveRequirement(index: number, direction: -1 | 1) {
  const target = index + direction;
  if (target < 0 || target >= model.value.requirements.length) {
    return;
  }
  const [requirement] = model.value.requirements.splice(index, 1);
  model.value.requirements.splice(target, 0, requirement);
}

function moveSource(index: number, direction: -1 | 1) {
  const target = index + direction;
  if (target < 0 || target >= model.value.sources.length) {
    return;
  }
  const [source] = model.value.sources.splice(index, 1);
  model.value.sources.splice(target, 0, source);
}

function sourceUrlIsValid(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  }
  catch {
    return false;
  }
}

async function loadRelatedGuides() {
  const { data } = await api.guides.getAll(1, -1);
  relatedGuideItems.value = (data?.items || [])
    .filter(item => item.id !== props.guide?.id)
    .map(item => ({ id: item.id, title: item.title }));
}

function persistedStep(stepId?: string | null): GuideStepOut | undefined {
  if (!stepId) return undefined;
  return props.guide?.steps?.find(step => step.id === stepId);
}

onMounted(loadRelatedGuides);
</script>

<style scoped>
.guide-step-number {
  width: 2rem;
  text-align: center;
}

.guide-callout-kind {
  max-width: 180px;
}

.guide-requirement-number {
  width: 2rem;
  text-align: center;
}

.guide-source-number {
  width: 2rem;
  text-align: center;
}

.guide-requirement-kind {
  max-width: 160px;
}

@media (max-width: 599px) {
  .guide-callout-kind,
  .guide-requirement-kind {
    max-width: none;
  }
}
</style>
