# AGENTS.md: write like a person, not a press release

Applies to everything you write for this project: docs, READMEs, commit messages, PR descriptions, release notes,
changelogs, UI copy and replies to the user. Readers now recognise machine prose on sight and stop trusting it.

## Rules
- Say the thing. Lead with the fact, the number or the instruction. No warm-up sentence, no summary of what you are
  about to say, no closing recap.
- Plain words. "Use" not "leverage", "has" not "boasts", "important" only when you say why. The `plain-prose` skill has the full word list.
- No inflated significance: nothing is a "testament", a "tapestry", "pivotal", "game-changing" or "a journey".
- No "it's not just X, it's Y" and no "not only X but also Y". State what it is.
- No reflexive groups of three. Use the number of items there are.
- Punctuation: full stops and commas. At most one em dash per paragraph; prefer a colon, comma or new sentence.
- No emoji as bullets or headings. No bold on every other phrase. Sentence-case headings.
- No unverifiable proof: "trusted by thousands", "10,000+ users", "industry-leading". Give a source or cut it.
- No chat filler in files: "Great question", "I hope this helps", "Let's dive in", "Certainly!".
- Be specific. Replace "improves performance" with the measurement, "various issues" with the issues.
- Follow the project's spelling. This project uses UK English unless a file already uses another variant.

## Check before you finish
- Run the `plain-prose` skill's linter (`scripts/prose_lint.py` in the skill folder) on prose you wrote or changed. Fix every finding or explain why it stays. Use the `plain-prose` skill for rewrites.
- Code, identifiers and quoted text are exempt. Do not "fix" a word inside backticks or a quotation.
