import { randomUUID } from "node:crypto";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp";
import { WebStandardStreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/webStandardStreamableHttp";
import { z } from "zod";

const backendBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

type TransportRecord = {
  server: McpServer;
  transport: WebStandardStreamableHTTPServerTransport;
};

const transports = new Map<string, TransportRecord>();

async function backendRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${backendBaseUrl}${path}`, {
    cache: "no-store",
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  const json = (await response.json()) as { success: boolean; data: T; error?: { message?: string } | null };
  if (!response.ok || !json.success) {
    throw new Error(json.error?.message ?? "Backend request failed");
  }
  return json.data;
}

function jsonToolResult(payload: unknown) {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(payload, null, 2),
      },
    ],
  };
}

function createLocalMcpServer() {
  const server = new McpServer({
    name: "ontology-local-doc-tools",
    version: "1.0.0",
  });

  server.registerTool(
    "list_project_documents",
    {
      description: "List uploaded project documents with OCR and knowledge-base status.",
      inputSchema: {},
    },
    async () => jsonToolResult(await backendRequest("/documents")),
  );

  server.registerTool(
    "run_document_ocr",
    {
      description:
        "Run OCR only when the target document is pending. If OCR is already processing, failed, or completed, return the current OCR state instead of rerunning.",
      inputSchema: {
        document_id: z.number(),
      },
    },
    async ({ document_id }) =>
      jsonToolResult(
        await backendRequest(`/documents/${document_id}/ocr`, {
          method: "POST",
          body: JSON.stringify({}),
        }),
      ),
  );

  server.registerTool(
    "get_document_ocr_result",
    {
      description: "Get the current OCR state or OCR result for an uploaded document.",
      inputSchema: {
        document_id: z.number(),
      },
    },
    async ({ document_id }) => jsonToolResult(await backendRequest(`/documents/${document_id}/ocr`)),
  );

  server.registerTool(
    "index_document_to_kb",
    {
      description: "Index an OCR-completed document into the local persistent Chroma knowledge base.",
      inputSchema: {
        document_id: z.number(),
      },
    },
    async ({ document_id }) =>
      jsonToolResult(
        await backendRequest(`/documents/${document_id}/index`, {
          method: "POST",
          body: JSON.stringify({}),
        }),
      ),
  );

  server.registerTool(
    "search_project_knowledge_base",
    {
      description: "Search the project knowledge base and return cited snippets.",
      inputSchema: {
        query: z.string(),
        limit: z.number().optional(),
      },
    },
    async ({ query, limit }) =>
      jsonToolResult(
        await backendRequest("/knowledge/search", {
          method: "POST",
          body: JSON.stringify({ query, limit }),
        }),
      ),
  );

  server.registerTool(
    "answer_with_project_knowledge_base",
    {
      description: "Answer a question strictly from the local project knowledge base with citations.",
      inputSchema: {
        question: z.string(),
        limit: z.number().optional(),
      },
    },
    async ({ question, limit }) =>
      jsonToolResult(
        await backendRequest("/knowledge/answer", {
          method: "POST",
          body: JSON.stringify({ question, limit }),
        }),
      ),
  );

  server.registerTool(
    "delete_project_document",
    {
      description: "Delete an uploaded document and purge its local knowledge-base chunks.",
      inputSchema: {
        document_id: z.number(),
      },
    },
    async ({ document_id }) =>
      jsonToolResult(
        await backendRequest(`/documents/${document_id}`, {
          method: "DELETE",
        }),
      ),
  );

  server.registerTool(
    "generate_editable_pptx",
    {
      description: "Generate a downloadable PPTX deck from a topic or project knowledge base.",
      inputSchema: {
        topic: z.string().optional(),
        slide_count: z.number().optional(),
        document_ids: z.array(z.number()).optional(),
        use_knowledge_base: z.boolean().optional(),
      },
    },
    async ({ topic, slide_count, document_ids, use_knowledge_base }) =>
      jsonToolResult(
        await backendRequest("/ppt/generate", {
          method: "POST",
          body: JSON.stringify({ topic, slide_count, document_ids, use_knowledge_base }),
        }),
      ),
  );

  server.registerTool(
    "get_ppt_generation_status",
    {
      description: "Get PPT generation result and download URL by presentation id.",
      inputSchema: {
        presentation_id: z.number(),
      },
    },
    async ({ presentation_id }) => jsonToolResult(await backendRequest(`/ppt/${presentation_id}`)),
  );

  return server;
}

async function getTransport(request: Request) {
  const sessionId = request.headers.get("mcp-session-id");

  if (sessionId) {
    return transports.get(sessionId)?.transport;
  }

  if (request.method !== "POST") {
    return null;
  }

  const body = (await request.clone().json().catch(() => null)) as { method?: string } | null;
  if (body?.method !== "initialize") {
    return null;
  }

  let createdTransport!: WebStandardStreamableHTTPServerTransport;
  const server = createLocalMcpServer();
  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: () => randomUUID(),
    onsessioninitialized: (newSessionId) => {
      transports.set(newSessionId, { server, transport: createdTransport });
    },
  });
  createdTransport = transport;
  transport.onclose = () => {
    if (transport.sessionId) {
      transports.delete(transport.sessionId);
    }
  };
  await server.connect(transport);
  return transport;
}

async function handle(request: Request) {
  const transport = await getTransport(request);
  if (!transport) {
    return Response.json(
      {
        jsonrpc: "2.0",
        error: {
          code: -32000,
          message: "Bad Request: No valid MCP session or initialize request provided",
        },
        id: null,
      },
      { status: 400 },
    );
  }

  try {
    return await transport.handleRequest(request);
  } catch (error) {
    return Response.json(
      {
        jsonrpc: "2.0",
        error: {
          code: -32603,
          message: error instanceof Error ? error.message : "Internal MCP server error",
        },
        id: null,
      },
      { status: 500 },
    );
  }
}

export async function POST(request: Request) {
  return handle(request);
}

export async function GET(request: Request) {
  return handle(request);
}

export async function DELETE(request: Request) {
  return handle(request);
}
