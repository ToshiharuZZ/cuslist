"""
AnalysisResult: 解析結果モデル
"""
from typing import Optional, Dict
from datetime import datetime
from app.models.csv_handler import CsvHandler
from app.models.crypto_manager import CryptoManager

class AnalysisResult:
    """
    実写データ解析結果を表すモデルクラス。
    analysis_results.csv とマッピングし、機密情報を暗号化して保存する。
    """

    FIELDNAMES = [
        'result_id',
        'customer_id',
        'analysis_date',
        'accuracy_score',
        'attribute_json_enc',
        'status'
    ]

    def __init__(
        self,
        result_id: str,
        customer_id: str,
        analysis_date: Optional[str] = None,
        accuracy_score: float = 0.0,
        attribute_json: str = '{}',
        status: str = 'completed',
        attribute_json_enc: str = ''
    ):
        self.result_id = result_id
        self.customer_id = customer_id
        self.analysis_date = analysis_date or datetime.now().isoformat()
        self.accuracy_score = accuracy_score
        self._attribute_json = attribute_json
        self.status = status
        self._attribute_json_enc = attribute_json_enc

    def to_encrypted_dict(self, crypto: CryptoManager) -> Dict[str, str]:
        """暗号化して辞書形式に変換（CSV保存用）"""
        return {
            'result_id': self.result_id,
            'customer_id': self.customer_id,
            'analysis_date': self.analysis_date,
            'accuracy_score': str(self.accuracy_score),
            'attribute_json_enc': crypto.encrypt(self._attribute_json),
            'status': self.status
        }

    @classmethod
    def from_encrypted_dict(cls, data: Dict[str, str], crypto: CryptoManager) -> 'AnalysisResult':
        """暗号化された辞書からインスタンスを生成（CSV読み込み用）"""
        return cls(
            result_id=data.get('result_id', ''),
            customer_id=data.get('customer_id', ''),
            analysis_date=data.get('analysis_date'),
            accuracy_score=float(data.get('accuracy_score', '0.0')),
            attribute_json=crypto.decrypt(data.get('attribute_json_enc', '')),
            status=data.get('status', 'completed'),
            attribute_json_enc=data.get('attribute_json_enc', '')
        )
