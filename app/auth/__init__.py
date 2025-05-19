from flask import Blueprint, flash, redirect, url_for
from flask_login import current_user
from functools import wraps

bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_manage_users():
            flash('您没有权限访问此页面。', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

from app.auth import routes  # 将routes的导入移到最后
from app.auth import routes