package storage

import (
	models "auth/internal/models"
	"context"
)

type AuthUsecase struct {
	repository AuthRepository
}

func (u *AuthUsecase) AddUser(user *models.UserCredentials, userExtras *models.UserExtras) <-chan *models.UserCredentials {
	resultChan := make(chan *models.UserCredentials, 1)
	go func() {
		addedUser, err := u.repository.AddUser(context.Background(), user, userExtras)
		if err != nil {
			resultChan <- nil
		} else {
			resultChan <- addedUser
		}
		close(resultChan)
	}()
	return resultChan
}
