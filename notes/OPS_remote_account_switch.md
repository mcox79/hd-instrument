# Remote account switching + laptop→desktop handoff

Written 2026-09-12. Everything below was verified against this laptop, the desktop
(`home`, 100.91.12.42) over SSH, and the Claude Code docs. Nothing has been changed yet.

## What is actually on the two machines (verified)

| | laptop (`frameworkmpc`) | desktop (`home`) |
|---|---|---|
| Claude Code | 2.1.229 (npm global) | 2.1.62 (native, `C:\Users\marsh\.local\bin\claude.exe`) |
| signed in as | `marshall.cox@gmail.com` (Max) | `marshall@kel.vin` (Max) |
| `C:\AI` project | present | **missing** |
| SSH over Tailscale | — | works, key auth, no password |
| remote default shell | — | `cmd.exe` (`;` is not a separator; use `&`) |

Both accounts are individual Max plans, not Team/Enterprise, so no admin policy
(`forceLoginOrgUUID`, Remote Control toggle) can block any of this.

## The two facts the whole design rests on

1. **On Windows there is no keychain.** Credentials are a plain file at
   `%USERPROFILE%\.claude\.credentials.json`, protected only by your profile's ACLs.
   That file *is* the account. Swapping it swaps the account.
2. **`CLAUDE_CODE_OAUTH_TOKEN` outranks the stored login** (position 5 vs 7 in the
   documented precedence order). Setting it overrides the signed-in account without
   destroying it; unsetting it reverts. This is the headless escape hatch.

## Does Remote Control do the account switch by itself? No — but it may remove the need for one

Remote Control connects claude.ai/code and the mobile app to a session **running on your
machine, on that machine's local credential**. Signing into a different account in the
browser does not move the work onto that account's quota — it just means you can no longer
see the session, because it lives in the other account's session list. The tokens are still
billed to whichever account the desktop's local Claude Code is logged into.

The docs are unambiguous that the session is owned by the local login:

- a Remote Control session "appears only in your own account's Claude apps";
- Claude Code shows `Remote Control could not verify the signed-in account` specifically
  "when the signed-in account changed";
- on reconnect, when the reconnection record "names a different account", Claude Code
  "starts a new session **without the conversation's earlier messages** and without showing
  a message".

So switching accounts *breaks* the Remote Control session rather than riding through it.
Your local conversation survives intact — only the remote mirror resets.

There is also a structural reason not to switch accounts *through* Remote Control: it rides
on the Anthropic API, authenticated by the very credential you are trying to change. If the
switch goes wrong you have cut your own control channel while 1000 miles away. **SSH over
Tailscale is out-of-band** — it does not depend on any Claude credential — which is exactly
why it is the right channel for the switch, even though Remote Control is the right channel
for the work.

### DECIDED 2026-09-12: the desktop is the live system

Owner's call: the full run lives on the desktop, because it is the live system and the
stronger machine for CPU and GPU tests. "Switch machines instead of accounts" is therefore
**rejected** — the desktop must be able to run on *either* account, so a real switch
mechanism is required.

Consequence worth holding onto: Remote Control is the steering channel (phone → desktop,
already proven working laptop → phone), and SSH is the switching channel. They are separate
on purpose, because SSH does not depend on the credential being switched.

## Mechanism 0: just log in over SSH (test this first — it may replace everything below)

The docs describe a paste-a-code fallback for exactly this case: "If your browser shows a
login code instead of redirecting back after you sign in, paste it into the terminal at the
`Paste code here if prompted` prompt. This happens when the browser can't reach Claude
Code's local callback server, which is common in WSL2, SSH sessions, and containers."

If that fallback works over `ssh -t`, then a remote account switch is simply:

```bash
ssh -t home "claude auth login"      # open the printed URL in whatever browser you have,
                                     # authorize as the account you want, paste the code back
```

