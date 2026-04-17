#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

command_status() {
  local cmd="$1"
  if command -v "$cmd" >/dev/null 2>&1; then
    printf 'present'
  else
    printf 'missing'
  fi
}

safe_version() {
  local cmd="$1"
  shift || true
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf ''
    return 0
  fi
  local out
  if out="$($cmd "$@" 2>&1 | head -n 2 | tr '\n' '|' | sed 's/|$//')"; then
    printf '%s' "$out"
  else
    printf '%s' "$out"
  fi
}

python_status="$(command_status python3)"
go_status="$(command_status go)"
node_status="$(command_status node)"
clang_status="$(command_status clang++)"
gxx_status="$(command_status g++)"
rustc_status="$(command_status rustc)"
cargo_status="$(command_status cargo)"
zig_status="$(command_status zig)"
moon_status="$(command_status moon)"
elixir_status="$(command_status elixir)"

if [[ -x tracks/a-jsonl-cli/node_modules/.bin/tsc ]] || [[ -x tracks/b-http-api/node_modules/.bin/tsc ]]; then
  ts_repo_local="available"
else
  ts_repo_local="needs npm ci"
fi

elixir_version="$(safe_version elixir --version)"
rustc_version="$(safe_version rustc --version)"
go_version="$(safe_version go version)"
python_version="$(safe_version python3 --version)"
node_version="$(safe_version node --version)"
zig_version="$(safe_version zig version)"
moon_version="$(safe_version moon version)"

python3 - <<'PY' \
  "$python_status" "$python_version" \
  "$go_status" "$go_version" \
  "$node_status" "$node_version" "$ts_repo_local" \
  "$clang_status" "$gxx_status" \
  "$rustc_status" "$cargo_status" "$rustc_version" \
  "$elixir_status" "$elixir_version" \
  "$zig_status" "$zig_version" \
  "$moon_status" "$moon_version"
import json, sys
(
    python_status, python_version,
    go_status, go_version,
    node_status, node_version, ts_repo_local,
    clang_status, gxx_status,
    rustc_status, cargo_status, rustc_version,
    elixir_status, elixir_version,
    zig_status, zig_version,
    moon_status, moon_version,
) = sys.argv[1:]

available_now = []
blocked_now = []
next_slices = {}
notes = {}

if python_status == 'present':
    available_now.append({"language": "Python", "status": "available", "version": python_version})
if go_status == 'present':
    available_now.append({"language": "Go", "status": "available", "version": go_version})
if node_status == 'present':
    available_now.append({"language": "Node/TypeScript", "status": f"repo-local {ts_repo_local}", "version": node_version})
if clang_status == 'present' or gxx_status == 'present':
    available_now.append({"language": "C++", "status": "available", "version": "clang++ present" if clang_status == 'present' else 'g++ present'})

if rustc_status == 'present' and cargo_status == 'present':
    available_now.append({"language": "Rust", "status": "available", "version": rustc_version})
    next_slices["Rust"] = {"track": "tracks/r5-binary-parser", "reason": "fixed binary parsing baseline already exists"}
else:
    blocked_now.append({"language": "Rust", "status": "blocked", "blocker": "rustc/cargo not both available on PATH", "observed": rustc_version or "rustc/cargo missing"})
    next_slices["Rust"] = {"track": "tracks/r5-binary-parser", "reason": "first meaningful slice once unblocked"}

if elixir_status == 'present' and 'No version is set for shim' not in elixir_version and elixir_version:
    available_now.append({"language": "Elixir", "status": "available", "version": elixir_version})
    next_slices["Elixir"] = {"track": "tracks/r3-worker-pool", "reason": "same jobs.json and summary contract as Go baseline"}
else:
    blocked_now.append({"language": "Elixir", "status": "blocked", "blocker": "runtime/version not configured", "observed": elixir_version or "elixir missing"})
    next_slices["Elixir"] = {"track": "tracks/r3-worker-pool", "reason": "first meaningful slice once unblocked"}

if zig_status == 'present':
    available_now.append({"language": "Zig", "status": "available", "version": zig_version})
    next_slices["Zig"] = {"track": "tracks/r5-binary-parser", "reason": "same fixed low-level baseline as Rust/C++"}
else:
    blocked_now.append({"language": "Zig", "status": "blocked", "blocker": "zig not found on PATH", "observed": zig_version or "zig missing"})
    next_slices["Zig"] = {"track": "tracks/r5-binary-parser", "reason": "first meaningful slice once unblocked"}

if moon_status == 'present':
    available_now.append({"language": "MoonBit", "status": "available", "version": moon_version})
else:
    blocked_now.append({"language": "MoonBit", "status": "blocked", "blocker": "moon not found on PATH", "observed": moon_version or "moon missing"})

notes["run_now_without_new_toolchains"] = [
    "R1/R2/R4 hardening on Python, TypeScript, and Go",
    "R3 baseline iteration in Go",
    "R5 baseline iteration in C++",
    "repo-level verification and decision-guide hardening",
]

print(json.dumps({
    "available_now": available_now,
    "blocked_now": blocked_now,
    "next_slices": next_slices,
    "notes": notes,
}, ensure_ascii=False, indent=2))
PY
