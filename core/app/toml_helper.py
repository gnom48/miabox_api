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
- MINIO_ROOT_USER
- MINIO_ROOT_PASSWORD
- RABBITMQ_PORT
- RABBITMQ_DEFAULT_USER
- RABBITMQ_DEFAULT_PASS

- SECRET_KEY

- LOG_LEVEL
"""

TOML_PATH = r'app/config/config.toml'


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
            "minio_api_port": os.getenv("MINIO_API_PORT"),
            "minio_access_key": os.getenv("MINIO_ROOT_USER"),
            "minio_secret_key": os.getenv("MINIO_ROOT_PASSWORD"),
            "minio_api_ip": os.getenv("MINIO_API_IP"),
            "rabbitmq_port": os.getenv("RABBITMQ_PORT"),
            "rabbitmq_user": os.getenv("RABBITMQ_DEFAULT_USER"),
            "rabbitmq_password": os.getenv("RABBITMQ_DEFAULT_PASS"),
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
