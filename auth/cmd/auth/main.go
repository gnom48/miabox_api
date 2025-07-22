package main

import (
	"auth/internal/server"
	tokens "auth/internal/server/tokens"
	"auth/internal/storage"
	"log"

	"github.com/BurntSushi/toml"
)

/*
Запуск
go run cmd/auth/main.go

Сборка документации
cd internal/server
swag init -g server.go account.go auth.go
*/

const conficFilePath = "./internal/config/config.toml"

func main() {
	defer func() {
		if r := recover(); r != nil {
			log.Fatal("Error while starting app: ", r)
		}
	}()

	type secret struct {
		secretKeyValue string `toml:"secret_key"`
	}
	secretStruct := &secret{}
	_, e := toml.DecodeFile(conficFilePath, secretStruct)
	if e != nil {
		panic(e)
	}

	tokens.SecretKey = secretStruct.secretKeyValue

	storageConfig := &storage.Config{}
	_, e = toml.DecodeFile(conficFilePath, storageConfig)
	if e != nil {
		panic(e)
	}

	serverConfig := &server.Config{}
	_, e = toml.DecodeFile(conficFilePath, serverConfig)
	if e != nil {
		panic(e)
	}

	serverConfig.SetDefaultValues()
	serverConfig.StorageConfig = storageConfig

	server := server.New(serverConfig)
	if err := server.Start(); err != nil {
		panic(err)
	}
}
