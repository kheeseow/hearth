<template>
  <v-app-bar
    clipped-left
    density="compact"
    app
    color="surface"
    class="hearth-app-header d-print-none"
  >
    <slot />
    <v-btn
      :to="routerLink"
      icon
      color="primary"
      class="hearth-app-header-logo"
      :aria-label="$t('general.product-home', { product: brand.name })"
    >
      <v-icon size="40" aria-hidden="true">
        {{ $globals.icons.primary }}
      </v-icon>
    </v-btn>

    <RouterLink
      :to="routerLink"
      class="app-header-title pl-2 hearth-app-header-brand"
    >
      <v-toolbar-title>
        {{ brand.name }}
      </v-toolbar-title>
    </RouterLink>
    <div v-if="contextLabel && smAndUp" class="hearth-header-context">
      <span>{{ $t("household.household") }}</span>
      <strong>{{ contextLabel }}</strong>
    </div>
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
        icon
        :aria-label="$vuetify.theme.current.dark ? $t('settings.theme.light-mode') : $t('settings.theme.dark-mode')"
        @click="toggleDark"
      >
        <v-icon>{{ $vuetify.theme.current.dark ? $globals.icons.weatherSunny : $globals.icons.weatherNight }}</v-icon>
      </v-btn>
      <v-btn
        v-if="loggedIn && newGuideLink && smAndUp"
        color="primary"
        variant="flat"
        :to="newGuideLink"
        :prepend-icon="$globals.icons.createAlt"
      >
        {{ $t("guide.new-guide") }}
      </v-btn>
      <v-btn
        v-if="loggedIn"
        variant="text"
        :icon="xs"
        :aria-label="xs ? $t('user.logout') : undefined"
        @click="logout()"
      >
        <v-icon :start="smAndUp">
          {{ $globals.icons.logout }}
        </v-icon>
        <span v-if="!xs" class="d-sr-only">{{ $t("user.logout") }}</span>
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
  contextLabel: {
    type: String,
    default: "",
  },
  newGuideLink: {
    type: String,
    default: "",
  },
});
const auth = useMealieAuth();
const brand = useAppBrand();
const { loggedIn } = useLoggedInState();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const { xs, smAndUp } = useDisplay();
const toggleDark = useToggleDarkMode();

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

.hearth-app-header {
  border-bottom: 1px solid rgb(var(--v-theme-outline));
  color: rgb(var(--v-theme-on-surface));
  box-shadow: none !important;
}

.hearth-header-context {
  display: grid;
  margin-left: 28px;
  line-height: 1.2;
}

.hearth-header-context span {
  color: rgb(var(--v-theme-on-surface-variant));
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.hearth-header-context strong {
  font-size: 0.95rem;
}

@media (min-width: 960px) {
  .hearth-app-header-logo,
  .hearth-app-header-brand {
    display: none;
  }
}

@media (max-width: 360px) {
  .hearth-app-header-brand {
    display: none;
  }
}
</style>
