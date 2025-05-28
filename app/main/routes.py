# 导入所需的模块
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from . import bp
from ..models import Contract
from .. import db, bootstrap
from ..forms import ContractForm  # 添加这行导入语句
from ..forms import ContractSearchForm
from flask import session, redirect, url_for
from ..babel import _ # 确保导入翻译函数

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    
    # 只显示默认的合同列表，按签署日期降序排序并分页
    pagination = Contract.query.order_by(Contract.signing_date.desc()).paginate(
        page=page, per_page=10, error_out=False)
    contracts = pagination.items
    
    # 添加搜索表单
    form = ContractSearchForm()
    
    return render_template('main/index.html',
                          form=form,  # 添加这行
                          contracts=contracts,
                          pagination=pagination,
                          datetime=datetime)

@bp.route('/contract/<contract_id>')
@login_required
def view_contract(contract_id):
    contract = Contract.query.filter_by(contract_id=contract_id).first_or_404()
    
    # 从Excel文件读取代码描述
    import pandas as pd
    excel_file = 'Database.xlsx'
    
    # 读取部门代码描述
    df_division = pd.read_excel(excel_file, sheet_name='Division Code')
    division_desc = df_division[df_division['Division Code'] == contract.division_code]['Description'].iloc[0]
    
    # 读取类别代码描述
    df_category = pd.read_excel(excel_file, sheet_name='Category Code')
    category_desc = df_category[df_category['Category Code'] == contract.category_code]['Description'].iloc[0]
    
    # 读取类型代码描述
    df_type = pd.read_excel(excel_file, sheet_name='Type Code')
    type_desc = df_type[df_type['Type Code'] == contract.type_code]['Description'].iloc[0]
    
    return render_template('main/contract_detail.html', 
                           contract=contract, 
                           datetime=datetime,
                           division_desc=division_desc,
                           category_desc=category_desc,
                           type_desc=type_desc)

@bp.route('/contract/<contract_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_contract(contract_id):
    # 检查用户权限
    if not current_user.is_admin:
        flash(_('only_admin_edit_contracts'), 'danger')
        return redirect(url_for('main.index'))
    
    contract = Contract.query.filter_by(contract_id=contract_id).first_or_404()
    form = ContractForm(obj=contract)
    
    # 在GET请求时正确设置表单字段
    if not form.is_submitted():  # 只在GET请求时设置
        # 设置no_expiry字段
        form.no_expiry.data = contract.valid_to is None
        if form.no_expiry.data:
            form.valid_to.data = None
        # 确保download_link正确加载
        form.downloadLink.data = contract.download_link
    
    if form.validate_on_submit():
        # 检查是否需要更新合同ID
        need_update_id = (
            form.division_code.data != contract.division_code or
            form.category_code.data != contract.category_code or
            form.type_code.data != contract.type_code or
            form.valid_from.data != contract.valid_from
        )
        
        if need_update_id:
            # 生成新的合同ID
            division_code = form.division_code.data
            category_code = form.category_code.data
            type_code = form.type_code.data
            valid_from_date = form.valid_from.data
            
            # 查找同一天的有效日期的同类型合同数量，用于生成版本号
            same_day_contracts = Contract.query.filter(
                Contract.division_code == division_code,
                Contract.category_code == category_code,
                Contract.type_code == type_code,
                db.func.date(Contract.valid_from) == valid_from_date,
                Contract.contract_id != contract_id  # 排除当前合同
            ).all()
            
            version = len(same_day_contracts) + 1
            new_contract_id = f"{division_code}-{category_code}-{type_code}-{valid_from_date.strftime('%Y%m%d')}-V{version}"
            contract.contract_id = new_contract_id
        
        # 更新其他合同信息
        form.populate_obj(contract)
        contract.updated_at = datetime.utcnow()
        db.session.commit()
        flash(_('contract_updated_successfully'), 'success')
        return redirect(url_for('main.view_contract', contract_id=contract.contract_id))
    
    return render_template('main/edit_contract.html', form=form, contract=contract, datetime=datetime)

@bp.route('/contract/<contract_id>/delete', methods=['POST'])
@login_required
def delete_contract(contract_id):
    # 检查用户权限
    if not current_user.is_admin:
        flash(_('only_admin_delete_contracts'), 'danger')
        return redirect(url_for('main.index'))
    
    contract = Contract.query.filter_by(contract_id=contract_id).first_or_404()
    db.session.delete(contract)
    db.session.commit()
    flash(_('contract_deleted_successfully'), 'success')
    return redirect(url_for('main.index'))


@bp.route('/contract/new', methods=['GET', 'POST'])
@login_required
def new_contract():
    form = ContractForm()
    
    # 如果是GET请求且session中有保存的表单数据，恢复数据
    if request.method == 'GET' and 'saved_form_data' in session:
        for field, value in session['saved_form_data'].items():
            if field in form._fields:
                if field == 'valid_from' or field == 'valid_to':
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        continue
                elif field == 'no_expiry':
                    value = value.lower() == 'true'
                setattr(form._fields[field], 'data', value)
        # 清除session中的表单数据
        session.pop('saved_form_data', None)
    
    if form.validate_on_submit():
        try:
            # 生成合同ID
            division_code = form.division_code.data
            category_code = form.category_code.data
            type_code = form.type_code.data
            valid_from_date = form.valid_from.data
            
            # 查找同一天的有效日期的同类型合同数量，用于生成版本号
            same_day_contracts = Contract.query.filter(
                Contract.division_code == division_code,
                Contract.category_code == category_code,
                Contract.type_code == type_code,
                db.func.date(Contract.valid_from) == valid_from_date
            ).all()
            
            version = len(same_day_contracts) + 1
            contract_id = f"{division_code}-{category_code}-{type_code}-{valid_from_date.strftime('%Y%m%d')}-V{version}"
            
            # 创建新合同
            contract = Contract(
                contract_id=contract_id,
                subject=form.subject.data,
                summary=form.summary.data,
                download_link=form.downloadLink.data,
                division_code=division_code,
                category_code=category_code,
                type_code=type_code,
                signing_date=datetime.now().date(),
                valid_from=valid_from_date,
                valid_to=None if form.no_expiry.data else form.valid_to.data,
                creator=current_user.username,
                created_at=datetime.now()
            )
            
            db.session.add(contract)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'success',
                    'redirect': url_for('main.view_contract', contract_id=contract.contract_id)
                })
            
            flash(_('contract_created_successfully'), 'success')
            return redirect(url_for('main.view_contract', contract_id=contract.contract_id))
            
        except Exception as e:
            db.session.rollback()
            # 添加详细的错误日志
            print(f'Error creating contract: {str(e)}')  # 开发环境查看 (Error creating contract: {error})
            print(f'Form data: {form.data}')  # 打印表单数据 (Print form data)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': _('error_creating_contract', error=str(e))  # 返回具体错误信息 (Return specific error message)
                }), 400
            
            flash(_('error_creating_contract', error=str(e)), 'danger')  # 显示具体错误 (Show specific error)
            # return render_template('main/new_contract.html', form=form, datetime=datetime) # Removed this line as it was causing the error
    
    return render_template('main/new_contract.html', form=form, datetime=datetime) # This line should be at this indentation level

