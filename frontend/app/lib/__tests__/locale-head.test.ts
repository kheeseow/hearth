import { describe, expect, it } from "vitest";
import { getLocaleDirection } from "~/lib/locale-head";

describe("locale document direction", () => {
  it("uses the configured direction for supported locales", () => {
    expect(getLocaleDirection("en-US")).toBe("ltr");
    expect(getLocaleDirection("ar-SA")).toBe("rtl");
    expect(getLocaleDirection("he-IL")).toBe("rtl");
  });

  it("defaults unknown locales to left-to-right", () => {
    expect(getLocaleDirection("unknown")).toBe("ltr");
  });
});
