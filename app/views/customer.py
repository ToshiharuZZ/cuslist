"""
顧客管理関連のビュー（ルート）
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.views.auth import login_required
from app.services.customer_service import CustomerService
from app.services.billing_service import BillingService, PlanLimits
from app.services.analysis_service import AnalysisService

customer_bp = Blueprint('customer', __name__, url_prefix='/customers')
customer_service = CustomerService()
billing_service = BillingService()
analysis_service = AnalysisService()


@customer_bp.route('/')
@login_required
def customer_list():
    """顧客一覧"""
    customers = customer_service.get_all_customers()
    
    # プラン制限情報を取得
    plan = session.get('plan', 'basic')
    customer_limit = PlanLimits.get_customer_limit(plan)
    current_count = len(customers)
    
    return render_template(
        'customer/list.html',
        customers=customers,
        customer_limit=customer_limit,
        current_count=current_count
    )


@customer_bp.route('/search')
@login_required
def search():
    """顧客検索"""
    keyword = request.args.get('keyword', '').strip()
    user_id = session.get('user_id')
    plan = session.get('plan', 'basic')

    # 検索制限チェック
    if keyword:
        allowed, message = billing_service.check_search_limit(user_id, plan)
        if not allowed:
            flash(message, 'warning')
            customers = customer_service.get_all_customers()
            return render_template('customer/list.html', customers=customers, keyword='')

        # 検索カウントをインクリメント
        billing_service.increment_search_count(user_id)
        customers = customer_service.search_customers(keyword, user_id)
    else:
        customers = customer_service.get_all_customers()

    # プラン制限情報を取得
    customer_limit = PlanLimits.get_customer_limit(plan)
    current_count = customer_service.get_customer_count()

    return render_template(
        'customer/list.html',
        customers=customers,
        keyword=keyword,
        customer_limit=customer_limit,
        current_count=current_count
    )


@customer_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """顧客新規登録"""
    user_id = session.get('user_id')
    plan = session.get('plan', 'basic')

    # 登録前に制限チェック
    current_count = customer_service.get_customer_count()
    allowed, message = billing_service.check_customer_limit(user_id, plan, current_count)

    if not allowed:
        flash(message, 'warning')
        return redirect(url_for('customer.customer_list'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()

        success, message, customer = customer_service.create_customer(
            name=name,
            address=address,
            phone=phone,
            email=email,
            user_id=user_id
        )

        if success:
            flash(message, 'success')
            return redirect(url_for('customer.customer_list'))
        else:
            flash(message, 'danger')

    return render_template('customer/form.html', customer=None, action='new')


@customer_bp.route('/<customer_id>')
@login_required
def detail(customer_id: str):
    """顧客詳細"""
    user_id = session.get('user_id')
    customer = customer_service.get_customer(customer_id, user_id)

    if not customer:
        flash('指定された顧客が見つかりません。', 'danger')
        return redirect(url_for('customer.customer_list'))

    # 解析結果を取得
    analysis_results = analysis_service.get_results_by_customer(customer_id)

    return render_template('customer/detail.html', customer=customer, analysis_results=analysis_results)

@customer_bp.route('/<customer_id>/run-analysis', methods=['POST'])
@login_required
def run_analysis(customer_id: str):
    """実写データ解析の実行"""
    user_id = session.get('user_id')
    # 管理者またはデータ所有者のみ実行可能とする（簡易）
    customer = customer_service.get_customer(customer_id, user_id)
    if not customer:
        flash('権限がありません。', 'danger')
        return redirect(url_for('customer.customer_list'))

    success, message, result = analysis_service.run_analysis(customer_id)
    if success:
        flash(f"{message} (精度: {result.accuracy_score*100:.1f}%)", 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('customer.detail', customer_id=customer_id))


@customer_bp.route('/<customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(customer_id: str):
    """顧客編集"""
    user_id = session.get('user_id')
    customer = customer_service.get_customer(customer_id, user_id)

    if not customer:
        flash('指定された顧客が見つかりません。', 'danger')
        return redirect(url_for('customer.customer_list'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()

        success, message = customer_service.update_customer(
            customer_id=customer_id,
            name=name,
            address=address,
            phone=phone,
            email=email,
            user_id=user_id
        )

        if success:
            flash(message, 'success')
            return redirect(url_for('customer.customer_list'))
        else:
            flash(message, 'danger')
            # フォームに入力値を保持
            customer.name = name
            customer.address = address
            customer.phone = phone
            customer.email = email

    return render_template('customer/form.html', customer=customer, action='edit')


@customer_bp.route('/<customer_id>/delete', methods=['POST'])
@login_required
def delete(customer_id: str):
    """顧客削除"""
    user_id = session.get('user_id')

    success, message = customer_service.delete_customer(customer_id, user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('customer.customer_list'))
