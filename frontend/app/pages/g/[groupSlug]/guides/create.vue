<template>
  <v-container class="guide-container">
    <v-btn variant="text" :prepend-icon="$globals.icons.backArrow" :to="`/g/${groupSlug}/guides`">
      {{ $t("guide.back-to-guides") }}
    </v-btn>
    <header class="guide-editor-header">
      <p>{{ $t("guide.create-guides") }}</p>
      <h1>
        {{ $t("guide.new-guide") }}
      </h1>
      <span>{{ $t("guide.create-guide-description") }}</span>
    </header>
    <GuideEditor
      v-model="draft"
      :loading="loading"
      :error="error"
      @save="save"
      @dirty-change="hasUnsavedChanges = $event"
    />
  </v-container>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import GuideEditor, { type GuideDraft } from "~/components/Domain/Guide/GuideEditor.vue";
import { guideNavigationCanProceed, guideSaveCanStart } from "~/lib/guide-editor";

definePageMeta({ middleware: ["group-only"] });

const i18n = useI18n();
useSeoMeta({ title: i18n.t("guide.new-guide") });

const route = useRoute();
const router = useRouter();
const groupSlug = computed(() => route.params.groupSlug as string);
const api = useUserApi();
const loading = ref(false);
const error = ref("");
const hasUnsavedChanges = ref(false);
const allowNavigation = ref(false);
const { activateNavigationWarning, deactivateNavigationWarning } = useNavigationWarning();
const draft = ref<GuideDraft>({
  title: "",
  description: "",
  guideType: null,
  difficulty: null,
  frequency: null,
  preparationMinutes: null,
  executionMinutes: null,
  notes: null,
  lastReviewed: null,
  category: null,
  tags: [],
  steps: [{ text: "" }],
  callouts: [],
  requirements: [],
  sources: [],
  relatedGuideIds: [],
});

async function save() {
  if (!guideSaveCanStart(loading.value)) return;
  loading.value = true;
  error.value = "";
  try {
    const { data } = await api.guides.createOne(draft.value);
    if (data) {
      allowNavigation.value = true;
      hasUnsavedChanges.value = false;
      await router.push(`/g/${groupSlug.value}/guides/${data.slug}`);
    }
    else {
      error.value = i18n.t("guide.save-error");
    }
  }
  catch {
    error.value = i18n.t("guide.save-error");
  }
  finally {
    loading.value = false;
  }
}

watch(hasUnsavedChanges, dirty => dirty ? activateNavigationWarning() : deactivateNavigationWarning());
onBeforeRouteLeave(() => guideNavigationCanProceed({
  dirty: hasUnsavedChanges.value,
  saving: loading.value,
  internal: allowNavigation.value,
  confirmDiscard: () => window.confirm(i18n.t("general.discard-changes-description")),
}));
onBeforeUnmount(deactivateNavigationWarning);
</script>

<style scoped>
.guide-container {
  max-width: 1040px;
  padding-top: 32px;
  padding-bottom: 112px;
}

.guide-editor-header {
  max-width: 920px;
  margin: 24px auto 32px;
}

.guide-editor-header p {
  margin: 0 0 8px;
  color: rgb(var(--v-theme-primary));
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.guide-editor-header h1 {
  font-size: clamp(2.25rem, 5vw, 3.5rem);
  letter-spacing: -0.045em;
  line-height: 1.05;
}

.guide-editor-header span {
  display: block;
  max-width: 60ch;
  margin-top: 12px;
  color: rgb(var(--v-theme-on-surface-variant));
}

@media (max-width: 599px) {
  .guide-container {
    padding-inline: 12px;
  }
}
</style>
