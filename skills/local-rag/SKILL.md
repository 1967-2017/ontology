---
name: local-rag
description: Index OCR-completed project documents into the local persistent Chroma knowledge base, search citations, answer questions with sources, and delete project documents cleanly. Use when the task involves project document retrieval, cited answers, or managing the local document knowledge base.
---

# Local RAG

Use the project's persisted Chroma-backed knowledge base instead of ad hoc text scanning.

## Workflow

1. List documents and confirm the target material.
2. Ensure the document has completed OCR before indexing.
3. Index the document into the knowledge base.
4. For question answering, always return the cited answer payload from the project toolchain.
5. If nothing is retrieved, state that clearly. Do not invent content.
6. When deleting a document, purge it through the project delete flow so Chroma entries are removed too.

## Project Endpoints

- `POST /documents/{document_id}/index`
- `POST /knowledge/search`
- `POST /knowledge/answer`
- `DELETE /documents/{document_id}`

## Notes

- The backing store is a persistent local Chroma collection under the project's data directory.
- Preserve filename and page citations in any final answer or UI action.
- For "this file" requests, resolve the target document from the latest uploaded project document first.
