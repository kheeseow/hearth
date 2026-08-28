<template>
  <v-app dark>
    <AppSkipLink />
    <TheSnackbar />

    <AppHeader :context-label="householdName" :new-guide-link="isOwnGroup ? newGuideLink : ''">
      <v-btn
        icon
        :aria-label="$t('general.menu')"
        aria-controls="app-navigation"
        :aria-expanded="sidebar"
        @click.stop="sidebar = !sidebar"
      >
        <v-icon> {{ $globals.icons.menu }}</v-icon>
      </v-btn>
    </AppHeader>

    <AppSidebar
      v-model="sidebar"
      :top-link="topLinks"
      :secondary-links="cookbookLinks || []"
    >
      <v-btn
        v-if="isOwnGroup && capabilities.guides && !capabilities.legacyRecipes"
        class="hearth-new-guide-button"
        color="primary"
        variant="flat"
        :to="newGuideLink"
        :prepend-icon="$globals.icons.createAlt"
      >
        {{ $t("guide.new-guide") }}
      </v-btn>
      <v-menu
        v-if="capabilities.legacyRecipes"
        offset-y
        nudge-bottom="5"
        close-delay="50"
        nudge-right="15"
      >
        <template #activator="{ props }">
          <v-btn
            v-if="isOwnGroup && createLinks.length"
            rounded
            size="large"
            class="hearth-legacy-create-button"
            v-bind="props"
            variant="elevated"
            elevation="2"
            :color="$vuetify.theme.current.dark ? 'background-lighten-1' : 'background-darken-1'"
          >
            <v-icon
              start
              size="large"
              color="primary"
            >
              {{ $globals.icons.createAlt }}
            </v-icon>
            {{ $t("general.create") }}
          </v-btn>
        </template>
        <v-list
          density="comfortable"
          class="mb-0 mt-1 py-0"
          variant="flat"
        >
          <template v-for="(item, index) in createLinks">
            <div
              v-if="!item.hide"
              :key="item.title"
            >
              <v-divider
                v-if="item.insertDivider"
                :key="index"
                class="mx-2"
              />
              <v-list-item
                v-if="!item.restricted || isOwnGroup"
                :key="item.title"
                :to="item.to"
                exact
                class="my-1"
              >
                <template #prepend>
                  <v-icon
                    size="40"
                    :icon="item.icon"
                  />
                </template>
                <v-list-item-title class="font-weight-medium" style="font-size: small;">
                  {{ item.title }}
                </v-list-item-title>
                <v-list-item-subtitle class="font-weight-medium" style="font-size: small;">
                  {{ item.subtitle }}
                </v-list-item-subtitle>
              </v-list-item>
            </div>
          </template>
        </v-list>
      </v-menu>
    </AppSidebar>
    <v-main id="main-content" tabindex="-1" class="hearth-main pt-12">
      <v-scroll-x-transition>
        <div>
          <NuxtPage />
        </div>
      </v-scroll-x-transition>
    </v-main>
    <nav
      v-if="display.smAndDown.value && !sidebar"
      class="hearth-mobile-nav d-print-none"
      :class="{ 'hearth-mobile-nav--two': !isOwnGroup }"
      :aria-label="$t('general.navigation')"
    >
      <NuxtLink :to="`/g/${groupSlug}/guides`">
        <v-icon aria-hidden="true">{{ $globals.icons.book }}</v-icon>
        <span>{{ $t("guide.guides") }}</span>
      </NuxtLink>
      <NuxtLink v-if="isOwnGroup" :to="newGuideLink" class="hearth-mobile-nav-primary">
        <v-icon aria-hidden="true">{{ $globals.icons.createAlt }}</v-icon>
        <span>{{ $t("general.create") }}</span>
      </NuxtLink>
      <NuxtLink to="/user/profile">
        <v-icon aria-hidden="true">{{ $globals.icons.user }}</v-icon>
        <span>{{ $t("general.settings") }}</span>
      </NuxtLink>
    </nav>
  </v-app>
</template>

<script setup lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import AppSkipLink from "~/components/Layout/LayoutParts/AppSkipLink.vue";
import type { SideBarLink } from "~/types/application-types";
import { useGroupSelf } from "~/composables/use-groups";
import { useCookbookPreferences } from "~/composables/use-users/preferences";
import { useCookbookStore, usePublicCookbookStore } from "~/composables/store/use-cookbook-store";
import type { ReadCookBook } from "~/lib/api/types/cookbook";

