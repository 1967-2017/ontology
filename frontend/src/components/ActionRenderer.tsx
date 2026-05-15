"use client";

import { AgentAction } from "@/types/ontology";
import { CreateOntologyObjectCard } from "./CreateOntologyObjectCard";
import { ObjectTableCard } from "./ObjectTableCard";
import { OcrResultCard } from "./OcrResultCard";
import { PptResultCard } from "./PptResultCard";
import { RagAnswerCard } from "./RagAnswerCard";
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
    case "show_ocr_result":
      return (
        <OcrResultCard
          documentId={action.payload.document_id}
          filename={action.payload.filename}
          fullText={action.payload.full_text}
          pages={action.payload.pages}
        />
      );
    case "show_rag_answer":
      return (
        <RagAnswerCard
          answer={action.payload.answer}
          citations={action.payload.citations}
          matchedDocuments={action.payload.matched_documents}
        />
      );
    case "show_ppt_result":
      return (
        <PptResultCard
          presentationId={action.payload.presentation_id}
          title={action.payload.title}
          topic={action.payload.topic}
          status={action.payload.status}
          slideCount={action.payload.slide_count}
          downloadUrl={action.payload.download_url}
          sourceDocumentIds={action.payload.source_document_ids}
        />
      );
    default:
      return null;
  }
}
