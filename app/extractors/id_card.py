"""ID card extractor (stub)."""
from .base import BaseExtractor

class IDCardExtractor(BaseExtractor):
    def extract(self, data):
        return {"type": "id_card", "data": {}}
