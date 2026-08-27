/* tslint:disable */
/* eslint-disable */
/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export type GuideCalloutKind = "warning" | "avoid";
export type GuideType = "cleaning" | "maintenance" | "setup" | "emergency" | "troubleshooting" | "care_instructions";
export type GuideDifficulty = "beginner" | "intermediate" | "advanced";
export type GuideFrequency = "one_time" | "weekly" | "monthly" | "yearly" | "as_needed";
export type GuideRequirementKind = "tool" | "material";

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
  frequency?: GuideFrequency | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  notes?: string | null;
  lastReviewed?: string | null;
  category?: string | null;
  tags?: string[];
  steps?: GuideStepIn[];
  callouts?: GuideCalloutIn[];
  requirements?: GuideRequirementIn[];
  sources?: GuideSourceIn[];
  relatedGuideIds?: string[];
}
export interface GuideStepIn {
  id?: string | null;
  text: string;
  tip?: string | null;
}
export interface GuideRequirementIn {
  id?: string | null;
  kind: GuideRequirementKind;
  name: string;
  note?: string | null;
}
export interface GuideSourceIn {
  id?: string | null;
  label: string;
  url: string;
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
  frequency?: GuideFrequency | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  lastReviewed?: string | null;
  coverImageVersion?: string | null;
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
  frequency?: GuideFrequency | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  notes?: string | null;
  lastReviewed?: string | null;
  category?: string | null;
  tags?: string[] | null;
  steps?: GuideStepIn[] | null;
  callouts?: GuideCalloutIn[] | null;
  requirements?: GuideRequirementIn[] | null;
  sources?: GuideSourceIn[] | null;
  relatedGuideIds?: string[] | null;
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
  frequency?: GuideFrequency | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  lastReviewed?: string | null;
  coverImageVersion?: string | null;
  category?: GuideCategoryOut | null;
  tags?: GuideTagOut[];
  createdAt: string;
  updatedAt: string;
  notes?: string | null;
  steps?: GuideStepOut[];
  callouts?: GuideCalloutOut[];
  requirements?: GuideRequirementOut[];
  sources?: GuideSourceOut[];
  relatedGuides?: GuideRelatedOut[];
}
export interface GuideStepOut {
  id: string;
  position: number;
  text: string;
  tip?: string | null;
  images?: GuideStepImageOut[];
}
export interface GuideStepImageOut {
  id: string;
  position: number;
  version: string;
  caption?: string | null;
  altText?: string | null;
}
export interface GuideRequirementOut {
  id: string;
  position: number;
  kind: GuideRequirementKind;
  name: string;
  note?: string | null;
}
export interface GuideSourceOut {
  id: string;
  position: number;
  label: string;
  url: string;
}
export interface GuideRelatedOut {
  id: string;
  slug: string;
  title: string;
  guideType?: GuideType | null;
  difficulty?: GuideDifficulty | null;
  coverImageVersion?: string | null;
}
export interface GuideSave {
  title: string;
  description?: string;
  guideType?: GuideType | null;
  difficulty?: GuideDifficulty | null;
  frequency?: GuideFrequency | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  notes?: string | null;
  lastReviewed?: string | null;
  category?: string | null;
  tags?: string[];
  steps?: GuideStepIn[];
  callouts?: GuideCalloutIn[];
  requirements?: GuideRequirementIn[];
  sources?: GuideSourceIn[];
  relatedGuideIds?: string[];
  groupId: string;
  householdId: string;
  authorId: string;
  slug: string;
}
export interface GuideStepImageOrder {
  imageIds:
    | []
    | [string]
    | [string, string]
    | [string, string, string]
    | [string, string, string, string]
    | [string, string, string, string, string]
    | [string, string, string, string, string, string]
    | [string, string, string, string, string, string, string]
    | [string, string, string, string, string, string, string, string]
    | [string, string, string, string, string, string, string, string, string]
    | [string, string, string, string, string, string, string, string, string, string]
    | [string, string, string, string, string, string, string, string, string, string, string]
    | [string, string, string, string, string, string, string, string, string, string, string, string]
    | [string, string, string, string, string, string, string, string, string, string, string, string, string]
    | [string, string, string, string, string, string, string, string, string, string, string, string, string, string]
    | [
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string
      ]
    | [
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string
      ]
    | [
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string
      ]
    | [
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string
      ]
    | [
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string
      ]
    | [
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string,
        string
      ];
}
export interface GuideStepImageUpdate {
  caption?: string | null;
  altText?: string | null;
}
export interface GuideUpdate {
  title: string;
  description?: string;
  guideType?: GuideType | null;
  difficulty?: GuideDifficulty | null;
  frequency?: GuideFrequency | null;
  preparationMinutes?: number | null;
  executionMinutes?: number | null;
  notes?: string | null;
  lastReviewed?: string | null;
  category?: string | null;
  tags?: string[];
  steps?: GuideStepIn[];
  callouts?: GuideCalloutIn[];
  requirements?: GuideRequirementIn[];
  sources?: GuideSourceIn[];
  relatedGuideIds?: string[];
}
