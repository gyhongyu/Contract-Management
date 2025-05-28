from flask import Blueprint
from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for
from ..babel import _ # 确保导入翻译函数

bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.can_manage_users():
            flash(_('no_permission_access_page'), 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

# 将routes导入放在最后
from . import routes