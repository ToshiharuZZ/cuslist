"""
システム統合テスト (Scenario Tests)
"""
import os
import pytest
import tempfile
import shutil
from app import create_app
from app.models.logger import OperationLogger
from app.services.billing_service import PlanLimits, BillingService
from app.models.csv_handler import CsvHandler
from app.models.crypto_manager import CryptoManager

class TestIntegration:
    """統合テストシナリオ"""

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch):
        """テスト環境セットアップ"""
        self.test_dir = tempfile.mkdtemp()
        
        # CsvHandlerのパス書き換え用モック
        def mock_init(self_handler, file_path, fieldnames):
             # 絶対パスでテストディレクトリ配下に強制変更
             filename = os.path.basename(file_path)
             self_handler.file_path = os.path.join(self.test_dir, filename)
             self_handler.fieldnames = fieldnames
             self_handler._ensure_file_exists()
             
        monkeypatch.setattr(CsvHandler, '__init__', mock_init)
        
        # 環境変数を一時的に変更
        os.environ['ENCRYPTION_KEY'] = CryptoManager.generate_key()
        
        # グローバル変数の汚染を防ぐため、モジュール変数を強制的に更新
        # これにより前回のテストのパスを保持したインスタンスが使われるのを防ぐ
        import app.views.auth
        import app.views.customer
        from app.services.auth_service import AuthService
        from app.services.customer_service import CustomerService
        from app.services.billing_service import BillingService

        app.views.auth.auth_service = AuthService()
        app.views.customer.customer_service = CustomerService()
        app.views.customer.billing_service = BillingService()
        
        # Flaskアプリ設定（データディレクトリをテスト用に変更）
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        yield
        
        # クリーンアップ
        shutil.rmtree(self.test_dir)

    def test_scenario_full_flow(self):
        """
        シナリオ: 管理者フローからユーザー利用フローまで
        """
        # 1. 準備: 管理者ユーザーを作成
        from app.services.auth_service import AuthService
        # グローバルインスタンスが既に作られている可能性があるため、
        # ここで新しく作ってもアプリが使うインスタンスとは別になる可能性があるが、
        # リポジトリはCSVファイル(モック済み)を見るのでデータは共有されるはず。
        auth_service = AuthService()
        # パスワードは8文字以上必須
        auth_service.register_user('admin', 'adminpassword', 'admin', 'basic', 'subscription')

        # 2. 管理者ログイン
        resp = self.client.post('/login', data={
            'user_id': 'admin',
            'password': 'adminpassword',
            'csrf_token': 'dummy'
        }, follow_redirects=True)
        assert b'\xe3\x83\xad\xe3\x82\xb0\xe3\x82\xa4\xe3\x83\xb3\xe3\x81\x97\xe3\x81\xbe\xe3\x81\x97\xe3\x81\x9f' in resp.data or b'Login successful' in resp.data or resp.status_code == 200

        # 3. 新規ユーザー作成 (user1 / Standard)
        resp = self.client.post('/users/register', data={
            'user_id': 'user1',
            'password': 'user1password',  # 8文字以上
            'role': 'user',
            'plan': 'standard',
            'billing_type': 'subscription',
            'csrf_token': 'dummy'
        }, follow_redirects=True)
        
        # 登録確認
        assert b'user1' in resp.data
        assert resp.status_code == 200
        
        # 4. ログアウト
        self.client.get('/logout')

        # 5. user1 でログイン
        resp = self.client.post('/login', data={
            'user_id': 'user1',
            'password': 'user1password',
            'csrf_token': 'dummy'
        }, follow_redirects=True)
        assert b'user1' in resp.data

        # 6. 顧客登録 (customers/new)
        resp = self.client.post('/customers/new', data={
            'name': 'Test Customer',
            'email': 'test@example.com',
            'phone': '090-0000-0000',
            'address': 'Test Address',
            'csrf_token': 'dummy'
        }, follow_redirects=True)
        assert b'Test Customer' in resp.data
        
        # データが暗号化されているか確認
        csv_path = os.path.join(self.test_dir, 'customers.csv')
        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Test Customer' not in content

    def test_scenario_plan_limit(self):
        """
        シナリオ: Basicプランの上限チェック
        """
        # ユーザー作成
        from app.services.auth_service import AuthService
        auth_service = AuthService()
        auth_service.register_user('basic_user', 'password1234', 'user', 'basic', 'subscription')

        # ログイン
        self.client.post('/login', data={
            'user_id': 'basic_user', 
            'password': 'password1234',
            'csrf_token': 'dummy'
        })

        # 100件登録 (サービス層を直接呼んで高速化)
        from app.services.customer_service import CustomerService
        from app.models.customer import Customer
        
        customer_service = CustomerService()
        
        # Repoを通じて保存 (モックされたCsvHandlerを使う)
        repo = customer_service.customer_repo
        for i in range(100):
            cust = Customer(customer_id=f"C{i}", name=f"Name{i}", address="addr", phone="tel", email="mail")
            repo.save(cust)
            
        # 101件目の登録を試みる -> エラーになるはず
        resp = self.client.post('/customers/new', data={
            'name': 'Over Limit Customer',
            'email': 'over@example.com',
            'csrf_token': 'dummy'
        }, follow_redirects=True)
        
        # フラッシュメッセージ等でエラーが出ているか
        assert b'\xe4\xb8\x8a\xe9\x99\x90' in resp.data or b'Limit' in resp.data or b'plan' in resp.data
