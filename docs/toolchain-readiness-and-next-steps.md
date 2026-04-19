# Toolchain readiness and next-step plan

This note exists to make the next comparison slice executable without re-discovering environment blockers.

## Snapshot from the 2026-04-17 JST 22:00 range check

Currently available in this environment:

- Go: available
- Python: available
- Node/TypeScript: available through repo-local `npm ci` + `tsc`
- C++: available through `clang++` and `g++`

Currently blocked:

- Zig: not found on PATH
- MoonBit: not found on PATH

Recently unblocked and already used:

- Rust: available via `mise use -g rust@stable`, and now exercised on `tracks/r5-binary-parser` and `tracks/r3-worker-pool`
- Elixir: available via `mise use -g erlang@28.4.2 elixir@1.19.5-otp-28`, and now exercised on `tracks/r3-worker-pool`

## What can move right now without new toolchains

### Safe to continue immediately

- R1 / R2 / R4 hardening on Python / TypeScript / Go
- R3 comparison interpretation and hardening in Go, Elixir, and Rust
- R5 baseline iteration in Rust and C++
- repo-level verification and decision-guide hardening

### Highest-value blocked additions

1. Zig on `tracks/r5-binary-parser`
   - Why next: R5 already has stable input/output expectations across C++ and Rust, and Zig is the remaining intended low-level comparison target.
2. Rust or another later language on an R2 API-evolution slice
   - Why next after that: Rust has moved past unblock work and now needs a second track if we want broader evidence than low-level parsing plus worker behavior.

## Exact next slice after each unblock

### Rust is now available

Completed first target:

- `tracks/r5-binary-parser`

What is now true:

- Rust produces the same summary fields as the C++ baseline on the same `frames.bin`
- the repo can verify the Rust and C++ outputs together in `./scripts/check_current_baselines.sh`
- the next meaningful Rust slices are no longer unblock work, but propagation into another track such as `tracks/r3-worker-pool` or a later R2 slice

### Elixir is now available

Completed first target:

- `tracks/r3-worker-pool`

What is now true:

- Elixir produces the same summary fields as the Go baseline on the same `jobs.json`
- the repo can verify Go, Elixir, and Rust together on the worker-pool track
- the next value from Elixir is no longer unblock work, but interpretation of the concurrency/failure tradeoffs or propagation into a new track if needed

### If Zig becomes available

First target:

- `tracks/r5-binary-parser`

Expected output contract:

- same `frames.bin`
- same summary fields as the C++ baseline
- implementation notes focused on buffer handling, allocator/control surface, and parser readability

## Executable readiness check

Run this to get the current runnable/blocked snapshot as JSON:

```bash
./scripts/check_toolchain_readiness.sh
```

It reports:

- what is available now
- what is blocked now
- the first track to use once Zig becomes runnable, plus the already-completed first targets for Rust and Elixir

## Why this doc matters

The repo already has good comparison artifacts, but the next step can still stall if the environment question is rediscovered from scratch every run.

This document turns the remaining work into:

- what is runnable now
- what is blocked now
- what the first meaningful task is once each blocker is removed or completed

That should keep future runs moving on implementation instead of re-triage.
