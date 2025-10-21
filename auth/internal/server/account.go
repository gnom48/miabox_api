package server

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"

	models "auth/internal/models"
)

type aboutMeResponseBody struct {
	User models.UserCredentials `json:"user"`
}

// @Summary Get current account
// @Description Retrieve the current account's data
// @Tags Accounts
// @Accept json
// @Produce json
// @Router /api/Accounts/Me [get]
// @Param Authorization header string true "Authorization header"
func (s *ApiServer) HandleGetCurrentAccount() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		user, ok := r.Context().Value(UserContextKey).(models.UserCredentials)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}

		user.Password = ""
		s.Respond(w, r, http.StatusOK, aboutMeResponseBody{
			User: user,
		})
	}
}

type updateAccountRequestBody struct {
	Login    string `json:"login"`
	Password string `json:"password"`
}

// @Summary Update account
// @Description Update the current account's information
// @Tags Accounts
// @Accept json
// @Produce json
// @Param requestBody body updateAccountRequestBody true "Account Update Data"
// @Router /api/Accounts/Update [put]
// @Param Authorization header string true "Authorization header"
func (s *ApiServer) HandleUpdateAccount() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		user, ok := r.Context().Value(UserContextKey).(models.UserCredentials)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}

		requestBody := &updateAccountRequestBody{}
		if err := json.NewDecoder(r.Body).Decode(requestBody); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		user.Login = requestBody.Login
		user.Password = requestBody.Password

		if err := s.storage.GetUsecase().UpdateUser(&user); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		s.Respond(w, r, http.StatusMultiStatus, nil)
	}
}

type createAccountRequestBody struct {
	Login      string                `json:"login"`
	Password   string                `json:"password"`
	Privileges models.AuthPrivileges `json:"privileges"`
	UserExtras models.UserExtras     `json:"extras"`
}

// @Summary Create a new account
// @Description Create a new user account by admin
// @Tags Accounts
// @Accept json
// @Produce json
// @Param requestBody body createAccountRequestBody true "Account Creation Data"
// @Router /api/Accounts [post]
// @Param Authorization header string true "Authorization header"
func (s *ApiServer) HandleCreateAccount() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		user, ok := r.Context().Value(UserContextKey).(models.UserCredentials)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}
		if user.Privileges != models.ADMIN {
			s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access forbidden"))
			return
		}

		requestBody := &createAccountRequestBody{}
		if err := json.NewDecoder(r.Body).Decode(requestBody); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		newUser := &models.UserCredentials{
			Login:      requestBody.Login,
			Privileges: requestBody.Privileges,
			Password:   requestBody.Password,
		}

		requestBody.UserExtras.SetDefaultsIfNil()

		if returning, err := s.storage.GetUsecase().AddUser(context.Background(), newUser, &requestBody.UserExtras); err != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, err)
			return
		} else {
			s.Respond(w, r, http.StatusCreated, struct {
				NewUserId string `json:"new_user_id"`
			}{
				NewUserId: returning.Id,
			})
		}
	}
}

type getAllAccountsResponseBody struct {
	Accounts []models.UserCredentials `json:"accounts"`
}

// @Summary Get all accounts
// @Description Retrieve a list of all accounts
// @Tags Accounts
// @Accept json
// @Produce json
// @Param from query int false "Start index"
// @Param count query int false "Number of records"
// @Router /api/Accounts [get]
// @Param Authorization header string true "Authorization header"
func (s *ApiServer) HandleGetAllAccounts() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		user, ok := r.Context().Value(UserContextKey).(models.UserCredentials)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}
		if user.Privileges != models.ADMIN {
			s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access forbidden"))
			return
		}

		fromParam := r.URL.Query().Get("from")
		countParam := r.URL.Query().Get("count")

		from, err := strconv.Atoi(fromParam)
		if err != nil {
			http.Error(w, "Invalid 'from' parameter", http.StatusBadRequest)
			return
		}

		count, err := strconv.Atoi(countParam)
		if err != nil {
			http.Error(w, "Invalid 'count' parameter", http.StatusBadRequest)
			return
		}

		accounts, err := s.storage.GetUsecase().GetAllAccounts(from, count)
		if err != nil {
			s.ErrorRespond(w, r, http.StatusInternalServerError, err)
			return
		}

		s.Respond(w, r, http.StatusOK, getAllAccountsResponseBody{Accounts: accounts})
	}
}

// @Summary Update account by Id
// @Description Update a user account by Id
// @Tags Accounts
// @Accept json
// @Produce json
// @Param id path string true "User Id"
// @Param requestBody body createAccountRequestBody true "Account Details"
// @Router /api/Accounts/{id} [put]
// @Param Authorization header string true "Authorization header"
func (s *ApiServer) HandleUpdateAccountById() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		user, ok := r.Context().Value(UserContextKey).(models.UserCredentials)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}
		if user.Privileges != models.ADMIN {
			s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access forbidden"))
			return
		}

		id := r.URL.Path[len("/api/Accounts/"):]
		requestBody := &createAccountRequestBody{}
		if err := json.NewDecoder(r.Body).Decode(requestBody); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		editableUser := models.UserCredentials{
			Id:         id,
			Login:      requestBody.Login,
			Privileges: requestBody.Privileges,
			Password:   requestBody.Password,
			IsActive:   true,
		}

		if err := s.storage.GetUsecase().UpdateUser(&editableUser); err != nil {
			s.ErrorRespond(w, r, http.StatusInternalServerError, err)
		} else {
			s.Respond(w, r, http.StatusMultiStatus, struct {
				UserId string `json:"user_id"`
			}{
				UserId: editableUser.Id,
			})
		}
	}
}

// @Summary Soft delete an account by ID
// @Description Soft delete a user account by ID
// @Tags Accounts
// @Param id path string true "User Id"
// @Router /api/Accounts/{id} [delete]
// @Param Authorization header string true "Authorization header"
func (s *ApiServer) HandleSoftDeleteAccountById() http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		user, ok := r.Context().Value(UserContextKey).(models.UserCredentials)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}
		if user.Privileges != models.ADMIN {
			s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access forbidden"))
			return
		}

		id := r.URL.Path[len("/api/Accounts/"):]
		if err := s.storage.GetUsecase().SoftDeleteUser(id); err != nil {
			s.ErrorRespond(w, r, http.StatusInternalServerError, err)
			return
		}
		s.Respond(w, r, http.StatusOK, nil)
	}
}
