"""
Logger: 操作ログ記録クラス
顧客リスト管理システム - 共通モジュール
"""
from datetime import datetime
from typing import Optional
from app import db
from app.models.db_models import OperationLog as OperationLogDB


class OperationLogger:
    """
    利用者の操作ログを記録するクラス (SQLAlchemy版)。
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

    def __init__(self, **kwargs):
        # 互換性のために引数は受け取るが使用しない
        pass

    def log(
        self,
        user_id: str,
        operation: str,
        target_id: Optional[str] = None,
        details: Optional[str] = None
    ) -> str:
        """
        操作ログを記録する。
        """
        # ID採番 (LOGxxxx)
        last_log = OperationLogDB.query.order_by(OperationLogDB.log_id.desc()).first()
        if last_log:
            try:
                last_num = int(last_log.log_id[3:])
                log_id = f"LOG{last_num + 1:04d}"
            except (ValueError, IndexError):
                log_id = f"LOG{datetime.now().strftime('%Y%m%d%H%M%S')}"
        else:
            log_id = "LOG0001"

        record = OperationLogDB(
            log_id=log_id,
            user_id=user_id,
            operation=operation,
            target_id=target_id or '',
            details=details or '',
            created_at=datetime.now().isoformat()
        )

        db.session.add(record)
        db.session.commit()
        return log_id

    def get_logs_by_user(self, user_id: str) -> list:
        """
        指定した利用者のログを取得する。
        """
        records = OperationLogDB.query.filter_by(user_id=user_id).all()
        return [r.to_dict() for r in records]

    def get_logs_by_operation(self, operation: str) -> list:
        """
        指定した操作種別のログを取得する。
        """
        records = OperationLogDB.query.filter_by(operation=operation).all()
        return [r.to_dict() for r in records]

    def get_logs_by_date_range(self, start_date: str, end_date: str) -> list:
        """
        指定した日付範囲のログを取得する。
        """
        records = OperationLogDB.query.filter(
            OperationLogDB.created_at >= start_date,
            OperationLogDB.created_at <= end_date
        ).all()
        return [r.to_dict() for r in records]

    def count_operations(self, user_id: str, operation: str, date: Optional[str] = None) -> int:
        """
        特定の利用者の操作回数をカウントする（課金計算用）。
        """
        query = OperationLogDB.query.filter_by(user_id=user_id, operation=operation)
        if date:
            query = query.filter(OperationLogDB.created_at.like(f"{date}%"))
        return query.count()
