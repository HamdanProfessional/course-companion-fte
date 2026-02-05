import type { GadgetModel } from "gadget-server";

// This file describes the schema for the "Chapter" model, go to https://course-companion-fte.gadget.app/edit to view/edit your model in Gadget
// For more information on how to update this file http://docs.gadget.dev

export const schema: GadgetModel = {
  type: "gadget/model-schema/v2",
  storageKey: "HCc9f_NiGs5y",
  fields: {
    content: { type: "string", storageKey: "-14hLQqtuFss" },
    difficultyLevel: { type: "string", storageKey: "EfyotTD2eWzC" },
    estimatedTime: { type: "number", storageKey: "tbqo4nnzdyC_" },
    order: { type: "number", storageKey: "OBOAByys3_uq" },
    title: { type: "string", storageKey: "B5SRJIIpfEw2" },
  },
};
