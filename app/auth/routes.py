from datetime import datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import bp, admin_required
from ..models import User, db
from ..forms import LoginForm, UserForm  # 添加 UserForm 的导入
from .. import bootstrap  # 添加这行

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # 如果用户已登录，直接跳转到主页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
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
        # 检查用户名是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/user_form.html', form=form, title='New User', datetime=datetime)
        
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        user.is_admin = form.is_admin.data
        db.session.add(user)
        db.session.commit()
        flash('User created successfully.', 'success')
        return redirect(url_for('auth.user_list'))
    return render_template('auth/user_form.html', form=form, title='New User', datetime=datetime)

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
        flash('User updated successfully.', 'success')
        return redirect(url_for('auth.user_list'))
    return render_template('auth/user_form.html', form=form, title='Edit User', datetime=datetime)

@bp.route('/users/<int:id>/delete')
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.username == 'admin':
        flash('Cannot delete the main administrator account.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    return redirect(url_for('auth.user_list'))