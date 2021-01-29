from p_config import Config

_DEFAULT_CONFIG = Config(
    project_name="fastapi_contrib",
    databases={"default": "sqlite:///db.sqlite3"},
)

CONFIG = _DEFAULT_CONFIG
