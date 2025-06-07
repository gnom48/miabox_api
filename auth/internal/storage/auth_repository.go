package storage

import models "auth/internal/models"

type AuthRepository interface {
	AddUser(user *models.UserCredentials) (*models.UserCredentials, error)
	DeleteTokensPair(userId string) (bool, error)
	GetAllAccounts(from int, count int) ([]models.UserCredentials, error)
	GetTokenById(id string) (*models.Token, error)
	GetTokenByUserId(id string) (*models.Token, *models.Token, error)
	GetUserById(userId string) (*models.UserCredentials, error)
	GetUserByUsernamePassword(login string, password string, checkWithoutHash bool) (*models.UserCredentials, error)
	SoftDeleteUser(userId string) error
	SyncToken(tokenId string, userId string, isRegular bool, tokenString string) (string, error)
	UpdateUser(user *models.UserCredentials) error
	addToken(token *models.Token) (string, error)
}
