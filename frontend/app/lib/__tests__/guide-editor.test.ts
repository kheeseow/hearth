import { describe, expect, it } from "vitest";
import {
  guideDiscardCanProceed,
  guideDraftIsDirty,
  guideEditorSaveState,
  guideNavigationCanProceed,
  guideSaveCanStart,
} from "~/lib/guide-editor";

describe("Guide editor save state", () => {
  it("prioritizes active and failed saves over draft state", () => {
    expect(guideEditorSaveState({ loading: true, error: "Network error", dirty: true })).toBe("saving");
    expect(guideEditorSaveState({ loading: false, error: "Network error", dirty: true })).toBe("failed");
  });

  it("distinguishes an untouched guide from unsaved changes", () => {
    expect(guideEditorSaveState({ loading: false, error: "", dirty: false })).toBe("saved");
    expect(guideEditorSaveState({ loading: false, error: "", dirty: true })).toBe("unsaved");
  });

  it("warns only after a draft actually changes", () => {
    expect(guideDraftIsDirty({ initial: "same", current: "same" })).toBe(false);
    expect(guideDraftIsDirty({ initial: "before", current: "after" })).toBe(true);
  });

  it("allows only one save request at a time", () => {
    expect(guideSaveCanStart(false)).toBe(true);
    expect(guideSaveCanStart(true)).toBe(false);
  });

  it("confirms only when discarding unsaved work", () => {
    let confirmations = 0;
    const confirmDiscard = () => {
      confirmations += 1;
      return false;
    };

    expect(guideDiscardCanProceed(false, confirmDiscard)).toBe(true);
    expect(confirmations).toBe(0);
    expect(guideDiscardCanProceed(true, confirmDiscard)).toBe(false);
    expect(confirmations).toBe(1);
  });

  it("blocks external navigation during a save but permits a completed save redirect", () => {
    const confirmDiscard = () => true;

    expect(guideNavigationCanProceed({
      dirty: true,
      saving: true,
      internal: false,
      confirmDiscard,
    })).toBe(false);
    expect(guideNavigationCanProceed({
      dirty: false,
      saving: true,
      internal: true,
      confirmDiscard,
    })).toBe(true);
  });
});
