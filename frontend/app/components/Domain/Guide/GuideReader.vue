<template>
  <article class="guide-reader" :aria-labelledby="titleId">
    <div class="guide-reader-toolbar d-print-none">
      <v-btn variant="text" :prepend-icon="$globals.icons.backArrow" :to="`/g/${groupSlug}/guides`">
        {{ $t("guide.back-to-guides") }}
      </v-btn>
      <div class="guide-reader-actions">
        <v-btn variant="outlined" :prepend-icon="$globals.icons.printer" @click="printGuide">
          {{ $t("guide.print-guide") }}
        </v-btn>
        <v-btn v-if="canEdit" variant="outlined" :prepend-icon="$globals.icons.edit" @click="$emit('edit')">
          {{ $t("general.edit") }}
        </v-btn>
      </div>
    </div>

    <header class="guide-reader-hero">
      <div>
        <p v-if="classification" class="guide-eyebrow">
          {{ classification }}
        </p>
        <h1 :id="titleId" class="guide-reader-title">
          {{ guide.title }}
        </h1>
        <p v-if="guide.description" class="guide-reader-outcome">
          {{ guide.description }}
        </p>
        <div class="guide-reader-metadata" :aria-label="$t('guide.guide-summary')">
          <span v-if="totalMinutes">
            <v-icon size="18" aria-hidden="true">{{ $globals.icons.clockOutline }}</v-icon>
            {{ $t("guide.total-minutes", { count: totalMinutes }) }}
          </span>
          <span v-if="guide.difficulty">
            <v-icon size="18" aria-hidden="true">{{ $globals.icons.chartLine }}</v-icon>
            {{ $t(`guide.difficulties.${guide.difficulty}`) }}
          </span>
          <span :class="{ 'text-warning': reviewState === 'stale', 'text-success': reviewState === 'current' }">
            <v-icon size="18" aria-hidden="true">{{ $globals.icons.calendar }}</v-icon>
            {{ reviewLabel }}
          </span>
        </div>
      </div>

      <div class="guide-reader-visual">
        <GuideMediaImage
          v-if="guide.coverImageVersion"
          :guide-slug="guide.slug"
          :version="guide.coverImageVersion"
          :alt="guide.title"
          size="original"
          class="guide-reader-cover"
        />
        <v-icon v-else size="76" aria-hidden="true">
          {{ $globals.icons.book }}
        </v-icon>
      </div>
    </header>

    <section v-if="warnings.length || avoids.length" class="guide-safety-panel" aria-labelledby="guide-safety-heading">
      <h2 id="guide-safety-heading">
        <v-icon aria-hidden="true">
          {{ $globals.icons.alert }}
        </v-icon>
        {{ $t("guide.safety") }}
      </h2>
      <div class="guide-safety-grid">
        <div v-for="warning in warnings" :key="warning.id">
          <strong>{{ $t("guide.warning") }}</strong>
          <p>{{ warning.text }}</p>
        </div>
        <div v-for="avoid in avoids" :key="avoid.id">
          <strong>{{ $t("guide.thing-to-avoid") }}</strong>
          <p>{{ avoid.text }}</p>
        </div>
      </div>
    </section>

    <div class="guide-reader-layout" :class="{ 'guide-reader-layout--single': !hasSupportingContent }">
      <aside v-if="hasSupportingContent" class="guide-before-card">
        <section v-if="guide.requirements?.length" aria-labelledby="guide-requirements-heading">
          <p class="guide-eyebrow">
            {{ $t("guide.preparation") }}
          </p>
          <h2 id="guide-requirements-heading">
            {{ $t("guide.before-you-start") }}
          </h2>
          <ul class="guide-requirements">
            <li v-for="requirement in guide.requirements" :key="requirement.id">
              <v-icon size="18" color="success" aria-hidden="true">
                {{ $globals.icons.check }}
              </v-icon>
              <span>
                <strong>{{ requirement.name }}</strong>
                <small v-if="requirement.note">{{ requirement.note }}</small>
              </span>
            </li>
          </ul>
        </section>
        <section v-if="guide.notes" class="guide-reader-notes" aria-labelledby="guide-notes-heading">
          <h2 id="guide-notes-heading">
            {{ $t("guide.notes") }}
          </h2>
          <p>{{ guide.notes }}</p>
        </section>
      </aside>

      <section class="guide-procedure" aria-labelledby="guide-steps-heading">
        <p class="guide-eyebrow">
          {{ $t("guide.procedure") }}
        </p>
        <h2 id="guide-steps-heading">
          {{ $t("guide.clear-steps-count", guide.steps?.length || 0) }}
        </h2>
        <ol v-if="guide.steps?.length" class="guide-steps">
          <li v-for="(step, index) in guide.steps" :key="step.id" class="guide-step">
            <span class="guide-step-number" aria-hidden="true">{{ index + 1 }}</span>
            <div>
              <h3>{{ step.text }}</h3>
              <div v-if="step.tip" class="guide-tip">
                <strong>{{ $t("guide.tip") }}:</strong> {{ step.tip }}
              </div>
              <div v-if="step.images?.length" class="guide-step-images">
                <figure v-for="image in step.images" :key="image.id">
                  <GuideMediaImage
                    :guide-slug="guide.slug"
                    :step-id="step.id"
                    :image-id="image.id"
                    :version="image.version"
                    :alt="image.altText || image.caption || ''"
                    size="small"
                  />
                  <figcaption v-if="image.caption">
                    {{ image.caption }}
                  </figcaption>
                </figure>
              </div>
            </div>
          </li>
        </ol>
        <p v-else class="text-medium-emphasis">
          {{ $t("guide.no-steps") }}
        </p>
      </section>
    </div>

    <section v-if="guide.sources?.length" class="guide-reader-secondary" aria-labelledby="guide-sources-heading">
      <h2 id="guide-sources-heading">
        {{ $t("guide.sources") }}
      </h2>
      <v-list density="compact" class="pa-0 bg-transparent">
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

    <section v-if="guide.relatedGuides?.length" class="guide-reader-secondary" aria-labelledby="guide-related-heading">
      <h2 id="guide-related-heading">
        {{ $t("guide.related-guides") }}
      </h2>
      <div class="guide-related-grid">
        <v-card v-for="related in guide.relatedGuides" :key="related.id" :to="`/g/${groupSlug}/guides/${related.slug}`" variant="outlined" class="pa-4">
          <h3>{{ related.title }}</h3>
          <p v-if="related.guideType" class="mb-0 text-medium-emphasis">
            {{ $t(`guide.types.${related.guideType.replace('_', '-')}`) }}
          </p>
        </v-card>
      </div>
    </section>

    <section v-if="guide.frequency || guide.tags?.length" class="guide-reader-secondary" aria-labelledby="guide-details-heading">
      <h2 id="guide-details-heading">
        {{ $t("guide.guide-details") }}
      </h2>
      <div class="d-flex flex-wrap ga-2">
        <v-chip v-if="guide.frequency" variant="tonal">
          {{ $t(`guide.frequencies.${guide.frequency.replace('_', '-')}`) }}
        </v-chip>
        <v-chip v-for="tag in guide.tags" :key="tag.id" variant="outlined">
          {{ tag.name }}
        </v-chip>
      </div>
    </section>

    <div v-if="canEdit" class="guide-delete-action d-print-none">
      <v-btn color="error" variant="text" :prepend-icon="$globals.icons.delete" @click="$emit('delete')">
        {{ $t("general.delete") }}
      </v-btn>
    </div>
    <footer class="guide-print-footer">
      {{ brand.name }} · {{ guide.title }}
    </footer>
  </article>
