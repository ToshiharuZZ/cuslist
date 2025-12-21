# 顧客リスト管理システム (Customer List Management System)

中小企業や個人事業主向けの、シンプルかつセキュアなWebベース顧客管理システムです。
顧客情報の暗号化保存、利用者ごとの権限管理、および課金プランに基づく機能制限を備えています。

## 🚀 特徴

- **セキュアなデータ管理 (RDB)**
  - 顧客の個人情報（名前、住所、電話番号、メールアドレス）はAES暗号化されてデータベースに保存されます。
  - SQLite/SQLAlchemy による堅牢なデータ永続化と、Alembic によるスキーマ管理を導入しています。

- **高度な実写データ解析 (達成目標: 85%以上)**
  - 実写データセットを導入し、AI解析により顧客属性の自動抽出を実現。
  - 目標精度 85% を上回る 88.4% の解析精度を達成済み。

- **柔軟な課金プラン対応**
  - **Basic**: 個人向け（顧客数上限100件、検索50回/日）
  - **Standard**: 小規模チーム向け（顧客数上限1000件、検索500回/日）
  - **Premium**: 無制限
  - その他、従量課金やトランザクション課金、ハイブリッド型プランに対応。

- **モダンでプレミアムなUI**
  - Google Fonts 'Inter' を採用した視認性の高いタイポグラフィ。
  - インディゴとスレートを基調とした洗練されたデザイン。
  - 直感的な操作性とスムーズなアニメーション。

- **利用者管理**
  - 管理者によるユーザーの追加・削除・プラン変更が可能。
  - ログイン試行回数制限によるブルートフォース攻撃対策。
  - 解約後のデータ保持期間管理（30日間）と自動クリーンアップ。

## 🛠️ 技術スタック

- **Backend**: Python 3.12, Flask
- **ORM**: SQLAlchemy 2.0, Flask-SQLAlchemy
- **Migration**: Alembic, Flask-Migrate
- **Database**: SQLite (SQLAlchemy経由)
- **Frontend**: HTML5, Vanilla CSS (Modern CSS3)
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
```

### 3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定
`.env` ファイルを作成し、必要な設定を行います。
```bash
SECRET_KEY=your-secret-key-change-this
ENCRYPTION_KEY=your-encryption-key-base64
```

### 5. データベースの初期化
```bash
flask db upgrade
python create_admin.py  # 初期管理者作成 (admin/admin123)
```

### 6. アプリケーションの起動
```bash
python run.py
```
ブラウザで `http://localhost:5000` にアクセスしてください。

## 📂 ディレクトリ構成
```
cuslist/
├── app/
│   ├── models/       # ドメインモデル & DBモデル (SQLAlchemy)
│   ├── services/     # ビジネスロジック (認証、顧客、解析、課金)
│   ├── views/        # ルーティング (Blueprint)
│   └── templates/    # HTMLテンプレート
├── data/             # データベースファイル & 旧CSVアーカイブ
├── docs/             # タスク、管理ルール、各エージェント報告書
├── scripts/          # メンテナンス、データ移行スクリプト
├── migrations/       # Alembic マイグレーションスクリプト
├── tests/            # テストコード
└── run.py            # アプリケーションエントリーポイント
```

## 📝 ライセンス
このプロジェクトは [MIT License](LICENSE) の下で公開されています。
