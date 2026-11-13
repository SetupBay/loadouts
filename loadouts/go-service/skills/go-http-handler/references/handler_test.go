package items

import (
	"io"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestHandlers(t *testing.T) {
	srv := NewServer(slog.New(slog.NewTextHandler(io.Discard, nil)))
	h := srv.Routes()

	tests := []struct {
		name, method, path, body string
		want                     int
	}{
		{"create", "POST", "/items", `{"name":"Tea","price_pence":250}`, http.StatusCreated},
		{"read created", "GET", "/items/1", "", http.StatusOK},
		{"missing", "GET", "/items/99", "", http.StatusNotFound},
		{"bad id", "GET", "/items/abc", "", http.StatusBadRequest},
		{"unknown field", "POST", "/items", `{"name":"Tea","colour":"red"}`, http.StatusBadRequest},
		{"negative price", "POST", "/items", `{"name":"Tea","price_pence":-1}`, http.StatusBadRequest},
		{"wrong method", "DELETE", "/items/1", "", http.StatusMethodNotAllowed},
	}
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			req := httptest.NewRequest(tc.method, tc.path, strings.NewReader(tc.body))
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if rec.Code != tc.want {
				t.Fatalf("%s %s: got %d, want %d (%s)", tc.method, tc.path, rec.Code, tc.want, rec.Body.String())
			}
		})
	}
}
