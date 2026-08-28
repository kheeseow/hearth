export type GuideEditorSaveState = "saved" | "unsaved" | "saving" | "failed";

export function guideDraftIsDirty({
  initial,
  current,
}: {
  initial: string;
  current: string;
}): boolean {
  return current !== initial;
}

export function guideSaveCanStart(loading: boolean): boolean {
  return !loading;
}

export function guideDiscardCanProceed(dirty: boolean, confirmDiscard: () => boolean): boolean {
  return !dirty || confirmDiscard();
}

export function guideNavigationCanProceed({
  dirty,
  saving,
  internal,
  confirmDiscard,
}: {
  dirty: boolean;
  saving: boolean;
  internal: boolean;
  confirmDiscard: () => boolean;
}): boolean {
  if (internal) return true;
  if (saving) return false;
  return guideDiscardCanProceed(dirty, confirmDiscard);
}

export function guideEditorSaveState({
  loading,
  error,
  dirty,
}: {
  loading: boolean;
  error?: string;
  dirty: boolean;
}): GuideEditorSaveState {
  if (loading) return "saving";
  if (error) return "failed";
  return dirty ? "unsaved" : "saved";
}
