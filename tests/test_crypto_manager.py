"""
CryptoManager 単体テスト
"""
import os
import pytest
from app.models.crypto_manager import CryptoManager


class TestCryptoManager:
    """CryptoManagerのテストクラス"""

    @pytest.fixture
    def crypto_manager(self):
        """テスト用の暗号化キーでCryptoManagerを初期化"""
        test_key = CryptoManager.generate_key()
        return CryptoManager(encryption_key=test_key)

    def test_generate_key(self):
        """暗号化キーを生成できること"""
        key = CryptoManager.generate_key()
        assert key is not None
        assert len(key) > 0
        # Fernetキーは44文字のBase64文字列
        assert len(key) == 44

    def test_encrypt_decrypt(self, crypto_manager):
        """暗号化と復号が正しく動作すること"""
        plaintext = "これはテストメッセージです。"
        encrypted = crypto_manager.encrypt(plaintext)

        # 暗号化されたテキストは元のテキストと異なる
        assert encrypted != plaintext

        # 復号すると元のテキストに戻る
        decrypted = crypto_manager.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_empty_string(self, crypto_manager):
        """空文字列の暗号化・復号"""
        encrypted = crypto_manager.encrypt("")
        assert encrypted == ""

        decrypted = crypto_manager.decrypt("")
        assert decrypted == ""

    def test_encrypt_special_characters(self, crypto_manager):
        """特殊文字を含む文字列の暗号化・復号"""
        plaintext = "テスト！@#$%^&*()<>?:\"{}|"
        encrypted = crypto_manager.encrypt(plaintext)
        decrypted = crypto_manager.decrypt(encrypted)
        assert decrypted == plaintext

    def test_generate_salt(self):
        """ソルトを生成できること"""
        salt1 = CryptoManager.generate_salt()
        salt2 = CryptoManager.generate_salt()

        # ソルトは32文字の16進数文字列
        assert len(salt1) == 32
        assert len(salt2) == 32

        # 毎回異なるソルトが生成される
        assert salt1 != salt2

    def test_hash_password(self):
        """パスワードをハッシュ化できること"""
        password = "secure_password_123"
        salt = CryptoManager.generate_salt()

        hash1 = CryptoManager.hash_password(password, salt)
        hash2 = CryptoManager.hash_password(password, salt)

        # 同じパスワードとソルトなら同じハッシュ
        assert hash1 == hash2

        # 異なるソルトなら異なるハッシュ
        different_salt = CryptoManager.generate_salt()
        hash3 = CryptoManager.hash_password(password, different_salt)
        assert hash1 != hash3

    def test_create_password_hash(self):
        """パスワードハッシュを作成できること"""
        password = "my_password"
        stored_hash = CryptoManager.create_password_hash(password)

        # "salt$hash" 形式であること
        assert '$' in stored_hash
        parts = stored_hash.split('$')
        assert len(parts) == 2

    def test_verify_password_success(self):
        """正しいパスワードで検証が成功すること"""
        password = "correct_password"
        stored_hash = CryptoManager.create_password_hash(password)

        result = CryptoManager.verify_password(password, stored_hash)
        assert result is True

    def test_verify_password_failure(self):
        """間違ったパスワードで検証が失敗すること"""
        password = "correct_password"
        stored_hash = CryptoManager.create_password_hash(password)

        result = CryptoManager.verify_password("wrong_password", stored_hash)
        assert result is False

    def test_verify_password_invalid_format(self):
        """不正な形式のハッシュで検証が失敗すること"""
        result = CryptoManager.verify_password("any_password", "invalid_hash_format")
        assert result is False
