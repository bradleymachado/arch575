# Prompt for Brad — GoDaddy CNAME walkthrough (Claude app conversation)

Paste everything inside the fence into a new Claude app conversation. Attach screenshots whenever a screen does not match the description.

```
GoDaddy CNAME for arch575.bradmachado.com
Name this conversation 'GoDaddy CNAME arch575'. You are walking me (Brad) through adding ONE DNS record at GoDaddy, step by step, one step per message. I will reply with "done", a screenshot, or a question after each step. If a screenshot shows something different from what you expected, adapt the next step to what is actually on my screen. Do not move on until I confirm the current step.

Context
- My domain bradmachado.com is registered at GoDaddy and its DNS is managed at GoDaddy. The main site is on GitHub Pages and works today. I must not break it.
- A new subdomain, arch575.bradmachado.com, will be served by GitHub Pages from the repo bradleymachado/arch575. The custom domain has already been set on the GitHub side (if I tell you it has not, stop and tell me to do that first; the order matters because of a past domain takeover).
- The record to add is exactly:
    Type: CNAME
    Name (Host): arch575
    Value (Points to): bradleymachado.github.io
    TTL: leave the default (1 hour / 3600 is fine)
- Nothing else changes. Do not let me edit or delete any existing record. In particular these must stay untouched: the four A records for @ (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153), the CNAME www -> bradleymachado.github.io, and the TXT record _github-pages-challenge-bradleymachado. Never create a wildcard (*) record. Never put the repo name in the value; it is the account host only.

Walk me through, in this order
1. Sign in at godaddy.com. Open My Products (the person icon or my name at top right -> My Products). Find bradmachado.com in the Domains list. Tell me which button to click to reach DNS (usually "DNS" or the three dots -> "Manage DNS"; on some layouts it is Domain -> DNS tab).
2. On the DNS page, ask me for a screenshot of the full record list BEFORE changing anything. Check that the records listed above are present and tell me to confirm. If anything named arch575 already exists, stop and ask me before continuing.
3. Click "Add New Record" (or "Add"). Tell me what to pick in each field: Type CNAME, Name arch575, Value bradleymachado.github.io, TTL default. Warn me that GoDaddy appends ".bradmachado.com" automatically, so the Name field must contain only arch575 (no dots, no domain) and the Value must not end with a dot or a slash and must not start with https://.
4. Before I press Save, ask for a screenshot of the filled-in form and check every field character by character. Then tell me to Save.
5. After saving, ask for a screenshot of the record list and confirm the new row reads: CNAME, arch575, bradleymachado.github.io. Confirm the other records are unchanged.
6. Verification. Tell me to open Command Prompt (Windows key, type cmd, Enter) and run:
       nslookup arch575.bradmachado.com
   Expected within a few minutes to a few hours: a line with bradleymachado.github.io and addresses 185.199.108.153 through 185.199.111.153. If it says "Non-existent domain", that is propagation delay; tell me to wait 10 minutes and try again, up to a few hours.
7. Then tell me to open https://github.com/bradleymachado/arch575/settings/pages and look at the Custom domain box. When the DNS check shows a green check, tell me to tick "Enforce HTTPS" (it may be greyed out for a while after the DNS check passes; that is GitHub issuing the certificate; wait and refresh).
8. Final check: open https://arch575.bradmachado.com (padlock expected once HTTPS is enforced) and https://bradmachado.com (must be unchanged). Report both results to me as a two-line summary I can paste back into my Claude Code session.

Style: short messages, numbered where there is more than one action, literal button names, no filler. If I paste a screenshot, describe what you see in one line before giving the next step.
```
