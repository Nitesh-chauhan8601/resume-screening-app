import re
from pathlib import Path
from typing import List, Optional

from backend.utils.text_cleaner import clean_text, remove_bias_terms
from backend.utils.validators import join_multi_value

try:
    import docx2txt
except ImportError:  # pragma: no cover
    docx2txt = None

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

try:
    import spacy
except ImportError:  # pragma: no cover
    spacy = None


SKILL_DB = [
    "python",
    "java",
    "c",
    "c++",
    "flask",
    "django",
    "mysql",
    "sql",
    "html",
    "css",
    "javascript",
    "typescript",
    "react",
    "angular",
    "node.js",
    "express",
    "git",
    "github",
    "rest api",
    "machine learning",
    "nlp",
    "spacy",
    "scikit-learn",
    "tensorflow",
    "pandas",
    "numpy",
    "excel",
    "communication",
    "teamwork",
]

EDUCATION_KEYWORDS = [
    "bca",
    "b.tech",
    "btech",
    "mca",
    "m.tech",
    "bsc",
    "msc",
    "computer science",
    "information technology",
]

CERTIFICATION_KEYWORDS = [
    "certified",
    "certification",
    "aws",
    "azure",
    "google cloud",
]

TOKENIZER = spacy.blank("en") if spacy else None


def extract_text_from_pdf(file_path: str) -> str:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber is not installed")
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return "\n".join(pages)


def extract_text_from_docx(file_path: str) -> str:
    if docx2txt is None:
        raise RuntimeError("docx2txt is not installed")
    return docx2txt.process(file_path) or ""


def extract_text_from_file(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    if suffix == ".docx":
        return extract_text_from_docx(file_path)
    raise ValueError("Unsupported file type")


def tokenize_text(text: str) -> List[str]:
    if TOKENIZER is None:
        return re.findall(r"[a-zA-Z][a-zA-Z0-9.+#-]*", text.lower())
    return [token.text.lower() for token in TOKENIZER(text) if not token.is_space]


def extract_email(text: str) -> str:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(r"(\+?\d[\d\s-]{8,}\d)", text)
    return match.group(0).strip() if match else ""


def extract_candidate_name(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:8]:
        words = line.split()
        lowered = line.lower()
        if 2 <= len(words) <= 4 and lowered not in {"resume", "curriculum vitae"}:
            if all(re.match(r"^[A-Za-z.'-]+$", word) for word in words):
                return line.title()
                
    if spacy:
        try:
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text[:2000])
            for ent in doc.ents:
                if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
                    return ent.text.title()
        except Exception:
            pass

    email = extract_email(text)
    if email:
        return email.split("@")[0].replace(".", " ").title()
    return "Unknown Candidate"


def extract_skills(text: str, skill_db: Optional[List[str]] = None) -> List[str]:
    skill_db = skill_db or SKILL_DB
    lowered = f" {text.lower()} "
    found = []
    for skill in skill_db:
        pattern = rf"(?<!\w){re.escape(skill.lower())}(?!\w)"
        if re.search(pattern, lowered):
            found.append(skill)
    return sorted(set(found), key=str.lower)


def extract_education(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    matched = []
    for line in lines:
        lower_line = line.lower()
        if any(keyword in lower_line for keyword in EDUCATION_KEYWORDS):
            matched.append(line)
    return "\n".join(dict.fromkeys(matched))


def extract_certifications(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    matched = []
    for line in lines:
        lower_line = line.lower()
        if any(keyword in lower_line for keyword in CERTIFICATION_KEYWORDS):
            matched.append(line)
    return join_multi_value(dict.fromkeys(matched))


def extract_experience_years(text: str) -> float:
    lowered = text.lower()
    
    word_to_num = {
        "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
        "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
        "eleven": "11", "twelve": "12"
    }
    for word, num in word_to_num.items():
        lowered = re.sub(rf"\b{word}\b", num, lowered)

    matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|year|yrs|yr)", lowered)
    if not matches:
        month_matches = re.findall(r"(\d+)\s*(?:months|month)", lowered)
        if month_matches:
            return round(max(int(value) for value in month_matches) / 12, 1)
        return 0.0
    return max(float(value) for value in matches)


def build_experience_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    experience_lines = []
    for line in lines:
        lower_line = line.lower()
        if "experience" in lower_line or re.search(
            r"\d+(?:\.\d+)?\s*(?:years|year|yrs|yr|months|month)",
            lower_line,
        ):
            experience_lines.append(line)
    return "\n".join(dict.fromkeys(experience_lines[:10]))


def parse_resume_text(text: str) -> dict:
    cleaned_text = remove_bias_terms(clean_text(text))
    skills = extract_skills(cleaned_text)
    return {
        "candidate_name": extract_candidate_name(cleaned_text),
        "email": extract_email(cleaned_text),
        "phone": extract_phone(cleaned_text),
        "skills": join_multi_value(skills),
        "education": extract_education(cleaned_text),
        "experience_text": build_experience_text(cleaned_text),
        "experience_years": extract_experience_years(cleaned_text),
        "certifications": extract_certifications(cleaned_text),
        "raw_text": cleaned_text,
    }


def parse_resume_file(file_path: str) -> dict:
    text = extract_text_from_file(file_path)
    if not text.strip():
        raise ValueError("Resume text extraction returned empty content")
    return parse_resume_text(text)
