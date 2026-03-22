from backend.services.resume_parser import extract_skills
from backend.utils.validators import as_int, join_multi_value, split_multi_value


def prepare_job_payload(data: dict) -> dict:
    title = (data.get("title") or "").strip()
    description_text = (data.get("description_text") or "").strip()
    required_skills = split_multi_value(data.get("required_skills"))
    keywords = split_multi_value(data.get("keywords"))
    qualifications = split_multi_value(data.get("qualifications"))

    if not required_skills and description_text:
        required_skills = extract_skills(description_text)
    if not keywords:
        keywords = required_skills[:]

    return {
        "title": title,
        "description_text": description_text,
        "required_skills": join_multi_value(required_skills),
        "keywords": join_multi_value(keywords),
        "min_experience": as_int(data.get("min_experience"), 0),
        "qualifications": join_multi_value(qualifications),
    }
