#!/usr/bin/env bash
# PreToolUse hook for the Bash tool (Claude Code). Codex hooks use the same JSON shape, and Cursor reads
# this deny reply when it loads the hook from .claude/settings.json.
# Reads the tool call as JSON on stdin. Prints a "deny" decision with a reason, or nothing to defer
# to the normal permission flow. Needs jq. Register it with onFailure "block" so a crash fails closed.
set -u
input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')
[ -z "$cmd" ] && exit 0
project="${CLAUDE_PROJECT_DIR:-$(printf '%s' "$input" | jq -r '.cwd // empty')}"
project="${project%/}"
flat=$(printf '%s' "$cmd" | tr '\n\t' '  ')
lower=$(printf '%s' "$flat" | tr '[:upper:]' '[:lower:]')

deny() {
  jq -n --arg r "Blocked by guard-bash: $1" \
    '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "deny", permissionDecisionReason: $r}}'
  exit 0
}

# 1. Shared git history and skipped checks.
if [[ "$lower" =~ git[[:space:]].*push ]]; then
  if [[ "$lower" =~ --force([[:space:]]|$) || "$lower" =~ [[:space:]]-[a-z]*f([[:space:]]|$) || "$lower" =~ [[:space:]]\+[a-z0-9/_.-]+ ]]; then
    deny "force-push rewrites shared history. Push a new commit, or ask the human."
  fi
  if [[ "$lower" =~ --force-with-lease && "$lower" =~ (^|[[:space:]:/])(main|master)([[:space:]]|$) ]]; then
    deny "force-push to main/master. Ask the human."
  fi
fi
[[ "$lower" =~ git[[:space:]]+reset[[:space:]].*--hard ]] && deny "git reset --hard discards work. Use git stash or a new branch, or ask the human."
[[ "$lower" =~ git[[:space:]]+clean[[:space:]]+-[a-z]*f ]] && deny "git clean -f deletes untracked files. List them with git clean -n and ask the human."
[[ "$lower" =~ --no-verify ]] && deny "--no-verify skips the project's checks. Fix what the checks report."

# 2. Secrets. .env.example / .sample / .template are fine.
if [[ "$flat" =~ (^|[[:space:]/=\'\"])\.env(\.[A-Za-z0-9_-]+)?([[:space:]\'\";|]|$) ]]; then
  m="${BASH_REMATCH[0]}"
  [[ "$m" =~ \.env\.(example|sample|template) ]] || deny "commands may not touch .env files; they hold secrets. Use .env.example for names."
fi

# 3. Recursive deletes outside the project, of the project itself, or via ~, $HOME or ..
read -r -a words <<< "$flat"
in_rm=0; recursive=0; targets=()
for w in "${words[@]}"; do
  case "$w" in
    rm|*/rm) in_rm=1; recursive=0; continue ;;
    ';'|'&&'|'||'|'|') in_rm=0; continue ;;
  esac
  [ "$in_rm" = 1 ] || continue
  if [[ "$w" == -* ]]; then [[ "$w" =~ ^-[a-zA-Z]*[rR] || "$w" == "--recursive" ]] && recursive=1; continue; fi
  [ "$recursive" = 1 ] && targets+=("$w")
done
for t in "${targets[@]:-}"; do
  [ -z "$t" ] && continue
  t="${t%\"}"; t="${t#\"}"; t="${t%\'}"; t="${t#\'}"
  case "$t" in
    '~'*|'$HOME'*|'${HOME}'*) deny "recursive delete under the home directory ($t)." ;;
    *..*) deny "recursive delete with .. in the path ($t). Use a path inside the project." ;;
    .|./|'*'|./'*') deny "recursive delete of the whole project folder ($t)." ;;
    /*)
      if [ -z "$project" ] || [[ "$t" != "$project"/* ]]; then deny "recursive delete outside the project ($t)."; fi ;;
  esac
done

# 4. Destructive SQL from the shell.
if [[ "$lower" =~ (drop[[:space:]]+(table|database|schema)|truncate[[:space:]]+) ]]; then
  deny "DROP/TRUNCATE from the shell. Write a migration file and ask the human to run it."
fi
if [[ "$lower" =~ delete[[:space:]]+from[[:space:]] && ! "$lower" =~ [[:space:]]where[[:space:]] ]]; then
  deny "DELETE without WHERE. Add a WHERE clause or ask the human."
fi

# 5. Downloaded code piped straight into a shell.
if [[ "$lower" =~ (curl|wget)[^\|]*\|[[:space:]]*(sudo[[:space:]]+)?(ba|z|da)?sh([[:space:]]|$) ]]; then
  deny "piping a download into a shell. Download, read, then run it, or ask the human."
fi
exit 0
