import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST: str = os.environ.get("DB_HOST")
DB_PORT: str = os.environ.get("DB_PORT")
DB_NAME: str = os.environ.get("DB_NAME")
DB_USER: str = os.environ.get("DB_USER")
DB_PASS: str = os.environ.get("DB_PASS")

TEST_DB_HOST: str = os.environ.get("TEST_DB_HOST")
TEST_DB_PORT: str = os.environ.get("TEST_DB_PORT")
TEST_DB_NAME: str = os.environ.get("TEST_DB_NAME")
TEST_DB_USER: str = os.environ.get("TEST_DB_USER")
TEST_DB_PASS: str = os.environ.get("TEST_DB_PASS")

static_dir: str = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "static",
)
FILE_DIR: str = os.path.join(static_dir, "images")
