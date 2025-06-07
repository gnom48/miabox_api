#!/bin/sh

TOML_PATH="/auth/internal/config/config.toml"

# Создание директории, если она не существует
mkdir -p "$(dirname "$TOML_PATH")"

# Создание файла конфигурации
cat <<EOF > "$TOML_PATH"
bind_address = "0.0.0.0:$AUTH_PORT"
log_level = "$LOG_LEVEL"
secret_key = "$SECRET_KEY"
database_url = "host=$POSTGRES_HOST port=$POSTGRES_PORT dbname=$POSTGRES_DB sslmode=disable user=$POSTGRES_USER password=$POSTGRES_PASSWORD search_path=auth"
EOF
