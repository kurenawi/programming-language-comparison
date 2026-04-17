# Toolchain readiness and next-step plan

This note exists to make the next comparison slice executable without re-discovering environment blockers.

## Snapshot from the 2026-04-17 JST 22:00 range check

Currently available in this environment:

- Go: available
- Python: available
- Node/TypeScript: available through repo-local `npm ci` + `tsc`
- C++: available through `clang++` and `g++`

Currently blocked:

- Rust: `rustc` / `cargo` not found on PATH
- Elixir: shim exists, but no active version is configured via mise
- Zig: not found on PATH
- MoonBit: not found on PATH

### Concrete observed blocker for Elixir

`elixir --version` currently returns:

```text
mise ERROR No version is set for shim: elixir
Set a global default version with one of the following:
mise use -g elixir@1.19.5-otp-28
```

This means the blocker is not conceptual. It is specifically runtime/version setup.

## What can move right now without new toolchains

### Safe to continue immediately

- R1 / R2 / R4 hardening on Python / TypeScript / Go
- R3 baseline iteration in Go
- R5 baseline iteration in C++
- repo-level verification and decision-guide hardening

### Highest-value blocked additions

1. Rust on `tracks/r5-binary-parser`
   - Why first: R5 is already fixed to a concrete binary parsing task, so Rust can be compared against an existing C++ baseline with minimal ambiguity.
2. Elixir on `tracks/r3-worker-pool`
   - Why second: R3 already has stable input/output expectations, and Elixir is one of the main planned comparison targets for concurrency / failure isolation.
3. Zig on `tracks/r5-binary-parser`
   - Why third: same fixed input/output shape as Rust, but lower immediate value than Rust for the current decision backlog.

## Exact next slice after each unblock

### If Rust becomes available

First target:

- `tracks/r5-binary-parser`

Expected output contract:

- same `frames.bin`
- same summary fields as the C++ baseline
- implementation notes focused on parsing clarity, memory-safety ergonomics, and extension cost

Only after that:

- consider Rust on `tracks/r3-worker-pool` or a later R2 slice

### If Elixir becomes available

First target:

- `tracks/r3-worker-pool`

Expected output contract:

- same `jobs.json`
- same summary fields as the Go baseline
- implementation notes focused on timeout handling, retry shape, and failure isolation model

### If Zig becomes available

First target:

- `tracks/r5-binary-parser`

Expected output contract:

- same `frames.bin`
- same summary fields as the C++ baseline
- implementation notes focused on buffer handling, allocator/control surface, and parser readability

## Why this doc matters

The repo already has good comparison artifacts, but the next step can still stall if the environment question is rediscovered from scratch every run.

This document turns the remaining work into:

- what is runnable now
- what is blocked now
- what the first meaningful task is once each blocker is removed

That should keep future runs moving on implementation instead of re-triage.
