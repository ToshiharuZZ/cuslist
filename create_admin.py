"""
初期管理者アカウント作成スクリプト
"""
import os
import sys

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from app.models.user import User, UserRepository
from app.models.crypto_manager import CryptoManager


def create_admin_user(user_id: str = 'admin', password: str = 'admin123'):
    """
    初期管理者アカウントを作成する。

    Args:
        user_id: 管理者ID（デフォルト: admin）
        password: パスワード（デフォルト: admin123）
    """
    repo = UserRepository()

    # 既存チェック
    if repo.exists(user_id):
        print(f"管理者 '{user_id}' は既に存在します。")
        return False

    # パスワードハッシュ化
    password_hash = CryptoManager.create_password_hash(password)

    # 管理者ユーザー作成
    admin = User(
        user_id=user_id,
        password_hash=password_hash,
        role=User.ROLE_ADMIN,
        plan=User.PLAN_PREMIUM,
        billing_type=User.BILLING_SUBSCRIPTION
    )

    repo.save(admin)
    print(f"✅ 管理者アカウントを作成しました。")
    print(f"   利用者ID: {user_id}")
    print(f"   パスワード: {password}")
    print(f"   ⚠️  ログイン後にパスワードを変更してください。")
    return True


if __name__ == '__main__':
    # 環境変数から暗号化キーを確認
    if not os.environ.get('ENCRYPTION_KEY'):
        # テスト用のキーを生成して設定
        key = CryptoManager.generate_key()
        os.environ['ENCRYPTION_KEY'] = key
        print(f"⚠️  ENCRYPTION_KEY が設定されていないため、一時キーを生成しました。")
        print(f"   本番環境では .env ファイルに以下を設定してください:")
        print(f"   ENCRYPTION_KEY={key}")
        print()

    # 引数があれば使用、なければデフォルト
    if len(sys.argv) >= 3:
        create_admin_user(sys.argv[1], sys.argv[2])
    else:
        create_admin_user()
