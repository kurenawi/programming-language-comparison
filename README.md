# programming-language-comparison

Experimental comparison work for Linear issue LIL-246: "understand each programming language trait".

This repository packages the concrete comparison artifacts that were previously spread across `/tmp/lil-246*`.

## What is here

- `tracks/a-jsonl-cli`: shared JSONL CLI comparison for Python, TypeScript, and Go
- `tracks/b-http-api`: minimal HTTP API comparison for Python, TypeScript, and Go
- `tracks/b1-change-impact`: change-impact version of the HTTP API (`blocked` status + filter)
- `tracks/c-etl`: CSV -> JSON ETL comparison for Python, TypeScript, and Go
- `tracks/r2-optional-due-date`: API compatibility/change-impact slice with optional `due_date`
- `tracks/r3-worker-pool`: Go baseline for worker pool + retry + timeout + partial failure
- `tracks/r5-binary-parser`: C++ baseline for binary parsing / buffer handling

## Current interim takeaways

- Python is the fastest starting point for one-off automation, CLI tasks, and ETL.
- TypeScript is strongest when preserving request/response contracts while evolving APIs.
- Go is strong for operationally simple CLI/API delivery and explicit worker behavior.
- R3 and R5 now have concrete baseline tasks instead of only abstract planning.
- A short situation-based interim guide now lives in `docs/current-decision-guide.md`.
- Current "verified now vs still blocked" repo status lives in `docs/current-baseline-status.md`.

## Gaps still open

- Rust / Elixir / Zig have not been run yet in the same tracks in this environment.
- The final decision guide still needs the remaining languages and track-by-track adoption / rejection conditions.
- TypeScript verification for the CLI / ETL tracks is not folded into the unified baseline script yet.

## Reproducing

Quick current-baseline verification:

```bash
./scripts/check_current_baselines.sh
```

HTTP-only verification:

```bash
python3 scripts/check_http_tracks.py
```

Examples:

```bash
python3 tracks/a-jsonl-cli/tasks_cli.py tracks/a-jsonl-cli/tasks.jsonl
node tracks/a-jsonl-cli/dist/tasks_cli.js tracks/a-jsonl-cli/tasks.jsonl
go run tracks/a-jsonl-cli/tasks_cli.go tracks/a-jsonl-cli/tasks.jsonl

python3 tracks/c-etl/tasks_etl.py tracks/c-etl/tasks.csv /tmp/out.json
go run tracks/c-etl/tasks_etl.go tracks/c-etl/tasks.csv /tmp/out.json

go run tracks/r3-worker-pool/main.go tracks/r3-worker-pool/jobs.json 4 250
clang++ -std=c++20 -O2 -Wall -Wextra -pedantic tracks/r5-binary-parser/main.cpp -o /tmp/r5_cpp
/tmp/r5_cpp tracks/r5-binary-parser/frames.bin
```

For the HTTP tracks, the repo can now install TypeScript dependencies locally with `npm ci` inside each track directory during verification.
