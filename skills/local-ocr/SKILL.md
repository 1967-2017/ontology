---
name: local-ocr
description: Perform OCR for uploaded images or PDFs in this ontology project, inspect OCR state, wait on in-progress jobs, and show cached OCR results without rerunning completed or failed work. Use when the task involves recognizing text from project documents, checking OCR status, or troubleshooting local OCR flows.
---

# Local OCR

Use the project's local document pipeline rather than inventing a new OCR path.

## Workflow

1. List available documents first.
2. Pick the target document, usually the most recently uploaded one when the user says "this file".
3. Inspect OCR state before deciding anything:
   - `pending`: trigger OCR once.
   - `processing`: wait and report the current processing state. Do not rerun.
   - `failed`: report the failure state. Do not rerun unless the user explicitly asks.
   - `completed`: show the cached result.
4. Render OCR output through the project's result card action when text is available.

## Project Endpoints

- `GET /documents`
- `POST /documents/{document_id}/ocr`
- `GET /documents/{document_id}/ocr`

## Notes

- The OCR API is stateful. `POST /documents/{document_id}/ocr` returns a structured state payload even when the document is already `processing`, `failed`, or `completed`.
- OCR text is sanitized before persistence, so invalid surrogate Unicode characters should not be reintroduced downstream.
- The recommended runtime is the main `ontology-dev` backend environment with `paddleocr + PyMuPDF` installed directly.
- `PADDLEOCR_ROOT` is only a compatibility fallback for an external Python environment; do not rely on it by default.
- Prefer the project MCP tool names that mirror these endpoints when the local MCP server is available.
