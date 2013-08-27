import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager


app = Flask(__name__)

try:
    # retarded env detection
    _db_uri = os.environ['DATABASE_URL']
    app.secret_key = os.environ['SECRET_KEY']
    app.debug = False
except KeyError:
    _db_uri = 'postgresql://localhost/yafblog-db'
    app.debug = True
    app.secret_key = 'secret-key-debug'

app.config['SQLALCHEMY_DATABASE_URI'] = _db_uri


db = SQLAlchemy(app)


from . import blog
from . import auth

app.register_blueprint(blog.blueprint)
app.register_blueprint(auth.blueprint, url_prefix='/auth')


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(userid):
    return auth.models.User.query.get(userid)
