"""
BillingService: 課金・制限管理サービス
顧客リスト管理システム - 課金ロジック
"""
from typing import Optional, Dict, Tuple
from datetime import datetime, date
from app.models.logger import OperationLogger
from app.models.csv_handler import CsvHandler


class PlanLimits:
    """
    プラン別の制限定義。
    limits.md に準拠。
    """

    # プラン名の定数
    PLAN_BASIC = 'basic'
    PLAN_STANDARD = 'standard'
    PLAN_PREMIUM = 'premium'
    PLAN_USAGE = 'usage'           # 従量課金型
    PLAN_TRANSACTION = 'transaction'  # トランザクション課金型
    PLAN_HYBRID = 'hybrid'         # ハイブリッド型

    # プラン定義
    PLANS = {
        PLAN_BASIC: {
            'name': 'Basic',
            'monthly_fee': 500,
            'customer_limit': 100,
            'search_limit_daily': 50,
            'billing_type': 'subscription'
        },
        PLAN_STANDARD: {
            'name': 'Standard',
            'monthly_fee': 1500,
            'customer_limit': 1000,
            'search_limit_daily': 500,
            'billing_type': 'subscription'
        },
        PLAN_PREMIUM: {
            'name': 'Premium',
            'monthly_fee': 3000,
            'customer_limit': None,  # 無制限
            'search_limit_daily': None,  # 無制限
            'billing_type': 'subscription'
        },
        PLAN_USAGE: {
            'name': '従量課金',
            'monthly_fee': 0,
            'customer_limit': None,
            'search_limit_daily': None,
            'billing_type': 'usage',
            'customer_rate': 200,      # 100件ごと
            'customer_unit': 100,
            'search_rate': 100,        # 100回ごと
            'search_unit': 100
        },
        PLAN_TRANSACTION: {
            'name': 'トランザクション',
            'monthly_fee': 0,
            'customer_limit': None,
            'search_limit_daily': None,
            'billing_type': 'transaction',
            'create_fee': 10,
            'update_fee': 5,
            'delete_fee': 0,
            'search_fee': 1
        },
        PLAN_HYBRID: {
            'name': 'ハイブリッド',
            'monthly_fee': 1000,
            'customer_limit': 500,
            'search_limit_daily': 200,
            'billing_type': 'hybrid',
            'customer_overage_rate': 500,  # 500件超過ごと
            'customer_overage_unit': 500,
            'search_overage_rate': 100,    # 100回ごと
            'search_overage_unit': 100
        }
    }

    @classmethod
    def get_plan(cls, plan_name: str) -> Optional[Dict]:
        """プラン情報を取得する"""
        return cls.PLANS.get(plan_name.lower())

    @classmethod
    def get_customer_limit(cls, plan_name: str) -> Optional[int]:
        """顧客登録件数上限を取得する（Noneは無制限）"""
        plan = cls.get_plan(plan_name)
        if plan:
            return plan.get('customer_limit')
        return 100  # デフォルトはBasic相当

    @classmethod
    def get_daily_search_limit(cls, plan_name: str) -> Optional[int]:
        """1日あたりの検索回数上限を取得する（Noneは無制限）"""
        plan = cls.get_plan(plan_name)
        if plan:
            return plan.get('search_limit_daily')
        return 50  # デフォルトはBasic相当

    @classmethod
    def is_subscription(cls, plan_name: str) -> bool:
        """サブスクリプション型かどうか"""
        plan = cls.get_plan(plan_name)
        return plan and plan.get('billing_type') == 'subscription'


