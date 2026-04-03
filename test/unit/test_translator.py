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


def test_llm_whitespace_text_returns_original_text(monkeypatch):
    mock_response = {"message": {"content": "ENGLISH: Yes\nTEXT:   "}}
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "This is a non-English message"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is True
    assert translated_content == original_content


#given that the parsing logic splits on colons, we need to test that the text line preserves colons
def test_text_line_preserves_colons(monkeypatch):
    mock_response = {"message": {"content": "ENGLISH: Yes\nTEXT: This is a: random colon message"}}
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "This is a: random colon message"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is True
    assert translated_content == original_content


def test_multiple_input_lines_takes_last(monkeypatch):
    mock_response = {"message": {"content": "ENGLISH: No\nTEXT: This is a non-English message\nENGLISH: Yes\nTEXT: This is a random message"}}
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "This is a non-English message\nThis is a random message"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is False
    assert translated_content == "This is a random message"
    

def test_llm_japanese_to_english_translation(monkeypatch):
    mock_response = {"message": {"content": "ENGLISH: No\nTEXT: Hello, this is a complex sentences with a lot of terms to test accuracy of translation"}}
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "こんにちは, これは複雑な文です。多くの用語をテストするために、翻訳の正確性をテストします。"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is False
    assert translated_content == "Hello, this is a complex sentences with a lot of terms to test accuracy of translation"

def test_llm_thai_to_english_translation(monkeypatch):
    mock_response = {"message": {"content": "ENGLISH: No\nTEXT: Hello, this is a complex sentences with a lot of terms to test accuracy of translation"}}
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "สวัสดี, นี่คือประโยคที่ซับซ้อนมากที่สุดที่สามารถทดสอบความแม่นยำของการแปล"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is False
    assert translated_content == "Hello, this is a complex sentences with a lot of terms to test accuracy of translation"

def test_llm_vietnamese_to_english_translation(monkeypatch):
    mock_response = {"message": {"content": "ENGLISH: No\nTEXT: Hello, this is a complex sentences with a lot of terms to test accuracy of translation"}}
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "Xin chào, đây là một câu phức tạp với nhiều thuật ngữ để kiểm tra độ chính xác của bản dịch"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is False
    assert translated_content == "Hello, this is a complex sentences with a lot of terms to test accuracy of translation"

def test_llm_korean_to_english_translation(monkeypatch):
    mock_response = {"message": {"content": "ENGLISH: No\nTEXT: Hello, this is a complex sentences with a lot of terms to test accuracy of translation"}}
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "안녕하세요, 이것은 복잡한 문장입니다. 많은 용어를 테스트하기 위해 번역 정확도를 테스트합니다."
    is_english, translated_content = translator.translate(original_content)
    assert is_english is False
    assert translated_content == "Hello, this is a complex sentences with a lot of terms to test accuracy of translation"

#if there is no extractable content, None is inputted into the LLM and the original text is returned, ensuring NodeBB doesn't crash
def test_no_response_fallback(monkeypatch):
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: None)
    original_content = "Bonjour"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is True
    assert translated_content == original_content

def test_non_string_response_fallback(monkeypatch):
    mock_response = {"message": {"content": None}}
    monkeypatch.setattr(translator.client, "chat", lambda **kwargs: mock_response)
    original_content = "Hello"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is True
    assert translated_content == original_content

#mocking raising an error, and ensuring original text is returned, NodeBB doesn't crash
def test_chat_raises_returns_original(monkeypatch):
    def boom(**kwargs):
        raise RuntimeError("ollama down")
    monkeypatch.setattr(translator.client, "chat", boom)
    original_content = "Bonjour"
    is_english, translated_content = translator.translate(original_content)
    assert is_english is True
    assert translated_content == original_content

