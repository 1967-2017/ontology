import React from "react";
import { render, screen } from "@testing-library/react";

import { ActionRenderer } from "./ActionRenderer";

describe("ActionRenderer", () => {
  it("renders result notice action", () => {
    render(
      <ActionRenderer
        action={{
          name: "show_result_notice",
          payload: { title: "创建成功", message: "对象已创建", status: "success" },
        }}
        onNotice={() => undefined}
      />,
    );
    expect(screen.getByText("创建成功")).toBeInTheDocument();
    expect(screen.getByText("对象已创建")).toBeInTheDocument();
  });
});
