FROM golang:1.23-alpine

WORKDIR /auth

COPY ./go.mod ./
COPY ./go.sum ./
RUN go mod download

COPY ./cmd ./cmd
COPY ./internal ./internal

COPY ./scripts/toml_helper.sh ./
RUN chmod +x ./toml_helper.sh

ARG POSTGRES_HOST
ARG POSTGRES_PORT
ARG POSTGRES_DB
ARG POSTGRES_PASSWORD
ARG POSTGRES_USER
ARG LOG_LEVEL
ARG AUTH_PORT

ENV POSTGRES_HOST=${POSTGRES_HOST}
ENV POSTGRES_PORT=${POSTGRES_PORT}
ENV POSTGRES_DB=${POSTGRES_DB}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV LOG_LEVEL="info"
# ENV LOG_LEVEL=${LOG_LEVEL}
ENV AUTH_PORT=${AUTH_PORT}

RUN /bin/sh ./toml_helper.sh

RUN go build -o ./auth-service ./cmd/auth

CMD ["sh", "-c", "sleep 5; while [ ! -f ./auth-service ]; do sleep 1; done; ./auth-service"]