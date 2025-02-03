package storage

import (
	models "auth/internal/models"
)

type Repository struct {
	storage *Storage
}

func (r *Repository) AddUser(user *models.UserCredentials) (*models.UserCredentials, error) {
	hashed_password_base64 := EncryptString(user.Password)
	user.Password = hashed_password_base64
	user.Id, _ = models.GenerateUuid32()

	if err := r.storage.db.QueryRow(
		"INSERT INTO users (id, login, password, privileges) VALUES ($1, $2, $3, $4, $5) RETURNING id",
		user.Id, user.Login, hashed_password_base64, user.Privileges,
	).Scan(&user.Id); err != nil {
		return nil, err
	}

	return user, nil
}

func (r *Repository) GetUserByUsernamePassword(login string, password string) (*models.UserCredentials, error) {
	hashed_password_base64 := EncryptString(password)

	user := models.UserCredentials{}

	if err := r.storage.db.QueryRow(
		"SELECT * FROM users WHERE login = $1 AND password = $2",
		login, hashed_password_base64,
	).Scan(&user.Id, &user.Login, &user.Password, &user.Privileges, &user.CreatedAt, &user.IsActive); err != nil {
		return nil, err
	}

	return &user, nil
}

func (r *Repository) GetUserById(userId string) (*models.UserCredentials, error) {
	user := models.UserCredentials{}

	if err := r.storage.db.QueryRow(
		"SELECT * FROM users WHERE id = $1",
		userId,
	).Scan(&user.Id, &user.Login, &user.Password, &user.Privileges, &user.CreatedAt, &user.IsActive); err != nil {
		return nil, err
	}

	return &user, nil
}

func (r *Repository) GetTokenById(id string) (*models.Token, error) {
	token := models.Token{}

	if err := r.storage.db.QueryRow(
		"SELECT * FROM tokens WHERE id = $1",
		id,
	).Scan(&token.Id, &token.UserId, &token.Token, &token.IsRegular); err != nil {
		return nil, err
	}

	return &token, nil
}

func (r *Repository) addToken(token *models.Token) (string, error) {
	if err := r.storage.db.QueryRow(
		"INSERT INTO tokens (id, token, user_id, is_regular) VALUES ($1, $2, $3, $4) RETURNING id",
		token.Id, token.Token, token.UserId, token.IsRegular,
	).Scan(&token.Id); err != nil {
		return "", err
	}

	return token.Id, nil
}

func (r *Repository) DeleteTokensPair(userId string) (bool, error) {
	if _, err := r.storage.db.Query(
		"DELETE FROM tokens WHERE user_id = $1;",
		userId,
	); err != nil {
		return false, err
	}

	return true, nil
}

func (r *Repository) SyncToken(tokenId string, userId string, isRegular bool) (string, error) {
	if _, err := r.storage.db.Query(
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

func (r *Repository) UpdateUser(user *models.UserCredentials) error {
	if _, err := r.storage.db.Query(
		"UPDATE users SET login = $1, password = $2, privileges = $3 WHERE id = $4",
		user.Login, EncryptString(user.Password), user.Privileges, user.Id,
	); err != nil {
		return err
	}
	return nil
}

func (r *Repository) GetAllAccounts(from int, count int) ([]models.UserCredentials, error) {
	rows, err := r.storage.db.Query(
		"SELECT * FROM users ORDER BY id OFFSET $1 ROWS FETCH NEXT $2 ROWS ONLY",
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

func (r *Repository) SoftDeleteUser(userId string) error {
	if _, err := r.storage.db.Query(
		"UPDATE users SET is_active = false WHERE id = $1;",
		userId,
	); err != nil {
		return err
	}
	return nil
}
