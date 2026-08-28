<template>
  <a class="app-skip-link" href="#main-content">
    {{ $t("general.skip-to-content") }}
  </a>
</template>

<style scoped>
.app-skip-link {
  position: fixed;
  top: 0.75rem;
  left: 0.75rem;
  z-index: 3000;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  color: rgb(var(--v-theme-on-primary));
  background: rgb(var(--v-theme-primary));
  font-weight: 700;
  transform: translateY(calc(-100% - 1rem));
  transition: transform 0.15s ease;
}

.app-skip-link:focus {
  transform: translateY(0);
}
</style>
