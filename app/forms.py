# 导入所需的模块
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, URL, ValidationError, Optional
from datetime import date
import pandas as pd

# 登录表单
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')

# 用户管理表单（仅管理员可用）
class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Username is required.')])
    password = PasswordField('Password', validators=[Optional()])
    password2 = PasswordField('Confirm Password', validators=[Optional()])
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Submit')

    def validate_password2(self, field):
        if self.password.data and field.data != self.password.data:
            raise ValidationError('Passwords do not match.')

# 合同表单
class ContractForm(FlaskForm):
    # 基本信息
    subject = StringField('Subject', validators=[DataRequired(), Length(1, 256)])
    summary = TextAreaField('Summary', validators=[DataRequired()])
    downloadLink = StringField('Download Link', validators=[
        DataRequired(),
        URL(),
        Length(1, 512)
    ])

    # 分类信息
    division_code = SelectField('Division Code', validators=[DataRequired()])
    category_code = SelectField('Category Code', validators=[DataRequired()])
    type_code = SelectField('Type Code', validators=[DataRequired()])

    # 日期信息
    valid_from = DateField('Valid From', validators=[DataRequired()])
    valid_to = DateField('Valid To', validators=[])
    no_expiry = BooleanField('No Expiry Date')
    
    # 预览合同ID
    preview_contract_id = StringField('Contract ID Preview', render_kw={'readonly': True})

    def __init__(self, *args, **kwargs):
        super(ContractForm, self).__init__(*args, **kwargs)
        # 从Excel文件读取选项
        import pandas as pd
        excel_file = 'Database.xlsx'
        
        # 读取部门代码
        df_division = pd.read_excel(excel_file, sheet_name='Division Code')
        self.division_code.choices = [
            ('', 'Select Division Code')
        ] + [
            (row['Division Code'], f"{row['Division Code']} - {row['Description']}") 
            for _, row in df_division.iterrows()
        ]
        
        # 读取类别代码
        df_category = pd.read_excel(excel_file, sheet_name='Category Code')
        self.category_code.choices = [
            ('', 'Select Category Code')
        ] + [
            (row['Category Code'], f"{row['Category Code']} - {row['Description']}") 
            for _, row in df_category.iterrows()
        ]
        
        # 读取类型代码 - 移除部门过滤
        df_type = pd.read_excel(excel_file, sheet_name='Type Code')
        self.type_code.choices = [
            ('', 'Select Type Code')
        ] + [
            (row['Type Code'], f"{row['Type Code']} - {row['Description']}") 
            for _, row in df_type.iterrows()
        ]

    # 移除类型代码的验证
    # def validate_type_code(self, field):
    #     import pandas as pd
    #     excel_file = 'Database.xlsx'
    #     df_type = pd.read_excel(excel_file, sheet_name='Type Code')
    #     
    #     # 检查选择的类型代码是否属于当前选择的部门
    #     valid_types = df_type[df_type['Division Code'] == self.division_code.data]['Type Code'].tolist()
    #     if field.data not in valid_types:
    #         raise ValidationError('Selected type code is not valid for the chosen division.')

    def validate_valid_to(self, field):
        if not self.no_expiry.data and field.data and field.data < self.valid_from.data:
            raise ValidationError('Valid to date cannot be earlier than valid from date.')

    def validate_downloadLink(self, field):
        if not field.data.startswith('https://drive.google.com/'):
            raise ValidationError('Please provide a valid Google Drive link.')

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
    contract_id = StringField('Contract ID')
    subject = StringField('Subject')
    summary = StringField('Summary')
    division_code = SelectField('Division Code', choices=[])
    category_code = SelectField('Category Code', choices=[])
    type_code = SelectField('Type Code', choices=[])
    date_from = DateField('Date From', format='%Y-%m-%d')
    date_to = DateField('Date To', format='%Y-%m-%d')
    
    def __init__(self, *args, **kwargs):
        super(ContractSearchForm, self).__init__(*args, **kwargs)
        # 从Excel文件读取选项
        df_division = pd.read_excel('Database.xlsx', sheet_name='Division Code')
        df_category = pd.read_excel('Database.xlsx', sheet_name='Category Code')
        df_type = pd.read_excel('Database.xlsx', sheet_name='Type Code')
        
        # 修改：只使用代码作为选项值，描述仅用于显示
        self.division_code.choices = [('', 'All')] + [
            (row['Division Code'], f"{row['Division Code']} - {row['Description']}") 
            for _, row in df_division.iterrows()
        ]
        self.category_code.choices = [('', 'All')] + [
            (row['Category Code'], f"{row['Category Code']} - {row['Description']}") 
            for _, row in df_category.iterrows()
        ]
        self.type_code.choices = [('', 'All')] + [
            (row['Type Code'], f"{row['Type Code']} - {row['Description']}") 
            for _, row in df_type.iterrows()
        ]