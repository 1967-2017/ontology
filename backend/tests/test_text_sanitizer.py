from app.services.text_sanitizer import sanitize_unicode_payload


def test_sanitize_unicode_payload_removes_surrogates_recursively():
    payload = {
        "full_text": "abc\ud835def",
        "pages": [{"text": "x\ud835y"}],
        "blocks": ["z\ud835w"],
    }

    sanitized = sanitize_unicode_payload(payload)

    assert sanitized["full_text"] == "abcdef"
    assert sanitized["pages"][0]["text"] == "xy"
    assert sanitized["blocks"][0] == "zw"
