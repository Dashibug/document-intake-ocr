"""Bank card extractor (stub)."""
from .base import BaseExtractor

class BankCardExtractor(BaseExtractor):
    def extract(self, data):
        return {"type": "bank_card", "data": {}}
