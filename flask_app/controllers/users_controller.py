from flask_app import app
from flask import render_template,redirect,request,flash,session
from flask_app.models.user_model import User
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    if not User.validate_user(request.form):
        return redirect('/')
    user_id = User.save(request.form)
    session.clear()
    session['user_id'] = user_id
    return redirect("/dashboard")

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/logout')
    user = User.get_one(session['user_id'])
    return render_template("dashboard.html", user = user)

@app.route('/login', methods=['POST'])
def login():
    user = User.validate_login(request.form)
    if not user:
        return redirect('/')
    session['user_id'] = user.id
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')