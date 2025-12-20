"""
Phase 8 (T017b 実写解析) 単体テスト
"""
import pytest
import os
import json
from app.models.analysis_result import AnalysisResult
from app.services.analysis_service import AnalysisService

@pytest.fixture(autouse=True)
def setup_encryption_key():
    from app.models.crypto_manager import CryptoManager
    os.environ['ENCRYPTION_KEY'] = CryptoManager.generate_key()

@pytest.fixture
def analysis_service(tmp_path):
    csv_path = tmp_path / "analysis_results.csv"
    return AnalysisService(history_csv_path=str(csv_path))

def test_run_analysis_accuracy_goal(analysis_service):
    """解析精度が目標(85%)以上であることを検証"""
    success, message, result = analysis_service.run_analysis("CUST001")
    
    assert success is True
    assert result.accuracy_score >= 0.85
    assert result.status == 'completed'

def test_analysis_data_encryption(analysis_service):
    """解析結果の属性情報が暗号化されて保存されていることを検証"""
    customer_id = "CUST999"
    analysis_service.run_analysis(customer_id)
    
    # 直接CSVを読み込んで暗号化を確認
    with open(analysis_service.handler.file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 平文の属性名が含まれていないことを確認
        assert "visit_frequency" not in content
        # JSONの一部ではない暗号化文字列っぽいものがあるか（簡易）
        assert "attribute_json_enc" in content
        
    # Service経由で復号されることを確認
    results = analysis_service.get_results_by_customer(customer_id)
    assert len(results) == 1
    decoded_attributes = json.loads(results[0]._attribute_json)
    assert "visit_frequency" in decoded_attributes
