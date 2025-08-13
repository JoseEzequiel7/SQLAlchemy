from flask import Flask, render_template
from flask import request, session, redirect, url_for
from flask import flash
import os

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


from flask_login import LoginManager, UserMixin, logout_user
from flask_login import login_required, login_user, current_user

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

import sqlite3

login_manager = LoginManager()

app = Flask(__name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    base_dir, "instance", "banco.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "eh_molodoy"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager.__init__(app)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    senha = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.nome}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dash"))

    if request.method == "POST":
        nome = request.form["name"]
        senha = request.form["password"]

        user = User.query.filter_by(nome=nome).first()
        if user and check_password_hash(user.senha, senha):
            login_user(user, remember=True)
            flash("Login realizado com sucesso!", category="success")
            return redirect(url_for("dash"))

        flash("Dados incorretos", category="error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form["name"]
        senha = request.form["password"]

        if User.query.filter_by(nome=nome).first():
            flash("Nome de usuário já existe.", category="error")
            return redirect(url_for("register"))

        senha_hash = generate_password_hash(senha)
        novo_usuario = User(nome=nome, senha=senha_hash)

        db.session.add(novo_usuario)
        db.session.commit()
        flash(
            "Cadastro realizado com sucesso! Faça login para continuar.",
            category="success",
        )
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
@login_required
def dash():
    return render_template("dash.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
