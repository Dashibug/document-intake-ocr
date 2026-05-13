"""Driver license extractor (stub)."""
from .base import BaseExtractor

class DriverLicenseExtractor(BaseExtractor):
    def extract(self, data):
        return {"type": "driver_license", "data": {}}
