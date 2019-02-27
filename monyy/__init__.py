from flask import Flask
from flask_login import LoginManager
from flask import Flask
from flask_login import UserMixin 
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, func
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection

app = Flask("monyy")
app.secret_key = b'\x0c\x18r\xd1E$\\\xa4\x1dQwN\x8bI\xbb\x11'
login_manager = LoginManager()
login_manager.init_app(app)



app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///monyy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()



from . import main