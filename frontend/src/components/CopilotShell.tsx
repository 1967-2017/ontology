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
          instructions="你是 ontology 项目的智能助手。除 ontology 对象外，也支持已上传图片/PDF 的 OCR、本地知识库问答，以及基于资料生成 PPTX 格式汇报。"
          labels={{
            title: "Ontology Copilot",
            initial: "可以直接输入：创建项目、识别这份文件、把这份资料加入知识库、根据上传资料生成 6 页 PPTX 汇报。",
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
