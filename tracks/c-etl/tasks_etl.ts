/// <reference types="node" />
import * as fs from 'fs';

type Status = 'todo' | 'in_progress' | 'done';
type Priority = 'high' | 'medium' | 'low';

type Task = {
  id: number;
  title: string;
  status: Status;
  priority: Priority;
  estimate: number;
};

type Summary = {
  total_tasks: number;
  status_counts: Record<string, number>;
  points_by_priority: Record<Priority, number>;
};

function parseCsv(input: string): Task[] {
  const [headerLine, ...lines] = input.trim().split(/\r?\n/);
  const headers = headerLine.split(',');
  return lines.map((line) => {
    const cols = line.split(',');
    const row = Object.fromEntries(headers.map((h, i) => [h, cols[i]]));
    return {
      id: Number(row.id),
      title: row.title,
      status: row.status as Status,
      priority: row.priority as Priority,
      estimate: Number(row.estimate),
    };
  });
}

function summarize(tasks: Task[]): Summary {
  const status_counts: Record<string, number> = {};
  const points_by_priority: Record<Priority, number> = { high: 0, medium: 0, low: 0 };
  for (const task of tasks) {
    status_counts[task.status] = (status_counts[task.status] ?? 0) + 1;
    points_by_priority[task.priority] += task.estimate;
  }
  return { total_tasks: tasks.length, status_counts, points_by_priority };
}

const tasks = parseCsv(fs.readFileSync(process.argv[2], 'utf8'));
const summary = summarize(tasks);
fs.writeFileSync(process.argv[3], JSON.stringify({ tasks, summary }, null, 2) + '\n');
console.log(JSON.stringify(summary));
