"use client";

type Props = {
  presentationId: number;
  title: string;
  topic: string;
  status: string;
  slideCount: number;
  downloadUrl?: string | null;
  sourceDocumentIds?: number[];
};

export function PptResultCard({
  presentationId,
  title,
  topic,
  status,
  slideCount,
  downloadUrl,
  sourceDocumentIds,
}: Props) {
  return (
    <section className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">PPTX Export</p>
          <h3>{title}</h3>
        </div>
        <span className="chip">{status}</span>
      </div>
      <p className="sidebar-copy">
        主题：{topic} · 页数：{slideCount} · 任务 #{presentationId}
      </p>
      {sourceDocumentIds?.length ? <p className="sidebar-copy">已处理资料：{sourceDocumentIds.join("、")}</p> : null}
      {downloadUrl ? (
        <a className="button button-link" href={downloadUrl} target="_blank" rel="noreferrer">
          下载 PPTX 汇报
        </a>
      ) : (
        <p>当前没有可下载文件。</p>
      )}
    </section>
  );
}
