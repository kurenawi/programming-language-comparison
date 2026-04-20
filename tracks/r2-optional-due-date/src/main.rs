use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::fs;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use tiny_http::{Header, Method, Response, Server, StatusCode};

const TODAY: &str = "2026-04-17";
const DATE_LEN: usize = 10;

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Task {
    id: i64,
    title: String,
    status: String,
    priority: String,
    estimate: i64,
    #[serde(skip_serializing_if = "Option::is_none")]
    due_date: Option<String>,
}

#[derive(Debug, Deserialize)]
struct IncomingTask {
    title: Option<String>,
    status: Option<String>,
    priority: Option<String>,
    estimate: Option<i64>,
    due_date: Option<String>,
}

#[derive(Debug)]
struct State {
    tasks: Vec<Task>,
    next_id: i64,
}

fn is_valid_date(date: &str) -> bool {
    date.len() == DATE_LEN
        && date
            .chars()
            .enumerate()
            .all(|(i, c)| matches!(i, 4 | 7) && c == '-' || !matches!(i, 4 | 7) && c.is_ascii_digit())
}

fn is_overdue(task: &Task) -> bool {
    matches!(task.due_date.as_deref(), Some(d) if is_valid_date(d) && d < TODAY && task.status != "done")
}

fn summary(tasks: &[Task]) -> Value {
    let mut status_todo = 0;
    let mut status_in_progress = 0;
    let mut status_done = 0;
    let mut status_blocked = 0;
    let mut points_high = 0;
    let mut points_medium = 0;
    let mut points_low = 0;
    let mut overdue_tasks = 0;

    for task in tasks {
        if is_overdue(task) {
            overdue_tasks += 1;
        }
        match task.status.as_str() {
            "todo" => status_todo += 1,
            "in_progress" => status_in_progress += 1,
            "done" => status_done += 1,
            "blocked" => status_blocked += 1,
            _ => {}
        }
        match task.priority.as_str() {
            "high" => points_high += task.estimate,
            "medium" => points_medium += task.estimate,
            "low" => points_low += task.estimate,
            _ => {}
        }
    }

    json!({
        "total_tasks": tasks.len(),
        "overdue_tasks": overdue_tasks,
        "status_todo": status_todo,
        "status_in_progress": status_in_progress,
        "status_done": status_done,
        "status_blocked": status_blocked,
        "points_high": points_high,
        "points_medium": points_medium,
        "points_low": points_low,
    })
}

fn send_json(request: tiny_http::Request, code: u16, body: Value) {
    let payload = body.to_string();
    let response = Response::from_string(payload)
        .with_status_code(StatusCode(code))
        .with_header(
            Header::from_bytes(b"Content-Type", b"application/json").expect("valid header"),
        );
    let _ = request.respond(response);
}

fn main() {
    let base_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let tasks_path = base_dir.join("tasks.json");
    let raw = fs::read_to_string(tasks_path).expect("read tasks.json");
    let tasks: Vec<Task> = serde_json::from_str(&raw).expect("parse tasks.json");
    let next_id = tasks.iter().map(|t| t.id).max().unwrap_or(0) + 1;
    let state = Arc::new(Mutex::new(State { tasks, next_id }));

    let server = Server::http("127.0.0.1:8124").expect("bind 8124");
    for mut request in server.incoming_requests() {
        let method = request.method().clone();
        let path = request.url().to_string();

        if method == Method::Get && path == "/tasks" {
            let tasks = state.lock().expect("lock state").tasks.clone();
            send_json(request, 200, json!({ "tasks": tasks }));
            continue;
        }

        if method == Method::Get && path == "/summary" {
            let tasks = state.lock().expect("lock state").tasks.clone();
            send_json(request, 200, summary(&tasks));
            continue;
        }

        if method == Method::Post && path == "/tasks" {
            let mut body = String::new();
            if request.as_reader().read_to_string(&mut body).is_err() {
                send_json(request, 400, json!({ "error": "invalid_json" }));
                continue;
            }

            let payload: IncomingTask = match serde_json::from_str(&body) {
                Ok(value) => value,
                Err(_) => {
                    send_json(request, 400, json!({ "error": "invalid_json" }));
                    continue;
                }
            };

            let mut errors: Vec<String> = Vec::new();
            let title = payload.title.unwrap_or_default().trim().to_string();
            if title.is_empty() {
                errors.push("title must be non-empty string".to_string());
            }

            let status = payload.status.unwrap_or_default();
            if !matches!(status.as_str(), "todo" | "in_progress" | "done" | "blocked") {
                errors.push("status must be one of todo, in_progress, done, blocked".to_string());
            }

            let priority = payload.priority.unwrap_or_default();
            if !matches!(priority.as_str(), "high" | "medium" | "low") {
                errors.push("priority must be one of high, medium, low".to_string());
            }

            let estimate = payload.estimate.unwrap_or(-1);
            if estimate < 0 {
                errors.push("estimate must be non-negative integer".to_string());
            }

            let due_date = payload.due_date;
            if let Some(ref due_date_value) = due_date {
                if !is_valid_date(due_date_value) {
                    errors.push("due_date must be YYYY-MM-DD".to_string());
                }
            }

            if !errors.is_empty() {
                send_json(request, 400, json!({ "error": "validation_error", "details": errors }));
                continue;
            }

            let mut state = state.lock().expect("lock state");
            let task = Task {
                id: state.next_id,
                title,
                status,
                priority,
                estimate,
                due_date,
            };
            state.next_id += 1;
            state.tasks.push(task.clone());
            send_json(request, 201, serde_json::to_value(task).expect("serialize task"));
            continue;
        }

        send_json(request, 404, json!({ "error": "not_found" }));
    }
}
