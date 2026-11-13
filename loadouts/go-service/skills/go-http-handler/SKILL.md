---
name: go-http-handler
description: Add a Go net/http handler with 1.22+ routing, a size-limited JSON body, wrapped errors mapped to status codes and table-driven httptest tests. Use when adding or changing an HTTP endpoint.
---

# Go HTTP handler

1. Read how the service builds its `http.ServeMux` and stores dependencies (usually a struct with methods).
2. Follow `references/handler.go`: a method on the server struct, `r.PathValue` for path parameters,
   `http.MaxBytesReader` plus `json.Decoder` with `DisallowUnknownFields` for bodies.
3. Map errors to status codes in one place: `errors.Is(err, ErrNotFound)` gives 404, validation 400, everything else 500
   with the detail logged through `slog`, not sent to the client.
4. Register the route with method and pattern: `mux.HandleFunc("POST /items", s.createItem)`.
5. Tests like `references/handler_test.go`: table-driven, `httptest.NewRecorder`, one row per status code.
6. Run `gofmt -l .`, `go vet ./...` and `go test -race ./...`. Report the results.
