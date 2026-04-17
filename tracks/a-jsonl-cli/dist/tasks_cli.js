#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const node_fs_1 = require("node:fs");
const input = process.argv[2];
if (!input) {
    console.error('usage: tasks_cli.ts <tasks.jsonl>');
    process.exit(1);
}
const statusCounts = new Map();
const priorityPoints = new Map();
let total = 0;
for (const rawLine of (0, node_fs_1.readFileSync)(input, 'utf8').split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line)
        continue;
    const task = JSON.parse(line);
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