class BillingService:
    """
    課金・制限管理サービス。
    プラン制限チェック、課金計算を担当。
    """

    BILLING_FIELDNAMES = [
        'billing_id',
        'user_id',
        'billing_period',
        'plan',
        'base_fee',
        'usage_fee',
        'total_fee',
        'details',
        'created_at'
    ]

    def __init__(
        self,
        logger: Optional[OperationLogger] = None,
        billing_csv_path: str = 'data/billing.csv'
    ):
        self.logger = logger or OperationLogger()
        self.billing_csv = CsvHandler(billing_csv_path, self.BILLING_FIELDNAMES)
        # 検索回数カウント用（メモリ内管理）
        self._daily_search_counts: Dict[str, Dict[str, int]] = {}

    def check_customer_limit(
        self,
        user_id: str,
        plan: str,
        current_count: int
    ) -> Tuple[bool, str]:
        """
        顧客登録件数制限をチェックする。

        Args:
            user_id: 利用者ID
            plan: プラン名
            current_count: 現在の顧客登録件数

        Returns:
            (制限内かどうか, メッセージ)
        """
        limit = PlanLimits.get_customer_limit(plan)

        if limit is None:
            return True, "登録可能です。"

        if current_count >= limit:
            return False, f"顧客登録件数が上限（{limit}件）に達しています。プランのアップグレードをご検討ください。"

        remaining = limit - current_count
        return True, f"残り{remaining}件登録可能です。"

    def check_search_limit(
        self,
        user_id: str,
        plan: str
    ) -> Tuple[bool, str]:
        """
        検索回数制限をチェックする。

        Args:
            user_id: 利用者ID
            plan: プラン名

        Returns:
            (制限内かどうか, メッセージ)
        """
        limit = PlanLimits.get_daily_search_limit(plan)

        if limit is None:
            return True, "検索可能です。"

        today = date.today().isoformat()
        count = self._get_daily_search_count(user_id, today)

        if count >= limit:
            return False, f"本日の検索回数が上限（{limit}回）に達しています。明日以降に再度お試しください。"

        remaining = limit - count
        return True, f"本日残り{remaining}回検索可能です。"

    def increment_search_count(self, user_id: str) -> int:
        """
        検索回数をインクリメントする。

        Args:
            user_id: 利用者ID

        Returns:
            更新後のカウント
        """
        today = date.today().isoformat()
        if today not in self._daily_search_counts:
            self._daily_search_counts[today] = {}

        current = self._daily_search_counts[today].get(user_id, 0)
        self._daily_search_counts[today][user_id] = current + 1
        return current + 1

    def _get_daily_search_count(self, user_id: str, date_str: str) -> int:
        """日別の検索回数を取得する"""
        if date_str not in self._daily_search_counts:
            return 0
        return self._daily_search_counts[date_str].get(user_id, 0)

    def calculate_monthly_bill(
        self,
        user_id: str,
        plan: str,
        billing_period: str
    ) -> Dict:
        """
        月額請求を計算する。

        Args:
            user_id: 利用者ID
            plan: プラン名
            billing_period: 請求期間（YYYY-MM形式）

        Returns:
            請求明細の辞書
        """
        plan_info = PlanLimits.get_plan(plan)
        if not plan_info:
            plan_info = PlanLimits.get_plan(PlanLimits.PLAN_BASIC)

        billing_type = plan_info.get('billing_type', 'subscription')
        base_fee = plan_info.get('monthly_fee', 0)
        usage_fee = 0
        details = []

        if billing_type == 'subscription':
            # サブスクリプション型：固定月額のみ
            details.append(f"月額プラン料金: ¥{base_fee}")

        elif billing_type == 'usage':
            # 従量課金型
            # 顧客登録件数に基づく課金
            customer_count = self._count_operations_in_period(
                user_id, OperationLogger.OP_CUSTOMER_CREATE, billing_period
            )
            customer_unit = plan_info.get('customer_unit', 100)
            customer_rate = plan_info.get('customer_rate', 200)
            customer_fee = (customer_count // customer_unit) * customer_rate
            usage_fee += customer_fee
            details.append(f"顧客登録 {customer_count}件: ¥{customer_fee}")

            # 検索回数に基づく課金
            search_count = self._count_operations_in_period(
                user_id, OperationLogger.OP_CUSTOMER_SEARCH, billing_period
            )
            search_unit = plan_info.get('search_unit', 100)
            search_rate = plan_info.get('search_rate', 100)
            search_fee = (search_count // search_unit) * search_rate
            usage_fee += search_fee
            details.append(f"検索 {search_count}回: ¥{search_fee}")

        elif billing_type == 'transaction':
            # トランザクション型
            create_count = self._count_operations_in_period(
                user_id, OperationLogger.OP_CUSTOMER_CREATE, billing_period
            )
            create_fee = create_count * plan_info.get('create_fee', 10)
            usage_fee += create_fee
            details.append(f"顧客登録 {create_count}件 × ¥10: ¥{create_fee}")

            update_count = self._count_operations_in_period(
                user_id, OperationLogger.OP_CUSTOMER_UPDATE, billing_period
            )
            update_fee = update_count * plan_info.get('update_fee', 5)
            usage_fee += update_fee
            details.append(f"顧客編集 {update_count}件 × ¥5: ¥{update_fee}")

            search_count = self._count_operations_in_period(
                user_id, OperationLogger.OP_CUSTOMER_SEARCH, billing_period
            )
            search_fee = search_count * plan_info.get('search_fee', 1)
            usage_fee += search_fee
            details.append(f"検索 {search_count}回 × ¥1: ¥{search_fee}")

        elif billing_type == 'hybrid':
            # ハイブリッド型
            details.append(f"基本料金: ¥{base_fee}")

            # 顧客件数超過分
            customer_count = self._count_operations_in_period(
                user_id, OperationLogger.OP_CUSTOMER_CREATE, billing_period
            )
            customer_limit = plan_info.get('customer_limit', 500)
            if customer_count > customer_limit:
                overage = customer_count - customer_limit
                overage_unit = plan_info.get('customer_overage_unit', 500)
                overage_rate = plan_info.get('customer_overage_rate', 500)
                overage_fee = ((overage + overage_unit - 1) // overage_unit) * overage_rate
                usage_fee += overage_fee
                details.append(f"顧客超過 {overage}件: ¥{overage_fee}")

            # 検索回数超過分（月間累計で計算）
            search_count = self._count_operations_in_period(
                user_id, OperationLogger.OP_CUSTOMER_SEARCH, billing_period
            )
            # ハイブリッドは日別制限だが、月末に超過分を課金
            search_limit = plan_info.get('search_limit_daily', 200) * 30  # 概算
            if search_count > search_limit:
                overage = search_count - search_limit
                overage_unit = plan_info.get('search_overage_unit', 100)
                overage_rate = plan_info.get('search_overage_rate', 100)
                overage_fee = ((overage + overage_unit - 1) // overage_unit) * overage_rate
                usage_fee += overage_fee
                details.append(f"検索超過 {overage}回: ¥{overage_fee}")

        total_fee = base_fee + usage_fee

        return {
            'user_id': user_id,
            'plan': plan,
            'billing_period': billing_period,
            'base_fee': base_fee,
            'usage_fee': usage_fee,
            'total_fee': total_fee,
            'details': details
        }

    def save_billing_record(self, billing_data: Dict) -> str:
        """
        請求データを保存する。

        Args:
            billing_data: 請求データ

        Returns:
            請求ID
        """
        billing_id = self.billing_csv.generate_next_id('billing_id', 'BILL')

        record = {
            'billing_id': billing_id,
            'user_id': billing_data['user_id'],
            'billing_period': billing_data['billing_period'],
            'plan': billing_data['plan'],
            'base_fee': str(billing_data['base_fee']),
            'usage_fee': str(billing_data['usage_fee']),
            'total_fee': str(billing_data['total_fee']),
            'details': '; '.join(billing_data.get('details', [])),
            'created_at': datetime.now().isoformat()
        }

        self.billing_csv.add_record(record)
        return billing_id

    def get_billing_history(self, user_id: str) -> list:
        """利用者の請求履歴を取得する"""
        all_records = self.billing_csv.read_all()
        return [r for r in all_records if r.get('user_id') == user_id]

    def _count_operations_in_period(
        self,
        user_id: str,
        operation: str,
        period: str
    ) -> int:
        """
        指定期間内の操作回数をカウントする。

        Args:
            user_id: 利用者ID
            operation: 操作種別
            period: 期間（YYYY-MM形式）

        Returns:
            操作回数
        """
        all_logs = self.logger.csv_handler.read_all()
        count = 0
        for log in all_logs:
            if log.get('user_id') != user_id:
                continue
            if log.get('operation') != operation:
                continue
            created_at = log.get('created_at', '')
            if created_at.startswith(period):
                count += 1
        return count


def limit_check_required(check_type: str):
    """
    制限チェック用デコレータ。

    Args:
        check_type: 'customer' または 'search'
    """
    from functools import wraps
    from flask import session, flash, redirect, url_for, current_app

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = session.get('user_id')
            plan = session.get('plan', 'basic')

            billing_service = BillingService()

            if check_type == 'customer':
                from app.services.customer_service import CustomerService
                customer_service = CustomerService()
                current_count = customer_service.get_customer_count()

                allowed, message = billing_service.check_customer_limit(
                    user_id, plan, current_count
                )
                if not allowed:
                    flash(message, 'warning')
                    return redirect(url_for('customer.customer_list'))

            elif check_type == 'search':
                allowed, message = billing_service.check_search_limit(user_id, plan)
                if not allowed:
                    flash(message, 'warning')
                    return redirect(url_for('customer.customer_list'))

                # 検索カウントをインクリメント
                billing_service.increment_search_count(user_id)

            return f(*args, **kwargs)
        return decorated_function
    return decorator
