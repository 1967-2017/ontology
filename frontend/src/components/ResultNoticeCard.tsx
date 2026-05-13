"use client";

type Props = {
  title: string;
  message: string;
  status: "success" | "error";
};

export function ResultNoticeCard({ title, message, status }: Props) {
  return (
    <section className={`card notice notice-${status}`}>
      <div className="card-header">
        <div>
          <p className="eyebrow">{status === "success" ? "Success" : "Warning"}</p>
          <h3>{title}</h3>
        </div>
      </div>
      <p>{message}</p>
    </section>
  );
}
