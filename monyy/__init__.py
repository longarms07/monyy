from flask import Flask
from flask_login import LoginManager

app = Flask("monyy")
app.secret_key = b'\x0c\x18r\xd1E$\\\xa4\x1dQwN\x8bI\xbb\x11'
login_manager = LoginManager()
login_manager.init_app(app)



from . import main