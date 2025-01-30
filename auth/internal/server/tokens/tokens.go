package tokens

import (
	"fmt"
	"time"

	models "auth/internal/models"

	"github.com/dgrijalva/jwt-go/v4"
)

type TokenSigner interface {
	GenerateRegularToken(*models.User) (string, string, error)
	GenerateCreationToken(*models.User) (string, string, error)
	ValidateCreationToken(string) (*CreationClaims, error)
	ValidateRegularToken(string) (*RegularClaims, error)
}

type TokenSign struct{}

type RegularClaims struct {
	UserId string `json:"user_id"`
	jwt.StandardClaims
}

type CreationClaims struct {
	UserId   string `json:"user_id"`
	Username string `json:"username"`
	Password string `json:"password"`
	jwt.StandardClaims
}

const regularTokenType string = "regular"
const creationTokenType string = "creation"

func (t *TokenSign) GenerateRegularToken(user *models.User) (string, string, error) {
	tokenId, _ := models.GenerateUuid32()
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, &RegularClaims{
		UserId: user.Id,
		StandardClaims: jwt.StandardClaims{
			ID:        tokenId,
			ExpiresAt: jwt.At(time.Now().Add(15 * time.Minute)),
			IssuedAt:  jwt.At(time.Now()),
			Subject:   regularTokenType,
		},
	})
	tokenString, err := token.SignedString([]byte(SecretKey))
	if err != nil {
		return "", "", err
	}
	return tokenString, tokenId, nil
}

func (t *TokenSign) GenerateCreationToken(user *models.User) (string, string, error) {
	tokenId, _ := models.GenerateUuid32()
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, &CreationClaims{
		UserId:   user.Id,
		Username: user.Username,
		Password: user.Password,
		StandardClaims: jwt.StandardClaims{
			ID:        tokenId,
			ExpiresAt: jwt.At(time.Now().Add(24 * 7 * time.Hour)),
			IssuedAt:  jwt.At(time.Now()),
			Subject:   creationTokenType,
		},
	})
	tokenString, err := token.SignedString([]byte(SecretKey))
	if err != nil {
		return "", "", err
	}
	return tokenString, tokenId, nil
}

func (t *TokenSign) ValidateRegularToken(tokenString string) (*RegularClaims, error) {
	token, err := jwt.ParseWithClaims(
		tokenString,
		&RegularClaims{},
		func(token *jwt.Token) (interface{}, error) {
			if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("Unexpected signing method: %v", token.Header["alg"])
			}
			return []byte(SecretKey), nil
		})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*RegularClaims); ok && token.Valid {
		if claims.Subject != regularTokenType {
			return nil, fmt.Errorf("Invalid token type")
		}
		if claims.ExpiresAt.Unix() < time.Now().Unix() {
			return nil, fmt.Errorf("Token has expired, refresh it")
		}
		return claims, nil
	}

	return nil, err
}

func (t *TokenSign) ValidateCreationToken(tokenString string) (*CreationClaims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &CreationClaims{}, func(token *jwt.Token) (interface{}, error) {
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, fmt.Errorf("Unexpected signing method: %v", token.Header["alg"])
		}
		return []byte(SecretKey), nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(*CreationClaims); ok && token.Valid {
		if claims.Subject != creationTokenType {
			return nil, fmt.Errorf("Invalid token type")
		}
		return claims, nil
	}

	return nil, err
}