</template>

<script setup lang="ts">
import type { GuideRead } from "~/lib/api/types/guide";
import { guideReviewState } from "~/composables/guides/use-guide-review";
import { getGuideTotalMinutes, splitGuideCallouts } from "~/lib/guide-reader";

const props = defineProps<{ guide: GuideRead; groupSlug: string; canEdit: boolean }>();
defineEmits<{ edit: []; delete: [] }>();

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
const reviewLabel = computed(() => {
  if (!props.guide.lastReviewed) return i18n.t("guide.not-reviewed");
  return reviewState.value === "stale"
    ? i18n.t("guide.review-overdue", { date: reviewDateLabel.value })
    : i18n.t("guide.reviewed-on", { date: reviewDateLabel.value });
});
const classification = computed(() => [
  props.guide.category?.name,
  props.guide.guideType ? i18n.t(`guide.types.${props.guide.guideType.replace("_", "-")}`) : "",
].filter(Boolean).join(" · "));

function printGuide() { window.print(); }
</script>

<style scoped>
.guide-reader {
  max-width: 1120px;
  margin: 0 auto;
  padding: 32px 20px 96px;
}
.guide-reader-toolbar,
.guide-reader-actions,
.guide-reader-metadata {
  display: flex;
  align-items: center;
}
.guide-reader-toolbar {
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 40px;
}
.guide-reader-actions {
  gap: 12px;
}
.guide-reader-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 48px;
  align-items: center;
  margin-bottom: 48px;
}
.guide-eyebrow {
  margin: 0 0 10px;
  color: rgb(var(--v-theme-primary));
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.guide-reader-title {
  max-width: 15ch;
  margin-bottom: 16px;
  font-size: clamp(2.5rem, 2rem + 2.5vw, 4rem);
  font-weight: 770;
  letter-spacing: -0.045em;
  line-height: 1.04;
  text-wrap: balance;
}
.guide-reader-outcome {
  max-width: 60ch;
  margin-bottom: 0;
  color: rgb(var(--v-theme-on-surface), 0.72);
  font-size: clamp(17px, 1.5vw, 19px);
  line-height: 1.65;
  white-space: pre-wrap;
}
.guide-reader-metadata {
  flex-wrap: wrap;
  gap: 8px 18px;
  margin-top: 20px;
  color: rgb(var(--v-theme-on-surface), 0.72);
  font-size: 14px;
  font-weight: 650;
}
.guide-reader-metadata span {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.guide-reader-visual {
  display: grid;
  aspect-ratio: 4 / 3;
  place-items: center;
  overflow: hidden;
  border-radius: 24px;
  background:
    radial-gradient(circle at 75% 24%, rgb(var(--v-theme-surface), 0.68) 0 12%, transparent 13%),
    linear-gradient(145deg, rgb(var(--v-theme-primary), 0.12), rgb(var(--v-theme-accent), 0.3));
  color: rgb(var(--v-theme-accent));
  box-shadow:
    0 10px 30px rgb(49 37 26 / 10%),
    0 2px 8px rgb(49 37 26 / 6%);
}
.guide-reader-cover {
  width: 100%;
  height: 100%;
}
.guide-safety-panel {
  margin-bottom: 40px;
  padding: 24px;
  border: 1px solid rgb(var(--v-theme-error), 0.38);
  border-radius: 16px;
  background: rgb(var(--v-theme-error), 0.1);
}
.guide-safety-panel h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  color: rgb(var(--v-theme-error));
  font-size: 23px;
  font-weight: 740;
}
.guide-safety-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px 32px;
  margin-top: 18px;
}
.guide-safety-grid strong {
  display: block;
  margin-bottom: 4px;
  color: rgb(var(--v-theme-error));
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.guide-safety-grid p {
  margin: 0;
  line-height: 1.55;
  white-space: pre-wrap;
}
.guide-reader-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 48px;
  align-items: start;
}
.guide-reader-layout--single {
  grid-template-columns: minmax(0, 1fr);
}
.guide-before-card {
  position: sticky;
  top: 96px;
  padding: 22px;
  border: 1px solid rgb(var(--v-theme-on-surface), 0.16);
  border-radius: 16px;
  background: rgb(var(--v-theme-surface));
  box-shadow:
    0 1px 2px rgb(49 37 26 / 8%),
    0 3px 10px rgb(49 37 26 / 5%);
}
.guide-before-card h2,
.guide-reader-notes h2 {
  margin-bottom: 8px;
  font-size: 21px;
  font-weight: 740;
  letter-spacing: -0.02em;
}
.guide-requirements {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}
.guide-requirements li {
  display: flex;
  gap: 10px;
  color: rgb(var(--v-theme-on-surface), 0.72);
  font-size: 14px;
}
.guide-requirements strong,
.guide-requirements small {
  display: block;
}
.guide-requirements strong {
  color: rgb(var(--v-theme-on-surface));
}
.guide-reader-notes {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgb(var(--v-theme-on-surface), 0.14);
}
.guide-reader-notes p {
  margin: 0;
  color: rgb(var(--v-theme-on-surface), 0.72);
  line-height: 1.6;
  white-space: pre-wrap;
}
.guide-procedure > h2,
.guide-reader-secondary > h2 {
  margin-bottom: 24px;
  font-size: clamp(24px, 2.4vw, 32px);
  font-weight: 740;
  letter-spacing: -0.03em;
  line-height: 1.15;
}
.guide-steps {
  margin: 0;
  padding: 0;
  list-style: none;
}
.guide-step {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr);
  gap: 18px;
  padding: 0 0 32px;
}
.guide-step + .guide-step {
  padding-top: 32px;
  border-top: 1px solid rgb(var(--v-theme-on-surface), 0.14);
}
.guide-step-number {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border: 1px solid rgb(var(--v-theme-primary), 0.48);
  border-radius: 50%;
  background: rgb(var(--v-theme-primary), 0.11);
  color: rgb(var(--v-theme-primary));
  font-size: 17px;
  font-weight: 800;
}
.guide-step h3 {
  max-width: 48ch;
  margin: 5px 0 0;
  font-size: 21px;
  font-weight: 720;
  line-height: 1.35;
  white-space: pre-wrap;
}
.guide-tip {
  max-width: 65ch;
  margin-top: 16px;
  padding: 14px 16px;
  border-left: 3px solid rgb(var(--v-theme-accent));
  border-radius: 0 10px 10px 0;
  background: rgb(var(--v-theme-accent), 0.12);
  font-size: 14px;
}
.guide-step-images {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-top: 20px;
}
.guide-step-images figure {
  min-width: 0;
  margin: 0;
}
.guide-step-images figcaption {
  margin-top: 8px;
  color: rgb(var(--v-theme-on-surface), 0.72);
  font-size: 14px;
}
.guide-reader-secondary {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid rgb(var(--v-theme-on-surface), 0.14);
}
.guide-related-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.guide-related-grid h3 {
  font-size: 18px;
}
.guide-delete-action {
  display: flex;
  justify-content: flex-end;
  margin-top: 32px;
}
.guide-print-footer {
  display: none;
}
@media (max-width: 900px) {
  .guide-reader-hero {
    grid-template-columns: minmax(0, 1fr) 290px;
    gap: 32px;
  }
  .guide-reader-layout {
    grid-template-columns: 240px minmax(0, 1fr);
    gap: 32px;
  }
}
@media (max-width: 760px) {
  .guide-reader {
    padding: 24px 18px 108px;
  }
  .guide-reader-toolbar {
    margin-bottom: 28px;
  }
  .guide-reader-actions :deep(.v-btn__content) {
    font-size: 0;
  }
  .guide-reader-actions :deep(.v-icon) {
    margin: 0;
  }
  .guide-reader-actions {
    gap: 6px;
  }
  .guide-reader-actions :deep(.v-btn) {
    width: 44px;
    min-width: 44px;
    padding-inline: 0;
  }
  .guide-reader-hero {
    display: block;
    margin-bottom: 28px;
  }
  .guide-reader-title {
    font-size: clamp(2.375rem, 11vw, 3.125rem);
  }
  .guide-reader-visual {
    display: none;
  }
  .guide-safety-panel {
    margin-bottom: 24px;
    padding: 20px;
  }
  .guide-safety-grid {
    grid-template-columns: 1fr;
  }
  .guide-reader-layout {
    display: flex;
    flex-direction: column;
    gap: 28px;
  }
  .guide-before-card,
  .guide-procedure {
    width: 100%;
  }
  .guide-before-card {
    position: static;
  }
  .guide-step {
    grid-template-columns: 40px minmax(0, 1fr);
    gap: 14px;
  }
  .guide-step-number {
    width: 38px;
    height: 38px;
  }
  .guide-step h3 {
    margin-top: 3px;
    font-size: 20px;
  }
  .guide-step-images,
  .guide-related-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 360px) {
  .guide-reader-toolbar {
    gap: 8px;
  }
  .guide-reader-toolbar > :deep(.v-btn) {
    padding-inline: 6px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .guide-reader :deep(*) {
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
@media print {
  @page {
    margin: 14mm;
  }
  .guide-reader {
    max-width: none;
    padding: 0;
    color: #111 !important;
    background: #fff !important;
  }
  .guide-reader-hero {
    display: block;
    margin-bottom: 8mm;
  }
  .guide-reader-title {
    font-size: 26pt !important;
  }
  .guide-reader-visual {
    display: none;
  }
  .guide-safety-panel,
  .guide-before-card,
  .guide-step,
  .guide-step-images figure,
  .guide-related-grid :deep(.v-card) {
    break-inside: avoid;
  }
  .guide-safety-panel,
  .guide-before-card {
    color: #111 !important;
    background: transparent !important;
    border-color: #777;
    box-shadow: none;
  }
  .guide-reader-layout {
    display: block;
  }
  .guide-before-card {
    position: static;
    margin-bottom: 8mm;
  }
  .guide-reader-secondary {
    margin-top: 8mm;
    padding-top: 5mm;
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
