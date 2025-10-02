from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from .db import db_session
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="")

login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return db_session.get(User, int(user_id))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = db_session.query(User).filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("main.index"))
        flash("Credenciais inválidas", "error")
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not email or not password:
            flash("Preencha e-mail e senha.", "error")
            return render_template("register.html")
        if db_session.query(User).filter_by(email=email).first():
            flash("E-mail já registrado.", "error")
            return render_template("register.html")
        user = User(email=email)
        user.set_password(password)
        db_session.add(user)
        db_session.commit()
        flash("Conta criada! Faça login.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("main.index"))
