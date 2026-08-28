import type { GuideDifficulty, GuideFrequency, GuideType } from "~/lib/api/types/guide";

export interface GuideLibraryFilters {
  search: string;
  guideType: GuideType | null;
  difficulty: GuideDifficulty | null;
  frequency: GuideFrequency | null;
  category: string;
  tag: string;
}

const GUIDE_TYPES = new Set<GuideType>([
  "cleaning",
  "maintenance",
  "setup",
  "emergency",
  "troubleshooting",
  "care_instructions",
]);
const GUIDE_DIFFICULTIES = new Set<GuideDifficulty>(["beginner", "intermediate", "advanced"]);
const GUIDE_FREQUENCIES = new Set<GuideFrequency>(["one_time", "weekly", "monthly", "yearly", "as_needed"]);
const GUIDE_QUERY_KEYS = new Set(["search", "type", "difficulty", "frequency", "category", "tag"]);

export function emptyGuideLibraryFilters(): GuideLibraryFilters {
  return {
    search: "",
    guideType: null,
    difficulty: null,
    frequency: null,
    category: "",
    tag: "",
  };
}

function firstString(value: unknown): string {
  const candidate = Array.isArray(value) ? value[0] : value;
  return typeof candidate === "string" ? candidate.trim() : "";
}

function selectedValue<T extends string>(value: unknown, choices: Set<T>): T | null {
  const candidate = firstString(value) as T;
  return choices.has(candidate) ? candidate : null;
}

export function guideLibraryFiltersFromQuery(query: Record<string, unknown>): GuideLibraryFilters {
  return {
    search: firstString(query.search),
    guideType: selectedValue(query.type, GUIDE_TYPES),
    difficulty: selectedValue(query.difficulty, GUIDE_DIFFICULTIES),
    frequency: selectedValue(query.frequency, GUIDE_FREQUENCIES),
    category: firstString(query.category),
    tag: firstString(query.tag),
  };
}

export function guideLibraryQuery(filters: GuideLibraryFilters): Record<string, string> {
  const query: Record<string, string> = {};
  const values = {
    search: filters.search.trim(),
    type: filters.guideType,
    difficulty: filters.difficulty,
    frequency: filters.frequency,
    category: filters.category.trim(),
    tag: filters.tag.trim(),
  };

  for (const [key, value] of Object.entries(values)) {
    if (value) {
      query[key] = value;
    }
  }
  return query;
}

export function guideLibraryCanonicalQuery(query: Record<string, unknown>): Record<string, string> {
  const canonical = guideLibraryQuery(guideLibraryFiltersFromQuery(query));

  for (const [key, value] of Object.entries(query)) {
    if (!GUIDE_QUERY_KEYS.has(key)) {
      const preserved = firstString(value);
      if (preserved) canonical[key] = preserved;
    }
  }
  return canonical;
}

export function guideLibraryQueryWithExistingState(
  filters: GuideLibraryFilters,
  query: Record<string, unknown>,
): Record<string, string> {
  const canonical = guideLibraryCanonicalQuery(query);
  const {
    search: _search,
    type: _type,
    difficulty: _difficulty,
    frequency: _frequency,
    category: _category,
    tag: _tag,
    ...unrelated
  } = canonical;
  return { ...unrelated, ...guideLibraryQuery(filters) };
}

export function guideLibraryAdvancedFilterCount(filters: GuideLibraryFilters): number {
  return [filters.guideType, filters.difficulty, filters.frequency, filters.category.trim(), filters.tag.trim()]
    .filter(Boolean)
    .length;
}

export function guideLibraryHasCriteria(filters: GuideLibraryFilters): boolean {
  return Boolean(filters.search.trim() || guideLibraryAdvancedFilterCount(filters));
}

export function createLatestGuideRequest() {
  let latestRequestId = 0;

  return async <T>(request: () => Promise<T>): Promise<T | undefined> => {
    const requestId = ++latestRequestId;
    try {
      const result = await request();
      return requestId === latestRequestId ? result : undefined;
    }
    catch (requestError) {
      if (requestId === latestRequestId) throw requestError;
      return undefined;
    }
  };
}
