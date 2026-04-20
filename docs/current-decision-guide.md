# Current decision guide for LIL-246

This is the current interim guide from the implemented tracks only. It is intentionally narrower than the final goal.

## Decision by situation

| Situation | First choice now | Why | Strong fallback | Avoid first when |
| -- | -- | -- | -- | -- |
| Fast one-person automation, ETL, throwaway CLI work | Python | Fastest to start, shortest path through CSV/JSON/HTTP basics | Go | You need strict contract evolution across a team |
| Team-owned API that will keep evolving | TypeScript | Best visibility into contract changes and optional field expansion | Go for explicit operational compatibility work, Rust for stronger safety/control comparison on the same optional-field slice | You want zero Node/build dependency or single-binary delivery |
| Operational CLI or API you want to ship simply | Go | Standard library coverage plus clean deployment story | Python | You mostly care about the fastest iteration loop |
| Worker pool baseline with retry, timeout, partial failure | Go | Clearest operational baseline on the same verified worker slice | Elixir for isolation/concurrency-model comparison, Rust for safety/control comparison | The main decision is supervisor-style isolation or stronger compile-time safety rather than the simplest operational baseline |
| Low-level binary parsing baseline | Rust | Same verified parser slice as C++, but with the stronger safety posture for new low-level work | C++ when existing native-code context or interop dominates | You must stay inside an existing C++ codebase right now or Rust adoption cost is higher than the parser risk |

## What this guide does not claim yet

- It is not the final answer for Elixir, Rust, Zig, MoonBit, C, or C++ as full comparison targets.
- Rust is now present on an R2 API-evolution slice, but that still does not make R2 fully settled.
- R3 still needs broader stress and scale slices beyond the current shared worker contract.
- R5 still needs Zig on the same binary parsing task and possibly more than one parser shape.
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

1. Add Zig to R5 on the same binary-parser slice.
2. Broaden R3 beyond contract-equivalent correctness into heavier stress slices.
3. Add Rust to an R2 API-evolution slice.
4. Convert the remaining interim rows into the final track-by-track adoption/rejection matrix.
