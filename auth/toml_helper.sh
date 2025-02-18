#!bin/bash

# В сервисе AUTH необходимы:
# 
# - POSTGRES_PORT
# - POSTGRES_DB
# - POSTGRES_PASSWORD
# - POSTGRES_USER
# 
# - AUTH_PORT
# 
# - API_KEY
# 
# - LOG_LEVEL

TOML_PATH="auth/config/config.toml"

cat <<EOF > "$TOML_PATH"
[services]
bind_address = ":$6"

[database]
database_url = "host=postgres port=$1 dbname=$2 sslmode=disable user=$4 password=$3"

[app]
EOF

if
$5 = "info"
then
echo "log_level = "$5"" >> $TOML_PATH
