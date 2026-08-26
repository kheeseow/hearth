<template>
  <v-card :to="to" hover height="100%" class="d-flex flex-column">
    <v-card-title class="d-flex align-center ga-2">
      <v-icon color="primary">
        {{ $globals.icons.book }}
      </v-icon>
      <span class="text-wrap">{{ guide.title }}</span>
    </v-card-title>
    <v-card-text class="flex-grow-1">
      <p v-if="guide.description" class="text-body-2 text-medium-emphasis guide-description">
        {{ guide.description }}
      </p>
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
