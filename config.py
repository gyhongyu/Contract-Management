# 导入所需模块
import os
from datetime import timedelta

# 获取当前文件所在的目录路径
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'contract.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Excel文件配置
    EXCEL_FILE = os.path.join(basedir, 'Database.xlsx')
    CONTRACT_SHEET = 'Database'
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # 默认用户配置
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin'
    GUEST_USERNAME = os.environ.get('GUEST_USERNAME') or 'guest'
    GUEST_PASSWORD = os.environ.get('GUEST_PASSWORD') or 'guest'