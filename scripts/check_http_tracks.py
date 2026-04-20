#!/usr/bin/env python3
import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent

TRACKS = [
    {
        "name": "b-http-api",
        "dir": ROOT / "tracks" / "b-http-api",
        "languages": [
            {
                "name": "Python",
                "port": 8011,
                "start": [sys.executable, "app.py"],
                "cwd": ROOT / "tracks" / "b-http-api",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("POST", "/tasks", {"title": "review api", "status": "todo", "priority": "high", "estimate": 4}, 201, {"id": 4, "title": "review api", "status": "todo", "priority": "high", "estimate": 4}),
                    ("POST", "/tasks", {"title": "", "status": "blocked", "priority": "urgent", "estimate": -1}, 400, {"error": "validation_error", "details": ["title must be non-empty string", "status must be one of todo, in_progress, done", "priority must be one of high, medium, low", "estimate must be non-negative integer"]}),
                    ("GET", "/summary", None, 200, {"total_tasks": 4, "status_todo": 2, "status_in_progress": 1, "status_done": 1, "points_high": 7, "points_medium": 2, "points_low": 5}),
                ],
            },
            {
                "name": "TypeScript",
                "port": 8012,
                "compile": True,
                "start": ["node", "dist/app.js"],
                "cwd": ROOT / "tracks" / "b-http-api",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("POST", "/tasks", {"title": "review api", "status": "todo", "priority": "high", "estimate": 4}, 201, {"id": 4, "title": "review api", "status": "todo", "priority": "high", "estimate": 4}),
                    ("POST", "/tasks", {"title": "", "status": "blocked", "priority": "urgent", "estimate": -1}, 400, {"error": "validation_error", "details": ["title must be non-empty string", "status must be one of todo, in_progress, done", "priority must be one of high, medium, low", "estimate must be non-negative integer"]}),
                    ("GET", "/summary", None, 200, {"total_tasks": 4, "status_todo": 2, "status_in_progress": 1, "status_done": 1, "points_high": 7, "points_medium": 2, "points_low": 5}),
                ],
            },
            {
                "name": "Go",
                "port": 8013,
                "start": ["go", "run", "app.go"],
                "cwd": ROOT / "tracks" / "b-http-api",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("POST", "/tasks", {"title": "review api", "status": "todo", "priority": "high", "estimate": 4}, 201, {"id": 4, "title": "review api", "status": "todo", "priority": "high", "estimate": 4}),
                    ("POST", "/tasks", {"title": "", "status": "blocked", "priority": "urgent", "estimate": -1}, 400, {"error": "validation_error", "details": ["title must be non-empty string", "status must be one of todo, in_progress, done", "priority must be one of high, medium, low", "estimate must be non-negative integer"]}),
                    ("GET", "/summary", None, 200, {"total_tasks": 4, "status_todo": 2, "status_in_progress": 1, "status_done": 1, "points_high": 7, "points_medium": 2, "points_low": 5}),
                ],
            },
        ],
    },
    {
        "name": "b1-change-impact",
        "dir": ROOT / "tracks" / "b1-change-impact",
        "languages": [
            {
                "name": "Python",
                "port": 8111,
                "start": [sys.executable, "app.py"],
                "cwd": ROOT / "tracks" / "b1-change-impact",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 0, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("POST", "/tasks", {"title": "wait vendor", "status": "blocked", "priority": "high", "estimate": 2}, 201, {"id": 4, "title": "wait vendor", "status": "blocked", "priority": "high", "estimate": 2}),
                    ("GET", "/tasks?status=blocked", None, 200, {"tasks": [{"id": 4, "title": "wait vendor", "status": "blocked", "priority": "high", "estimate": 2}]}),
                ],
            },
            {
                "name": "TypeScript",
                "port": 8112,
                "compile": True,
                "start": ["node", "dist/app.js"],
                "cwd": ROOT / "tracks" / "b1-change-impact",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 0, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("POST", "/tasks", {"title": "wait vendor", "status": "blocked", "priority": "high", "estimate": 2}, 201, {"id": 4, "title": "wait vendor", "status": "blocked", "priority": "high", "estimate": 2}),
                    ("GET", "/tasks?status=blocked", None, 200, {"tasks": [{"id": 4, "title": "wait vendor", "status": "blocked", "priority": "high", "estimate": 2}]}),
                ],
            },
            {
                "name": "Go",
                "port": 8113,
                "start": ["go", "run", "app.go"],
                "cwd": ROOT / "tracks" / "b1-change-impact",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 0, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("POST", "/tasks", {"title": "wait vendor", "status": "blocked", "priority": "high", "estimate": 2}, 201, {"id": 4, "title": "wait vendor", "status": "blocked", "priority": "high", "estimate": 2}),
                    ("GET", "/tasks?status=blocked", None, 200, {"tasks": [{"id": 4, "title": "wait vendor", "status": "blocked", "priority": "high", "estimate": 2}]}),
                ],
            },
        ],
    },
    {
        "name": "r2-optional-due-date",
        "dir": ROOT / "tracks" / "r2-optional-due-date",
        "languages": [
            {
                "name": "Python",
                "port": 8121,
                "start": [sys.executable, "app.py"],
                "cwd": ROOT / "tracks" / "r2-optional-due-date",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "overdue_tasks": 1, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 0, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("GET", "/tasks", None, 200, {"tasks": [{"id": 1, "title": "draft spec", "status": "todo", "priority": "high", "estimate": 3, "due_date": "2026-04-10"}, {"id": 2, "title": "implement API", "status": "in_progress", "priority": "medium", "estimate": 2}, {"id": 3, "title": "ship release", "status": "done", "priority": "low", "estimate": 5, "due_date": "2026-04-15"}]}),
                    ("POST", "/tasks", {"title": "follow up vendor", "status": "blocked", "priority": "high", "estimate": 2, "due_date": "2026-04-20"}, 201, {"id": 4, "title": "follow up vendor", "status": "blocked", "priority": "high", "estimate": 2, "due_date": "2026-04-20"}),
                    ("POST", "/tasks", {"title": "bad due date", "status": "todo", "priority": "high", "estimate": 1, "due_date": "2026/04/20"}, 400, {"error": "validation_error", "details": ["due_date must be YYYY-MM-DD"]}),
                    ("GET", "/summary", None, 200, {"total_tasks": 4, "overdue_tasks": 1, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 1, "points_high": 5, "points_medium": 2, "points_low": 5}),
                ],
            },
            {
                "name": "TypeScript",
                "port": 8122,
                "compile": True,
                "start": ["node", "dist/app.js"],
                "cwd": ROOT / "tracks" / "r2-optional-due-date",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "overdue_tasks": 1, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 0, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("GET", "/tasks", None, 200, {"tasks": [{"id": 1, "title": "draft spec", "status": "todo", "priority": "high", "estimate": 3, "due_date": "2026-04-10"}, {"id": 2, "title": "implement API", "status": "in_progress", "priority": "medium", "estimate": 2}, {"id": 3, "title": "ship release", "status": "done", "priority": "low", "estimate": 5, "due_date": "2026-04-15"}]}),
                    ("POST", "/tasks", {"title": "follow up vendor", "status": "blocked", "priority": "high", "estimate": 2, "due_date": "2026-04-20"}, 201, {"id": 4, "title": "follow up vendor", "status": "blocked", "priority": "high", "estimate": 2, "due_date": "2026-04-20"}),
                    ("POST", "/tasks", {"title": "bad due date", "status": "todo", "priority": "high", "estimate": 1, "due_date": "2026/04/20"}, 400, {"error": "validation_error", "details": ["due_date must be YYYY-MM-DD"]}),
                    ("GET", "/summary", None, 200, {"total_tasks": 4, "overdue_tasks": 1, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 1, "points_high": 5, "points_medium": 2, "points_low": 5}),
                ],
            },
            {
                "name": "Go",
                "port": 8123,
                "start": ["go", "run", "app.go"],
                "cwd": ROOT / "tracks" / "r2-optional-due-date",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "overdue_tasks": 1, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 0, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("GET", "/tasks", None, 200, {"tasks": [{"id": 1, "title": "draft spec", "status": "todo", "priority": "high", "estimate": 3, "due_date": "2026-04-10"}, {"id": 2, "title": "implement API", "status": "in_progress", "priority": "medium", "estimate": 2}, {"id": 3, "title": "ship release", "status": "done", "priority": "low", "estimate": 5, "due_date": "2026-04-15"}]}),
                    ("POST", "/tasks", {"title": "follow up vendor", "status": "blocked", "priority": "high", "estimate": 2, "due_date": "2026-04-20"}, 201, {"id": 4, "title": "follow up vendor", "status": "blocked", "priority": "high", "estimate": 2, "due_date": "2026-04-20"}),
                    ("POST", "/tasks", {"title": "bad due date", "status": "todo", "priority": "high", "estimate": 1, "due_date": "2026/04/20"}, 400, {"error": "validation_error", "details": ["due_date must be YYYY-MM-DD"]}),
                    ("GET", "/summary", None, 200, {"total_tasks": 4, "overdue_tasks": 1, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 1, "points_high": 5, "points_medium": 2, "points_low": 5}),
                ],
            },
            {
                "name": "Rust",
                "port": 8124,
                "start": ["cargo", "run", "--quiet"],
                "cwd": ROOT / "tracks" / "r2-optional-due-date",
                "checks": [
                    ("GET", "/summary", None, 200, {"total_tasks": 3, "overdue_tasks": 1, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 0, "points_high": 3, "points_medium": 2, "points_low": 5}),
                    ("GET", "/tasks", None, 200, {"tasks": [{"id": 1, "title": "draft spec", "status": "todo", "priority": "high", "estimate": 3, "due_date": "2026-04-10"}, {"id": 2, "title": "implement API", "status": "in_progress", "priority": "medium", "estimate": 2}, {"id": 3, "title": "ship release", "status": "done", "priority": "low", "estimate": 5, "due_date": "2026-04-15"}]}),
                    ("POST", "/tasks", {"title": "follow up vendor", "status": "blocked", "priority": "high", "estimate": 2, "due_date": "2026-04-20"}, 201, {"id": 4, "title": "follow up vendor", "status": "blocked", "priority": "high", "estimate": 2, "due_date": "2026-04-20"}),
                    ("POST", "/tasks", {"title": "bad due date", "status": "todo", "priority": "high", "estimate": 1, "due_date": "2026/04/20"}, 400, {"error": "validation_error", "details": ["due_date must be YYYY-MM-DD"]}),
                    ("GET", "/summary", None, 200, {"total_tasks": 4, "overdue_tasks": 1, "status_todo": 1, "status_in_progress": 1, "status_done": 1, "status_blocked": 1, "points_high": 5, "points_medium": 2, "points_low": 5}),
                ],
            },
        ],
    },
]


