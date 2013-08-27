from flask import Blueprint

from .. import db  # NOQA


blueprint = Blueprint('auth', 'auth', template_folder='../templates')


from . import views  # NOQA
from . import models  # NOQA
