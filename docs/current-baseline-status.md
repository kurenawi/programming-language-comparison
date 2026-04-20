# Current baseline status

## Verified now

- `a-jsonl-cli`
  - Python
  - TypeScript (repo-local `npm ci` + `tsc` during baseline check)
- `b-http-api`
  - Python
  - TypeScript
  - Go
- `b1-change-impact`
  - Python
  - TypeScript
  - Go
- `c-etl`
  - Python
  - TypeScript (repo-local `npm ci` + `tsc` during baseline check)
  - Go
- `r2-optional-due-date`
  - Python
  - TypeScript
  - Go
  - Rust
- `r3-worker-pool`
  - Go
  - Elixir
  - Rust
- `r5-binary-parser`
  - C++
  - Rust

## Present but not auto-checked yet

- Zig tracks, blocked by missing toolchain in the current environment
- MoonBit tracks, blocked by missing toolchain in the current environment

## Current meaning

The repo can now re-verify the currently implemented Python, TypeScript, Go, and C++ baselines with one command:

```bash
./scripts/check_current_baselines.sh
```

That command now covers:

- CLI
- HTTP API
- HTTP change-impact
- HTTP optional-field compatibility
- ETL
- worker-pool baseline (Go + Elixir + Rust)
- binary-parser baseline (C++ + Rust)
