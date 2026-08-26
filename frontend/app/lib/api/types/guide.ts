/* tslint:disable */

/**
/* This file was automatically generated from pydantic models by running pydantic2ts.
/* Do not modify it by hand - just update the pydantic models and then re-run the script
*/

export interface GuideCreate {
  title: string;
  description?: string;
  steps?: GuideStepIn[];
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
  createdAt: string;
  updatedAt: string;
}
export interface GuidePatch {
  title?: string | null;
  description?: string | null;
  steps?: GuideStepIn[] | null;
}
export interface GuideRead {
  id: string;
  groupId: string;
  householdId: string;
  authorId: string;
  slug: string;
  title: string;
  description: string;
  createdAt: string;
  updatedAt: string;
  steps?: GuideStepOut[];
}
export interface GuideStepOut {
  id: string;
  position: number;
  text: string;
}
export interface GuideSave {
  title: string;
  description?: string;
  steps?: GuideStepIn[];
  groupId: string;
  householdId: string;
  authorId: string;
  slug: string;
}
export interface GuideUpdate {
  title: string;
  description?: string;
  steps?: GuideStepIn[];
}
