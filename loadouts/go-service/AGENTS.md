# AGENTS.md: Go service

Go module. Check the `go` directive in `go.mod` before using newer language or standard library features.

## Commands
- Build: `go build ./...`. Tests: `go test -race ./...`. Vet: `go vet ./...`.
- Format: `gofmt -l .` must print nothing (or `goimports` if the project uses it).
- Lint, if `.golangci.yml` exists: `golangci-lint run`.
- Done means: gofmt clean, vet clean, tests green with `-race`.

## Errors
- Return errors; never `panic` on input. Wrap with context: `fmt.Errorf("load user %d: %w", id, err)`.
- Compare with `errors.Is` and `errors.As`, never by string. Define sentinel errors (`var ErrNotFound = errors.New(...)`)
  for conditions callers handle.
- Handle every error once: either return it or log it, not both.

## Concurrency
- `context.Context` is the first parameter of anything that does I/O or may block. Respect cancellation.
- Every goroutine has an owner and a way to stop (context, closed channel or `errgroup`). No fire-and-forget goroutines.
- Shared state behind a mutex or owned by one goroutine. `go test -race` must stay clean.

## HTTP
- Go 1.22+ routing: `mux.HandleFunc("GET /items/{id}", h)` and `r.PathValue("id")`. Do not add a router library for that.
- Servers set timeouts (`ReadHeaderTimeout` at least). Clients use a `http.Client` with `Timeout`, never the default client
  for external calls.
- Write JSON with the right `Content-Type` and status; decode with a size limit (`http.MaxBytesReader`).

## Dependencies and style
- Standard library first. Ask before adding a module; then `go get <module>@<version>` and `go mod tidy`.
- Logging with `log/slog`, structured key-value pairs. No secrets in logs.
- Table-driven tests with `t.Run`; `net/http/httptest` for handlers. New handlers: use the `go-http-handler` skill.
- Small interfaces, defined where they are used. Accept interfaces, return structs.
