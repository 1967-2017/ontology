"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import { ReactNode } from "react";
import { ActionFeedProvider } from "./ActionFeedContext";
import { CopilotActionBridge } from "./CopilotActionBridge";

type Props = {
  children: ReactNode;
};

export function CopilotShell({ children }: Props) {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <ActionFeedProvider>
        <CopilotSidebar
          defaultOpen
          instructions="你是 ontology 项目的智能助手。严格围绕 Project、Team、Developer、Task 四类对象工作。"
          labels={{
            title: "Ontology Copilot",
            initial: "可以直接输入：创建项目、查看test项目有哪些团队、给张三创建一个任务，归属test项目。",
            placeholder: "输入你的业务问题或创建请求",
          }}
          clickOutsideToClose={false}
        >
          <CopilotActionBridge />
          <div className="copilot-frame">{children}</div>
        </CopilotSidebar>
      </ActionFeedProvider>
    </CopilotKit>
  );
}
