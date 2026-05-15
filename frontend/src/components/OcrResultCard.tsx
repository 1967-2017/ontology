"use client";

type Props = {
  documentId: number;
  filename: string;
  fullText: string;
  pages: Record<string, unknown>[];
};

export function OcrResultCard({ documentId, filename, fullText, pages }: Props) {
  return (
    <section className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">OCR Result</p>
          <h3>{filename}</h3>
        </div>
        <span className="chip">文档 #{documentId}</span>
      </div>
      <p className="sidebar-copy">共识别 {pages.length} 页。以下为主文本结果，可重复查看，无需再次识别。</p>
      <div className="result-panel">
        <pre className="result-text">{fullText || "未识别到文本。"}</pre>
      </div>
    </section>
  );
}
