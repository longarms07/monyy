from monyy import app
from .database import db, User
from .login import *
from flask import Flask, render_template, redirect
from flask_login import current_user, login_user


@app.route("/")
def hello():
    return "Hello "+current_user.get_username()+"!"


@app.route("/login", methods=['GET', 'POST'])
def login():
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
        return redirect("/")
    return render_template('login_test.html', title='Sign In', form=form)



