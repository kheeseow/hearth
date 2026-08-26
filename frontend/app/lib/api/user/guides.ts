import { BaseCRUDAPI } from "../base/base-clients";
import type { GuideCreate, GuideRead, GuideUpdate } from "~/lib/api/types/guide";

const routes = {
  guides: "/api/guides",
  guide: (slugOrId: string | number) => `/api/guides/${slugOrId}`,
};

export class GuideAPI extends BaseCRUDAPI<GuideCreate, GuideRead, GuideUpdate> {
  baseRoute = routes.guides;
  itemRoute = routes.guide;
}
