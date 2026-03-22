from backend.extensions import db
from backend.utils.validators import split_multi_value


class JobDescription(db.Model):
    __tablename__ = "job_descriptions"

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description_text = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text)
    keywords = db.Column(db.Text)
    min_experience = db.Column(db.Integer, nullable=False, default=0)
    qualifications = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    recruiter = db.relationship("User", back_populates="jobs")
    results = db.relationship(
        "ScreeningResult",
        back_populates="job_description",
        cascade="all, delete-orphan",
    )
    reports = db.relationship("Report", back_populates="job_description")

    @property
    def required_skill_list(self) -> list[str]:
        return split_multi_value(self.required_skills)

    @property
    def keyword_list(self) -> list[str]:
        return split_multi_value(self.keywords)

    @property
    def qualification_list(self) -> list[str]:
        return split_multi_value(self.qualifications)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recruiter_id": self.recruiter_id,
            "title": self.title,
            "description_text": self.description_text,
            "required_skills": self.required_skill_list,
            "keywords": self.keyword_list,
            "min_experience": self.min_experience,
            "qualifications": self.qualification_list,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
