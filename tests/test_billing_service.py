"""
BillingService 単体テスト
"""
import os
import pytest
from app import create_app, db
from app.models.crypto_manager import CryptoManager
from app.services.billing_service import BillingService, PlanLimits

class TestPlanLimits:
    """PlanLimitsのテストクラス"""

    def test_get_basic_plan(self):
        """Basicプランの情報を取得できること"""
        plan = PlanLimits.get_plan('basic')
        assert plan is not None
        assert plan['monthly_fee'] == 500
        assert plan['customer_limit'] == 100
        assert plan['search_limit_daily'] == 50

    def test_get_premium_plan_unlimited(self):
        """Premiumプランは無制限であること"""
        plan = PlanLimits.get_plan('premium')
        assert plan is not None
        assert plan['customer_limit'] is None
        assert plan['search_limit_daily'] is None

    def test_get_customer_limit(self):
        """顧客登録件数上限を取得できること"""
        assert PlanLimits.get_customer_limit('basic') == 100
        assert PlanLimits.get_customer_limit('standard') == 1000
        assert PlanLimits.get_customer_limit('premium') is None

    def test_get_daily_search_limit(self):
        """検索回数上限を取得できること"""
        assert PlanLimits.get_daily_search_limit('basic') == 50
        assert PlanLimits.get_daily_search_limit('standard') == 500
        assert PlanLimits.get_daily_search_limit('premium') is None

    def test_is_subscription(self):
        """サブスクリプション型判定ができること"""
        assert PlanLimits.is_subscription('basic') is True
        assert PlanLimits.is_subscription('premium') is True
        assert PlanLimits.is_subscription('usage') is False
        assert PlanLimits.is_subscription('transaction') is False

class TestBillingService:
    """BillingServiceのテストクラス"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """テスト環境セットアップ"""
        os.environ['ENCRYPTION_KEY'] = CryptoManager.generate_key()
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            from app.models.logger import OperationLogger
            self.logger = OperationLogger()
            self.billing_service = BillingService(
                logger=self.logger
            )
            yield
            db.session.remove()
            db.drop_all()

    def test_check_customer_limit_within(self):
        """顧客登録件数が上限内の場合"""
        allowed, message = self.billing_service.check_customer_limit(
            user_id='testuser',
            plan='basic',
            current_count=50
        )
        assert allowed is True
        assert '残り50件' in message

    def test_check_customer_limit_reached(self):
        """顧客登録件数が上限に達した場合"""
        allowed, message = self.billing_service.check_customer_limit(
            user_id='testuser',
            plan='basic',
            current_count=100
        )
        assert allowed is False
        assert '上限（100件）' in message

    def test_check_customer_limit_premium_unlimited(self):
        """Premiumプランは無制限であること"""
        allowed, message = self.billing_service.check_customer_limit(
            user_id='testuser',
            plan='premium',
            current_count=9999
        )
        assert allowed is True

    def test_check_search_limit(self):
        """検索回数制限チェックが機能すること"""
        # 初回は許可される
        allowed, _ = self.billing_service.check_search_limit('testuser', 'basic')
        assert allowed is True

    def test_increment_search_count(self):
        """検索カウントがインクリメントされること"""
        count1 = self.billing_service.increment_search_count('testuser')
        count2 = self.billing_service.increment_search_count('testuser')
        count3 = self.billing_service.increment_search_count('testuser')

        assert count1 == 1
        assert count2 == 2
        assert count3 == 3

    def test_calculate_monthly_bill_basic(self):
        """Basicプランの月額請求計算"""
        bill = self.billing_service.calculate_monthly_bill(
            user_id='testuser',
            plan='basic',
            billing_period='2025-12'
        )

        assert bill['base_fee'] == 500
        assert bill['usage_fee'] == 0
        assert bill['total_fee'] == 500

    def test_calculate_monthly_bill_transaction(self):
        """トランザクションプランの請求計算"""
        # 操作ログを追加
        from app.models.logger import OperationLogger
        with self.app.app_context():
            self.logger.log('testuser', OperationLogger.OP_CUSTOMER_CREATE, target_id='CUS001')
            self.logger.log('testuser', OperationLogger.OP_CUSTOMER_CREATE, target_id='CUS002')
            self.logger.log('testuser', OperationLogger.OP_CUSTOMER_UPDATE, target_id='CUS001')
            self.logger.log('testuser', OperationLogger.OP_CUSTOMER_SEARCH, details='keyword=test')

            bill = self.billing_service.calculate_monthly_bill(
                user_id='testuser',
                plan='transaction',
                billing_period='2025-12'
            )

            # 登録2件×¥10 + 編集1件×¥5 + 検索1回×¥1 = ¥26
            assert bill['base_fee'] == 0
            assert bill['total_fee'] == 26

    def test_save_billing_record(self):
        """請求データを保存できること"""
        bill = {
            'user_id': 'testuser',
            'plan': 'basic',
            'billing_period': '2025-12',
            'base_fee': 500,
            'usage_fee': 0,
            'total_fee': 500,
            'details': ['月額プラン料金: ¥500']
        }

        with self.app.app_context():
            billing_id = self.billing_service.save_billing_record(bill)

            assert billing_id.startswith('BILL')

            # 履歴を確認
            history = self.billing_service.get_billing_history('testuser')
            assert len(history) == 1
            assert history[0]['total_fee'] == 500.0
