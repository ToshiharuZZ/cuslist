# Phase 8: 実写データ解析基盤 詳細設計書 (T017b)

## 1. 目的
実写データセット（画像、ビデオ等）から、顧客属性や行動パターンを85%以上の精度で抽出する基盤を構築する。

## 2. アーキテクチャ概要
既存の管理システム（Flask + CSV）のパフォーマンスを維持するため、解析処理は「非同期/バックグラウンド実行」を前提とした疎結合な設計とする。

### データフロー
1. **Raw Data Ingest**: `data/raw_samples/{customer_id}/` にデータを配置。
2. **Analysis Processor**: 背景で解析スクリプトが走り、特徴量を抽出。
3. **Structured Results**: 解析結果を `data/analysis_results.csv` に保存。
4. **Integration**: 管理画面の顧客詳細から、解析結果をAPI経由で取得・表示。

## 3. データ構造定義

### `data/analysis_results.csv`
解析結果を保持する新しいデータファイル。
- `result_id`: 結果の一意識別子 (RES001...)
- `customer_id`: 関連する顧客ID
- `analysis_date`: 解析実施日時
- `accuracy_score`: 解析精度 (0.00 〜 1.00)
- `attribute_json_enc`: 抽出された属性データのJSON（暗号化済み）
- `status`: 'completed', 'processing', 'failed'

## 4. セキュリティ設計
- **解析元データ**: `crypto_manager.py` を拡張または流用し、生データディレクトリもアクセス制限と暗号化の対象とする。
- **解析結果**: 属性などの機密情報は `attribute_json_enc` カラムに暗号化して保存する。

## 5. 精度向上（85%）へのアプローチ
- **データ水増し (Augmentation)**: 限られた実写データから学習・評価の信頼性を高める。
- **アンサンブル手法**: 複数の小型モデルを組み合わせて、エッジでも動作可能な高精度化を図る。

## 6. 統合プラン
- `CustomerService` は直接解析ロジックを持たず、`AnalysisService` (新規) を介してデータを読み取る。
- UI側には「解析レポート」タブを新設。
