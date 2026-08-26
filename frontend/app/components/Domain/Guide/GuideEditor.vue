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
        <v-textarea
          v-model="step.text"
          :label="$t('guide.step')"
          :rules="[value => !!value?.trim() || $t('guide.step-required')]"
          variant="outlined"
          rows="2"
          hide-details="auto"
        />
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
  GuideStepIn,
  GuideType,
} from "~/lib/api/types/guide";

export interface GuideDraft {
  title: string;
  description: string;
  guideType: GuideType | null;
  difficulty: GuideDifficulty | null;
  preparationMinutes: number | null;
  executionMinutes: number | null;
  category: string | null;
  tags: string[];
  steps: GuideStepIn[];
  callouts: GuideCalloutIn[];
}

defineProps<{
  loading?: boolean;
  error?: string;
  showCancel?: boolean;
}>();

const emit = defineEmits<{
  save: [];
  cancel: [];
}>();

const model = defineModel<GuideDraft>({ required: true });
const i18n = useI18n();
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
const calloutKindItems = computed(() => [
  { title: i18n.t("guide.warning"), value: "warning" },
  { title: i18n.t("guide.thing-to-avoid"), value: "avoid" },
]);
const isValid = computed(() =>
  model.value.title.trim()
  && model.value.steps.every(step => step.text.trim())
  && model.value.callouts.every(callout => callout.text.trim()),
);

function addStep() {
  model.value.steps.push({ text: "" });
}

function addCallout(kind: GuideCalloutKind) {
  model.value.callouts.push({ kind, text: "" });
}

function moveStep(index: number, direction: -1 | 1) {
  const target = index + direction;
  if (target < 0 || target >= model.value.steps.length) {
    return;
  }
  const [step] = model.value.steps.splice(index, 1);
  model.value.steps.splice(target, 0, step);
}
</script>

<style scoped>
.guide-step-number {
  width: 2rem;
  text-align: center;
}

.guide-callout-kind {
  max-width: 180px;
}

@media (max-width: 599px) {
  .guide-callout-kind {
    max-width: none;
  }
}
</style>
