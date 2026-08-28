<template>
  <article class="guide-reader" :aria-labelledby="titleId">
    <v-card class="guide-reader-card" rounded="xl">
      <GuideMediaImage
        v-if="guide.coverImageVersion"
        :guide-slug="guide.slug"
        :version="guide.coverImageVersion"
        :alt="guide.title"
        size="original"
        class="guide-cover"
      />

      <header class="guide-reader-header pa-5 pa-sm-8">
        <div class="d-flex flex-column flex-sm-row align-start ga-4">
          <div class="flex-grow-1">
            <div class="text-overline text-primary font-weight-bold mb-1">
              {{ brand.name }} · {{ $t("guide.guide") }}
            </div>
            <h1 :id="titleId" class="guide-title text-h3 text-sm-h2 font-weight-bold mb-3">
              {{ guide.title }}
            </h1>
            <p v-if="guide.description" class="text-body-1 text-sm-h6 text-medium-emphasis guide-description mb-0">
              {{ guide.description }}
            </p>
          </div>

          <div class="d-print-none d-flex flex-wrap ga-2 guide-actions">
            <v-btn
              variant="outlined"
              :prepend-icon="$globals.icons.printer"
              @click="printGuide"
            >
              {{ $t("guide.print-guide") }}
            </v-btn>
            <v-btn
              v-if="canEdit"
              color="primary"
              variant="outlined"
              :prepend-icon="$globals.icons.edit"
              @click="$emit('edit')"
            >
              {{ $t("general.edit") }}
            </v-btn>
          </div>
        </div>

        <div class="d-flex flex-wrap ga-2 mt-5 guide-metadata">
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
          <v-chip
            v-if="guide.lastReviewed"
            :color="reviewState === 'stale' ? 'warning' : 'success'"
            variant="tonal"
            :prepend-icon="$globals.icons.calendar"
          >
            {{ reviewState === "stale"
              ? $t("guide.review-overdue", { date: reviewDateLabel })
              : $t("guide.reviewed-on", { date: reviewDateLabel }) }}
          </v-chip>
          <v-chip v-else color="warning" variant="tonal" :prepend-icon="$globals.icons.calendar">
            {{ $t("guide.not-reviewed") }}
          </v-chip>
        </div>
        <div v-if="guide.tags?.length" class="d-flex flex-wrap ga-2 mt-3">
          <v-chip v-for="tag in guide.tags" :key="tag.id" size="small">
            {{ tag.name }}
          </v-chip>
        </div>
      </header>

      <div class="guide-reader-body pa-5 pa-sm-8 pt-0 pt-sm-0">
        <section
          v-if="warnings.length || avoids.length"
          class="guide-section guide-safety mb-8"
          aria-labelledby="guide-safety-heading"
        >
          <h2 id="guide-safety-heading" class="text-h5 font-weight-bold mb-4">
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

        <div class="guide-content-grid" :class="{ 'guide-content-grid--single': !hasSupportingContent }">
          <aside v-if="hasSupportingContent" class="guide-sidebar">
            <section
              v-if="guide.requirements?.length"
              class="guide-section guide-support-card pa-5"
              aria-labelledby="guide-requirements-heading"
            >
              <h2 id="guide-requirements-heading" class="text-h5 font-weight-bold mb-4">
                {{ $t("guide.requirements") }}
              </h2>
              <ul class="guide-requirements">
                <li v-for="requirement in guide.requirements" :key="requirement.id">
                  <div class="d-flex flex-wrap align-center ga-2">
                    <strong>{{ requirement.name }}</strong>
                    <v-chip size="x-small" variant="tonal">
                      {{ $t(`guide.${requirement.kind}`) }}
                    </v-chip>
                  </div>
                  <p v-if="requirement.note" class="text-body-2 text-medium-emphasis mt-1 mb-0">
                    {{ requirement.note }}
                  </p>
                </li>
              </ul>
            </section>

            <section
              v-if="guide.notes"
              class="guide-section guide-support-card pa-5"
              aria-labelledby="guide-notes-heading"
            >
              <h2 id="guide-notes-heading" class="text-h5 font-weight-bold mb-3">
                {{ $t("guide.notes") }}
              </h2>
              <p class="text-body-1 guide-notes mb-0">
                {{ guide.notes }}
              </p>
            </section>
          </aside>

          <section class="guide-section guide-procedure" aria-labelledby="guide-steps-heading">
            <h2 id="guide-steps-heading" class="text-h4 font-weight-bold mb-5">
              {{ $t("guide.steps") }}
            </h2>
            <ol v-if="guide.steps?.length" class="guide-steps">
              <li v-for="(step, index) in guide.steps" :key="step.id" class="guide-step pa-5 pa-sm-6">
                <div class="guide-step-heading">
                  <span class="guide-step-number" aria-hidden="true">{{ index + 1 }}</span>
                  <h3 class="text-h6 font-weight-bold mb-0 guide-step-text">
                    {{ step.text }}
                  </h3>
                </div>
                <v-alert v-if="step.tip" type="info" variant="tonal" density="compact" class="mt-4 guide-tip">
                  <strong>{{ $t("guide.tip") }}:</strong> {{ step.tip }}
                </v-alert>
                <div v-if="step.images?.length" class="guide-step-images mt-4">
                  <figure v-for="image in step.images" :key="image.id" class="ma-0 guide-step-figure">
                    <GuideMediaImage
                      :guide-slug="guide.slug"
                      :step-id="step.id"
                      :image-id="image.id"
                      :version="image.version"
                      :alt="image.altText || image.caption || ''"
                      size="small"
                    />
                    <figcaption v-if="image.caption" class="text-body-2 text-medium-emphasis mt-2">
                      {{ image.caption }}
                    </figcaption>
                  </figure>
                </div>
              </li>
            </ol>
            <p v-else class="text-medium-emphasis">
              {{ $t("guide.no-steps") }}
            </p>
          </section>
        </div>

        <section v-if="guide.sources?.length" class="guide-section mt-9" aria-labelledby="guide-sources-heading">
          <v-divider class="mb-7" />
          <h2 id="guide-sources-heading" class="text-h5 font-weight-bold mb-3">
            {{ $t("guide.sources") }}
          </h2>
          <v-list density="compact" class="pa-0 guide-sources">
            <v-list-item
              v-for="source in guide.sources"
              :key="source.id"
              :title="source.label"
              :subtitle="source.url"
              :href="source.url"
              target="_blank"
              rel="noopener noreferrer"
              :prepend-icon="$globals.icons.link"
            />
          </v-list>
        </section>

        <section
          v-if="guide.relatedGuides?.length"
          class="guide-section mt-9 guide-related"
          aria-labelledby="guide-related-heading"
        >
          <v-divider class="mb-7" />
          <h2 id="guide-related-heading" class="text-h5 font-weight-bold mb-3">
            {{ $t("guide.related-guides") }}
          </h2>
          <v-row density="compact">
            <v-col v-for="related in guide.relatedGuides" :key="related.id" cols="12" sm="6">
              <v-card :to="`/g/${groupSlug}/guides/${related.slug}`" variant="outlined" hover>
                <v-card-title class="text-subtitle-1 text-wrap">
                  {{ related.title }}
                </v-card-title>
                <v-card-subtitle v-if="related.guideType">
                  {{ $t(`guide.types.${related.guideType.replace('_', '-')}`) }}
                </v-card-subtitle>
              </v-card>
            </v-col>
          </v-row>
        </section>

        <div v-if="canEdit" class="d-print-none d-flex justify-end mt-8">
          <v-btn color="error" variant="text" :prepend-icon="$globals.icons.delete" @click="$emit('delete')">
            {{ $t("general.delete") }}
          </v-btn>
        </div>
      </div>
    </v-card>

    <footer class="guide-print-footer">
      {{ brand.name }} · {{ guide.title }}
    </footer>
  </article>
