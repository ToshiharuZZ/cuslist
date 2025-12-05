"""
CsvHandler 単体テスト
"""
import os
import pytest
import tempfile
import shutil
from app.models.csv_handler import CsvHandler


class TestCsvHandler:
    """CsvHandlerのテストクラス"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前にテンポラリディレクトリを作成"""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.csv')
        self.fieldnames = ['id', 'name', 'email']
        yield
        # テスト後にクリーンアップ
        shutil.rmtree(self.test_dir)

    def test_create_file_if_not_exists(self):
        """ファイルが存在しない場合、ヘッダー付きで作成されること"""
        handler = CsvHandler(self.test_file, self.fieldnames)
        assert os.path.exists(self.test_file)

        with open(self.test_file, 'r') as f:
            content = f.read()
        assert 'id,name,email' in content

    def test_add_record(self):
        """レコードを追加できること"""
        handler = CsvHandler(self.test_file, self.fieldnames)
        record = {'id': '001', 'name': 'Test User', 'email': 'test@example.com'}
        handler.add_record(record)

        records = handler.read_all()
        assert len(records) == 1
        assert records[0]['id'] == '001'
        assert records[0]['name'] == 'Test User'

    def test_find_by_id(self):
        """IDでレコードを検索できること"""
        handler = CsvHandler(self.test_file, self.fieldnames)
        handler.add_record({'id': '001', 'name': 'User1', 'email': 'user1@example.com'})
        handler.add_record({'id': '002', 'name': 'User2', 'email': 'user2@example.com'})

        result = handler.find_by_id('id', '002')
        assert result is not None
        assert result['name'] == 'User2'

        result_none = handler.find_by_id('id', '999')
        assert result_none is None

    def test_update_record(self):
        """レコードを更新できること"""
        handler = CsvHandler(self.test_file, self.fieldnames)
        handler.add_record({'id': '001', 'name': 'Old Name', 'email': 'old@example.com'})

        success = handler.update_record('id', '001', {'name': 'New Name'})
        assert success is True

        updated = handler.find_by_id('id', '001')
        assert updated['name'] == 'New Name'
        assert updated['email'] == 'old@example.com'  # 更新していない項目は保持

    def test_delete_record(self):
        """レコードを削除できること"""
        handler = CsvHandler(self.test_file, self.fieldnames)
        handler.add_record({'id': '001', 'name': 'User1', 'email': 'user1@example.com'})
        handler.add_record({'id': '002', 'name': 'User2', 'email': 'user2@example.com'})

        success = handler.delete_record('id', '001')
        assert success is True
        assert handler.count() == 1

        remaining = handler.read_all()
        assert remaining[0]['id'] == '002'

    def test_generate_next_id(self):
        """次のIDを自動採番できること"""
        handler = CsvHandler(self.test_file, self.fieldnames)

        # 最初のIDは001
        first_id = handler.generate_next_id('id', 'CUS')
        assert first_id == 'CUS001'

        handler.add_record({'id': 'CUS001', 'name': 'User1', 'email': 'user1@example.com'})
        handler.add_record({'id': 'CUS002', 'name': 'User2', 'email': 'user2@example.com'})

        next_id = handler.generate_next_id('id', 'CUS')
        assert next_id == 'CUS003'

    def test_count(self):
        """レコード数を正しくカウントできること"""
        handler = CsvHandler(self.test_file, self.fieldnames)
        assert handler.count() == 0

        handler.add_record({'id': '001', 'name': 'User1', 'email': 'user1@example.com'})
        assert handler.count() == 1

        handler.add_record({'id': '002', 'name': 'User2', 'email': 'user2@example.com'})
        assert handler.count() == 2
