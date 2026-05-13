import { AgentResponse, FormSchema } from "@/types/ontology";

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
