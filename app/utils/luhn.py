"""Luhn algorithm utilities."""
import re

def digits_of(n):
    return [int(d) for d in str(n)]

def validate_luhn(number: str) -> bool:
    """Return True if number (string) passes Luhn checksum."""
    s = re.sub(r"\D", "", number or "")
    if not s:
        return False
    digits = digits_of(s)
    odd_sum = sum(digits[-1::-2])
    even_sum = 0
    for d in digits[-2::-2]:
        dbl = d * 2
        even_sum += dbl if dbl < 10 else dbl - 9
    return (odd_sum + even_sum) % 10 == 0
