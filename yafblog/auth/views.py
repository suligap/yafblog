from flask import render_template, request, redirect, flash
from flask.ext.login import login_user, logout_user, login_required, login_url

from . import blueprint
from .models import User, LoginForm


DEFAULT_REDIRECT_TO = '/'


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    form_url = login_url('.login', request.args.get('next'))
    if request.method == 'POST' and form.validate():
        user = User.query.filter(User.username == form.username.data).first()
        if user is None or not user.authenticate(form.password.data):
            flash('Wrong username or password')
        elif not login_user(user):
            flash('Sorry, this account is inactive.')
        else:
            flash('Hi {0}!'.format(user.username))
            url = request.args.get('next') or DEFAULT_REDIRECT_TO
            return redirect(url)
    return render_template('auth/login.html', form=form, form_url=form_url)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.')
    return redirect(DEFAULT_REDIRECT_TO)
