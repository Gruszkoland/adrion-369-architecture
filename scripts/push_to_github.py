#!/usr/bin/env python3
"""
push_to_github.py — ADRION 369 v5.6 Full Security Package Push
================================================================
Wgrywa WSZYSTKIE pliki v5.6 do repozytorium GitHub.

Użycie:
    export GITHUB_TOKEN="ghp_twój_token"
    python scripts/push_to_github.py

Token: https://github.com/settings/tokens/new
Uprawnienia: repo → Contents (read/write)
"""

import os, base64, json, urllib.request, urllib.error
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER   = "Gruszkoland"
REPO_NAME    = "adrion-369-architecture"
BRANCH       = "master"

COMMIT_MSG_PREFIX = "security(v5.7): "

# Pliki: (lokalny path względem repo root, repo path na GitHubie)
FILES = [
    # Root
    ("README.md",                                 "README.md"),
    (".gitignore",                                ".gitignore"),
    (".aiexclude",                                ".aiexclude"),
    ("VERSION",                                   "VERSION"),
    # Core
    ("core/trinity.py",                           "core/trinity.py"),
    ("core/security_hardening.py",                "core/security_hardening.py"),
    ("core/redis_backend.py",                     "core/redis_backend.py"),
    ("core/decision_space_162d.py",               "core/decision_space_162d.py"),
    ("core/steganography_detector.py",            "core/steganography_detector.py"),
    ("core/superior_moral_code.py",               "core/superior_moral_code.py"),
    # Tests
    ("tests/test_trinity.py",                     "tests/test_trinity.py"),
    ("tests/test_penetration.py",                 "tests/test_penetration.py"),
    ("tests/test_performance.py",                 "tests/test_performance.py"),
    ("tests/test_new_modules.py",                 "tests/test_new_modules.py"),
    # Docs — top level
    ("docs/CHANGELOG.md",                         "docs/CHANGELOG.md"),
    ("docs/IMPLEMENTATION_CHECKLIST_v56.md",      "docs/IMPLEMENTATION_CHECKLIST_v56.md"),
    ("docs/PENETRATION_REPORT_v54.md",            "docs/PENETRATION_REPORT_v54.md"),
    ("docs/SECURITY_HARDENING.md",                "docs/SECURITY_HARDENING.md"),
    ("docs/THREAT_MODEL.md",                      "docs/THREAT_MODEL.md"),
    ("docs/QUICKSTART.md",                        "docs/QUICKSTART.md"),
    # Docs — core
    ("docs/core/01_CORE_TRINITY.md",              "docs/core/01_CORE_TRINITY.md"),
    ("docs/core/02_CORE_HEXAGON.md",              "docs/core/02_CORE_HEXAGON.md"),
    ("docs/core/03_CORE_GUARDIANS.md",            "docs/core/03_CORE_GUARDIANS.md"),
    ("docs/core/04_CORE_EBDI.md",                 "docs/core/04_CORE_EBDI.md"),
    # Docs — security
    ("docs/security/AGENT_AUTHENTICATION.md",     "docs/security/AGENT_AUTHENTICATION.md"),
    ("docs/security/CIRCUIT_BREAKER.md",          "docs/security/CIRCUIT_BREAKER.md"),
    ("docs/security/DEGRADED_MODE.md",            "docs/security/DEGRADED_MODE.md"),
    ("docs/security/GENESIS_HARDENING.md",        "docs/security/GENESIS_HARDENING.md"),
    ("docs/security/GO_VORTEX_HARDENING.md",      "docs/security/GO_VORTEX_HARDENING.md"),
    ("docs/security/RATE_LIMITING.md",            "docs/security/RATE_LIMITING.md"),
    # Script (self)
    ("scripts/push_to_github.py",                 "scripts/push_to_github.py"),
]

BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"


def gh(method, endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
        "User-Agent": "ADRION-369-Patcher/5.6",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:200]}")
        raise


def get_sha(repo_path):
    try:
        return gh("GET", f"contents/{repo_path}?ref={BRANCH}").get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def push(local_abs, repo_path):
    p = Path(local_abs)
    if not p.exists():
        print(f"  SKIP: {p.name} — plik nie istnieje")
        return False
    content = base64.b64encode(p.read_bytes()).decode()
    sha = get_sha(repo_path)
    action = "UPDATE" if sha else "CREATE"
    print(f"  {action}: {repo_path}")
    payload = {
        "message": f"{COMMIT_MSG_PREFIX}{repo_path}",
        "content": content,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha
    gh("PUT", f"contents/{repo_path}", payload)
    print(f"  OK: {repo_path}")
    return True


def main():
    if not GITHUB_TOKEN:
        print("BRAK GITHUB_TOKEN!")
        print("  export GITHUB_TOKEN='ghp_...'")
        print("  Token: https://github.com/settings/tokens/new")
        print("  Wymagane uprawnienia: repo -> Contents (read/write)")
        return

    repo_root = Path(__file__).parent.parent.resolve()
    print(f"ADRION 369 v5.6 — Full Security Package Push")
    print(f"  Repo:  {REPO_OWNER}/{REPO_NAME} ({BRANCH})")
    print(f"  Root:  {repo_root}")
    print(f"  Files: {len(FILES)}")
    print()

    ok, skip, fail = 0, 0, 0
    for local_rel, repo_path in FILES:
        local_abs = repo_root / local_rel
        try:
            if push(str(local_abs), repo_path):
                ok += 1
            else:
                skip += 1
        except Exception as e:
            print(f"  FAIL: {repo_path}: {e}")
            fail += 1

    print()
    total = ok + skip + fail
    status = "OK" if fail == 0 else "WARNING"
    print(f"[{status}] {ok}/{total} pushed, {skip} skipped, {fail} failed")
    print(f"  https://github.com/{REPO_OWNER}/{REPO_NAME}")


if __name__ == "__main__":
    main()
