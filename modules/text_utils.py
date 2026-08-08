"""
text_utils.py
-------------
Generic, dependency-free text processing helpers used by both the
Job Description analyzer and the Resume analyzer.

Only Python's built-in `re`, `string`, `difflib` and `collections`
modules are used - no external packages.
"""

import re
import string
import difflib
from collections import Counter

from modules.constants import STOPWORDS


def clean_text(text: str) -> str:
    """Lowercase text and normalize whitespace while preserving
    characters commonly found inside skill names such as '+', '#', '.'.
    """
    if not text:
        return ""
    text = text.lower()
    # Keep letters, digits, spaces and a few symbols used in skills
    # (c++, c#, node.js, asp.net, etc.)
    allowed = set(string.ascii_lowercase + string.digits + " +#./-")
    text = "".join(ch if ch in allowed else " " for ch in text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str):
    """Split cleaned text into a list of word tokens."""
    cleaned = clean_text(text)
    if not cleaned:
        return []
    return cleaned.split(" ")


def remove_stopwords(tokens):
    return [t for t in tokens if t and t not in STOPWORDS]


def get_word_frequency(text: str) -> Counter:
    tokens = remove_stopwords(tokenize(text))
    return Counter(tokens)


def extract_emails(text: str):
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    return re.findall(pattern, text or "")


def extract_phone_numbers(text: str):
    pattern = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3,4}\)?[-.\s]?)?\d{3}[-.\s]?\d{3,4}"
    candidates = re.findall(pattern, text or "")
    # Keep only sequences with at least 9 digits (avoid false positives)
    results = []
    for c in candidates:
        digits = re.sub(r"\D", "", c)
        if 9 <= len(digits) <= 13:
            results.append(c.strip())
    return results


def similarity_ratio(text_a: str, text_b: str) -> float:
    """Return a 0-100 similarity score between two texts using the
    built-in difflib.SequenceMatcher (no external NLP library)."""
    a = clean_text(text_a)
    b = clean_text(text_b)
    if not a or not b:
        return 0.0
    return round(difflib.SequenceMatcher(None, a, b).ratio() * 100, 2)


def find_max_number_near(text: str, keywords):
    """Search for a number that appears near one of `keywords`
    (e.g. 'years', 'yrs') and return the maximum match found.
    Used to detect experience requirements like '3+ years'.
    """
    if not text:
        return None
    text_lower = text.lower()
    numbers = []
    for kw in keywords:
        pattern = r"(\d{1,2})\+?\s*(?:" + re.escape(kw) + r")"
        found = re.findall(pattern, text_lower)
        numbers.extend(int(n) for n in found)
    return max(numbers) if numbers else None
