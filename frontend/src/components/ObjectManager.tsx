"use client";

import { useEffect, useState } from "react";

import { fetchOntologyClasses, listObjects } from "@/lib/api";
import { CreateOntologyObjectCard } from "./CreateOntologyObjectCard";
import { ObjectTableCard } from "./ObjectTableCard";
import { ResultNoticeCard } from "./ResultNoticeCard";

export function ObjectManager() {
  const [classes, setClasses] = useState<{ class_name: string; label: string }[]>([]);
  const [activeClass, setActiveClass] = useState("Project");
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [notice, setNotice] = useState<{ title: string; message: string; status: "success" | "error" } | null>(null);

  useEffect(() => {
    fetchOntologyClasses()
      .then(setClasses)
      .catch((error) =>
        setNotice({
          title: "类定义加载失败",
          message: error instanceof Error ? error.message : "无法加载 ontology classes",
          status: "error",
        }),
      );
  }, []);

  useEffect(() => {
    listObjects(activeClass)
      .then((result) => setRows(result.items))
      .catch((error) => {
        setRows([]);
        setNotice({
          title: "列表加载失败",
          message: error instanceof Error ? error.message : "无法加载对象列表",
          status: "error",
        });
      });
  }, [activeClass]);

  return (
    <div className="object-page">
      <div className="toolbar">
        {classes.map((item) => (
          <button
            key={item.class_name}
            className={`chip ${item.class_name === activeClass ? "chip-active" : ""}`}
            onClick={() => setActiveClass(item.class_name)}
            type="button"
          >
            {item.label}
          </button>
        ))}
      </div>
      {notice ? <ResultNoticeCard {...notice} /> : null}
      <div className="split-grid">
        <CreateOntologyObjectCard className={activeClass} onNotice={setNotice} />
        <ObjectTableCard className={activeClass} rows={rows} />
      </div>
    </div>
  );
}
