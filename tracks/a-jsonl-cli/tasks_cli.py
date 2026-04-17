#!/usr/bin/env python3
import json
import sys
from collections import Counter, defaultdict

if len(sys.argv) != 2:
    print("usage: tasks_cli.py <tasks.jsonl>", file=sys.stderr)
    sys.exit(1)

status_counts = Counter()
priority_points = defaultdict(int)
total = 0

with open(sys.argv[1], "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        task = json.loads(line)
        total += 1
        status_counts[task["status"]] += 1
        priority_points[task["priority"]] += int(task.get("estimate", 0))

print(f"total_tasks={total}")
for status in ["todo", "in_progress", "done"]:
    print(f"status_{status}={status_counts.get(status, 0)}")
for priority in ["high", "medium", "low"]:
    print(f"points_{priority}={priority_points.get(priority, 0)}")
