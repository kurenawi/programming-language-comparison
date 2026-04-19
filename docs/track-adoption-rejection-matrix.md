# Track-by-track adoption and rejection matrix for LIL-246

This matrix is still **interim**. It only uses tracks that are already implemented and verified in this repository.

It is meant to answer a more practical question than raw language comparison notes:

> Given the current evidence, which language should be the first pick for this kind of work, which one is the fallback, and when should I avoid choosing it first?

## Track R1: fast one-person automation, ETL, throwaway CLI work

| Choice | Language | Why it currently earns this slot | Avoid first when |
| -- | -- | -- | -- |
| First pick | Python | Fastest iteration, shortest implementations, standard library is enough for JSONL/CSV/HTTP basics | Contract evolution, multi-person API maintenance, or stricter schema visibility matters more than speed |
| Strong fallback | Go | Still simple enough, better delivery story when the script starts turning into an operational tool | You mostly care about exploratory speed and compact data-wrangling code |
| Not first for this track | TypeScript | Shape control is strong, but local build/runtime preparation still makes the first loop heavier in this environment | The work is already API-contract-heavy, or it needs to stay close to Node/browser integrations |

## Track R2: team-owned API that keeps evolving

| Choice | Language | Why it currently earns this slot | Avoid first when |
| -- | -- | -- | -- |
| First pick | TypeScript | Best visibility into request/response contract changes, optional field expansion, and API-shape maintenance | You need single-binary delivery, zero Node/build dependency, or the runtime environment is tightly constrained |
| Strong fallback | Go | Explicit structs and optional handling make backward-compatibility changes readable and operationally stable | You want the strongest type-guided contract editing loop and fastest schema-surface discovery |
| Not first for this track | Python | Still fast to change, but contract and validation boundaries stay more human-dependent in the current slices | Speed of prototyping matters more than sustained contract safety |

## Track R3: worker pool, retry, timeout, partial failure

| Choice | Language | Why it currently earns this slot | Avoid first when |
| -- | -- | -- | -- |
| First pick for the current environment | Go | It now has the clearest same-track evidence across implementation and verification, keeps timeout/retry behavior explicit, and remains the easiest operational baseline to reason about | The main decision hinges on supervision trees or process-level failure isolation more than explicit worker logic |
| Strong comparison target with differentiated concurrency model | Elixir | It now runs on the same `jobs.json` and summary contract, so its failure-isolation and concurrency model can be judged on the same task rather than as theory | You need the most direct operationally-familiar control flow, or team/runtime familiarity with BEAM is low |
| Strong comparison target with safety/performance posture | Rust | It now runs on the same worker-pool track and gives a real comparison point for explicit safety and control on concurrent work | The extra implementation ceremony is not justified by the actual operational needs of the worker system |
| Not enough evidence yet | Python, TypeScript, C++, C, Zig, MoonBit | No same-track implementation here yet, so choosing them first would still be guesswork | The track is being used only as planning, not for an evidence-backed decision |

## Track R4: operational CLI or API delivery

| Choice | Language | Why it currently earns this slot | Avoid first when |
| -- | -- | -- | -- |
| First pick | Go | Standard library coverage plus simple shipping story make it the cleanest current operational default | The tool is mostly throwaway automation and delivery friction is irrelevant |
| Strong fallback | Python | Fastest way to get the tool working and learn the task shape before hardening delivery | You want fewer runtime dependencies or easier single-artifact distribution |
| Not first for this track | TypeScript | Good contracts, but Node/build/runtime dependence is still a real operational tradeoff here | The product already lives inside a Node ecosystem and that tradeoff is acceptable |

## Track R5: low-level byte parsing, buffer handling, memory-aware work

| Choice | Language | Why it currently earns this slot | Avoid first when |
| -- | -- | -- | -- |
| First pick for the current environment | Rust | Rust now runs on the same fixed binary-parser track as C++, matches the C++ output, and brings memory-safety guarantees to the exact low-level slice we wanted to test first | You explicitly need C++ interop first, or you need to stay inside an existing C++ codebase with no Rust adoption budget |
| Strong fallback | C++ | The original baseline is still explicit, controllable, and fully available in this environment | Memory safety and extension confidence matter more than ecosystem inertia or existing C++ familiarity |
| Planned strong comparison target | Zig | Zig is still one of the intended low-level comparison targets, but it remains blocked by missing toolchain | Toolchain is missing, so current selection would still be aspirational rather than verified |
| Not enough evidence yet | Go, Python, TypeScript, Elixir, MoonBit, C | They have not been implemented on this binary-parser track in this repo | The task is not actually low-level or buffer-centric |

## What this matrix is safe to use for right now

Use it for:

- choosing between Python, TypeScript, and Go for the currently implemented tracks
- deciding whether to start an operational baseline in Go
- deciding whether low-level comparison work should start with Rust or fall back to C++ in the current environment
- explaining why the next highest-value additions are Elixir on R3 and Zig on R5

Do not use it yet for:

- final claims about Elixir, Rust, Zig, MoonBit, C, or C++ across all tracks
- final language ranking
- any claim that R3 or R5 is settled before the planned languages land on the same tasks

## Immediate upgrade path for this matrix

1. Interpret and summarize the tradeoffs across Go, Elixir, and Rust on `tracks/r3-worker-pool`
2. Add Zig to `tracks/r5-binary-parser`
3. Add Rust or another later language to an R2 API-evolution slice
4. Replace the remaining speculative rows with evidence-backed rows from implemented tracks
