package server

import (
	"encoding/json"
	"fmt"
	"net/http"

	models "auth/internal/models"
)

var tokenError = fmt.Errorf("Invalid token, refresh or sign in to get a new pair")

type signUpRequestBody struct {
	LastName  string `json:"last_name"`
	FirstName string `json:"first_name"`
	Username  string `json:"username"`
	Password  string `json:"password"`
}

// @Summary SignUp
// @Description SignUp
// @Tags Authentication
// @Accept json
// @Produce json
// @Param requestBody body signUpRequestBody true "User Credentials"
// @Router /api/Authentication/SignUp [post]
func (s *ApiServer) HandleAuthenticationSignUp() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		requestBody := &signUpRequestBody{}
		if err := json.NewDecoder(r.Body).Decode(requestBody); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		user := &models.User{
			FirstName: requestBody.FirstName,
			LastName:  requestBody.LastName,
			Username:  requestBody.Username,
			Password:  requestBody.Password,
		}
		defer s.storage.Close()
		if returning, err := s.storage.Repository().AddUser(user); err != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, err)
		} else {
			s.Respond(w, r, http.StatusCreated, returning.Id)
		}
	}
}

type signInRequestBody struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type TokensPairResponseBody struct {
	CreationToken string `json:"creation_token"`
	RegularToken  string `json:"regular_token"`
}

// @Summary Sign in a user
// @Description Authenticates a user based on their username and password and generates tokens
// @Tags Authentication
// @Accept json
// @Produce json
// @Param requestBody body signInRequestBody true "User Credentials"
// @Router /api/Authentication/SignIn [post]
func (s *ApiServer) HandleAuthenticationSignIn() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		requestBody := &signInRequestBody{}
		if err := json.NewDecoder(r.Body).Decode(requestBody); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		defer s.storage.Close()
		user, err := s.storage.Repository().GetUserByUsernamePassword(requestBody.Username, requestBody.Password)
		if err != nil {
			s.ErrorRespond(w, r, http.StatusNotFound, fmt.Errorf("User not found"))
			return
		}

		creationToken, creationTokenId, cte := s.tokenSigner.GenerateCreationToken(user)
		regularToken, regularTokenId, rte := s.tokenSigner.GenerateRegularToken(user)
		if cte != nil || rte != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Errors: "+cte.Error()+"; "+rte.Error()))
			return
		}

		if _, err := s.storage.Repository().SyncToken(creationTokenId, user.Id, false); err != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Error srt: %v", err))
			return
		}
		if _, err := s.storage.Repository().SyncToken(regularTokenId, user.Id, true); err != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Error sct: %v", err))
			return
		}

		s.Respond(w, r, http.StatusCreated, TokensPairResponseBody{
			CreationToken: creationToken,
			RegularToken:  regularToken,
		})
	}
}

// @Summary SignOut
// @Description Delete token pair by creation token
// @Tags Authentication
// @Accept json
// @Produce json
// @Router /api/Authentication/SignOut [head]
// @Param Authorization header string true "Authorization header"
func (s *ApiServer) HandleAuthenticationSignOut() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		user, ok := r.Context().Value(UserContextKey).(models.User)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
		}

		defer s.storage.Close()
		res, err := s.storage.Repository().DeleteTokensPair(user.Id)
		if !res {
			s.ErrorRespond(w, r, http.StatusUnauthorized, err)
		}

		s.Respond(w, r, http.StatusOK, nil)
	}
}

// @Summary Validate
// @Description Validate regular token
// @Tags Authentication
// @Accept json
// @Produce json
// @Router /api/Authentication/Validate [get]
// @Param AccessToken query string true "Authorization header"
func (s *ApiServer) HandleAuthenticationValidate() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		params := r.URL.Query()
		accessToken := params.Get("AccessToken")
		data, e := s.tokenSigner.ValidateRegularToken(accessToken)
		if e != nil {
			s.ErrorRespond(w, r, http.StatusUnauthorized, e)
			return
		}

		defer s.storage.Close()
		if token, err := s.storage.Repository().GetTokenById(data.ID); err != nil || token == nil {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("Token revoked"))
			return
		}

		s.Respond(w, r, http.StatusOK, data)

	}
}

// @Summary Refresh
// @Description Refresh token pair by creation token
// @Tags Authentication
// @Accept json
// @Produce json
// @Router /api/Authentication/Refresh [get]
// @Param Authorization header string true "Authorization header (creation token)"
func (s *ApiServer) HandleAuthenticationRefresh() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		user, ok := r.Context().Value(UserContextKey).(models.User)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
		}

		creationToken, creationTokenId, cte := s.tokenSigner.GenerateCreationToken(&user)
		regularToken, regularTokenId, rte := s.tokenSigner.GenerateRegularToken(&user)
		if cte != nil || rte != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Errors: %v", cte, rte))
			return
		}

		defer s.storage.Close()
		if _, err := s.storage.Repository().SyncToken(creationTokenId, user.Id, false); err != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Error: %v", err))
			return
		}
		if _, err := s.storage.Repository().SyncToken(regularTokenId, user.Id, true); err != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Error: %v", err))
			return
		}

		s.Respond(w, r, http.StatusCreated, TokensPairResponseBody{
			CreationToken: creationToken,
			RegularToken:  regularToken,
		})
	}
}
