# AGENTS.md

`shipctl`: a Go 1.27 command-line tool for managing deploy manifests. Single binary, no CGO.

## Commands
- Build: `go build ./...` · run: `go run ./cmd/shipctl --help`
- Tests: `go test ./...` · race: `go test -race ./...` · one: `go test ./internal/manifest -run TestMerge`
- Lint: `golangci-lint run`
- Golden files: `go test ./internal/render -update` rewrites `testdata/*.golden`; only after reading the diff

## Layout
- `cmd/shipctl/` flags and wiring only; `internal/` everything else; no pkg folder
- `testdata/` inputs and golden outputs for table-driven tests

## Conventions
- Errors wrap with context: `fmt.Errorf("load %s: %w", path, err)`; no panics outside `main`
- Flags are kebab-case and documented in `--help`; any new flag is added to `docs/cli.md`
- Output: human text by default, `--json` for machines; never change existing JSON field names
- Standard library first; ask before adding a module

## Never
- Accept updated golden files without reading the diff
- Change exit codes (0 ok, 1 error, 2 usage); scripts depend on them

## Done means
`go test -race ./...` and `golangci-lint run` pass, and you ran the changed command for real and pasted its output.
