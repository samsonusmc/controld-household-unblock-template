#!/usr/bin/env python3
import os, sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import tmp_state
API = "https://api.controld.com"

def profiles():
    raw = os.environ.get("CONTROLD_PROFILE_IDS", "").strip()
    if raw:
        return [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
    one = os.environ.get("CONTROLD_PROFILE_ID", "").strip()
    return [one] if one else []

def api(token, method, path):
    req = Request(f"{API}{path}", method=method, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urlopen(req, timeout=30) as resp:
            return {"status": resp.status, "body": resp.read().decode()}
    except HTTPError as exc:
        return {"status": exc.code, "body": exc.read().decode(errors="replace")}

def main():
    token = os.environ.get("CONTROLD_API_TOKEN", "").strip()
    ids = profiles()
    if not token or not ids:
        sys.exit("Need token and profiles")
    dry = os.environ.get("AUTO_APPLY", "false").lower() != "true"
    removed = []
    for r in tmp_state.due():
        host = r.get("host")
        if not host:
            continue
        print("EXPIRE", host)
        if dry:
            continue
        ok = True
        for pid in ids:
            res = api(token, "DELETE", f"/profiles/{pid}/rules/{host}")
            print(pid, host, res)
            if int(res.get("status", 0)) >= 400 and int(res.get("status", 0)) != 404:
                ok = False
        if ok:
            removed.append(host)
    if removed:
        tmp_state.drop(removed)

if __name__ == "__main__":
    main()
