"use client";

import { useTransition } from "react";

import {
  deleteProjectDocument,
  getDocumentOcrResult,
  indexDocumentToKnowledgeBase,
  runDocumentOcr,
  uploadProjectDocument,
} from "@/lib/api";
import { useActionFeed } from "./ActionFeedContext";

type Notice = { title: string; message: string; status: "success" | "error" };

export function DocumentWorkbench() {
  const {
    pushAction,
    sessionDocuments,
    upsertSessionDocument,
    patchSessionDocument,
    removeSessionDocuments,
  } = useActionFeed();
  const [isPending, startTransition] = useTransition();

  function pushNotice(notice: Notice) {
    pushAction({ name: "show_result_notice", payload: notice });
  }
  async function handleUpload(file: File | null) {
    if (!file) {
      return;
    }
    try {
      const uploaded = await uploadProjectDocument(file);
      upsertSessionDocument(uploaded);
      pushNotice({
        title: "上传完成",
        message: `已加入当前会话附件：${uploaded.filename}。该附件执行一次功能后会自动移出列表。`,
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
    try {
      const result =
        document.ocr_status === "completed"
          ? await getDocumentOcrResult(document.document_id)
          : await runDocumentOcr(document.document_id);
      if (result.status === "completed") {
        removeSessionDocuments([document.document_id]);
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
        patchSessionDocument(document.document_id, { ocr_status: result.status ?? document.ocr_status });
        pushNotice({
          title: result.status === "failed" ? "OCR 失败" : "OCR 处理中",
          message: result.message ?? "OCR 当前没有可展示的结果。",
          status: result.status === "failed" ? "error" : "success",
        });
      }
    } catch (error) {
      patchSessionDocument(document.document_id, { ocr_status: "failed" });
      pushNotice({
        title: "OCR 失败",
        message: error instanceof Error ? error.message : "文档识别失败",
        status: "error",
      });
    }
  }

  async function handleIndex(document: ProjectDocument) {
    try {
      if (document.ocr_status !== "completed") {
        const ocrResult = await runDocumentOcr(document.document_id);
        if (ocrResult.status !== "completed") {
          patchSessionDocument(document.document_id, { ocr_status: ocrResult.status ?? document.ocr_status });
          pushNotice({
            title: ocrResult.status === "failed" ? "OCR 失败" : "OCR 处理中",
            message: ocrResult.message ?? "OCR 当前没有可展示的结果。",
            status: ocrResult.status === "failed" ? "error" : "success",
          });
          return;
        }
        patchSessionDocument(document.document_id, { ocr_status: "completed" });
      }
      await indexDocumentToKnowledgeBase(document.document_id);
      removeSessionDocuments([document.document_id]);
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
      removeSessionDocuments([document.document_id]);
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
        <span className="chip">{sessionDocuments.length} 份待处理附件</span>
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
        <p>这里显示当前待处理附件。每次上传的附件只能执行一次功能，完成 OCR、入库或生成 PPT 后会自动移出。</p>
      </label>
      <div className="doc-list">
        {sessionDocuments.length === 0 ? <p>当前没有待处理附件。</p> : null}
        {sessionDocuments.map((document) => (
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
