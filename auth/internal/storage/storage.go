package storage

import (
	"database/sql"

	_ "github.com/lib/pq"
)

type Storage struct {
	config     *Config
	db         *sql.DB
	repository *Repository
}

func New(config *Config) *Storage {
	return &Storage{
		config: config,
	}
}

func (s *Storage) Open() error {
	db, err := sql.Open("postgres", s.config.DatabaseUrl)

	if err != nil {
		return err
	}

	if err := db.Ping(); err != nil {
		return err
	}

	s.db = db

	return nil
}

func (s *Storage) Close() {
	if s != nil {
		if s.db != nil {
			s.db.Close()
		}
	}
}

func (s *Storage) Repository() *Repository {
	if s.repository == nil {
		s.repository = &Repository{
			storage: s,
		}
	}
	if s.db == nil {
		s.Open()
	}
	return s.repository
}
