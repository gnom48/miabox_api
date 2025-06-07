import os
import toml

TOML_PATH = r'app/config/config.toml'


def dump_env_to_toml(filepath: str):
    config_data = {
        "services": {
            "auth_host": os.getenv("AUTH_HOST"),
            "auth_port": os.getenv("AUTH_PORT"),
            "core_host": os.getenv("CORE_HOST"),
            "core_port": os.getenv("CORE_PORT"),
            "redis_host": os.getenv("REDIS_HOST"),
            "redis_port": os.getenv("REDIS_PORT"),
            "redis_user": os.getenv("REDIS_USER"),
            "redis_user_password": os.getenv("REDIS_USER_PASSWORD")
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
