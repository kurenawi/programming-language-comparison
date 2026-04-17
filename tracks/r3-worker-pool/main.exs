Mix.install([{:jason, "~> 1.4"}])

if length(System.argv()) < 1 do
  IO.puts(:stderr, "usage: elixir main.exs <jobs.json> [worker_count] [timeout_ms]")
  System.halt(1)
end

[jobs_path | rest] = System.argv()
worker_count = Enum.at(rest, 0, "4") |> String.to_integer()
timeout_ms = Enum.at(rest, 1, "250") |> String.to_integer()

jobs =
  jobs_path
  |> File.read!()
  |> Jason.decode!()
  |> Enum.map(fn job ->
    %{
      id: job["id"],
      kind: job["kind"],
      duration_ms: job["duration_ms"],
      max_retries: job["max_retries"]
    }
  end)

execute_job = fn job ->
  attempt_range = 1..(job.max_retries + 1)

  Enum.reduce_while(attempt_range, {%{job_id: job.id, final_status: "failed", attempts: 0, timed_out: false, retried: false}, [], 0}, fn attempt, {_, logs, total_attempts} ->
    Process.sleep(job.duration_ms)

    {outcome, detail} =
      case job.kind do
        "fast" -> {"succeeded", "completed normally"}
        "slow" -> {"succeeded", "completed normally"}
        "flaky" when attempt == 1 -> {"failed", "transient error on first attempt"}
        "flaky" -> {"succeeded", "succeeded after retry"}
        "timeout" -> {"timed_out", "exceeded #{timeout_ms}ms timeout"}
        "fatal" -> {"failed", "non-retryable upstream rejection"}
        _ -> {"failed", "unknown kind"}
      end

    timed_out = outcome == "timed_out"
    retried = attempt > 1

    log = %{job_id: job.id, attempt: attempt, outcome: outcome, detail: detail}
    result = %{
      job_id: job.id,
      final_status: if(outcome == "succeeded", do: "succeeded", else: "failed"),
      attempts: attempt,
      timed_out: timed_out,
      retried: retried
    }

    cond do
      outcome == "succeeded" -> {:halt, {result, logs ++ [log], total_attempts + 1}}
      attempt <= job.max_retries -> {:cont, {Map.put(result, :retried, true), logs ++ [log], total_attempts + 1}}
      true -> {:halt, {result, logs ++ [log], total_attempts + 1}}
    end
  end)
end

{results, logs, total_attempts} =
  jobs
  |> Task.async_stream(execute_job, ordered: false, max_concurrency: worker_count, timeout: :infinity)
  |> Enum.reduce({[], [], 0}, fn
    {:ok, {result, job_logs, attempts}}, {results, logs, total_attempts} ->
      {[result | results], job_logs ++ logs, total_attempts + attempts}
  end)

results = Enum.sort_by(results, & &1.job_id)
logs = Enum.sort_by(logs, &{&1.job_id, &1.attempt})

summary = %{
  total_jobs: length(jobs),
  succeeded: Enum.count(results, &(&1.final_status == "succeeded")),
  failed: Enum.count(results, &(&1.final_status == "failed")),
  timed_out: Enum.count(results, & &1.timed_out),
  retried_jobs: Enum.count(results, & &1.retried),
  total_attempts: total_attempts,
  worker_count: worker_count,
  timeout_ms: timeout_ms,
  results: results,
  logs: logs
}

IO.puts(Jason.encode_to_iodata!(summary, pretty: true))
