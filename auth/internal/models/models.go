package models

type AuthPrivileges string

const (
	USER  AuthPrivileges = "USER"
	ADMIN AuthPrivileges = "ADMIN"
)

type UserCredentials struct {
	Id         string         `json:"id"`
	Login      string         `json:"login"`
	Password   string         `json:"password,omitempty"`
	Privileges AuthPrivileges `json:"privileges"`
	CreatedAt  string         `json:"created_at"`
	IsActive   bool           `json:"is_active"`
}

type Token struct {
	Id        string `json:"id"`
	UserId    string `json:"user_id"`
	Token     string `json:"token"`
	IsRegular bool   `json:"is_regular"`
	CreatedAt int64  `json:"created_at"`
}
