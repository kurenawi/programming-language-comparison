package main

import (
  "encoding/csv"
  "encoding/json"
  "fmt"
  "os"
  "strconv"
)

type Task struct {
  ID       int    `json:"id"`
  Title    string `json:"title"`
  Status   string `json:"status"`
  Priority string `json:"priority"`
  Estimate int    `json:"estimate"`
}

type Summary struct {
  TotalTasks       int            `json:"total_tasks"`
  StatusCounts     map[string]int `json:"status_counts"`
  PointsByPriority map[string]int `json:"points_by_priority"`
}

type Output struct {
  Tasks   []Task  `json:"tasks"`
  Summary Summary `json:"summary"`
}

func main() {
  src, dst := os.Args[1], os.Args[2]
  f, err := os.Open(src)
  if err != nil { panic(err) }
  defer f.Close()
  rows, err := csv.NewReader(f).ReadAll()
  if err != nil { panic(err) }

  var tasks []Task
  for _, row := range rows[1:] {
    id, _ := strconv.Atoi(row[0])
    estimate, _ := strconv.Atoi(row[4])
    tasks = append(tasks, Task{ID: id, Title: row[1], Status: row[2], Priority: row[3], Estimate: estimate})
  }

  summary := Summary{TotalTasks: len(tasks), StatusCounts: map[string]int{}, PointsByPriority: map[string]int{"high": 0, "medium": 0, "low": 0}}
  for _, task := range tasks {
    summary.StatusCounts[task.Status]++
    summary.PointsByPriority[task.Priority] += task.Estimate
  }

  out, _ := json.MarshalIndent(Output{Tasks: tasks, Summary: summary}, "", "  ")
  if err := os.WriteFile(dst, append(out, '\n'), 0644); err != nil { panic(err) }
  stdout, _ := json.Marshal(summary)
  fmt.Println(string(stdout))
}
