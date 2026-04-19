# R5 binary-parser tradeoff summary

This note distills the current same-track evidence from `tracks/r5-binary-parser`, where C++ and Rust both run the same `frames.bin` input and produce the same summary contract.

## Shared evidence now available

Both implementations have been run on the same fixed low-level slice with:

- 8-byte little-endian fixed-width records
- explicit byte decoding for `u16 type`, `u16 flags`, and `u32 value`
- failure on truncated input
- failure on unsupported record type
- shared summary output

Current verified command set:

```bash
clang++ -std=c++20 -O2 -Wall -Wextra -pedantic tracks/r5-binary-parser/main.cpp -o /tmp/r5_cpp
/tmp/r5_cpp tracks/r5-binary-parser/frames.bin
cargo run --quiet --manifest-path tracks/r5-binary-parser/Cargo.toml -- tracks/r5-binary-parser/frames.bin
```

Current shared summary:

```json
{"total_records":5,"total_value":527,"flagged_records":2,"type_counts":{"type_1":2,"type_2":2,"type_3":1},"type_value_sums":{"type_1":420,"type_2":100,"type_3":7}}
```

## Practical decision summary

| If you mainly want... | First pick | Why |
| -- | -- | -- |
| a safer default for new low-level parsing work | Rust | It preserves explicit parsing while adding stronger memory-safety guarantees on the exact binary-slice we wanted to test |
| the most familiar low-level baseline in an existing native code setting | C++ | It stays fully explicit and controllable, and it is still the easier fallback when the surrounding codebase is already C++ |

## Language-specific tradeoffs

### Rust

Choose Rust first on this track when:

- you want low-level parsing with stronger safety guarantees
- the project can afford some implementation ceremony for better extension confidence
- the main question is how much control you can keep without dropping to unsafe-by-default patterns

Do not choose Rust first when:

- you must stay inside an existing C++ codebase right now
- the main constraint is ecosystem or team inertia, not parsing safety
- introducing Rust is a larger organizational cost than the parser itself justifies

### C++

Choose C++ first on this track when:

- the surrounding system is already native/C++ and integration friction matters most
- you want the most direct manual control with no new language adoption step
- the code is serving as a baseline or interop-friendly native implementation

Do not choose C++ first when:

- memory safety is a first-order requirement rather than a nice-to-have
- you want the safer default for extending the parser over time
- the project is greenfield enough that adopting Rust is realistic

## Current recommendation boundary

For R5 today, the safest evidence-backed wording is:

- **Rust is the first pick for new low-level parsing work on this track**
- **C++ remains the strongest fallback when existing native-code context dominates**

That is stronger than the earlier availability-driven baseline state because Rust and C++ now share the same binary-parser task and summary contract.

## What is still not settled

This summary does not claim that R5 is fully finished forever.

Open upgrades still include:

1. adding Zig on the same binary-parser slice
2. broadening beyond one fixed parser shape
3. checking whether the same preference holds on other low-level tasks besides this parser
