#!/usr/bin/env bash
# Prove a git checkout is exactly the pinned commit.
# Usage: check_pin.sh <repo-dir> <40-char-sha>
# Detaches at the commit object (not a branch or tag that happens to share the name), then checks HEAD.
set -euo pipefail
dir="${1:?repo dir}"; pin="${2:?pinned sha}"
if ! [[ "$pin" =~ ^[0-9a-f]{40}$ ]]; then echo "FAIL pin is not a full lowercase 40-character SHA: $pin"; exit 1; fi
cd "$dir"
# A ref named like a SHA is how Plugin4Shell swapped code under a pinned marketplace entry.
suspicious=$(git for-each-ref --format='%(refname)' refs/heads refs/tags refs/remotes | grep -E '/[0-9a-f]{40}$|/FETCH_HEAD$' || true)
if [ -n "$suspicious" ]; then echo "FAIL refs named like a commit: $suspicious"; exit 1; fi
if ! git cat-file -e "${pin}^{commit}" 2>/dev/null; then echo "FAIL commit $pin is not in this clone"; exit 1; fi
git -c advice.detachedHead=false checkout -q --detach "${pin}^{commit}"
head=$(git rev-parse HEAD)
if [ "$head" != "$pin" ]; then echo "FAIL HEAD is $head, expected $pin"; exit 1; fi
if [ -n "$(git status --porcelain)" ]; then echo "FAIL working tree has changes not in the pinned commit"; exit 1; fi
echo "OK HEAD matches pin $pin"
