from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import validators, Form, TextField, PasswordField
from flask.ext.login import UserMixin

from . import db

MAX_USERNAME_LENGTH = 70


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(MAX_USERNAME_LENGTH),
        unique=True,
        nullable=False,
    )
    email = db.Column(db.String(170), unique=True, nullable=False)
    # 66 is length of pbkdf hash used here
    password = db.Column(db.String(66), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, value):
        # pbkdf2:sha1 hash with salt_length 8
        self.password = generate_password_hash(value)

    def authenticate(self, password):
        return check_password_hash(self.password, password)


class LoginForm(Form):
    username = TextField(
        'Username',
        [validators.Length(min=3, max=MAX_USERNAME_LENGTH)],
    )
    password = PasswordField('Password', [validators.Required()])
