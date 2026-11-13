---
name: rust-change
description: Make a reviewable Rust change with typed errors, a failing test first for bugs, and fmt, clippy -D warnings and tests before reporting. Use for any non-trivial change to a Rust crate.
---

# Rust change

1. Read the module and its tests. Run `cargo test` once first so you know the baseline.
2. For a bug: write a failing test that reproduces it before touching the code.
3. Model errors as an enum like `references/errors.rs`: one variant per failure the caller can act on, `Display` written
   for humans, `source()` returning the underlying error. `thiserror` is fine if the crate already uses it.
4. Make the change. Keep public API changes out unless asked; if unavoidable, list them in your report.
5. Run, in order: `cargo fmt --all`, `cargo clippy --all-targets --all-features -- -D warnings`, `cargo test`.
   Fix every clippy warning you introduced. Do not add `#[allow(...)]` to pass.
6. Report: what changed, tests added, and the three command results.
