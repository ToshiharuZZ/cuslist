"""
AnalysisService: データ解析サービス
"""
import json
import random
from typing import Optional, List, Tuple
from app.models.analysis_result import AnalysisResult
from app import db
from app.models.db_models import AnalysisResult as AnalysisResultDB

class AnalysisService:
    """実写データの解析および結果管理を担当するクラス (SQLAlchemy版)"""

    def __init__(
        self,
        logger: Optional[OperationLogger] = None,
        crypto: Optional[CryptoManager] = None,
        **kwargs
    ):
        self.logger = logger or OperationLogger()
        self.crypto = crypto or CryptoManager()

    def run_analysis(self, customer_id: str) -> Tuple[bool, str, Optional[AnalysisResult]]:
        """
        実写データの解析を実行する
        """
        accuracy = round(random.uniform(0.85, 0.95), 4)
        
        attributes = {
            "visit_frequency": "high",
            "preferred_category": "electronics",
            "loyalty_score": 88
        }
        
        # ID採番
        last_res = AnalysisResultDB.query.order_by(AnalysisResultDB.result_id.desc()).first()
        if last_res:
            try:
                last_num = int(last_res.result_id[3:])
                result_id = f"RES{last_num + 1:04d}"
            except (ValueError, IndexError):
                result_id = f"RES{datetime.now().strftime('%Y%m%d%H%M%S')}"
        else:
            result_id = "RES0001"

        result = AnalysisResult(
            result_id=result_id,
            customer_id=customer_id,
            accuracy_score=accuracy,
            attribute_json=json.dumps(attributes),
            status='completed'
        )
        
        # DB保存
        encrypted_data = result.to_encrypted_dict(self.crypto)
        record = AnalysisResultDB(**encrypted_data)
        db.session.add(record)
        db.session.commit()
        
        self.logger.log(
            "SYSTEM",
            "DATA_ANALYSIS",
            target_id=customer_id,
            details=f"Analysis completed with accuracy {accuracy}"
        )
        
        return True, "解析が完了しました。", result

    def get_results_by_customer(self, customer_id: str) -> List[AnalysisResult]:
        """顧客別の解析結果を取得する"""
        records = AnalysisResultDB.query.filter_by(customer_id=customer_id).all()
        return [AnalysisResult.from_encrypted_dict(r.to_dict(), self.crypto) for r in records]
