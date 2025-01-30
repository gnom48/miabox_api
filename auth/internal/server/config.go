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
	return &Config{
		BindAddress:    ":8081",
		LogLevel:       "debug",
		LogHeaders:     false,
		LogBody:        true,
		LogQueryParams: true,
		StorageConfig:  storage.NewConfig(),
	}
}
