# Control D household unblock template

Public starter for:

- weekly review of Control D **blocked** DNS logs
- family email → GitHub issue → optional 24h Bypass (`ttl` on the custom rule)
- promote to permanent only on an **exact** hostname repeat, or a shared suffix **deeper than** the company apex

This is **not** a live household repo. Do not put API tokens, profile IDs, or activity logs here.

Private live example (do not copy its `digests/`): keep yours private.

## What you add after you Use this template

1. Copy `config/settings.example.yaml` → `config/settings.yaml` and fill your IDs locally (keep that file private or gitignored).
2. GitHub Actions secrets: `CONTROLD_API_TOKEN`, `CONTROLD_PROFILE_ID` or `CONTROLD_PROFILE_IDS`, optional `CONTROLD_ALLOWLIST_FOLDER_ID`, optional `CONTROLD_ANALYTICS_HOST`.
3. Control D endpoints on **Full Analytics**.
4. Your own Grok/Gmail automations with **your** From allowlist. Automations are not stored in this git repo.

## Safety defaults

- No auto-bypass for malware, phishing, scams, illegal, or unknown-risky hosts.
- Ads / mailer click wrappers stay refused.
- Family first allow is 24 hours via Control D rule `ttl` (unix expiry).
- Never commit secrets.