const i18n = useI18n();
const { $globals } = useNuxtApp();
const display = useDisplay();
const auth = useMealieAuth();
const { isOwnGroup } = useLoggedInState();
const { group } = useGroupSelf();
const capabilities = useAppCapabilities();

const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const householdName = computed(() => auth.user.value?.household || "");
const newGuideLink = computed(() => `/g/${groupSlug.value}/guides/create`);

const cookbookPreferences = useCookbookPreferences();
const ownCookbookStore = computed(() => isOwnGroup.value ? useCookbookStore(i18n) : null);
const publicCookbookStoreCache = ref<Record<string, ReturnType<typeof usePublicCookbookStore>>>({});

function getPublicCookbookStore(slug: string) {
  if (!publicCookbookStoreCache.value[slug]) {
    publicCookbookStoreCache.value[slug] = usePublicCookbookStore(slug, i18n);
  }
  return publicCookbookStoreCache.value[slug];
}

const cookbooks = computed(() => {
  if (ownCookbookStore.value) {
    return ownCookbookStore.value.store.value;
  }
  else if (groupSlug.value) {
    const publicStore = getPublicCookbookStore(groupSlug.value);
    return unref(publicStore.store);
  }
  return [];
});

const showAIImport = computed(() => group.value?.aiProviderSettings?.aiEnabled);

const sidebar = ref<boolean>(false);
onMounted(() => {
  sidebar.value = display.lgAndUp.value;
});

function cookbookAsLink(cookbook: ReadCookBook): SideBarLink {
  return {
    key: cookbook.slug || "",
    icon: $globals.icons.pages,
    title: cookbook.name,
    to: `/g/${groupSlug.value}/cookbooks/${cookbook.slug || ""}`,
    restricted: false,
  };
}

const currentUserHouseholdId = computed(() => auth.user.value?.householdId);
const cookbookLinks = computed<SideBarLink[]>(() => {
  if (!capabilities.value.legacyRecipes || !cookbooks.value?.length) {
    return [];
  }

  const sortedCookbooks = [...cookbooks.value].sort((a, b) => (a.position || 0) - (b.position || 0));

  const ownLinks: SideBarLink[] = [];
  const links: SideBarLink[] = [];
  const cookbooksByHousehold = sortedCookbooks.reduce((acc, cookbook) => {
    const householdName = cookbook.household?.name || "";
    (acc[householdName] ||= []).push(cookbook);
    return acc;
  }, {} as Record<string, ReadCookBook[]>);

  Object.entries(cookbooksByHousehold).forEach(([householdName, cookbooks]) => {
    if (!cookbooks.length) {
      return;
    }
    if (cookbooks[0].householdId === currentUserHouseholdId.value) {
      ownLinks.push(...cookbooks.map(cookbookAsLink));
    }
    else {
      links.push({
        key: householdName,
        icon: $globals.icons.book,
        title: householdName,
        children: cookbooks.map(cookbookAsLink),
        restricted: false,
      });
    }
  });

  links.sort((a, b) => a.title.localeCompare(b.title));
  if (auth.user.value && cookbookPreferences.value.hideOtherHouseholds) {
    return ownLinks;
  }
  else {
    return [...ownLinks, ...links];
  }
});

const createLinks = computed(() => [
  {
    insertDivider: false,
    icon: $globals.icons.link,
    title: i18n.t("general.import"),
    subtitle: i18n.t("new-recipe.import-by-url"),
    to: `/g/${groupSlug.value}/r/create/url`,
    restricted: true,
    hide: false,
  },
  {
    insertDivider: false,
    icon: $globals.icons.autoFix,
    title: i18n.t("recipe.import-with-ai"),
    subtitle: i18n.t("recipe.import-with-ai-subtitle"),
    to: `/g/${groupSlug.value}/r/create/ai`,
    restricted: true,
    hide: !showAIImport.value,
  },
  {
    insertDivider: true,
    icon: $globals.icons.edit,
    title: i18n.t("general.create"),
    subtitle: i18n.t("new-recipe.create-manually"),
    to: `/g/${groupSlug.value}/r/create/new`,
    restricted: true,
    hide: false,
  },
].filter(() => capabilities.value.legacyRecipes));

