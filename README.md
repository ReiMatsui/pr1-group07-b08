# pr1-group07-b08
Practice of Infomation Systemsの7班のプロジェクトです．


# Chari Spot App

このプロジェクトは、**Flutter** をフロントエンドに、**FastAPI** をバックエンドに使用したアプリケーションです． 
バックエンドは [Poetry](https://python-poetry.org/) を用いて依存関係を管理しています．

---

## 🧰 前提条件

- Python 3.10+
- Poetry 1.8+
- Flutter SDK（3.x以上）
- Android/iOS エミュレータ or 実機（必要に応じて）

---

## 🚀 セットアップ手順


### 📦 バックエンド（FastAPI + Poetry）

0. Poetryのダウンロード（なければ）
```
curl -sSL https://install.python-poetry.org | python3 -
```

1. ディレクトリ移動：

```
cd backend
```

2. 依存関係のインストール：

```
poetry install
```

3. サーバー起動
```
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. 動作確認：

* API エンドポイント: http://localhost:8000/api/hello

* Swagger UI: http://localhost:8000/docs

### 💻 フロントエンド（Flutter）

0. flutterのインストール
```
git clone https://github.com/flutter/flutter.git -b stable
```
* pathを通す
```
export PATH="$PATH:`pwd`/flutter/bin"
```

1. ディレクトリ移動
```
cd frontend
```

2. 依存関係のインストール
```
flutter pub get
```

3. アプリ起動
```
flutter run
```

4. 動作確認
* バックエンドの3を行い，APIが起動していることを確認してください．
* アプリ画面に`Hello from FastAPI!`と表示されれば成功です！