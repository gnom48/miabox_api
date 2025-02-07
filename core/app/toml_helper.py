import os
import toml

"""
В сервисе CORE необходимы:

- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_PASSWORD
- POSTGRES_USER

- AUTH_PORT
- WHISPER_PORT
- MINIO_API_PORT
- RABBITMQ_PORT

- API_KEY

- LOG_LEVEL
"""

TOML_PATH = 'core/app/config/config.toml'


def dump_env_to_toml(filepath: str):
    config_data = {
        "database": {
            "postgres_port": os.getenv("POSTGRES_PORT"),
            "postgres_db": os.getenv("POSTGRES_DB"),
            "postgres_user": os.getenv("POSTGRES_USER"),
            "postgres_password": os.getenv("POSTGRES_PASSWORD")
        },
        "services": {
            "auth_port": os.getenv("AUTH_PORT"),
            "whisper_port": os.getenv("WHISPER_PORT"),
            "minio_port": os.getenv("MINIO_API_PORT"),
            "rabbitmq_port": os.getenv("RABBITMQ_PORT")
        },
        "access": {
            "api_key": os.getenv("API_KEY")
        },
        "app": {
            "log_level": os.getenv("LOG_LEVEL", default="INFO")
        }
    }

    with open(filepath, 'w') as f:
        toml.dump(config_data, f)


def load_var_from_toml(filepath: str, tag: str, key: str):
    with open(filepath, 'r') as f:
        data = toml.load(f)
        return data[tag][key]


def load_data_from_toml(filepath: str):
    with open(filepath, 'r') as f:
        return toml.load(f)


if __name__ == "__main__":
    dump_env_to_toml(TOML_PATH)
