"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const node_http_1 = require("node:http");
const node_fs_1 = require("node:fs");
const node_path_1 = require("node:path");
const tasks = JSON.parse((0, node_fs_1.readFileSync)((0, node_path_1.join)(__dirname, "..", "tasks.json"), "utf8"));
let nextId = Math.max(...tasks.map((t) => t.id)) + 1;
function send(res, code, body) {
    const raw = JSON.stringify(body);
    res.writeHead(code, { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(raw) });
    res.end(raw);
}
function summary(source) {
    const count = (value) => source.filter((t) => t.status === value).length;
    const points = (priority) => source.filter((t) => t.priority === priority).reduce((sum, t) => sum + t.estimate, 0);
    return {
        total_tasks: source.length,
        status_todo: count("todo"),
        status_in_progress: count("in_progress"),
        status_done: count("done"),
        status_blocked: count("blocked"),
        points_high: points("high"),
        points_medium: points("medium"),
        points_low: points("low"),
    };
}
(0, node_http_1.createServer)((req, res) => {
    const url = new URL(req.url ?? "/", "http://127.0.0.1");
    if (req.method === "GET" && url.pathname === "/tasks") {
        const status = url.searchParams.get("status");
        const filtered = status ? tasks.filter((t) => t.status === status) : tasks;
        return send(res, 200, { tasks: filtered });
    }
    if (req.method === "GET" && url.pathname === "/summary")
        return send(res, 200, summary(tasks));
    if (req.method === "POST" && url.pathname === "/tasks") {
        let raw = "";
        req.on("data", (chunk) => (raw += chunk.toString()));
        req.on("end", () => {
            let payload;
            try {
                payload = raw ? JSON.parse(raw) : {};
            }
            catch {
                return send(res, 400, { error: "invalid_json" });
            }
            const errors = [];
            if (typeof payload.title !== "string" || payload.title.trim() === "")
                errors.push("title must be non-empty string");
            if (!["todo", "in_progress", "done", "blocked"].includes(payload.status))
                errors.push("status must be one of todo, in_progress, done, blocked");
            if (!["high", "medium", "low"].includes(payload.priority))
                errors.push("priority must be one of high, medium, low");
            if (!Number.isInteger(payload.estimate) || payload.estimate < 0)
                errors.push("estimate must be non-negative integer");
            if (errors.length)
                return send(res, 400, { error: "validation_error", details: errors });
            const task = { id: nextId++, title: payload.title.trim(), status: payload.status, priority: payload.priority, estimate: payload.estimate };
            tasks.push(task);
            return send(res, 201, task);
        });
        return;
    }
    return send(res, 404, { error: "not_found" });
}).listen(8112, "127.0.0.1");
