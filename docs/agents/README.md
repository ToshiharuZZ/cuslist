# エージェントシステム概要

## 📋 エージェント一覧

cuslistプロジェクトは、以下の専門エージェントによって管理・開発されています。

---

## 🎯 管理系エージェント

### 1. Manager Agent (`docs/agents/manager_agent.md`)
**役割**: プロジェクト全体の進行管理、各フェーズ担当エージェントの指揮・監督、成果物の品質管理

**主な責任**:
- 進捗管理とタスク監視
- エージェントへの作業指示
- 品質レビューと統合管理
- **Impact Analysis Agentへの影響分析委任**
- Git反映とタスクチケット更新

**Why**: プロジェクト全体を俯瞰し、各エージェントを適切に指揮する司令塔

---

### 2. Impact Analysis Agent (`docs/agents/impact_analysis_agent.md`) **🆕**
**役割**: 新機能追加・既存機能変更時の影響分析とドキュメント更新の専門家

**主な責任**:
- 影響範囲の特定（既存Phase 1-Xへの影響評価）
- 依存関係の分析（データモデル、API、画面遷移）
- ドキュメント更新（エージェントプロファイル、タスクファイル、設計書）
- 影響分析レポート作成
- リスク評価と対策提案

**Why**: Manager Agentの負荷を軽減し、専門的な影響分析により見落としを防ぐ

**活躍する場面**:
- Phase 8, 9...などの新機能追加時
- データモデルの変更時
- アーキテクチャの変更時

---

### 3. Reviewer Agent (`docs/agents/reviewer_agent.md`)
**役割**: コードレビュー、品質保証、セキュリティチェックの専門家

**主な責任**:
- 要件・設計との整合性チェック
- セキュリティチェック
- コード品質チェック
- APPROVEDまたはCHANGES_REQUESTEDの判定

**Why**: 客観的な視点でのレビューにより、品質を保証する

---

## 🔧 開発系エージェント

### 4. Phase 1 Agent (Foundation) (`docs/agents/phase1_agent.md`)
**役割**: データの読み書きとセキュリティ基盤の確立

**主な責任**:
- CsvHandler、CryptoManager、Logger実装
- 暗号化処理の標準化

**Status**: ✅ 完了（21テストPASSED）

---

### 5. Phase 2 Agent (User Management) (`docs/agents/phase2_agent.md`)
**役割**: 利用者管理機能と認証システムの実装

**主な責任**:
- 認証機能、セッション管理
- 利用者管理
- アクセス制御
- **🆕 Phase 7対応**: Userモデル拡張、ステータス管理、マイグレーション

**Status**: ✅ 完了（12テストPASSED） + 🔄 Phase 7対応作業待ち

---

### 6. Phase 3 Agent (Customer Management) (`docs/agents/phase3_agent.md`)
**役割**: 顧客情報のCRUD・検索機能の実装

**主な責任**:
- 顧客モデル、CRUD処理
- 検索機能
- **🆕 Phase 7対応**: ユーザー削除時の顧客データ一括削除

**Status**: ✅ 完了（8テストPASSED） + 🔄 Phase 7対応作業待ち

---

### 7. Phase 4 Agent (Billing & Limits) (`docs/agents/phase4_agent.md`)
**役割**: 複雑な課金ロジックとプラン制限機能の実装

**主な責任**:
- 課金ロジック（6種類のプラン）
- 制限機能（顧客数、検索回数）
- 請求管理

**Status**: ✅ 完了（13テストPASSED）

---

### 8. Phase 5 Agent (Refinement) (`docs/agents/phase5_agent.md`)
**役割**: UIデザインとユーザー体験の向上

**主な責任**:
- デザイン適用（Vanilla CSS）
- UX改善
- **🆕 Phase 7対応**: ナビゲーション拡張、新画面スタイル適用

**Status**: ✅ 完了 + 🔄 Phase 7対応作業待ち

---

### 9. Phase 6 Agent (QA) (`docs/agents/phase6_agent.md`)
**役割**: システム全体の品質保証

