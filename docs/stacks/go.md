---
id: go-stack
title: Go Stack
description: >
  Go stack tooling: gofumpt for formatting, golangci-lint for linting,
  go vet for static analysis, go test for testing, and a distroless Dockerfile.
index:
  - id: tools
    keywords: [gofumpt, golangci-lint, go-vet, go-test, tools]
  - id: formatter-gofumpt
    keywords: [gofumpt, format, strict, gofmt]
  - id: linter-golangci-lint
    keywords: [golangci-lint, errcheck, staticcheck, linters, rules]
  - id: test-runner-go-test
    keywords: [go-test, cgo-disabled, parallel, t-parallel]
  - id: docker
    keywords: [dockerfile, distroless, multi-stage, builder, runtime]
---

# Go Stack

## Tools

| Purpose | Tool | Config |
|---------|------|--------|
| Formatter | [gofumpt](https://github.com/mvdan/gofumpt) | (no config file, stricter than gofmt) |
| Linter | [golangci-lint](https://golangci-lint.run/) | `.golangci.yml` |
| Type checker | go vet | (built into toolchain) |
| Test runner | go test | (built into toolchain) |
| Build | go build | (built into toolchain) |

All tools except the Go toolchain itself are managed by mise.

## mise.toml (generated)

```toml
[tools]
go = "1.23.12"
gofumpt = "latest"
golangci-lint = "latest"
```

## Project layout

```
my-service/
├── go.mod
├── go.sum
├── .golangci.yml
├── Dockerfile
├── cmd/
│   └── main.go
└── internal/
    └── app/
        ├── app.go
        └── app_test.go
```

## Formatter — gofumpt

gofumpt is a stricter superset of gofmt. It enforces additional formatting rules on top of the Go standard.

```bash
mise run fmt           # format in-place (gofumpt -w .)
mise run fmt --check   # check only (gofumpt -l .)
```

golangci-lint is configured to enforce gofumpt-compatible formatting via the `gofumpt` linter.

## Linter — golangci-lint

Runs 17+ linters in a single pass. Configuration in `.golangci.yml` (v2 format).

```bash
mise run lint
```

Key linters enabled:

| Linter | Catches |
|--------|---------|
| `errcheck` | Unchecked error returns |
| `gosimple` | Simplifiable code |
| `govet` | Suspicious constructs |
| `ineffassign` | Ineffectual assignments |
| `staticcheck` | Bugs, performance, style |
| `gofumpt` | Formatting violations |
| `goimports` | Import ordering |
| `misspell` | Spelling errors |
| `unconvert` | Unnecessary type conversions |

## Type checker — go vet

Go's type system is enforced at compile time. `go vet` provides the closest equivalent to a standalone static analysis pass.

```bash
mise run typecheck   # go vet ./...
```

## Test runner — go test

```bash
mise run test   # CGO_ENABLED=0 go test ./...
```

CGO is disabled for reproducibility. Generated tests use `t.Parallel()` for intra-package parallelism:

```go
func TestGreet(t *testing.T) {
    t.Parallel()
    // ...
}
```

## Docker

Generated Go projects include a multi-stage Dockerfile:

1. **Builder** — `golang:1.23-alpine`, compiles the binary
2. **Runtime** — `gcr.io/distroless/static-debian12`, ships only the binary

```bash
docker build -t my-service:latest .
```

The Docker build is validated during `mise run verify`.

## CGO

All build and test tasks set `CGO_ENABLED=0` to produce statically-linked binaries compatible with distroless images.
