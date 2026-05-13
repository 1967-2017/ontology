"use client";

import { FormEvent, useState } from "react";

import { sendAgentMessage } from "@/lib/api";
import { TimelineItem, toTimelineActions } from "@/lib/agui";
import { ActionRenderer } from "./ActionRenderer";

export function ChatWorkspace() {
  const [message, setMessage] = useState("");
  const [timeline, setTimeline] = useState<TimelineItem[]>([
    {
      id: "welcome",
      type: "message",
      role: "assistant",
      content: "可直接输入：创建项目、创建团队、创建开发者、创建任务，或查看张三的任务。",
    },
  ]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim()) {
      return;
    }

    const currentMessage = message;
    setMessage("");
    setTimeline((items) => [...items, { id: `user-${Date.now()}`, type: "message", role: "user", content: currentMessage }]);

    const response = await sendAgentMessage(currentMessage);
    setTimeline((items) => [
      ...items,
      { id: `assistant-${Date.now()}`, type: "message", role: "assistant", content: response.reply },
      ...toTimelineActions(response.actions),
    ]);
  }

  function pushNotice(notice: { title: string; message: string; status: "success" | "error" }) {
    setTimeline((items) => [
      ...items,
      {
        id: `notice-${Date.now()}`,
        type: "action",
        action: { name: "show_result_notice", payload: notice },
      },
    ]);
  }

  return (
    <div className="workspace">
      <aside className="sidebar">
        <p className="eyebrow">Copilot Sidebar</p>
        <h2>Ontology Agent</h2>
        <p className="sidebar-copy">
          当前实现先对齐设计稿中的 action 协议。待你确认具体 AG-UI 仓库后，可直接替换这一层为真实 SDK。
        </p>
      </aside>
      <main className="main-panel">
        <div className="timeline">
          {timeline.map((item) =>
            item.type === "message" ? (
              <article key={item.id} className={`bubble bubble-${item.role}`}>
                {item.content}
              </article>
            ) : (
              <ActionRenderer key={item.id} action={item.action} onNotice={pushNotice} />
            ),
          )}
        </div>
        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            className="chat-input"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="输入：创建任务，或者查看张三的任务"
          />
          <button className="button" type="submit">
            发送
          </button>
        </form>
      </main>
    </div>
  );
}
