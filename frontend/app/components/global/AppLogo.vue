<template>
  <div class="icon-container">
    <v-divider class="icon-divider" />
    <v-avatar
      :class="['pa-2', 'icon-avatar']"
      color="primary"
      :size="size"
    >
      <slot>
        <v-icon color="white" :size="size * 0.68">
          {{ $globals.icons.primary }}
        </v-icon>
      </slot>
    </v-avatar>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ size?: number }>(), { size: 75 });
</script>

<style scoped>
.icon-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
  margin-top: 2.5rem;
}
.icon-divider {
  width: 100%;
  margin-bottom: -2.5rem;
}
.icon-avatar {
  border-color: rgba(0, 0, 0, 0.12);
  border: 2px;
}
</style>
