"""
認証関連のビュー（ルート）
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from app.services.auth_service import AuthService
from app.models.user import User

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


def login_required(f):
    """ログイン必須デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('この機能を使用するにはログインが必要です。', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理者権限必須デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('この機能を使用するにはログインが必要です。', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != User.ROLE_ADMIN:
            flash('この機能は管理者のみ使用できます。', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """ログイン画面"""
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')

        if not user_id or not password:
            flash('利用者IDとパスワードを入力してください。', 'danger')
            return render_template('auth/login.html')

        success, user, message = auth_service.authenticate(user_id, password)

        if success and user:
            session['user_id'] = user.user_id
            session['role'] = user.role
            session['plan'] = user.plan
            flash(message, 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash(message, 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """ログアウト"""
    user_id = session.get('user_id')
    if user_id:
        auth_service.logout(user_id)
    session.clear()
    flash('ログアウトしました。', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/users')
@admin_required
def user_list():
    """利用者一覧（管理者用）"""
    users = auth_service.user_repo.find_all()
    return render_template('auth/user_list.html', users=users)


@auth_bp.route('/users/register', methods=['GET', 'POST'])
@admin_required
def register_user():
    """利用者登録（管理者用）"""
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', User.ROLE_USER)
        plan = request.form.get('plan', User.PLAN_BASIC)
        billing_type = request.form.get('billing_type', User.BILLING_SUBSCRIPTION)

        if not user_id or not password:
            flash('利用者IDとパスワードは必須です。', 'danger')
            return render_template('auth/register.html')

        success, message = auth_service.register_user(
            user_id=user_id,
            password=password,
            role=role,
            plan=plan,
            billing_type=billing_type,
            admin_user_id=session.get('user_id')
        )

        if success:
            flash(message, 'success')
            return redirect(url_for('auth.user_list'))
        else:
            flash(message, 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/users/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id: str):
    """利用者削除（管理者用）"""
    admin_user_id = session.get('user_id')
    success, message = auth_service.delete_user(user_id, admin_user_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')

    return redirect(url_for('auth.user_list'))
