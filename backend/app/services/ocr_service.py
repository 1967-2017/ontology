from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

from fastapi import HTTPException

from app.config import get_settings


class OCRService:
    def __init__(self) -> None:
        settings = get_settings()
        self.paddle_root = settings.paddleocr_root
        if self.paddle_root and self.paddle_root.exists():
            paddle_root_str = str(self.paddle_root)
            if paddle_root_str not in sys.path:
                sys.path.insert(0, paddle_root_str)

    def extract(self, file_path: str, file_type: str) -> dict[str, Any]:
        path = Path(file_path)
        if file_type == "pdf":
            pages = self._extract_pdf(path)
        elif file_type == "image":
            pages = [self._ocr_image(path, 1)]
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")

        blocks = [block for page in pages for block in page["blocks"]]
        full_text = "\n\n".join(page["text"] for page in pages if page["text"].strip()).strip()
        return {"full_text": full_text, "pages": pages, "blocks": blocks}

    def _extract_pdf(self, path: Path) -> list[dict[str, Any]]:
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError as exc:
            raise HTTPException(status_code=500, detail="缺少 pypdf，无法解析 PDF") from exc

        reader = PdfReader(str(path))
        pages: list[dict[str, Any]] = []
        extracted_text = False
        for index, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                extracted_text = True
                blocks = [{"page_number": index, "text": paragraph.strip()} for paragraph in text.split("\n") if paragraph.strip()]
                pages.append({"page_number": index, "text": text, "blocks": blocks, "source": "pdf_text"})

        if extracted_text:
            return pages

        try:
            import fitz  # type: ignore
        except ModuleNotFoundError as exc:
            raise HTTPException(status_code=500, detail="PDF 无可提取文本，且缺少 PyMuPDF 以执行 OCR 回退") from exc

        pdf = fitz.open(path)
        rendered_pages: list[dict[str, Any]] = []
        for index, page in enumerate(pdf, start=1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            try:
                from PIL import Image
            except ModuleNotFoundError as exc:
                raise HTTPException(status_code=500, detail="缺少 Pillow，无法执行 PDF OCR 回退") from exc
            image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            rendered_pages.append(self._ocr_pil_image(image, index))
        return rendered_pages

    def _ocr_image(self, path: Path, page_number: int) -> dict[str, Any]:
        try:
            from PIL import Image
        except ModuleNotFoundError as exc:
            raise HTTPException(status_code=500, detail="缺少 Pillow，无法读取图片") from exc
        image = Image.open(path).convert("RGB")
        return self._ocr_pil_image(image, page_number)

    def _ocr_pil_image(self, image: Any, page_number: int) -> dict[str, Any]:
        provider = self._build_provider()
        blocks = provider(image)
        text = "\n".join(block["text"] for block in blocks if block["text"].strip())
        return {"page_number": page_number, "text": text, "blocks": blocks, "source": "ocr"}

    def _build_provider(self):
        rapidocr_module = self._safe_import("rapidocr_onnxruntime")
        if rapidocr_module is not None:
            engine = rapidocr_module.RapidOCR()

            def run_rapidocr(image: Any) -> list[dict[str, Any]]:
                result, _ = engine(image)
                return self._normalize_rapidocr_result(result)

            return run_rapidocr

        paddleocr_module = self._safe_import("paddleocr")
        if paddleocr_module is not None:
            engine = paddleocr_module.PaddleOCR(use_angle_cls=True, lang="ch")

            def run_paddleocr(image: Any) -> list[dict[str, Any]]:
                result = engine.ocr(image, cls=True)
                return self._normalize_paddleocr_result(result)

            return run_paddleocr

        raise HTTPException(
            status_code=500,
            detail="未找到 RapidOCR 或 PaddleOCR。请先安装 OCR 依赖，或确认 E:\\paddleOCR 可用。",
        )

    def _safe_import(self, module_name: str):
        try:
            return importlib.import_module(module_name)
        except ModuleNotFoundError:
            return None

    def _normalize_rapidocr_result(self, result: Any) -> list[dict[str, Any]]:
        blocks: list[dict[str, Any]] = []
        if not result:
            return blocks
        for item in result:
            box, text, score = item
            blocks.append({"text": str(text), "score": float(score), "box": box})
        return blocks

    def _normalize_paddleocr_result(self, result: Any) -> list[dict[str, Any]]:
        blocks: list[dict[str, Any]] = []
        if not result:
            return blocks
        for page in result:
            for item in page or []:
                box, payload = item
                text, score = payload
                blocks.append({"text": str(text), "score": float(score), "box": box})
        return blocks
