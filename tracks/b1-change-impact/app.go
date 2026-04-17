package main

import (
  "encoding/json"
  "net/http"
  "net/url"
  "os"
  "strings"
)

type Task struct {
  ID       int    `json:"id"`
  Title    string `json:"title"`
  Status   string `json:"status"`
  Priority string `json:"priority"`
  Estimate int    `json:"estimate"`
}

var tasks []Task
var nextID int

func send(w http.ResponseWriter, code int, body any) {
  raw, _ := json.Marshal(body)
  w.Header().Set("Content-Type", "application/json")
  w.WriteHeader(code)
  _, _ = w.Write(raw)
}

func summary(source []Task) map[string]int {
  out := map[string]int{"total_tasks": len(source), "status_todo": 0, "status_in_progress": 0, "status_done": 0, "status_blocked": 0, "points_high": 0, "points_medium": 0, "points_low": 0}
  for _, t := range source {
    switch t.Status {
    case "todo": out["status_todo"]++
    case "in_progress": out["status_in_progress"]++
    case "done": out["status_done"]++
    case "blocked": out["status_blocked"]++
    }
    switch t.Priority {
    case "high": out["points_high"] += t.Estimate
    case "medium": out["points_medium"] += t.Estimate
    case "low": out["points_low"] += t.Estimate
    }
  }
  return out
}

func filterByStatus(source []Task, status string) []Task {
  if status == "" { return source }
  filtered := []Task{}
  for _, t := range source {
    if t.Status == status { filtered = append(filtered, t) }
  }
  return filtered
}

func main() {
  raw, err := os.ReadFile("tasks.json")
  if err != nil { panic(err) }
  if err := json.Unmarshal(raw, &tasks); err != nil { panic(err) }
  nextID = 1
  for _, t := range tasks { if t.ID >= nextID { nextID = t.ID + 1 } }

  http.HandleFunc("/tasks", func(w http.ResponseWriter, r *http.Request) {
    if r.Method == http.MethodGet {
      parsed, _ := url.Parse(r.URL.String())
      send(w, 200, map[string]any{"tasks": filterByStatus(tasks, parsed.Query().Get("status"))})
      return
    }
    if r.Method != http.MethodPost { send(w, 405, map[string]string{"error": "method_not_allowed"}); return }
    var payload Task
    if err := json.NewDecoder(r.Body).Decode(&payload); err != nil { send(w, 400, map[string]string{"error": "invalid_json"}); return }
    errors := []string{}
    payload.Title = strings.TrimSpace(payload.Title)
    if payload.Title == "" { errors = append(errors, "title must be non-empty string") }
    if payload.Status != "todo" && payload.Status != "in_progress" && payload.Status != "done" && payload.Status != "blocked" { errors = append(errors, "status must be one of todo, in_progress, done, blocked") }
    if payload.Priority != "high" && payload.Priority != "medium" && payload.Priority != "low" { errors = append(errors, "priority must be one of high, medium, low") }
    if payload.Estimate < 0 { errors = append(errors, "estimate must be non-negative integer") }
    if len(errors) > 0 { send(w, 400, map[string]any{"error": "validation_error", "details": errors}); return }
    payload.ID = nextID
    nextID++
    tasks = append(tasks, payload)
    send(w, 201, payload)
  })
  http.HandleFunc("/summary", func(w http.ResponseWriter, r *http.Request) { send(w, 200, summary(tasks)) })
  http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) { send(w, 404, map[string]string{"error": "not_found"}) })
  if err := http.ListenAndServe("127.0.0.1:8113", nil); err != nil { panic(err) }
}
