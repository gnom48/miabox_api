package server

import (
	"auth/internal/server/tokens"
	"auth/internal/storage"
	"net/http"

	_ "auth/internal/server/docs"

	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
	httpSwagger "github.com/swaggo/http-swagger"
)

type ApiServer struct {
	config      *Config
	logger      *logrus.Logger
	router      *mux.Router
	storage     *storage.Storage
	tokenSigner tokens.TokenSigner
}

func New(config *Config) *ApiServer {
	return &ApiServer{
		config:      config,
		logger:      logrus.New(),
		router:      mux.NewRouter(),
		tokenSigner: &tokens.TokenSign{},
	}
}

func (s *ApiServer) Start() error {
	if err := s.ConfigureLogger(); err != nil {
		return err
	}
	s.logger.Info("Logger configured")

	s.ConfigureRouter()
	s.logger.Info("Router configured")

	if err := s.ConfigureStore(); err != nil {
		s.logger.Error(err)
		return err
	}
	s.logger.Info("Storage configured")

	s.logger.Info("Starting ApiServer")
	return http.ListenAndServe(s.config.BindAddress, s.router)
}

func (s *ApiServer) ConfigureLogger() error {
	level, err := logrus.ParseLevel(s.config.LogLevel)
	if err != nil {
		return err
	}

	s.logger.SetLevel(level)
	s.logger.SetFormatter(&logrus.TextFormatter{})

	return nil
}

func (s *ApiServer) ConfigureStore() error {
	s.storage = storage.New(s.config.StorageConfig)

	conn := s.storage.GetDbConnection()

	err := conn.Ping()
	if err != nil {
		s.logger.Fatal(err)
	}

	return nil
}

// @title Auth
// @version 1.0
// @description Account API (Auth microservice) documentation. Отвечает за авторизацию и данные о пользователях. Все остальные сервисы зависят от него, ведь именно он выпускает JWT токен и проводит интроспекцию.
// @host localhost:8081
// @BasePath /
// @schemes http
func (s *ApiServer) ConfigureRouter() {
	s.router.Use(s.internalServerErrorMiddleware)
	s.router.Use(s.loggingMiddleware)

	s.router.HandleFunc("/api/Authentication/SignUp", s.HandleAuthenticationSignUp()).Methods("POST")
	s.router.HandleFunc("/api/Authentication/SignIn", s.HandleAuthenticationSignIn()).Methods("POST")
	s.router.HandleFunc("/api/Authentication/SignOut", s.AuthCreationTokenMiddleware(s.HandleAuthenticationSignOut())).Methods("HEAD")
	s.router.HandleFunc("/api/Authentication/Validate", s.HandleAuthenticationValidate()).Methods("GET")
	s.router.HandleFunc("/api/Authentication/Refresh", s.AuthCreationTokenMiddleware(s.HandleAuthenticationRefresh())).Methods("GET")

	s.router.HandleFunc("/api/Accounts/Me", s.AuthRegularTokenMiddleware(s.HandleGetCurrentAccount())).Methods("GET")
	s.router.HandleFunc("/api/Accounts/Update", s.AuthRegularTokenMiddleware(s.HandleUpdateAccount())).Methods("PUT")
	s.router.HandleFunc("/api/Accounts", s.AuthRegularTokenMiddleware(s.HandleGetAllAccounts())).Methods("GET")
	s.router.HandleFunc("/api/Accounts", s.AuthRegularTokenMiddleware(s.HandleCreateAccount())).Methods("POST")
	s.router.HandleFunc("/api/Accounts/{id}", s.AuthRegularTokenMiddleware(s.HandleUpdateAccountById())).Methods("PUT")
	s.router.HandleFunc("/api/Accounts/{id}", s.AuthRegularTokenMiddleware(s.HandleSoftDeleteAccountById())).Methods("DELETE")

	s.router.PathPrefix("/swagger").Handler(httpSwagger.WrapHandler)
}
