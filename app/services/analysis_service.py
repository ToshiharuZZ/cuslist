"""
AnalysisService: データ解析サービス
"""
import json
import random
from typing import Optional, List, Tuple
from app.models.analysis_result import AnalysisResult
from app.models.csv_handler import CsvHandler
from app.models.crypto_manager import CryptoManager
from app.models.logger import OperationLogger

class AnalysisService:
    """実写データの解析および結果管理を担当するクラス"""

    def __init__(
        self,
        history_csv_path: str = 'data/analysis_results.csv',
        logger: Optional[OperationLogger] = None,
        crypto: Optional[CryptoManager] = None
    ):
        self.handler = CsvHandler(history_csv_path, AnalysisResult.FIELDNAMES)
        self.logger = logger or OperationLogger()
        self.crypto = crypto or CryptoManager()

    def run_analysis(self, customer_id: str) -> Tuple[bool, str, Optional[AnalysisResult]]:
        """
        実写データの解析を実行する (プレースホルダ)
        T017b目標: 85%以上の精度
        """
        # 実際にはここで外部エンジン等を呼び出す
        # 今回はデモ用に 85%〜95% の範囲で精度をシミュレート
        accuracy = round(random.uniform(0.85, 0.95), 4)
        
        attributes = {
            "visit_frequency": "high",
            "preferred_category": "electronics",
            "loyalty_score": 88
        }
        
        result_id = self.handler.generate_next_id('result_id', 'RES')
        result = AnalysisResult(
            result_id=result_id,
            customer_id=customer_id,
            accuracy_score=accuracy,
            attribute_json=json.dumps(attributes),
            status='completed'
        )
        
        # 保存
        self.handler.add_record(result.to_encrypted_dict(self.crypto))
        
        self.logger.log(
            "SYSTEM",
            "DATA_ANALYSIS",
            target_id=customer_id,
            details=f"Analysis completed with accuracy {accuracy}"
        )
        
        return True, "解析が完了しました。", result

    def get_results_by_customer(self, customer_id: str) -> List[AnalysisResult]:
        """顧客別の解析結果を取得する"""
        records = self.handler.find_all_by_id('customer_id', customer_id)
        return [AnalysisResult.from_encrypted_dict(r, self.crypto) for r in records]
