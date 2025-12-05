"""
User: 利用者モデル
顧客リスト管理システム - 利用者管理
"""
from typing import Optional, List, Dict
from datetime import datetime
from app.models.csv_handler import CsvHandler
from app.models.crypto_manager import CryptoManager


class User:
    """
    利用者を表すモデルクラス。
    users.csv とマッピングし、認証・権限管理を行う。
    """

    # users.csv のカラム定義
    FIELDNAMES = [
        'user_id',
        'password_hash',
        'role',
        'plan',
        'billing_type',
        'balance_enc',
        'created_at'
    ]

    # 権限定数
    ROLE_ADMIN = 'admin'
    ROLE_USER = 'user'

    # プラン定数
    PLAN_BASIC = 'Basic'
    PLAN_STANDARD = 'Standard'
    PLAN_PREMIUM = 'Premium'

    # 課金方式定数
    BILLING_SUBSCRIPTION = 'subscription'
    BILLING_USAGE = 'usage'
    BILLING_TRANSACTION = 'transaction'
    BILLING_HYBRID = 'hybrid'

    def __init__(
        self,
        user_id: str,
        password_hash: str,
        role: str = ROLE_USER,
        plan: str = PLAN_BASIC,
        billing_type: str = BILLING_SUBSCRIPTION,
        balance_enc: str = '',
        created_at: Optional[str] = None
    ):
        self.user_id = user_id
        self.password_hash = password_hash
        self.role = role
        self.plan = plan
        self.billing_type = billing_type
        self.balance_enc = balance_enc
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, str]:
        """辞書形式に変換"""
        return {
            'user_id': self.user_id,
            'password_hash': self.password_hash,
            'role': self.role,
            'plan': self.plan,
            'billing_type': self.billing_type,
            'balance_enc': self.balance_enc,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'User':
        """辞書からUserインスタンスを生成"""
        return cls(
            user_id=data.get('user_id', ''),
            password_hash=data.get('password_hash', ''),
            role=data.get('role', cls.ROLE_USER),
            plan=data.get('plan', cls.PLAN_BASIC),
            billing_type=data.get('billing_type', cls.BILLING_SUBSCRIPTION),
            balance_enc=data.get('balance_enc', ''),
            created_at=data.get('created_at')
        )

    def is_admin(self) -> bool:
        """管理者かどうかを判定"""
        return self.role == self.ROLE_ADMIN


class UserRepository:
    """
    利用者データへのアクセスを管理するリポジトリクラス。
    """

    def __init__(self, csv_path: str = 'data/users.csv'):
        self.csv_handler = CsvHandler(csv_path, User.FIELDNAMES)

    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        利用者IDで検索する。

        Args:
            user_id: 検索する利用者ID

        Returns:
            見つかったUserオブジェクト、または None
        """
        record = self.csv_handler.find_by_id('user_id', user_id)
        if record:
            return User.from_dict(record)
        return None

    def find_all(self) -> List[User]:
        """
        全利用者を取得する。

        Returns:
            Userオブジェクトのリスト
        """
        records = self.csv_handler.read_all()
        return [User.from_dict(record) for record in records]

    def save(self, user: User) -> None:
        """
        利用者を保存する（新規追加）。

        Args:
            user: 保存するUserオブジェクト
        """
        self.csv_handler.add_record(user.to_dict())

    def update(self, user: User) -> bool:
        """
        利用者情報を更新する。

        Args:
            user: 更新するUserオブジェクト

        Returns:
            更新成功時True
        """
        return self.csv_handler.update_record('user_id', user.user_id, user.to_dict())

    def delete(self, user_id: str) -> bool:
        """
        利用者を削除する。

        Args:
            user_id: 削除する利用者ID

        Returns:
            削除成功時True
        """
        return self.csv_handler.delete_record('user_id', user_id)

    def exists(self, user_id: str) -> bool:
        """
        利用者が存在するかチェックする。

        Args:
            user_id: チェックする利用者ID

        Returns:
            存在する場合True
        """
        return self.find_by_id(user_id) is not None

    def count(self) -> int:
        """利用者数を返す"""
        return self.csv_handler.count()
