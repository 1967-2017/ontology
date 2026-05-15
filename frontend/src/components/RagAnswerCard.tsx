"use client";

type Props = {
  answer: string;
  citations: { document_id: number; filename: string; page_number?: number | null; snippet: string; score: number }[];
  matchedDocuments: string[];
};

export function RagAnswerCard({ answer, citations, matchedDocuments }: Props) {
  return (
    <section className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">Knowledge Answer</p>
          <h3>知识库回答</h3>
        </div>
        <span className="chip">{matchedDocuments.length} 份资料</span>
      </div>
      <div className="result-panel">
        <pre className="result-text">{answer}</pre>
      </div>
      <div className="citation-list">
        {citations.map((citation) => (
          <article key={`${citation.document_id}-${citation.page_number ?? 0}-${citation.score}`} className="citation-card">
            <strong>{citation.filename}</strong>
            <p>
              {citation.page_number ? `第 ${citation.page_number} 页` : "未标注页码"} · 相关度 {citation.score}
            </p>
            <p>{citation.snippet}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
