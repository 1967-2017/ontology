"use client";

import { ActionRenderer } from "./ActionRenderer";
import { useActionFeed } from "./ActionFeedContext";

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
        <p className="sidebar-copy">左侧 CopilotSidebar 负责真实 LLM 对话，主区域只显示被触发的表单、表格和通知。</p>
        <p className="sidebar-copy">推荐试试：创建项目、查看test项目有哪些团队、给张三创建一个任务，归属test项目。</p>
      </aside>
      <main className="main-panel">
        <div className="timeline">
          {items.length === 0 ? (
            <section className="card">
              <div className="card-header">
                <div>
                  <p className="eyebrow">Ready</p>
                  <h3>等待 Copilot 动作</h3>
                </div>
              </div>
              <p>在左侧聊天窗口输入创建或查询请求，结果会显示在这里。</p>
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
