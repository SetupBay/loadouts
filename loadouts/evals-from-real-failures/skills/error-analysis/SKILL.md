---
name: error-analysis
description: Read real traces, note what went wrong in each, group notes into failure categories and count them. Use before writing any eval, after a model or prompt change, or when users report bad answers.
---

# Error analysis

Goal: a ranked list of real failure modes, each with example trace ids.

1. Export a sample of recent traces to `evals/traces/` (gitignored). Mix ordinary traffic with known complaints.
   30 to 50 traces is enough to start; stop adding when new traces stop producing new kinds of failure.
2. Create `evals/notes.csv` with the header `trace_id,pass,note,category`.
3. Read each trace end to end: input, retrieved context, tool calls, final output. For each one write:
   - `pass`: `1` if a domain expert would accept the output as is, else `0`.
   - `note`: the first thing that went wrong, in plain words ("ignored the date range", "called search twice").
   Leave `category` empty for now. Do not invent categories before reading.
4. Read all the notes together. Group them into 4 to 8 categories named after the failure, not the component
   ("wrong date range", not "retrieval"). Fill in `category` for every failing row.
5. Tally: `python3 scripts/tally.py evals/notes.csv` prints each category with its count, share of failures and example
   trace ids, and lists failing rows that still have no category.
6. Report the table to the human. Recommend: fix obvious bugs directly (a broken prompt line, a missing tool argument);
   write evals only for failures that will recur or are costly.

Rules:
- One note per trace, about the first failure. Downstream errors usually follow from it.
- Do not grade with a model at this stage. The point is for a person (or you, read carefully) to see the data.
- Re-run this after every model or prompt change; categories move.
