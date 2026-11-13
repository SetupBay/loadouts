# Setting up JupyterLab for an agent (the human does this)

Checked 29 October 2026 against jupyter-mcp-server 2.2.4, JupyterLab 4.6.4 and jupyter-collaboration 5.0.4.

1. Start JupyterLab on the loopback address with a random token. The upstream quick start uses `--ip 0.0.0.0` and
   `MY_TOKEN`, which exposes a code-running server to your network with a guessable password. Don't.
   ```bash
   export JUPYTER_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
   uv run --with jupyterlab==4.6.4 --with jupyter-collaboration==5.0.4 --with ipykernel==7.4.0 \
     jupyter lab --ip 127.0.0.1 --port 8888 --IdentityProvider.token "$JUPYTER_TOKEN" --no-browser
   ```
   jupyter-collaboration is required: the MCP server edits the notebook through the real-time collaboration API.
   To check it works, type in a cell and watch the tab's "×" turn into "●" a few seconds later without saving.
2. Start your agent from the same shell so `JUPYTER_TOKEN` is in its environment.
3. The MCP config in this loadout passes `${JUPYTER_TOKEN}`:
   - Claude Code expands `${VAR}` in its project MCP config.
   - Codex passes `env` values as written. Use `env_vars = ["JUPYTER_TOKEN"]` in the `[mcp_servers.jupyter]` table
     instead of an `env` entry so it forwards your shell's value.
   - Cursor, Gemini CLI, Antigravity CLI and VS Code: check your client's docs for variable expansion; if it doesn't
     expand, paste the token into your user-level config, never a committed file.
4. Pin the server (`jupyter-mcp-server==2.2.4`), not `@latest`. Version 2 needs the MCP Python SDK 2 (`mcp>=2,<3`);
   an environment that pins `mcp<2` must stay on jupyter-mcp-server 1.x.
5. When you're done, stop JupyterLab (Ctrl+C twice). The token dies with it.
