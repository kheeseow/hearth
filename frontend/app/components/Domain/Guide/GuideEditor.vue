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
import type { GuideStepIn } from "~/lib/api/types/guide";

export interface GuideDraft {
  title: string;
  description: string;
  steps: GuideStepIn[];
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
const isValid = computed(() => model.value.title.trim() && model.value.steps.every(step => step.text.trim()));

function addStep() {
  model.value.steps.push({ text: "" });
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
</style>
