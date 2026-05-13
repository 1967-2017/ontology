"use client";

import { useCopilotAction } from "@copilotkit/react-core";

import { CreateOntologyObjectCard } from "./CreateOntologyObjectCard";
import { ObjectTableCard } from "./ObjectTableCard";
import { ResultNoticeCard } from "./ResultNoticeCard";

export function CopilotActionBridge() {
  useCopilotAction({
    name: "show_create_object_form",
    description: "Render a dynamic ontology object creation form.",
    parameters: [
      {
        name: "class_name",
        type: "string",
        description: "Ontology class name such as Project, Team, Developer, or Task.",
        required: true,
      },
      {
        name: "preset_values",
        type: "object",
        description: "Optional preset field values used to prefill the form.",
        required: false,
      },
    ],
    handler: () => null,
    render: ({ args }) => (
      <CreateOntologyObjectCard
        className={String(args.class_name)}
        presetValues={(args.preset_values as Record<string, unknown> | undefined) ?? {}}
      />
    ),
  });

  useCopilotAction({
    name: "show_object_table",
    description: "Render a result table for ontology objects.",
    parameters: [
      {
        name: "class_name",
        type: "string",
        description: "Ontology class name used as the table title.",
        required: true,
      },
      {
        name: "rows",
        type: "object[]",
        description: "Rows to render in the result table.",
        required: true,
      },
    ],
    handler: () => null,
    render: ({ args }) => (
      <ObjectTableCard
        className={String(args.class_name)}
        rows={(args.rows as Record<string, unknown>[] | undefined) ?? []}
      />
    ),
  });

  useCopilotAction({
    name: "show_result_notice",
    description: "Render a status notice after a create or sync action.",
    parameters: [
      {
        name: "title",
        type: "string",
        description: "Notice title.",
        required: true,
      },
      {
        name: "message",
        type: "string",
        description: "Notice message body.",
        required: true,
      },
      {
        name: "status",
        type: "string",
        description: "Notice status, either success or error.",
        required: true,
      },
    ],
    handler: () => null,
    render: ({ args }) => (
      <ResultNoticeCard
        title={String(args.title)}
        message={String(args.message)}
        status={String(args.status) === "error" ? "error" : "success"}
      />
    ),
  });

  return null;
}
