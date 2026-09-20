from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
STATE = Path("state/tmp-bypasses.json")

def load():
    if not STATE.exists():
        return []
    return list(json.loads(STATE.read_text()).get("rules") or [])

def save(rules):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"rules": rules}, indent=2) + "\n")

def upsert(host, until_iso, hours):
    host = host.lower().rstrip(".")
    rules = [r for r in load() if r.get("host") != host]
    rules.append({"host": host, "until": until_iso, "hours": hours})
    save(rules)

def due(now=None):
    now = now or datetime.now(timezone.utc)
    out = []
    for r in load():
        try:
            until = datetime.fromisoformat((r.get("until") or "").replace("Z", "+00:00"))
        except ValueError:
            continue
        if until.tzinfo is None:
            until = until.replace(tzinfo=timezone.utc)
        if now >= until:
            out.append(r)
    return out

def drop(hosts):
    gone = {h.lower().rstrip(".") for h in hosts}
    save([r for r in load() if r.get("host") not in gone])
