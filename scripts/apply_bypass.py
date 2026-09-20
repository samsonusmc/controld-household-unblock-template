#!/usr/bin/env python3
"""Create Control D BYPASS rules. Family default 24h uses native ttl (unix)."""
from __future__ import annotations
import argparse, json, os, re, sys
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import family_history, tmp_state
API = "https://api.controld.com"
HOST_RE = re.compile(r"^[A-Za-z0-9._*-]{1,253}$")
REFUSE = ("doubleclick.net", "googleadservices.com", "sendgrid.net", "list-manage.com", "mlsend.com")

def refused(h):
    h = h.lower().rstrip(".")
    return any(h == s or h.endswith("." + s) for s in REFUSE)

def profiles():
    raw = os.environ.get("CONTROLD_PROFILE_IDS", "").strip()
    if raw:
        return [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
    one = os.environ.get("CONTROLD_PROFILE_ID", "").strip()
    return [one] if one else []

def api(token, method, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = Request(f"{API}{path}", data=data, method=method, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urlopen(req, timeout=30) as resp:
            return {"status": resp.status, "body": resp.read().decode()}
    except HTTPError as exc:
        return {"status": exc.code, "body": exc.read().decode(errors="replace")}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hostname", action="append", required=True)
    p.add_argument("--hours", type=int, default=24)
    p.add_argument("--permanent", action="store_true")
    p.add_argument("--issue", type=int, default=int(os.environ.get("ISSUE_NUM", "0") or 0))
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    token = os.environ.get("CONTROLD_API_TOKEN", "").strip()
    apply_live = os.environ.get("AUTO_APPLY", "false").lower() == "true" and not args.dry_run
    ids = profiles()
    now = datetime.now(timezone.utc)
    hosts = []
    for h in args.hostname:
        h = h.strip().lower().rstrip(".")
        if HOST_RE.match(h) and not refused(h):
            hosts.append(h)
    if not apply_live:
        print("dry-run", hosts)
        return
    if not token or not ids:
        sys.exit("Need token and profiles")
    for requested in hosts:
        promo, why = family_history.promotion_target(requested)
        if args.permanent:
            promo, why = requested, "forced-permanent"
        nums = family_history.record(requested, args.issue or None, bool(promo), promo)
        comment = family_history.comment(nums, bool(promo))
        for h in family_history.hosts_to_apply(requested, promo):
            permanent = bool(promo) and (h == promo or h == f"*.{promo}" or why == "exact-repeat")
            if args.permanent:
                permanent = True
            hours = None if permanent else args.hours
            until = now + timedelta(hours=hours) if hours else None
            payload = {"do": 1, "status": 1, "via": "-1", "via_v6": "-1", "hostnames": [h], "group": 0, "comment": comment}
            if until:
                payload["ttl"] = int(until.timestamp())
            print("APPLY", h, "perm" if permanent else f"{hours}h", why)
            for pid in ids:
                res = api(token, "POST", f"/profiles/{pid}/rules", payload)
                if int(res.get("status", 0)) >= 400:
                    res = api(token, "PUT", f"/profiles/{pid}/rules", payload)
                print(h, pid, res)
            if hours and until:
                tmp_state.upsert(h, until.isoformat(), hours)
            else:
                tmp_state.drop([h])

if __name__ == "__main__":
    main()
