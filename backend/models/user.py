from werkzeug.security import check_password_hash, generate_password_hash

from backend.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    jobs = db.relationship(
        "JobDescription",
        back_populates="recruiter",
        cascade="all, delete-orphan",
    )
    resumes = db.relationship(
        "Resume",
        back_populates="recruiter",
        cascade="all, delete-orphan",
    )
    reports = db.relationship("Report", back_populates="user")
    created_tickets = db.relationship(
        "IssueTicket",
        foreign_keys="IssueTicket.created_by",
        back_populates="creator",
    )
    assigned_tickets = db.relationship(
        "IssueTicket",
        foreign_keys="IssueTicket.assigned_to",
        back_populates="assignee",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
