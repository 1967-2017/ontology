import React from "react";
import { render, screen } from "@testing-library/react";

import { ObjectTableCard } from "./ObjectTableCard";

describe("ObjectTableCard", () => {
  it("shows empty state when rows are empty", () => {
    render(<ObjectTableCard className="Task" rows={[]} />);
    expect(screen.getByText("暂无数据")).toBeInTheDocument();
  });

  it("renders table columns from the first row", () => {
    render(<ObjectTableCard className="Task" rows={[{ id: 1, title: "demo", status: "todo" }]} />);
    expect(screen.getByText("title")).toBeInTheDocument();
    expect(screen.getByText("demo")).toBeInTheDocument();
  });
});
