from flask import Blueprint

from .. import db  # NOQA


blueprint = Blueprint('blog', 'blog', template_folder='../templates')


from . import views  # NOQA
from . import models  # NOQA
