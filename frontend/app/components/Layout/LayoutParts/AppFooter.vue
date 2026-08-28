<template>
  <v-footer
    color="primary"
    padless
    app
  >
    <v-row
      justify="center"
      align="center"
      density="comfortable"
      no-gutters
    >
      <v-col
        class="py-2 text-center white--text"
        cols="12"
      >
        <v-btn
          color="white"
          icon
          href="https://github.com/kheeseow/hearth"
          target="_blank"
        >
          <v-icon>
            {{ $globals.icons.github }}
          </v-icon>
        </v-btn>
        {{ new Date().getFullYear() }} — <strong>{{ brand.name }}</strong>
      </v-col>
    </v-row>
  </v-footer>
</template>

<script setup lang="ts">
const brand = useAppBrand();
</script>
