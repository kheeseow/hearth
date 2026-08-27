import { BaseCRUDAPI } from "../base/base-clients";
import type {
  GuideCreate,
  GuideRead,
  GuideStepImageUpdate,
  GuideUpdate,
} from "~/lib/api/types/guide";

const routes = {
  guides: "/api/guides",
  guide: (slugOrId: string | number) => `/api/guides/${slugOrId}`,
  coverImage: (slugOrId: string | number) => `/api/guides/${slugOrId}/image`,
  coverImageFile: (slugOrId: string | number, size: string) => `/api/guides/${slugOrId}/image/${size}`,
  stepImages: (slugOrId: string | number, stepId: string) => `/api/guides/${slugOrId}/steps/${stepId}/images`,
  stepImage: (slugOrId: string | number, stepId: string, imageId: string) => `/api/guides/${slugOrId}/steps/${stepId}/images/${imageId}`,
  stepImageFile: (slugOrId: string | number, stepId: string, imageId: string) => `/api/guides/${slugOrId}/steps/${stepId}/images/${imageId}/file`,
  stepImageMedia: (slugOrId: string | number, stepId: string, imageId: string, size: string) => `/api/guides/${slugOrId}/steps/${stepId}/images/${imageId}/${size}`,
  stepImageOrder: (slugOrId: string | number, stepId: string) => `/api/guides/${slugOrId}/steps/${stepId}/images/order`,
};

export class GuideAPI extends BaseCRUDAPI<GuideCreate, GuideRead, GuideUpdate> {
  baseRoute = routes.guides;
  itemRoute = routes.guide;

  updateCoverImage(slugOrId: string | number, file: File) {
    const formData = this.imageForm(file);
    return this.requests.put<GuideRead, FormData>(routes.coverImage(slugOrId), formData);
  }

  deleteCoverImage(slugOrId: string | number) {
    return this.requests.delete<GuideRead>(routes.coverImage(slugOrId));
  }

  getCoverImage(slugOrId: string | number, size = "original") {
    return this.requests.get<Blob>(routes.coverImageFile(slugOrId, size), undefined, { responseType: "blob" });
  }

  addStepImage(slugOrId: string | number, stepId: string, file: File, caption = "", altText = "") {
    const formData = this.imageForm(file);
    formData.append("caption", caption);
    formData.append("alt_text", altText);
    return this.requests.post<GuideRead>(routes.stepImages(slugOrId, stepId), formData);
  }

  updateStepImage(slugOrId: string | number, stepId: string, imageId: string, data: GuideStepImageUpdate) {
    return this.requests.patch<GuideRead, GuideStepImageUpdate>(routes.stepImage(slugOrId, stepId, imageId), data);
  }

  replaceStepImage(slugOrId: string | number, stepId: string, imageId: string, file: File) {
    return this.requests.put<GuideRead, FormData>(
      routes.stepImageFile(slugOrId, stepId, imageId),
      this.imageForm(file),
    );
  }

  reorderStepImages(slugOrId: string | number, stepId: string, imageIds: string[]) {
    return this.requests.put<GuideRead>(routes.stepImageOrder(slugOrId, stepId), { imageIds });
  }

  deleteStepImage(slugOrId: string | number, stepId: string, imageId: string) {
    return this.requests.delete<GuideRead>(routes.stepImage(slugOrId, stepId, imageId));
  }

  getStepImage(slugOrId: string | number, stepId: string, imageId: string, size = "original") {
    return this.requests.get<Blob>(routes.stepImageMedia(slugOrId, stepId, imageId, size), undefined, {
      responseType: "blob",
    });
  }

  private imageForm(file: File) {
    const formData = new FormData();
    formData.append("image", file);
    formData.append("extension", file.name.split(".").pop() ?? "");
    return formData;
  }
}
