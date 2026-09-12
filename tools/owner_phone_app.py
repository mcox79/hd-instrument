"""tools/owner_phone_app.py -- the owner's window as a PHONE web app (2026-09-12, owner request), replacing scorecard_gui.py
when you are away from the desk, PLUS a remote switch of the desktop's Claude Code login between two saved profiles.

WHAT IT SERVES (stdlib only, no framework):
  /                    one-page app (installable: Chrome -> "Add to Home screen"), four tabs:
                         HOW WE'RE DOING  -- the plain-language scorecard (same source of truth as scorecard_gui: tools/scorecard.py)
                         QUESTIONS        -- open board questions + answer box; finished work waiting for your verdict + Mark as DONE;
                                             a note box (-> notes/COMMENTARY.md, read at the start of the next turn)
                         UPDATES          -- tools/owner_updates.py list
                         ACCOUNT          -- which Claude Code login the desktop is using; save it as a profile; switch profiles
  /api/...             JSON endpoints behind a TOKEN (generated on first run -> data/hook_state/owner_phone_token.txt; the page
                       asks for it once and keeps it in localStorage). Every write and the ACCOUNT tab require the token.

ACCOUNT SWITCH -- what it does and its limits (verified on this machine 2026-09-12):
  Claude Code keeps the login in TWO files under the user profile: ~/.claude/.credentials.json (OAuth tokens) and the
  `oauthAccount` block of ~/.claude.json (account identity). "Save as <profile>" copies both into ~/.claude/profiles/<profile>/;
  "Switch to <profile>" writes them back. Running Claude Code processes keep their old login in memory, so the switch offers to
  END the VS Code extension's claude.exe processes (ONLY those under .vscode/extensions/anthropic.claude-code-*; never the Claude
  desktop app, never other processes) -- you then reload the VS Code window / reopen the Claude panel. Refresh tokens expire
  (shown per profile): a profile whose refresh token has expired needs a normal /login once; the app cannot log in for you.

REACH IT FROM THE PHONE SAFELY: run it on the desktop bound to the Tailscale (or LAN/VPN) address, never a public one:
    .venv\\Scripts\\python tools\\owner_phone_app.py --host 100.x.y.z --port 8765      (then open http://100.x.y.z:8765 on the phone)
  or --host 0.0.0.0 behind your firewall. Plain HTTP on a private network + the token; do NOT port-forward it to the internet.
Self-test: python tools/owner_phone_app.py --self-test   (serves on 127.0.0.1, exercises every endpoint, exits).
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO))

TOKEN_PATH = REPO / "data" / "hook_state" / "owner_phone_token.txt"
HOME = Path(os.path.expanduser("~"))
CRED = HOME / ".claude" / ".credentials.json"
CLAUDE_JSON = HOME / ".claude.json"
PROFILES = HOME / ".claude" / "profiles"
PROFILE_NAMES = ("work", "private")


# ---------------------------------------------------------------------------------------------------------------- data
def token() -> str:
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not TOKEN_PATH.is_file():
        TOKEN_PATH.write_text(secrets.token_urlsafe(24), encoding="utf-8")
    return TOKEN_PATH.read_text(encoding="utf-8").strip()


def scorecard() -> dict:
    import scorecard as SC
    sc = SC.build()
    try:
        SC.write_outputs(sc)
    except Exception:
        pass
    return sc


def mark_done(slug: str) -> str:
    """Same operation as scorecard_gui._mark_done: owner_verdict: DONE in that problem's OWNER_NOTES.md."""
    if not slug or "/" in slug or "\\" in slug or slug.startswith("."):
        raise ValueError("bad slug")
    path = REPO / "notes" / "problems" / slug / "OWNER_NOTES.md"
    txt = path.read_text(encoding="utf-8") if path.is_file() else ""
    if txt.startswith("---"):
        head, _, rest = txt[3:].partition("---")
        lines = [ln for ln in head.strip("\n").splitlines() if not ln.strip().startswith("owner_verdict:")]
        lines.append("owner_verdict: DONE")
        txt = "---\n" + "\n".join(lines) + "\n---" + rest
    else:
        txt = "---\nowner_verdict: DONE\n---\n\n" + txt
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(txt, encoding="utf-8", newline="\n")
    return "Marked DONE: %s. The strategy session will fold it in." % slug


