from backend.extensions import db
from backend.utils.validators import split_multi_value


class ScreeningResult(db.Model):
    __tablename__ = "screening_results"

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"), nullable=False)
    jd_id = db.Column(db.Integer, db.ForeignKey("job_descriptions.id"), nullable=False)
    skill_score = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    experience_score = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    education_score = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    similarity_score = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    suitability_score = db.Column(db.Numeric(5, 2), nullable=False, default=0.0)
    ranking = db.Column(db.Integer)
    recommendation = db.Column(db.String(30))
    matched_skills = db.Column(db.Text)
    missing_skills = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    resume = db.relationship("Resume", back_populates="results")
    job_description = db.relationship("JobDescription", back_populates="results")

    @property
    def matched_skill_list(self) -> list[str]:
        return split_multi_value(self.matched_skills)

    @property
    def missing_skill_list(self) -> list[str]:
        return split_multi_value(self.missing_skills)

    def to_dict(self, include_resume: bool = True) -> dict:
        payload = {
            "id": self.id,
            "resume_id": self.resume_id,
            "jd_id": self.jd_id,
            "skill_score": float(self.skill_score or 0),
            "experience_score": float(self.experience_score or 0),
            "education_score": float(self.education_score or 0),
            "similarity_score": float(self.similarity_score or 0),
            "suitability_score": float(self.suitability_score or 0),
            "ranking": self.ranking,
            "recommendation": self.recommendation,
            "matched_skills": self.matched_skill_list,
            "missing_skills": self.missing_skill_list,
            "notes": self.notes or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_resume and self.resume:
            payload["resume"] = self.resume.to_dict()
        return payload
