from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/yafblog-db'

app.debug = True  # TODO
app.secret_key = 'secret-key-debug'  # TODO


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
