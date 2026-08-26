<template>
  <v-card :to="to" hover height="100%" class="d-flex flex-column">
    <v-card-title class="d-flex align-center ga-2">
      <v-icon color="primary">
        {{ $globals.icons.book }}
      </v-icon>
      <span class="text-wrap">{{ guide.title }}</span>
    </v-card-title>
    <v-card-text class="flex-grow-1">
      <div
        v-if="guide.guideType || guide.difficulty || guide.frequency || guide.category"
        class="d-flex flex-wrap ga-1 mb-3"
      >
        <v-chip v-if="guide.guideType" color="primary" size="small" variant="tonal">
          {{ $t(`guide.types.${guide.guideType.replace('_', '-')}`) }}
        </v-chip>
        <v-chip v-if="guide.difficulty" size="small" variant="tonal">
          {{ $t(`guide.difficulties.${guide.difficulty}`) }}
        </v-chip>
        <v-chip v-if="guide.frequency" size="small" variant="tonal">
          {{ $t(`guide.frequencies.${guide.frequency.replace('_', '-')}`) }}
        </v-chip>
        <v-chip v-if="guide.category" size="small" variant="outlined">
          {{ guide.category.name }}
        </v-chip>
      </div>
      <p v-if="guide.description" class="text-body-2 text-medium-emphasis guide-description">
        {{ guide.description }}
      </p>
      <div v-if="guide.tags?.length" class="d-flex flex-wrap ga-1 mt-3">
        <v-chip v-for="tag in guide.tags" :key="tag.id" size="x-small">
          {{ tag.name }}
        </v-chip>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import type { GuideSummary } from "~/lib/api/types/guide";

defineProps<{
  guide: GuideSummary;
  to: string;
}>();
</script>

<style scoped>
.guide-description {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}
</style>
