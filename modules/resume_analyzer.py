"""
resume_analyzer.py
-------------------
Extracts structured candidate information from raw resume text:
- name       : best-guess candidate name (heuristic: first meaningful line)
- email      : first email address found
- phone      : first phone number found
- skills     : set of recognized skill keywords found in the resume
- experience : detected years of experience (int, default 0)
- education_level : highest education keyword level found (int or None)
- raw_text   : original resume text (used later for similarity scoring)
"""

import os

from modules.jd_analyzer import extract_skills, extract_education_level
from modules.text_utils import (
    extract_emails,
    extract_phone_numbers,
    find_max_number_near,
)


def extract_name(text: str, fallback: str = "Unknown Candidate") -> str:
    if not text:
        return fallback
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Skip lines that look like headers/emails/phones
        lowered = stripped.lower()
        if "@" in stripped or any(ch.isdigit() for ch in stripped):
            continue
        if len(stripped.split()) <= 5 and stripped.replace(" ", "").isalpha():
            return stripped.title()
        break
    return fallback


def extract_experience_years(text: str) -> int:
    years = find_max_number_near(text, ["years", "year", "yrs", "yr"])
    return years if years is not None else 0


def analyze_resume(text: str, source_path: str = "") -> dict:
    if text is None or not text.strip():
        raise ValueError("Resume text is empty.")

    emails = extract_emails(text)
    phones = extract_phone_numbers(text)
    filename = os.path.basename(source_path) if source_path else ""

    return {
        "name": extract_name(text, fallback=filename or "Unknown Candidate"),
        "email": emails[0] if emails else "Not found",
        "phone": phones[0] if phones else "Not found",
        "skills": extract_skills(text),
        "experience_years": extract_experience_years(text),
        "education_level": extract_education_level(text),
        "raw_text": text,
        "source_file": filename,
    }
