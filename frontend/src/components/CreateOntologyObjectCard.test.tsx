import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import { CreateOntologyObjectCard } from "./CreateOntologyObjectCard";

vi.mock("@/lib/api", () => ({
  fetchFormSchema: vi.fn(async () => ({
    class_name: "Task",
    title: "创建任务",
    fields: [
      { name: "title", label: "任务标题", data_type: "string", required: true },
      {
        name: "status",
        label: "状态",
        data_type: "enum",
        required: true,
        enum_options: ["todo", "doing"],
      },
    ],
  })),
  createObject: vi.fn(async () => ({
    object: { class_name: "Task", id: 1, values: { title: "demo", status: "todo" } },
    graph_sync: { status: "success" },
  })),
}));

describe("CreateOntologyObjectCard", () => {
  it("renders fetched fields", async () => {
    render(<CreateOntologyObjectCard className="Task" />);
    await waitFor(() => expect(screen.getByText("创建任务")).toBeInTheDocument());
    expect(screen.getByText("任务标题 *")).toBeInTheDocument();
    expect(screen.getByText("状态 *")).toBeInTheDocument();
  });

  it("shows validation notice when required field is empty", async () => {
    const onNotice = vi.fn();
    render(<CreateOntologyObjectCard className="Task" onNotice={onNotice} />);
    await waitFor(() => expect(screen.getByText("创建任务")).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "提交创建" }));
    expect(onNotice).toHaveBeenCalledWith(
      expect.objectContaining({
        title: "表单校验失败",
      }),
    );
  });
});
