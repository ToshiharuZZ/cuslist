"""
CustomerService 単体テスト
"""
import os
import pytest
from app import create_app, db
from app.models.customer import Customer, CustomerRepository
from app.models.crypto_manager import CryptoManager
from app.services.customer_service import CustomerService

class TestCustomerService:
    """CustomerServiceのテストクラス"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """テスト環境セットアップ"""
        os.environ['ENCRYPTION_KEY'] = CryptoManager.generate_key()
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.crypto = CryptoManager()
            self.customer_repo = CustomerRepository(crypto=self.crypto)
            from app.models.logger import OperationLogger
            self.logger = OperationLogger()
            self.customer_service = CustomerService(
                customer_repository=self.customer_repo,
                logger=self.logger
            )
            yield
            db.session.remove()
            db.drop_all()

    def test_create_customer(self):
        """顧客を作成できること"""
        success, message, customer = self.customer_service.create_customer(
            name='山田 太郎',
            address='東京都渋谷区',
            phone='03-1234-5678',
            email='yamada@example.com',
            user_id='testuser'
        )

        assert success is True
        assert customer is not None
        assert customer.customer_id.startswith('CUS')
        assert customer.name == '山田 太郎'

    def test_create_customer_name_required(self):
        """顧客名が必須であること"""
        success, message, customer = self.customer_service.create_customer(
            name='',
            address='東京都',
            phone='',
            email='',
            user_id='testuser'
        )

        assert success is False
        assert '必須' in message

    def test_create_customer_invalid_email(self):
        """無効なメールアドレスでエラーになること"""
        success, message, customer = self.customer_service.create_customer(
            name='山田 太郎',
            address='',
            phone='',
            email='invalid-email',
            user_id='testuser'
        )

        assert success is False
        assert 'メールアドレス' in message

    def test_get_customer(self):
        """顧客を取得できること"""
        # 顧客作成
        success, _, created = self.customer_service.create_customer(
            name='田中 花子',
            address='大阪府大阪市',
            phone='06-9876-5432',
            email='tanaka@example.com',
            user_id='testuser'
        )

        # 取得
        customer = self.customer_service.get_customer(created.customer_id, 'testuser')

        assert customer is not None
        assert customer.name == '田中 花子'

    def test_update_customer(self):
        """顧客情報を更新できること"""
        # 顧客作成
        success, _, created = self.customer_service.create_customer(
            name='佐藤 次郎',
            address='',
            phone='',
            email='',
            user_id='testuser'
        )

        # 更新
        success, message = self.customer_service.update_customer(
            customer_id=created.customer_id,
            name='佐藤 次郎（更新）',
            address='福岡県福岡市',
            phone='092-111-2222',
            email='sato@example.com',
            user_id='testuser'
        )

        assert success is True

        # 確認
        updated = self.customer_service.get_customer(created.customer_id, 'testuser')
        assert updated.name == '佐藤 次郎（更新）'
        assert updated.address == '福岡県福岡市'

    def test_delete_customer(self):
        """顧客を削除できること"""
        # 顧客作成
        success, _, created = self.customer_service.create_customer(
            name='削除対象',
            address='',
            phone='',
            email='',
            user_id='testuser'
        )

        # 削除
        success, message = self.customer_service.delete_customer(
            created.customer_id, 'testuser'
        )

        assert success is True

        # 確認
        customer = self.customer_service.get_customer(created.customer_id, 'testuser')
        assert customer is None

    def test_search_customers(self):
        """顧客を検索できること"""
        # 複数の顧客を作成
        self.customer_service.create_customer(
            name='山田 太郎', address='東京都', phone='03-1111-1111',
            email='yamada@example.com', user_id='testuser'
        )
        self.customer_service.create_customer(
            name='田中 花子', address='大阪府', phone='06-2222-2222',
            email='tanaka@example.com', user_id='testuser'
        )
        self.customer_service.create_customer(
            name='鈴木 一郎', address='東京都', phone='03-3333-3333',
            email='suzuki@example.com', user_id='testuser'
        )

        # 名前で検索
        results = self.customer_service.search_customers('山田', 'testuser')
        assert len(results) == 1
        assert results[0].name == '山田 太郎'

        # 住所で検索
        results = self.customer_service.search_customers('東京', 'testuser')
        assert len(results) == 2

    def test_customer_data_encrypted(self):
        """顧客データが暗号化されて保存されていること"""
        self.customer_service.create_customer(
            name='暗号化テスト',
            address='秘密の住所',
            phone='090-0000-0000',
            email='secret@example.com',
            user_id='testuser'
        )

        # DBレコードを直接確認
        from app.models.db_models import Customer as CustomerDB
        with self.app.app_context():
            record = CustomerDB.query.filter_by(user_id='testuser').first()
            assert record is not None
            # 平文データが含まれていないことを確認
            assert '暗号化テスト' not in record.name_enc
            assert '秘密の住所' not in record.address_enc
            assert '090-0000-0000' not in record.phone_enc
            assert 'secret@example.com' not in record.email_enc
