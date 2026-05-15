---
name: pptx-generator
description: Generate PPTX-format presentation decks from a topic or uploaded project documents using a DeepSeek outline planner and gpt-image-2 slide rendering flow. Use when the task involves project report generation, document-to-slide conversion, or exporting a non-editable presentation from current project materials.
---

# PPTX Generator

Use the project's PPTX presentation pipeline rather than assembling slides manually.

## Workflow

1. Decide whether the user wants a topic-only deck or a document-grounded deck.
2. If the deck depends on uploaded files, pass the project document ids directly. Do not require prior OCR or knowledge-base indexing.
3. Trigger deck generation with topic, slide count, and optional document scope.
4. Inspect the generated status payload and return the download link when available.

## Project Endpoints

- `POST /ppt/generate`
- `GET /ppt/{presentation_id}`
- `GET /ppt/{presentation_id}/download`

## Notes

- The current implementation generates a non-editable `.pptx` deck where each slide is a single full-page image.
- The deck is planned by DeepSeek and slide imagery is rendered by `gpt-image-2`.
- Image generation must pass explicit `size="16:9"`, plus `extra_body={"quality":"high","style":"natural","upscale":"2k"}`.
- The server does not crop, pad, or composite slide images. It expects the image model to return a true 16:9 slide image directly.
- If the user says "based on current knowledge base", set the generation flow to use the project knowledge base.
- Return the generated deck through the project's PPT result card action when working in the chat UI.
