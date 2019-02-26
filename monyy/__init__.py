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

#db.drop_all()
#db.create_all()
#db.session.query(Account).delete()
#db.session.query(User).delete()
#db.session.query(Transaction).delete()
#db.session.query(Bank_account).delete()
#db.session.query(Transaction_bank_account).delete()
#db.session.query(Bond).delete()
#db.session.query(Transaction_bond).delete()
#db.session.query(Stock).delete()
#db.session.query(Stock_value).delete()
#db.session.query(Transaction_stock).delete()
#db.session.query(Debt).delete()
#db.session.query(Transaction_debt).delete()
#db.session.query(Real_estate).delete()
#db.session.query(Transaction_real_estate).delete()
#db.session.query(Transaction_tag).delete()
#db.session.query(Tag).delete()
#db.session.query(Account_tag).delete()
#db.session.commit()

from . import main