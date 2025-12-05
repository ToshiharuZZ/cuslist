"""
顧客管理関連のビュー（ルート）
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.views.auth import login_required
from app.services.customer_service import CustomerService

customer_bp = Blueprint('customer', __name__, url_prefix='/customers')
customer_service = CustomerService()


@customer_bp.route('/')
@login_required
def customer_list():
    """顧客一覧"""
    customers = customer_service.get_all_customers()
    return render_template('customer/list.html', customers=customers)


@customer_bp.route('/search')
@login_required
def search():
    """顧客検索"""
    keyword = request.args.get('keyword', '').strip()
    user_id = session.get('user_id')

    if keyword:
        customers = customer_service.search_customers(keyword, user_id)
    else:
        customers = customer_service.get_all_customers()

    return render_template('customer/list.html', customers=customers, keyword=keyword)


@customer_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    """顧客新規登録"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        user_id = session.get('user_id')

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

    return render_template('customer/detail.html', customer=customer)


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
