#!/usr/bin/env python3
import json
import re
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

TODAY = date.fromisoformat("2026-04-17")
TASKS = json.loads(Path(__file__).with_name("tasks.json").read_text())
NEXT_ID = max(t["id"] for t in TASKS) + 1
VALID_STATUS = {"todo", "in_progress", "done", "blocked"}
VALID_PRIORITY = {"high", "medium", "low"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_overdue(task):
    due_date = task.get("due_date")
    return isinstance(due_date, str) and DATE_RE.match(due_date) and due_date < TODAY.isoformat() and task["status"] != "done"


def summary(tasks):
    out = {"total_tasks": len(tasks), "overdue_tasks": sum(1 for t in tasks if is_overdue(t))}
    for status in ["todo", "in_progress", "done", "blocked"]:
        out[f"status_{status}"] = sum(1 for t in tasks if t["status"] == status)
    for priority in ["high", "medium", "low"]:
        out[f"points_{priority}"] = sum(t["estimate"] for t in tasks if t["priority"] == priority)
    return out


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        raw = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/tasks":
            self._send(200, {"tasks": TASKS})
        elif self.path == "/summary":
            self._send(200, summary(TASKS))
        else:
            self._send(404, {"error": "not_found"})

    def do_POST(self):
        global NEXT_ID
        if self.path != "/tasks":
            return self._send(404, {"error": "not_found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid_json"})
        errors = []
        if not isinstance(payload.get("title"), str) or not payload["title"].strip():
            errors.append("title must be non-empty string")
        if payload.get("status") not in VALID_STATUS:
            errors.append("status must be one of todo, in_progress, done, blocked")
        if payload.get("priority") not in VALID_PRIORITY:
            errors.append("priority must be one of high, medium, low")
        if not isinstance(payload.get("estimate"), int) or payload["estimate"] < 0:
            errors.append("estimate must be non-negative integer")
        due_date = payload.get("due_date")
        if due_date is not None and (not isinstance(due_date, str) or not DATE_RE.match(due_date)):
            errors.append("due_date must be YYYY-MM-DD")
        if errors:
            return self._send(400, {"error": "validation_error", "details": errors})
        task = {
            "id": NEXT_ID,
            "title": payload["title"].strip(),
            "status": payload["status"],
            "priority": payload["priority"],
            "estimate": payload["estimate"],
        }
        if due_date is not None:
            task["due_date"] = due_date
        NEXT_ID += 1
        TASKS.append(task)
        self._send(201, task)

    def log_message(self, fmt, *args):
        return


HTTPServer(("127.0.0.1", 8121), Handler).serve_forever()
