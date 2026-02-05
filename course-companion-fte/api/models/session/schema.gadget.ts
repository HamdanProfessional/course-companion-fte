import type { GadgetModel } from "gadget-server";

// This file describes the schema for the "session" model, go to https://course-companion-fte.gadget.app/edit to view/edit your model in Gadget
// For more information on how to update this file http://docs.gadget.dev

export const schema: GadgetModel = {
  type: "gadget/model-schema/v2",
  storageKey: "l9SB_pLuVKWY",
  fields: {
    roles: {
      type: "roleList",
      default: ["unauthenticated"],
      storageKey: "PnXy362QYPMb",
    },
  },
};
