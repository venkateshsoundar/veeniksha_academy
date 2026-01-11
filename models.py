from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    level = db.Column(db.String(50))
    timezone = db.Column(db.String(100))
    notes = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session_links = db.relationship("SessionStudent", back_populates="student")


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    duration_mins = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String(255))
    meet_link = db.Column(db.String(500))
    calendar_event_id = db.Column(db.String(255))
    status = db.Column(db.String(50), default="scheduled")
    over_capacity = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    students = db.relationship("SessionStudent", back_populates="session", cascade="all, delete-orphan")


class SessionStudent(db.Model):
    __tablename__ = "session_students"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    invite_status = db.Column(db.String(50), default="invited")
    attendance_status = db.Column(db.String(50), default="pending")
    removed_from_session = db.Column(db.Boolean, default=False)
    reason = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = db.relationship("Session", back_populates="students")
    student = db.relationship("Student", back_populates="session_links")

    __table_args__ = (
        db.UniqueConstraint("session_id", "student_id", name="unique_session_student"),
    )


class GoogleToken(db.Model):
    __tablename__ = "google_tokens"
    id = db.Column(db.Integer, primary_key=True)  # we will use id=1
    token_json = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
