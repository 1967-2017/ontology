"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { ReactNode } from "react";
import { CopilotActionBridge } from "./CopilotActionBridge";

type Props = {
  children: ReactNode;
};

export function CopilotShell({ children }: Props) {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <CopilotSidebar
        defaultOpen
        instructions="你是 ontology v1 agent。优先通过自定义 action 渲染创建表单和查询表格。"
        labels={{
          title: "Ontology Copilot",
          initial: "输入“创建项目”或“查看张三的任务”开始。",
        }}
        clickOutsideToClose={false}
      >
        <CopilotActionBridge />
        <div className="copilot-frame">{children}</div>
      </CopilotSidebar>
    </CopilotKit>
  );
}
