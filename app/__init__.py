"""
Flaskアプリケーション設定
"""
import os
from flask import Flask
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()


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

    # ブループリントの登録
    from app.views.auth import auth_bp
    from app.views.main import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
