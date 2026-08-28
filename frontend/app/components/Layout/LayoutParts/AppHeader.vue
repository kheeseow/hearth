<template>
  <v-app-bar
    clipped-left
    density="compact"
    app
    color="primary"
    dark
    class="d-print-none"
  >
    <slot />
    <v-btn
      :to="routerLink"
      icon
      color="white"
      :aria-label="$t('general.product-home', { product: brand.name })"
    >
      <v-icon size="40" aria-hidden="true">
        {{ $globals.icons.primary }}
      </v-icon>
    </v-btn>

    <RouterLink
      :to="routerLink"
      class="app-header-title pl-2"
    >
      <v-toolbar-title>
        {{ brand.name }}
      </v-toolbar-title>
    </RouterLink>
    <GuideDialogSearch ref="domSearchDialog" />

    <v-spacer />

    <!-- Navigation Menu -->
    <template v-if="menu">
      <v-responsive
        v-if="!xs && !isGuideLibrary"
        max-width="250"
        role="search"
        @click="activateSearch"
        @keydown.enter.prevent="activateSearch"
        @keydown.space.prevent="activateSearch"
      >
        <v-text-field
          readonly
          class="mt-1"
          rounded
          variant="solo-filled"
          density="compact"
          flat
          :prepend-inner-icon="$globals.icons.search"
          :aria-label="$t('guide.search')"
          bg-color="primary-darken-1"
          :placeholder="$t('search.search-hint')"
        />
      </v-responsive>
      <v-btn
        v-else
        icon
        :aria-label="$t('guide.search')"
        @click="activateSearch"
      >
        <v-icon> {{ $globals.icons.search }}</v-icon>
      </v-btn>
      <v-btn
        v-if="loggedIn"
        :variant="smAndUp ? 'text' : undefined"
        :icon="xs"
        :aria-label="xs ? $t('user.logout') : undefined"
        @click="logout()"
      >
        <v-icon :start="smAndUp">
          {{ $globals.icons.logout }}
        </v-icon>
        {{ smAndUp ? $t("user.logout") : "" }}
      </v-btn>
      <v-btn
        v-else
        variant="text"
        nuxt
        to="/login"
      >
        <v-icon start>
          {{ $globals.icons.user }}
        </v-icon>
        {{ $t("user.login") }}
      </v-btn>
    </template>
  </v-app-bar>
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type GuideDialogSearch from "~/components/Domain/Guide/GuideDialogSearch.vue";

defineProps({
  menu: {
    type: Boolean,
    default: true,
  },
});
const auth = useMealieAuth();
const brand = useAppBrand();
const { loggedIn } = useLoggedInState();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const { xs, smAndUp } = useDisplay();

const routerLink = computed(() => groupSlug.value ? `/g/${groupSlug.value}` : "/");
const isGuideLibrary = computed(() => /^\/g\/[^/]+\/guides\/?$/.test(route.path));
const domSearchDialog = ref<InstanceType<typeof GuideDialogSearch> | null>(null);

function activateSearch() {
  domSearchDialog.value?.open();
}

function handleKeyEvent(e: KeyboardEvent) {
  const activeTag = document.activeElement?.tagName;
  if (e.key === "/" && activeTag !== "INPUT" && activeTag !== "TEXTAREA") {
    e.preventDefault();
    activateSearch();
  }
}

onMounted(() => {
  document.addEventListener("keydown", handleKeyEvent);
});

onBeforeUnmount(() => {
  document.removeEventListener("keydown", handleKeyEvent);
});

async function logout() {
  try {
    await auth.signOut("/login?direct=1");
  }
  catch (e) {
    console.error(e);
  }
}
</script>

<style scoped>
.v-toolbar {
  z-index: 2010 !important;
}

.app-header-title {
  color: inherit;
  text-decoration: none;
}
</style>