def answer_question(qid: str, text: str) -> str:
    import board as B
    B.resolve(qid, text)
    return "Answer to %s saved to notes/BOARD.md." % qid


def add_note(text: str) -> str:
    import commentary as C
    C.add(text, source="the phone app")
    return "Note saved to notes/COMMENTARY.md; it is read at the start of the next turn."


def updates() -> list:
    import owner_updates as U
    return U.list_updates() if hasattr(U, "list_updates") else U.load() if hasattr(U, "load") else []


def now_panel() -> dict:
    """What the strategy session is doing right now, from disk: heartbeat age, the current STATUS position entry, the last
    ledger bullets, the latest owner update."""
    hb = REPO / "data" / "heartbeats" / "research.timestamp"
    age_min = None
    try:
        ts = datetime.strptime(hb.read_text(encoding="utf-8").strip(), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        age_min = int((datetime.now(timezone.utc) - ts).total_seconds() // 60)
    except Exception:
        pass
    position = ""
    try:
        txt = (REPO / "notes" / "STATUS.md").read_text(encoding="utf-8")
        i = txt.find("## POSITION")
        block = txt[i:].split("\n### ", 2)
        position = ("### " + block[1]).strip() if len(block) > 1 else ""
    except Exception:
        pass
    ledger = []
    try:
        lines = (REPO / "notes" / "SIGNAL_LOSS_LEDGER_affected_entity_chain.md").read_text(encoding="utf-8").splitlines()
        bullets = [ln for ln in lines if ln.startswith("- ")]
        ledger = bullets[-4:]
    except Exception:
        pass
    ups = updates()
    return {"heartbeat_minutes_ago": age_min, "position": position[:2500], "ledger_tail": ledger, "latest_update": (ups[-1] if ups else None)}


# ------------------------------------------------------------------------------------------------------------- account
def _read_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def account_state() -> dict:
    cur = _read_json(CLAUDE_JSON) or {}
    oa = cur.get("oauthAccount") or {}
    cred = _read_json(CRED) or {}
    oauth = cred.get("claudeAiOauth") or {}
    def exp(ms):
        if not ms:
            return None
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    current = {"email": oa.get("emailAddress"), "org": oa.get("organizationName"), "plan": oauth.get("subscriptionType"),
               "access_expires": exp(oauth.get("expiresAt")), "refresh_expires": exp(oauth.get("refreshTokenExpiresAt"))}
    profiles = {}
    for name in PROFILE_NAMES:
        d = PROFILES / name
        pj = _read_json(d / "claude.json") or {}
        pc = _read_json(d / "credentials.json") or {}
        if pj or pc:
            po = (pj.get("oauthAccount") or {}); pa = (pc.get("claudeAiOauth") or {})
            profiles[name] = {"email": po.get("emailAddress"), "org": po.get("organizationName"), "plan": pa.get("subscriptionType"),
                              "refresh_expires": exp(pa.get("refreshTokenExpiresAt")),
                              "saved_at": datetime.fromtimestamp((d / "credentials.json").stat().st_mtime).strftime("%Y-%m-%d %H:%M") if (d / "credentials.json").is_file() else None,
                              "is_current": bool(po.get("emailAddress") and po.get("emailAddress") == oa.get("emailAddress"))}
        else:
            profiles[name] = None
    return {"current": current, "profiles": profiles, "claude_processes": claude_extension_processes()}


def save_profile(name: str) -> str:
    if name not in PROFILE_NAMES:
        raise ValueError("profile must be one of %s" % (PROFILE_NAMES,))
    d = PROFILES / name; d.mkdir(parents=True, exist_ok=True)
    if not CRED.is_file() or not CLAUDE_JSON.is_file():
        raise FileNotFoundError("no current Claude Code login on this machine")
    shutil.copy2(CRED, d / "credentials.json")
    cur = _read_json(CLAUDE_JSON) or {}
    (d / "claude.json").write_text(json.dumps({"oauthAccount": cur.get("oauthAccount")}, indent=1), encoding="utf-8")
    return "Saved the current login as profile '%s' (%s)." % (name, (cur.get("oauthAccount") or {}).get("emailAddress"))


def switch_profile(name: str) -> str:
    if name not in PROFILE_NAMES:
        raise ValueError("profile must be one of %s" % (PROFILE_NAMES,))
    d = PROFILES / name
    if not (d / "credentials.json").is_file() or not (d / "claude.json").is_file():
        raise FileNotFoundError("profile '%s' has not been saved yet (log in as that account on the desktop, then Save)" % name)
    # keep a rolling backup of what we overwrite
    bk = PROFILES / "_last_overwritten"; bk.mkdir(parents=True, exist_ok=True)
    if CRED.is_file():
        shutil.copy2(CRED, bk / "credentials.json")
    cur = _read_json(CLAUDE_JSON) or {}
    (bk / "claude.json").write_text(json.dumps({"oauthAccount": cur.get("oauthAccount")}, indent=1), encoding="utf-8")
    shutil.copy2(d / "credentials.json", CRED)
    prof = _read_json(d / "claude.json") or {}
    cur["oauthAccount"] = prof.get("oauthAccount")
    CLAUDE_JSON.write_text(json.dumps(cur, indent=2), encoding="utf-8")
    return ("Switched the saved login to '%s' (%s). Running Claude Code processes still hold the old login: use "
            "'End VS Code Claude processes' then reload the VS Code window." % (name, (prof.get("oauthAccount") or {}).get("emailAddress")))


def claude_extension_processes() -> list:
    """ONLY the VS Code extension's claude.exe processes (path contains .vscode/extensions/anthropic.claude-code)."""
    if os.name != "nt":
        return []
    ps = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'claude.exe' -and $_.CommandLine -match "
          "'\\\\.vscode\\\\extensions\\\\anthropic\\.claude-code' } | Select-Object ProcessId | ConvertTo-Json -Compress")
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=30).stdout.strip()
        if not out:
            return []
        data = json.loads(out)
        rows = data if isinstance(data, list) else [data]
        return [int(r["ProcessId"]) for r in rows]
    except Exception:
        return []


