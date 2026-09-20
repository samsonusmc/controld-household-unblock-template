# Control D household unblock template

Public starter for weekly Control D blocked-DNS review and a family email → 24h Bypass pipeline.

**Grok and household admins: read [SETUP_WITH_GROK.md](SETUP_WITH_GROK.md) first.** That file is the implementation playbook (required products, questions to ask, automation skeleton).

This repo has **no secrets and no live logs**. Put the real household copy in a private repo.

Required to run the full pipeline:

1. Control D subscription + API token + Full Analytics
2. GitHub (connector + private repo + Actions secrets)
3. Grok connected to **Gmail or Outlook** (family mail)
4. Grok Automations on the admin account
