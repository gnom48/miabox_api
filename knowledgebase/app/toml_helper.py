import os
import toml

"""
В сервисе KNOWLEDGEBASE необходимы:

- AUTH_PORT
- MINIO_API_PORT
- MINIO_ACCESS_KEY
- MINIO_SECRET_KEY

- SECRET_KEY

- LOG_LEVEL
"""

TOML_PATH = r'knowledgebase/app/config/config.toml'


def dump_env_to_toml(filepath: str):
    config_data = {
        "services": {
            "auth_port": os.getenv("AUTH_PORT"),
            "minio_port": os.getenv("MINIO_API_PORT"),
            "minio_access_key": os.getenv("MINIO_ROOT_USER"),
            "minio_secret_key": os.getenv("MINIO_ROOT_PASSWORD")
        },
        "access": {
            "secret_key": os.getenv("SECRET_KEY")
        },
        "app": {
            "log_level": os.getenv("LOG_LEVEL", default="INFO")
        }
    }

    if not os.path.exists(TOML_PATH):
        os.makedirs(os.path.dirname(TOML_PATH))

    with open(filepath, 'w') as f:
        toml.dump(config_data, f)


def load_var_from_toml(tag: str, key: str, filepath: str = TOML_PATH):
    with open(filepath, 'r') as f:
        data = toml.load(f)
        return data[tag][key]


def load_data_from_toml(filepath: str = TOML_PATH):
    with open(filepath, 'r') as f:
        return toml.load(f)


if __name__ == "__main__":
    dump_env_to_toml(TOML_PATH)
