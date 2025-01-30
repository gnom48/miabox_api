package storage

type Config struct {
	DatabaseUrl string `toml:"database_url"`
}

func NewConfig() *Config {
	return &Config{
		DatabaseUrl: "host=db port=6432 dbname=postgres sslmode=disable user=postgres password=fbM849INe17RPxy",
	}
}
