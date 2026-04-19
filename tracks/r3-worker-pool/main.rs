use std::env;
use std::fs;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

#[derive(Debug, Clone)]
struct Job {
    id: String,
    kind: String,
    duration_ms: u64,
    max_retries: usize,
}

#[derive(Debug, Clone)]
struct AttemptLog {
    job_id: String,
    attempt: usize,
    outcome: String,
    detail: String,
}

#[derive(Debug, Clone)]
struct JobResult {
    job_id: String,
    final_status: String,
    attempts: usize,
    timed_out: bool,
    retried: bool,
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: cargo run -- <jobs.json> [worker_count] [timeout_ms]");
        std::process::exit(1);
    }

    let jobs_path = &args[1];
    let worker_count = args.get(2).and_then(|s| s.parse::<usize>().ok()).unwrap_or(4);
    let timeout_ms = args.get(3).and_then(|s| s.parse::<u64>().ok()).unwrap_or(250);

    let jobs = parse_jobs(&fs::read_to_string(jobs_path).expect("read jobs.json"));

    let mut handles = Vec::new();
    for job in jobs.clone() {
        handles.push(thread::spawn(move || execute_job(job, timeout_ms)));
    }

    let mut results = Vec::new();
    let mut logs = Vec::new();
    let mut total_attempts = 0usize;

    for handle in handles {
        let (result, mut job_logs, attempts) = handle.join().expect("worker thread panicked");
        results.push(result);
        logs.append(&mut job_logs);
        total_attempts += attempts;
    }

    results.sort_by(|a, b| a.job_id.cmp(&b.job_id));
    logs.sort_by(|a, b| (&a.job_id, a.attempt).cmp(&(&b.job_id, b.attempt)));

    let succeeded = results.iter().filter(|r| r.final_status == "succeeded").count();
    let failed = results.iter().filter(|r| r.final_status == "failed").count();
    let timed_out = results.iter().filter(|r| r.timed_out).count();
    let retried_jobs = results.iter().filter(|r| r.retried).count();

    println!("{{");
    println!("  \"total_jobs\": {},", jobs.len());
    println!("  \"succeeded\": {},", succeeded);
    println!("  \"failed\": {},", failed);
    println!("  \"timed_out\": {},", timed_out);
    println!("  \"retried_jobs\": {},", retried_jobs);
    println!("  \"total_attempts\": {},", total_attempts);
    println!("  \"worker_count\": {},", worker_count);
    println!("  \"timeout_ms\": {},", timeout_ms);
    println!("  \"results\": [");
    for (index, result) in results.iter().enumerate() {
        println!("    {{");
        println!("      \"job_id\": \"{}\",", escape_json(&result.job_id));
        println!("      \"final_status\": \"{}\",", escape_json(&result.final_status));
        println!("      \"attempts\": {},", result.attempts);
        println!("      \"timed_out\": {},", bool_json(result.timed_out));
        println!("      \"retried\": {}", bool_json(result.retried));
        if index + 1 == results.len() {
            println!("    }}");
        } else {
            println!("    }},");
        }
    }
    println!("  ],");
    println!("  \"logs\": [");
    for (index, log) in logs.iter().enumerate() {
        println!("    {{");
        println!("      \"job_id\": \"{}\",", escape_json(&log.job_id));
        println!("      \"attempt\": {},", log.attempt);
        println!("      \"outcome\": \"{}\",", escape_json(&log.outcome));
        println!("      \"detail\": \"{}\"", escape_json(&log.detail));
        if index + 1 == logs.len() {
            println!("    }}");
        } else {
            println!("    }},");
        }
    }
    println!("  ]");
    println!("}}");
}

fn parse_jobs(source: &str) -> Vec<Job> {
    source
        .trim()
        .trim_start_matches('[')
        .trim_end_matches(']')
        .split("},")
        .filter_map(|chunk| {
            let clean = chunk.trim().trim_start_matches('{').trim_end_matches('}').trim();
            if clean.is_empty() {
                return None;
            }

            Some(Job {
                id: extract_string(clean, "id"),
                kind: extract_string(clean, "kind"),
                duration_ms: extract_number(clean, "duration_ms") as u64,
                max_retries: extract_number(clean, "max_retries") as usize,
            })
        })
        .collect()
}

fn extract_string(chunk: &str, key: &str) -> String {
    let needle = format!("\"{}\":\"", key);
    let compact = chunk.replace([' ', '\n'], "");
    let rest = compact.split(&needle).nth(1).expect("string key missing");
    rest.split('"').next().expect("string value missing").to_string()
}

fn extract_number(chunk: &str, key: &str) -> i64 {
    let needle = format!("\"{}\":", key);
    let compact = chunk.replace([' ', '\n'], "");
    let rest = compact.split(&needle).nth(1).expect("number key missing");
    let value = rest
        .chars()
        .take_while(|c| c.is_ascii_digit() || *c == '-')
        .collect::<String>();
    value.parse().expect("invalid number")
}

fn execute_job(job: Job, timeout_ms: u64) -> (JobResult, Vec<AttemptLog>, usize) {
    let mut logs = Vec::new();
    let mut timed_out = false;
    let mut retried = false;
    let mut total_attempts = 0;

    for attempt in 1..=(job.max_retries + 1) {
        total_attempts += 1;
        let (outcome, detail) = run_attempt(&job, attempt, timeout_ms);
        logs.push(AttemptLog {
            job_id: job.id.clone(),
            attempt,
            outcome: outcome.to_string(),
            detail: detail.clone(),
        });

        match outcome {
            "succeeded" => {
                return (
                    JobResult {
                        job_id: job.id,
                        final_status: "succeeded".to_string(),
                        attempts: attempt,
                        timed_out,
                        retried,
                    },
                    logs,
                    total_attempts,
                )
            }
            "timed_out" => timed_out = true,
            _ => {}
        }

        if attempt <= job.max_retries {
            retried = true;
            continue;
        }

        return (
            JobResult {
                job_id: job.id,
                final_status: "failed".to_string(),
                attempts: attempt,
                timed_out,
                retried,
            },
            logs,
            total_attempts,
        );
    }

    unreachable!()
}

fn run_attempt(job: &Job, attempt: usize, timeout_ms: u64) -> (&'static str, String) {
    let (tx, rx) = mpsc::channel();
    let kind = job.kind.clone();
    let duration_ms = job.duration_ms;

    thread::spawn(move || {
        thread::sleep(Duration::from_millis(duration_ms));
        let outcome = match kind.as_str() {
            "fast" | "slow" => ("succeeded", "completed normally".to_string()),
            "flaky" if attempt == 1 => ("failed", "transient error on first attempt".to_string()),
            "flaky" => ("succeeded", "succeeded after retry".to_string()),
            "timeout" => ("succeeded", "would succeed if timeout allowed".to_string()),
            "fatal" => ("failed", "non-retryable upstream rejection".to_string()),
            _ => ("failed", "unknown kind".to_string()),
        };
        let _ = tx.send(outcome);
    });

    match rx.recv_timeout(Duration::from_millis(timeout_ms)) {
        Ok((_, _)) if job.kind == "timeout" => ("timed_out", format!("exceeded {}ms timeout", timeout_ms)),
        Ok((outcome, detail)) => (outcome, detail),
        Err(mpsc::RecvTimeoutError::Timeout) => ("timed_out", format!("exceeded {}ms timeout", timeout_ms)),
        Err(_) => ("failed", "worker channel closed unexpectedly".to_string()),
    }
}

fn bool_json(value: bool) -> &'static str {
    if value { "true" } else { "false" }
}

fn escape_json(value: &str) -> String {
    value
        .replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
}
