"use client";

import { useCopilotAction, useCopilotAdditionalInstructions } from "@copilotkit/react-core";
import { useActionFeed } from "./ActionFeedContext";

export function CopilotActionBridge() {
  const { pushAction } = useActionFeed();

  useCopilotAdditionalInstructions(
    {
      instructions:
        "你是 ontology 项目的智能助手。只处理 Project、Team、Developer、Task 四类对象和 MySQL→Neo4j 图导入。用户表达创建/新增/添加对象时，优先调用 show_create_object_form。创建任务且用户已给出开发者名或项目名时，先调用 search_objects；唯一命中后把命中的 id 放进 preset_values。Task 的项目字段名必须是 project_id，指派开发者字段名必须是 assignee_developer_id，不能写成 developer_id。Team 负责人字段名必须是 leader_developer_id。查询类问题只支持 developer_tasks、project_teams、team_members、project_tasks，查询结果必须调用 show_object_table。用户表达同步图数据库、导入 MySQL 到 Neo4j、重建图数据库时，调用 import_mysql_to_neo4j；普通同步用 rebuild=false，明确说重建或清空后重导时用 rebuild=true。工具执行后调用 show_result_notice 汇总处理表数、节点数、关系数和错误数。不要输出原始 JSON。",
    },
    [],
  );

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

  return null;
}