type CapabilitySideBarLink = SideBarLink & { enabled: boolean };

const topLinks = computed<SideBarLink[]>(() => ([
  {
    enabled: capabilities.value.legacyRecipes,
    icon: $globals.icons.silverwareForkKnife,
    to: `/g/${groupSlug.value}`,
    title: i18n.t("general.recipes"),
    restricted: false,
  },
  {
    enabled: capabilities.value.legacyRecipes,
    icon: $globals.icons.search,
    to: `/g/${groupSlug.value}/recipes/finder`,
    title: i18n.t("recipe-finder.recipe-finder"),
    restricted: false,
  },
  {
    enabled: capabilities.value.guides,
    icon: $globals.icons.book,
    to: `/g/${groupSlug.value}/guides`,
    title: i18n.t("guide.guides"),
    restricted: true,
  },
  {
    enabled: capabilities.value.mealPlanning,
    icon: $globals.icons.calendarMultiselect,
    title: i18n.t("meal-plan.meal-planner"),
    to: "/household/mealplan/planner/view",
    restricted: true,
  },
  {
    enabled: capabilities.value.shoppingLists,
    icon: $globals.icons.formatListCheck,
    title: i18n.t("shopping-list.shopping-lists"),
    to: "/shopping-lists",
    restricted: true,
  },
  {
    enabled: capabilities.value.legacyRecipes,
    icon: $globals.icons.timelineText,
    title: i18n.t("recipe.timeline"),
    to: `/g/${groupSlug.value}/recipes/timeline`,
    restricted: true,
  },
  {
    enabled: capabilities.value.legacyRecipes,
    icon: $globals.icons.book,
    to: `/g/${groupSlug.value}/cookbooks`,
    title: i18n.t("cookbook.cookbooks"),
    restricted: true,
  },
  {
    enabled: capabilities.value.legacyRecipes,
    icon: $globals.icons.organizers,
    title: i18n.t("general.organizers"),
    restricted: true,
    children: [
      {
        icon: $globals.icons.categories,
        to: `/g/${groupSlug.value}/recipes/categories`,
        title: i18n.t("sidebar.categories"),
        restricted: true,
      },
      {
        icon: $globals.icons.tags,
        to: `/g/${groupSlug.value}/recipes/tags`,
        title: i18n.t("sidebar.tags"),
        restricted: true,
      },
      {
        icon: $globals.icons.potSteam,
        to: `/g/${groupSlug.value}/recipes/tools`,
        title: i18n.t("tool.tools"),
        restricted: true,
      },
    ],
  },
] satisfies CapabilitySideBarLink[]).filter(link => link.enabled));
</script>

<style scoped>
.hearth-new-guide-button {
  width: calc(100% - 32px);
  min-height: 48px;
  margin: 8px 16px 12px;
  border-radius: 12px;
}

.hearth-legacy-create-button {
  margin: 12px 16px 16px;
}

.hearth-mobile-nav {
  display: none;
}

@media (max-width: 959px) {
  .hearth-main {
    padding-bottom: 84px;
  }
  .hearth-mobile-nav {
    position: fixed;
    z-index: 2020;
    right: 12px;
    bottom: 10px;
    left: 12px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    padding: 6px;
    border: 1px solid rgb(var(--v-theme-outline));
    border-radius: 18px;
    background: rgb(var(--v-theme-surface));
    box-shadow: 0 14px 36px rgb(38 33 28 / 18%);
  }

  .hearth-mobile-nav a {
    display: flex;
    min-height: 52px;
    align-items: center;
    justify-content: center;
    gap: 4px;
    border-radius: 12px;
    color: rgb(var(--v-theme-on-surface-variant));
    font-size: 0.72rem;
    font-weight: 700;
    text-decoration: none;
  }

  .hearth-mobile-nav--two {
    grid-template-columns: repeat(2, 1fr);
  }

  .hearth-mobile-nav-primary {
    color: rgb(var(--v-theme-primary)) !important;
  }
  .hearth-mobile-nav .router-link-exact-active {
    background: rgb(var(--v-theme-primary), 0.12);
  }
}
</style>
