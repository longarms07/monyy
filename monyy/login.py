from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from .database import User
from monyy import db, login_manager


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


#Register new user
def RegisterUser(username, password):
    #Check to see if username is in database
    temp_user = User.query.filter_by(user_name=username).first()
    #if it is, raise "Already Registered" exception and tell user to pick another username or log in
    if not temp_user is None:
        raise Exception('Username is already in use, please choose another.')
    #If it isn't, we are good to go.
    #Next, generate the password hash.
    passhash=HashPassword(password)
    #Generate the new user and store it in the User database table.
    new_user = User(user_name=username, pass_hash=passhash)
    db.session.add(new_user)
    db.session.commit()
    #Pull the user from the database, to ensure it was added properly, and return it
    temp_user = User.query.filter_by(user_name=username).first()
    if(temp_user is None):
        raise Exception('Problem adding user to database!')
    return temp_user


#Get user from database
def GetUser(username, password):
    #Check to see if username is in database
    temp_user = User.query.filter_by(user_name=username).first()
    #If not, raise "Invalid Username" exception.
    if temp_user is None:
        raise Exception('User not in database, please register a new user.')
    #Next, check that the password is correct matches the stored password hash.
    if not CheckPassword(temp_user.pass_hash, password):
    #If not, raise "Invalid password" exception.
        raise Exception('Incorrect password!')
    #If so, return the current user. 
    return temp_user


#hash password
def HashPassword(password):
    return generate_password_hash(password)

#check password
def CheckPassword(passhash, password):
    return check_password_hash(passhash, password)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')