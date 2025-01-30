package storage

import (
	"crypto/sha256"
	"encoding/base64"
)

func EncryptString(str string) string {
	encryptor := sha256.New()
	encryptor.Write([]byte(str))
	hashed_str := encryptor.Sum(nil)
	hashed_str_base64 := base64.StdEncoding.EncodeToString(hashed_str)
	return hashed_str_base64
}
