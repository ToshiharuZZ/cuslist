"""
AuthService: 認証サービス
顧客リスト管理システム - 認証・セッション管理
"""
from typing import Optional, Tuple
from datetime import datetime
from app.models.user import User, UserRepository
from app.models.crypto_manager import CryptoManager
from app.models.logger import OperationLogger


class AuthService:
    """
    認証・ユーザー管理を行うサービスクラス。
    ログイン試行回数制限、パスワードハッシュ検証などを担当。
    """

    # ログイン試行回数の制限
    MAX_LOGIN_ATTEMPTS = 5
    
    def __init__(
        self,
        user_repository: Optional[UserRepository] = None,
        logger: Optional[OperationLogger] = None
    ):
        self.user_repo = user_repository or UserRepository()
        self.logger = logger or OperationLogger()
        # ログイン試行回数を追跡（メモリ内、本番ではRedis等を検討）
        self._login_attempts: dict = {}

    def authenticate(self, user_id: str, password: str) -> Tuple[bool, Optional[User], str]:
        """
        利用者を認証する。

        Args:
            user_id: 利用者ID
            password: パスワード（平文）

        Returns:
            (成功フラグ, Userオブジェクト or None, メッセージ)
        """
        # ログイン試行回数チェック
        if self._is_locked_out(user_id):
            return False, None, "ログイン試行回数の上限に達しました。しばらく待ってから再試行してください。"

        # ユーザー検索
        user = self.user_repo.find_by_id(user_id)
        if not user:
            self._increment_login_attempts(user_id)
            return False, None, "利用者IDまたはパスワードが正しくありません。"

        # パスワード検証
        if not CryptoManager.verify_password(password, user.password_hash):
            self._increment_login_attempts(user_id)
            return False, None, "利用者IDまたはパスワードが正しくありません。"

        # 認証成功
        self._reset_login_attempts(user_id)
        self.logger.log(user_id, OperationLogger.OP_LOGIN)
        return True, user, "ログインに成功しました。"

    def logout(self, user_id: str) -> None:
        """
        ログアウト処理を行う。

        Args:
            user_id: 利用者ID
        """
        self.logger.log(user_id, OperationLogger.OP_LOGOUT)

    def register_user(
        self,
        user_id: str,
        password: str,
        role: str = User.ROLE_USER,
        plan: str = User.PLAN_BASIC,
        billing_type: str = User.BILLING_SUBSCRIPTION,
        admin_user_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        新規利用者を登録する。

        Args:
            user_id: 新規利用者ID
            password: パスワード（平文）
            role: 権限
            plan: 契約プラン
            billing_type: 課金方式
            admin_user_id: 登録を行う管理者のID（ログ用）

        Returns:
            (成功フラグ, メッセージ)
        """
        # 重複チェック
        if self.user_repo.exists(user_id):
            return False, "この利用者IDは既に使用されています。"

        # パスワードをハッシュ化
        password_hash = CryptoManager.create_password_hash(password)

        # ユーザー作成
        new_user = User(
            user_id=user_id,
            password_hash=password_hash,
            role=role,
            plan=plan,
            billing_type=billing_type
        )

        self.user_repo.save(new_user)

        # ログ記録
        if admin_user_id:
            self.logger.log(
                admin_user_id,
                OperationLogger.OP_USER_CREATE,
                target_id=user_id,
                details=f"role={role}, plan={plan}"
            )

        return True, "利用者の登録が完了しました。"

    def delete_user(self, user_id: str, admin_user_id: str) -> Tuple[bool, str]:
        """
        利用者を削除する。

        Args:
            user_id: 削除する利用者ID
            admin_user_id: 削除を行う管理者のID

        Returns:
            (成功フラグ, メッセージ)
        """
        if not self.user_repo.exists(user_id):
            return False, "指定された利用者が見つかりません。"

        # 自分自身は削除できない
        if user_id == admin_user_id:
            return False, "自分自身を削除することはできません。"

        self.user_repo.delete(user_id)

        # ログ記録
        self.logger.log(
            admin_user_id,
            OperationLogger.OP_USER_DELETE,
            target_id=user_id
        )

        return True, "利用者を削除しました。"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        パスワードを変更する。

        Args:
            user_id: 利用者ID
            old_password: 現在のパスワード
            new_password: 新しいパスワード

        Returns:
            (成功フラグ, メッセージ)
        """
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False, "利用者が見つかりません。"

        # 現在のパスワードを検証
        if not CryptoManager.verify_password(old_password, user.password_hash):
            return False, "現在のパスワードが正しくありません。"

        # 新しいパスワードをハッシュ化
        user.password_hash = CryptoManager.create_password_hash(new_password)
        self.user_repo.update(user)

        return True, "パスワードを変更しました。"

    def _is_locked_out(self, user_id: str) -> bool:
        """ログインがロックされているかチェック"""
        attempts = self._login_attempts.get(user_id, 0)
        return attempts >= self.MAX_LOGIN_ATTEMPTS

    def _increment_login_attempts(self, user_id: str) -> None:
        """ログイン試行回数をインクリメント"""
        self._login_attempts[user_id] = self._login_attempts.get(user_id, 0) + 1

    def _reset_login_attempts(self, user_id: str) -> None:
        """ログイン試行回数をリセット"""
        if user_id in self._login_attempts:
            del self._login_attempts[user_id]
