# Impact Analysis Report: CSVからデータベース（RDB）への移行

**Task ID**: T018 (Proposed)  
**Subject**: データ管理基盤のデータベース化（SQLite/PostgreSQL等）

## 📊 Analysis Summary
現在のシステムは `CsvHandler` を介したファイルベースのデータ管理を行っています。これをリレーショナルデータベース（RDB）へ移行することは、整合性、同時実行性、および検索スケーラビリティの向上に大きく寄与しますが、データアクセス層全体にわたる広範な変更を伴います。

## 🔍 Impact Details

### 1. 影響範囲の要約
- **影響度**: 🔴 Critical
- **対象箇所**: 全ての Model クラス（`User`, `Customer`, `AnalysisResult`）、Repository クラス、および `CsvHandler` に依存する全 Service 層（`BillingService`, `PlanChangeService` 等）。

### 2. 具体的な影響箇所
| コンポーネント | 現状 (CSV) | 変更後 (RDB) | 影響度 |
|----------------|------------|--------------|--------|
| `app/models/csv_handler.py` | ファイルロック、辞書ベース | 廃棄、または ORM (SQLAlchemy等) への置換 | 🔴 高 |
| `app/models/*_repo.py` | `CsvHandler` のラップ | DBクエリ（Select/Insert/Update）の発行 | 🔴 高 |
| `app/services/logger.py` | CSVへの追記 | ログテーブルへの Insert または外部ロギングツール | 🟡 中 |
| `tests/` | 物理ファイルの削除/作成による初期化 | DBマイグレーション、Fixturesの導入 | 🔴 高 |

### 3. 技術的課題と対策
- **トランザクション管理**: 現在はファイル単位の排他制御ですが、DB化により ACID トランザクションが可能になります。複数のServiceを跨ぐ処理の Atomicity を再設計する必要があります。
- **暗号化の維持**: データベース化後も `CryptoManager` による暗号化（カラム単位）は維持すべきです。ORM の Setter/Getter で自動暗号化する仕組みを推奨。
- **データ移行 (Migration)**: 既存の CSV データを SQL 形式に変換し、初期投入するための `seed` スクリプトが必要です。

### 4. エージェント割当への影響
- **Impact Analysis Agent**: マイグレーション計画の詳細化とスキーマ設計の主導。
- **Phase Agent**: 各ドメイン（User, Customer, Billing）の Repository 層を DB 対応に書き換える作業。

## 🛠 Proposed Action Plan (Phase 9)
1. **基盤選定**: SQLite（ポータビリティ重視）または PostgreSQL（スケーラビリティ重視）の決定。
2. **Repository パターンの抽象化**: `BaseRepository` インターフェースを定義し、内部実装を `CsvHandler` から `DB (SQLAlchemy)` へ切り替え。
3. **マイグレーションツールの導入**: `Alembic` 等を用いたスキーマ管理。
4. **段階的移行**: ログ系（書き込み主体）から始め、マスター系（読み書き複雑）へ順次移行。

## 🏁 Recommendation
**GO (Highly Recommended for scale)**
現在の顧客数（数千件）までは CSV でも耐えられますが、Phase 8 で実写解析結果（大量データ）が追加されたため、パフォーマンスと整合性の観点から早期のデータベース化を強く推奨します。