**主な責任**:
- 結合テスト、負荷テスト
- セキュリティ監査
- **🆕 Phase 7対応**: 新機能テスト（24項目）、リグレッションテスト

**Status**: ✅ 完了（54テストPASSED） + 🔄 Phase 7テスト作業待ち

---

### 10. Phase 7 Agent (Plan Change & Cancellation) (`docs/agents/phase7_agent.md`) **🆕**
**役割**: プラン変更・解約機能の実装

**主な責任**:
- プラン変更機能（アップグレード/ダウングレード）
- 日割り計算
- 解約機能（即時/月末/予約）
- データ保持管理とバッチ削除
- 履歴管理
- 画面実装

**Status**: 🔄 実装待ち（Phase 2対応完了後に開始）

---

## 🔄 ワークフロー

### 新機能追加時（Phase 8以降も同様）

```
1. 📊 Manager Agent → Impact Analysis Agent: 影響分析依頼
       ↓
2. 🔍 Impact Analysis Agent: 影響分析実施
   - 既存Phaseへの影響評価
   - ドキュメント更新
   - レポート作成
       ↓
3. 📊 Impact Analysis Agent → Manager Agent: 分析完了報告
       ↓
4. 📊 Manager Agent: アクションプラン承認
       ↓
5. 📊 Manager Agent → Phase X Agent: 準備作業指示（必要な場合）
       ↓
6. 🔧 Phase X Agent: 準備作業完了
       ↓
7. 📊 Manager Agent → Phase X Agent: 実装作業指示
       ↓
8. 🔧 Phase X Agent: 実装・テスト実施
       ↓
9. 🔧 Phase X Agent → Reviewer Agent: 実装完了報告
       ↓
10. 🔍 Reviewer Agent: レビュー実施
       ↓
    [CHANGES_REQUESTED] → Phase X Agentが修正 → 再レビュー
    [APPROVED]
       ↓
11. 🔍 Reviewer Agent → Manager Agent: レビュー完了報告
       ↓
12. 📊 Manager Agent: Git反映・タスク更新
```

---

## 📈 エージェントシステムの利点

### 1. 役割の明確化
各エージェントが専門領域を持ち、責任範囲が明確

### 2. 品質の向上
- **Impact Analysis Agent**: 影響分析の専門家による見落とし防止
- **Reviewer Agent**: 客観的なレビューによる品質保証
- **Phase Agent**: 専門分野に集中した実装

### 3. 効率化
- **Manager Agent**: 進行管理に専念できる
- **Impact Analysis Agent**: 標準化された分析プロセス
- 並行作業が可能（例: Phase 7実装中にPhase 8の影響分析）

### 4. スケーラビリティ
- Phase 8, 9...と機能が増えても、同じワークフローで対応可能
- Impact Analysis Agentが常に整合性を保つ

### 5. ナレッジの蓄積
- 各エージェントのプロファイルがナレッジベースとなる
- 影響分析レポートが次回の参考資料となる

---

## 🎯 Phase 7実装における実例

今回のPhase 7（プラン変更・解約機能）実装では：

1. **Impact Analysis Agentが実施した作業**:
   - Phase 1-6への影響度評価
   - 6個のエージェントプロファイル更新
   - 5個のタスクファイル更新
   - 2つの分析ドキュメント作成
   - 合計13ファイルを更新

2. **Manager Agentが実施する作業**:
   - 影響分析結果の確認と承認
   - Phase 2 Agentへの準備作業指示（Userモデル拡張）
   - Phase 7 Agentへの実装作業指示
   - Git反映とタスク更新

**結果**: Manager Agentは進行管理と意思決定に専念でき、Impact Analysis Agentの専門的な分析により見落としがゼロに。

---

## 📝 まとめ

**10個のエージェント**が連携することで：
- ✅ 高品質な開発プロセス
- ✅ 明確な役割分担
- ✅ 効率的なワークフロー
- ✅ スケーラブルなシステム

を実現しています。

**最新追加**:
- Impact Analysis Agent（影響分析専門）
- Phase 7 Agent（プラン変更・解約機能）

**今後の展開**: Phase 8以降の新機能も、同じワークフローで安全かつ効率的に追加可能です。
