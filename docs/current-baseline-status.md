# Current baseline status for LIL-246

This file answers a practical question: what can be re-run and trusted **right now** in this environment, and what still depends on extra toolchain setup?

## Verified in this environment

These are checked by `scripts/check_current_baselines.sh`.

| Track | Languages checked now | What is verified |
| -- | -- | -- |
| `a-jsonl-cli` | Python | Shared CLI summary output matches the current expected totals |
| `b-http-api` | Python, TypeScript, Go | Shared API summary, successful POST, and validation-error behavior all match the expected results |
| `b1-change-impact` | Python, TypeScript, Go | `blocked` status support and `GET /tasks?status=blocked` behavior match the shared expected result |
| `c-etl` | Python, Go | CSV -> JSON ETL summary matches the shared expected result |
| `r2-optional-due-date` | Python, TypeScript, Go | Optional `due_date`, backward-compatible `GET /tasks`, validation error, and `overdue_tasks` summary behavior all match |
| `r3-worker-pool` | Go | Worker pool baseline matches the expected retry / timeout / partial-failure summary |
| `r5-binary-parser` | C++ | Binary parser baseline matches the expected record summary |

## Present but not auto-checked yet

| Track | Why it is not in the current baseline check |
| -- | -- |
| TypeScript variants for `a-jsonl-cli` and `c-etl` | Repo-local TypeScript verification is now in place for the HTTP tracks first, but CLI / ETL TypeScript variants still need to be folded into the unified baseline check |
| Rust / Elixir / Zig comparison tracks | The comparison plan exists, but those language runs are still blocked by missing toolchains or runtime setup in this environment |

## Why this matters

Before this file and the check script existed, the repository had useful artifacts but not a fast way to confirm which slices still run as expected after edits.
Now the current repo-hardening priority is much narrower: extend the same reproducible verification pattern to the remaining TypeScript-backed non-HTTP tracks, then add new languages when toolchains are ready.

## Best next upgrades

1. Fold TypeScript verification for `a-jsonl-cli` and `c-etl` into the current baseline check.
2. Add Rust once toolchain setup is available, starting from `r5-binary-parser` or another already-fixed baseline track.
3. Add Elixir to `r3-worker-pool` once the runtime is configured so partial-failure behavior can be compared on the same task.
