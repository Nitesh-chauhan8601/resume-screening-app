from backend.extensions import db
from backend.utils.validators import split_multi_value


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    candidate_name = db.Column(db.String(150))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    skills = db.Column(db.Text)
    education = db.Column(db.Text)
    experience_text = db.Column(db.Text)
    experience_years = db.Column(db.Numeric(4, 1), nullable=False, default=0.0)
    certifications = db.Column(db.Text)
    raw_text = db.Column(db.Text)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    parse_status = db.Column(db.String(20), nullable=False, default="pending")
    uploaded_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    recruiter = db.relationship("User", back_populates="resumes")
    results = db.relationship(
        "ScreeningResult",
        back_populates="resume",
        cascade="all, delete-orphan",
    )

    @property
    def skill_list(self) -> list[str]:
        return split_multi_value(self.skills)

    @property
    def certification_list(self) -> list[str]:
        return split_multi_value(self.certifications)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recruiter_id": self.recruiter_id,
            "candidate_name": self.candidate_name,
            "email": self.email,
            "phone": self.phone,
            "skills": self.skill_list,
            "education": self.education or "",
            "experience_text": self.experience_text or "",
            "experience_years": float(self.experience_years or 0),
            "certifications": self.certification_list,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "parse_status": self.parse_status,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
