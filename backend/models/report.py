from backend.extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    jd_id = db.Column(db.Integer, db.ForeignKey("job_descriptions.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    date_range = db.Column(db.String(50))
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    user = db.relationship("User", back_populates="reports")
    job_description = db.relationship("JobDescription", back_populates="reports")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "jd_id": self.jd_id,
            "type": self.type,
            "date_range": self.date_range,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
