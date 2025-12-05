"""
CryptoManager: 暗号化・復号・ハッシュ化クラス
顧客リスト管理システム - 共通モジュール
"""
import os
import hashlib
import secrets
from typing import Optional
from cryptography.fernet import Fernet


class CryptoManager:
    """
    暗号化・復号・ハッシュ化を行うクラス。
    - 顧客情報: AES暗号化 (Fernetを使用)
    - パスワード: SHA-256 + Salt によるハッシュ化
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        CryptoManagerを初期化する。

        Args:
            encryption_key: Fernet暗号化キー（Base64エンコード文字列）
                           Noneの場合は環境変数から取得
        """
        if encryption_key:
            self._key = encryption_key.encode()
        else:
            key_from_env = os.environ.get('ENCRYPTION_KEY')
            if not key_from_env:
                raise ValueError(
                    "暗号化キーが設定されていません。"
                    "環境変数 ENCRYPTION_KEY を設定するか、コンストラクタにキーを渡してください。"
                )
            self._key = key_from_env.encode()

        self._fernet = Fernet(self._key)

    @staticmethod
    def generate_key() -> str:
        """
        新しい暗号化キーを生成する。

        Returns:
            Base64エンコードされた暗号化キー
        """
        return Fernet.generate_key().decode()

    # ===== 暗号化・復号 (顧客情報用) =====

    def encrypt(self, plaintext: str) -> str:
        """
        平文を暗号化する。

        Args:
            plaintext: 暗号化する平文

        Returns:
            暗号化されたテキスト（Base64エンコード）
        """
        if not plaintext:
            return ""
        encrypted = self._fernet.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        暗号文を復号する。

        Args:
            ciphertext: 復号する暗号文（Base64エンコード）

        Returns:
            復号された平文
        """
        if not ciphertext:
            return ""
        decrypted = self._fernet.decrypt(ciphertext.encode())
        return decrypted.decode()

    # ===== ハッシュ化 (パスワード用) =====

    @staticmethod
    def generate_salt() -> str:
        """
        ソルトを生成する。

        Returns:
            16バイトのソルト（16進数文字列）
        """
        return secrets.token_hex(16)

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """
        パスワードをソルト付きでハッシュ化する。

        Args:
            password: ハッシュ化するパスワード
            salt: ソルト（16進数文字列）

        Returns:
            ハッシュ化されたパスワード（16進数文字列）
        """
        salted_password = salt + password
        hashed = hashlib.sha256(salted_password.encode()).hexdigest()
        return hashed

    @staticmethod
    def create_password_hash(password: str) -> str:
        """
        パスワードからソルト付きハッシュを生成する。
        保存形式: "salt$hash"

        Args:
            password: ハッシュ化するパスワード

        Returns:
            "salt$hash" 形式の文字列
        """
        salt = CryptoManager.generate_salt()
        hashed = CryptoManager.hash_password(password, salt)
        return f"{salt}${hashed}"

    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """
        パスワードを検証する。

        Args:
            password: 検証するパスワード
            stored_hash: 保存されているハッシュ（"salt$hash" 形式）

        Returns:
            パスワードが一致する場合True
        """
        if '$' not in stored_hash:
            return False

        salt, expected_hash = stored_hash.split('$', 1)
        actual_hash = CryptoManager.hash_password(password, salt)
        return secrets.compare_digest(actual_hash, expected_hash)
