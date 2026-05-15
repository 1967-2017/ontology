from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.services.ppt_image_service import PPTImageService


class FakeImagesApi:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def generate(self, **kwargs):
        self.calls.append(kwargs)
        response = self.responses[len(self.calls) - 1]
        if isinstance(response, Exception):
            raise response
        return response


class FakeOpenAIClient:
    def __init__(self, responses):
        self.images = FakeImagesApi(responses)


def _fake_image_response():
    return SimpleNamespace(data=[SimpleNamespace(b64_json="aGVsbG8=", url=None)])


def test_generate_slide_image_sends_size_and_extra_body(monkeypatch):
    service = PPTImageService()
    service.api_key = "test-key"
    service.primary_size = "16:9"
    service.fallback_size = None

    fake_client = FakeOpenAIClient([_fake_image_response()])
    monkeypatch.setattr("app.services.ppt_image_service.OpenAI", lambda **kwargs: fake_client)

    payload = service.generate_slide_image("test visual")

    assert payload == b"hello"
    assert len(fake_client.images.calls) == 1
    first_call = fake_client.images.calls[0]
    assert first_call["size"] == "16:9"
    assert first_call["extra_body"] == {"quality": "high", "style": "natural", "upscale": "2k"}
    assert "16:9 deck" in first_call["prompt"]


def test_candidate_sizes_uses_only_primary_size_when_fallback_disabled():
    service = PPTImageService()
    service.primary_size = "16:9"
    service.fallback_size = None

    assert service._candidate_sizes() == ["16:9"]


def test_generate_slide_image_requires_api_key():
    service = PPTImageService()
    service.api_key = None

    with pytest.raises(HTTPException) as exc_info:
        service.generate_slide_image("test visual")

    assert "GPT_IMAGE_API_KEY" in exc_info.value.detail
