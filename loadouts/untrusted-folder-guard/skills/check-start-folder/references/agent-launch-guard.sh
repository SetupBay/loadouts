# agent-launch-guard.sh: add to ~/.zshrc or ~/.bashrc yourself (the agent must not edit your profile).
# Wraps the agent commands so they refuse to start in a folder the web can write to, and run start_check.py first.
# Set AGENT_START_CHECK to where you keep start_check.py.
AGENT_START_CHECK="${AGENT_START_CHECK:-$HOME/.agents/skills/check-start-folder/scripts/start_check.py}"

_agent_guard() {
  case "$PWD/" in
    "$HOME/Downloads/"*|"$HOME/Desktop/"*|/tmp/*|/private/tmp/*|/var/tmp/*)
      echo "agent-launch-guard: not starting $1 in $PWD (a folder other apps can write to). Move the project first." >&2
      return 1 ;;
  esac
  if [ "$PWD" = "$HOME" ]; then
    echo "agent-launch-guard: not starting $1 in your home folder. cd into a project first." >&2
    return 1
  fi
  if [ -f "$AGENT_START_CHECK" ] && ! python3 "$AGENT_START_CHECK" . >&2; then
    echo "agent-launch-guard: read the files above, then run 'command $1' to start anyway." >&2
    return 1
  fi
  command "$@"
}

claude()       { _agent_guard claude "$@"; }
codex()        { _agent_guard codex "$@"; }
gemini()       { _agent_guard gemini "$@"; }
agy()          { _agent_guard agy "$@"; }
cursor-agent() { _agent_guard cursor-agent "$@"; }
