#!/usr/bin/env python3
"""Validate plugin folders for a pull request.

usage: validate.py <checker-binary> <plugin-dir>...

Checks: plugin.toml parses, id matches the folder name, the id is unique in
the repo, README.md exists, size limits, no binaries / unexpected files, and
BigWave Radio's own checker (`bwr-plugin-check`). Writes a Markdown summary
(including each plugin's permissions) to $GITHUB_STEP_SUMMARY and to
summary.md. Exit code 1 on any error.
"""
import os
import pathlib
import re
import subprocess
import sys
import tomllib

MAX_PLUGIN_BYTES = 512 * 1024
MAX_FILE_BYTES = 256 * 1024
MAX_IMAGE_BYTES = 300 * 1024
TEXT_EXT = {".toml", ".rhai", ".md", ".txt", ".json"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,39}$")

PERMS = {
    "audio": "read audio levels and beats",
    "now_playing": "see the station and song playing",
    "overlay": "draw over the app window",
    "fullscreen": "go fullscreen",
    "hotkeys": "use keyboard shortcuts",
    "panel": "show a panel on the Plugins page",
    "page": "add pages to the side bar",
    "storage": "save small amounts of data",
    "player_control": "control playback and volume",
}


def all_ids(root):
    ids = {}
    for t in sorted(root.glob("plugins/*/plugin.toml")):
        try:
            ids.setdefault(tomllib.load(open(t, "rb")).get("id"), []).append(t.parent.name)
        except Exception:
            pass
    return ids


def check(checker, d, ids):
    errors, warnings, info = [], [], {}
    name = d.name
    toml = d / "plugin.toml"
    if not d.is_dir():
        return [f"{d} is not a folder"], warnings, info
    if not toml.is_file():
        return ["missing plugin.toml"], warnings, info
    try:
        m = tomllib.load(open(toml, "rb"))
    except Exception as e:
        return [f"plugin.toml does not parse: {e}"], warnings, info
    info = m
    pid = m.get("id", "")
    if not ID_RE.match(pid or ""):
        errors.append(f"id {pid!r} must be 1-40 chars of a-z 0-9 - _")
    if pid != name:
        errors.append(f"folder name {name!r} must match the id {pid!r}")
    if len(ids.get(pid, [])) > 1:
        errors.append(f"id {pid!r} is used by several folders: {', '.join(ids[pid])}")
    for key in ("name", "version", "description"):
        if not str(m.get(key, "")).strip():
            errors.append(f"plugin.toml needs a non-empty `{key}`")
    if not str(m.get("author", "")).strip():
        warnings.append("no `author` in plugin.toml")
    for p in m.get("permissions", []):
        if p not in PERMS:
            errors.append(f"unknown permission {p!r}")
    if not (d / "README.md").is_file():
        errors.append("missing README.md")
    if not (d / "main.rhai").is_file() and m.get("entry", "main.rhai") == "main.rhai":
        errors.append("missing main.rhai")
    total = 0
    for f in sorted(d.rglob("*")):
        if f.is_dir():
            continue
        rel = f.relative_to(d)
        size = f.stat().st_size
        total += size
        ext = f.suffix.lower()
        if f.is_symlink():
            errors.append(f"{rel}: symlinks are not allowed")
        elif ext in IMAGE_EXT:
            if size > MAX_IMAGE_BYTES:
                errors.append(f"{rel}: image is {size // 1024} KB (max {MAX_IMAGE_BYTES // 1024} KB)")
            if rel.name not in ("preview.png", "preview.jpg", "preview.gif") and len(rel.parts) == 1:
                warnings.append(f"{rel}: images other than preview.png are not shown in the catalog")
        elif ext in TEXT_EXT:
            data = f.read_bytes()
            if b"\0" in data:
                errors.append(f"{rel}: looks binary (contains NUL bytes)")
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                errors.append(f"{rel}: is not UTF-8 text")
            if size > MAX_FILE_BYTES:
                errors.append(f"{rel}: {size // 1024} KB (max {MAX_FILE_BYTES // 1024} KB per file)")
        else:
            errors.append(f"{rel}: file type not allowed (no binaries; allowed: {', '.join(sorted(TEXT_EXT | IMAGE_EXT))})")
    if total > MAX_PLUGIN_BYTES:
        errors.append(f"plugin is {total // 1024} KB in total (max {MAX_PLUGIN_BYTES // 1024} KB)")
    if checker:
        r = subprocess.run([checker, str(d)], capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip()
        info["_checker"] = out
        if r.returncode != 0:
            errors.append("bwr-plugin-check failed:\n" + out)
        for line in out.splitlines():
            if line.startswith("warning:"):
                warnings.append(line[len("warning: "):])
    return errors, warnings, info


def main():
    checker = sys.argv[1]
    dirs = [pathlib.Path(x) for x in sys.argv[2:]]
    root = pathlib.Path(".")
    ids = all_ids(root)
    lines = ["# Plugin check", ""]
    failed = False
    if not dirs:
        lines.append("No plugin folders changed.")
    for d in dirs:
        if not d.exists():
            lines += [f"## `{d.name}`", "", "Removed.", ""]
            continue
        errors, warnings, m = check(checker, d, ids)
        failed |= bool(errors)
        icon = "❌" if errors else "✅"
        lines += [f"## {icon} {m.get('name', d.name)} (`{d.name}`) {m.get('version', '')}", ""]
        if m:
            flashing = m.get("flashing", True)
            lines += [
                f"*{m.get('description', '')}*", "",
                f"Author: {m.get('author', '?')} · flashing: {'**yes**' if flashing else 'no'}", "",
                "**Permissions requested:**", "",
            ]
            perms = m.get("permissions", [])
            lines += [f"- `{p}`: {PERMS.get(p, 'unknown')}" for p in perms] or ["- none"]
            lines.append("")
        lines += [f"- ❌ {e}" for e in errors] + [f"- ⚠️ {w}" for w in warnings]
        if not errors:
            lines.append("- ✅ passed all checks")
        lines.append("")
    text = "\n".join(lines) + "\n"
    print(text)
    pathlib.Path("summary.md").write_text(text)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(text)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
