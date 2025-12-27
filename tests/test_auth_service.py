"""
AuthService 単体テスト
"""
import os
import pytest
from app import create_app, db
from app.models.user import User, UserRepository
from app.models.crypto_manager import CryptoManager
from app.services.auth_service import AuthService

class TestAuthService:
    """AuthServiceのテストクラス"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """テスト環境セットアップ"""
        os.environ['ENCRYPTION_KEY'] = CryptoManager.generate_key()
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            from app.models.logger import OperationLogger
            self.user_repo = UserRepository()
            self.logger = OperationLogger()
            self.auth_service = AuthService(
                user_repository=self.user_repo,
                logger=self.logger
            )
            yield
            db.session.remove()
            db.drop_all()

    def test_register_user(self):
        """利用者を登録できること"""
        success, message = self.auth_service.register_user(
            user_id='testuser',
            password='password123',
            role=User.ROLE_USER,
            plan=User.PLAN_BASIC
        )

        assert success is True
        assert self.user_repo.exists('testuser')

    def test_register_duplicate_user(self):
        """重複した利用者IDで登録が失敗すること"""
        self.auth_service.register_user('testuser', 'password123')

        success, message = self.auth_service.register_user('testuser', 'different_password')

        assert success is False
        assert '既に使用されています' in message

    def test_authenticate_success(self):
        """正しい認証情報でログインできること"""
        self.auth_service.register_user('testuser', 'password123')

        success, user, message = self.auth_service.authenticate('testuser', 'password123')

        assert success is True
        assert user is not None
        assert user.user_id == 'testuser'

    def test_authenticate_wrong_password(self):
        """間違ったパスワードでログインが失敗すること"""
        self.auth_service.register_user('testuser', 'password123')

        success, user, message = self.auth_service.authenticate('testuser', 'wrong_password')

        assert success is False
        assert user is None

    def test_authenticate_nonexistent_user(self):
        """存在しない利用者でログインが失敗すること"""
        success, user, message = self.auth_service.authenticate('nonexistent', 'password')

        assert success is False
        assert user is None

    def test_login_attempt_limit(self):
        """ログイン試行回数制限が機能すること"""
        self.auth_service.register_user('testuser', 'password123')

        # MAX_LOGIN_ATTEMPTS回失敗させる
        for _ in range(AuthService.MAX_LOGIN_ATTEMPTS):
            self.auth_service.authenticate('testuser', 'wrong_password')

        # 正しいパスワードでもロックアウトされる
        success, user, message = self.auth_service.authenticate('testuser', 'password123')
        assert success is False
        assert 'ログイン試行回数の上限' in message

    def test_delete_user(self):
        """利用者を削除できること"""
        self.auth_service.register_user('admin', 'admin123', role=User.ROLE_ADMIN)
        self.auth_service.register_user('testuser', 'password123')

        success, message = self.auth_service.delete_user('testuser', 'admin')

        assert success is True
        assert not self.user_repo.exists('testuser')

    def test_delete_self_not_allowed(self):
        """自分自身を削除できないこと"""
        self.auth_service.register_user('admin', 'admin12345', role=User.ROLE_ADMIN)

        success, message = self.auth_service.delete_user('admin', 'admin')

        assert success is False
        assert '自分自身を削除' in message

    def test_register_user_id_too_short(self):
        """利用者IDが短すぎる場合に登録が失敗すること"""
        success, message = self.auth_service.register_user('ab', 'password123')

        assert success is False
        assert '3文字以上' in message

    def test_register_password_too_short(self):
        """パスワードが短すぎる場合に登録が失敗すること"""
        success, message = self.auth_service.register_user('testuser', 'short')

        assert success is False
        assert '8文字以上' in message

    def test_register_invalid_user_id_characters(self):
        """利用者IDに不正な文字が含まれる場合に登録が失敗すること"""
        success, message = self.auth_service.register_user('test@user!', 'password123')

        assert success is False
        assert '半角英数字' in message

    def test_register_password_same_as_user_id(self):
        """パスワードが利用者IDと同じ場合に登録が失敗すること"""
        success, message = self.auth_service.register_user('testuser', 'testuser')

        assert success is False
        assert '利用者IDは使用できません' in message
