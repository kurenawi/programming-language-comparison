# Current decision guide for LIL-246

This is the current interim guide from the implemented tracks only. It is intentionally narrower than the final goal.

## Decision by situation

| Situation | First choice now | Why | Strong fallback | Avoid first when |
| -- | -- | -- | -- | -- |
| Fast one-person automation, ETL, throwaway CLI work | Python | Fastest to start, shortest path through CSV/JSON/HTTP basics | Go | You need strict contract evolution across a team |
| Team-owned API that will keep evolving | TypeScript | Best visibility into contract changes and optional field expansion | Go | You want zero Node/build dependency or single-binary delivery |
| Operational CLI or API you want to ship simply | Go | Standard library coverage plus clean deployment story | Python | You mostly care about the fastest iteration loop |
| Worker pool baseline with retry, timeout, partial failure | Go, for the current environment | Concrete baseline already implemented and runnable here | TypeScript, later Rust/Elixir for better comparison | You need language-level process isolation comparisons, which are not tested yet |
| Low-level binary parsing baseline | C++, for the current environment | Toolchain exists now and the binary parsing baseline already runs | Rust/Zig later when toolchains exist | You want memory safety guarantees first |

## What this guide does not claim yet

- It is not the final answer for Elixir, Rust, Zig, MoonBit, C, or C++ as full comparison targets.
- R3 still needs Rust/Elixir on the same worker-pool task.
- R5 still needs Rust/Zig on the same binary parsing task.
- The final guide still needs track-by-track rejection conditions for the added languages.

## Implemented evidence behind this interim guide

- `tracks/a-jsonl-cli`
- `tracks/b-http-api`
- `tracks/b1-change-impact`
- `tracks/c-etl`
- `tracks/r2-optional-due-date`
- `tracks/r3-worker-pool`
- `tracks/r5-binary-parser`

## Next comparison priorities

1. Add Rust to R5-1 when toolchain is available.
2. Add Elixir to R3-1 when runtime is available.
3. Add Rust to R3-1 or R2 once toolchain setup is solved.
4. Convert this interim guide into the final track-by-track adoption/rejection matrix.
