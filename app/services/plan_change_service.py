"""
PlanChangeService: プラン変更管理サービス
"""
from typing import Optional, Tuple, List, Dict
from datetime import datetime, date
import calendar
from app.models.user import User, UserRepository
from app import db
from app.models.db_models import PlanChangeHistory as PlanChangeHistoryDB


class PlanChangeService:
    """プラン変更に関するビジネスロジックを担当するクラス (SQLAlchemy版)"""

    HISTORY_FIELDNAMES = [
        'history_id', 'user_id', 'change_type', 'old_plan', 'new_plan',
        'old_billing_type', 'new_billing_type', 'change_reason',
        'changed_by', 'prorated_amount', 'effective_date', 'created_at'
    ]

    # プラン別価格設定（limits.md準拠）
    PLAN_PRICES = {
        User.PLAN_BASIC: 500,
        User.PLAN_STANDARD: 1500,
        User.PLAN_PREMIUM: 3000
    }

    def __init__(
        self,
        user_repository: Optional[UserRepository] = None,
        logger: Optional[OperationLogger] = None,
        **kwargs
    ):
        self.user_repo = user_repository or UserRepository()
        self.logger = logger or OperationLogger()

    def can_change_plan(self, user_id: str, new_plan: str) -> Tuple[bool, str]:
        """プラン変更が可能かチェックする"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False, "ユーザーが見つかりません。"

        # 1. 変更頻度制限 (1ヶ月に1回)
        if user.last_plan_change_date:
            try:
                last_date = datetime.fromisoformat(user.last_plan_change_date).date()
                today = date.today()
                if last_date.year == today.year and last_date.month == today.month:
                    return False, "プラン変更は月に1回までです。来月以降に再度お試しください。"
            except ValueError:
                pass

        return True, ""

    def calculate_prorated_amount(self, old_plan: str, new_plan: str) -> float:
        """日割り計算額を算出"""
        old_price = self.PLAN_PRICES.get(old_plan, 0)
        new_price = self.PLAN_PRICES.get(new_plan, 0)
        
        if new_price <= old_price:
            return 0.0 # ダウングレード時は返金なし
            
        today = date.today()
        days_in_month = calendar.monthrange(today.year, today.month)[1]
        remaining_days = days_in_month - today.day
        
        diff = new_price - old_price
        prorated = (diff * remaining_days) / days_in_month
        return round(float(prorated), 2)

    def execute_plan_change(
        self,
        user_id: str,
        new_plan: str,
        new_billing_type: str,
        changed_by: str,
        reason: str = 'user_request'
    ) -> Tuple[bool, str]:
        """プラン変更を実行する"""
        can_change, message = self.can_change_plan(user_id, new_plan)
        if not can_change:
            return False, message

        user = self.user_repo.find_by_id(user_id)
        old_plan = user.plan
        old_billing_type = user.billing_type
        
        prorated_amount = self.calculate_prorated_amount(old_plan, new_plan)

        # ユーザー情報更新
        user.plan = new_plan
        user.billing_type = new_billing_type
        user.plan_change_count += 1
        user.last_plan_change_date = datetime.now().isoformat()
        
        self.user_repo.update(user)

        # 履歴記録
        last_pch = PlanChangeHistoryDB.query.order_by(PlanChangeHistoryDB.history_id.desc()).first()
        if last_pch:
            try:
                last_num = int(last_pch.history_id[3:])
                history_id = f"PCH{last_num + 1:04d}"
            except (ValueError, IndexError):
                history_id = f"PCH{datetime.now().strftime('%Y%m%d%H%M%S')}"
        else:
            history_id = "PCH0001"

        history_record = PlanChangeHistoryDB(
            history_id=history_id,
            user_id=user_id,
            change_type='upgrade' if prorated_amount > 0 else 'downgrade',
            old_plan=old_plan,
            new_plan=new_plan,
            old_billing_type=old_billing_type,
            new_billing_type=new_billing_type,
            change_reason=reason,
            changed_by=changed_by,
            prorated_amount=prorated_amount,
            effective_date=date.today().isoformat(),
            created_at=datetime.now().isoformat()
        )
        db.session.add(history_record)
        db.session.commit()

        self.logger.log(
            changed_by,
            "PLAN_CHANGE",
            target_id=user_id,
            details=f"{old_plan} -> {new_plan}, amount={prorated_amount}"
        )

        return True, "プランを変更しました。"
