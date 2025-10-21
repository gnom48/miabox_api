package storage

import (
	"database/sql"

	_ "github.com/lib/pq"
	"github.com/sirupsen/logrus"
)

type Storage struct {
	logger     *logrus.Logger
	config     *Config
	db         *sql.DB
	repository AuthRepository
	usecase    *AuthUsecase
}

func New(config *Config) *Storage {
	return &Storage{
		config: config,
		logger: logrus.New(),
	}
}

func (s *Storage) Open() error {
	db, err := sql.Open("postgres", s.config.DatabaseUrl)
	if err != nil {
		return err
	}

	s.db = db

	return nil
}

func (s *Storage) GetDbConnection() *sql.DB {
	if s.db == nil {
		s.Open()
	}
	return s.db
}

func (s *Storage) Close() {
	if s.db != nil {
		s.db.Close()
	}
}

func (s *Storage) getRepository() AuthRepository {
	if s.repository == nil {
		s.repository = NewAuthRepository(s.GetDbConnection())
	} else {
		_ = s.GetDbConnection()
	}
	return s.repository
}

func (s *Storage) GetUsecase() *AuthUsecase {
	if s.usecase == nil {
		s.usecase = &AuthUsecase{
			repository: s.getRepository(),
		}
	}
	return s.usecase
}
