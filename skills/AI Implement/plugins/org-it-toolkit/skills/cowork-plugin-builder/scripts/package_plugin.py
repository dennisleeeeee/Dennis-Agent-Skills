#!/usr/bin/env python3
"""
Package a M365 Copilot Cowork plugin folder into a sideload-ready .zip.

Why this exists
---------------
Two things break a Cowork upload and both are handled here:

1. Backslash zip entries. Windows `Compress-Archive` writes `skills\\x\\SKILL.md`;
   Cowork rejects backslashes. Every entry written here uses forward slashes.
2. Unsupported file extensions. Cowork validates the extension of every file
   inside a skill folder and rejects the whole package if one is not allowed
   (`.ps1` is a known rejection). This script refuses to build in that case
   instead of shipping a zip that fails at upload time.

It also strips macOS junk (`.DS_Store`, `__MACOSX`, AppleDouble `._*`).

Usage
-----
    python3 package_plugin.py --plugin-dir <folder> [--version 1.0.0] [--name my-toolkit]

Version defaults to the `version` field in manifest.json.
Name defaults to the plugin folder's own name.
Output: <plugin-dir>/dist/<name>-<version>.zip
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import zipfile

# Extensions Cowork accepts inside a skill folder. Keep this list conservative -
# anything not listed here is rejected at upload, so fail loudly at build time.
ALLOWED_SKILL_EXTENSIONS = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".csv",
    ".py", ".js", ".ts", ".sh",
    ".png", ".jpg", ".jpeg", ".svg", ".gif",
    ".pdf", ".docx", ".xlsx", ".pptx",
}

JUNK_NAMES = {".DS_Store", "Thumbs.db"}


def is_junk(path: pathlib.Path) -> bool:
    if path.name in JUNK_NAMES or path.name.startswith("._"):
        return True
    return "__MACOSX" in path.parts


def collect_files(plugin_dir: pathlib.Path) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []

    for required in ("manifest.json", "color.png", "outline.png"):
        p = plugin_dir / required
        if not p.is_file():
            sys.exit(f"ERROR: missing required file at plugin root: {required}")
        files.append(p)

    skills_dir = plugin_dir / "skills"
    if not skills_dir.is_dir():
        sys.exit("ERROR: no skills/ folder found in the plugin directory")

    for p in sorted(skills_dir.rglob("*")):
        if p.is_file() and not is_junk(p):
            files.append(p)

    # Connector packages reference tool-description JSON via mcpToolDescription.file.
    tools_dir = plugin_dir / "tools"
    if tools_dir.is_dir():
        for p in sorted(tools_dir.rglob("*")):
            if p.is_file() and not is_junk(p):
                files.append(p)

    return files


def validate_extensions(files: list[pathlib.Path], plugin_dir: pathlib.Path) -> None:
    bad: list[str] = []
    for p in files:
        rel = p.relative_to(plugin_dir)
        if rel.parts[0] != "skills":
            continue
        if p.suffix.lower() not in ALLOWED_SKILL_EXTENSIONS:
            bad.append(str(rel).replace("\\", "/"))

    if bad:
        print("ERROR: unsupported file extensions inside skills/ - Cowork will")
        print("reject the whole package. Remove or convert these files:")
        for b in bad:
            print(f"  - {b}")
        sys.exit(1)


def build(plugin_dir: pathlib.Path, version: str, name: str) -> pathlib.Path:
    files = collect_files(plugin_dir)
    validate_extensions(files, plugin_dir)

    dist = plugin_dir / "dist"
    dist.mkdir(exist_ok=True)
    out = dist / f"{name}-{version}.zip"
    if out.exists():
        out.unlink()

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            # Root-level, forward-slash entry path - required by Cowork.
            arcname = p.relative_to(plugin_dir).as_posix()
            z.write(p, arcname)

    verify(out)
    return out


def verify(zip_path: pathlib.Path) -> None:
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()

    problems = []
    if any("\\" in n for n in names):
        problems.append("zip entries contain backslashes")
    if "manifest.json" not in names:
        problems.append("manifest.json is not at the package root")
    if any(n.startswith("__MACOSX") or n.endswith(".DS_Store") for n in names):
        problems.append("macOS junk files were included")
    if not any(n.startswith("skills/") for n in names):
        problems.append("no skill files were included")

    if problems:
        sys.exit("ERROR: package verification failed - " + "; ".join(problems))

    print(f"built: {zip_path}  ({zip_path.stat().st_size:,} bytes, {len(names)} entries)")
    for n in names:
        print(f"  {n}")
    print("verification OK - forward slashes, root manifest, no junk")


def main() -> None:
    ap = argparse.ArgumentParser(description="Package a Cowork plugin into a sideload-ready zip.")
    ap.add_argument("--plugin-dir", required=True, help="Path to the plugin folder")
    ap.add_argument("--version", help="Override the version (defaults to manifest.json)")
    ap.add_argument("--name", help="Base name for the zip (defaults to folder name)")
    args = ap.parse_args()

    plugin_dir = pathlib.Path(args.plugin_dir).expanduser().resolve()
    if not plugin_dir.is_dir():
        sys.exit(f"ERROR: not a directory: {plugin_dir}")

    manifest_path = plugin_dir / "manifest.json"
    if not manifest_path.is_file():
        sys.exit("ERROR: manifest.json not found in the plugin directory")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = args.version or manifest.get("version")
    if not version:
        sys.exit("ERROR: no version given and manifest.json has no version field")

    name = args.name or plugin_dir.name
    build(plugin_dir, version, name)


if __name__ == "__main__":
    main()
