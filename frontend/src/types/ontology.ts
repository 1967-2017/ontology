export type FieldType =
  | "string"
  | "text"
  | "date"
  | "number"
  | "enum"
  | "relation"
  | "json_string_array";

export type FieldDefinition = {
  name: string;
  label: string;
  data_type: FieldType;
  required: boolean;
  readonly?: boolean;
  enum_options?: string[];
  relation_target?: string;
  relation_multiple?: boolean;
  placeholder?: string;
};

export type FormSchema = {
  class_name: string;
  title: string;
  fields: FieldDefinition[];
};

export type AgentAction =
  | { name: "show_create_object_form"; payload: { class_name: string; preset_values?: Record<string, unknown> } }
  | { name: "show_object_table"; payload: { class_name: string; rows: Record<string, unknown>[] } }
  | { name: "show_result_notice"; payload: { title: string; message: string; status: "success" | "error" } }
  | {
      name: "show_ocr_result";
      payload: { document_id: number; filename: string; full_text: string; pages: Record<string, unknown>[] };
    }
  | {
      name: "show_rag_answer";
      payload: {
        answer: string;
        citations: { document_id: number; filename: string; page_number?: number | null; snippet: string; score: number }[];
        matched_documents: string[];
      };
    }
  | {
      name: "show_ppt_result";
      payload: {
        presentation_id: number;
        title: string;
        topic: string;
        status: string;
        slide_count: number;
        download_url?: string | null;
        source_document_ids?: number[];
      };
    };

export type AgentResponse = {
  reply: string;
  actions: AgentAction[];
};

export type ProjectDocument = {
  document_id: number;
  filename: string;
  mime_type: string;
  file_type: string;
  ocr_status: string;
  knowledge_status: string;
  created_at: string;
};

export type OCRResult = {
  document_id: number;
  filename?: string;
  status?: string;
  message?: string;
  full_text: string;
  pages: { page_number: number; text: string; source?: string; blocks: Record<string, unknown>[] }[];
  blocks: Record<string, unknown>[];
};

export type RagAnswer = {
  answer: string;
  citations: { document_id: number; filename: string; page_number?: number | null; snippet: string; score: number }[];
  matched_documents: string[];
};

export type PptResult = {
  presentation_id: number;
  title: string;
  topic: string;
  status: string;
  slide_count: number;
  download_url?: string | null;
  outline?: Record<string, unknown>[] | null;
  source_document_ids?: number[] | null;
};
