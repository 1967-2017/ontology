"use client";

import { AgentAction } from "@/types/ontology";
import { CreateOntologyObjectCard } from "./CreateOntologyObjectCard";
import { ObjectTableCard } from "./ObjectTableCard";
import { ResultNoticeCard } from "./ResultNoticeCard";

type Props = {
  action: AgentAction;
  onNotice: (notice: { title: string; message: string; status: "success" | "error" }) => void;
};

export function ActionRenderer({ action, onNotice }: Props) {
  switch (action.name) {
    case "show_create_object_form":
      return (
        <CreateOntologyObjectCard
          className={action.payload.class_name}
          presetValues={action.payload.preset_values}
          onNotice={onNotice}
        />
      );
    case "show_object_table":
      return <ObjectTableCard className={action.payload.class_name} rows={action.payload.rows} />;
    case "show_result_notice":
      return (
        <ResultNoticeCard
          title={action.payload.title}
          message={action.payload.message}
          status={action.payload.status}
        />
      );
    default:
      return null;
  }
}
