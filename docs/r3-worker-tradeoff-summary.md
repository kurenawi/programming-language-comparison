# R3 worker-pool tradeoff summary

This note distills the current same-track evidence from `tracks/r3-worker-pool`, where Go, Elixir, and Rust all run the same `jobs.json` input and produce the same summary contract.

## Shared evidence now available

All three implementations have been run on the same worker slice with:

- worker pool execution
- per-job timeout
- retry behavior
- partial failure without whole-run collapse
- shared summary output

Current verified command set:

```bash
go run tracks/r3-worker-pool/main.go tracks/r3-worker-pool/jobs.json 4 250
elixir tracks/r3-worker-pool/main.exs tracks/r3-worker-pool/jobs.json 4 250
cargo run --quiet --manifest-path tracks/r3-worker-pool/Cargo.toml -- tracks/r3-worker-pool/jobs.json 4 250
```

Current shared summary:

```json
{"total_jobs":7,"succeeded":5,"failed":2,"timed_out":1,"retried_jobs":4,"total_attempts":12,"worker_count":4,"timeout_ms":250}
```

## Practical decision summary

| If you mainly want... | First pick | Why |
| -- | -- | -- |
| the clearest operational baseline and lowest ceremony | Go | The control flow stays explicit, timeout/retry logic is easy to inspect, and the implementation style is operationally familiar |
| stronger failure-isolation/concurrency-model comparison | Elixir | The same task now gives a real BEAM-side comparison instead of only theoretical claims about supervisors and isolation |
| stronger safety/control posture on concurrent worker logic | Rust | The same task now shows what explicit control plus memory-safety looks like on a real worker slice |

## Language-specific tradeoffs

### Go

Choose Go first on this track when:

- you want the most straightforward worker-pool baseline
- you need operational simplicity more than language-level process isolation
- the team benefits from explicit, familiar timeout/retry code

Do not choose Go first when:

- the main question is supervisor-style recovery behavior
- you specifically want to lean on BEAM-style isolation semantics
- you need stronger compile-time safety guarantees badly enough to pay more implementation ceremony

### Elixir

Choose Elixir first on this track when:

- the hardest part of the system is not raw worker code but failure containment and recovery structure
- you want the concurrency model itself to carry more of the operational story
- you are evaluating supervisor/process isolation as a core selection reason

Do not choose Elixir first when:

- the surrounding team and runtime are much more comfortable with direct imperative worker logic
- BEAM adoption cost is higher than the actual concurrency benefit for this system
- the worker system is simple enough that Go's explicitness is already sufficient

### Rust

Choose Rust first on this track when:

- you need tighter safety guarantees around concurrent worker implementation
- explicit control and performance posture matter enough to justify more ceremony
- the system is sensitive enough that stronger compile-time constraints are a real benefit

Do not choose Rust first when:

- the worker problem is operationally simple and does not justify the extra implementation overhead
- the team primarily needs fast iteration and familiar runtime behavior
- the concurrency comparison is really about isolation/recovery semantics, where Elixir is the more differentiated test

## Current recommendation boundary

For R3 today, the safest evidence-backed wording is:

- **Go is the first operational baseline**
- **Elixir is the strongest differentiated comparison for isolation/concurrency model**
- **Rust is the strongest differentiated comparison for safety/control posture**

That is stronger than the earlier interim state because all three now share the same worker track and summary contract.

## What is still not settled

This summary does not claim that R3 is fully finished forever.

Open upgrades still include:

1. broader stress/scale slices on the same track
2. more nuanced measurements beyond contract-equivalent correctness
3. possible additional later-language comparisons if they become relevant
