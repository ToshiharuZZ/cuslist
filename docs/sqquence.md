# 顧客登録処理シーケンス図 (sequence.md)

```mermaid
sequenceDiagram
    participant U as 利用者
    participant UI as 顧客登録画面
    participant APP as アプリケーション
    participant ENC as 暗号化モジュール
    participant CSV as customers.csv
    participant LOG as logs.csv

    U->>UI: 顧客情報入力
    UI->>APP: 入力データ送信
    APP->>APP: バリデーションチェック
    APP->>ENC: 顧客情報暗号化要求
    ENC-->>APP: 暗号化済みデータ返却
    APP->>CSV: 暗号化データ保存
    APP->>LOG: 操作ログ保存
    APP-->>UI: 登録完了通知
    UI-->>U: 「登録完了」表示
