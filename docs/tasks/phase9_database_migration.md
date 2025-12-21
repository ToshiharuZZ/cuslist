# Phase 9: データベース移行 (Database Migration)

## 🎯 目的
データ管理基盤をCSVファイルからリレーショナルデータベース（RDB）へ移行し、整合性、パフォーマンス、スケーラビリティを向上させる。

## 📋 要件
1.  **DBエンジン**: SQLite（初期段階、ポータビリティ重視）
2.  **ORM導入**: SQLAlchemy を使用し、Repository パターンを維持
3.  **データ整合性**: トランザクション管理による ACID 属性の確保
4.  **セキュリティ**: `CryptoManager` によるデータ暗号化の維持（カラム単位）
5.  **移行**: 既存 CSV データから DB へのシームレスな移行スクリプト
6.  **テスト**: DB 接続を前提とした既存テストの全パス

## 🛠 スキーマ管理方針
1.  **管理場所**: 
    - **モデル定義**: `app/models/db_models.py` (SQLAlchemy Declarative Base)
    - **移行スクリプト**: `migrations/` ディレクトリ (Alembic による管理)
2.  **実行主体の定義**:
    - **Backend Agent**: 
        - スキーマ（モデル）の設計と実装。
        - `alembic revision --autogenerate` による移行スクリプトの作成。
        - `flask db upgrade` 等による環境への適用（ローカル/テスト環境）。
    - **Security Agent**:
        - DDL (Create Table文等) に対するセキュリティ監査。特に PII (個人情報) のカラム型や暗号化フラグの確認。
    - **Manager Agent**:
        - マイグレーションの整合性レビューと、デプロイメントパイプラインでの実行承認。

## 🛠 タスク
### 1. 基盤設計 & 環境構築
- [ ] SQLAlchemy / Alembic の導入
- [ ] DB スキーマ設計（User, Customer, AnalysisResult, Billing, Logs）
- [ ] `BaseRepository` の抽象化と Repository 層の再設計

### 2. データアクセス層の実装
- [ ] `users`, `customers` 関連の Repository を DB 移行
- [ ] `analysis_results`, `billing`, `logs` 関連の Repository を DB 移行
- [ ] トランザクション管理の実装（特に課金・ログ関連）

### 3. セキュリティ & 監査
- [ ] DB 移行に伴うセキュリティ監査（SQL インジェクション等）
- [ ] カラム単位の自動暗号化/復号ロジック（SQLAlchemy Hybrid Property 等）

### 4. データ移行スクリプト
- [ ] CSV to DB 変換スクリプトの実装 (`scripts/migrate_csv_to_db.py`)
- [ ] 初期データのマイグレーション実施

### 5. テスト & 品質保証
- [ ] テスト用 DB (In-memory SQLite) 環境の構築
- [ ] 既存の 63 テストがすべて PASS することを確認
- [ ] DB 固有のシナリオテスト追加

## 👤 担当割当
- **Backend Agent**: 基盤設計、Repository 実装、移行スクリプト
- **Security Agent**: セキュリティ監査、暗号化ロジック検証
- **Impact Analysis Agent**: 進捗に伴う影響の継続的監視

## 🏁 完了条件
- 全ての CSV データが DB へ正常に移行されていること
- 既存機能が以前と同様に（またはそれ以上に）動作すること
- `gaws_checker.py` がエラーなしで終了すること
- 全テストが PASSED であること

---
**ステータス**: 🚀 進行中  
**進捗**: 5%  
**最終更新**: 2025-12-21 by Manager Agent
