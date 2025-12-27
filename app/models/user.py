"""
User: 利用者モデル
顧客リスト管理システム - 利用者管理
"""
from typing import Optional, List, Dict
from datetime import datetime
from app.models.crypto_manager import CryptoManager


class User:
    """
    利用者を表すモデルクラス。
    """

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
        status: str = 'active',
        cancellation_date: str = '',
        plan_change_count: int = 0,
        last_plan_change_date: str = '',
        data_retention_until: str = '',
        created_at: Optional[str] = None,
        # 平文データ
        balance: str = '0'
    ):
        self.user_id = user_id
        self.password_hash = password_hash
        self.role = role
        self.plan = plan
        self.billing_type = billing_type
        self._balance_enc = balance_enc
        self.status = status
        self.cancellation_date = cancellation_date
        self.plan_change_count = int(plan_change_count)
        self.last_plan_change_date = last_plan_change_date
        self.data_retention_until = data_retention_until
        self.created_at = created_at or datetime.now().isoformat()
        self._balance = balance

    @property
    def balance(self) -> str:
        return self._balance

    @balance.setter
    def balance(self, value: str):
        self._balance = value

    def to_dict(self) -> Dict[str, str]:
        """プレーンな辞書形式に変換（アプリケーション内使用）"""
        return {
            'user_id': self.user_id,
            'password_hash': self.password_hash,
            'role': self.role,
            'plan': self.plan,
            'billing_type': self.billing_type,
            'balance': self._balance,
            'status': self.status,
            'cancellation_date': self.cancellation_date,
            'plan_change_count': str(self.plan_change_count),
            'last_plan_change_date': self.last_plan_change_date,
            'data_retention_until': self.data_retention_until,
            'created_at': self.created_at
        }

    def to_encrypted_dict(self, crypto: CryptoManager) -> Dict[str, str]:
        """暗号化して辞書形式に変換（DB保存用）"""
        return {
            'user_id': self.user_id,
            'password_hash': self.password_hash,
            'role': self.role,
            'plan': self.plan,
            'billing_type': self.billing_type,
            'balance_enc': crypto.encrypt(self._balance),
            'status': self.status,
            'cancellation_date': self.cancellation_date,
            'plan_change_count': self.plan_change_count,
            'last_plan_change_date': self.last_plan_change_date,
            'data_retention_until': self.data_retention_until,
            'created_at': self.created_at
        }

    @classmethod
    def from_encrypted_dict(cls, data: Dict[str, str], crypto: CryptoManager) -> 'User':
        """暗号化された辞書からUserインスタンスを生成（DB読み込み用）"""
        return cls(
            user_id=data.get('user_id', ''),
            password_hash=data.get('password_hash', ''),
            role=data.get('role', cls.ROLE_USER),
            plan=data.get('plan', cls.PLAN_BASIC),
            billing_type=data.get('billing_type', cls.BILLING_SUBSCRIPTION),
            balance=crypto.decrypt(data.get('balance_enc', '')) if data.get('balance_enc') else '0',
            balance_enc=data.get('balance_enc', ''),
            status=data.get('status', 'active'),
            cancellation_date=data.get('cancellation_date', ''),
            plan_change_count=int(data.get('plan_change_count', 0)),
            last_plan_change_date=data.get('last_plan_change_date', ''),
            data_retention_until=data.get('data_retention_until', ''),
            created_at=data.get('created_at')
        )

    def is_admin(self) -> bool:
        """管理者かどうかを判定"""
        return self.role == self.ROLE_ADMIN


from app import db
from app.models.db_models import User as UserDB


class UserRepository:
    """
    利用者データへのアクセスを管理するリポジトリクラス (SQLAlchemy版)。
    """

    def __init__(self, crypto: Optional[CryptoManager] = None, **kwargs):
        self.crypto = crypto or CryptoManager()

    def find_by_id(self, user_id: str) -> Optional[User]:
        """
        利用者IDで検索する。
        """
        record = db.session.get(UserDB, user_id)
        if record:
            return User.from_encrypted_dict(record.to_dict(), self.crypto)
        return None

    def find_all(self) -> List[User]:
        """
        全利用者を取得する。
        """
        records = UserDB.query.all()
        return [User.from_encrypted_dict(r.to_dict(), self.crypto) for r in records]

    def save(self, user: User) -> None:
        """
        利用者を保存する。
        """
        if self.find_by_id(user.user_id):
            self.update(user)
            return

        encrypted_data = user.to_encrypted_dict(self.crypto)
        record = UserDB(**encrypted_data)
        db.session.add(record)
        db.session.commit()

    def update(self, user: User) -> bool:
        """
        利用者情報を更新する。
        """
        record = db.session.get(UserDB, user.user_id)
        if record:
            encrypted_data = user.to_encrypted_dict(self.crypto)
            for key, value in encrypted_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            db.session.commit()
            return True
        return False

    def delete(self, user_id: str) -> bool:
        """
        利用者を削除する。
        """
        record = db.session.get(UserDB, user_id)
        if record:
            db.session.delete(record)
            db.session.commit()
            return True
        return False

    def exists(self, user_id: str) -> bool:
        """
        利用者が存在するかチェックする。
        """
        return db.session.get(UserDB, user_id) is not None

    def count(self) -> int:
        """利用者数を返す"""
        return UserDB.query.count()
