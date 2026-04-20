# programming-language-comparison

Experimental comparison work for Linear issue LIL-246: "understand each programming language trait".

This repository packages the concrete comparison artifacts that were previously spread across `/tmp/lil-246*`.

## What is here

- `tracks/a-jsonl-cli`: shared JSONL CLI comparison for Python, TypeScript, and Go
- `tracks/b-http-api`: minimal HTTP API comparison for Python, TypeScript, and Go
- `tracks/b1-change-impact`: change-impact version of the HTTP API (`blocked` status + filter)
- `tracks/c-etl`: CSV -> JSON ETL comparison for Python, TypeScript, and Go
- `tracks/r2-optional-due-date`: API compatibility/change-impact slice with optional `due_date` for Python, TypeScript, Go, and Rust
- `tracks/r3-worker-pool`: Go baseline plus Elixir and Rust implementations for worker pool + retry + timeout + partial failure
- `tracks/r5-binary-parser`: C++ baseline plus Rust implementation for binary parsing / buffer handling

## Current interim takeaways

- Python is the fastest starting point for one-off automation, CLI tasks, and ETL.
- TypeScript is strongest when preserving request/response contracts while evolving APIs.
- Rust now also shares the same R2 optional-field slice, so API-evolution comparisons are no longer limited to Python, TypeScript, and Go.
- Go is strong for operationally simple CLI/API delivery and explicit worker behavior.
- R3 and R5 now have concrete baseline tasks instead of only abstract planning.
- A short situation-based interim guide now lives in `docs/current-decision-guide.md`.
- A track-by-track adoption / fallback / rejection matrix now lives in `docs/track-adoption-rejection-matrix.md`.
- A same-track worker comparison summary now lives in `docs/r3-worker-tradeoff-summary.md`.
- A same-track low-level parser comparison summary now lives in `docs/r5-binary-parser-tradeoff-summary.md`.
- Current "verified now vs still blocked" repo status lives in `docs/current-baseline-status.md`.
- Toolchain readiness and the exact next comparison slice per blocked language live in `docs/toolchain-readiness-and-next-steps.md`.

## Gaps still open

- Zig has not been run yet in the same tracks in this environment.
- Rust has now been added to `tracks/r2-optional-due-date`, `tracks/r3-worker-pool`, and `tracks/r5-binary-parser`, but broader multi-slice API-evolution evidence is still missing.
- Elixir now shares the same worker-pool track with both Go and Rust, but broader multi-track evidence is still missing.
- The final decision guide still needs the remaining languages and track-by-track adoption / rejection conditions.

## Reproducing

Quick current-baseline verification:

```bash
./scripts/check_current_baselines.sh
```

HTTP-only verification:

```bash
python3 scripts/check_http_tracks.py
```

Toolchain/readiness notes for blocked languages:

```bash
sed -n '1,220p' docs/toolchain-readiness-and-next-steps.md
```

Executable readiness check:

```bash
./scripts/check_toolchain_readiness.sh
```

Examples:

```bash
python3 tracks/a-jsonl-cli/tasks_cli.py tracks/a-jsonl-cli/tasks.jsonl
node tracks/a-jsonl-cli/dist/tasks_cli.js tracks/a-jsonl-cli/tasks.jsonl
go run tracks/a-jsonl-cli/tasks_cli.go tracks/a-jsonl-cli/tasks.jsonl

python3 tracks/c-etl/tasks_etl.py tracks/c-etl/tasks.csv /tmp/out.json
go run tracks/c-etl/tasks_etl.go tracks/c-etl/tasks.csv /tmp/out.json

go run tracks/r3-worker-pool/main.go tracks/r3-worker-pool/jobs.json 4 250
elixir tracks/r3-worker-pool/main.exs tracks/r3-worker-pool/jobs.json 4 250
cargo run --quiet --manifest-path tracks/r3-worker-pool/Cargo.toml -- tracks/r3-worker-pool/jobs.json 4 250
clang++ -std=c++20 -O2 -Wall -Wextra -pedantic tracks/r5-binary-parser/main.cpp -o /tmp/r5_cpp
/tmp/r5_cpp tracks/r5-binary-parser/frames.bin

. "$HOME/.cargo/env"
cargo run --quiet --manifest-path tracks/r5-binary-parser/Cargo.toml -- tracks/r5-binary-parser/frames.bin
```

For the TypeScript tracks, the repo now installs dependencies locally with `npm ci` and compiles with repo-local `tsc` during verification.
