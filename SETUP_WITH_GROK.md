# Setup with Grok — start here

This file is for **Grok** (the assistant in this chat) and the household admin.
If you are Grok and the user pointed you at this repo, follow it in order. Do not skip the connections. Do not invent Control D IDs.

Live household copies of this pipeline should stay in a **private** GitHub repo. This public repo is the template only.

---

## 0. What this is

A household Control D helper:

- Weekly review of **blocked** DNS lookups.
- Family emails a mailbox with subject containing `blocked`.
- Low-risk first allow is **24 hours** (Control D custom rule `ttl`).
- Permanent only after an exact hostname repeat, a low-risk “make permanent” reply, or a shared suffix **deeper than** the company apex (`c.parent.com`, not `parent.com`).
- Malware / phishing / illegal / unknown-risky: **hold for the admin**, never auto-bypass.
- Ads and mailer click wrappers: refuse.

You (Grok) suggest and apply **hostname Bypass rules**. You never turn off whole Control D filters.

---

## 1. Required products (tell the user this first)

Grok must state these are required. If any is missing, stop and get it connected before writing rules.

### Control D subscription

- A paid **Control D** account (consumer is fine).
- At least one **Profile** and one **Endpoint** (the resolver the family devices use).
- Endpoints used by the family should be on **Full Analytics** or activity logs will be empty.
- An **API token** from the Control D dashboard (API page) with permission to read analytics and **write custom rules**.

Without a Control D subscription + API token this pipeline cannot fetch blocks or create Bypass rules.

### GitHub

- A GitHub account Grok can use via the **GitHub connector**.
- A **private** repo for the live household (do not run this against the public template with real logs).
- Permission to create repos, push, set Actions secrets, and open issues.

### Grok mail connector — Gmail **or** Outlook

Family unblock mail **requires** a connected inbox:

- Connect **Gmail** *or* **Outlook** in Grok (the same account that will receive family “blocked” mail).
- If neither connector is connected, family email automation cannot run. Say so and call the connector auth flow. Do not pretend SMS is wired.

### Grok Automations

- The household admin needs Automations available on their xAI/Grok account.
- Weekly review + family-mail + “admin approved” reply are Automations, not files in git.

### Optional but useful

- Control D **Custom Rules folder** named something like `Family Allowlist` (folder action Bypass). Folder ID can go in settings later.
- Family members who will send requests (their exact From addresses).

### Not required / not available here

- SMS / iMessage as a first-class connector. Use email (or an SMS-to-email gateway the family already has).
- Google Contacts. Use a hard From allowlist.
- Org-only Control D CSV API. Consumer accounts use the dashboard JSON activity-log (`/v2/activity-log`) when Full Analytics is on, or a manual CSV drop in `incoming/`.

---

## 2. Grok: collect this before you implement

Ask the user these. Do not proceed to live apply until 2.1–2.4 are answered.

### 2.1 Control D

- Consumer or Organization account?
- API token created? (they paste it only into GitHub Actions secrets, never into chat if they can avoid it)
- Profile ID(s) — every profile that should receive Bypass rules
- Endpoint ID(s) on Full Analytics
- Analytics host if they know it (consumer JSON often looks like `america.analytics.controld.com` or regional). If unknown, Grok can discover it from a dashboard HAR later; do not guess tokens.
- Custom rules folder ID, if any

### 2.2 GitHub

- Org or personal account to put the **private** live repo under?
- Proposed private repo name (suggest `controld-household-review` or similar — not this template name)
- Confirm GitHub connector works (list repos)

### 2.3 Mail

- Gmail or Outlook?
- Address that receives family requests (usually the admin inbox)
- Subject token (default: `blocked`)
- Allowlisted From addresses (family + admin). Everyone else is ignore-or-hold.

### 2.4 Policy

- First allow hours (default 24)
- Auto-apply allowlisted low-risk family requests? (default yes)
- High-risk always hold for admin? (default yes)
- Admin display name for “waiting for …” mail

Write answers into `config/settings.yaml` in the **private** repo only.

---

## 3. Implementation order (Grok)

1. Confirm connectors: GitHub, Gmail **or** Outlook, Automations.
2. Create a **private** repo from this template (or copy these files). Never dump live `activity.csv` into the public template.
3. Push sanitized copies of `scripts/`, `.github/workflows/`, issue templates, `config/settings.example.yaml` → household `settings.yaml`.
4. Tell the user the exact Actions secrets to set:
   - `CONTROLD_API_TOKEN`
   - `CONTROLD_PROFILE_ID` and/or `CONTROLD_PROFILE_IDS` (comma-separated)
   - optional `CONTROLD_ANALYTICS_HOST`
   - optional `CONTROLD_ENDPOINT_ID`
   - optional `CONTROLD_ALLOWLIST_FOLDER_ID`
5. Enable Actions on the private repo. Run `weekly-review` with `workflow_dispatch` once (CSV in `incoming/` is enough if analytics host is not ready).
6. Create Grok Automations on the admin account:
   - **Family blocked email** — Gmail/Outlook `new_email`, subject contains `blocked`. Prompt: allowlist From, classify host, 24h vs hold, HTML reply, issue with `APPROVED TO APPLY` only when auto-safe.
   - **Weekly review** — GitHub issue created/labeled `weekly-review` or a Sunday schedule. Comment suggestions only; apply only on `APPROVED TO APPLY`.
   - **Admin approved mail** — GitHub `issue_comment` on the private repo when the comment contains `APPROVED TO APPLY`; email the original family sender.
7. Send the admin one HTML sample mail per status (24h, waiting, approved, permanent) if they want to judge tone.
8. Do a text-only family test from an allowlisted address (`TEST ONLY` in the body the first time if they do not want a live Bypass).

---

## 4. Automation prompt skeleton (family mail)

Paste and fill brackets:

```
Family DNS unblock mail (subject contains blocked).
Private repo only: [OWNER/PRIVATE_REPO].
Mail From allowlist (case-insensitive): [admin@, family@, …].
Unknown From: never apply. Spam → ignore. Real-looking stranger → needs-admin issue, no APPROVED TO APPLY.
HOLD: malware, phishing, scams, illegal, CSAM, weapons, illicit drugs, piracy, or unclear+risky.
REFUSE: ad networks and ESP click wrappers.
AUTO 24h: allowlisted + low-risk household host. Issue body starts with:
APPROVED TO APPLY
bypass hostname
Permanent only if allowlisted + low-risk and they asked (mailto make-permanent / reply).
Always reply on the same thread with HTML + plain text: host, one-line summary, category, status.
mailto make-permanent button only on low-risk 24h.
Never disable filters. Never touch unrelated repos.
```

---

## 5. Apply comment format

```
APPROVED TO APPLY
bypass checkout.example.com
bypass data.m.example.com permanent
```

GitHub Actions `apply-approved` must require that phrase. No phrase → no API write.

---

## 6. Safety reminders for Grok

- Do not print the Control D API token back to the user after they set it.
- Do not commit tokens, `config/settings.yaml` with real IDs, or raw household `activity.csv` to a public repo.
- Do not auto-allow a host just because it was blocked a lot.
- Do not promote `parent.com` just because two different subdomains were requested; promote `c.parent.com` only when that suffix is shared and deeper than eTLD+1.
- If the user has no mail connector, implement weekly review only and say family-email is blocked on connecting Gmail or Outlook.
