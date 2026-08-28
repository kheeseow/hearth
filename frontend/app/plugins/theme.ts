export interface ThemeConfig {
  lightPrimary: string;
  lightAccent: string;
  lightSecondary: string;
  lightSuccess: string;
  lightInfo: string;
  lightWarning: string;
  lightError: string;
  darkPrimary: string;
  darkAccent: string;
  darkSecondary: string;
  darkSuccess: string;
  darkInfo: string;
  darkWarning: string;
  darkError: string;
}

let __cachedTheme: ThemeConfig | undefined;

async function fetchTheme(): Promise<ThemeConfig | undefined> {
  // Use a distinct cache key so upgraded browsers do not retain Mealie's theme response for a week.
  const route = "/api/app/about/theme?profile=hearth-v1";

  try {
    const response = await fetch(route);
    const data = await response.json();
    return data as ThemeConfig;
  }
  catch {
    return undefined;
  }
}

export default defineNuxtPlugin(async (nuxtApp) => {
  nuxtApp.hook("vuetify:before-create", async ({ vuetifyOptions }) => {
    let theme = __cachedTheme;
    if (!theme) {
      theme = await fetchTheme();
      __cachedTheme = theme;
    }
    vuetifyOptions.theme = {
      defaultTheme: nuxtApp.$config.public.useDark ? "dark" : "light",
      variations: {
        colors: ["primary", "accent", "secondary", "success", "info", "warning", "error", "background"],
        lighten: 3,
        darken: 3,
      },
      themes: {
        light: {
          dark: false,
          colors: {
            "primary": theme?.lightPrimary ?? "#9A4F2E",
            "accent": theme?.lightAccent ?? "#496B5A",
            "secondary": theme?.lightSecondary ?? "#C58B2B",
            "success": theme?.lightSuccess ?? "#43A047",
            "info": theme?.lightInfo ?? "#1976d2",
            "warning": theme?.lightWarning ?? "#FF6D00",
            "error": theme?.lightError ?? "#EF5350",
            "background": "#F6F2EA",
            "surface": "#FFFDF8",
            "surface-variant": "#EEE8DC",
            "on-surface": "#26211C",
            "on-surface-variant": "#6E655B",
            "outline": "#DDD5C8",
          },
        },
        dark: {
          dark: true,
          colors: {
            "primary": theme?.darkPrimary ?? "#D47A50",
            "accent": theme?.darkAccent ?? "#7FA58F",
            "secondary": theme?.darkSecondary ?? "#D9A441",
            "success": theme?.darkSuccess ?? "#43A047",
            "info": theme?.darkInfo ?? "#1976d2",
            "warning": theme?.darkWarning ?? "#FF6D00",
            "error": theme?.darkError ?? "#EF5350",
            "background": "#181714",
            "surface": "#211F1B",
            "surface-variant": "#312D26",
            "on-surface": "#F6F1E7",
            "on-surface-variant": "#B9AFA2",
            "outline": "#443E35",
          },
        },
      },
    };
  });
});
