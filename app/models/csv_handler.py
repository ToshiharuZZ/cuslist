"""
CsvHandler: 排他制御付きCSV操作クラス
顧客リスト管理システム - 共通モジュール
"""
import csv
import os
import fcntl
from typing import List, Dict, Optional
from datetime import datetime


class CsvHandler:
    """
    CSVファイルの読み書きを行うクラス。
    ファイルロック機構により、同時書き込みによるデータ破損を防止する。
    """

    def __init__(self, file_path: str, fieldnames: List[str]):
        """
        CsvHandlerを初期化する。

        Args:
            file_path: CSVファイルのパス
            fieldnames: CSVのカラム名リスト
        """
        self.file_path = file_path
        self.fieldnames = fieldnames
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """ファイルが存在しない場合、ヘッダー付きで作成する。"""
        if not os.path.exists(self.file_path):
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def read_all(self) -> List[Dict[str, str]]:
        """
        CSVファイルから全レコードを読み込む。

        Returns:
            レコードのリスト（各レコードは辞書形式）
        """
        with open(self.file_path, 'r', newline='', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # 共有ロック（読み取り用）
            try:
                reader = csv.DictReader(f)
                return list(reader)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def find_by_id(self, id_field: str, id_value: str) -> Optional[Dict[str, str]]:
        """
        指定されたIDでレコードを検索する。

        Args:
            id_field: IDフィールド名
            id_value: 検索するID値

        Returns:
            見つかったレコード、または None
        """
        records = self.read_all()
        for record in records:
            if record.get(id_field) == id_value:
                return record
        return None

    def find_all_by_id(self, id_field: str, id_value: str) -> List[Dict[str, str]]:
        """
        指定されたIDに一致するすべてのレコードを検索する。

        Args:
            id_field: 検索対象のフィールド名
            id_value: 検索する値

        Returns:
            一致したレコードのリスト
        """
        records = self.read_all()
        return [r for r in records if r.get(id_field) == id_value]

    def add_record(self, record: Dict[str, str]) -> None:
        """
        新しいレコードをCSVファイルに追加する。

        Args:
            record: 追加するレコード（辞書形式）
        """
        with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # 排他ロック（書き込み用）
            try:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(record)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def update_record(self, id_field: str, id_value: str, updated_data: Dict[str, str]) -> bool:
        """
        指定されたIDのレコードを更新する。

        Args:
            id_field: IDフィールド名
            id_value: 更新対象のID値
            updated_data: 更新データ

        Returns:
            更新成功時True、レコードが見つからない場合False
        """
        records = self.read_all()
        updated = False

        for i, record in enumerate(records):
            if record.get(id_field) == id_value:
                records[i].update(updated_data)
                updated = True
                break

        if updated:
            self._write_all(records)

        return updated

    def delete_record(self, id_field: str, id_value: str) -> bool:
        """
        指定されたIDのレコードを削除する。

        Args:
            id_field: IDフィールド名
            id_value: 削除対象のID値

        Returns:
            削除成功時True、レコードが見つからない場合False
        """
        records = self.read_all()
        original_count = len(records)
        records = [r for r in records if r.get(id_field) != id_value]

        if len(records) < original_count:
            self._write_all(records)
            return True

        return False

    def _write_all(self, records: List[Dict[str, str]]) -> None:
        """
        全レコードをCSVファイルに書き込む（上書き）。

        Args:
            records: 書き込むレコードのリスト
        """
        with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # 排他ロック
            try:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(records)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def count(self) -> int:
        """
        レコード数を返す。

        Returns:
            レコード数
        """
        return len(self.read_all())

    def generate_next_id(self, id_field: str, prefix: str = "") -> str:
        """
        次のIDを自動採番する。

        Args:
            id_field: IDフィールド名
            prefix: IDのプレフィックス（例: "CUS"）

        Returns:
            新しいID（例: "CUS001"）
        """
        records = self.read_all()
        if not records:
            return f"{prefix}001"

        max_num = 0
        for record in records:
            id_val = record.get(id_field, "")
            if id_val.startswith(prefix):
                try:
                    num = int(id_val[len(prefix):])
                    max_num = max(max_num, num)
                except ValueError:
                    continue

        return f"{prefix}{max_num + 1:03d}"
