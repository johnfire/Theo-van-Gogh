# CLAUDE.md — AI Coding Guide for Theo-van-Gogh

Art management automation system for working artists. See docs/ARCHITECTURE.md for full structure and data schemas.

## Quick Orientation

- **Entry point:** `main.py` (Click CLI commands)
- **All paths:** `config/settings.py` — never hardcode paths elsewhere
- **Metadata schema:** `src/metadata_manager.py` — source of truth for JSON structure
- **Tests:** `tests/` — run with `source venv/bin/activate && pytest`
- **Docs:** docs/ARCHITECTURE.md (structure), docs/INSTALL.md, docs/FASO_SETUP.md, docs/TESTING.md

## Running Things

Always activate the virtualenv first:
```bash
source venv/bin/activate
pytest                          # full suite
pytest tests/test_foo.py -v     # single file
python main.py --help           # CLI commands
```

## Key Conventions

- **Platform stubs** in `src/social/` raise `NotImplementedError` — don't implement them until the dev account is ready
- **URL checks** use `urlparse().hostname ==` (not `in` substring) — CodeQL enforces this
- **Gallery sites** track `last_uploaded` (one-time). **Social media** tracks `last_posted` + `post_count` (can repeat)
- **No external HTTP deps** — Mastodon uses stdlib `urllib.request` only; keep it that way
- **Lazy platform loading** — import platform classes on demand, not at module level

## Adding a New Social Platform

1. Create `src/social/newplatform.py` implementing `SocialPlatform` ABC
2. Register it in `src/social/__init__.py`
3. Add to `SOCIAL_MEDIA_PLATFORMS` list in `src/social/base.py`
4. Add credentials to `config/settings.py` + `env.example`

The CLI, scheduler, and metadata tracking all work automatically after step 4.

## FASO Browser Automation

- Uses persistent Chromium profile at `~/.config/theo-van-gogh/cookies/faso_browser_profile`
- Login: `data.fineartstudioonline.com/login/`
- Always sets Availability to "Available"
- Uses fuzzy dropdown matching for form fields

## GitHub Workflow

Issues are managed via `gh` CLI (auth via `GH_TOKEN` env var):
```bash
gh issue list --repo johnfire/theo-van-gogh
gh issue view <number> --repo johnfire/theo-van-gogh --json title,body,labels
gh issue close <number> --repo johnfire/theo-van-gogh --comment "Fixed in commit ..."
```

Label `claude code should fix` marks issues ready for AI implementation.

## Testing Notes

- Coverage threshold is 40% — running a single test file will fail the coverage check, that's expected
- Tests use `pytest-mock` for Playwright and API mocking
- Security tests: use `urlparse().hostname ==` not substring `in` for URL assertions (CodeQL rule)
