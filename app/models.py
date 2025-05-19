# 导入所需的模块
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can_manage_users(self):
        return self.is_admin

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# 合同模型
class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    # 基本信息
    contract_id = db.Column(db.String(64), unique=True, index=True)  # 合同编号
    subject = db.Column(db.String(256), nullable=False)  # 合同主题
    summary = db.Column(db.Text)  # 合同摘要
    download_link = db.Column(db.String(512))  # 下载链接
    
    # 分类信息
    division_code = db.Column(db.String(8), nullable=False)  # 部门代码
    category_code = db.Column(db.String(8), nullable=False)  # 类别代码
    type_code = db.Column(db.String(8), nullable=False)  # 类型代码
    
    # 日期信息
    signing_date = db.Column(db.Date, nullable=False)  # 签署日期
    valid_from = db.Column(db.Date, nullable=False)  # 生效日期
    valid_to = db.Column(db.Date)  # 失效日期（可选）
    
    # 系统信息
    creator = db.Column(db.String(64), db.ForeignKey('users.username'))  # 创建者
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    def __repr__(self):
        return f'<Contract {self.contract_id}>'


# 删除这些类
# class DivisionCode(db.Model):
#     __tablename__ = 'division_codes'
#     code = db.Column(db.String(8), primary_key=True)
#     name = db.Column(db.String(64))

# class CategoryCode(db.Model):
#     __tablename__ = 'category_codes'
#     code = db.Column(db.String(8), primary_key=True)
#     name = db.Column(db.String(64))

# class TypeCode(db.Model):
#     __tablename__ = 'type_codes'
#     code = db.Column(db.String(8), primary_key=True)
#     name = db.Column(db.String(64))
#     division_code = db.Column(db.String(8), db.ForeignKey('division_codes.code'))