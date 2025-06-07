package server

import (
	"auth/internal/storage"
)

type Config struct {
	BindAddress    string `toml:"bind_address"`
	LogLevel       string `toml:"log_level"`
	LogHeaders     bool
	LogBody        bool
	LogQueryParams bool
	StorageConfig  *storage.Config
}

func (c *Config) SetDefaultValues() {
	c.LogHeaders = c.LogLevel == "debug"
	c.LogBody = c.LogLevel == "debug"
	c.LogQueryParams = c.LogLevel == "debug"
}
