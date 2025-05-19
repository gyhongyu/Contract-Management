# 导入所需的模块
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from config import Config
import pandas as pd
from datetime import datetime

# 初始化Flask扩展
db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap5()

def create_app(config_class=Config):
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_class)
    
    # 设置 WTForms 为英文
    app.config['WTF_I18N_ENABLED'] = False
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    
    # 设置登录视图
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # 确保数据库表存在
    with app.app_context():
        db.create_all()
        
        # 初始化默认用户
        from app.models import User
        if not User.query.filter_by(username=app.config['ADMIN_USERNAME']).first():
            admin = User(username=app.config['ADMIN_USERNAME'],
                        is_admin=True)
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            
            guest = User(username=app.config['GUEST_USERNAME'],
                        is_admin=False)
            guest.set_password(app.config['GUEST_PASSWORD'])
            db.session.add(guest)
            
            db.session.commit()
    
    # 注册CLI命令
    @app.cli.command('create-admin')
    def create_admin():
        """创建管理员账户"""
        from app.models import User
        admin = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
        if admin is None:
            admin = User(username=app.config['ADMIN_USERNAME'], is_admin=True)
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            print('管理员账户创建成功。')
        else:
            print('管理员账户已存在。')
    
    return app

def init_database_from_excel(app):
    with app.app_context():
        from app.models import DivisionCode, CategoryCode, TypeCode
        
        try:
            # 读取Excel文件中的代码表
            division_df = pd.read_excel('Database.xlsx', sheet_name='Division Code')
            category_df = pd.read_excel('Database.xlsx', sheet_name='Category Code')
            type_df = pd.read_excel('Database.xlsx', sheet_name='Type Code')
            
            # 导入部门代码
            for _, row in division_df.iterrows():
                if pd.notna(row['Division Code']):
                    code = DivisionCode(code=str(row['Division Code']), 
                                       name=str(row['Description']))
                    db.session.add(code)
            
            # 导入类别代码
            for _, row in category_df.iterrows():
                if pd.notna(row['Category Code']):
                    code = CategoryCode(code=str(row['Category Code']), 
                                       name=str(row['Description']))
                    db.session.add(code)
            
            # 导入类型代码
            for _, row in type_df.iterrows():
                if pd.notna(row['Type Code']):
                    code = TypeCode(
                        code=str(row['Type Code']),
                        name=str(row['Description']),
                        division_code=str(row['Division Code'])
                    )
                    db.session.add(code)
            
            db.session.commit()
            print('成功导入代码表数据')
            
        except Exception as e:
            print(f'导入Excel数据时出错: {str(e)}')
            import traceback
            print('错误详情：', traceback.format_exc())
            db.session.rollback()