and **the entire credential-stash design below becomes unnecessary** — no secrets at rest,
no stale-stash expiry trap, nothing to rotate.

**Status: UNVERIFIED.** Probed on 2026-09-12 and the result was inconclusive for an
environment reason, not a real one: the probing shell had no TTY, so SSH refused to allocate
a pseudo-terminal and Claude Code's full-screen UI aborted with `Raw mode is not supported
on the current process.stdin`. From a real terminal, `ssh -t` allocates a PTY and this
should behave normally.

**Test it from a real terminal before building anything else.** Update the desktop first —
it is on 2.1.62, and there have been auth and Remote Control fixes since.

## Two fallback mechanisms, if Mechanism 0 does not work

### A. Credential-file swap (primary, full fidelity)

Log in as each account **on the desktop** once, stash a copy of each file, then a remote
switch is: copy the right file into place, restart the session.

Keeps everything a normal login has: Remote Control, claude.ai connectors, `/schedule`.

Cost: needs you physically at the desktop once, for two browser logins.

### B. `claude setup-token` → `CLAUDE_CODE_OAUTH_TOKEN` (break-glass, no presence needed)

`claude setup-token` opens a browser authorization flow, prints a **one-year** token, and
saves it nowhere. Because the account is chosen in the *browser*, you can mint **both**
tokens from the laptop right now — use a private window for the second one so you can sign
in as the other account — and just store the two strings on the desktop. No physical
presence at the desktop at all.

Cost, and given the decision above it is a serious one: a session authenticated this way
**cannot start Remote Control** and cannot fetch claude.ai connectors (`--bare` ignores the
variable entirely). So in break-glass mode you **lose phone steering of the desktop** — the
run keeps going, but you are reduced to SSH until you restore a real login. Treat this as
degraded mode for keeping a long run alive, not as a way to work.

**Recommendation: set up both.** A is the daily driver; B is what saves you when you are
1000 miles away and A's stored login has expired.

## Two design traps worth avoiding

- **Do not give each account its own `CLAUDE_CONFIG_DIR`.** It is the obvious "clean"
  answer and it is wrong here: the config dir holds `projects/`, session history,
  `settings.json` and the auto-memory. Split them and `--resume` after a switch will not
  find the work. Use **one** config dir and swap only the credential. That is exactly what
  `/login` does.
- **A running session holds the credential it started with.** Changing the file or the env
  var under a live process does nothing. Every switch is a restart, so continuity comes
  from `claude --resume <id>` plus the project's own recovery path (`notes/STATUS.md`,
  the LEDGER, `git log`).

## The expiry trap (this is the one that will bite)

Logins expire. Claude Code warns 3 days out, and the docs are explicit that an unattended
session which outlives its login **stops making progress and cannot recover** until
someone signs in again. The account you have *not* used for two months is the one whose
stash is stale.

Mitigations, in order of value:

1. Keep mechanism B provisioned — a one-year token is unaffected by the `/login` expiry.
2. Once a month, switch to the idle account for a few minutes and re-stash it (the script
   below re-stashes automatically on every switch).
3. Before any long trip, switch to each slot once and check `claude auth status --json`.

## Setup (do this at the desktop, once)

```powershell
mkdir "$env:USERPROFILE\.claude-accounts"

# currently signed in as work (marshall@kel.vin) — stash that one first
copy "$env:USERPROFILE\.claude\.credentials.json" "$env:USERPROFILE\.claude-accounts\work.credentials.json"

claude auth logout
claude auth login          # sign in as marshall.cox@gmail.com
copy "$env:USERPROFILE\.claude\.credentials.json" "$env:USERPROFILE\.claude-accounts\home.credentials.json"
```

Then mint the two break-glass tokens and save them on the desktop in
`%USERPROFILE%\.claude-accounts\tokens.txt`:

```
claude setup-token     # authorize as work in the browser  -> work token
claude setup-token     # authorize as home (private window) -> home token
```

**Keep `.claude-accounts` out of OneDrive, Dropbox, and any git repo.** It holds two live
credentials in the clear; anyone with admin on that box, or a copy of your profile backup,
gets both accounts.

## The switch script (desktop: `%USERPROFILE%\switch-account.ps1`)

```powershell
param([Parameter(Mandatory)][ValidateSet('work','home')][string]$Account)
$ErrorActionPreference = 'Stop'

