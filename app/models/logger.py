"""
Logger: 操作ログ記録クラス
顧客リスト管理システム - 共通モジュール
"""
import os
from datetime import datetime
from typing import Optional
from app.models.csv_handler import CsvHandler


class OperationLogger:
    """
    利用者の操作ログを記録するクラス。
    課金計算の根拠となるため、確実なログ保存が求められる。
    """

    LOG_FIELDNAMES = [
        'log_id',
        'user_id',
        'operation',
        'target_id',
        'details',
        'created_at'
    ]

    # 操作種別の定数
    OP_LOGIN = 'login'
    OP_LOGOUT = 'logout'
    OP_CUSTOMER_CREATE = 'customer_create'
    OP_CUSTOMER_READ = 'customer_read'
    OP_CUSTOMER_UPDATE = 'customer_update'
    OP_CUSTOMER_DELETE = 'customer_delete'
    OP_CUSTOMER_SEARCH = 'customer_search'
    OP_USER_CREATE = 'user_create'
    OP_USER_DELETE = 'user_delete'

    def __init__(self, log_file_path: str = 'data/logs.csv'):
        """
        OperationLoggerを初期化する。

        Args:
            log_file_path: ログファイルのパス
        """
        self.csv_handler = CsvHandler(log_file_path, self.LOG_FIELDNAMES)

    def log(
        self,
        user_id: str,
        operation: str,
        target_id: Optional[str] = None,
        details: Optional[str] = None
    ) -> str:
        """
        操作ログを記録する。

        Args:
            user_id: 操作を行った利用者ID
            operation: 操作種別（OP_* 定数を使用）
            target_id: 操作対象のID（顧客ID等）
            details: 追加の詳細情報

        Returns:
            記録されたログID
        """
        log_id = self.csv_handler.generate_next_id('log_id', 'LOG')
        timestamp = datetime.now().isoformat()

        record = {
            'log_id': log_id,
            'user_id': user_id,
            'operation': operation,
            'target_id': target_id or '',
            'details': details or '',
            'created_at': timestamp
        }

        self.csv_handler.add_record(record)
        return log_id

    def get_logs_by_user(self, user_id: str) -> list:
        """
        指定した利用者のログを取得する。

        Args:
            user_id: 利用者ID

        Returns:
            ログレコードのリスト
        """
        all_logs = self.csv_handler.read_all()
        return [log for log in all_logs if log.get('user_id') == user_id]

    def get_logs_by_operation(self, operation: str) -> list:
        """
        指定した操作種別のログを取得する。

        Args:
            operation: 操作種別

        Returns:
            ログレコードのリスト
        """
        all_logs = self.csv_handler.read_all()
        return [log for log in all_logs if log.get('operation') == operation]

    def get_logs_by_date_range(self, start_date: str, end_date: str) -> list:
        """
        指定した日付範囲のログを取得する。

        Args:
            start_date: 開始日（ISO8601形式）
            end_date: 終了日（ISO8601形式）

        Returns:
            ログレコードのリスト
        """
        all_logs = self.csv_handler.read_all()
        filtered = []
        for log in all_logs:
            created_at = log.get('created_at', '')
            if start_date <= created_at <= end_date:
                filtered.append(log)
        return filtered

    def count_operations(self, user_id: str, operation: str, date: Optional[str] = None) -> int:
        """
        特定の利用者の操作回数をカウントする（課金計算用）。

        Args:
            user_id: 利用者ID
            operation: 操作種別
            date: 対象日（YYYY-MM-DD形式、Noneの場合は全期間）

        Returns:
            操作回数
        """
        all_logs = self.csv_handler.read_all()
        count = 0
        for log in all_logs:
            if log.get('user_id') != user_id:
                continue
            if log.get('operation') != operation:
                continue
            if date:
                log_date = log.get('created_at', '')[:10]  # YYYY-MM-DD部分を取得
                if log_date != date:
                    continue
            count += 1
        return count
