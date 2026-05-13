"""Logging setup (basic)."""
import logging

def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(message)s")
    return logging.getLogger("document-intake-ocr")

logger = setup_logging()
