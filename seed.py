from datetime import datetime, timedelta
from app import create_app
from models import Session, SessionStudent, Student, db

def run_seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if Student.query.count() == 0:
            students = [
                Student(full_name="Asha Rao", email="asha@example.com", level="Beginner", timezone="Asia/Kolkata"),
                Student(full_name="Meera Nair", email="meera@example.com", level="Intermediate", timezone="Asia/Kolkata"),
                Student(full_name="Priya Shah", email="priya@example.com", level="Advanced", timezone="America/New_York"),
            ]
            db.session.add_all(students)
            db.session.commit()

        if Session.query.count() == 0:
            now = datetime.utcnow()
            session = Session(
                start_time=now + timedelta(days=1),
                duration_mins=60,
                topic="Raga Basics",
                meet_link="https://meet.google.com/example",
                status="scheduled",
            )
            db.session.add(session)
            db.session.flush()
            for student in Student.query.limit(2).all():
                db.session.add(
                    SessionStudent(
                        session_id=session.id,
                        student_id=student.id,
                        invite_status="invited",
                        attendance_status="pending",
                    )
                )
            db.session.commit()

        print("Seed data created.")

if __name__ == "__main__":
    run_seed()
