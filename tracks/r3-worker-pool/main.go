package main

import (
  "context"
  "encoding/json"
  "fmt"
  "os"
  "sort"
  "sync"
  "sync/atomic"
  "time"
)

type Job struct {
  ID         string `json:"id"`
  Kind       string `json:"kind"`
  DurationMs int    `json:"duration_ms"`
  MaxRetries int    `json:"max_retries"`
}

type AttemptLog struct {
  JobID    string `json:"job_id"`
  Attempt  int    `json:"attempt"`
  Outcome  string `json:"outcome"`
  Detail   string `json:"detail"`
}

type JobResult struct {
  JobID       string `json:"job_id"`
  FinalStatus string `json:"final_status"`
  Attempts    int    `json:"attempts"`
  TimedOut    bool   `json:"timed_out"`
  Retried     bool   `json:"retried"`
}

type Summary struct {
  TotalJobs     int         `json:"total_jobs"`
  Succeeded     int         `json:"succeeded"`
  Failed        int         `json:"failed"`
  TimedOut      int         `json:"timed_out"`
  RetriedJobs   int         `json:"retried_jobs"`
  TotalAttempts int         `json:"total_attempts"`
  WorkerCount   int         `json:"worker_count"`
  TimeoutMs     int         `json:"timeout_ms"`
  Results       []JobResult `json:"results"`
  Logs          []AttemptLog `json:"logs"`
}

func main() {
  if len(os.Args) < 2 {
    fmt.Fprintln(os.Stderr, "usage: go run main.go <jobs.json> [worker_count] [timeout_ms]")
    os.Exit(1)
  }
  workerCount := 4
  timeoutMs := 250
  if len(os.Args) >= 3 {
    fmt.Sscanf(os.Args[2], "%d", &workerCount)
  }
  if len(os.Args) >= 4 {
    fmt.Sscanf(os.Args[3], "%d", &timeoutMs)
  }

  jobs, err := loadJobs(os.Args[1])
  if err != nil {
    fmt.Fprintln(os.Stderr, err)
    os.Exit(1)
  }

  summary := runJobs(jobs, workerCount, timeoutMs)
  enc := json.NewEncoder(os.Stdout)
  enc.SetIndent("", "  ")
  _ = enc.Encode(summary)
}

func loadJobs(path string) ([]Job, error) {
  data, err := os.ReadFile(path)
  if err != nil { return nil, err }
  var jobs []Job
  if err := json.Unmarshal(data, &jobs); err != nil { return nil, err }
  return jobs, nil
}

func runJobs(jobs []Job, workerCount, timeoutMs int) Summary {
  jobCh := make(chan Job)
  resultsCh := make(chan JobResult, len(jobs))
  logCh := make(chan AttemptLog, len(jobs)*8)
  var flakyState sync.Map
  var wg sync.WaitGroup
  var totalAttempts atomic.Int64

  worker := func() {
    defer wg.Done()
    for job := range jobCh {
      result := executeJob(job, timeoutMs, &flakyState, &totalAttempts, logCh)
      resultsCh <- result
    }
  }

  for i := 0; i < workerCount; i++ {
    wg.Add(1)
    go worker()
  }

  go func() {
    for _, job := range jobs { jobCh <- job }
    close(jobCh)
    wg.Wait()
    close(resultsCh)
    close(logCh)
  }()

  summary := Summary{TotalJobs: len(jobs), WorkerCount: workerCount, TimeoutMs: timeoutMs}
  for result := range resultsCh {
    summary.Results = append(summary.Results, result)
    if result.FinalStatus == "succeeded" { summary.Succeeded++ } else { summary.Failed++ }
    if result.TimedOut { summary.TimedOut++ }
    if result.Retried { summary.RetriedJobs++ }
  }
  for log := range logCh { summary.Logs = append(summary.Logs, log) }
  summary.TotalAttempts = int(totalAttempts.Load())

  sort.Slice(summary.Results, func(i, j int) bool { return summary.Results[i].JobID < summary.Results[j].JobID })
  sort.Slice(summary.Logs, func(i, j int) bool {
    if summary.Logs[i].JobID == summary.Logs[j].JobID { return summary.Logs[i].Attempt < summary.Logs[j].Attempt }
    return summary.Logs[i].JobID < summary.Logs[j].JobID
  })
  return summary
}

func executeJob(job Job, timeoutMs int, flakyState *sync.Map, totalAttempts *atomic.Int64, logCh chan<- AttemptLog) JobResult {
  attempts := 0
  timedOut := false
  retried := false
  for {
    attempts++
    totalAttempts.Add(1)
    outcome, detail := runAttempt(job, attempts, timeoutMs, flakyState)
    logCh <- AttemptLog{JobID: job.ID, Attempt: attempts, Outcome: outcome, Detail: detail}

    if outcome == "succeeded" {
      return JobResult{JobID: job.ID, FinalStatus: "succeeded", Attempts: attempts, TimedOut: timedOut, Retried: retried}
    }
    if outcome == "timed_out" { timedOut = true }
    if attempts <= job.MaxRetries {
      retried = true
      continue
    }
    return JobResult{JobID: job.ID, FinalStatus: "failed", Attempts: attempts, TimedOut: timedOut, Retried: retried}
  }
}

func runAttempt(job Job, attempt, timeoutMs int, flakyState *sync.Map) (string, string) {
  ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeoutMs)*time.Millisecond)
  defer cancel()

  resultCh := make(chan struct {
    outcome string
    detail  string
  }, 1)

  go func() {
    time.Sleep(time.Duration(job.DurationMs) * time.Millisecond)
    switch job.Kind {
    case "fast", "slow":
      resultCh <- struct{ outcome, detail string }{"succeeded", "completed normally"}
    case "flaky":
      raw, _ := flakyState.LoadOrStore(job.ID, 0)
      failures := raw.(int)
      if failures == 0 {
        flakyState.Store(job.ID, 1)
        resultCh <- struct{ outcome, detail string }{"failed", "transient error on first attempt"}
      } else {
        resultCh <- struct{ outcome, detail string }{"succeeded", "succeeded after retry"}
      }
    case "timeout":
      resultCh <- struct{ outcome, detail string }{"succeeded", "would succeed if timeout allowed"}
    case "fatal":
      resultCh <- struct{ outcome, detail string }{"failed", "non-retryable upstream rejection"}
    default:
      resultCh <- struct{ outcome, detail string }{"failed", "unknown kind"}
    }
  }()

  select {
  case <-ctx.Done():
    return "timed_out", fmt.Sprintf("exceeded %dms timeout", timeoutMs)
  case result := <-resultCh:
    if job.Kind == "timeout" {
      return "timed_out", fmt.Sprintf("exceeded %dms timeout", timeoutMs)
    }
    return result.outcome, result.detail
  }
}
