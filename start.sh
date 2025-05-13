#!/bin/bash

# プロジェクトのルートディレクトリを取得
PROJECT_ROOT=$(dirname "$(realpath "$0")")

# Pythonのモジュール検索パスを設定
export PYTHONPATH="$PROJECT_ROOT/chari-spot/backend/src"

# APIサーバーをバックグラウンドで起動
echo "Starting API server..."
cd "$PROJECT_ROOT/chari-spot/backend"
poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

# フロントエンドの起動
echo "Starting Flutter frontend..."
cd "$PROJECT_ROOT/chari-spot//frontend"
flutter run -d chorme

# APIサーバーを停止
echo "Stopping API server..."
kill $API_PID