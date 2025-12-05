"""
CustomerService: 顧客管理サービス
顧客リスト管理システム - ビジネスロジック層
"""
from typing import Optional, Tuple, List
from app.models.customer import Customer, CustomerRepository
from app.models.logger import OperationLogger
import re


class CustomerService:
    """
    顧客管理のビジネスロジックを提供するサービスクラス。
    バリデーション、CRUD操作、検索機能を担当。
    """

    def __init__(
        self,
        customer_repository: Optional[CustomerRepository] = None,
        logger: Optional[OperationLogger] = None
    ):
        self.customer_repo = customer_repository or CustomerRepository()
        self.logger = logger or OperationLogger()

    def create_customer(
        self,
        name: str,
        address: str,
        phone: str,
        email: str,
        user_id: str
    ) -> Tuple[bool, str, Optional[Customer]]:
        """
        新規顧客を登録する。

        Args:
            name: 顧客名
            address: 住所
            phone: 電話番号
            email: メールアドレス
            user_id: 操作を行う利用者ID

        Returns:
            (成功フラグ, メッセージ, 作成されたCustomerオブジェクト or None)
        """
        # バリデーション
        validation_error = self._validate_customer_input(name, phone, email)
        if validation_error:
            return False, validation_error, None

        # 顧客作成
        customer = Customer(
            customer_id='',  # 自動採番
            name=name,
            address=address,
            phone=phone,
            email=email
        )

        customer_id = self.customer_repo.save(customer)
        customer.customer_id = customer_id

        # ログ記録
        self.logger.log(
            user_id,
            OperationLogger.OP_CUSTOMER_CREATE,
            target_id=customer_id,
            details=f"name={name}"
        )

        return True, f"顧客を登録しました。(ID: {customer_id})", customer

    def get_customer(self, customer_id: str, user_id: str) -> Optional[Customer]:
        """
        顧客を取得する。

        Args:
            customer_id: 顧客ID
            user_id: 操作を行う利用者ID

        Returns:
            Customerオブジェクト or None
        """
        customer = self.customer_repo.find_by_id(customer_id)
        if customer:
            self.logger.log(
                user_id,
                OperationLogger.OP_CUSTOMER_READ,
                target_id=customer_id
            )
        return customer

    def get_all_customers(self) -> List[Customer]:
        """全顧客を取得する"""
        return self.customer_repo.find_all()

    def update_customer(
        self,
        customer_id: str,
        name: str,
        address: str,
        phone: str,
        email: str,
        user_id: str
    ) -> Tuple[bool, str]:
        """
        顧客情報を更新する。

        Args:
            customer_id: 顧客ID
            name: 顧客名
            address: 住所
            phone: 電話番号
            email: メールアドレス
            user_id: 操作を行う利用者ID

        Returns:
            (成功フラグ, メッセージ)
        """
        # 存在チェック
        existing = self.customer_repo.find_by_id(customer_id)
        if not existing:
            return False, "指定された顧客が見つかりません。"

        # バリデーション
        validation_error = self._validate_customer_input(name, phone, email)
        if validation_error:
            return False, validation_error

        # 更新
        existing.name = name
        existing.address = address
        existing.phone = phone
        existing.email = email

        success = self.customer_repo.update(existing)
        if not success:
            return False, "顧客情報の更新に失敗しました。"

        # ログ記録
        self.logger.log(
            user_id,
            OperationLogger.OP_CUSTOMER_UPDATE,
            target_id=customer_id,
            details=f"name={name}"
        )

        return True, "顧客情報を更新しました。"

    def delete_customer(self, customer_id: str, user_id: str) -> Tuple[bool, str]:
        """
        顧客を削除する。

        Args:
            customer_id: 顧客ID
            user_id: 操作を行う利用者ID

        Returns:
            (成功フラグ, メッセージ)
        """
        # 存在チェック
        if not self.customer_repo.exists(customer_id):
            return False, "指定された顧客が見つかりません。"

        success = self.customer_repo.delete(customer_id)
        if not success:
            return False, "顧客の削除に失敗しました。"

        # ログ記録
        self.logger.log(
            user_id,
            OperationLogger.OP_CUSTOMER_DELETE,
            target_id=customer_id
        )

        return True, "顧客を削除しました。"

    def search_customers(self, keyword: str, user_id: str) -> List[Customer]:
        """
        顧客を検索する。

        Args:
            keyword: 検索キーワード
            user_id: 操作を行う利用者ID

        Returns:
            マッチしたCustomerオブジェクトのリスト
        """
        results = self.customer_repo.search(keyword)

        # ログ記録
        self.logger.log(
            user_id,
            OperationLogger.OP_CUSTOMER_SEARCH,
            details=f"keyword={keyword}, results={len(results)}"
        )

        return results

    def get_customer_count(self) -> int:
        """顧客数を取得する"""
        return self.customer_repo.count()

    def _validate_customer_input(
        self,
        name: str,
        phone: str,
        email: str
    ) -> Optional[str]:
        """
        顧客入力のバリデーションを行う。

        Args:
            name: 顧客名
            phone: 電話番号
            email: メールアドレス

        Returns:
            エラーメッセージ（問題がなければNone）
        """
        # 名前のバリデーション
        if not name or len(name.strip()) == 0:
            return "顧客名は必須です。"
        if len(name) > 100:
            return "顧客名は100文字以内で入力してください。"

        # 電話番号のバリデーション（任意項目だが、入力時はフォーマットチェック）
        if phone:
            # ハイフンあり/なし、数字のみを許可
            phone_pattern = r'^[\d\-\+\(\)\s]+$'
            if not re.match(phone_pattern, phone):
                return "電話番号の形式が正しくありません。"
            if len(phone) > 20:
                return "電話番号は20文字以内で入力してください。"

        # メールアドレスのバリデーション（任意項目だが、入力時はフォーマットチェック）
        if email:
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, email):
                return "メールアドレスの形式が正しくありません。"
            if len(email) > 255:
                return "メールアドレスは255文字以内で入力してください。"

        return None
