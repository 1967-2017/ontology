import { createOpenAI } from "@ai-sdk/openai";
import { CopilotRuntime } from "@copilotkit/runtime";
import { BuiltInAgent, defineTool } from "@copilotkit/runtime/v2";
import { z } from "zod";

const backendBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function backendPost<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${backendBaseUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const json = (await response.json()) as { success: boolean; data: T; error?: { message?: string } | null };
  if (!response.ok || !json.success) {
    throw new Error(json.error?.message ?? "Backend request failed");
  }
  return json.data;
}

async function backendGet<T>(path: string): Promise<T> {
  const response = await fetch(`${backendBaseUrl}${path}`, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
  });
  const json = (await response.json()) as { success: boolean; data: T; error?: { message?: string } | null };
  if (!response.ok || !json.success) {
    throw new Error(json.error?.message ?? "Backend request failed");
  }
  return json.data;
}

const deepseek = createOpenAI({
  apiKey: process.env.DEEPSEEK_API_KEY,
  baseURL: process.env.DEEPSEEK_BASE_URL ?? "https://api.deepseek.com",
  fetch: async (input, init) => {
    if (!init?.body || typeof init.body !== "string") {
      return fetch(input, init);
    }

    const parsedBody = JSON.parse(init.body) as Record<string, unknown>;
    delete parsedBody.reasoning_effort;
    parsedBody.thinking = { type: "disabled" };

    return fetch(input, {
      ...init,
      body: JSON.stringify(parsedBody),
    });
  },
});

const defaultAgent = new BuiltInAgent({
  model: deepseek.chat(process.env.DEEPSEEK_MODEL ?? "deepseek-v4-flash"),
  maxSteps: 4,
  forwardDeveloperMessages: true,
  prompt: [
    "你是 ontology 项目的智能助手。",
    "你处理 Project、Team、Developer、Task 四类对象，也处理已上传文档的 OCR、本地知识库问答和 PPTX 汇报生成。",
    "用户表达创建/新增/添加对象时，优先调用前端动作 show_create_object_form。",
    "创建任务且用户已给出开发者名或项目名时，先调用 search_objects；唯一命中后把命中的 id 填进 preset_values。",
    "查询类问题只支持 developer_tasks、project_teams、team_members、project_tasks。",
    "查询结果必须调用前端动作 show_object_table。",
    "涉及 OCR、知识库和 PPT 前，先调用 list_project_documents 理解当前会话可用文档。",
    "list_project_documents 只返回当前会话仍可处理的附件，不包含已处理附件。",
    "OCR、入库和 PPT 工具本身会同步附件状态；OCR 完成时会直接渲染 OCR 结果，入库成功时会直接渲染结果通知，PPT 工具会直接渲染结果卡片。",
    "只有用户明确要求识别/OCR 时才允许调用 run_document_ocr 或 get_document_ocr_result。",
    "用户要求基于知识库回答时，调用 answer_with_project_knowledge_base，然后调用 show_rag_answer。",
    "用户要求根据上传文件、这份文件、当前资料生成 PPTX 汇报时，禁止只传 topic。必须先调用 list_project_documents 选择文档，再直接调用 generate_ppt_from_uploaded_documents 或 generate_editable_pptx，并传入 document_ids 和 slide_count；这条路径绝对禁止先调用 run_document_ocr 或 get_document_ocr_result，因为 PPT 工具会自己完成所需文本提取。",
    "PPT 生成工具本身会渲染结果卡片，不需要额外调用 show_ppt_result。",
    "需要说明结果时，用中文简洁说明，不输出原始 JSON。",
  ].join("\n"),
  tools: [
    defineTool({
      name: "get_ontology_classes",
      description: "Get the four supported ontology classes for this project.",
      parameters: z.object({}),
      execute: async () => backendGet("/ontology/classes"),
    }),
    defineTool({
      name: "search_objects",
      description: "Search Project, Team, Developer or Task records by keyword for prefill and disambiguation.",
      parameters: z.object({
        class_name: z.string(),
        keyword: z.string(),
      }),
      execute: async (args) => backendPost("/query/search", args),
    }),
    defineTool({
      name: "query_graph_context",
      description: "Run one of the fixed graph queries and return rows ready for rendering.",
      parameters: z.object({
        query_type: z.string(),
        params: z.object({
          developer_name: z.string().optional(),
          project_name: z.string().optional(),
          team_name: z.string().optional(),
        }),
      }),
      execute: async (args) => backendPost("/query/graph", args),
    }),
    defineTool({
      name: "import_mysql_to_neo4j",
      description:
        "Import local MySQL schema and row data into Neo4j. Use rebuild=true to clear the imported graph labels first, or rebuild=false for a sync import.",
      parameters: z.object({
        rebuild: z.boolean().default(false),
      }),
      execute: async (args) => backendPost("/admin/import/mysql-to-neo4j", args),
    }),
    defineTool({
      name: "search_project_knowledge_base",
      description: "Search the project knowledge base and return cited snippets.",
      parameters: z.object({
        query: z.string(),
        limit: z.number().optional(),
      }),
      execute: async (args) => backendPost("/knowledge/search", args),
    }),
    defineTool({
      name: "answer_with_project_knowledge_base",
      description: "Answer a question strictly based on the local project knowledge base with citations.",
      parameters: z.object({
        question: z.string(),
        limit: z.number().optional(),
      }),
      execute: async (args) => backendPost("/knowledge/answer", args),
    }),
    defineTool({
      name: "get_ppt_generation_status",
      description: "Get PPT generation result and download URL by presentation id.",
      parameters: z.object({
        presentation_id: z.number(),
      }),
      execute: async (args) => backendGet(`/ppt/${args.presentation_id}`),
    }),
  ],
});

export const copilotRuntime = new CopilotRuntime({
  agents: {
    default: defaultAgent,
  },
});
