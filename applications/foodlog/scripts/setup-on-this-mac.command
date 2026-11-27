#!/bin/bash
# ===========================================================================
# FoodLog — one-time setup on a Mac.
#
# Run this ONCE on the laptop that should run the 9pm automation.
# Safe to re-run (it just reinstalls the schedule).
#
# HOW TO RUN: double-click in Finder, OR in Terminal:
#     bash ~/foodlog/scripts/setup-on-this-mac.command
# ===========================================================================
set -e

# This installer lives in <repo>/scripts/ ; the repo root is one level up.
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$REPO_DIR/src"
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/FoodLog"
PLIST="$HOME/Library/LaunchAgents/com.user.foodlog.plist"
RUN_HOUR=21   # 9pm

echo "FoodLog setup — configuring the 9pm automation on this Mac"
echo "----------------------------------------------------------"

# 1) Package present?
if [ ! -f "$SRC_DIR/foodlog/cli.py" ]; then
  echo "ERROR: $SRC_DIR/foodlog not found. Run this from inside the foodlog repo."
  exit 1
fi
echo "[ok] package: $SRC_DIR/foodlog"

# 2) iCloud inbox present (create if missing)
mkdir -p "$ICLOUD_DIR/inbox"
echo "[ok] iCloud inbox: $ICLOUD_DIR/inbox"

# 3) Find python3 on THIS Mac (paths differ per machine)
PYBIN="$(command -v python3 || true)"
if [ -z "$PYBIN" ]; then
  echo "ERROR: python3 not found. Install it (python.org) and re-run."
  exit 1
fi
PYREAL="$($PYBIN -c 'import sys,os; print(os.path.realpath(sys.executable))')"
echo "[ok] python3: $PYREAL"

# 4) Estimator + key sanity check (config lives in src/foodlog/config.py)
EST="$(FOODLOG_ICLOUD_DIR="$ICLOUD_DIR" PYTHONPATH="$SRC_DIR" "$PYBIN" - <<'PY'
import foodlog.config as c
print(c.ESTIMATOR, "key" if c.GEMINI_API_KEY else "nokey")
PY
)"
echo "[info] estimator/key: $EST"
case "$EST" in
  gemini\ nokey)
    echo "WARNING: ESTIMATOR=gemini but no key. export GEMINI_API_KEY before the"
    echo "         9pm run (e.g. add it to this plist or your shell profile)." ;;
  claude\ *)
    command -v claude >/dev/null || echo "WARNING: 'claude' CLI not on PATH." ;;
esac
EXTRA_PATH="$HOME/.local/bin:/usr/local/bin"

# 5) Write the launchd job (runs `python -m foodlog` with src/ on PYTHONPATH)
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PLISTEOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.user.foodlog</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYREAL</string>
        <string>-m</string>
        <string>foodlog</string>
    </array>
    <key>WorkingDirectory</key><string>$REPO_DIR</string>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>$RUN_HOUR</integer><key>Minute</key><integer>0</integer></dict>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key><string>$SRC_DIR</string>
        <key>PATH</key><string>$EXTRA_PATH:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    <key>StandardOutPath</key><string>/tmp/foodlog.out.log</string>
    <key>StandardErrorPath</key><string>/tmp/foodlog.err.log</string>
    <key>RunAtLoad</key><false/>
</dict>
</plist>
PLISTEOF
echo "[ok] wrote launchd job -> $PLIST"

# 6) Load it
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "[ok] scheduled: daily at ${RUN_HOUR}:00 (catch-up on wake)"

echo
echo "ALMOST DONE — manual steps:"
echo "  1) Grant Full Disk Access to python so the job can read iCloud Drive:"
echo "     System Settings -> Privacy & Security -> Full Disk Access -> '+'"
echo "     Add:  $PYREAL    (toggle ON)"
echo "  2) If using Gemini, make sure GEMINI_API_KEY is available to the job."
echo
echo "Test now (optional):  launchctl start com.user.foodlog ; cat /tmp/foodlog.out.log"
echo "Setup complete."
