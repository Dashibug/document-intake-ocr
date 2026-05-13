"""Regex helpers and patterns (stubs)."""
import re

CARD_NUMBER_RE = re.compile(r"\b\d{12,19}\b")

def find_card_numbers(text):
    return CARD_NUMBER_RE.findall(text or "")
