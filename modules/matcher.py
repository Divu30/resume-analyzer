"""
matcher.py
----------
Core comparison logic: given a parsed Job Description and a parsed
Resume, compute a match score and a detailed breakdown.

Scoring formula (weights sum to 100):
- Skill match      : 60%  -> (matched required skills / total required skills)
- Text similarity  : 20%  -> difflib ratio between JD text and resume text
- Experience match : 10%  -> full credit if resume years >= JD min years
- Education match  : 10%  -> full credit if resume education level >= JD level

If the JD does not specify a requirement (e.g. no experience mentioned),
that component is given full credit by default so it does not unfairly
penalize candidates.
"""

from modules.text_utils import similarity_ratio

WEIGHT_SKILLS = 0.60
WEIGHT_TEXT_SIMILARITY = 0.20
WEIGHT_EXPERIENCE = 0.10
WEIGHT_EDUCATION = 0.10


def compute_match(jd_data: dict, resume_data: dict) -> dict:
    required_skills = jd_data.get("required_skills", set())
    candidate_skills = resume_data.get("skills", set())

    matched_skills = sorted(required_skills & candidate_skills)
    missing_skills = sorted(required_skills - candidate_skills)
    extra_skills = sorted(candidate_skills - required_skills)

    if required_skills:
        skill_score = (len(matched_skills) / len(required_skills)) * 100
    else:
        skill_score = 100.0

    text_score = similarity_ratio(jd_data.get("raw_text", ""),
                                   resume_data.get("raw_text", ""))

    min_exp = jd_data.get("min_experience")
    candidate_exp = resume_data.get("experience_years", 0)
    if min_exp is None:
        experience_score = 100.0
        experience_ok = True
    else:
        experience_ok = candidate_exp >= min_exp
        experience_score = 100.0 if experience_ok else max(
            0.0, (candidate_exp / min_exp) * 100
        )

    jd_edu = jd_data.get("education_level")
    cand_edu = resume_data.get("education_level")
    if jd_edu is None:
        education_score = 100.0
        education_ok = True
    else:
        education_ok = cand_edu is not None and cand_edu >= jd_edu
        education_score = 100.0 if education_ok else 0.0

    overall_score = (
        skill_score * WEIGHT_SKILLS
        + text_score * WEIGHT_TEXT_SIMILARITY
        + experience_score * WEIGHT_EXPERIENCE
        + education_score * WEIGHT_EDUCATION
    )

    return {
        "candidate_name": resume_data.get("name", "Unknown"),
        "email": resume_data.get("email", "Not found"),
        "phone": resume_data.get("phone", "Not found"),
        "source_file": resume_data.get("source_file", ""),
        "overall_score": round(overall_score, 2),
        "skill_score": round(skill_score, 2),
        "text_similarity_score": round(text_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "extra_skills": extra_skills,
        "candidate_experience_years": candidate_exp,
        "required_experience_years": min_exp,
        "experience_ok": experience_ok,
        "education_ok": education_ok,
    }


def rank_candidates(jd_data: dict, resumes_data: list) -> list:
    """Return match results sorted by overall_score, descending."""
    results = [compute_match(jd_data, r) for r in resumes_data]
    results.sort(key=lambda r: r["overall_score"], reverse=True)
    return results
