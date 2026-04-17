#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

compile_ts() {
  local track_dir="$1"
  if [[ ! -x "$track_dir/node_modules/.bin/tsc" ]]; then
    (cd "$track_dir" && npm ci >/dev/null)
  fi
  rm -rf "$track_dir/dist"
  (
    cd "$track_dir"
    ./node_modules/.bin/tsc "$2"       --outDir dist       --module nodenext       --target es2020       --moduleResolution nodenext       --types node       --esModuleInterop       --skipLibCheck >/dev/null
  )
}

cd "$ROOT"

echo "== programming-language-comparison baseline check =="
echo "repo: $ROOT"

echo
printf '[1/5] A JSONL CLI (Python + TypeScript) ... '
EXPECTED_A=$'total_tasks=6
status_todo=2
status_in_progress=2
status_done=2
points_high=8
points_medium=4
points_low=9'
A_PY_OUT="$(python3 tracks/a-jsonl-cli/tasks_cli.py tracks/a-jsonl-cli/tasks.jsonl)"
if [[ "$A_PY_OUT" != "$EXPECTED_A" ]]; then
  echo "FAIL"
  echo "$A_PY_OUT"
  exit 1
fi
compile_ts "$ROOT/tracks/a-jsonl-cli" tasks_cli.ts
A_TS_OUT="$(node tracks/a-jsonl-cli/dist/tasks_cli.js tracks/a-jsonl-cli/tasks.jsonl)"
if [[ "$A_TS_OUT" != "$EXPECTED_A" ]]; then
  echo "FAIL"
  echo "$A_TS_OUT"
  exit 1
fi
echo "ok"

echo
printf '[2/5] HTTP tracks (Python + TypeScript + Go) ... '
python3 scripts/check_http_tracks.py > "$TMP_DIR/http.log"
echo "ok"

echo
printf '[3/5] C ETL (Python + TypeScript + Go) ... '
python3 tracks/c-etl/tasks_etl.py tracks/c-etl/tasks.csv "$TMP_DIR/py.json" >/dev/null
compile_ts "$ROOT/tracks/c-etl" tasks_etl.ts
node tracks/c-etl/dist/tasks_etl.js tracks/c-etl/tasks.csv "$TMP_DIR/ts.json" >/dev/null
GO_ETL_OUT="$TMP_DIR/go.json"
go run tracks/c-etl/tasks_etl.go tracks/c-etl/tasks.csv "$GO_ETL_OUT" >/dev/null
python3 - <<'INNERPY' "$TMP_DIR/py.json" "$TMP_DIR/ts.json" "$GO_ETL_OUT"
import json, sys
py_path, ts_path, go_path = sys.argv[1], sys.argv[2], sys.argv[3]
expected = {
    "total_tasks": 5,
    "status_counts": {"todo": 2, "in_progress": 2, "done": 1},
    "points_by_priority": {"high": 11, "medium": 6, "low": 2},
}
for path in (py_path, ts_path, go_path):
    with open(path) as f:
        data = json.load(f)
    assert data["summary"] == expected, (path, data["summary"])
INNERPY
echo "ok"

echo
printf '[4/5] R3 worker pool (Go) ... '
R3_OUT="$TMP_DIR/r3.json"
go run tracks/r3-worker-pool/main.go tracks/r3-worker-pool/jobs.json 4 250 > "$R3_OUT"
python3 - <<'INNERPY' "$R3_OUT"
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
expected = {
    "total_jobs": 7,
    "succeeded": 5,
    "failed": 2,
    "timed_out": 1,
    "retried_jobs": 4,
    "total_attempts": 12,
    "worker_count": 4,
    "timeout_ms": 250,
}
for k, v in expected.items():
    assert data.get(k) == v, (k, data.get(k), v)
INNERPY
echo "ok"

echo
printf '[5/5] R5 binary parser (C++) ... '
R5_BIN="$TMP_DIR/r5_cpp"
clang++ -std=c++20 -O2 -Wall -Wextra -pedantic tracks/r5-binary-parser/main.cpp -o "$R5_BIN"
R5_OUT="$TMP_DIR/r5.json"
"$R5_BIN" tracks/r5-binary-parser/frames.bin > "$R5_OUT"
python3 - <<'INNERPY' "$R5_OUT"
import json, sys
with open(sys.argv[1]) as f:
    data = json.load(f)
assert data == {
    "total_records": 5,
    "total_value": 527,
    "flagged_records": 2,
    "type_counts": {"type_1": 2, "type_2": 2, "type_3": 1},
    "type_value_sums": {"type_1": 420, "type_2": 100, "type_3": 7},
}, data
INNERPY
echo "ok"

echo
echo "All checked baselines passed."
echo "TypeScript HTTP, CLI, and ETL tracks are now compiled from repo-local dependencies during verification."
