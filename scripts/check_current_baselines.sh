#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

cd "$ROOT"

echo "== programming-language-comparison baseline check =="
echo "repo: $ROOT"

echo
printf '[1/4] A JSONL CLI (Python) ... '
A_PY_OUT="$(python3 tracks/a-jsonl-cli/tasks_cli.py tracks/a-jsonl-cli/tasks.jsonl)"
EXPECTED_A=$'total_tasks=6\nstatus_todo=2\nstatus_in_progress=2\nstatus_done=2\npoints_high=8\npoints_medium=4\npoints_low=9'
if [[ "$A_PY_OUT" != "$EXPECTED_A" ]]; then
  echo "FAIL"
  echo "$A_PY_OUT"
  exit 1
fi
echo "ok"

echo
printf '[2/4] C ETL (Python + Go) ... '
python3 tracks/c-etl/tasks_etl.py tracks/c-etl/tasks.csv "$TMP_DIR/py.json" >/dev/null
GO_ETL_OUT="$TMP_DIR/go.json"
go run tracks/c-etl/tasks_etl.go tracks/c-etl/tasks.csv "$GO_ETL_OUT" >/dev/null
python3 - <<'PY' "$TMP_DIR/py.json" "$GO_ETL_OUT"
import json, sys
py_path, go_path = sys.argv[1], sys.argv[2]
expected = {
    "total_tasks": 5,
    "status_counts": {"todo": 2, "in_progress": 2, "done": 1},
    "points_by_priority": {"high": 11, "medium": 6, "low": 2},
}
with open(py_path) as f:
    py = json.load(f)
with open(go_path) as f:
    go = json.load(f)
assert py["summary"] == expected, py["summary"]
assert go["summary"] == expected, go["summary"]
PY
echo "ok"

echo
printf '[3/4] R3 worker pool (Go) ... '
R3_OUT="$TMP_DIR/r3.json"
go run tracks/r3-worker-pool/main.go tracks/r3-worker-pool/jobs.json 4 250 > "$R3_OUT"
python3 - <<'PY' "$R3_OUT"
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
PY
echo "ok"

echo
printf '[4/4] R5 binary parser (C++) ... '
R5_BIN="$TMP_DIR/r5_cpp"
clang++ -std=c++20 -O2 -Wall -Wextra -pedantic tracks/r5-binary-parser/main.cpp -o "$R5_BIN"
R5_OUT="$TMP_DIR/r5.json"
"$R5_BIN" tracks/r5-binary-parser/frames.bin > "$R5_OUT"
python3 - <<'PY' "$R5_OUT"
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
PY
echo "ok"

echo
echo "All checked baselines passed."
echo "Unchecked tracks: TypeScript-based tracks still require local npm/tsc setup in this environment."
