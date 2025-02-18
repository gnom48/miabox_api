package server

import (
	"auth/internal/storage"
)

type Config struct {
	BindAddress    string `toml:"bind_address"`
	LogLevel       string `toml:"log_level"`
	LogHeaders     bool   `toml:"log_headers"`
	LogBody        bool   `toml:"log_body"`
	LogQueryParams bool   `toml:"log_query_params"`
	StorageConfig  *storage.Config
}

func NewConfig() *Config {
	logLevel := "debug"
	return &Config{
		BindAddress:    ":8081",
		LogLevel:       logLevel,
		LogHeaders:     logLevel == "info",
		LogBody:        logLevel == "info",
		LogQueryParams: logLevel == "info",
		StorageConfig:  storage.NewConfig(),
	}
}
