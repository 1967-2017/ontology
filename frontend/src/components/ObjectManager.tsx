"use client";

import { useEffect, useState } from "react";

import { fetchOntologyClasses, importMysqlToNeo4j, listObjects } from "@/lib/api";
import { CreateOntologyObjectCard } from "./CreateOntologyObjectCard";
import { ObjectTableCard } from "./ObjectTableCard";
import { ResultNoticeCard } from "./ResultNoticeCard";

export function ObjectManager() {
  const [classes, setClasses] = useState<{ class_name: string; label: string }[]>([]);
  const [activeClass, setActiveClass] = useState("Project");
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [notice, setNotice] = useState<{ title: string; message: string; status: "success" | "error" } | null>(null);
  const [importingMode, setImportingMode] = useState<"sync" | "rebuild" | null>(null);

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

  async function handleImport(rebuild: boolean) {
    setImportingMode(rebuild ? "rebuild" : "sync");
    try {
      const result = await importMysqlToNeo4j(rebuild);
      setNotice({
        title: rebuild ? "重建导入完成" : "同步导入完成",
        message:
          `处理 ${result.tables_processed} 张表，导入 ${result.nodes_created_or_updated} 个节点，` +
          `${result.relationships_created} 条关系。` +
          (result.errors.length > 0 ? ` 错误数：${result.errors.length}` : ""),
        status: result.errors.length > 0 ? "error" : "success",
      });
    } catch (error) {
      setNotice({
        title: "导入失败",
        message: error instanceof Error ? error.message : "无法执行 MySQL 到 Neo4j 导入",
        status: "error",
      });
    } finally {
      setImportingMode(null);
    }
  }

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
        <button className="button" disabled={importingMode !== null} onClick={() => handleImport(false)} type="button">
          {importingMode === "sync" ? "同步中..." : "同步导入图"}
        </button>
        <button className="button button-secondary" disabled={importingMode !== null} onClick={() => handleImport(true)} type="button">
          {importingMode === "rebuild" ? "重建中..." : "重建导入图"}
        </button>
      </div>
      {notice ? <ResultNoticeCard {...notice} /> : null}
      <div className="split-grid">
        <CreateOntologyObjectCard className={activeClass} onNotice={setNotice} />
        <ObjectTableCard className={activeClass} rows={rows} />
      </div>
    </div>
  );
}
