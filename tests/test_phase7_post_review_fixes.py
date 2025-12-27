import pytest
from flask.testing import FlaskCliRunner
from app import create_app, db
from app.models.user import User, UserRepository
from app.services.cancellation_service import CancellationService
from datetime import date, timedelta
import os

@pytest.fixture(autouse=True)
def setup_encryption_key():
    from app.models.crypto_manager import CryptoManager
    os.environ['ENCRYPTION_KEY'] = CryptoManager.generate_key()

@pytest.fixture
def app():
    app = create_app('testing')
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

def test_cleanup_accounts_command(app, runner):
    """CLIコマンド cleanup-accounts が正常に動作することを検証"""
    with app.app_context():
        # 準備: 期限切れの解約ユーザーを作成
        user_repo = UserRepository()
        user_id = "expired_user"
        
        # 31日前に解約されたユーザー（保持期限切れ）
        expired_date = (date.today() - timedelta(days=31)).isoformat()
        user = User(
            user_id=user_id,
            password_hash="hash",
            status='cancelled',
            data_retention_until=expired_date
        )
        user_repo.save(user)
        
        # 実行: CLIコマンド
        result = runner.invoke(args=['cleanup-accounts'])
        
        # 検証
        assert result.exit_code == 0
        assert "Cleanup completed. 1 accounts removed." in result.output
        
        # ユーザーが削除されていることを確認
        assert user_repo.find_by_id(user_id) is None

def test_plan_prices_externalization():
    """プラン価格がハードコードではなくクラス定数から取得されていることを検証"""
    from app.services.plan_change_service import PlanChangeService
    
    # 定数が定義されているか
    assert hasattr(PlanChangeService, 'PLAN_PRICES')
    assert PlanChangeService.PLAN_PRICES[User.PLAN_BASIC] == 500
    assert PlanChangeService.PLAN_PRICES[User.PLAN_STANDARD] == 1500
    assert PlanChangeService.PLAN_PRICES[User.PLAN_PREMIUM] == 3000
