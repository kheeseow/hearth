/* tslint:disable */

/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type GuideCalloutKind = "warning" | "avoid";
export type GuideType = "cleaning" | "maintenance" | "setup" | "emergency" | "troubleshooting" | "care_instructions";
export type GuideDifficulty = "beginner" | "intermediate" | "advanced";

export interface GuideCalloutIn {
  id?: string | null;
  kind: GuideCalloutKind;
  text: string;
}
export interface GuideCalloutOut {
  id: string;
  position: number;
  kind: GuideCalloutKind;
  text: string;
}
export interface GuideCategoryOut {
  id: string;
  name: string;
}
export interface GuideCreate {
  title: string;
  description?: string;
  guideType?: GuideType | null;
  difficulty?: GuideDifficulty | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  category?: string | null;
  tags?: string[];
  steps?: GuideStepIn[];
  callouts?: GuideCalloutIn[];
}
export interface GuideStepIn {
  id?: string | null;
  text: string;
}
export interface GuidePagination {
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
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  category?: GuideCategoryOut | null;
  tags?: GuideTagOut[];
  createdAt: string;
  updatedAt: string;
}
export interface GuideTagOut {
  id: string;
  name: string;
}
export interface GuidePatch {
  title?: string | null;
  description?: string | null;
  guideType?: GuideType | null;
  difficulty?: GuideDifficulty | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  category?: string | null;
  tags?: string[] | null;
  steps?: GuideStepIn[] | null;
  callouts?: GuideCalloutIn[] | null;
}
export interface GuideRead {
  id: string;
  groupId: string;
  householdId: string;
  authorId: string;
  slug: string;
  title: string;
  description: string;
  guideType?: GuideType | null;
  difficulty?: GuideDifficulty | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  category?: GuideCategoryOut | null;
  tags?: GuideTagOut[];
  createdAt: string;
  updatedAt: string;
  steps?: GuideStepOut[];
  callouts?: GuideCalloutOut[];
}
export interface GuideStepOut {
  id: string;
  position: number;
  text: string;
}
export interface GuideSave {
  title: string;
  description?: string;
  guideType?: GuideType | null;
  difficulty?: GuideDifficulty | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  category?: string | null;
  tags?: string[];
  steps?: GuideStepIn[];
  callouts?: GuideCalloutIn[];
  groupId: string;
  householdId: string;
  authorId: string;
  slug: string;
}
export interface GuideUpdate {
  title: string;
  description?: string;
  guideType?: GuideType | null;
  difficulty?: GuideDifficulty | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  category?: string | null;
  tags?: string[];
  steps?: GuideStepIn[];
  callouts?: GuideCalloutIn[];
}
