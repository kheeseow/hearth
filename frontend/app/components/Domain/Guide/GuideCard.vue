<template>
  <v-card
    :to="to"
    height="100%"
    variant="flat"
    class="guide-card d-flex flex-column"
  >
    <div class="guide-card-cover">
      <GuideMediaImage
        v-if="guide.coverImageVersion"
        :guide-slug="guide.slug"
        :version="guide.coverImageVersion"
        :alt="guide.title"
        size="tiny"
        :aspect-ratio="16 / 8"
      />
      <div v-else class="guide-card-placeholder" aria-hidden="true">
        <v-icon>{{ $globals.icons.book }}</v-icon>
      </div>
      <v-chip
        v-if="reviewState === 'stale'"
        class="guide-card-review"
        color="warning"
        size="small"
        variant="flat"
        :prepend-icon="$globals.icons.calendar"
      >
        {{ $t("guide.review-needed") }}
      </v-chip>
    </div>

    <v-card-text class="guide-card-body d-flex flex-column flex-grow-1">
      <p v-if="classification" class="guide-card-kicker mb-2">
        {{ classification }}
      </p>
      <h3 class="guide-card-title mb-2">
        {{ guide.title }}
      </h3>
      <p v-if="guide.description" class="guide-card-outcome text-medium-emphasis mb-4">
        {{ guide.description }}
      </p>
      <div v-if="recognitionDetails.length" class="guide-card-meta text-medium-emphasis mt-auto">
        <span v-for="detail in recognitionDetails" :key="detail.label">
          <v-icon size="16" aria-hidden="true">{{ detail.icon }}</v-icon>
          {{ detail.label }}
        </span>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { GuideSummary } from "~/lib/api/types/guide";
import { guideReviewState } from "~/composables/guides/use-guide-review";

const props = defineProps<{
  guide: GuideSummary;
  to: string;
}>();

const { $globals } = useNuxtApp();
const i18n = useI18n();
const reviewState = computed(() => guideReviewState(props.guide.lastReviewed));
const classification = computed(() => {
  const type = props.guide.guideType
    ? i18n.t(`guide.types.${props.guide.guideType.replace("_", "-")}`)
    : "";
  return [type, props.guide.category?.name].filter(Boolean).join(" · ");
});
const totalMinutes = computed(() =>
  (props.guide.preparationMinutes ?? 0) + (props.guide.executionMinutes ?? 0),
);
const recognitionDetails = computed(() => {
  const details: { icon: string; label: string }[] = [];
  if (totalMinutes.value) {
    details.push({ icon: $globals.icons.clock, label: i18n.t("guide.total-minutes", totalMinutes.value) });
  }
  if (props.guide.difficulty) {
    details.push({
      icon: $globals.icons.chartLine,
      label: i18n.t(`guide.difficulties.${props.guide.difficulty}`),
    });
  }
  else if (props.guide.frequency) {
    details.push({
      icon: $globals.icons.calendar,
      label: i18n.t(`guide.frequencies.${props.guide.frequency.replace("_", "-")}`),
    });
  }
  return details.slice(0, 2);
});
</script>

<style scoped>
.guide-card {
  overflow: hidden;
  border: 1px solid rgb(var(--v-theme-on-surface), 0.16);
  border-radius: 16px;
  background: rgb(var(--v-theme-surface));
  box-shadow: 0 1px 2px rgb(42 31 25 / 8%);
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    transform 180ms ease;
}

.guide-card:hover {
  border-color: rgb(var(--v-theme-primary), 0.42);
  box-shadow: 0 8px 20px rgb(42 31 25 / 12%);
  transform: translateY(-2px);
}

.guide-card:focus-visible {
  outline: 3px solid rgb(var(--v-theme-primary));
  outline-offset: -4px;
}

.guide-card-cover {
  position: relative;
  overflow: hidden;
  background: rgb(var(--v-theme-primary), 0.08);
}

.guide-card-placeholder {
  display: grid;
  aspect-ratio: 16 / 8;
  place-items: center;
  background:
    radial-gradient(circle at 75% 25%, rgb(var(--v-theme-secondary), 0.18), transparent 34%),
    linear-gradient(145deg, rgb(var(--v-theme-primary), 0.11), rgb(var(--v-theme-accent), 0.16));
  color: rgb(var(--v-theme-primary));
}

.guide-card-placeholder :deep(.v-icon) {
  font-size: 40px;
  opacity: 0.72;
}

.guide-card-review {
  position: absolute;
  top: 12px;
  right: 12px;
}

.guide-card-body {
  padding: 20px;
}

.guide-card-kicker {
  color: rgb(var(--v-theme-primary));
  font-size: 12px;
  font-weight: 750;
  letter-spacing: 0.06em;
  line-height: 1.4;
  text-transform: uppercase;
}

.guide-card-title {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.25;
  text-wrap: balance;
}

.guide-card-outcome {
  display: -webkit-box;
  overflow: hidden;
  font-size: 16px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.guide-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  font-size: 13px;
  font-weight: 600;
}

.guide-card-meta span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

@media (prefers-reduced-motion: reduce) {
  .guide-card {
    transition: none;
  }

  .guide-card:hover {
    transform: none;
  }
}
</style>