def end_claude_extension_processes() -> str:
    pids = claude_extension_processes()
    ended = []
    for pid in pids:
        try:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, text=True, timeout=15)
            ended.append(pid)
        except Exception:
            pass
    return "Ended %d VS Code Claude process(es) %s. Now reload the VS Code window (Ctrl+Shift+P -> Reload Window) and reopen Claude." % (len(ended), ended)


# ---------------------------------------------------------------------------------------------------------------- page
PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>hd-instrument</title>
<link rel="manifest" href='data:application/manifest+json,{"name":"hd-instrument","short_name":"hd-instrument","start_url":"/","display":"standalone","background_color":"%23141414","theme_color":"%23141414"}'>
<style>
body{margin:0;background:#141414;color:#e8e8e8;font:15px system-ui,sans-serif;padding:0 12px 24px}
nav{display:flex;gap:6px;position:sticky;top:0;background:#141414;padding:10px 0;z-index:2}
nav button{flex:1;background:#262626;color:#ccc;border:0;border-radius:8px;padding:10px 4px;font-size:13px}
nav button.on{background:#5d4a2e;color:#fff}
h2{font-size:17px;margin:14px 0 6px}.small{color:#9a9a9a;font-size:13px}
.card{background:#1e1e1e;border-radius:10px;padding:10px 12px;margin:8px 0}
.good{color:#6fcf8a}.meh{color:#e0b35a}.bad{color:#e07a7a}.none{color:#888}
table{width:100%;border-collapse:collapse;font-size:13px}td{padding:5px 4px;border-top:1px solid #2a2a2a;vertical-align:top}
textarea,input{width:100%;box-sizing:border-box;background:#111;color:#eee;border:1px solid #333;border-radius:8px;padding:8px;font-size:15px}
.btn{background:#5d4a2e;color:#fff;border:0;border-radius:8px;padding:10px 14px;font-size:15px;margin:6px 6px 0 0}
.btn.gray{background:#333}.btn.red{background:#7a2e2e}
#status{position:fixed;left:12px;right:12px;bottom:10px;background:#262626;border-radius:8px;padding:8px 12px;display:none}
.sel{outline:2px solid #5d4a2e}
</style></head><body>
<nav><button onclick="tab(0)" class="on">Doing</button><button onclick="tab(1)">Questions</button><button onclick="tab(2)">Updates</button><button onclick="tab(3)">Account</button></nav>
<div id="now"></div><div id="t0"></div><div id="t1" hidden></div><div id="t2" hidden></div><div id="t3" hidden></div>
<div id="status"></div>
<script>
let T=localStorage.getItem('hdi_token')||'';const qp=new URLSearchParams(location.search);if(qp.get('t')){T=qp.get('t');localStorage.setItem('hdi_token',T);history.replaceState({},'',location.pathname)}let SC=null,selQ=null,selR=null;
function tab(i){document.getElementById('now').hidden=(i!==0);for(let k=0;k<4;k++){document.getElementById('t'+k).hidden=(k!==i);document.querySelectorAll('nav button')[k].className=k===i?'on':''}if(i===3)account();if(i===2)upd();}
function say(m,ok){const s=document.getElementById('status');s.textContent=m;s.style.display='block';s.style.color=ok===false?'#e07a7a':'#6fcf8a';setTimeout(()=>s.style.display='none',6000)}
function needTok(){if(!T){T=prompt('Enter the app token (data/hook_state/owner_phone_token.txt on the desktop)')||'';localStorage.setItem('hdi_token',T)}return T}
async function api(path,body){const h={'Content-Type':'application/json','X-Token':needTok()};const r=await fetch(path,{method:body?'POST':'GET',headers:h,body:body?JSON.stringify(body):undefined});const j=await r.json();if(!r.ok){say(j.error||'error',false);throw new Error(j.error)}return j}
function esc(s){return (s==null?'':String(s)).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
async function load(){SC=await api('/api/state');doing();questions();nowp();}
async function nowp(){try{const n=await api('/api/now');const age=n.heartbeat_minutes_ago;const col=age==null?'none':(age<20?'good':(age<120?'meh':'bad'));let h=`<div class="card"><b>Now</b> <span class="${col}">· last heartbeat ${age==null?'unknown':age+' min ago'}</span>${n.latest_update?`<div class=small style="margin-top:6px">${esc(n.latest_update.stamp)} · ${esc(n.latest_update.kind)}: ${esc(n.latest_update.text)}</div>`:''}<details style="margin-top:6px"><summary class=small>current position (from STATUS.md)</summary><div class=small>${esc(n.position).replace(/\n/g,'<br>')}</div></details><details><summary class=small>last ledger entries</summary><div class=small>${n.ledger_tail.map(esc).join('<br><br>')}</div></details></div>`;document.getElementById('now').innerHTML=h}catch(e){}}
function doing(){const o=SC.scorecard.overall,fi=SC.scorecard.fidelity;let h=`<div class="card"><b>${o.n_clearly_better} of ${o.n_abilities_scored}</b> abilities are clearly better than a simple rule. <b>${fi.pinned} of ${fi.organs_total}</b> building blocks copy the brain's math exactly; ${fi.stand_ins} are stand-ins still being replaced.</div>`;
h+=`<h2>The short version</h2><div class="card">${esc(SC.scorecard.sections['THE SHORT VERSION']||'').replace(/\n/g,'<br>')}</div>`;
h+=`<h2>What changed lately</h2><div class="card small">${esc(SC.scorecard.sections['WHAT CHANGED LATELY']||'').replace(/\n/g,'<br>')}</div>`;
h+='<h2>Every ability</h2><table>';let g='';for(const r of SC.scorecard.capabilities){if(r.group!==g){g=r.group;h+=`<tr><td colspan=2><b>${esc(g)}</b></td></tr>`}const cls=r.model==null?'none':(r.ci_sep?'good':(r.floor!=null&&r.model<=r.floor?'bad':'meh'));h+=`<tr><td>${esc(r.name)}${r.headline?' <span class=small>(headline)</span>':''}<div class=small>${esc(r.how_well)} · ${esc(r.trend)} · ${esc(r.fidelity)}</div></td><td class="${cls}">${esc(r.verdict)}</td></tr>`}
h+='</table>';document.getElementById('t0').innerHTML=h}
function questions(){const qs=SC.scorecard.questions_for_owner||[],rv=(SC.scorecard.problems||{}).in_review||[];let h='<h2>Questions for you ('+qs.length+')</h2>';
if(!qs.length)h+='<div class="card small">Nothing is waiting on you right now.</div>';for(const q of qs){h+=`<div class="card ${selQ===q.id?'sel':''}" onclick="selQ='${esc(q.id)}';questions()"><b>${esc(q.id)}</b> ${esc(q.question)}${selQ===q.id?`<p><b>What is waiting on it</b><br>${esc(q.why)}</p><p><b>My recommendation</b><br>${esc(q.rec)}</p>`:''}</div>`}
h+=`<textarea id="ans" rows=3 placeholder="Your answer to the selected question"></textarea><button class="btn" onclick="sendAns()">Send answer</button>`;
h+='<h2>Finished work waiting for your verdict</h2>';if(!rv.length)h+='<div class="card small">Nothing waiting.</div>';for(const p of rv){h+=`<div class="card ${selR===p.slug?'sel':''}" onclick="selR='${esc(p.slug)}';questions()">${esc(p.title)}</div>`}
h+=`<button class="btn" onclick="done()">Mark selected as DONE</button>`;
h+=`<h2>A note for the strategy session</h2><textarea id="note" rows=3 placeholder="Anything you want read at the start of the next turn"></textarea><button class="btn" onclick="sendNote()">Save note</button>`;
document.getElementById('t1').innerHTML=h}
async function sendAns(){const t=document.getElementById('ans').value.trim();if(!selQ||!t){say('Pick a question and type an answer first.',false);return}const j=await api('/api/answer',{id:selQ,text:t});say(j.message);load()}
async function done(){if(!selR){say('Select a finished piece of work first.',false);return}const j=await api('/api/mark_done',{slug:selR});say(j.message);load()}
async function sendNote(){const t=document.getElementById('note').value.trim();if(!t){say('Type a note first.',false);return}const j=await api('/api/note',{text:t});say(j.message);document.getElementById('note').value=''}
async function upd(){const j=await api('/api/updates');let h='<h2>Updates</h2>';if(!j.updates.length)h+='<div class="card small">No updates posted.</div>';for(const u of j.updates.slice().reverse()){h+=`<div class="card"><span class=small>${esc(u.stamp)} · ${esc(u.kind)}</span><br>${esc(u.text)}</div>`}document.getElementById('t2').innerHTML=h}
async function account(){const a=await api('/api/account');const c=a.current;let h=`<h2>Desktop Claude Code login</h2><div class="card"><b>${esc(c.email||'(none)')}</b><div class=small>${esc(c.org||'')} · ${esc(c.plan||'')}<br>access token until ${esc(c.access_expires)} · refresh until ${esc(c.refresh_expires)}<br>VS Code Claude processes running: ${a.claude_processes.length}</div></div>`;
for(const n of ['work','private']){const p=a.profiles[n];h+=`<div class="card"><b>${n}</b> ${p?`— ${esc(p.email)} <span class=small>(${esc(p.org||'')}; saved ${esc(p.saved_at)}; refresh until ${esc(p.refresh_expires)})</span>${p.is_current?' <span class=good>current</span>':''}`:'<span class=small>— not saved yet</span>'}<br><button class="btn gray" onclick="acct('save','${n}')">Save current login as ${n}</button>${p?`<button class="btn" onclick="acct('switch','${n}')">Switch to ${n}</button>`:''}</div>`}
h+=`<div class="card small">Switching rewrites the saved login files; processes already running keep the old login until restarted.</div><button class="btn red" onclick="if(confirm('End the VS Code extension\\'s Claude processes now? Any running conversation in VS Code stops; you then reload the VS Code window.'))acct('end','')">End VS Code Claude processes</button>`;
document.getElementById('t3').innerHTML=h}
async function acct(op,name){const j=await api('/api/account/'+op,{profile:name});say(j.message);account()}
load().catch(e=>say('Could not load: '+e.message,false));
</script></body></html>"""


# ------------------------------------------------------------------------------------------------------------- server
class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, obj, ctype="application/json"):
        body = (json.dumps(obj) if ctype == "application/json" else obj).encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self.end_headers()
        self.wfile.write(body)

    def _auth(self) -> bool:
        return self.headers.get("X-Token", "") == token()

    def log_message(self, fmt, *args):  # quiet
        pass

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        try:
            if path == "/":
                return self._send(200, PAGE, "text/html")
            if path == "/api/state":
                return self._send(200, {"scorecard": scorecard(), "ts": datetime.now().isoformat(timespec="seconds")})
            if path == "/api/updates":
                return self._send(200, {"updates": updates()})
            if path == "/api/now":
                return self._send(200, now_panel())
            if path == "/api/account":
                if not self._auth():
                    return self._send(401, {"error": "token required"})
                return self._send(200, account_state())
            return self._send(404, {"error": "not found"})
        except Exception as e:
            return self._send(500, {"error": "%s: %s" % (type(e).__name__, e)})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if not self._auth():
            return self._send(401, {"error": "token required"})
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            if path == "/api/mark_done":
                return self._send(200, {"message": mark_done(body.get("slug", ""))})
            if path == "/api/answer":
                return self._send(200, {"message": answer_question(body.get("id", ""), body.get("text", ""))})
            if path == "/api/note":
                return self._send(200, {"message": add_note(body.get("text", ""))})
            if path == "/api/account/save":
                return self._send(200, {"message": save_profile(body.get("profile", ""))})
            if path == "/api/account/switch":
                return self._send(200, {"message": switch_profile(body.get("profile", ""))})
            if path == "/api/account/end":
                return self._send(200, {"message": end_claude_extension_processes()})
            return self._send(404, {"error": "not found"})
        except Exception as e:
            return self._send(400, {"error": "%s: %s" % (type(e).__name__, e)})


def serve(host: str, port: int):
    srv = ThreadingHTTPServer((host, port), Handler)
    print("owner phone app: http://%s:%d   token file: %s" % (host, port, TOKEN_PATH), flush=True)
    print("PAIRING LINK (open once on the phone; it keeps the token): http://%s:%d/?t=%s" % (host, port, token()), flush=True)
    srv.serve_forever()


def self_test() -> int:
    host, port = "127.0.0.1", 8799
    srv = ThreadingHTTPServer((host, port), Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    time.sleep(0.3)
    base = "http://%s:%d" % (host, port); tok = token(); fails = 0
    def get(p, auth=False):
        req = urllib.request.Request(base + p, headers={"X-Token": tok} if auth else {})
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read()
    def post(p, body, auth=True):
        req = urllib.request.Request(base + p, data=json.dumps(body).encode(), method="POST",
                                     headers={"Content-Type": "application/json", **({"X-Token": tok} if auth else {})})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")
    s, b = get("/"); print("page", s, len(b)); fails += s != 200 or b"hd-instrument" not in b
    s, b = get("/api/state"); j = json.loads(b); print("state", s, "capabilities", len(j["scorecard"]["capabilities"])); fails += s != 200
    s, b = get("/api/updates"); print("updates", s, len(json.loads(b)["updates"])); fails += s != 200
    s, b = get("/api/now"); j = json.loads(b); print("now", s, "heartbeat_min", j["heartbeat_minutes_ago"], "ledger", len(j["ledger_tail"])); fails += s != 200 or not j["position"]
    s, _ = post("/api/note", {"text": "x"}, auth=False); print("unauth POST ->", s); fails += s != 401
    s, b = get("/api/account", auth=True); j = json.loads(b); print("account", s, "current email set:", bool(j["current"]["email"]), "processes:", len(j["claude_processes"])); fails += s != 200
    s, j = post("/api/mark_done", {"slug": "../evil"}); print("bad slug ->", s); fails += s != 400
    s, j = post("/api/account/switch", {"profile": "nope"}); print("bad profile ->", s); fails += s != 400
    srv.shutdown()
    print("SELF-TEST", "PASS" if not fails else "FAIL (%d)" % fails)
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1", help="bind address (use your Tailscale/LAN address for the phone)")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    serve(a.host, a.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
