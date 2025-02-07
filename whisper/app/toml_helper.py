import os
import toml

"""
В сервисе CORE необходимы:

- RABBITMQ_PORT
- CORE_PORT

- API_KEY

- MODEL
- LOG_LEVEL
"""

TOML_PATH = 'core/app/config/config.toml'


def dump_env_to_toml(filepath: str):
    config_data = {
        "services": {
            "core_port": os.getenv("CORE_PORT"),
            "rabbitmq_port": os.getenv("RABBITMQ_PORT")
        },
        "access": {
            "api_key": os.getenv("API_KEY")
        },
        "app": {
            "model": os.getenv("MODEL", default="base"),
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
