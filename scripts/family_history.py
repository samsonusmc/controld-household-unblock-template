from __future__ import annotations
import json, os
from datetime import datetime, timezone
from pathlib import Path
PATH = Path("state/family-history.json")
MULTI = {"co.uk", "com.au", "co.nz", "com.br", "co.jp"}

def issue_base():
    repo = os.environ.get("GITHUB_REPOSITORY", "OWNER/REPO")
    return f"https://github.com/{repo}/issues"

def labels(host):
    return [p for p in host.lower().rstrip(".").split(".") if p]

def parent(host):
    parts = labels(host)
    if len(parts) < 2:
        return host.lower().rstrip(".")
    last2 = ".".join(parts[-2:])
    if last2 in MULTI and len(parts) >= 3:
        return ".".join(parts[-3:])
    return last2

def common_suffix(a, b):
    pa, pb = labels(a), labels(b)
    i = 0
    while i < len(pa) and i < len(pb) and pa[-(i + 1)] == pb[-(i + 1)]:
        i += 1
    return ".".join(pa[-i:]) if i else ""

def load():
    if not PATH.exists():
        return {"requests": []}
    return json.loads(PATH.read_text())

def save(data):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(data, indent=2) + "\n")

def prior_exact(host):
    host = host.lower().rstrip(".")
    return [r for r in load().get("requests") or [] if (r.get("host") or "").lower() == host]

def related(host):
    p = parent(host)
    return [r for r in load().get("requests") or [] if r.get("parent") == p or parent(r.get("host") or "") == p]

def promotion_target(host):
    host = host.lower().rstrip(".")
    if prior_exact(host):
        return host, "exact-repeat"
    best = ""
    for row in related(host):
        other = (row.get("host") or "").lower()
        if not other or other == host:
            continue
        lcs = common_suffix(host, other)
        if len(labels(lcs)) > len(labels(best)):
            best = lcs
    if best and len(labels(best)) > len(labels(parent(host))):
        return best, "shared-suffix"
    return None, "first-or-apex-only"

def hosts_to_apply(requested, promote):
    requested = requested.lower().rstrip(".")
    out = [requested]
    if promote and promote != requested:
        out += [promote, f"*.{promote}"]
    seen, uniq = set(), []
    for h in out:
        if h not in seen:
            seen.add(h)
            uniq.append(h)
    return uniq

def record(host, issue, permanent, promoted=None):
    data = load()
    rows = list(data.get("requests") or [])
    rows.append({
        "host": host.lower().rstrip("."),
        "parent": parent(host),
        "promoted": promoted,
        "issue": issue,
        "permanent": permanent,
        "at": datetime.now(timezone.utc).isoformat(),
        "url": f"{issue_base()}/{issue}" if issue else None,
    })
    data["requests"] = rows
    save(data)
    nums = []
    for row in related(host):
        if row.get("issue") and int(row["issue"]) not in nums:
            nums.append(int(row["issue"]))
    if issue and issue not in nums:
        nums.append(issue)
    return nums

def comment(issue_nums, permanent, hours=None):
    refs = " ".join(f"#{n}" for n in issue_nums[-6:])
    return f"{'perm' if permanent else '24h'} {refs}".strip()[:64]
