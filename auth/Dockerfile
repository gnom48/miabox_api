FROM golang:1.23-alpine

WORKDIR /auth

COPY ./go.mod ./
COPY ./go.sum ./
RUN go mod download

COPY ./cmd ./cmd
COPY ./internal ./internal
COPY ./config ./config

RUN go build -o ./auth-service ./cmd/auth

EXPOSE 8081

CMD ["sh", "-c", "sleep 5; while [ ! -f ./auth-service ]; do sleep 1; done; ./auth-service"]