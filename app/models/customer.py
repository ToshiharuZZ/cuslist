"""
Customer: 顧客モデル
顧客リスト管理システム - 顧客管理
"""
from typing import Optional, List, Dict
from datetime import datetime
from app.models.crypto_manager import CryptoManager


class Customer:
    """
    顧客を表すモデルクラス。
    customers.csv とマッピングし、暗号化・復号処理を行う。
    """

    # customers.csv のカラム定義（詳細設計書準拠）
    FIELDNAMES = [
        'customer_id',
        'user_id',                   # 変更: 所有者ID
        'name_enc',
        'address_enc',
        'phone_enc',
        'email_enc',
        'created_at'
    ]

    def __init__(
        self,
        customer_id: str,
        user_id: str = '',
        name: str = '',
        address: str = '',
        phone: str = '',
        email: str = '',
        created_at: Optional[str] = None,
        # 暗号化済みデータ（CSV読み込み時に使用）
        name_enc: str = '',
        address_enc: str = '',
        phone_enc: str = '',
        email_enc: str = ''
    ):
        self.customer_id = customer_id
        self.user_id = user_id
        # 平文データ
        self._name = name
        self._address = address
        self._phone = phone
        self._email = email
        # 暗号化済みデータ
        self._name_enc = name_enc
        self._address_enc = address_enc
        self._phone_enc = phone_enc
        self._email_enc = email_enc
        self.created_at = created_at or datetime.now().isoformat()

    # プロパティ（平文アクセス用）
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, value: str):
        self._address = value

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        self._phone = value

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        self._email = value

    def to_encrypted_dict(self, crypto: CryptoManager) -> Dict[str, str]:
        """
        暗号化して辞書形式に変換（CSV保存用）。

        Args:
            crypto: 暗号化に使用するCryptoManagerインスタンス

        Returns:
            暗号化されたデータの辞書
        """
        return {
            'customer_id': self.customer_id,
            'user_id': self.user_id,
            'name_enc': crypto.encrypt(self._name),
            'address_enc': crypto.encrypt(self._address),
            'phone_enc': crypto.encrypt(self._phone),
            'email_enc': crypto.encrypt(self._email),
            'created_at': self.created_at
        }

    @classmethod
    def from_encrypted_dict(cls, data: Dict[str, str], crypto: CryptoManager) -> 'Customer':
        """
        暗号化された辞書からCustomerインスタンスを生成（CSV読み込み用）。

        Args:
            data: CSVから読み込んだ暗号化データ
            crypto: 復号に使用するCryptoManagerインスタンス

        Returns:
            復号されたCustomerインスタンス
        """
        return cls(
            customer_id=data.get('customer_id', ''),
            user_id=data.get('user_id', ''),
            name=crypto.decrypt(data.get('name_enc', '')),
            address=crypto.decrypt(data.get('address_enc', '')),
            phone=crypto.decrypt(data.get('phone_enc', '')),
            email=crypto.decrypt(data.get('email_enc', '')),
            created_at=data.get('created_at'),
            name_enc=data.get('name_enc', ''),
            address_enc=data.get('address_enc', ''),
            phone_enc=data.get('phone_enc', ''),
            email_enc=data.get('email_enc', '')
        )

    def to_display_dict(self) -> Dict[str, str]:
        """表示用の辞書形式に変換"""
        return {
            'customer_id': self.customer_id,
            'name': self._name,
            'address': self._address,
            'phone': self._phone,
            'email': self._email,
            'created_at': self.created_at
        }


from app import db
from app.models.db_models import Customer as CustomerDB


class CustomerRepository:
    """
    顧客データへのアクセスを管理するリポジトリクラス (SQLAlchemy版)。
    暗号化・復号処理を内包する。
    """

    def __init__(self, crypto: Optional[CryptoManager] = None, **kwargs):
        self.crypto = crypto or CryptoManager()

    def find_by_id(self, customer_id: str) -> Optional[Customer]:
        """
        顧客IDで検索する。
        """
        record = db.session.get(CustomerDB, customer_id)
        if record:
            return Customer.from_encrypted_dict(record.to_dict(), self.crypto)
        return None

    def find_all(self) -> List[Customer]:
        """
        全顧客を取得する（復号済み）。
        """
        records = CustomerDB.query.all()
        return [Customer.from_encrypted_dict(r.to_dict(), self.crypto) for r in records]

    def save(self, customer: Customer) -> str:
        """
        顧客を保存する（新規追加）。
        """
        # IDが未設定の場合は自動採番（DBの連番機能等も検討可能だが、一旦現状の仕様を維持）
        if not customer.customer_id:
            # 簡略化のためにラストID+1を取得するロジックが必要だが、
            # SQLAlchemyモデルで自動採番するようにしていないため、
            # 以前の CSV 用ロジック（または代替）が必要
            last_record = CustomerDB.query.order_by(CustomerDB.customer_id.desc()).first()
            if last_record:
                last_num = int(last_record.customer_id[3:]) # 'CUS001' -> 1
                customer.customer_id = f"CUS{last_num + 1:03d}"
            else:
                customer.customer_id = "CUS001"

        encrypted_data = customer.to_encrypted_dict(self.crypto)
        record = CustomerDB(**encrypted_data)
        db.session.add(record)
        db.session.commit()
        return customer.customer_id

    def update(self, customer: Customer) -> bool:
        """
        顧客情報を更新する。
        """
        record = db.session.get(CustomerDB, customer.customer_id)
        if record:
            encrypted_data = customer.to_encrypted_dict(self.crypto)
            for key, value in encrypted_data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            db.session.commit()
            return True
        return False

    def delete(self, customer_id: str) -> bool:
        """
        顧客を削除する。
        """
        record = db.session.get(CustomerDB, customer_id)
        if record:
            db.session.delete(record)
            db.session.commit()
            return True
        return False

    def search(self, keyword: str) -> List[Customer]:
        """
        キーワードで顧客を検索する（メモリ内検索 または DB検索）。
        暗号化されているため、現状通り全件取得してメモリで検索する。
        """
        all_customers = self.find_all()
        if not keyword:
            return all_customers

        keyword_lower = keyword.lower()
        results = []
        for customer in all_customers:
            if (keyword_lower in customer.name.lower() or
                keyword_lower in customer.phone.lower() or
                keyword_lower in customer.email.lower() or
                keyword_lower in customer.address.lower()):
                results.append(customer)
        return results

    def count(self) -> int:
        """顧客数を返す"""
        return CustomerDB.query.count()

    def exists(self, customer_id: str) -> bool:
        """顧客が存在するかチェックする"""
        return db.session.get(CustomerDB, customer_id) is not None
