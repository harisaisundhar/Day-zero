# FoodLog

A low-effort, background calorie + macro logger.

Snap a photo of your food on your phone (one tap via an iOS Shortcut). Once a
day your Mac estimates calories + macros from the photos and appends them to a
single log you can glance at. Approximation, not precision. No daily effort.

## How it works

**Local backend** — Mac + iCloud, triggered by `launchd`:
```
Phone shortcut → photo → iCloud Drive/FoodLog/inbox/  (syncs to the Mac)
9pm via launchd → python -m foodlog → estimate → archive to done/ →
                  rewrite iCloud summary.md  (glanceable on phone)
```
Simple and free; runs when the Mac is awake (catches up on next wake if asleep).

Core: estimate kcal+macros with the inline prompt, label the meal from the
photo's time, and keep a single `summary.md` log.

> Note: a cloud backend (Google Drive + GitHub Actions) was prototyped but
> dropped — iOS Shortcuts can't reliably upload a file to Drive (it can't send a
> raw body without a Content-Type it strips, build multipart, or read the
> resumable `Location` response header). The backend layer remains pluggable if
> revisited via a different store or an upload relay.

## Project layout

```
foodlog/
├── src/foodlog/            # the package
│   ├── config.py           # settings + paths (env-overridable)
│   ├── models.py           # Meal dataclass, meal-type windows
│   ├── images.py           # EXIF date, HEIC→JPEG, notes, file naming
│   ├── prompt.py           # the nutrition prompt
│   ├── summary.py          # render/parse summary.md (pure, no I/O)
│   ├── estimators/         # pluggable model backends (work on image bytes)
│   │   ├── __init__.py     #   factory + shared JSON normalization
│   │   ├── gemini.py
│   │   └── claude.py
│   ├── backends/           # pluggable storage backends
│   │   ├── __init__.py     #   factory + InboxItem + Backend interface
│   │   └── local.py        #   Mac/iCloud filesystem
│   ├── pipeline.py         # orchestration (backend- + estimator-agnostic)
│   └── cli.py              # entry point
├── tests/                  # pytest unit tests
├── scripts/
│   └── setup-on-this-mac.command   # installs the launchd schedule
├── done/                   # local photo archive (gitignored)
├── pyproject.toml
├── .env.example
└── README.md
```

Two clean axes of pluggability: **storage backend** (currently `local`) and
**estimator** (`gemini` / `claude`), each behind a small factory + interface, so
the orchestration in `pipeline.py` doesn't change when you swap either.

## Setup

```bash
git clone <your-repo> ~/foodlog
cd ~/foodlog
python3 -m pip install -e ".[dev]"     # optional: installs the `foodlog` command + pytest
```

Configure (env vars override `src/foodlog/config.py`):

```bash
export GEMINI_API_KEY="AIza..."        # personal AI Studio key
# export FOODLOG_ESTIMATOR=claude      # to use the local claude CLI instead
```

Run once to check wiring:

```bash
python -m foodlog --show-config
python -m foodlog            # processes whatever is in the inbox
```

Schedule the daily 9pm run on the Mac that should own it:

```bash
bash scripts/setup-on-this-mac.command
```

It writes a launchd job and prints the Python binary to add to **Full Disk
Access** (required so the background job can read iCloud Drive).

## Configuration

| Setting | Env var | Default |
|---|---|---|
| Estimator | `FOODLOG_ESTIMATOR` | `gemini` |
| Daily target | `FOODLOG_TARGET_KCAL` | `2400` |
| Gemini key | `GEMINI_API_KEY` | _(empty)_ |
| Gemini model | `FOODLOG_GEMINI_MODEL` | `gemini-2.0-flash` |
| iCloud folder | `FOODLOG_ICLOUD_DIR` | `~/.../CloudDocs/FoodLog` |
| claude binary | `FOODLOG_CLAUDE_BIN` | `~/.local/bin/claude` |

## ⚠️ API key + git

Never commit your key. Set `GEMINI_API_KEY` via env var (the recommended path)
— `config.py` reads it from the environment. Use a **personal** Google AI Studio
key, not a corporate GCP/Vertex credential. `.env` is gitignored; copy
`.env.example` to start.

## Tests

```bash
python -m pytest
```

## How `summary.md` stays the single source of truth

The file has a human-readable view on top and a hidden machine-readable JSON
block inside an HTML comment at the bottom. Each run reads that block, appends
the new meals, and rewrites the file — so there's no separate database/CSV, and
you can still edit the visible part freely (just leave the comment alone).
