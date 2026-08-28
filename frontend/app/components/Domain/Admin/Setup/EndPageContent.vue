<template>
  <v-container max-width="880" class="end-page-content">
    <div class="d-flex flex-column ga-6">
      <header class="setup-complete-header">
        <p>{{ brand.name }}</p>
        <v-card-title class="text-h4 justify-center">
          {{ $t('admin.setup.setup-complete') }}
        </v-card-title>
        <v-card-subtitle class="justify-center">
          {{ $t('admin.setup.here-are-a-few-things-to-help-you-get-started') }}
        </v-card-subtitle>
      </header>
      <div
        v-for="section, idx in sections"
        :key="idx"
        class="d-flex flex-column ga-3"
      >
        <v-card-title class="text-h6 pl-0">
          {{ section.title }}
        </v-card-title>
        <div class="sections d-flex flex-column ga-2">
          <v-card
            v-for="link, linkIdx in section.links"
            :key="linkIdx"
            class="link-card"
            :class="{ 'link-card--primary': !capabilities.legacyRecipes && idx === 0 && linkIdx === 0 }"
            :to="link.to"
            :title="link.text"
            :subtitle="link.description"
            :append-icon="$globals.icons.chevronRight"
          >
            <template #prepend>
              <v-avatar :icon="link.icon || undefined" variant="tonal" :color="section.color" />
            </template>
          </v-card>
        </div>
      </div>
    </div>
  </v-container>
</template>

<script setup lang="ts">
const i18n = useI18n();
const auth = useMealieAuth();
const groupSlug = computed(() => auth.user.value?.groupSlug);
const { $globals } = useNuxtApp();
const capabilities = useAppCapabilities();
const brand = useAppBrand();

const sections = ref([
  {
    title: i18n.t("profile.data-migrations"),
    color: "info",
    links: [
      {
        icon: $globals.icons.backupRestore,
        to: "/admin/backups",
        text: i18n.t("settings.backup.backup-restore"),
        description: i18n.t("admin.setup.restore-from-v1-backup"),
      },
      {
        icon: $globals.icons.import,
        to: "/group/migrations",
        text: i18n.t("migration.recipe-migration"),
        description: i18n.t("migration.coming-from-another-application-or-an-even-older-version-of-mealie"),
      },
    ],
  },
  {
    title: i18n.t("recipe.create-recipes"),
    color: "success",
    links: [
      {
        icon: $globals.icons.createAlt,
        to: computed(() => `/g/${groupSlug.value || ""}/r/create/new`),
        text: i18n.t("recipe.create-recipe"),
        description: i18n.t("recipe.create-recipe-description"),
      },
      {
        icon: $globals.icons.link,
        to: computed(() => `/g/${groupSlug.value || ""}/r/create/url`),
        text: i18n.t("recipe.import-with-url"),
        description: i18n.t("recipe.scrape-recipe-description"),
      },
    ],
  },
  {
    title: i18n.t("user.manage-users"),
    color: "primary",
    links: [
      {
        icon: $globals.icons.group,
        to: "/admin/manage/users",
        text: i18n.t("user.manage-users"),
        description: i18n.t("user.manage-users-description"),
      },
      {
        icon: $globals.icons.user,
        to: "/user/profile",
        text: i18n.t("profile.manage-user-profile"),
        description: i18n.t("admin.setup.manage-profile-or-get-invite-link"),
      },
    ],
  },
]);

if (!capabilities.value.legacyRecipes) {
  sections.value = [
    {
      title: i18n.t("guide.create-guides"),
      color: "success",
      links: [
        {
          icon: $globals.icons.createAlt,
          to: computed(() => `/g/${groupSlug.value || ""}/guides/create`),
          text: i18n.t("guide.new-guide"),
          description: i18n.t("guide.create-guide-description"),
        },
      ],
    },
    sections.value[2],
  ];
}
</script>

<style scoped>
.end-page-content {
  padding-block: 48px 72px;
}
.setup-complete-header {
  max-width: 640px;
  margin-inline: auto;
  text-align: center;
}
.setup-complete-header p {
  margin-bottom: 12px;
  color: rgb(var(--v-theme-primary));
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.end-page-content :deep(.v-card-title),
.end-page-content :deep(.v-card-subtitle) {
  padding: 0;
  white-space: unset;
}
.end-page-content :deep(.v-card-item) {
  gap: 0.5rem;
}
.link-card {
  min-height: 88px;
  padding: 8px;
  border: 1px solid rgb(var(--v-theme-outline));
  background: rgb(var(--v-theme-surface));
}
.link-card--primary {
  min-height: 112px;
  border-color: rgb(var(--v-theme-primary), 0.45);
  background: rgb(var(--v-theme-primary), 0.09);
  box-shadow: 0 12px 30px rgb(38 33 28 / 8%);
}

@media (max-width: 599px) {
  .end-page-content {
    padding: 32px 12px 88px;
  }
}
</style>
