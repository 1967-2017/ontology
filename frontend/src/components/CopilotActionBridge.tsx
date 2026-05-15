"use client";

import { useCopilotAction, useCopilotAdditionalInstructions } from "@copilotkit/react-core";
import { generateEditablePptx } from "@/lib/api";
import { useActionFeed } from "./ActionFeedContext";

export function CopilotActionBridge() {
  const { pushAction } = useActionFeed();

  useCopilotAdditionalInstructions(
    {
      instructions:
        "你是 ontology 项目的智能助手。你既处理 Project、Team、Developer、Task 四类对象和 MySQL→Neo4j 图导入，也处理已上传文档的 OCR、本地知识库问答和 PPTX 汇报生成。用户表达创建/新增/添加对象时，优先调用 show_create_object_form。创建任务且用户已给出开发者名或项目名时，先调用 search_objects；唯一命中后把命中的 id 放进 preset_values。Task 的项目字段名必须是 project_id，指派开发者字段名必须是 assignee_developer_id，不能写成 developer_id。Team 负责人字段名必须是 leader_developer_id。查询类问题只支持 developer_tasks、project_teams、team_members、project_tasks，查询结果必须调用 show_object_table。用户请求 OCR 时，先调用 list_project_documents 确认文档。只有在文档状态是 pending 时才调用 run_document_ocr。若状态是 processing 或 failed，调用 get_document_ocr_result 读取状态，不要手动重新触发 OCR。OCR 工具返回 status=completed 时才调用 show_ocr_result；返回 status=processing 或 failed 时调用 show_result_notice 展示处理中的说明或失败结果。用户请求知识库问答时，优先调用 answer_with_project_knowledge_base，随后调用 show_rag_answer。用户请求把文档加入知识库时，先列出文档并选择目标文档，再调用 index_document_to_kb。用户请求根据上传文件、这份文件、当前资料生成 PPTX 汇报时，必须先调用 list_project_documents 选择文档，再调用 generate_ppt_from_uploaded_documents 或 generate_editable_pptx 并传入 document_ids 和 slide_count；禁止退化成只根据 topic 生成通用汇报。用户请求生成 PPTX 汇报时，调用 generate_editable_pptx，随后调用 show_ppt_result。用户表达同步图数据库、导入 MySQL 到 Neo4j、重建图数据库时，调用 import_mysql_to_neo4j；普通同步用 rebuild=false，明确说重建或清空后重导时用 rebuild=true。工具执行后调用 show_result_notice 汇总结果。不要输出原始 JSON。"
    },
    [],
  );

  useCopilotAction({
    name: "generate_editable_pptx",
    description: "Generate a downloadable PPTX presentation from a topic, uploaded documents, or the current knowledge base, then render the result card.",
    parameters: [
      { name: "topic", type: "string", description: "Presentation topic.", required: false },
      { name: "slide_count", type: "number", description: "Slide count.", required: false },
      { name: "document_ids", type: "number[]", description: "Uploaded source document ids.", required: false },
      { name: "use_knowledge_base", type: "boolean", description: "Whether to use the project knowledge base.", required: false },
    ],
    handler: async (args) => {
      const result = await generateEditablePptx({
        topic: args.topic ? String(args.topic) : undefined,
        slide_count: args.slide_count ? Number(args.slide_count) : undefined,
        document_ids: Array.isArray(args.document_ids)
          ? args.document_ids.map((item) => Number(item)).filter((item) => Number.isFinite(item))
          : undefined,
        use_knowledge_base: typeof args.use_knowledge_base === "boolean" ? args.use_knowledge_base : undefined,
      });

      pushAction({
        name: "show_ppt_result",
        payload: {
          presentation_id: result.presentation_id,
          title: result.title,
          topic: result.topic,
          status: result.status,
          slide_count: result.slide_count,
          download_url: result.download_url,
          source_document_ids: result.source_document_ids ?? [],
        },
      });

      return `PPTX 已生成，共 ${result.slide_count} 页。`;
    },
  });

  useCopilotAction({
    name: "generate_ppt_from_uploaded_documents",
    description: "Generate a downloadable PPTX presentation directly from uploaded project documents, then render the result card.",
    parameters: [
      { name: "document_ids", type: "number[]", description: "Uploaded source document ids.", required: true },
      { name: "slide_count", type: "number", description: "Slide count.", required: false },
      { name: "topic", type: "string", description: "Optional presentation topic.", required: false },
    ],
    handler: async (args) => {
      const result = await generateEditablePptx({
        topic: args.topic ? String(args.topic) : undefined,
        slide_count: args.slide_count ? Number(args.slide_count) : undefined,
        document_ids: Array.isArray(args.document_ids)
          ? args.document_ids.map((item) => Number(item)).filter((item) => Number.isFinite(item))
          : [],
        use_knowledge_base: false,
      });

      pushAction({
        name: "show_ppt_result",
        payload: {
          presentation_id: result.presentation_id,
          title: result.title,
          topic: result.topic,
          status: result.status,
          slide_count: result.slide_count,
          download_url: result.download_url,
          source_document_ids: result.source_document_ids ?? [],
        },
      });

      return `PPTX 已生成，共 ${result.slide_count} 页。`;
    },
  });

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
    handler: async (args) => {
      pushAction({
        name: "show_create_object_form",
        payload: {
          class_name: String(args.class_name),
          preset_values: (args.preset_values as Record<string, unknown> | undefined) ?? {},
        },
      });
      return "创建表单已渲染到主区域。";
    },
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
    handler: async (args) => {
      pushAction({
        name: "show_object_table",
        payload: {
          class_name: String(args.class_name),
          rows: (args.rows as Record<string, unknown>[] | undefined) ?? [],
        },
      });
      return "结果表格已渲染到主区域。";
    },
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
    handler: async (args) => {
      pushAction({
        name: "show_result_notice",
        payload: {
          title: String(args.title),
          message: String(args.message),
          status: String(args.status) === "error" ? "error" : "success",
        },
      });
      return "通知已渲染到主区域。";
    },
  });

  useCopilotAction({
    name: "show_ocr_result",
    description: "Render OCR text result for an uploaded document.",
    parameters: [
      { name: "document_id", type: "number", description: "Uploaded document id.", required: true },
      { name: "filename", type: "string", description: "Original filename.", required: true },
      { name: "full_text", type: "string", description: "OCR full text.", required: true },
      { name: "pages", type: "object[]", description: "OCR page list.", required: true },
    ],
    handler: async (args) => {
      pushAction({
        name: "show_ocr_result",
        payload: {
          document_id: Number(args.document_id),
          filename: String(args.filename),
          full_text: String(args.full_text),
          pages: (args.pages as Record<string, unknown>[] | undefined) ?? [],
        },
      });
      return "OCR 结果已渲染到主区域。";
    },
  });

  useCopilotAction({
    name: "show_rag_answer",
    description: "Render a project knowledge base answer with citations.",
    parameters: [
      { name: "answer", type: "string", description: "Answer text.", required: true },
      { name: "citations", type: "object[]", description: "Citations list.", required: true },
      { name: "matched_documents", type: "string[]", description: "Matched source filenames.", required: true },
    ],
    handler: async (args) => {
      pushAction({
        name: "show_rag_answer",
        payload: {
          answer: String(args.answer),
          citations:
            (args.citations as
              | { document_id: number; filename: string; page_number?: number | null; snippet: string; score: number }[]
              | undefined) ?? [],
          matched_documents: (args.matched_documents as string[] | undefined) ?? [],
        },
      });
      return "知识库回答已渲染到主区域。";
    },
  });

  useCopilotAction({
    name: "show_ppt_result",
    description: "Render generated PPTX report result with download link.",
    parameters: [
      { name: "presentation_id", type: "number", description: "Presentation id.", required: true },
      { name: "title", type: "string", description: "Presentation title.", required: true },
      { name: "topic", type: "string", description: "Presentation topic.", required: true },
      { name: "status", type: "string", description: "Generation status.", required: true },
      { name: "slide_count", type: "number", description: "Slide count.", required: true },
      { name: "download_url", type: "string", description: "Download URL.", required: false },
    ],
    handler: async (args) => {
      pushAction({
        name: "show_ppt_result",
        payload: {
          presentation_id: Number(args.presentation_id),
          title: String(args.title),
          topic: String(args.topic),
          status: String(args.status),
          slide_count: Number(args.slide_count),
          download_url: args.download_url ? String(args.download_url) : null,
          source_document_ids: [],
        },
      });
      return "PPT 结果已渲染到主区域。";
    },
  });

  return null;
}
