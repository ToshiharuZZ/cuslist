"""
Customer: 顧客モデル
顧客リスト管理システム - 顧客管理
"""
from typing import Optional, List, Dict
from datetime import datetime
from app.models.csv_handler import CsvHandler
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


class CustomerRepository:
    """
    顧客データへのアクセスを管理するリポジトリクラス。
    暗号化・復号処理を内包する。
    """

    def __init__(
        self,
        csv_path: str = 'data/customers.csv',
        crypto: Optional[CryptoManager] = None
    ):
        self.csv_handler = CsvHandler(csv_path, Customer.FIELDNAMES)
        self.crypto = crypto or CryptoManager()

    def find_by_id(self, customer_id: str) -> Optional[Customer]:
        """
        顧客IDで検索する。

        Args:
            customer_id: 検索する顧客ID

        Returns:
            見つかったCustomerオブジェクト、または None
        """
        record = self.csv_handler.find_by_id('customer_id', customer_id)
        if record:
            return Customer.from_encrypted_dict(record, self.crypto)
        return None

    def find_all(self) -> List[Customer]:
        """
        全顧客を取得する（復号済み）。

        Returns:
            Customerオブジェクトのリスト
        """
        records = self.csv_handler.read_all()
        return [Customer.from_encrypted_dict(record, self.crypto) for record in records]

    def save(self, customer: Customer) -> str:
        """
        顧客を保存する（新規追加）。

        Args:
            customer: 保存するCustomerオブジェクト

        Returns:
            採番された顧客ID
        """
        # IDが未設定の場合は自動採番
        if not customer.customer_id:
            customer.customer_id = self.csv_handler.generate_next_id('customer_id', 'CUS')

        encrypted_data = customer.to_encrypted_dict(self.crypto)
        self.csv_handler.add_record(encrypted_data)
        return customer.customer_id

    def update(self, customer: Customer) -> bool:
        """
        顧客情報を更新する。

        Args:
            customer: 更新するCustomerオブジェクト

        Returns:
            更新成功時True
        """
        encrypted_data = customer.to_encrypted_dict(self.crypto)
        return self.csv_handler.update_record('customer_id', customer.customer_id, encrypted_data)

    def delete(self, customer_id: str) -> bool:
        """
        顧客を削除する。

        Args:
            customer_id: 削除する顧客ID

        Returns:
            削除成功時True
        """
        return self.csv_handler.delete_record('customer_id', customer_id)

    def search(self, keyword: str) -> List[Customer]:
        """
        キーワードで顧客を検索する（メモリ内検索）。

        Args:
            keyword: 検索キーワード（名前、電話番号、メールアドレスで検索）

        Returns:
            マッチしたCustomerオブジェクトのリスト
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
        return self.csv_handler.count()

    def exists(self, customer_id: str) -> bool:
        """顧客が存在するかチェックする"""
        return self.find_by_id(customer_id) is not None
