from datetime import datetime, timedelta
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import case, func
from sqlalchemy.orm import joinedload
import time
import os as _os

from google_calendar import create_calendar_event
from models import Session, SessionStudent, Student, db


if os.environ.get("RUN_SEED_ON_STARTUP") == "true":
    from seed import run_seed
    run_seed(app)


load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///veeniksha.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    # Admin credentials removed; no authentication required.
    app.config["GOOGLE_CREDENTIALS_FILE"] = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    app.config["GOOGLE_TOKEN_FILE"] = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
    app.config["GOOGLE_CALENDAR_ID"] = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    app.config["DEFAULT_TIMEZONE"] = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")
    # Optional: If set, this fixed Meet URL will be used for sessions when no manual link is provided.
    # Example: DEFAULT_MEET_LINK=https://meet.google.com/abc-defg-hij
    app.config["DEFAULT_MEET_LINK"] = os.getenv("DEFAULT_MEET_LINK", "")

    db.init_app(app)

    @app.context_processor
    def inject_static_version():
        # Provide a cache-busting version for static assets; uses STATIC_VERSION env var or app start timestamp
        return {"static_version": _os.getenv("STATIC_VERSION", str(int(time.time())))}

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Database initialized.")

    def login_required(view):
        # Authentication removed; allow all access.
        return view

    @app.route("/")
    def index():
        return redirect(url_for("dashboard"))

    # Login endpoint removed; no authentication required.

    # Logout endpoint removed.

    @app.route("/dashboard")
    @login_required
    def dashboard():
        now = datetime.utcnow()
        student_filter = request.args.get("student_id")
        year_filter = request.args.get("year")
        month_filter = request.args.get("month")

        def parse_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        student_id = parse_int(student_filter)
        year_value = parse_int(year_filter)
        month_value = parse_int(month_filter)

        if month_value and not year_value:
            year_value = now.year

        selected_year = year_value if year_value else now.year
        selected_month = month_value if month_value else now.month

        def month_range(year, month):
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
            return start, end

        month_start, month_end = month_range(selected_year, selected_month)
        year_start = datetime(selected_year, 1, 1)
        year_end = datetime(selected_year + 1, 1, 1)

        base_qs = Session.query
        if student_id:
            base_qs = base_qs.join(SessionStudent).filter(SessionStudent.student_id == student_id)

        total_sessions = base_qs.filter(Session.start_time >= month_start, Session.start_time < month_end).count()
        total_sessions_year = base_qs.filter(Session.start_time >= year_start, Session.start_time < year_end).count()

        # Added: total active students
        total_active_students = Student.query.filter_by(active=True).count()

        filter_start = None
        filter_end = None
        if year_value:
            if month_value:
                filter_start, filter_end = month_range(year_value, month_value)
            else:
                filter_start = datetime(year_value, 1, 1)
                filter_end = datetime(year_value + 1, 1, 1)
            total_sessions = base_qs.filter(Session.start_time >= filter_start, Session.start_time < filter_end).count()

        stats_start = filter_start or month_start
        stats_end = filter_end or month_end

        sessions_by_student_qs = (
            db.session.query(Student.full_name, func.count(SessionStudent.id))
            .join(SessionStudent)
            .join(Session)
            .filter(Session.start_time >= stats_start, Session.start_time < stats_end, SessionStudent.removed_from_session.is_(False))
        )
        if student_id:
            sessions_by_student_qs = sessions_by_student_qs.filter(SessionStudent.student_id == student_id)
        sessions_by_student = sessions_by_student_qs.group_by(Student.full_name).all()

        attendance_stats_qs = (
            db.session.query(
                Student.full_name,
                func.sum(case((SessionStudent.attendance_status == "attended", 1), else_=0)),
                func.count(SessionStudent.id),
            )
            .join(SessionStudent)
            .join(Session)
            .filter(Session.start_time >= stats_start, Session.start_time < stats_end, SessionStudent.removed_from_session.is_(False))
        )
        if student_id:
            attendance_stats_qs = attendance_stats_qs.filter(SessionStudent.student_id == student_id)
        attendance_stats = attendance_stats_qs.group_by(Student.full_name).all()

        # Today's sessions (midnight to midnight UTC)
        eager_students = joinedload(Session.students).joinedload(SessionStudent.student)
        today_start = datetime(now.year, now.month, now.day)
        tomorrow_start = today_start + timedelta(days=1)
        todays_qs = base_qs.options(eager_students).filter(Session.start_time >= today_start, Session.start_time < tomorrow_start)
        if filter_start:
            todays_qs = todays_qs.filter(Session.start_time >= filter_start)
        if filter_end:
            todays_qs = todays_qs.filter(Session.start_time < filter_end)
        todays_sessions = todays_qs.order_by(Session.start_time.asc()).all()

        upcoming_qs = base_qs.options(eager_students).filter(Session.start_time >= tomorrow_start)
        if filter_start:
            upcoming_qs = upcoming_qs.filter(Session.start_time >= filter_start)
        if filter_end:
            upcoming_qs = upcoming_qs.filter(Session.start_time < filter_end)
        upcoming_sessions = upcoming_qs.order_by(Session.start_time.asc()).limit(5).all()

        # Student list for filter dropdown
        students = Student.query.order_by(Student.full_name.asc()).all()

        filtered_sessions = None
        if student_id or year_value or month_value:
            filtered_qs = base_qs
            if filter_start:
                filtered_qs = filtered_qs.filter(Session.start_time >= filter_start)
            if filter_end:
                filtered_qs = filtered_qs.filter(Session.start_time < filter_end)
            filtered_sessions = filtered_qs.order_by(Session.start_time.asc()).all()

        years_raw = (
            db.session.query(func.strftime("%Y", Session.start_time))
            .distinct()
            .order_by(func.strftime("%Y", Session.start_time).desc())
            .all()
        )
        years = [int(y) for (y,) in years_raw if y]
        if not years:
            years = [now.year]

        month_options = [
            (1, "January"),
            (2, "February"),
            (3, "March"),
            (4, "April"),
            (5, "May"),
            (6, "June"),
            (7, "July"),
            (8, "August"),
            (9, "September"),
            (10, "October"),
            (11, "November"),
            (12, "December"),
        ]

        return render_template(
            "dashboard.html",
            total_sessions=total_sessions,
            total_sessions_year=total_sessions_year,
            total_active_students=total_active_students,
            sessions_by_student=sessions_by_student,
            attendance_stats=attendance_stats,
            upcoming_sessions=upcoming_sessions,
            todays_sessions=todays_sessions,
            students=students,
            filtered_sessions=filtered_sessions,
            years=years,
            month_options=month_options,
        )

    @app.route("/students")
    @login_required
    def students_list():
        students = Student.query.order_by(Student.created_at.desc()).all()
        return render_template("students.html", students=students)

    @app.route("/students/new", methods=["GET", "POST"])
    @login_required
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
    @login_required
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
    @login_required
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

            # Determine meet link: manual link takes precedence, then DEFAULT_MEET_LINK, otherwise create via Google Calendar
            fixed_meet = app.config.get("DEFAULT_MEET_LINK") or ""
            attendees_emails = [student.email for student in students if str(student.id) in selected_student_ids]

            meet_link = manual_meet_link or (fixed_meet or None)
            calendar_event_id = None
            # If no manual or fixed link provided, create event and conference via Google Calendar
            if not (manual_meet_link or fixed_meet):
                try:
                    meet_link, calendar_event_id = create_calendar_event(
                        summary=topic or "Veeniksha Session",
                        start_time=start_time,
                        duration_mins=duration_mins,
                        timezone=timezone,
                        attendees=attendees_emails,
                        credentials_file=app.config["GOOGLE_CREDENTIALS_FILE"],
                        token_file=app.config["GOOGLE_TOKEN_FILE"],
                        calendar_id=app.config["GOOGLE_CALENDAR_ID"],
                    )
                except RuntimeError as exc:
                    flash(f"Google Calendar setup missing: {exc}. Add a manual Meet link or set DEFAULT_MEET_LINK.", "warning")
                except Exception as exc:  # noqa: BLE001
                    flash(f"Google Calendar error: {exc}. Add a manual Meet link or set DEFAULT_MEET_LINK.", "warning")

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
    @login_required
    def sessions_list():
        now = datetime.utcnow()
        student_filter = request.args.get("student_id")
        year_filter = request.args.get("year")
        month_filter = request.args.get("month")
        day_filter = request.args.get("day")

        def parse_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        student_id = parse_int(student_filter)
        year_value = parse_int(year_filter)
        month_value = parse_int(month_filter)
        day_value = parse_int(day_filter)

        eager_students = joinedload(Session.students).joinedload(SessionStudent.student)
        upcoming_qs = Session.query.options(eager_students).filter(Session.start_time >= now)
        past_qs = Session.query.options(eager_students).filter(Session.start_time < now)
        if student_id:
            past_qs = (
                past_qs.join(SessionStudent)
                .filter(
                    SessionStudent.student_id == student_id,
                    SessionStudent.removed_from_session.is_(False),
                )
                .distinct()
            )

        past_start = now - timedelta(days=1)
        if year_value:
            if month_value and day_value:
                past_start = datetime(year_value, month_value, day_value)
            elif month_value:
                past_start = datetime(year_value, month_value, 1)
            else:
                past_start = datetime(year_value, 1, 1)

        past_qs = past_qs.filter(Session.start_time >= past_start)

        upcoming = upcoming_qs.order_by(Session.start_time.asc()).all()
        past = past_qs.order_by(Session.start_time.desc()).all()

        students = Student.query.order_by(Student.full_name.asc()).all()
        years_raw = (
            db.session.query(func.strftime("%Y", Session.start_time))
            .distinct()
            .order_by(func.strftime("%Y", Session.start_time).desc())
            .all()
        )
        years = [int(y) for (y,) in years_raw if y]
        if not years:
            years = [now.year]

        month_options = [
            (1, "January"),
            (2, "February"),
            (3, "March"),
            (4, "April"),
            (5, "May"),
            (6, "June"),
            (7, "July"),
            (8, "August"),
            (9, "September"),
            (10, "October"),
            (11, "November"),
            (12, "December"),
        ]

        return render_template(
            "sessions.html",
            upcoming=upcoming,
            past=past,
            students=students,
            years=years,
            month_options=month_options,
        )

    @app.route("/sessions/<int:session_id>", methods=["GET", "POST"])
    @login_required
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
