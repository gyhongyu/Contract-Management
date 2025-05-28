# 导入所需的模块
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, URL, ValidationError, Optional
from datetime import date
import pandas as pd
from flask_babel import gettext as _

# 登录表单
class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me')

# 用户管理表单（仅管理员可用）
class UserForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(message='username_required')])
    password = PasswordField('password', validators=[Optional()])
    password2 = PasswordField('confirm_password', validators=[Optional()])
    is_admin = BooleanField('administrator')
    submit = SubmitField('submit')

    def validate_password2(self, field):
        if self.password.data and field.data != self.password.data:
            raise ValidationError('passwords_not_match')

# 合同表单
class ContractForm(FlaskForm):
    subject = StringField('subject', validators=[DataRequired(message=_('field_required')), Length(1, 256, message=_('maximum_256_characters'))])
    summary = TextAreaField('summary', validators=[DataRequired(message=_('field_required'))])
    downloadLink = StringField('contract_link', validators=[
        DataRequired(message=_('field_required')),
        URL(message=_('invalid_url')),
        Length(max=512, message=_('provide_url_max_512'))
    ])
    division_code = SelectField('division_code', validators=[DataRequired(message=_('field_required'))])
    category_code = SelectField('category_code', validators=[DataRequired(message=_('field_required'))])
    type_code = SelectField('type_code', validators=[DataRequired(message=_('field_required'))])
    valid_from = DateField('valid_from', validators=[DataRequired(message=_('field_required'))])
    valid_to = DateField('valid_to', validators=[])
    no_expiry = BooleanField('no_expiry_date')
    preview_contract_id = StringField('contract_id_preview', render_kw={'readonly': True})
    submit = SubmitField('create_contract_button')

    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)
        excel_file = 'Database.xlsx'
        df_division = pd.read_excel(excel_file, sheet_name='Division Code')
        self.division_code.choices = [('', _('select_division_code'))] + [
            (row['Division Code'], f"{row['Division Code']} - {row['Description']}") 
            for _, row in df_division.iterrows()
        ]
        df_category = pd.read_excel(excel_file, sheet_name='Category Code')
        self.category_code.choices = [('', _('select_category_code'))] + [
            (row['Category Code'], f"{row['Category Code']} - {row['Description']}") 
            for _, row in df_category.iterrows()
        ]
        df_type = pd.read_excel(excel_file, sheet_name='Type Code')
        self.type_code.choices = [('', _('select_type_code'))] + [
            (row['Type Code'], f"{row['Type Code']} - {row['Description']}") 
            for _, row in df_type.iterrows()
        ]

    def validate_valid_to(self, field):
        if not self.no_expiry.data and field.data and field.data < self.valid_from.data:
            raise ValidationError(_('valid_to_earlier_than_valid_from'))

    # 移除 validate_downloadLink 方法，不再限制必须是 Google Drive 链接

# 合同ID生成函数
def generate_contract_id(division_code, category_code, type_code, signing_date, contracts):
    """
    生成合同ID
    :param division_code: 部门代码
    :param category_code: 类别代码
    :param type_code: 类型代码
    :param signing_date: 签署日期
    :param contracts: 当天已有的同类型合同列表
    :return: 新的合同ID
    """
    date_str = signing_date.strftime('%Y%m%d')
    base_id = f'{division_code}-{category_code}-{type_code}-{date_str}'
    
    # 查找当天最大版本号
    max_version = 0
    for contract in contracts:
        if contract.contract_id.startswith(base_id):
            version = int(contract.contract_id.split('-V')[-1])
            max_version = max(max_version, version)
    
    # 生成新版本号
    new_version = max_version + 1
    return f'{base_id}-V{new_version}'


class ContractSearchForm(FlaskForm):
    contract_id = StringField('contract_id')
    subject = StringField('subject')
    summary = TextAreaField('summary')
    division_code = SelectField('division_code', choices=[])
    category_code = SelectField('category_code', choices=[])
    type_code = SelectField('type_code', choices=[])
    date_from = DateField('date_from', format='%Y-%m-%d')
    date_to = DateField('date_to', format='%Y-%m-%d')
    def __init__(self, *args, **kwargs):
        super(ContractSearchForm, self).__init__(*args, **kwargs)
        df_division = pd.read_excel('Database.xlsx', sheet_name='Division Code')
        df_category = pd.read_excel('Database.xlsx', sheet_name='Category Code')
        df_type = pd.read_excel('Database.xlsx', sheet_name='Type Code')
        self.division_code.choices = [('', 'all')] + [
            (row['Division Code'], f"{row['Division Code']} - {row['Description']}") 
            for _, row in df_division.iterrows()
        ]
        self.category_code.choices = [('', 'all')] + [
            (row['Category Code'], f"{row['Category Code']} - {row['Description']}") 
            for _, row in df_category.iterrows()
        ]
        self.type_code.choices = [('', 'all')] + [
            (row['Type Code'], f"{row['Type Code']} - {row['Description']}") 
            for _, row in df_type.iterrows()
        ]