"""
OperationLogger 単体テスト
"""
import os
import pytest
import tempfile
import shutil
from app.models.logger import OperationLogger


class TestOperationLogger:
    """OperationLoggerのテストクラス"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前にテンポラリディレクトリを作成"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'logs.csv')
        yield
        # テスト後にクリーンアップ
        shutil.rmtree(self.test_dir)

    def test_log_operation(self):
        """操作ログを記録できること"""
        logger = OperationLogger(self.test_file)

        log_id = logger.log(
            user_id='USER001',
            operation=OperationLogger.OP_CUSTOMER_CREATE,
            target_id='CUS001',
            details='新規顧客登録'
        )

        assert log_id.startswith('LOG')

        logs = logger.csv_handler.read_all()
        assert len(logs) == 1
        assert logs[0]['user_id'] == 'USER001'
        assert logs[0]['operation'] == 'customer_create'

    def test_get_logs_by_user(self):
        """利用者IDでログを取得できること"""
        logger = OperationLogger(self.test_file)

        logger.log('USER001', OperationLogger.OP_LOGIN)
        logger.log('USER002', OperationLogger.OP_LOGIN)
        logger.log('USER001', OperationLogger.OP_CUSTOMER_CREATE, 'CUS001')

        user1_logs = logger.get_logs_by_user('USER001')
        assert len(user1_logs) == 2

        user2_logs = logger.get_logs_by_user('USER002')
        assert len(user2_logs) == 1

    def test_get_logs_by_operation(self):
        """操作種別でログを取得できること"""
        logger = OperationLogger(self.test_file)

        logger.log('USER001', OperationLogger.OP_LOGIN)
        logger.log('USER001', OperationLogger.OP_CUSTOMER_CREATE, 'CUS001')
        logger.log('USER001', OperationLogger.OP_CUSTOMER_CREATE, 'CUS002')

        login_logs = logger.get_logs_by_operation(OperationLogger.OP_LOGIN)
        assert len(login_logs) == 1

        create_logs = logger.get_logs_by_operation(OperationLogger.OP_CUSTOMER_CREATE)
        assert len(create_logs) == 2

    def test_count_operations(self):
        """操作回数をカウントできること"""
        logger = OperationLogger(self.test_file)

        logger.log('USER001', OperationLogger.OP_CUSTOMER_SEARCH)
        logger.log('USER001', OperationLogger.OP_CUSTOMER_SEARCH)
        logger.log('USER001', OperationLogger.OP_CUSTOMER_SEARCH)
        logger.log('USER002', OperationLogger.OP_CUSTOMER_SEARCH)

        count = logger.count_operations('USER001', OperationLogger.OP_CUSTOMER_SEARCH)
        assert count == 3

        count_user2 = logger.count_operations('USER002', OperationLogger.OP_CUSTOMER_SEARCH)
        assert count_user2 == 1
