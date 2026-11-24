#!/usr/bin/env python3
"""Bump Formula/claude-desktop-unofficial.rb to the latest upstream release.

Reads the latest release of aaddrick/claude-desktop-debian (tag
v<repo>+claude<app>), takes each AppImage's SHA-256 from the digest GitHub
publishes for release assets, and rewrites the formula's version, both URLs
and both checksums. Prints the new version, or nothing if already current.
With GITHUB_OUTPUT set (GitHub Actions), also writes changed=true|false and
version=<new>.

Uses GITHUB_TOKEN if set (higher API rate limit). Standard library only.
"""

import json
import os
import re
import sys
import urllib.request

UPSTREAM = "aaddrick/claude-desktop-debian"
FORMULA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                       "Formula", "claude-desktop-unofficial.rb")
TAG_RE = re.compile(r"^v(\d+(?:\.\d+)+)\+claude(\d+(?:\.\d+)+)$")
ARCHES = ("arm64", "amd64")


def api(path):
    req = urllib.request.Request(f"https://api.github.com/{path}")
    req.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def output(**kv):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            for key, value in kv.items():
                fh.write(f"{key}={value}\n")


def main():
    release = api(f"repos/{UPSTREAM}/releases/latest")
    tag = release["tag_name"]
    match = TAG_RE.match(tag)
    if not match:
        sys.exit(f"unexpected tag format: {tag}")
    repo_ver, app_ver = match.groups()
    new_version = f"{app_ver}-{repo_ver}"

    with open(FORMULA, encoding="utf-8") as fh:
        text = fh.read()
    current = re.search(r'^  version "([^"]+)"$', text, re.M).group(1)
    if current == new_version:
        output(changed="false", version=current)
        return

    assets = {a["name"]: a for a in release["assets"]}
    new = {}
    for arch in ARCHES:
        name = f"claude-desktop-unofficial-{new_version}-{arch}.AppImage"
        asset = assets.get(name)
        if asset is None:
            sys.exit(f"{tag}: missing asset {name}")
        digest = asset.get("digest") or ""
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
            sys.exit(f"{tag}: no sha256 digest for {name}")
        new[arch] = (asset["browser_download_url"], digest.split(":", 1)[1])

    # Each url line is followed by its sha256 line; rewrite them as pairs,
    # keyed on the arch in the old URL.
    lines = text.splitlines(keepends=True)
    seen = set()
    for i, line in enumerate(lines):
        url_match = re.match(r'^(\s*)url "([^"]+)"$', line.rstrip("\n"))
        if not url_match:
            continue
        indent, old_url = url_match.groups()
        arch = next((a for a in ARCHES if f"-{a}.AppImage" in old_url), None)
        if arch is None:
            continue
        sha_match = re.match(r'^(\s*)sha256 "[0-9a-f]{64}"$',
                             lines[i + 1].rstrip("\n"))
        if not sha_match:
            sys.exit(f"no sha256 line after the {arch} url")
        url, sha = new[arch]
        lines[i] = f'{indent}url "{url}"\n'
        lines[i + 1] = f'{sha_match.group(1)}sha256 "{sha}"\n'
        seen.add(arch)
    if seen != set(ARCHES):
        sys.exit(f"formula urls found for {sorted(seen)}, expected {sorted(ARCHES)}")

    text = "".join(lines)
    text = re.sub(r'^  version "[^"]+"$', f'  version "{new_version}"',
                  text, count=1, flags=re.M)
    with open(FORMULA, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(new_version)
    output(changed="true", version=new_version)


if __name__ == "__main__":
    main()
