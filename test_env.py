import os
import environ

# BASE_DIRの定義
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 環境変数の設定
env = environ.Env(DEBUG=(bool, False))

# .envファイルのパスを指定
env_path = os.path.join(BASE_DIR, "django/24pro/.env")
print("ENV_PATH:", env_path)

# .envファイルの読み込み
environ.Env.read_env(env_path)

# 環境変数を出力
print("SECRET_KEY:", env("SECRET_KEY"))
print("DEBUG:", env.bool("DEBUG"))
print("DATABASE_URL:", env("DATABASE_URL"))
print("ALLOWED_HOSTS:", env.list("ALLOWED_HOSTS"))
