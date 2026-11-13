# Cooldown settings by package manager

| Tool | File | Setting | Unit | Seven days |
|---|---|---|---|---|
| npm 11.10+ | `.npmrc` | `min-release-age=7` | days | `7` |
| pnpm | `pnpm-workspace.yaml` | `minimumReleaseAge: 10080` | minutes | `10080` |
| Bun | `bunfig.toml` | `[install]` `minimumReleaseAge = 604800` | seconds | `604800` |
| uv | `pyproject.toml` `[tool.uv]` or `uv.toml` | `exclude-newer = "7 days"` | duration or date | `"7 days"` or `"P7D"` |

Notes from the official docs:
- npm: only versions published more than the given number of days ago are installed; if none fits, the command
  errors. It complements `before`, which takes an exact date.
- pnpm: current pnpm defaults `minimumReleaseAge` to 1440 (one day). Set it explicitly so the project doesn't depend
  on the pnpm version. `minimumReleaseAgeExclude` exempts named packages.
- Bun: disabled by default. `minimumReleaseAgeExcludes` exempts packages or exact versions.
- uv: `exclude-newer` compares against each file's upload time. A duration like `"7 days"` rolls forward; an RFC 3339
  date freezes resolution at that moment. `exclude-newer-package` sets it per package.
- pip has no rolling setting. Use uv, or pin with hashes from a lockfile.
