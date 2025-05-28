from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from . import bp, admin_required
from ..models import User, db
from ..forms import LoginForm, UserForm
from .. import bootstrap
from ..babel import _
from . import bp

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('invalid_username_or_password'), 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form, bootstrap=bootstrap, datetime=datetime)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('auth/user_list.html', users=users, datetime=datetime)

@bp.route('/users/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    form = UserForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash(_('username_exists'), 'danger')
            return render_template('auth/user_form.html', form=form, title=_('new_user'), datetime=datetime)
        
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        user.is_admin = form.is_admin.data
        db.session.add(user)
        db.session.commit()
        flash(_('user_created_successfully'), 'success')
        return redirect(url_for('auth.user_list'))
    return render_template('auth/user_form.html', form=form, title=_('new_user'), datetime=datetime)

@bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            user.set_password(form.password.data)
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash(_('user_updated_successfully'), 'success')
        return redirect(url_for('auth.user_list'))
    return render_template('auth/user_form.html', title=_('edit_user'), form=form, datetime=datetime)

@bp.route('/users/<int:id>/delete')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.username == 'admin':
        flash(_('cannot_delete_admin'), 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(_('user_deleted_successfully'), 'success')
    return redirect(url_for('auth.user_list'))


@bp.route('/set_language/<lang>')
def set_language(lang):
    if lang in ['en', 'zh']:
        session['language'] = lang
    return redirect(request.referrer or url_for('auth.user_list'))