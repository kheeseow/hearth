/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type OrderByNullPosition = "first" | "last";
export type OrderDirection = "asc" | "desc";
export type GuideType = "cleaning" | "maintenance" | "setup" | "emergency" | "troubleshooting" | "care_instructions";
export type GuideDifficulty = "beginner" | "intermediate" | "advanced";
export type GuideFrequency = "one_time" | "weekly" | "monthly" | "yearly" | "as_needed";

export interface ErrorResponse {
  message: string;
  error?: boolean;
  exception?: string | null;
}
export interface FileTokenResponse {
  fileToken: string;
}
export interface PaginationQuery {
  orderBy?: string | null;
  orderByNullPosition?: OrderByNullPosition | null;
  orderDirection?: OrderDirection;
  queryFilter?: string | null;
  paginationSeed?: string | null;
  page?: number;
  perPage?: number;
}
export interface RecipeSearchQuery {
  cookbook?: string | null;
  requireAllCategories?: boolean;
  requireAllTags?: boolean;
  requireAllTools?: boolean;
  requireAllFoods?: boolean;
  search?: string | null;
}
export interface RequestQuery {
  orderBy?: string | null;
  orderByNullPosition?: OrderByNullPosition | null;
  orderDirection?: OrderDirection;
  queryFilter?: string | null;
  paginationSeed?: string | null;
}
export interface SSEDataEventBase {}
export interface SSEDataEventDone {
  slug: string;
}
export interface SSEDataEventMessage {
  message: string;
}
export interface SuccessResponse {
  message: string;
  error?: boolean;
}
export interface ValidationResponse {
  valid: boolean;
}
export interface PaginationBaseGuideSummary {
  page?: number;
  per_page?: number;
  total?: number;
  total_pages?: number;
  items: GuideSummary[];
  next?: string | null;
  previous?: string | null;
}
export interface GuideSummary {
  id: string;
  groupId: string;
  householdId: string;
  authorId: string;
  slug: string;
  title: string;
  description: string;
  guideType?: GuideType | null;
  difficulty?: GuideDifficulty | null;
  frequency?: GuideFrequency | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  coverImageVersion?: string | null;
  category?: GuideCategoryOut | null;
  tags?: GuideTagOut[];
  createdAt: string;
  updatedAt: string;
}
export interface GuideCategoryOut {
  id: string;
  name: string;
}
export interface GuideTagOut {
  id: string;
  name: string;
}
