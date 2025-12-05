"""
app/views パッケージ
ビュー（ルート）層
"""
from app.views.auth import auth_bp, login_required, admin_required
from app.views.main import main_bp
from app.views.customer import customer_bp

__all__ = ['auth_bp', 'main_bp', 'customer_bp', 'login_required', 'admin_required']