</template>

<script setup lang="ts">
import type { GuideRead } from "~/lib/api/types/guide";
import { guideReviewState } from "~/composables/guides/use-guide-review";
import { getGuideTotalMinutes, splitGuideCallouts } from "~/lib/guide-reader";

const props = defineProps<{
  guide: GuideRead;
  groupSlug: string;
  canEdit: boolean;
}>();

defineEmits<{
  edit: [];
  delete: [];
}>();

const i18n = useI18n();
const brand = useAppBrand();
const titleId = computed(() => `guide-title-${props.guide.id}`);
const callouts = computed(() => splitGuideCallouts(props.guide.callouts));
const warnings = computed(() => callouts.value.warnings);
const avoids = computed(() => callouts.value.avoids);
const totalMinutes = computed(() => getGuideTotalMinutes(props.guide));
const hasSupportingContent = computed(() => Boolean(props.guide.requirements?.length || props.guide.notes));
const reviewState = computed(() => guideReviewState(props.guide.lastReviewed));
const reviewDateLabel = computed(() => {
  if (!props.guide.lastReviewed) return "";
  return new Intl.DateTimeFormat(i18n.locale.value, { dateStyle: "medium", timeZone: "UTC" })
    .format(new Date(`${props.guide.lastReviewed}T00:00:00Z`));
});

