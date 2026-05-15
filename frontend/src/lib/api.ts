import { AgentResponse, FormSchema, OCRResult, PptResult, ProjectDocument, RagAnswer } from "@/types/ontology";

const API_BASE_URL = "/api/backend";

async function unwrap<T>(input: Promise<Response>): Promise<T> {
  const response = await input;
  const json = (await response.json()) as { success: boolean; data: T; error?: { message: string } | null };
  if (!response.ok || !json.success) {
    throw new Error(json.error?.message ?? "Request failed");
  }
  return json.data;
}

export async function fetchOntologyClasses(): Promise<{ class_name: string; label: string }[]> {
  return unwrap(fetch(`${API_BASE_URL}/ontology/classes`, { cache: "no-store" }));
}

export async function fetchFormSchema(className: string): Promise<FormSchema> {
  return unwrap(fetch(`${API_BASE_URL}/ontology/classes/${className}/form-schema`, { cache: "no-store" }));
}

export async function searchRelationOptions(className: string, keyword: string) {
  return unwrap<{ items: Record<string, unknown>[] }>(
    fetch(
      `${API_BASE_URL}/objects/${className}?keyword=${encodeURIComponent(keyword)}&page=1&page_size=20`,
      { cache: "no-store" },
    ),
  );
}

export async function listObjects(className: string) {
  return unwrap<{ items: Record<string, unknown>[]; page: number; page_size: number; total: number }>(
    fetch(`${API_BASE_URL}/objects/${className}`, { cache: "no-store" }),
  );
}

export async function createObject(className: string, values: Record<string, unknown>) {
  return unwrap<{
    object: { class_name: string; id: number; values: Record<string, unknown> };
    graph_sync: { status: string; message?: string | null };
  }>(
    fetch(`${API_BASE_URL}/objects/${className}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ values }),
    }),
  );
}

export async function sendAgentMessage(message: string): Promise<AgentResponse> {
  return unwrap<AgentResponse>(
    fetch(`${API_BASE_URL}/agent/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    }),
  );
}

export async function importMysqlToNeo4j(rebuild: boolean) {
  return unwrap<{
    tables_processed: number;
    nodes_created_or_updated: number;
    relationships_created: number;
    skipped_tables: string[];
    errors: string[];
    table_summaries: Record<string, Record<string, unknown>>;
  }>(
    fetch(`${API_BASE_URL}/admin/import/mysql-to-neo4j`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rebuild }),
    }),
  );
}

export async function listProjectDocuments(): Promise<{ items: ProjectDocument[] }> {
  return unwrap(fetch(`${API_BASE_URL}/documents`, { cache: "no-store" }));
}

export async function uploadProjectDocument(file: File): Promise<ProjectDocument> {
  const formData = new FormData();
  formData.append("file", file);
  return unwrap(
    fetch(`${API_BASE_URL}/documents/upload`, {
      method: "POST",
      body: formData,
    }),
  );
}

export async function runDocumentOcr(documentId: number): Promise<OCRResult> {
  return unwrap(
    fetch(`${API_BASE_URL}/documents/${documentId}/ocr`, {
      method: "POST",
    }),
  );
}

export async function getDocumentOcrResult(documentId: number): Promise<OCRResult> {
  return unwrap(fetch(`${API_BASE_URL}/documents/${documentId}/ocr`, { cache: "no-store" }));
}

export async function indexDocumentToKnowledgeBase(documentId: number) {
  return unwrap(
    fetch(`${API_BASE_URL}/documents/${documentId}/index`, {
      method: "POST",
    }),
  );
}

export async function deleteProjectDocument(documentId: number) {
  return unwrap(
    fetch(`${API_BASE_URL}/documents/${documentId}`, {
      method: "DELETE",
    }),
  );
}

export async function answerWithKnowledgeBase(question: string): Promise<RagAnswer> {
  return unwrap(
    fetch(`${API_BASE_URL}/knowledge/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    }),
  );
}

export async function generateEditablePptx(payload: {
  topic?: string;
  slide_count?: number;
  document_ids?: number[];
  use_knowledge_base?: boolean;
}): Promise<PptResult> {
  return unwrap(
    fetch(`${API_BASE_URL}/ppt/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
  );
}
