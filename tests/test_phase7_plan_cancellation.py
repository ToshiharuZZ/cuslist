import pytest
import os
from datetime import date
from app.models.user import User, UserRepository
from app.services.auth_service import AuthService
from app.services.plan_change_service import PlanChangeService
from app.services.cancellation_service import CancellationService

@pytest.fixture(autouse=True)
def setup_encryption_key():
    from app.models.crypto_manager import CryptoManager
    os.environ['ENCRYPTION_KEY'] = CryptoManager.generate_key()

@pytest.fixture
def user_repo(tmp_path):
    csv_path = tmp_path / "users.csv"
    return UserRepository(str(csv_path))

@pytest.fixture
def auth_service(user_repo):
    return AuthService(user_repository=user_repo)

@pytest.fixture
def plan_service(user_repo, tmp_path):
    history_csv = tmp_path / "plan_history.csv"
    return PlanChangeService(user_repository=user_repo, history_csv_path=str(history_csv))

@pytest.fixture
def cancel_service(user_repo, tmp_path):
    history_csv = tmp_path / "cancel_history.csv"
    return CancellationService(user_repository=user_repo, history_csv_path=str(history_csv))

def test_login_blocked_for_cancelled_user(auth_service, user_repo):
    """解約済みユーザーがログインできないことを検証"""
    user_id = "cancelled_user"
    password = "password123"
    from app.models.crypto_manager import CryptoManager
    user = User(
        user_id=user_id,
        password_hash=CryptoManager.create_password_hash(password),
        status='cancelled'
    )
    user_repo.save(user)
    
    success, authenticated_user, message = auth_service.authenticate(user_id, password)
    
    assert success is False
    assert "解約済み" in message

def test_execute_plan_change_success(plan_service, user_repo):
    """プラン変更が正常に実行され、履歴が保存されることを検証"""
    user_id = "test_user"
    user = User(user_id=user_id, password_hash="hash", plan=User.PLAN_BASIC)
    user_repo.save(user)
    
    success, message = plan_service.execute_plan_change(
        user_id=user_id,
        new_plan=User.PLAN_STANDARD,
        new_billing_type=User.BILLING_SUBSCRIPTION,
        changed_by=user_id
    )
    
    assert success is True
    updated_user = user_repo.find_by_id(user_id)
    assert updated_user.plan == User.PLAN_STANDARD
    assert updated_user.plan_change_count == 1
    
    # 履歴確認
    history = plan_service.history_handler.read_all()
    assert len(history) == 1
    assert history[0]['new_plan'] == User.PLAN_STANDARD

def test_execute_cancellation_success(cancel_service, user_repo):
    """解約が正常に実行され、ステータスが更新されることを検証"""
    user_id = "cancel_user"
    user = User(user_id=user_id, password_hash="hash", status='active')
    user_repo.save(user)
    
    success, message = cancel_service.execute_cancellation(
        user_id=user_id,
        cancellation_type='immediate',
        reason='cost',
        comment='too expensive',
        cancelled_by=user_id
    )
    
    assert success is True
    updated_user = user_repo.find_by_id(user_id)
    assert updated_user.status == 'cancelled'
    assert updated_user.cancellation_date == date.today().isoformat()
    
    # 履歴確認
    history = cancel_service.history_handler.read_all()
    assert len(history) == 1
    assert history[0]['cancellation_reason'] == 'cost'
