package main

import (
  "bufio"
  "encoding/json"
  "fmt"
  "os"
)

type Task struct {
  Status   string `json:"status"`
  Priority string `json:"priority"`
  Estimate int    `json:"estimate"`
}

func main() {
  if len(os.Args) != 2 {
    fmt.Fprintln(os.Stderr, "usage: tasks_cli.go <tasks.jsonl>")
    os.Exit(1)
  }

  file, err := os.Open(os.Args[1])
  if err != nil {
    fmt.Fprintln(os.Stderr, err)
    os.Exit(1)
  }
  defer file.Close()

  statusCounts := map[string]int{}
  priorityPoints := map[string]int{}
  total := 0

  scanner := bufio.NewScanner(file)
  for scanner.Scan() {
    line := scanner.Bytes()
    if len(line) == 0 {
      continue
    }
    var task Task
    if err := json.Unmarshal(line, &task); err != nil {
      fmt.Fprintln(os.Stderr, err)
      os.Exit(1)
    }
    total++
    statusCounts[task.Status]++
    priorityPoints[task.Priority] += task.Estimate
  }
  if err := scanner.Err(); err != nil {
    fmt.Fprintln(os.Stderr, err)
    os.Exit(1)
  }

  fmt.Printf("total_tasks=%d\n", total)
  for _, status := range []string{"todo", "in_progress", "done"} {
    fmt.Printf("status_%s=%d\n", status, statusCounts[status])
  }
  for _, priority := range []string{"high", "medium", "low"} {
    fmt.Printf("points_%s=%d\n", priority, priorityPoints[priority])
  }
}