def kill_port(port: int) -> None:
    lsof = shutil.which("lsof")
    if not lsof:
        return
    result = subprocess.run(
        [lsof, "-ti", f"tcp:{port}"],
        check=False,
        capture_output=True,
        text=True,
    )
    for pid in result.stdout.split():
        subprocess.run(["kill", pid], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.stdout:
        time.sleep(0.2)


def wait_for_port(port: int, timeout: float = 10.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError(f"timed out waiting for port {port}")


def request_json(port: int, method: str, path: str, payload):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(f"http://127.0.0.1:{port}{path}", data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=5) as resp:
            return resp.getcode(), json.load(resp)
    except HTTPError as err:
        body = err.read().decode()
        return err.code, json.loads(body)


def ensure_ts_toolchain(track_dir: Path) -> None:
    if shutil.which("npm") is None:
        raise RuntimeError("npm is required for TypeScript track verification")
    ts_bin = track_dir / "node_modules" / ".bin" / "tsc"
    if not ts_bin.exists():
        subprocess.run(["npm", "ci"], cwd=track_dir, check=True, stdout=subprocess.DEVNULL)


def compile_ts(track_dir: Path) -> None:
    ensure_ts_toolchain(track_dir)
    dist_dir = track_dir / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    subprocess.run(
        [
            str(track_dir / "node_modules" / ".bin" / "tsc"),
            "app.ts",
            "--outDir",
            "dist",
            "--module",
            "nodenext",
            "--target",
            "es2020",
            "--moduleResolution",
            "nodenext",
            "--types",
            "node",
            "--esModuleInterop",
            "--skipLibCheck",
        ],
        cwd=track_dir,
        check=True,
        stdout=subprocess.DEVNULL,
    )


def run_language(lang_cfg):
    kill_port(lang_cfg["port"])
    if lang_cfg.get("compile"):
        compile_ts(lang_cfg["cwd"])
    proc = subprocess.Popen(
        lang_cfg["start"],
        cwd=lang_cfg["cwd"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        wait_for_port(lang_cfg["port"])
        for method, path, payload, expected_status, expected_body in lang_cfg["checks"]:
            status, body = request_json(lang_cfg["port"], method, path, payload)
            assert status == expected_status, (lang_cfg["name"], method, path, status, expected_status, body)
            assert body == expected_body, (lang_cfg["name"], method, path, body, expected_body)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)


def main():
    for track in TRACKS:
        print(f"[{track['name']}]")
        for lang in track["languages"]:
            print(f"  - {lang['name']} ... ", end="", flush=True)
            run_language(lang)
            print("ok")
    print("HTTP track checks passed.")


if __name__ == "__main__":
    main()
