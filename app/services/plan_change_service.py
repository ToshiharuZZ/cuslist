"""
PlanChangeService: プラン変更管理サービス
"""
from typing import Optional, Tuple, List, Dict
from datetime import datetime, date
import calendar
from app.models.user import User, UserRepository
from app.models.csv_handler import CsvHandler
from app.models.logger import OperationLogger

class PlanChangeService:
    """プラン変更に関するビジネスロジックを担当するクラス"""

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
        history_csv_path: str = 'data/plan_change_history.csv'
    ):
        self.user_repo = user_repository or UserRepository()
        self.logger = logger or OperationLogger()
        self.history_handler = CsvHandler(history_csv_path, self.HISTORY_FIELDNAMES)

    def can_change_plan(self, user_id: str, new_plan: str) -> Tuple[bool, str]:
        """プラン変更が可能かチェックする"""
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return False, "ユーザーが見つかりません。"

        # 1. 変更頻度制限 (1ヶ月に1回)
        # 簡易チェック: last_plan_change_date が今月ならNG
        if user.last_plan_change_date:
            last_date = datetime.fromisoformat(user.last_plan_change_date).date()
            today = date.today()
            if last_date.year == today.year and last_date.month == today.month:
                return False, "プラン変更は月に1回までです。来月以降に再度お試しください。"

        # 2. ダウングレード時の顧客数チェック
        # TODO: 各プランの上限値を取得して比較
        
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
        return round(prorated, 2)

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
        history_id = self.history_handler.generate_next_id('history_id', 'PCH')
        history_record = {
            'history_id': history_id,
            'user_id': user_id,
            'change_type': 'upgrade' if prorated_amount > 0 else 'downgrade',
            'old_plan': old_plan,
            'new_plan': new_plan,
            'old_billing_type': old_billing_type,
            'new_billing_type': new_billing_type,
            'change_reason': reason,
            'changed_by': changed_by,
            'prorated_amount': str(prorated_amount),
            'effective_date': date.today().isoformat(),
            'created_at': datetime.now().isoformat()
        }
        self.history_handler.add_record(history_record)

        self.logger.log(
            changed_by,
            "PLAN_CHANGE",
            target_id=user_id,
            details=f"{old_plan} -> {new_plan}, amount={prorated_amount}"
        )

        return True, "プランを変更しました。"
