#!/usr/bin/env node
import { readFileSync } from 'node:fs';

const input = process.argv[2];
if (!input) {
  console.error('usage: tasks_cli.ts <tasks.jsonl>');
  process.exit(1);
}

const statusCounts = new Map<string, number>();
const priorityPoints = new Map<string, number>();
let total = 0;

for (const rawLine of readFileSync(input, 'utf8').split(/\r?\n/)) {
  const line = rawLine.trim();
  if (!line) continue;
  const task = JSON.parse(line) as {
    status: string;
    priority: string;
    estimate?: number;
  };
  total += 1;
  statusCounts.set(task.status, (statusCounts.get(task.status) ?? 0) + 1);
  priorityPoints.set(task.priority, (priorityPoints.get(task.priority) ?? 0) + (task.estimate ?? 0));
}

console.log(`total_tasks=${total}`);
for (const status of ['todo', 'in_progress', 'done']) {
  console.log(`status_${status}=${statusCounts.get(status) ?? 0}`);
}
for (const priority of ['high', 'medium', 'low']) {
  console.log(`points_${priority}=${priorityPoints.get(priority) ?? 0}`);
}
