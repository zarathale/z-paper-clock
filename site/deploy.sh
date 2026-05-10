#!/usr/bin/env bash
#
# deploy.sh — push site/build/ to mypaperclock.cc
#
# Pattern: rsync over SSH using a host alias from ~/.ssh/config.
# No credentials live in this script. The SSH connection is configured
# entirely in ~/.ssh/config (see "Setup" below).
#
# Usage:
#   bash site/deploy.sh           # dry run (default) — shows what would change
#   bash site/deploy.sh --apply   # actually push the changes
#
# Setup (one-time, on the mac you deploy from):
#
#   1. Generate an SSH key for this server (if you don't already have one):
#        ssh-keygen -t ed25519 -f ~/.ssh/mypaperclock_ed25519
#
#   2. Copy the public key to the server. Easiest way:
#        ssh-copy-id -i ~/.ssh/mypaperclock_ed25519.pub root@50.28.105.83
#      (You'll type the root password once. After this, key auth works
#      and you should disable SSH password auth on the server — see the
#      coaching notes that came with this script.)
#
#   3. Add a host alias to ~/.ssh/config (create the file if it doesn't exist):
#        Host mypaperclock
#          HostName 50.28.105.83
#          User root
#          Port 22
#          IdentityFile ~/.ssh/mypaperclock_ed25519
#          IdentitiesOnly yes
#
#      After this, `ssh mypaperclock` connects with no IP, no user,
#      no password — and rsync uses the same alias.
#
#   4. Confirm DEPLOY_PATH below matches the actual document root the
#      web server is configured to serve mypaperclock.cc from. Default
#      assumes /var/www/mypaperclock.cc/ — adjust if the server uses
#      a different convention.
#
# That's it. After setup, deploys are: bash site/deploy.sh --apply

set -euo pipefail

# ---- Configuration ----

SSH_HOST="mypaperclock"                  # alias defined in ~/.ssh/config
DEPLOY_PATH="/var/www/mypaperclock.cc/"  # confirmed 2026-05-09 by sibling-site convention
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOCAL_PATH="${SCRIPT_DIR}/build/"

# ---- Argument parsing ----

DRY_RUN=true
case "${1:-}" in
  --apply) DRY_RUN=false ;;
  --help|-h)
    sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  "") ;;  # default — dry run
  *)
    echo "Unknown argument: ${1}" >&2
    echo "Usage: bash site/deploy.sh [--apply | --help]" >&2
    exit 1
    ;;
esac

# ---- Sanity checks ----

if [[ ! -d "$LOCAL_PATH" ]]; then
  echo "Error: local path does not exist: $LOCAL_PATH" >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "Error: rsync not found on PATH. Install with: brew install rsync" >&2
  exit 1
fi

# ---- Build rsync options ----

RSYNC_OPTS=(
  --archive
  --verbose
  --compress
  --human-readable
  --delete
  --exclude=".DS_Store"
  --exclude="README.md"
)

if $DRY_RUN; then
  echo "DRY RUN — showing what would change."
  echo "Re-run with --apply to actually deploy."
  echo ""
  RSYNC_OPTS+=(--dry-run)
else
  echo "Deploying ${LOCAL_PATH} -> ${SSH_HOST}:${DEPLOY_PATH}"
  echo ""
fi

# ---- The deploy ----

rsync "${RSYNC_OPTS[@]}" "$LOCAL_PATH" "${SSH_HOST}:${DEPLOY_PATH}"

# ---- Post ----

echo ""
if $DRY_RUN; then
  echo "(dry run complete — re-run with --apply to push for real)"
else
  echo "Deploy complete. Verify at https://mypaperclock.cc/"
fi
