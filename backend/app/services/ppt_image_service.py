from __future__ import annotations

import base64
from typing import Any
from urllib.request import Request, urlopen

from fastapi import HTTPException
from openai import OpenAI

from app.config import get_settings


class PPTImageService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.gpt_image_model
        self.base_url = settings.gpt_image_base_url
        self.api_key = settings.gpt_image_api_key
        self.primary_size = settings.gpt_image_size
        self.fallback_size = settings.gpt_image_fallback_size
        self.default_style_prompt = (
            "A modern premium presentation slide. "
            "Style: clean internet-tech aesthetic, elegant layout, light background, "
            "glassmorphism accents, soft gradients, sparse typography, sleek vector illustration. "
            "Avoid clutter, avoid academic template style, avoid heavy borders."
        )
        self.default_extra_body = {"quality": "high", "style": "natural", "upscale": "2k"}

    def generate_slide_image(self, visual_prompt: str, reference_style_prompt: str | None = None) -> bytes:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="缺少 GPT_IMAGE_API_KEY，无法生成 PPT 图片")
        client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

        prompt = self.default_style_prompt
        if reference_style_prompt:
            prompt += f" Keep visual consistency with previous slide style: {reference_style_prompt}. "
        prompt += (
            " Slide requirement: create a single full-slide presentation image for a 16:9 deck, "
            "keep key information inside safe margins, use sparse text only, avoid dense paragraphs. "
            f"{visual_prompt}"
        )

        try:
            response = client.images.generate(
                model=self.model,
                prompt=prompt,
                n=1,
                size=self.primary_size,
                extra_body=dict(self.default_extra_body),
            )
            return self._extract_image_bytes(response)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"gpt-image-2 生成图片失败：{exc}") from exc

    def _candidate_sizes(self) -> list[str]:
        sizes: list[str] = []
        for candidate in (self.primary_size, self.fallback_size):
            if candidate is None:
                continue
            cleaned = candidate.strip()
            if cleaned and cleaned not in sizes:
                sizes.append(cleaned)
        return sizes or ["16:9"]

    def _extract_image_bytes(self, response: Any) -> bytes:
        data = response.data[0]
        if getattr(data, "b64_json", None):
            return base64.b64decode(data.b64_json)
        if getattr(data, "url", None):
            request = Request(data.url, headers={"User-Agent": "ontology-ppt-agent"})
            with urlopen(request) as remote:
                return remote.read()
        raise HTTPException(status_code=500, detail="gpt-image-2 未返回可用图片")
