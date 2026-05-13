"""Generic extractor fallback."""
from .base import BaseExtractor

class GenericExtractor(BaseExtractor):
    def extract(self, data):
        return {"type": "generic", "data": {}}
