import csv
from collections import Counter
from pathlib import Path
from typing import Optional

from backend.extensions import db
from backend.models import JobDescription, Report, ScreeningResult


def build_summary(job: JobDescription) -> dict:
    results = (
        ScreeningResult.query.filter_by(jd_id=job.id)
        .order_by(ScreeningResult.ranking.is_(None), ScreeningResult.ranking.asc())
        .all()
    )
    total_candidates = len(results)
    scores = [float(item.suitability_score or 0) for item in results]
    avg_score = round(sum(scores) / total_candidates, 2) if total_candidates else 0
    strong_matches = sum(1 for score in scores if score >= 80)
    moderate_matches = sum(1 for score in scores if 60 <= score < 80)
    weak_matches = sum(1 for score in scores if score < 60)

    distribution = Counter()
    for score in scores:
        if score >= 80:
            distribution["80-100"] += 1
        elif score >= 60:
            distribution["60-79"] += 1
        elif score >= 40:
            distribution["40-59"] += 1
        else:
            distribution["0-39"] += 1

    return {
        "job": job.to_dict(),
        "total_candidates": total_candidates,
        "average_score": avg_score,
        "strong_matches": strong_matches,
        "moderate_matches": moderate_matches,
        "weak_matches": weak_matches,
        "score_distribution": distribution,
        "top_candidates": [item.to_dict() for item in results[:5]],
    }


def export_results_csv(job: JobDescription, export_folder: str) -> str:
    Path(export_folder).mkdir(parents=True, exist_ok=True)
    file_path = Path(export_folder) / f"job_{job.id}_results.csv"
    results = (
        ScreeningResult.query.filter_by(jd_id=job.id)
        .order_by(ScreeningResult.ranking.is_(None), ScreeningResult.ranking.asc())
        .all()
    )
    with file_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "Rank",
                "Candidate Name",
                "Score",
                "Recommendation",
                "Matched Skills",
                "Missing Skills",
                "Experience Years",
                "Education",
            ]
        )
        for result in results:
            writer.writerow(
                [
                    result.ranking,
                    result.resume.candidate_name if result.resume else "",
                    float(result.suitability_score or 0),
                    result.recommendation,
                    result.matched_skills or "",
                    result.missing_skills or "",
                    float(result.resume.experience_years or 0) if result.resume else 0,
                    result.resume.education if result.resume else "",
                ]
            )
    return str(file_path)


def save_report_record(user_id: int, jd_id: int, report_type: str, file_path: Optional[str] = None) -> Report:
    report = Report(
        user_id=user_id,
        jd_id=jd_id,
        type=report_type,
        date_range="All Time",
        file_path=file_path,
    )
    db.session.add(report)
    db.session.commit()
    return report
