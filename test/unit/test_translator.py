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

def test_english_text(monkeypatch):
    mock_response = {
        "message": {
            "content": "ENGLISH: Yes\nTEXT: Hello world"
        }
    }

    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    is_english, translated_content = translator.translate("Hello world")

    assert is_english is True
    assert translated_content == "Hello world"


def test_french_text(monkeypatch):
    mock_response = {
        "message": {
            "content": "ENGLISH: No\nTEXT: Good evening"
        }
    }

    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    is_english, translated_content = translator.translate("Bonsoir")

    assert is_english is False
    assert translated_content == "Good evening"


def test_response_with_think_artifacts(monkeypatch):
    mock_response = {
        "message": {
            "content": "/think I need to analyze this text\nENGLISH: No\nTEXT: Hello there"
        }
    }

    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    is_english, translated_content = translator.translate("Hola amigo")

    assert is_english is False
    assert translated_content == "Hello there"


def test_empty_response_fallback(monkeypatch):
    mock_response = {
        "message": {
            "content": ""
        }
    }

    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "Test message"
    is_english, translated_content = translator.translate(original_content)

    assert is_english is True
    assert translated_content == original_content


def test_raw_yes_no_format(monkeypatch):
    mock_response = {
        "message": {
            "content": "No\nThis is the translation"
        }
    }

    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    is_english, translated_content = translator.translate("Hola mundo")

    assert is_english is False
    assert translated_content == "This is the translation"
    
def test_llm_english_returns_original_text(monkeypatch):
    mock_response = {"message": {"content": "ENGLISH: Yes\nTEXT: This is an English message"}}
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "This is an English message"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is True
    assert translated_content == original_content