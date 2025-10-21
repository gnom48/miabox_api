package server

import (
	"encoding/json"
	"fmt"
	"net/http"

	models "auth/internal/models"
)

type signUpRequestBody struct {
	Login      string            `json:"login"`
	Password   string            `json:"password"`
	UserExtras models.UserExtras `json:"extras"`
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

		user := &models.UserCredentials{
			Login:      requestBody.Login,
			Password:   requestBody.Password,
			Privileges: models.USER,
			IsActive:   true,
		}

		requestBody.UserExtras.SetDefaultsIfNil()

		ch := s.storage.GetUsecase().AddUser(user, &requestBody.UserExtras)
		select {
		case user := <-ch:
			if user != nil {
				s.logger.Debug("Получен пользователь: %+v\n", user)
				s.Respond(w, r, http.StatusCreated, user.Id)
			} else {
				s.logger.Warn("Ошибка при получении пользователя.")
				s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Ошибка при получении пользователя."))
			}
		}
	}
}

type signInRequestBody struct {
	Login    string `json:"login"`
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

		user, err := s.storage.GetUsecase().GetUserByUsernamePassword(requestBody.Login, requestBody.Password, false)
		if err != nil {
			s.ErrorRespond(w, r, http.StatusNotFound, fmt.Errorf("User not found"))
			return
		}

		creationToken, regularToken, no_tokens_error := s.storage.GetUsecase().GetTokenByUserId(user.Id) // NOTE: обязательно в таком порядке т.к. сортировка по is_regular ASC

		if creationToken != nil && regularToken != nil {
			_, creationTokenValidateError := s.tokenSigner.ValidateCreationToken(creationToken.Token)
			_, regularTokenValidateError := s.tokenSigner.ValidateRegularToken(regularToken.Token)
			if creationTokenValidateError != nil || regularTokenValidateError != nil {
				no_tokens_error = fmt.Errorf("Need new tokens pair")
			}
		}

		if no_tokens_error != nil {
			creationTokenValue, creationTokenId, cte := s.tokenSigner.GenerateCreationToken(user)
			regularTokenValue, regularTokenId, rte := s.tokenSigner.GenerateRegularToken(user)
			if cte != nil || rte != nil {
				s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("%s", "Errors: "+cte.Error()+"; "+rte.Error()))
				return
			}

			if _, err := s.storage.GetUsecase().SyncToken(creationTokenId, user.Id, false, creationTokenValue); err != nil {
				s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Error srt: %v", err))
				return
			}
			if _, err := s.storage.GetUsecase().SyncToken(regularTokenId, user.Id, true, regularTokenValue); err != nil {
				s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Error sct: %v", err))
				return
			}

			s.Respond(w, r, http.StatusCreated, TokensPairResponseBody{
				CreationToken: creationTokenValue,
				RegularToken:  regularTokenValue,
			})
			return
		}

		s.Respond(w, r, http.StatusCreated, TokensPairResponseBody{
			CreationToken: creationToken.Token,
			RegularToken:  regularToken.Token,
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
		user, ok := r.Context().Value(UserContextKey).(models.UserCredentials)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
		}

		res, err := s.storage.GetUsecase().DeleteTokensPair(user.Id)
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

		if token, err := s.storage.GetUsecase().GetTokenById(data.ID); err != nil || token == nil {
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
		user, ok := r.Context().Value(UserContextKey).(models.UserCredentials)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
		}

		creationToken, creationTokenId, cte := s.tokenSigner.GenerateCreationToken(&user)
		regularToken, regularTokenId, rte := s.tokenSigner.GenerateRegularToken(&user)
		if cte != nil || rte != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Errors: %v", cte, rte))
			return
		}

		if _, err := s.storage.GetUsecase().SyncToken(creationTokenId, user.Id, false, creationToken); err != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Error: %v", err))
			return
		}
		if _, err := s.storage.GetUsecase().SyncToken(regularTokenId, user.Id, true, regularToken); err != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, fmt.Errorf("Error: %v", err))
			return
		}

		s.Respond(w, r, http.StatusCreated, TokensPairResponseBody{
			CreationToken: creationToken,
			RegularToken:  regularToken,
		})
	}
}
