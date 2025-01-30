package server

import (
	"encoding/json"
	"net/http"
)

func (s *ApiServer) Respond(w http.ResponseWriter, r *http.Request, code int, data interface{}) {
	w.WriteHeader(code)
	if data != nil {
		json.NewEncoder(w).Encode(data)
	}
}

func (s *ApiServer) ErrorRespond(w http.ResponseWriter, r *http.Request, code int, err error) {
	s.logger.Error(err)
	s.Respond(w, r, code, map[string]string{"server_error": err.Error()})
}
