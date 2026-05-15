from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException
from openai import OpenAI

from app.config import get_settings


class PPTPlannerService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.deepseek_model
        self.base_url = settings.deepseek_base_url
        self.api_key = settings.deepseek_api_key

    def generate_outline(self, topic: str, slide_count: int, context_text: str) -> dict[str, Any]:
        if not self.api_key:
            raise HTTPException(status_code=500, detail="缺少 DEEPSEEK_API_KEY，无法生成 PPT 大纲")
        client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )

        system_prompt = f"""
You are a senior strategy consultant and presentation director.

TASK:
Generate a document-grounded presentation outline.

RULES:
1. Output exactly {slide_count} slides.
2. Slide 1 must be a cover slide.
3. The final slide title must be `结论与行动建议`.
4. Middle slides must follow the document's logic, not generic summary templates.
5. Use the reference content to infer a narrative arc:
   background -> concept -> method -> value -> scenarios -> risks -> outlook
6. If some sections are missing, reorganize around the strongest available document logic.
7. Return slide titles and content summaries in Chinese.
8. Each slide must include a visual_prompt for image generation.
9. visual_prompt must describe a modern, clean, high-end presentation slide with sparse text rendered into the image.
10. Each slide object may only contain index, title, content_summary, visual_prompt.

OUTPUT JSON:
{{
  "global_style": "...",
  "slides": [
    {{
      "index": 0,
      "title": "...",
      "content_summary": "...",
      "visual_prompt": "..."
    }}
  ]
}}
"""
        user_message = f"Topic: {topic}\n\nReference Context:\n{context_text}"
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                response_format={"type": "json_object"},
            )
            payload = response.choices[0].message.content or "{}"
            data = json.loads(payload)
            slides = data.get("slides", [])
            if len(slides) != slide_count:
                raise HTTPException(status_code=500, detail="大纲模型返回的页数与请求不一致")
            return data
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"DeepSeek 大纲生成失败：{exc}") from exc
