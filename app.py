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

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'eh_molodoy'

db = SQLAlchemy(app)
migrate = Migrate(app , db)

login_manager.__init__(app)

app.secret_key = 'chave_secreta'

class User(db.model):
    ___tablename___ = 'users'
    id = db.Column(db.Integer , primary_key =True)
    nome = db.Column(db.String(100) , nullable =False)
    senha = db.column(db.String(100) , nullable =False)

def obter_conexao():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

class User(UserMixin):
    def __init__(self, nome, senha) -> None:
        self.nome = nome
        self.senha = senha

    @classmethod
    def get(cls, user_id):
        conexao = obter_conexao()        
        sql = "select * from users where nome = ?"
        resultado = conexao.execute(sql, (user_id,)).fetchone()
        user = User(nome=resultado['nome'], senha=resultado['senha'])
        user.id = resultado['nome']
        return user

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        nome = request.form['name']
        senha= request.form['password']

        conexao = obter_conexao()        
        sql = "select * from users where nome = ?"
        resultado = conexao.execute(sql, (nome,)).fetchone()
        conexao.close()
        
        if resultado and check_password_hash(resultado['senha'], senha):
            user = User(nome=resultado['nome'], senha=resultado['senha'])
            user.id = resultado['nome']
            login_user(user)
            flash('Login realizado com sucesso!', category='success')
            return redirect(url_for('dash'))

        flash('Dados incorretos', category='error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['name']
        senha = request.form['password']
    
        conexao = obter_conexao()        
        sql = "select * from users where nome = ?"
        resultado = conexao.execute(sql, (nome,)).fetchone()

        if not resultado:
            senha_hash = generate_password_hash(senha)
            sql = "INSERT INTO users(nome, senha) VALUES(?,?)"
            conexao.execute(sql, (nome, senha_hash))
            conexao.commit()
            conexao.close()

            flash('Cadastro realizado com sucesso! Faça login para continuar.', category='success')
            return redirect(url_for('login'))

        conexao.close()
        
        flash('Problema no cadastro, o nome de usuário já existe.', category='error')
        return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/dashboard')
@login_required
def dash():
    return render_template('dash.html')

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))