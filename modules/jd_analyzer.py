"""
jd_analyzer.py
--------------
Extracts structured requirements from a raw Job Description (JD) text:
- required_skills : set of recognized skill keywords mentioned in the JD
- min_experience  : minimum years of experience requested (int or None)
- education_level : highest education keyword level requested (int or None)
- raw_text        : original JD text (used later for similarity scoring)
"""

from modules.constants import SKILL_KEYWORDS, EDUCATION_KEYWORDS
from modules.text_utils import clean_text, find_max_number_near


def extract_skills(text: str) -> set:
    """Match multi-word and single-word skills from SKILL_KEYWORDS
    against the cleaned JD/resume text."""
    cleaned = " " + clean_text(text) + " "
    found = set()
    for skill in SKILL_KEYWORDS:
        needle = " " + skill + " "
        if needle in cleaned:
            found.add(skill)
    return found


def extract_min_experience(text: str):
    return find_max_number_near(text, ["years", "year", "yrs", "yr"])


def extract_education_level(text: str):
    cleaned = clean_text(text)
    levels_found = []
    for keyword, level in EDUCATION_KEYWORDS.items():
        if f" {keyword} " in f" {cleaned} ":
            levels_found.append(level)
    return max(levels_found) if levels_found else None


def analyze_jd(text: str) -> dict:
    if text is None or not text.strip():
        raise ValueError("Job description text is empty.")

    return {
        "required_skills": extract_skills(text),
        "min_experience": extract_min_experience(text),
        "education_level": extract_education_level(text),
        "raw_text": text,
    }
