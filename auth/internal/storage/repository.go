package storage

import (
	models "auth/internal/models"
	utils "auth/internal/utils"
	"database/sql"
)

type repository struct {
	db *sql.DB
}

func NewAuthRepository(dbConnection *sql.DB) AuthRepository {
	return &repository{
		db: dbConnection,
	}
}

func (r *repository) AddUser(user *models.UserCredentials) (*models.UserCredentials, error) {
	user.Password = utils.EncryptString(user.Password)
	user.Id, _ = models.GenerateUuid32()

	if err := r.db.QueryRow(
		"INSERT INTO user_credentials (id, login, password, privileges) VALUES ($1, $2, $3, $4) RETURNING id",
		user.Id, user.Login, user.Password, user.Privileges,
	).Scan(&user.Id); err != nil {
		return nil, err
	}

	return user, nil
}

func (r *repository) GetUserByUsernamePassword(login string, password string) (*models.UserCredentials, error) {
	hashed_password_base64 := utils.EncryptString(password)

	user := models.UserCredentials{}

	if err := r.db.QueryRow(
		"SELECT * FROM user_credentials WHERE login = $1 AND password = $2",
		login, hashed_password_base64,
	).Scan(&user.Id, &user.Login, &user.Password, &user.Privileges, &user.CreatedAt, &user.IsActive); err != nil {
		return nil, err
	}

	return &user, nil
}

func (r *repository) GetUserById(userId string) (*models.UserCredentials, error) {
	user := models.UserCredentials{}

	if err := r.db.QueryRow(
		"SELECT * FROM user_credentials WHERE id = $1",
		userId,
	).Scan(&user.Id, &user.Login, &user.Password, &user.Privileges, &user.CreatedAt, &user.IsActive); err != nil {
		return nil, err
	}

	return &user, nil
}

func (r *repository) GetTokenById(id string) (*models.Token, error) {
	token := models.Token{}

	if err := r.db.QueryRow(
		"SELECT * FROM tokens WHERE id = $1",
		id,
	).Scan(&token.Id, &token.UserId, &token.Token, &token.IsRegular); err != nil {
		return nil, err
	}

	return &token, nil
}

func (r *repository) addToken(token *models.Token) (string, error) {
	if err := r.db.QueryRow(
		"INSERT INTO tokens (id, token, user_id, is_regular) VALUES ($1, $2, $3, $4) RETURNING id",
		token.Id, token.Token, token.UserId, token.IsRegular,
	).Scan(&token.Id); err != nil {
		return "", err
	}

	return token.Id, nil
}

func (r *repository) DeleteTokensPair(userId string) (bool, error) {
	if _, err := r.db.Query(
		"DELETE FROM tokens WHERE user_id = $1;",
		userId,
	); err != nil {
		return false, err
	}

	return true, nil
}

func (r *repository) SyncToken(tokenId string, userId string, isRegular bool) (string, error) {
	if _, err := r.db.Query(
		"DELETE FROM tokens WHERE user_id = $1 AND is_regular = $2",
		userId, isRegular,
	); err != nil {
		return "", err
	}

	res, err := r.addToken(&models.Token{
		Id:        tokenId,
		UserId:    userId,
		Token:     "tokenString",
		IsRegular: isRegular,
	})
	if err != nil {
		return "", err
	}

	return res, nil
}

func (r *repository) UpdateUser(user *models.UserCredentials) error {
	if _, err := r.db.Query(
		"UPDATE user_credentials SET login = $1, password = $2, privileges = $3 WHERE id = $4",
		user.Login, utils.EncryptString(user.Password), user.Privileges, user.Id,
	); err != nil {
		return err
	}
	return nil
}

func (r *repository) GetAllAccounts(from int, count int) ([]models.UserCredentials, error) {
	rows, err := r.db.Query(
		"SELECT * FROM user_credentials ORDER BY id OFFSET $1 ROWS FETCH NEXT $2 ROWS ONLY",
		from, count,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var accounts []models.UserCredentials
	for rows.Next() {
		var user models.UserCredentials
		if err := rows.Scan(&user.Id, &user.Login, &user.Password, &user.Privileges, &user.CreatedAt, &user.IsActive); err != nil {
			return nil, err
		}
		accounts = append(accounts, user)
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return accounts, nil
}

func (r *repository) SoftDeleteUser(userId string) error {
	if _, err := r.db.Query(
		"UPDATE user_credentials SET is_active = false WHERE id = $1;",
		userId,
	); err != nil {
		return err
	}
	return nil
}
