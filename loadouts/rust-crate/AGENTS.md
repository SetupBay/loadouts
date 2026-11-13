# AGENTS.md: Rust crate

Rust project built with Cargo. Read `Cargo.toml` for the edition and `rust-version` (MSRV) before using newer features.

## Commands
- Build: `cargo build`. Tests: `cargo test` (add `--all-features` if the crate has features).
- Format: `cargo fmt --all -- --check`. Lint: `cargo clippy --all-targets --all-features -- -D warnings`.
- Docs: `cargo doc --no-deps`. Dependency advisories, if installed: `cargo deny check` or `cargo audit`.
- Done means: fmt clean, clippy with no warnings, tests green. Do not silence a lint with `#[allow]` without a comment why.

## Errors
- Library code returns `Result<T, E>` with a typed error enum; no `unwrap()`, `expect()` or `panic!` on input-driven paths.
  `expect("reason")` is fine for true invariants, with the reason saying why it cannot fail.
- Binaries may use `anyhow` for context (`.context("reading config")`). Libraries should not expose `anyhow::Error`.
- Use `?` to propagate. Add context at boundaries, not at every call.

## Safety and dependencies
- `unsafe` only with the human's approval and a `// SAFETY:` comment explaining the invariant. Prefer `#![forbid(unsafe_code)]`.
- Add dependencies with `cargo add <crate>`; check it is maintained and widely used. Keep default features off when you
  only need a small part (`cargo add <crate> --no-default-features --features ...`).
- Never bump the MSRV, edition or a major dependency version as a side effect of another change.

## Style
- Borrow instead of clone; clone only where ownership is genuinely needed, and not to quiet the borrow checker.
  If you fight the borrow checker for more than two attempts, stop and explain the ownership problem.
- Prefer iterators and `match` over index loops and nested `if let`. Keep functions short; name types after the domain.
- Public items get doc comments with an example where it helps; doc tests run with `cargo test`.
- Use the `rust-change` skill for any non-trivial change.