@bp.route('/search')
@login_required
def search_contracts():
    form = ContractSearchForm()
    page = request.args.get('page', 1, type=int)
    
    # 构建查询
    query = Contract.query
    is_search = False
    
    if request.args.get('search'):
        is_search = True
        if request.args.get('contract_id'):
            query = query.filter(Contract.contract_id.ilike(f'%{request.args.get("contract_id")}%'))
        if request.args.get('subject'):
            query = query.filter(Contract.subject.ilike(f'%{request.args.get("subject")}%'))
        if request.args.get('summary'):
            query = query.filter(Contract.summary.ilike(f'%{request.args.get("summary")}%'))
        if request.args.get('division_code'):
            query = query.filter(Contract.division_code == request.args.get('division_code'))
        if request.args.get('category_code'):
            query = query.filter(Contract.category_code == request.args.get('category_code'))
        if request.args.get('type_code'):
            query = query.filter(Contract.type_code == request.args.get('type_code'))
        if request.args.get('date_from'):
            query = query.filter(Contract.valid_from >= datetime.strptime(request.args.get('date_from'), '%Y-%m-%d'))
        if request.args.get('date_to'):
            query = query.filter(Contract.valid_from <= datetime.strptime(request.args.get('date_to'), '%Y-%m-%d'))
    
    # 按签署日期降序排序并分页
    pagination = query.order_by(Contract.signing_date.desc()).paginate(
        page=page, per_page=10, error_out=False)
    contracts = pagination.items
    
    return render_template('main/search.html',
                          form=form,
                          contracts=contracts,
                          pagination=pagination,
                          is_search=is_search,
                          datetime=datetime)


@bp.route('/set_language/<lang>', methods=['GET', 'POST'])
def set_language(lang):
    session['language'] = lang
    # 移除表单数据保存的相关代码，只保留语言设置
    return_url = request.form.get('return_to') if request.method == 'POST' else \
                 request.args.get('return_to') or request.referrer or url_for('main.index')
    return redirect(return_url)