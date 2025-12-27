"""
Flaskアプリケーション設定
"""
import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

# CSRFProtect インスタンス（グローバル）
csrf = CSRFProtect()

# データベース・マイグレーションインスタンス
db = SQLAlchemy()
migrate = Migrate()


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

    # データベース設定
    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
    else:
        data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        db_path = os.path.join(data_dir, 'database.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初期化
    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # ブループリントの登録
    from app.views.auth import auth_bp
    from app.views.main import main_bp
    from app.views.customer import customer_bp
    from app.views.plan import plan_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(plan_bp, url_prefix='/plan')

    # カスタムJinja2フィルタ
    import json
    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return {}

    # CLIコマンド登録
    from app.commands import init_app_commands
    init_app_commands(app)

    # モデルのインポート（Alembic検出用）
    from app.models import db_models

    return app
