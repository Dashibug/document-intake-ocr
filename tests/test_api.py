from app.main import create_app


def test_create_app():
    app = create_app()
    assert isinstance(app, dict)
    assert app.get("name") == "document-intake-ocr-stub"
