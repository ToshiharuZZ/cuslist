"""
OperationLogger 単体テスト
"""
import os
import pytest
from app import create_app, db
from app.models.logger import OperationLogger

class TestOperationLogger:
    """OperationLoggerのテストクラス"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """テスト環境セットアップ"""
        self.app = create_app('testing')
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self.logger = OperationLogger()
            yield
            db.session.remove()
            db.drop_all()

    def test_log_operation(self):
        """操作ログを記録できること"""
        with self.app.app_context():
            log_id = self.logger.log(
                user_id='USER001',
                operation=OperationLogger.OP_CUSTOMER_CREATE,
                target_id='CUS001',
                details='新規顧客登録'
            )

            assert log_id.startswith('LOG')

            logs = self.logger.get_logs_by_user('USER001')
            assert len(logs) == 1
            assert logs[0]['user_id'] == 'USER001'
            assert logs[0]['operation'] == 'customer_create'

    def test_get_logs_by_user(self):
        """利用者IDでログを取得できること"""
        with self.app.app_context():
            self.logger.log('USER001', OperationLogger.OP_LOGIN)
            self.logger.log('USER002', OperationLogger.OP_LOGIN)
            self.logger.log('USER001', OperationLogger.OP_CUSTOMER_CREATE, 'CUS001')

            user1_logs = self.logger.get_logs_by_user('USER001')
            assert len(user1_logs) == 2

            user2_logs = self.logger.get_logs_by_user('USER002')
            assert len(user2_logs) == 1

    def test_get_logs_by_operation(self):
        """操作種別でログを取得できること"""
        with self.app.app_context():
            self.logger.log('USER001', OperationLogger.OP_LOGIN)
            self.logger.log('USER001', OperationLogger.OP_CUSTOMER_CREATE, 'CUS001')
            self.logger.log('USER001', OperationLogger.OP_CUSTOMER_CREATE, 'CUS002')

            login_logs = self.logger.get_logs_by_operation(OperationLogger.OP_LOGIN)
            assert len(login_logs) == 1

            create_logs = self.logger.get_logs_by_operation(OperationLogger.OP_CUSTOMER_CREATE)
            assert len(create_logs) == 2

    def test_count_operations(self):
        """操作回数をカウントできること"""
        with self.app.app_context():
            self.logger.log('USER001', OperationLogger.OP_CUSTOMER_SEARCH)
            self.logger.log('USER001', OperationLogger.OP_CUSTOMER_SEARCH)
            self.logger.log('USER001', OperationLogger.OP_CUSTOMER_SEARCH)
            self.logger.log('USER002', OperationLogger.OP_CUSTOMER_SEARCH)

            count = self.logger.count_operations('USER001', OperationLogger.OP_CUSTOMER_SEARCH)
            assert count == 3

            count_user2 = self.logger.count_operations('USER002', OperationLogger.OP_CUSTOMER_SEARCH)
            assert count_user2 == 1
