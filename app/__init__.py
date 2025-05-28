from flask import Flask, session, request, current_app # Ensure session, request, current_app are imported (确保导入 session, request, current_app)
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5
from flask_babel import Babel, Locale
from config import Config
import pandas as pd
from datetime import datetime
import os # Import os (导入 os)
import json # Import json (导入 json)

# 初始化Flask扩展
db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap5()
babel = Babel() # This is the global Babel instance (这是全局的 Babel 实例)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure Flask-Babel (配置 Flask-Babel)
    # Pass the locale_selector directly to init_app
    # (直接将 locale_selector 传递给 init_app)
    babel.init_app(app, locale_selector=get_locale) # MODIFIED LINE (修改此行)
    
    # Ensure these are set correctly (确保这些设置正确)
    app.config['LANGUAGES'] = ['en', 'zh']
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.abspath('locales')

    # app.config['WTF_I18N_ENABLED'] = False # Consider removing or keeping commented out (考虑移除或保持注释状态)
    
    # 初始化扩展 (Initialize extensions)
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    # The line below was problematic (babel_ext) and redundant if using the decorator.
    # (下面这行代码 (babel_ext) 有问题，并且如果使用装饰器则是多余的。)
    # babel_ext.init_app(app, locale_selector=get_locale) # REMOVE THIS LINE (删除此行)
    
    # Removed custom translation initialization as we are trying to rely on Flask-Babel or a revised custom approach.
    # (移除了自定义翻译初始化，因为我们试图依赖Flask-Babel或修订后的自定义方法。)
    # from app.babel import init_translations
    # init_translations(app)

    # If Flask-Babel does not pick up JSON files directly with the above config,
    # we will need to implement a simple JSON loader and register the translations.
    # For example, by loading JSON into app.extensions['babel'].translations or similar,
    # or by re-introducing a lightweight version of the custom '_' function.
    # (如果Flask-Babel通过上述配置不能直接提取JSON文件，
    # 我们将需要实现一个简单的JSON加载器并注册翻译。
    # 例如，通过将JSON加载到app.extensions['babel'].translations或类似的地方，
    # 或者通过重新引入自定义“_”函数的轻量级版本。)

    # Example of how you might load JSON translations if Babel doesn't do it automatically:
    # This is a placeholder for a more robust solution if needed.
    # (如果Babel不能自动完成，以下是如何加载JSON翻译的示例：
    #  这是一个占位符，如果需要，可以提供更稳健的解决方案。)
    # This custom loading and translation function is key for your requirement of using JSON files directly.
    # (这个自定义加载和翻译函数是您直接使用JSON文件的要求的关键。)
    if not hasattr(app, 'translations_custom'): # Ensure it's loaded once (确保只加载一次)
        app.translations_custom = {}
        locales_dir = app.config['BABEL_TRANSLATION_DIRECTORIES'] 
        for lang_code in app.config['LANGUAGES']:
            file_path = os.path.join(locales_dir, f'{lang_code}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    app.translations_custom[lang_code] = json.load(f)
            else:
                app.translations_custom[lang_code] = {}
                print(f"Warning: Translation file not found: {file_path}") # 警告：未找到翻译文件

    # Make translations available in Jinja2 templates via a custom function if Babel's _() doesn't work with our JSONs
    # (如果Babel的_()不能与我们的JSON一起工作，则通过自定义函数使翻译在Jinja2模板中可用)
    # This is a fallback if Flask-Babel's default _ or gettext doesn't pick up the JSONs.
    # (如果Flask-Babel的默认 _ 或 gettext 无法识别JSON，这是一个后备方案。)
    def custom_translate(text, **kwargs):
        lang = get_locale()
        translation_map = app.translations_custom.get(lang, app.translations_custom.get(app.config['BABEL_DEFAULT_LOCALE'], {}))
        translated_text = translation_map.get(text, text)
        if kwargs:
            try:
                return translated_text.format(**kwargs)
            except (KeyError, ValueError):
                return translated_text
        return translated_text

    # 将custom_translate绑定到current_app
    app.custom_translate = custom_translate
    def custom_ngettext(singular, plural, n, **kwargs):
        if n == 1:
            return custom_translate(singular)
        else:
            return custom_translate(plural)

    # Override the default gettext and ngettext functions in Jinja environment
    # (在 Jinja 环境中覆盖默认的 gettext 和 ngettext 函数)
    app.jinja_env.globals['gettext'] = custom_translate
    app.jinja_env.globals['ngettext'] = custom_ngettext # Ensure custom_ngettext is defined (确保 custom_ngettext 已定义)
    app.jinja_env.globals['lazy_gettext'] = custom_translate # Crucial for WTForms (对 WTForms 至关重要)
    app.jinja_env.globals.update(_=custom_translate) # Common alias for gettext (gettext 的常用别名)
    app.jinja_env.globals.update(_l=custom_translate) # Ensure _l is also covered (确保 _l 也被覆盖)

    # REMOVE THE PREVIOUS ATTEMPT TO MODIFY babel.domain_instance or babel.gettext directly here
    # (在此处移除之前尝试直接修改 babel.domain_instance 或 babel.gettext 的代码)
    # The following block caused the RuntimeError and should be removed:
    # if hasattr(babel, 'domain_instance') and babel.domain_instance: 
    #     babel.domain_instance.gettext = custom_translate
    #     babel.domain_instance.ngettext = custom_ngettext
    # elif hasattr(babel, 'translation_service'): 
    #     if hasattr(babel.translation_service, 'gettext'): 
    #         babel.translation_service.gettext = custom_translate
    #     if hasattr(babel.translation_service, 'ngettext'): 
    #         babel.translation_service.ngettext = custom_ngettext
    # else: 
    #     babel.gettext = custom_translate
    #     babel.ngettext = custom_ngettext

    # 设置登录视图
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # 注册蓝图
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app

# REMOVE the decorator from here (从此移除装饰器)
def get_locale():
    # Example: get language from session or request args
    # Ensure this returns 'en' or 'zh' correctly
    user_lang = session.get('language', request.accept_languages.best_match(current_app.config['LANGUAGES']))
    return user_lang

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
def get_locale():
    # Example: get language from session or request args
    # Ensure this returns 'en' or 'zh' correctly
    user_lang = session.get('language', request.accept_languages.best_match(current_app.config['LANGUAGES']))
    return user_lang

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