function printGuide() {
  window.print();
}
</script>

<style scoped>
.guide-reader-card {
  overflow: hidden;
}

.guide-cover {
  max-height: 520px;
  overflow: hidden;
}

.guide-reader-header {
  background:
    radial-gradient(circle at top right, rgb(var(--v-theme-secondary), 0.18), transparent 32%),
    linear-gradient(145deg, rgb(var(--v-theme-primary), 0.08), transparent 55%);
}

.guide-title {
  line-height: 1.08;
  text-wrap: balance;
}

.guide-description,
.guide-notes,
.guide-callout,
.guide-tip,
.guide-step-text {
  white-space: pre-wrap;
}

.guide-content-grid {
  display: grid;
  grid-template-columns: minmax(230px, 0.72fr) minmax(0, 2fr);
  gap: 2rem;
  align-items: start;
}

.guide-content-grid--single {
  grid-template-columns: minmax(0, 1fr);
}

.guide-sidebar {
  display: grid;
  gap: 1rem;
  position: sticky;
  top: 5rem;
}

.guide-support-card,
.guide-step {
  border: 1px solid rgb(var(--v-theme-on-surface), 0.12);
  border-radius: 16px;
}

.guide-support-card {
  background: rgb(var(--v-theme-primary), 0.045);
}

.guide-requirements,
.guide-steps {
  list-style: none;
  margin: 0;
  padding: 0;
}

.guide-requirements {
  display: grid;
  gap: 1rem;
}

.guide-steps {
  display: grid;
  gap: 1.25rem;
}

.guide-step-heading {
  display: grid;
  grid-template-columns: 2.25rem minmax(0, 1fr);
  gap: 0.9rem;
  align-items: start;
}

.guide-step-number {
  display: inline-grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 999px;
  color: rgb(var(--v-theme-on-primary));
  background: rgb(var(--v-theme-primary));
  font-weight: 800;
}

.guide-step-images {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  padding-left: 3.15rem;
}

.guide-step-figure {
  min-width: 0;
}

.guide-print-footer {
  display: none;
}

@media (max-width: 759px) {
  .guide-content-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .guide-sidebar {
    position: static;
  }

  .guide-actions {
    width: 100%;
  }

  .guide-step-images {
    grid-template-columns: minmax(0, 1fr);
    padding-left: 0;
  }
}

@media print {
  @page {
    margin: 14mm;
  }

  .guide-reader {
    color: #111 !important;
    background: #fff !important;
  }

  .guide-reader-card {
    color: #111 !important;
    background: #fff !important;
    box-shadow: none !important;
    border-radius: 0 !important;
    overflow: visible;
  }

  .guide-cover {
    max-height: 70mm;
    border-radius: 0;
  }

  .guide-reader-header,
  .guide-reader-body {
    padding-left: 0 !important;
    padding-right: 0 !important;
    background: transparent !important;
  }

  .guide-title {
    font-size: 26pt !important;
  }

  .guide-content-grid {
    display: block;
  }

  .guide-sidebar {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    position: static;
    margin-bottom: 8mm;
  }

  .guide-support-card,
  .guide-step,
  .guide-callout,
  .guide-tip,
  .guide-step-figure,
  .guide-related :deep(.v-card) {
    break-inside: avoid;
  }

  .guide-support-card,
  .guide-step {
    border-color: #999;
    background: transparent;
  }

  .guide-step-images {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  :deep(.v-chip) {
    color: #111 !important;
    background: transparent !important;
    border: 1px solid #777 !important;
  }

  :deep(.v-alert) {
    color: #111 !important;
    background: transparent !important;
    border: 1px solid #777;
  }

  :deep(.text-medium-emphasis),
  :deep(.v-list-item-subtitle),
  :deep(.v-card-subtitle) {
    color: #444 !important;
    opacity: 1 !important;
  }

  .guide-print-footer {
    display: block;
    margin-top: 10mm;
    padding-top: 4mm;
    border-top: 1px solid #aaa;
    color: #555;
    font-size: 9pt;
  }
}
</style>
