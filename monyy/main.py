from monyy import app
from .database import db, User
from .login import *
from .db_accessor import *
from flask import Flask, render_template, redirect
from flask_login import current_user, login_user, login_required, logout_user


@app.route("/")
def hello():
    #BAATest()
    if current_user.is_authenticated:
        return "Hello "+current_user.get_username()+"!"
    else:
        return "Hello mlemlem!"


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = GetUser(form.username.data, form.password.data)
        except Exception as error:
            print(error)
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        return redirect("/index")
    return render_template('login.html', title='Sign In', form=form)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        try:
            RegisterUser(form.username.data, form.password.data)
            user = GetUser(form.username.data, form.password.data)
        except Exception as error:
            print(error)
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        return redirect("/index")
    return render_template('login.html', title='Register', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@app.route("/index")
@login_required
def index():
    return render_template('index.html')

