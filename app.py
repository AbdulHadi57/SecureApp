import os
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect, FlaskForm
from flask_wtf.csrf import generate_csrf
from wtforms import PasswordField, StringField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", "change-this-secret"),
    SQLALCHEMY_DATABASE_URI="sqlite:///firstapp.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_USE_HTTPS", "0") == "1",
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
    WTF_CSRF_TIME_LIMIT=3600,
)

USE_HTTPS = app.config["SESSION_COOKIE_SECURE"]

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)


@app.context_processor
def inject_csrf_token() -> dict:
    """Expose a callable for templates to fetch CSRF tokens."""

    return {"csrf_token": generate_csrf}


FORBIDDEN_SEQUENCES = ("--", ";", "/*", "*/")
SQL_KEYWORDS = ("SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "UNION")


class FirstApp(db.Model):
    __tablename__ = "first_app"
    sno = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fname = db.Column(db.String(100), nullable=False)
    lname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:  # pragma: no cover - convenience only
        return f"{self.sno} - {self.fname}"


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)


def reject_injection(_, field) -> None:
    value = (field.data or "").strip()
    if any(seq in value for seq in FORBIDDEN_SEQUENCES):
        raise ValidationError("Input contains characters that look like an injection attempt.")

    upper_value = value.upper()
    for keyword in SQL_KEYWORDS:
        if (
            upper_value == keyword
            or upper_value.startswith(f"{keyword} ")
            or upper_value.endswith(f" {keyword}")
            or f" {keyword} " in upper_value
        ):
            raise ValidationError("Input contains characters that look like an injection attempt.")


class ContactForm(FlaskForm):
    fname = StringField(
        "First name",
        validators=[
            DataRequired(message="First name is required."),
            Length(max=100),
            Regexp(r"^[A-Za-z' -]+$", message="Only letters, spaces, apostrophes, and hyphens allowed."),
            reject_injection,
        ],
    )
    lname = StringField(
        "Last name",
        validators=[
            DataRequired(message="Last name is required."),
            Length(max=100),
            Regexp(r"^[A-Za-z' -]+$", message="Only letters, spaces, apostrophes, and hyphens allowed."),
            reject_injection,
        ],
    )
    email = EmailField(
        "Email",
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Please provide a valid email."),
            Length(max=200),
            reject_injection,
        ],
    )
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=80),
            Regexp(
                r"^[A-Za-z0-9_.@-]+$",
                message="Usernames may contain letters, numbers, @, dashes, underscores, and dots.",
            ),
        ],
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    submit = SubmitField("Log in")


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapped


DEFAULT_ADMIN_USERNAME = os.environ.get("DEFAULT_ADMIN_USERNAME", "i221693@nu.edu.pk")
DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "123456@a")


def ensure_seed_admin() -> None:
    user = User.query.filter_by(username=DEFAULT_ADMIN_USERNAME).first()
    if user and user.check_password(DEFAULT_ADMIN_PASSWORD):
        return

    if not user:
        user = User(username=DEFAULT_ADMIN_USERNAME)
        user.set_password(DEFAULT_ADMIN_PASSWORD)
        db.session.add(user)
    else:
        user.set_password(DEFAULT_ADMIN_PASSWORD)

    db.session.commit()


@app.before_request
def bootstrap_seed_admin() -> None:
    if getattr(app, "_admin_seeded", False):
        return
    ensure_seed_admin()
    app._admin_seeded = True


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            session.clear()
            session["user_id"] = user.id
            session.permanent = True
            flash("Successfully logged in.", "success")
            next_location = request.args.get("next")
            return redirect(next_location or url_for("index"))

        flash("Invalid username or password.", "danger")

    elif request.method == "POST":
        flash("Please correct the highlighted errors.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = ContactForm()
    if form.validate_on_submit():
        new_record = FirstApp(
            fname=form.fname.data.strip(),
            lname=form.lname.data.strip(),
            email=form.email.data.strip(),
        )
        db.session.add(new_record)
        db.session.commit()
        flash("Record added successfully.", "success")
        return redirect(url_for("index"))

    elif request.method == "POST":
        flash("Please correct the highlighted errors.", "danger")

    students = FirstApp.query.order_by(FirstApp.sno.asc()).all()
    return render_template("index.html", form=form, students=students)


@app.route("/delete/<int:sno>", methods=["POST"])
@login_required
def delete(sno: int):
    rec = FirstApp.query.get_or_404(sno)
    db.session.delete(rec)
    db.session.commit()
    flash("Record deleted.", "info")
    return redirect(url_for("index"))


@app.route("/update/<int:sno>", methods=["GET", "POST"])
@login_required
def update(sno: int):
    rec = FirstApp.query.get_or_404(sno)
    form = ContactForm(obj=rec)
    if form.validate_on_submit():
        rec.fname = form.fname.data.strip()
        rec.lname = form.lname.data.strip()
        rec.email = form.email.data.strip()
        db.session.commit()
        flash("Record updated successfully.", "success")
        return redirect(url_for("index"))

    elif request.method == "POST":
        flash("Please correct the highlighted errors.", "danger")

    return render_template("update.html", student=rec, form=form)


@app.errorhandler(404)
def handle_not_found(_error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def handle_server_error(error):
    db.session.rollback()
    app.logger.error("Unhandled error: %s", error)
    return render_template("500.html"), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_seed_admin()
    run_kwargs = {"ssl_context": "adhoc"} if USE_HTTPS else {}
    app.run(**run_kwargs)
