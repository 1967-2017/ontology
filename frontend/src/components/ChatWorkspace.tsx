"use client";

import { ActionRenderer } from "./ActionRenderer";
import { useActionFeed } from "./ActionFeedContext";
import { DocumentWorkbench } from "./DocumentWorkbench";

export function ChatWorkspace() {
  const { items, pushAction } = useActionFeed();

  function pushNotice(notice: { title: string; message: string; status: "success" | "error" }) {
    pushAction({
      name: "show_result_notice",
      payload: notice,
    });
  }

  return (
    <div className="workspace">
      <aside className="sidebar">
        <p className="eyebrow">Action Canvas</p>
        <h2>Ontology Workspace</h2>
        <p className="sidebar-copy">左侧 CopilotSidebar 负责真实 LLM 对话，主区域显示当前会话附件以及被触发的表单、结果和通知。</p>
        <p className="sidebar-copy">推荐试试：上传资料后直接说“识别这份文件”“把这份资料加入知识库”“根据上传资料生成 6 页 PPTX 汇报”。</p>
      </aside>
      <main className="main-panel">
        <DocumentWorkbench />
        <div className="timeline">
          {items.length === 0 ? (
            <section className="card">
              <div className="card-header">
                <div>
                  <p className="eyebrow">Ready</p>
                  <h3>等待 Copilot 动作</h3>
                </div>
              </div>
              <p>在左侧聊天窗口输入创建、查询、OCR、知识库或 PPTX 汇报请求，结果会显示在这里。</p>
            </section>
          ) : null}
          {items.map((item) => (
            <ActionRenderer key={item.id} action={item.action} onNotice={pushNotice} />
          ))}
        </div>
      </main>
    </div>
  );
}
