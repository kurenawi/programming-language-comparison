"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
/// <reference types="node" />
const fs = __importStar(require("fs"));
function parseCsv(input) {
    const [headerLine, ...lines] = input.trim().split(/\r?\n/);
    const headers = headerLine.split(',');
    return lines.map((line) => {
        const cols = line.split(',');
        const row = Object.fromEntries(headers.map((h, i) => [h, cols[i]]));
        return {
            id: Number(row.id),
            title: row.title,
            status: row.status,
            priority: row.priority,
            estimate: Number(row.estimate),
        };
    });
}
function summarize(tasks) {
    const status_counts = {};
    const points_by_priority = { high: 0, medium: 0, low: 0 };
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
