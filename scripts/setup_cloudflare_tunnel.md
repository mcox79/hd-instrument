# Cloudflare Tunnel setup (user-action; ~10 min)

This is the only audit-week task that needs YOU at the machine — Cloudflare auth opens a
browser for OAuth and can't be automated headlessly.

After this, the v1 demo gets a public URL like `demo.<your-domain>.com` (or a free
`*.trycloudflare.com` URL) reachable from anywhere — laptop, investor's phone, customer
browser — all for $0.

## Prerequisites (already done)

- `cloudflared` 2026.5.2 installed (verified at `C:\Program Files (x86)\cloudflared\cloudflared.exe`)

## Option A — Free trycloudflare.com URL (zero-config, quick test)

For a quick demo URL that doesn't need a domain:

```cmd
cd /d C:\dev\hd-instrument
cloudflared tunnel --url http://localhost:8000
```

This prints a URL like `https://random-words-abc.trycloudflare.com`. The URL changes
every restart, so this is for QUICK TESTING only — not a stable demo link.

## Option B — Named tunnel with custom domain (the production demo path)

### Step 1: Cloudflare account + domain

If you already have a Cloudflare account with a domain managed there: skip to Step 2.

If you need to set this up: sign up at https://dash.cloudflare.com, add a domain (or
transfer one), wait for DNS propagation.

### Step 2: cloudflared login

```cmd
cloudflared tunnel login
```

Opens a browser window. Log in to Cloudflare. Select the domain (zone) you want to use.
A certificate file `cert.pem` is saved to `%USERPROFILE%\.cloudflared\`.

### Step 3: create the tunnel

```cmd
cloudflared tunnel create v1-demo
```

Prints a tunnel UUID. Note it. A credentials file is saved at
`%USERPROFILE%\.cloudflared\<UUID>.json`.

### Step 4: DNS route

Pick a hostname for the demo (e.g., `demo.yourdomain.com`):

```cmd
cloudflared tunnel route dns v1-demo demo.yourdomain.com
```

Cloudflare creates a CNAME record pointing to the tunnel.

### Step 5: tunnel config

Create `%USERPROFILE%\.cloudflared\config.yml`:

```yaml
tunnel: <UUID-from-step-3>
credentials-file: C:\Users\marsh\.cloudflared\<UUID>.json

ingress:
  - hostname: demo.yourdomain.com
    service: http://localhost:8000   # FastAPI backend
  # Optionally route frontend separately on a different hostname or path:
  # - hostname: app.yourdomain.com
  #   service: http://localhost:3000  # Next.js frontend
  - service: http_status:404
```

For v1, route everything to port 8000 (backend serves both API + statically-served
frontend). Once Next.js dev workflow is in place we'll split.

### Step 6: run the tunnel

```cmd
cloudflared tunnel run v1-demo
```

Or as a Windows service (auto-start on reboot):

```cmd
cloudflared service install
```

### Step 7: test

From the laptop (or anywhere) browse `https://demo.yourdomain.com`. Should see the
backend's `/` JSON.

## Hardening checklist

- [ ] Cloudflare Access enabled (require Google login / email whitelist)
- [ ] Rate limits set in Cloudflare dashboard (e.g., 10 req/sec per IP)
- [ ] Cloudflare WAF rules: block known bad IPs / countries if relevant
- [ ] Tunnel runs as a Windows service (survives reboots)
- [ ] `cloudflared` updates monthly (newer versions patch security issues)

## Pause cost / billing

Cloudflare Tunnel is FREE forever for personal + small business use. No usage limits
apply at our scale. Closing the tunnel stops the connection but doesn't cost anything.

## Troubleshooting

- "tunnel not found": run `cloudflared tunnel list` to verify UUID
- "ingress not matching": check `config.yml` hostname matches the DNS route
- Backend not reachable: `curl http://localhost:8000/` on the desktop first
- Slow first request: tunnel cold-starts in ~1s; subsequent are warm

## Reference

- https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/
- https://github.com/cloudflare/cloudflared