$Store = "$env:USERPROFILE\.claude-accounts"
$Live  = "$env:USERPROFILE\.claude\.credentials.json"
$Src   = Join-Path $Store "$Account.credentials.json"
$Map   = @{ 'marshall@kel.vin' = 'work'; 'marshall.cox@gmail.com' = 'home' }

if (-not (Test-Path $Src)) { throw "No stashed credential for '$Account' at $Src" }

# 1. Preserve the live credential back into its own slot. Claude Code refreshes the
#    token in place, so the live file is always newer than its stash.
try {
  $cur = (claude auth status --json | ConvertFrom-Json).email
  if ($Map.ContainsKey($cur)) {
    if ($Map[$cur] -eq $Account) { Write-Host "Already on '$Account' ($cur)."; exit 0 }
    Copy-Item $Live (Join-Path $Store "$($Map[$cur]).credentials.json") -Force
    Write-Host "Re-stashed current account '$($Map[$cur])' ($cur)."
  } else { Write-Warning "Live account '$cur' is not in the map; not re-stashing." }
} catch { Write-Warning "Could not read current auth status: $_" }

# 2. Stop anything holding the old credential.
Get-Process claude -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# 3. Swap, and report what we landed on.
Copy-Item $Src $Live -Force
$now = claude auth status --json | ConvertFrom-Json
Write-Host "Now signed in as $($now.email) [$($now.subscriptionType)]"
```

Drive it from anywhere on the tailnet:

```bash
ssh home "powershell -NoProfile -ExecutionPolicy Bypass -File %USERPROFILE%\switch-account.ps1 -Account home"
ssh home "claude auth status --json"
```

Break-glass form, when the stored logins are unusable:

```bash
ssh home "set CLAUDE_CODE_OAUTH_TOKEN=<token> & cd /d C:\AI\hd-instrument & claude --resume <session-id>"
```

## Knowing *when* to switch

`claude auth status --json` reports which account is live — it does **not** report how much
quota is left, and there is no documented CLI for remaining quota. So detection is either
the running session reporting a limit, or checking usage on claude.ai. A wrapper that trips
the switch automatically on the rate-limit error is buildable, but it should be written
against a real limit message rather than a guessed one.

Worth knowing: **Remote Control** (`claude --remote-control`) puts the desktop session into
the session list at claude.ai/code and in the mobile app, reconnects by itself after
network drops and sleep, and queues messages while disconnected. That is a better way to
*watch and steer* the desktop from a phone than SSH — but it needs mechanism A, since a
setup-token session cannot establish it.

## Desktop handoff — open questions (deferred, per your call)

`C:\AI` does not exist on the desktop. Before moving the work, settle:

1. **Transport** — is the project a git repo with a reachable remote, or does it move as a
   file copy over Tailscale? `C:\AI` itself is not a repo; `hd-instrument` needs checking.
2. **Untracked state** — `data/`, heartbeats, queue files and `notes/` artifacts that are
   gitignored but load-bearing for recovery.
3. **Python environment** — versions, venv, GPU/CUDA if any experiment cells need it.
4. **The `~/.claude` payload** — `agents/`, `skills/`, `commands/`, the hooks in
   `settings.json`, and the auto-memory directory. The desktop has its own `~/.claude`;
   these need merging, not overwriting.
5. **Version skew** — desktop is on 2.1.62, laptop on 2.1.229. Update the desktop first.
6. **Cron/loops** — anything scheduled on the laptop that should stop there and start there.
