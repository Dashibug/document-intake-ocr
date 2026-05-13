"""Base extractor classes."""
class BaseExtractor:
    """Base class for extractors."""
    def extract(self, data):
        raise NotImplementedError()
