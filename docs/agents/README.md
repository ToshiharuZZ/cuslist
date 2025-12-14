# エージェントシステム概要

## 📋 エージェント一覧
cuslistプロジェクトは、以下の専門エージェントによって管理・開発されています。

### 管理系
1. **Manager Agent**: プロジェクト進行管理、エージェント指揮
2. **Impact Analysis Agent**: 新機能の影響分析、エージェント割当最適化
3. **Reviewer Agent**: コードレビュー、品質保証

### 開発系
4. **Phase 1 Agent**: 基盤実装 (Foundation)
5. **Phase 2 Agent**: 利用者管理 (User)
6. **Phase 3 Agent**: 顧客管理 (Customer)
7. **Phase 4 Agent**: 課金・制限 (Billing)
8. **Phase 5 Agent**: UI/UX (Refinement)
9. **Phase 6 Agent**: 品質保証 (QA)
10. **Phase 7 Agent**: プラン変更・解約 (Plan Change)

---

## ⚖️ エージェント設計の最適化指針
**「タスク毎のエージェント乱立」を防ぎ、効率を最大化するための指針**

1.  **既存エージェントの活用**
    - 新しいタスクが発生した際、Impact Analysis Agentが凝集度・結合度を分析
    - 可能な限り既存の「機能ドメイン」エージェントに割り当てる

2.  **密結合タスクの集約**
    - 相互に依存し合うタスクは、同一エージェントが担当
    - 分業によるオーバーヘッドを削減

3.  **新規作成の制限**
    - 独立性が極めて高い場合のみ、新エージェントを作成

---

## 🔄 ワークフロー

### プロジェクト状況管理
- 完了後、全エージェントが `docs/project_status.md` を更新
- 詳細報告は `docs/reports/` に格納

### 新機能追加時
1. Manager → Impact Analysis: 分析依頼
2. Impact Analysis: 影響分析 ＋ **エージェント割当分析**
3. 最適な担当エージェントを決定し、Managerが承認
4. 実装開始
