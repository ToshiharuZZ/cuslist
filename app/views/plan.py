"""
プラン変更・解約関連のビュー
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.views.auth import login_required
from app.services.plan_change_service import PlanChangeService
from app.services.cancellation_service import CancellationService
from app.models.user import User

plan_bp = Blueprint('plan', __name__)
plan_service = PlanChangeService()
cancel_service = CancellationService()

@plan_bp.route('/change', methods=['GET', 'POST'])
@login_required
def change_plan():
    """プラン変更画面"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        new_plan = request.form.get('plan')
        new_billing_type = request.form.get('billing_type', User.BILLING_SUBSCRIPTION)
        
        success, message = plan_service.execute_plan_change(
            user_id=user_id,
            new_plan=new_plan,
            new_billing_type=new_billing_type,
            changed_by=user_id
        )
        
        if success:
            session['plan'] = new_plan # セッション更新
            flash(message, 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash(message, 'danger')

    return render_template('plan/change.html')

@plan_bp.route('/history')
@login_required
def history():
    """プラン変更履歴"""
    user_id = session.get('user_id')
    # 履歴取得ロジックの実装が必要
    records = [r for r in plan_service.history_handler.read_all() if r['user_id'] == user_id]
    return render_template('plan/history.html', records=records)

@plan_bp.route('/cancel', methods=['GET', 'POST'])
@login_required
def cancel_account():
    """解約申請画面"""
    user_id = session.get('user_id')
    
    if request.method == 'POST':
        cancellation_type = request.form.get('cancellation_type', 'immediate')
        reason = request.form.get('reason')
        comment = request.form.get('comment', '')
        
        success, message = cancel_service.execute_cancellation(
            user_id=user_id,
            cancellation_type=cancellation_type,
            reason=reason,
            comment=comment,
            cancelled_by=user_id
        )
        
        if success:
            flash(message, 'warning')
            return redirect(url_for('auth.logout'))
        else:
            flash(message, 'danger')

    return render_template('plan/cancel.html')
