"""
メイン画面のビュー（ルート）
"""
from flask import Blueprint, render_template, session
from app.views.auth import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """トップページ（ログイン画面へリダイレクト）"""
    if 'user_id' in session:
        return render_template('main/dashboard.html')
    return render_template('auth/login.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """ダッシュボード（ログイン後のメイン画面）"""
    return render_template('main/dashboard.html')
