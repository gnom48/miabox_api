package server

import models "auth/internal/models"

func IsUserInRole(roles []models.Role, roleId string) bool {
	for _, role := range roles {
		if role.Id == roleId {
			return true
		}
	}
	return false
}
