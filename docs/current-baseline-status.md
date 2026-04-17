# Current baseline status for LIL-246

This file answers a practical question: what can be re-run and trusted **right now** in this environment, and what still depends on extra toolchain setup?

## Verified in this environment

These are checked by `scripts/check_current_baselines.sh`.

| Track | Languages checked now | What is verified |
| -- | -- | -- |
| `a-jsonl-cli` | Python | Shared CLI summary output matches the current expected totals |
| `c-etl` | Python, Go | CSV -> JSON ETL summary matches the shared expected result |
| `r3-worker-pool` | Go | Worker pool baseline matches the expected retry / timeout / partial-failure summary |
| `r5-binary-parser` | C++ | Binary parser baseline matches the expected record summary |

## Present but not auto-checked yet

| Track | Why it is not in the current baseline check |
| -- | -- |
| `b-http-api` | Needs a small harness to boot each server, hit endpoints, and shut it down cleanly |
| `b1-change-impact` | Same as `b-http-api`, plus endpoint-level assertions |
| `r2-optional-due-date` | Same as `b-http-api`, plus backward-compatibility and validation assertions |
| TypeScript variants across tracks | This environment has Node/npm but not a stable always-on global `tsc`; past runs used temporary setup |

## Why this matters

Before this file and the check script existed, the repository had useful artifacts but not a fast way to confirm which slices still run as expected after edits.
Now there is at least one repeatable verification path for the current runnable baselines.

## Best next upgrades

1. Add a tiny HTTP test harness so `b-http-api`, `b1-change-impact`, and `r2-optional-due-date` can join the baseline check.
2. Make the TypeScript toolchain reproducible inside the repo instead of relying on ad hoc temporary setup.
3. When Rust / Elixir / Zig are added, extend this file with the same "verified now" vs "present but blocked" split.
