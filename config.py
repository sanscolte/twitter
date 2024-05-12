import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST: str | None = os.environ.get("DB_HOST")
DB_PORT: str | None = os.environ.get("DB_PORT")
DB_NAME: str | None = os.environ.get("DB_NAME")
DB_USER: str | None = os.environ.get("DB_USER")
DB_PASS: str | None = os.environ.get("DB_PASS")

TEST_DB_HOST: str | None = os.environ.get("TEST_DB_HOST")
TEST_DB_PORT: str | None = os.environ.get("TEST_DB_PORT")
TEST_DB_NAME: str | None = os.environ.get("TEST_DB_NAME")
TEST_DB_USER: str | None = os.environ.get("TEST_DB_USER")
TEST_DB_PASS: str | None = os.environ.get("TEST_DB_PASS")

FILE_DIR: str = 'static/images'
