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

  it("renders OCR result action", () => {
    render(
      <ActionRenderer
        action={{
          name: "show_ocr_result",
          payload: { document_id: 1, filename: "sample.pdf", full_text: "识别文本", pages: [] },
        }}
        onNotice={() => undefined}
      />,
    );
    expect(screen.getByText("sample.pdf")).toBeInTheDocument();
    expect(screen.getByText("识别文本")).toBeInTheDocument();
  });
});
