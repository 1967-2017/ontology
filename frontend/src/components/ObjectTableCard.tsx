"use client";

type Props = {
  className: string;
  rows: Record<string, unknown>[];
};

export function ObjectTableCard({ className, rows }: Props) {
  const columns = rows[0] ? Object.keys(rows[0]) : [];

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">Query Result</p>
          <h3>{className}</h3>
        </div>
      </div>
      {rows.length === 0 ? (
        <p className="empty-state">暂无数据</p>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr key={index}>
                  {columns.map((column) => (
                    <td key={column}>{String(row[column] ?? "")}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
