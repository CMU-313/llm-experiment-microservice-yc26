from src import translator


def test_chinese(monkeypatch):
    mock_response = {
        "message": {
            "content": "ENGLISH: No\nTEXT: This is a Chinese message"
        }
    }

    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    is_english, translated_content = translator.translate("这是一条中文消息")

    assert is_english == False
    assert translated_content == "This is a Chinese message"


def test_llm_normal_response(monkeypatch):
    mock_response = {
        "message": {
            "content": "ENGLISH: No\nTEXT: Good morning"
        }
    }

    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    is_english, translated_content = translator.translate("Buenos dias")

    assert is_english is False
    assert translated_content == "Good morning"


def test_llm_gibberish_response(monkeypatch):
    mock_response = {
        "message": {
            "content": "blorp glorp ???"
        }
    }

    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "Hola"
    is_english, translated_content = translator.translate(original_content)

    assert is_english is True
    assert translated_content == original_content


def test_llm_missing_text_fallback(monkeypatch):
    mock_response = {
        "message": {
            "content": "ENGLISH: No"
        }
    }

    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "Bonjour"
    is_english, translated_content = translator.translate(original_content)

    assert is_english is True
    assert translated_content == original_content