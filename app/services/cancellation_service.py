"""
CancellationService: 解約管理サービス
"""
from typing import Optional, Tuple, List, Dict
from datetime import datetime, date, timedelta
from app.models.user import User, UserRepository
from app import db
from app.models.db_models import CancellationHistory as CancellationHistoryDB


class CancellationService:
    """解約・データ保持期間管理を担当するクラス (SQLAlchemy版)"""

    HISTORY_FIELDNAMES = [
        'cancellation_id', 'user_id', 'cancellation_type', 'cancellation_reason',
        'cancellation_comment', 'cancelled_by', 'is_forced', 'plan_at_cancellation',
        'requested_date', 'effective_date', 'data_retention_until', 'created_at'
    ]

    def __init__(
        self,
        user_repository: Optional[UserRepository] = None,
        customer_service: Optional[CustomerService] = None,
        logger: Optional[OperationLogger] = None,
        **kwargs
    ):
        self.user_repo = user_repository or UserRepository()
        self.customer_service = customer_service or CustomerService()
        self.logger = logger or OperationLogger()

    def execute_cancellation(
        self,
        user_id: str,
        cancellation_type: str,
        reason: str,
        comment: str,
        cancelled_by: str,
        is_forced: bool = False
    ) -> Tuple[bool, str]:
        """解約を実行する"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False, "ユーザーが見つかりません。"

        if user.status == 'cancelled':
            return False, "このアカウントは既に解約されています。"

        # 解約日の決定
        requested_date = date.today()
        effective_date = requested_date
        data_retention_until = effective_date + timedelta(days=30)

        # ユーザー情報更新
        user.status = 'cancelled'
        user.cancellation_date = effective_date.isoformat()
        user.data_retention_until = data_retention_until.isoformat()
        self.user_repo.update(user)

        # 履歴記録
        last_can = CancellationHistoryDB.query.order_by(CancellationHistoryDB.cancellation_id.desc()).first()
        if last_can:
            try:
                last_num = int(last_can.cancellation_id[3:])
                can_id = f"CAN{last_num + 1:04d}"
            except (ValueError, IndexError):
                can_id = f"CAN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        else:
            can_id = "CAN0001"

        history_record = CancellationHistoryDB(
            cancellation_id=can_id,
            user_id=user_id,
            cancellation_type=cancellation_type,
            cancellation_reason=reason,
            cancellation_comment=comment,
            cancelled_by=cancelled_by,
            is_forced=is_forced,
            plan_at_cancellation=user.plan,
            requested_date=requested_date.isoformat(),
            effective_date=effective_date.isoformat(),
            data_retention_until=data_retention_until.isoformat(),
            created_at=datetime.now().isoformat()
        )
        db.session.add(history_record)
        db.session.commit()

        self.logger.log(
            cancelled_by,
            "CANCELLATION",
            target_id=user_id,
            details=f"type={cancellation_type}, reason={reason}"
        )

        return True, "解約手続きが完了しました。"

    def reactivate_account(self, user_id: str) -> Tuple[bool, str]:
        """解約を撤回（再有効化）する（データ保持期間内のみ）"""
        user = self.user_repo.find_by_id(user_id)
        if not user or user.status != 'cancelled':
            return False, "解約済みのユーザーが見つかりません。"

        retention_date = date.fromisoformat(user.data_retention_until)
        if retention_date < date.today():
            return False, "データ保持期限が切れているため、再有効化できません。"

        # 復帰処理
        user.status = 'active'
        user.cancellation_date = ''
        user.data_retention_until = ''
        self.user_repo.update(user)

        self.logger.log(user_id, "ACCOUNT_REACTIVATE")
        return True, "アカウントを再有効化しました。"

    def cleanup_expired_accounts(self) -> int:
        """保持期限切れアカウントのデータを物理削除する"""
        today = date.today().isoformat()
        users = self.user_repo.find_all()
        count = 0
        
        for user in users:
            if user.status == 'cancelled' and user.data_retention_until:
                if user.data_retention_until < today:
                    # 1. 顧客データ削除
                    self.customer_service.delete_customers_by_user(user.user_id)
                    # 2. ユーザー削除
                    self.user_repo.delete(user.user_id)
                    count += 1
                    self.logger.log("SYSTEM", "ACCOUNT_CLEANUP", target_id=user.user_id)
        
        return count
