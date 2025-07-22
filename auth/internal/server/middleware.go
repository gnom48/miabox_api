package server

import (
	"bytes"
	"context"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"

	_ "auth/internal/server/docs"
)

type StringContextKey string

var UserContextKey StringContextKey = "user"

func (s *ApiServer) AuthRegularTokenMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		tokenString := r.Header.Get("Authorization")
		if tokenString == "" {
			http.Error(w, "Authorization header is empty", http.StatusUnauthorized)
			return
		}

		claims, err := s.tokenSigner.ValidateRegularToken(tokenString)
		if err != nil {
			s.ErrorRespond(w, r, http.StatusUnauthorized, err)
			return
		}

		if token, err := s.storage.GetRepository().GetTokenById(claims.ID); err != nil || token == nil {
			s.ErrorRespond(w, r, http.StatusUnauthorized, tokenError)
			return
		}

		user, err := s.storage.GetRepository().GetUserById(claims.UserId)
		if err != nil {
			s.ErrorRespond(w, r, http.StatusUnauthorized, tokenError)
			return
		}

		ctx := context.WithValue(r.Context(), UserContextKey, *user)
		next.ServeHTTP(w, r.WithContext(ctx))
	}
}

func (s *ApiServer) AuthCreationTokenMiddleware(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		tokenString := r.Header.Get("Authorization")
		if tokenString == "" {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("Authorization header is empty"))
			return
		}

		claims, err := s.tokenSigner.ValidateCreationToken(tokenString)
		if err != nil {
			s.ErrorRespond(w, r, http.StatusUnauthorized, err)
			return
		}

		token, err := s.storage.GetRepository().GetTokenById(claims.ID)
		if err != nil || token == nil {
			s.ErrorRespond(w, r, http.StatusUnauthorized, tokenError)
			return
		}

		user, err := s.storage.GetRepository().GetUserByUsernamePassword(claims.Login, claims.Password, true)
		if err != nil {
			s.ErrorRespond(w, r, http.StatusUnauthorized, tokenError)
			return
		}

		ctx := context.WithValue(r.Context(), UserContextKey, *user)
		next.ServeHTTP(w, r.WithContext(ctx))
	}
}

func (s *ApiServer) loggingMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		headers := &strings.Builder{}
		headers.Write([]byte("["))
		if s.config.LogHeaders {
			for key, values := range r.Header {
				for _, value := range values {
					headers.Write([]byte(key + " = " + value + ", "))
				}
			}
		}
		headers.Write([]byte("]"))

		bodyBytes := make([]byte, 0)
		if s.config.LogBody {
			bodyBytes, _ = ioutil.ReadAll(r.Body)
			r.Body = ioutil.NopCloser(bytes.NewBuffer(bodyBytes))
		}

		queryParams := ""
		if s.config.LogQueryParams {
			queryParams = r.URL.Query().Encode()
		}

		s.logger.Info("Method: " + r.Method + " | Path: " + r.URL.Path + " | Headers: " + headers.String() + " | Body: " + string(bodyBytes) + " | Query: " + queryParams)

		next.ServeHTTP(w, r)
	})
}

func (s *ApiServer) internalServerErrorMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				s.ErrorRespond(w, r, http.StatusNotImplemented, fmt.Errorf("Internal Server Error: %v", err))
			}
		}()
		next.ServeHTTP(w, r)
	})
}
