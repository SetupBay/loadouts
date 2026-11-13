// Package items is an example of a net/http handler set: Go 1.22+ routing, limited JSON bodies, errors mapped to status.
package items

import (
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"net/http"
	"strconv"
	"sync"
)

// ErrNotFound is returned when an item does not exist.
var ErrNotFound = errors.New("item not found")

// Item is the public representation of an item.
type Item struct {
	ID         int    `json:"id"`
	Name       string `json:"name"`
	PricePence int    `json:"price_pence"`
}

// Server holds dependencies for the handlers.
type Server struct {
	mu    sync.Mutex
	items map[int]Item
	log   *slog.Logger
}

// NewServer returns a Server with an empty store.
func NewServer(log *slog.Logger) *Server {
	return &Server{items: map[int]Item{}, log: log}
}

// Routes registers the handlers on a new mux.
func (s *Server) Routes() *http.ServeMux {
	mux := http.NewServeMux()
	mux.HandleFunc("POST /items", s.createItem)
	mux.HandleFunc("GET /items/{id}", s.getItem)
	return mux
}

func (s *Server) find(id int) (Item, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	it, ok := s.items[id]
	if !ok {
		return Item{}, fmt.Errorf("find %d: %w", id, ErrNotFound)
	}
	return it, nil
}

func (s *Server) getItem(w http.ResponseWriter, r *http.Request) {
	id, err := strconv.Atoi(r.PathValue("id"))
	if err != nil {
		http.Error(w, "id must be a number", http.StatusBadRequest)
		return
	}
	it, err := s.find(id)
	if err != nil {
		s.fail(w, err)
		return
	}
	writeJSON(w, http.StatusOK, it)
}

func (s *Server) createItem(w http.ResponseWriter, r *http.Request) {
	r.Body = http.MaxBytesReader(w, r.Body, 1<<20)
	dec := json.NewDecoder(r.Body)
	dec.DisallowUnknownFields()
	var in struct {
		Name       string `json:"name"`
		PricePence int    `json:"price_pence"`
	}
	if err := dec.Decode(&in); err != nil {
		http.Error(w, "invalid JSON body", http.StatusBadRequest)
		return
	}
	if in.Name == "" || in.PricePence < 0 {
		http.Error(w, "name is required and price_pence must be 0 or more", http.StatusBadRequest)
		return
	}
	s.mu.Lock()
	it := Item{ID: len(s.items) + 1, Name: in.Name, PricePence: in.PricePence}
	s.items[it.ID] = it
	s.mu.Unlock()
	writeJSON(w, http.StatusCreated, it)
}

// fail maps errors to status codes in one place. Internal detail is logged, not sent.
func (s *Server) fail(w http.ResponseWriter, err error) {
	switch {
	case errors.Is(err, ErrNotFound):
		http.Error(w, "not found", http.StatusNotFound)
	default:
		s.log.Error("request failed", "err", err)
		http.Error(w, "internal error", http.StatusInternalServerError)
	}
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}
