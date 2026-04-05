# Debugging Log: ambient-weather-mcp

Tracks every error encountered, root cause, and resolution.

\---

## Issue #1: FastMCP constructor parameter

**Date:** 2026-03-20
**Error:** `TypeError: FastMCP.\_\_init\_\_() got an unexpected keyword argument 'description'`
**Root cause:** FastMCP (mcp >= 1.2.0) uses `instructions` not `description` as the constructor parameter.
**Fix:** Changed `description=` to `instructions=` in server.py.

## Issue #2: Claude Desktop "No module named src"

**Date:** 2026-03-20
**Error:** `C:\\Python313\\python.exe: No module named src`
**Root cause:** Claude Desktop on Windows does not reliably apply the `cwd` config field. Python starts in the wrong directory and can't find the `src` package.
**Fix:** Created `run\_mcp.bat` wrapper that `cd /d` into the project dir before running Python. Config uses `"command": "cmd.exe", "args": \["/c", "path\\\\to\\\\run\_mcp.bat"]`.

## Issue #3: WSL Docker credential helper broken

**Date:** 2026-03-20
**Error:** `fork/exec /usr/bin/docker-credential-desktop.exe: exec format error`
**Root cause:** Symlink `/usr/bin/docker-credential-desktop.exe -> /Docker/host/bin/docker-credential-desktop.exe` points to a Windows exe that WSL can't execute.
**Fix:** `sudo rm /usr/bin/docker-credential-desktop.exe`

## Issue #4: WSL pip blocked by externally-managed-environment

**Date:** 2026-03-20
**Error:** `error: externally-managed-environment` when running `pip install` inside activated venv.
**Root cause:** Ubuntu 24 venv created with system Python inherits the PEP 668 restriction.
**Fix:** Recreate venv with `python3 -m venv venv --without-pip`, then bootstrap pip with `curl -sS https://bootstrap.pypa.io/get-pip.py | python3`.

## Issue #5: Exposed API keys in source code

**Date:** 2026-03-22
**Error:** Wilson's API keys hardcoded in ambient\_client.py docstring, pushed to public GitHub repo.
**Root cause:** Keys were pasted into the usage example docstring instead of placeholder text.
**Fix:** Replaced with `"your-api-key-here"` placeholder. Wilson needs to regenerate both keys.

## Issue #6: GitHub Actions Node.js 20 deprecation

**Date:** 2026-04-03
**Error:** Warning in GitHub Actions: "Node.js 20 actions are deprecated" for actions/checkout@v4, docker/build-push-action@v5, docker/login-action@v3, docker/metadata-action@v5.
**Root cause:** These action versions use Node.js 20 runtime which GitHub is phasing out by Sept 2026.
**Fix:** Warnings are cosmetic — Node.js 20 deprecation does not prevent the actions from running. Image was confirmed at ghcr.io with both latest and SHA tags. Will bump action versions when v6 releases are available.

