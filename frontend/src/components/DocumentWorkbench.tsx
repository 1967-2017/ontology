"use client";

import { useEffect, useState, useTransition } from "react";

import {
  deleteProjectDocument,
  getDocumentOcrResult,
  indexDocumentToKnowledgeBase,
  runDocumentOcr,
  uploadProjectDocument,
} from "@/lib/api";
import { ProjectDocument } from "@/types/ontology";
import { useActionFeed } from "./ActionFeedContext";

type Notice = { title: string; message: string; status: "success" | "error" };

export function DocumentWorkbench() {
  const { items, pushAction } = useActionFeed();
  const [pendingDocuments, setPendingDocuments] = useState<ProjectDocument[]>([]);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const raw = window.localStorage.getItem("pending-upload-documents");
    if (!raw) {
      return;
    }
    try {
      const parsed = JSON.parse(raw) as ProjectDocument[];
      setPendingDocuments(Array.isArray(parsed) ? parsed : []);
    } catch {
      window.localStorage.removeItem("pending-upload-documents");
    }
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    window.localStorage.setItem("pending-upload-documents", JSON.stringify(pendingDocuments));
  }, [pendingDocuments]);

  useEffect(() => {
    for (const item of items) {
      if (item.action.name === "show_ocr_result") {
        removePendingDocuments([item.action.payload.document_id]);
      }
      if (item.action.name === "show_ppt_result") {
        removePendingDocuments(item.action.payload.source_document_ids ?? []);
      }
    }
  }, [items]);

  function pushNotice(notice: Notice) {
    pushAction({ name: "show_result_notice", payload: notice });
  }

  function removePendingDocuments(documentIds: number[]) {
    if (documentIds.length === 0) {
      return;
    }
    setPendingDocuments((current) => current.filter((document) => !documentIds.includes(document.document_id)));
  }

  async function handleUpload(file: File | null) {
    if (!file) {
      return;
    }
    try {
      const uploaded = await uploadProjectDocument(file);
      setPendingDocuments((current) => [uploaded, ...current.filter((item) => item.document_id !== uploaded.document_id)]);
      pushNotice({
        title: "上传完成",
        message: `已加入当前会话附件：${uploaded.filename}。发送去处理后，它会自动从工作区移出。`,
        status: "success",
      });
    } catch (error) {
      pushNotice({
        title: "上传失败",
        message: error instanceof Error ? error.message : "文档上传失败",
        status: "error",
      });
    }
  }

  async function handleOcr(document: ProjectDocument) {
    removePendingDocuments([document.document_id]);
    try {
      const result =
        document.ocr_status === "completed"
          ? await getDocumentOcrResult(document.document_id)
          : await runDocumentOcr(document.document_id);
      if (result.status === "completed") {
        pushAction({
          name: "show_ocr_result",
          payload: {
            document_id: document.document_id,
            filename: result.filename ?? document.filename,
            full_text: result.full_text,
            pages: result.pages,
          },
        });
      } else {
        pushNotice({
          title: result.status === "failed" ? "OCR 失败" : "OCR 处理中",
          message: result.message ?? "OCR 当前没有可展示的结果。",
          status: result.status === "failed" ? "error" : "success",
        });
      }
    } catch (error) {
      pushNotice({
        title: "OCR 失败",
        message: error instanceof Error ? error.message : "文档识别失败",
        status: "error",
      });
    }
  }

  async function handleIndex(document: ProjectDocument) {
    removePendingDocuments([document.document_id]);
    try {
      await indexDocumentToKnowledgeBase(document.document_id);
      pushNotice({
        title: "已入库",
        message: `${document.filename} 已写入本地知识库。`,
        status: "success",
      });
    } catch (error) {
      pushNotice({
        title: "入库失败",
        message: error instanceof Error ? error.message : "知识库写入失败",
        status: "error",
      });
    }
  }

  async function handleDelete(document: ProjectDocument) {
    try {
      await deleteProjectDocument(document.document_id);
      removePendingDocuments([document.document_id]);
      pushNotice({
        title: "已删除",
        message: `${document.filename} 已从本地存储和知识库移除。`,
        status: "success",
      });
    } catch (error) {
      pushNotice({
        title: "删除失败",
        message: error instanceof Error ? error.message : "文档删除失败",
        status: "error",
      });
    }
  }

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <p className="eyebrow">Attachment Tray</p>
          <h3>当前会话附件</h3>
        </div>
        <span className="chip">{pendingDocuments.length} 份待发送附件</span>
      </div>
      <label className="upload-dropzone">
        <input
          type="file"
          accept=".pdf,image/*"
          className="sr-only"
          onChange={(event) => {
            const [file] = Array.from(event.target.files ?? []);
            startTransition(() => {
              void handleUpload(file ?? null);
            });
            event.target.value = "";
          }}
        />
        <strong>上传图片或 PDF</strong>
        <p>这里仅显示当前待处理附件。附件一旦被送去 OCR、入库或生成 PDF，就会自动从工作区移出。</p>
      </label>
      <div className="doc-list">
        {pendingDocuments.length === 0 ? <p>当前没有待发送附件。</p> : null}
        {pendingDocuments.map((document) => (
          <article key={document.document_id} className="doc-row">
            <div>
              <strong>{document.filename}</strong>
              <p>
                OCR: {document.ocr_status} · KB: {document.knowledge_status}
              </p>
            </div>
            <div className="toolbar">
              <button className="chip" type="button" onClick={() => void handleOcr(document)} disabled={isPending}>
                {document.ocr_status === "completed" ? "查看 OCR" : "运行 OCR"}
              </button>
              <button className="chip" type="button" onClick={() => void handleIndex(document)} disabled={isPending}>
                加入知识库
              </button>
              <button className="chip" type="button" onClick={() => void handleDelete(document)} disabled={isPending}>
                删除
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
