"""
Flaskアプリケーション設定
"""
import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# CSRFProtect インスタンス（グローバル）
csrf = CSRFProtect()


def create_app(config_name: str = 'development') -> Flask:
    """
    Flaskアプリケーションファクトリ。

    Args:
        config_name: 設定名（development/production/testing）

    Returns:
        Flaskアプリケーションインスタンス
    """
    app = Flask(__name__)

    # 基本設定
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['WTF_CSRF_ENABLED'] = True

    # CSRF保護の初期化
    csrf.init_app(app)

    # ブループリントの登録
    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.customer import customer_bp
    from app.views.plan import plan_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(plan_bp, url_prefix='/plan')

    # CLIコマンド登録
    from app.commands import init_app_commands
    init_app_commands(app)

    return app
