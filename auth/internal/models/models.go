package models

import (
	"time"
)

type User struct {
	Id        string    `json:"id"`
	LastName  string    `json:"last_name"`
	FirstName string    `json:"first_name"`
	Username  string    `json:"username"`
	Password  string    `json:"password,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	IsActive  bool      `json:"is_active"`
}

type Token struct {
	Id        string `json:"id"`
	UserId    string `json:"user_id"`
	Token     string `json:"token"`
	IsRegular bool   `json:"is_regular"`
}

type Role struct {
	Id   string `json:"id"`
	Name string `json:"name"`
}

type UserRole struct {
	UserId string `json:"user_id"`
	RoleId string `json:"role_id"`
}
