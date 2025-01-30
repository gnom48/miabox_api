package storage

import (
	models "auth/internal/models"
)

type Repository struct {
	storage *Storage
}

func (r *Repository) AddUser(user *models.User) (*models.User, error) {
	hashed_password_base64 := EncryptString(user.Password)
	user.Password = hashed_password_base64
	user.Id, _ = models.GenerateUuid32()

	if err := r.storage.db.QueryRow(
		"INSERT INTO users (id, last_name, first_name, username, password) VALUES ($1, $2, $3, $4, $5) RETURNING id",
		user.Id, user.LastName, user.FirstName, user.Username, hashed_password_base64,
	).Scan(&user.Id); err != nil {
		return nil, err
	}

	return user, nil
}

func (r *Repository) GetUserByUsernamePassword(username string, password string) (*models.User, error) {
	hashed_password_base64 := EncryptString(password)

	user := models.User{}

	if err := r.storage.db.QueryRow(
		"SELECT * FROM users WHERE username = $1 AND password = $2",
		username, hashed_password_base64,
	).Scan(&user.Id, &user.LastName, &user.FirstName, &user.Username, &user.Password, &user.CreatedAt, &user.IsActive); err != nil {
		return nil, err
	}

	return &user, nil
}

func (r *Repository) GetUserById(userId string) (*models.User, error) {
	user := models.User{}

	if err := r.storage.db.QueryRow(
		"SELECT * FROM users WHERE id = $1",
		userId,
	).Scan(&user.Id, &user.LastName, &user.FirstName, &user.Username, &user.Password, &user.CreatedAt, &user.IsActive); err != nil {
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

func (r *Repository) UpdateUser(user *models.User) error {
	if _, err := r.storage.db.Query(
		"UPDATE users SET last_name = $1, first_name = $2, password = $3 WHERE id = $4",
		user.LastName, user.FirstName, EncryptString(user.Password), user.Id,
	); err != nil {
		return err
	}
	return nil
}

func (r *Repository) GetAllAccounts(from int, count int) ([]models.User, error) {
	rows, err := r.storage.db.Query(
		"SELECT * FROM users ORDER BY id OFFSET $1 ROWS FETCH NEXT $2 ROWS ONLY",
		from, count,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var accounts []models.User
	for rows.Next() {
		var user models.User
		if err := rows.Scan(&user.Id, &user.LastName, &user.FirstName, &user.Username, &user.Password, &user.CreatedAt, &user.IsActive); err != nil {
			return nil, err
		}
		accounts = append(accounts, user)
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return accounts, nil
}

func (r *Repository) GetAllUserRoles(userId string) ([]models.Role, error) {
	rows, err := r.storage.db.Query(
		"SELECT * FROM roles WHERE id IN (SELECT role_id FROM user_roles WHERE user_id = $1)",
		userId,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var roles []models.Role
	for rows.Next() {
		var r models.Role
		if err := rows.Scan(&r.Id, &r.Name); err != nil {
			return nil, err
		}
		roles = append(roles, r)
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return roles, nil
}

func (r *Repository) AddUserRole(userId string, roleName string) error {
	if _, err := r.storage.db.Query(
		"INSERT INTO user_roles (user_id, role_id) VALUES ($1, (SELECT id FROM roles WHERE name = $2 LIMIT 1));",
		userId, roleName,
	); err != nil {
		return err
	} else {
		return nil
	}
}

func (r *Repository) DeleteAllUserRoles(userId string) (int, error) {
	res, err := r.storage.db.Exec(
		"DELETE FROM user_roles WHERE user_id = $1",
		userId,
	)
	if err != nil {
		return 0, err
	}

	returning, err := res.RowsAffected()
	if err != nil {
		return 0, err
	}

	return int(returning), nil
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
