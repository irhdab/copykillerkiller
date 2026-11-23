#!/bin/sh
# Install the copykillerkiller skill into an agent skills directory.
set -eu

usage() {
  cat <<'EOF'
usage: ./install.sh [--agent codex|claude|hermes|cursor|project|auto] [--dir PATH] [--force] [--list]

  --agent   target agent (default: auto, which picks the first one found)
  --dir     explicit skill parent directory, overrides --agent
  --force   replace an existing installation, moving the old folder to a timestamped backup
  --list    print the resolved target directories and exit
EOF
}

AGENT=auto
DIR=""
FORCE=0
LIST=0

while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2 ;;
    --dir) DIR="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --list) LIST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC="$SCRIPT_DIR/copykillerkiller"

if [ ! -f "$SRC/SKILL.md" ]; then
  printf 'skill folder not found next to install.sh: %s\n' "$SRC" >&2
  exit 1
fi

codex_dir="${CODEX_HOME:-$HOME/.codex}/skills"
claude_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills"
hermes_dir="${HERMES_HOME:-$HOME/.hermes}/skills"
cursor_dir="./.cursor/skills"
project_dir="./.agents/skills"

if [ "$LIST" -eq 1 ]; then
  printf 'codex    %s\n' "$codex_dir"
  printf 'claude   %s\n' "$claude_dir"
  printf 'hermes   %s\n' "$hermes_dir"
  printf 'cursor   %s\n' "$cursor_dir"
  printf 'project  %s\n' "$project_dir"
  exit 0
fi

if [ -z "$DIR" ]; then
  case "$AGENT" in
    auto)
      if [ -d "${CODEX_HOME:-$HOME/.codex}" ]; then AGENT=codex
      elif [ -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}" ]; then AGENT=claude
      elif [ -d "${HERMES_HOME:-$HOME/.hermes}" ]; then AGENT=hermes
      else AGENT=project
      fi
      ;;
  esac
  case "$AGENT" in
    codex) DIR="$codex_dir" ;;
    claude) DIR="$claude_dir" ;;
    hermes) DIR="$hermes_dir" ;;
    cursor) DIR="$cursor_dir" ;;
    project) DIR="$project_dir" ;;
    *) printf 'unknown agent: %s\n' "$AGENT" >&2; usage >&2; exit 2 ;;
  esac
fi

DEST="$DIR/copykillerkiller"

if [ -e "$DEST" ]; then
  if [ "$FORCE" -ne 1 ]; then
    printf 'already installed: %s\n' "$DEST" >&2
    printf 'rerun with --force to replace it, or use --dir to install elsewhere.\n' >&2
    exit 1
  fi
  BACKUP="$DEST.bak.$(date +%Y%m%d%H%M%S)"
  mv "$DEST" "$BACKUP"
  printf 'previous installation moved to %s\n' "$BACKUP"
fi

mkdir -p "$DIR"
cp -R "$SRC" "$DEST"

printf 'installed: %s\n' "$DEST"
printf '\n'

if command -v python3 >/dev/null 2>&1; then
  TIER=$(python3 "$DEST/scripts/capability.py" --tier-only 2>/dev/null || echo unknown)
else
  TIER=manual
fi
printf 'capability tier: %s\n' "$TIER"

case "$AGENT" in
  codex) printf 'invoke: $copykillerkiller\n' ;;
  claude|cursor|hermes) printf 'invoke: /copykillerkiller, or let the agent pick it up from the description\n' ;;
  project) printf 'invoke: mention the skill folder, or copykillerkiller\n' ;;
  *) printf 'invoke: point the agent at %s/SKILL.md\n' "$DEST" ;;
esac

if [ "$TIER" = "manual" ]; then
  printf 'python3 or a writable temp folder was not found; see references/capabilities.md manual path.\n'
elif [ "$TIER" = "reduced" ]; then
  printf 'pdftotext was not found; PDF text extraction falls back to agent-read text. See references/capabilities.md.\n'
fi
