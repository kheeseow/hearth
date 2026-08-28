<template>
  <v-app dark>
    <AppSkipLink />
    <TheSnackbar />

    <v-banner
      v-if="$appInfo.demoStatus"
      sticky
    >
      <div class="text-center">
        <b> {{ $t("demo.info_message_with_version", { version: $appInfo.version }) }} </b>
      </div>
    </v-banner>

    <v-main id="main-content" tabindex="-1">
      <v-scroll-x-transition>
        <div>
          <NuxtPage />
        </div>
      </v-scroll-x-transition>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import TheSnackbar from "~/components/Layout/LayoutParts/TheSnackbar.vue";
import AppSkipLink from "~/components/Layout/LayoutParts/AppSkipLink.vue";
</script>
