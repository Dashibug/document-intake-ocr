from app.extractors.generic import GenericExtractor


def test_generic_extractor():
    e = GenericExtractor()
    assert e.extract({})["type"] == "generic"
