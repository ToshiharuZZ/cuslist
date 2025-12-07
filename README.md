# 顧客リスト管理システム (Customer List Management System)

中小企業や個人事業主向けの、シンプルかつセキュアなWebベース顧客管理システムです。
顧客情報の暗号化保存、利用者ごとの権限管理、および課金プランに基づく機能制限を備えています。

## 🚀 特徴

- **セキュアなデータ管理**
  - 顧客の個人情報（名前、住所、電話番号、メールアドレス）はAES暗号化されてCSVファイルに保存されます。
  - 万が一ファイルが流出しても、鍵がなければ復号できません。

- **柔軟な課金プラン対応**
  - **Basic**: 個人向け（顧客数上限50件、検索5回/日）
  - **Standard**: 小規模チーム向け（顧客数上限1000件、検索50回/日）
  - **Premium**: 無制限
  - その他、従量課金やトランザクション課金などのプランに対応。

- **モダンでプレミアムなUI**
  - Google Fonts 'Inter' を採用した視認性の高いタイポグラフィ。
  - インディゴとスレートを基調とした洗練されたデザイン。
  - 直感的な操作性とスムーズなアニメーション。

- **利用者管理**
  - 管理者によるユーザーの追加・削除・プラン変更が可能。
  - ログイン試行回数制限によるブルートフォース攻撃対策。

## 🛠️ 技術スタック

- **Backend**: Python 3.9+, Flask
- **Frontend**: HTML5, Vanilla CSS (Modern CSS3)
- **Database**: CSV File System (Encrypted)
- **Security**: Flask-WTF (CSRF Protection), Cryptography (Fernet)

## ⚙️ セットアップと起動

### 前提条件
- Python 3.9 以上

### 1. リポジトリのクローン
```bash
git clone https://github.com/ToshiharuZZ/cuslist.git
cd cuslist
```

### 2. 仮想環境の作成と有効化
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定
`.env` ファイルを作成し、必要な設定を行います。
暗号化キーは初回起動時に自動生成されますが、セキュリティのため手動設定を推奨します。

```bash
# .env の例
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this
# ENCRYPTION_KEY=... (初回起動後に logs/ またはコンソールに出力されたキーを設定することを推奨)
```

### 5. アプリケーションの起動
```bash
python run.py
```
ブラウザで `http://localhost:5000` にアクセスしてください。

## 📖 使い方

### 初回ログイン
初期状態ではユーザーが存在しない場合、`AuthService` を通じて管理者ユーザーを作成するか、開発用スクリプトを利用してください（本番運用時は適切な初期化フローに従ってください）。

**テスト用デフォルトアカウント例** (開発環境のみ):
- ID: `admin`
- Pass: `admin123`
(※実際に登録されているかは環境によります)

### ダッシュボード
ログイン後、ダッシュボードから以下の機能にアクセスできます。
- **顧客管理**: 顧客の新規登録、一覧表示、検索、編集、削除
- **利用者管理** (管理者のみ): システム利用者の管理
- **契約プラン**: 現在のプランと制限状況の確認

## 📂 ディレクトリ構成
```
cuslist/
├── app/
│   ├── models/       # データモデル (CSV操作、暗号化)
│   ├── services/     # ビジネスロジック (認証、顧客、課金)
│   ├── views/        # ルーティング (Blueprint)
│   ├── templates/    # HTMLテンプレート
│   └── static/       # CSS, 画像
├── data/             # データ保存ディレクトリ (CSV)
├── docs/             # ドキュメント
├── logs/             # アプリケーションログ
├── tests/            # テストコード
├── run.py            # アプリケーションエントリーポイント
└── requirements.txt  # 依存パッケージ一覧
```

## 📝 ライセンス
このプロジェクトは [MIT License](LICENSE) の下で公開されています。

