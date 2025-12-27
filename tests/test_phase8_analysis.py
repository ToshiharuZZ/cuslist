"""
Phase 8 (T017b 実写解析) 単体テスト
"""
import pytest
import os
import json
from app import create_app, db
from app.models.analysis_result import AnalysisResult
from app.services.analysis_service import AnalysisService
from app.models.db_models import AnalysisResult as AnalysisResultDB

@pytest.fixture(autouse=True)
def app_context():
    from app.models.crypto_manager import CryptoManager
    os.environ['ENCRYPTION_KEY'] = CryptoManager.generate_key()
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def analysis_service():
    return AnalysisService()

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
    
    # 直接DBを確認
    record = AnalysisResultDB.query.filter_by(customer_id=customer_id).first()
    assert record is not None
    # 平文の属性名が含まれていないことを確認
    assert "visit_frequency" not in record.attribute_json_enc
        
    # Service経由で復号されることを確認
    results = analysis_service.get_results_by_customer(customer_id)
    assert len(results) == 1
    # AnalysisResultモデルでは _attribute_json にアクセス可能（内部的には復号済み）
    decoded_attributes = json.loads(results[0]._attribute_json)
    assert "visit_frequency" in decoded_attributes
