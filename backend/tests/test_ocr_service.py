from types import SimpleNamespace
import builtins
import sys

import pytest
from fastapi import HTTPException
from PIL import Image

from app.services.ocr_service import OCRService


def test_extend_import_paths_adds_site_packages(monkeypatch, tmp_path):
    service = OCRService()
    fake_sys_path: list[str] = []
    monkeypatch.setattr(sys, "path", fake_sys_path)

    fake_root = tmp_path / "paddle-env"
    site_packages = fake_root / "Lib" / "site-packages"
    site_packages.mkdir(parents=True)

    service._extend_import_paths(fake_root)

    assert str(fake_root) in fake_sys_path
    assert str(site_packages) in fake_sys_path


def test_build_provider_reports_missing_dependencies(monkeypatch):
    service = OCRService()
    monkeypatch.setattr(service, "_safe_import", lambda module_name: None)

    with pytest.raises(HTTPException) as exc_info:
        service._build_provider()

    assert "ontology-dev" in exc_info.value.detail
    assert "paddleocr" in exc_info.value.detail.lower()


def test_build_provider_raises_clear_error_when_paddleocr_init_fails(monkeypatch):
    service = OCRService()

    class BrokenPaddleOCRModule:
        class PaddleOCR:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("model files missing")

    monkeypatch.setattr(
        service,
        "_safe_import",
        lambda module_name: BrokenPaddleOCRModule if module_name == "paddleocr" else None,
    )

    with pytest.raises(HTTPException) as exc_info:
        service._build_provider()

    assert "PaddleOCR 初始化失败" in exc_info.value.detail


def test_build_provider_converts_pil_image_for_paddleocr(monkeypatch):
    service = OCRService()

    captured = {}

    class FakePaddleOCRInstance:
        def ocr(self, image, cls=True):
            captured["image_type"] = type(image).__name__
            captured["shape"] = getattr(image, "shape", None)
            return [[([[0, 0], [1, 0], [1, 1], [0, 1]], ("OCR", 0.99))]]

    class FakePaddleOCRModule:
        class PaddleOCR:
            def __new__(cls, *args, **kwargs):
                return FakePaddleOCRInstance()

    monkeypatch.setattr(
        service,
        "_safe_import",
        lambda module_name: FakePaddleOCRModule if module_name == "paddleocr" else None,
    )

    provider = service._build_provider()
    result = provider(Image.new("RGB", (32, 32), color="white"))

    assert captured["image_type"] == "ndarray"
    assert captured["shape"] == (32, 32, 3)
    assert result[0]["text"] == "OCR"


def test_extract_pdf_requires_pymupdf_for_scanned_pdf(monkeypatch, tmp_path):
    service = OCRService()
    pdf_path = tmp_path / "scan.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 mock")

    class EmptyPage:
        def extract_text(self):
            return ""

    class FakePdfReader:
        def __init__(self, path):
            self.pages = [EmptyPage()]

    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "fitz":
            raise ModuleNotFoundError("No module named 'fitz'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setitem(sys.modules, "pypdf", SimpleNamespace(PdfReader=FakePdfReader))
    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(HTTPException) as exc_info:
        service._extract_pdf(pdf_path)

    assert "PyMuPDF" in exc_info.value.detail
