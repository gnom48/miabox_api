FROM golang:1.23-alpine

WORKDIR /auth

COPY ./go.mod ./
COPY ./go.sum ./
RUN go mod download

COPY ./cmd ./cmd
COPY ./internal ./internal

RUN mkdir ./config

COPY ./toml_helper ./toml_helper

ARG POSTGRES_PORT
ARG POSTGRES_DB
ARG POSTGRES_PASSWORD
ARG POSTGRES_USER
ARG LOG_LEVEL
ARG AUTH_PORT

RUN toml_helper.sh POSTGRES_PORT POSTGRES_DB POSTGRES_PASSWORD POSTGRES_USER LOG_LEVEL AUTH_PORT

RUN go build -o ./auth-service ./cmd/auth

CMD ["sh", "-c", "sleep 5; while [ ! -f ./auth-service ]; do sleep 1; done; ./auth-service"]