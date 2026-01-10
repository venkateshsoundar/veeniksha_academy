from datetime import datetime
import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import case, func

from google_calendar import create_calendar_event
from models import Session, SessionStudent, Student, db


load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///veeniksha.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["GOOGLE_CREDENTIALS_FILE"] = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    app.config["GOOGLE_TOKEN_FILE"] = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    app.config["GOOGLE_CALENDAR_ID"] = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    app.config["DEFAULT_TIMEZONE"] = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")

    db.init_app(app)

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Database initialized.")

    @app.route("/")
    def index():
        return redirect(url_for("dashboard"))

    @app.route("/dashboard")
    def dashboard():
        now = datetime.utcnow()
        month_start = datetime(now.year, now.month, 1)
        total_sessions = Session.query.filter(Session.start_time >= month_start).count()
        sessions_by_student = (
            db.session.query(Student.full_name, func.count(SessionStudent.id))
            .join(SessionStudent)
            .join(Session)
            .filter(Session.start_time >= month_start, SessionStudent.removed_from_session.is_(False))
            .group_by(Student.full_name)
            .all()
        )
        attendance_stats = (
            db.session.query(
                Student.full_name,
                func.sum(case((SessionStudent.attendance_status == "attended", 1), else_=0)),
                func.count(SessionStudent.id),
            )
            .join(SessionStudent)
            .join(Session)
            .filter(Session.start_time >= month_start, SessionStudent.removed_from_session.is_(False))
            .group_by(Student.full_name)
            .all()
        )
        upcoming_sessions = (
            Session.query.filter(Session.start_time >= now)
            .order_by(Session.start_time.asc())
            .limit(5)
            .all()
        )
        return render_template(
            "dashboard.html",
            total_sessions=total_sessions,
            sessions_by_student=sessions_by_student,
            attendance_stats=attendance_stats,
            upcoming_sessions=upcoming_sessions,
        )

    @app.route("/students")
    def students_list():
        students = Student.query.order_by(Student.created_at.desc()).all()
        return render_template("students.html", students=students)

    @app.route("/students/new", methods=["GET", "POST"])
    def students_new():
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            if not full_name or not email:
                flash("Full name and email are required.", "error")
                return render_template("student_form.html", student=None)
            student = Student(
                full_name=full_name,
                email=email,
                phone=request.form.get("phone"),
                level=request.form.get("level"),
                timezone=request.form.get("timezone") or app.config["DEFAULT_TIMEZONE"],
                notes=request.form.get("notes"),
                active=True,
            )
            db.session.add(student)
            db.session.commit()
            flash("Student added.", "success")
            return redirect(url_for("students_list"))
        return render_template("student_form.html", student=None)

    @app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
    def students_edit(student_id):
        student = Student.query.get_or_404(student_id)
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip()
            if not full_name or not email:
                flash("Full name and email are required.", "error")
                return render_template("student_form.html", student=student)
            student.full_name = full_name
            student.email = email
            student.phone = request.form.get("phone")
            student.level = request.form.get("level")
            student.timezone = request.form.get("timezone")
            student.notes = request.form.get("notes")
            student.active = bool(request.form.get("active"))
            db.session.commit()
            flash("Student updated.", "success")
            return redirect(url_for("students_list"))
        return render_template("student_form.html", student=student)

    @app.route("/schedule", methods=["GET", "POST"])
    def schedule_session():
        students = Student.query.filter_by(active=True).order_by(Student.full_name.asc()).all()
        if request.method == "POST":
            start_time_str = request.form.get("start_time")
            duration_mins = int(request.form.get("duration_mins", "0"))
            topic = request.form.get("topic")
            selected_student_ids = request.form.getlist("student_ids")
            manual_meet_link = request.form.get("manual_meet_link")

            if not start_time_str or duration_mins <= 0:
                flash("Start time and duration are required.", "error")
                return render_template("schedule.html", students=students)

            if not selected_student_ids:
                flash("Select at least one student.", "error")
                return render_template("schedule.html", students=students)

            start_time = datetime.fromisoformat(start_time_str)
            over_capacity = len(selected_student_ids) > 2
            timezone = request.form.get("timezone") or app.config["DEFAULT_TIMEZONE"]

            meet_link = manual_meet_link
            calendar_event_id = None
            if not manual_meet_link:
                try:
                    meet_link, calendar_event_id = create_calendar_event(
                        summary=topic or "Veena Session",
                        start_time=start_time,
                        duration_mins=duration_mins,
                        timezone=timezone,
                        attendees=[student.email for student in students if str(student.id) in selected_student_ids],
                        credentials_file=app.config["GOOGLE_CREDENTIALS_FILE"],
                        token_file=app.config["GOOGLE_TOKEN_FILE"],
                        calendar_id=app.config["GOOGLE_CALENDAR_ID"],
                    )
                except RuntimeError as exc:
                    flash(f"Google Calendar setup missing: {exc}. Add a manual Meet link.", "warning")
                except Exception as exc:  # noqa: BLE001
                    flash(f"Google Calendar error: {exc}. Add a manual Meet link.", "warning")

            session_record = Session(
                start_time=start_time,
                duration_mins=duration_mins,
                topic=topic,
                meet_link=meet_link,
                calendar_event_id=calendar_event_id,
                status="scheduled",
                over_capacity=over_capacity,
            )
            db.session.add(session_record)
            db.session.flush()

            for student_id in selected_student_ids:
                db.session.add(
                    SessionStudent(
                        session_id=session_record.id,
                        student_id=int(student_id),
                        invite_status="invited",
                        attendance_status="pending",
                    )
                )

            db.session.commit()
            flash("Session scheduled.", "success")
            return redirect(url_for("sessions_list"))

        return render_template("schedule.html", students=students)

    @app.route("/sessions")
    def sessions_list():
        now = datetime.utcnow()
        upcoming = Session.query.filter(Session.start_time >= now).order_by(Session.start_time.asc()).all()
        past = Session.query.filter(Session.start_time < now).order_by(Session.start_time.desc()).all()
        return render_template("sessions.html", upcoming=upcoming, past=past)

    @app.route("/sessions/<int:session_id>", methods=["GET", "POST"])
    def sessions_detail(session_id):
        session_record = Session.query.get_or_404(session_id)
        if request.method == "POST":
            action = request.form.get("action")
            link_id = request.form.get("link_id")
            session_student = SessionStudent.query.get_or_404(link_id)

            if action == "update_status":
                session_student.invite_status = request.form.get("invite_status")
                session_student.attendance_status = request.form.get("attendance_status")
                db.session.commit()
                flash("Status updated.", "success")
            elif action == "remove_student":
                session_student.removed_from_session = True
                session_student.reason = request.form.get("reason") or "Denied"
                db.session.commit()
                flash("Student removed from session.", "success")
            return redirect(url_for("sessions_detail", session_id=session_id))

        session_students = (
            SessionStudent.query.filter_by(session_id=session_id)
            .join(Student)
            .order_by(Student.full_name.asc())
            .all()
        )
        return render_template("session_detail.html", session=session_record, session_students=session_students)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
