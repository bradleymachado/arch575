# Prompt for Brad — Cloudflare API token for the comment API (Claude app conversation)

Needed only if S10–S12 (reviewer comments) run tonight: have it in place before 22:00. Paste everything inside the fence into a new Claude app conversation. Attach screenshots whenever a screen does not match the description.

```
Cloudflare token for arch575 comments
Name this conversation 'Cloudflare token arch575'. You are walking me (Brad) through getting two values from Cloudflare, one step per message. I will reply with "done", a screenshot, or a question after each step. If a screenshot shows something different from what you expected, adapt the next step to what is actually on my screen. Do not move on until I confirm the current step.

Context
- Purpose: a small Cloudflare Worker with a KV store will hold reviewer comments for my presentation site arch575.bradmachado.com. Nothing about my domain bradmachado.com changes: its DNS stays at GoDaddy. Do not let me add the domain to Cloudflare or change nameservers.
- I need: (a) my Cloudflare Account ID; (b) an API token named arch575-comments with exactly two permissions, Account · Workers Scripts · Edit and Account · Workers KV Storage · Edit, limited to my account.
- Where they go: a file C:\Users\User\Projects\arch575\_local\cf.env with two lines:
    CF_ACCOUNT_ID=<the id>
    CF_API_TOKEN=<the token>
  That folder is git-ignored. The token must never be pasted anywhere else, including this chat. If I paste it here by accident, tell me to roll it (My Profile -> API Tokens -> the token's menu -> Roll) and continue with the new value.

Walk me through, in this order
1. Sign in at https://dash.cloudflare.com. If I have no account: Sign up, free plan; no payment details are needed for the Workers free tier.
2. Left menu: Workers & Pages. If Cloudflare asks me to choose a workers.dev subdomain, tell me to enter bradmachado and confirm (if it is taken, try bradmachado-arch; tell me to note the exact name). On the Workers & Pages Overview page, find Account ID in the right-hand column and click "Click to copy". Tell me to paste it into Notepad for now.
3. Top right: profile icon -> My Profile -> API Tokens (left tab) -> Create Token -> scroll to "Custom token" -> Get started.
4. Fill the form: Token name arch575-comments. Permissions row 1: Account · Workers Scripts · Edit. Click "+ Add more". Row 2: Account · Workers KV Storage · Edit. Account Resources: Include · my account. Leave Client IP Address Filtering and TTL blank. Ask for a screenshot before I press "Continue to summary" and check the two permission rows and the account.
5. Continue to summary -> Create Token. The token is shown once. Tell me to click Copy.
6. Create the file: open Notepad; line 1 CF_ACCOUNT_ID= followed by the id, line 2 CF_API_TOKEN= followed by the token; no quotes, no spaces around the equals sign. File -> Save As -> go to C:\Users\User\Projects\arch575 -> create a folder named _local if it is missing -> open it -> File name cf.env -> Save as type "All files" -> Encoding UTF-8 -> Save.
7. Verify: Windows key, type cmd, Enter, then run:
       type C:\Users\User\Projects\arch575\_local\cf.env
   Two lines should print. Then run:
       cd C:\Users\User\Projects\arch575 && git status --short
   _local must NOT appear (it is ignored). If it appears, stop and tell me.
8. Report back a two-line summary I can paste into my Claude Code session: the workers.dev subdomain name, and "cf.env saved" (no values).

Style: short messages, numbered where there is more than one action, literal button names, no filler. If I paste a screenshot, describe what you see in one line before giving the next step.
```
