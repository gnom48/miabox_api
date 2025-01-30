package server

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strconv"

	models "auth/internal/models"
)

type aboutMeResponseBody struct {
	User  models.User   `json:"user"`
	Roles []models.Role `json:"roles"`
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
		user, ok := r.Context().Value(UserContextKey).(models.User)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}
		roles, ok := r.Context().Value(RoleContextKey).([]models.Role)
		if !ok {
			s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access denied"))
			return
		}

		s.Respond(w, r, http.StatusOK, aboutMeResponseBody{
			User:  user,
			Roles: roles,
		})
	}
}

type updateAccountRequestBody struct {
	LastName  string `json:"last_name"`
	FirstName string `json:"first_name"`
	Password  string `json:"password"`
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
		user, ok := r.Context().Value(UserContextKey).(models.User)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}

		requestBody := &updateAccountRequestBody{}
		if err := json.NewDecoder(r.Body).Decode(requestBody); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		user.LastName = requestBody.LastName
		user.FirstName = requestBody.FirstName
		user.Password = requestBody.Password

		defer s.storage.Close()
		if err := s.storage.Repository().UpdateUser(&user); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		s.Respond(w, r, http.StatusMultiStatus, nil)
	}
}

type createAccountRequestBody struct {
	LastName  string   `json:"last_name"`
	FirstName string   `json:"first_name"`
	Username  string   `json:"username"`
	Password  string   `json:"password"`
	Roles     []string `json:"roles"`
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
		_, ok := r.Context().Value(UserContextKey).(models.User)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}
		roles, ok := r.Context().Value(RoleContextKey).([]models.Role)
		if !ok {
			s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access forbidden"))
			return
		} else {
			if !IsUserInRole(roles, "0") {
				s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access only for admin"))
				return
			}
		}

		requestBody := &createAccountRequestBody{}
		if err := json.NewDecoder(r.Body).Decode(requestBody); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		newUser := &models.User{
			LastName:  requestBody.LastName,
			FirstName: requestBody.FirstName,
			Username:  requestBody.Username,
			Password:  requestBody.Password,
		}

		defer s.storage.Close()
		if returning, err := s.storage.Repository().AddUser(newUser); err != nil {
			s.ErrorRespond(w, r, http.StatusUnprocessableEntity, err)
			return
		} else {
			currentErrors := make([]string, 0)
			for _, roleName := range requestBody.Roles {
				if e := s.storage.Repository().AddUserRole(returning.Id, roleName); e != nil {
					currentErrors = append(currentErrors, e.Error())
				}
			}
			s.Respond(w, r, http.StatusCreated, struct {
				NewUserId string   `json:"new_user_id"`
				Errors    []string `json:"errors"`
			}{
				NewUserId: returning.Id,
				Errors:    currentErrors,
			})
		}
	}
}

type getAllAccountsResponseBody struct {
	Accounts []models.User `json:"accounts"`
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
		_, ok := r.Context().Value(UserContextKey).(models.User)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}
		roles, ok := r.Context().Value(RoleContextKey).([]models.Role)
		if !ok {
			s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access forbidden"))
			return
		} else {
			if !IsUserInRole(roles, "0") {
				s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access only for admin"))
				return
			}
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

		defer s.storage.Close()
		accounts, err := s.storage.Repository().GetAllAccounts(from, count)
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
		_, ok := r.Context().Value(UserContextKey).(models.User)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}
		roles, ok := r.Context().Value(RoleContextKey).([]models.Role)
		if !ok {
			s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access forbidden"))
			return
		} else {
			if !IsUserInRole(roles, "0") {
				s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access only for admin"))
				return
			}
		}

		id := r.URL.Path[len("/api/Accounts/"):]
		requestBody := &createAccountRequestBody{}
		if err := json.NewDecoder(r.Body).Decode(requestBody); err != nil {
			s.ErrorRespond(w, r, http.StatusBadRequest, err)
			return
		}

		editableUser := models.User{
			Id:        id,
			LastName:  requestBody.LastName,
			FirstName: requestBody.FirstName,
			Username:  requestBody.Username,
			Password:  requestBody.Password,
		}

		defer s.storage.Close()
		if err := s.storage.Repository().UpdateUser(&editableUser); err != nil {
			s.ErrorRespond(w, r, http.StatusInternalServerError, err)
		} else {
			currentErrors := make([]string, 0)
			_, e := s.storage.Repository().DeleteAllUserRoles(editableUser.Id)
			if e != nil {
				currentErrors = append(currentErrors, e.Error())
			}
			for _, r := range requestBody.Roles {
				if e := s.storage.Repository().AddUserRole(id, r); e != nil {
					currentErrors = append(currentErrors, e.Error())
				}
			}

			s.Respond(w, r, http.StatusMultiStatus, struct {
				UserId string   `json:"user_id"`
				Errors []string `json:"errors"`
			}{
				UserId: editableUser.Id,
				Errors: currentErrors,
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
		_, ok := r.Context().Value(UserContextKey).(models.User)
		if !ok {
			s.ErrorRespond(w, r, http.StatusUnauthorized, fmt.Errorf("User not found"))
			return
		}
		roles, ok := r.Context().Value(RoleContextKey).([]models.Role)
		if !ok {
			s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access forbidden"))
			return
		} else {
			if !IsUserInRole(roles, "0") {
				s.ErrorRespond(w, r, http.StatusForbidden, fmt.Errorf("Access only for admin"))
				return
			}
		}

		id := r.URL.Path[len("/api/Accounts/"):]
		defer s.storage.Close()
		if err := s.storage.Repository().SoftDeleteUser(id); err != nil {
			s.ErrorRespond(w, r, http.StatusInternalServerError, err)
			return
		}
		s.Respond(w, r, http.StatusOK, nil)
	}
}
