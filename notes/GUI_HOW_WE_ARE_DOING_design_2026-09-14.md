# The "how we're doing" view -- research note and design record (2026-09-14)

**Owner's brief:** *"update the 'how we're doing' tab in the gui to be 1) more informative and less
like a list. Consider what it is we're working on and the full development plan... 2) I'd like this
tab to be kept updated -- can it reference a live doc that you work on in the normal course here?
3) I'd like this to survive the transition to the remote desktop... we should try and make sure that
the gui is compatible with remote to a tailscale machine."*

Files this produced: `notes/HOW_WE_ARE_DOING.md` (the live document), `tools/scorecard_gui.py`
(tab 1 rebuilt), `tools/how_we_are_doing_web.py` (the shared parser **and** the browser view).

---

## 1. What this view is actually for

Before any design: who reads it, what question do they arrive with, what do they do next?

- **Reader:** the owner, once or twice a day, often after being away for hours while agents landed
  work. Not looking for a number -- looking for *orientation*.
- **The question:** "where is this, is it moving, and is anything wrong?"
- **The decision it feeds:** whether to intervene (answer a question, hand out a problem, change the
  direction) or let it run.

That makes it a **status view**, not an analytics dashboard and not a report. The old tab answered a
different question -- "how does each of 36 abilities score" -- which is a *lookup* question, and a
table is the right shape for a lookup. It is the wrong shape for orientation, which is exactly the
"too much like a list" complaint. The fix is not to delete the table; it is to **stop leading with
it**.

## 2. What the literature and practice say

**(a) Overview first, details on demand.** Shneiderman's visual information-seeking mantra --
*overview first, zoom and filter, then details-on-demand* -- is the oldest and most directly
applicable rule here: the top of the screen carries the whole, and everything specific is one action
away rather than on screen.
[Shneiderman 1996, *The Eyes Have It*](https://www.cs.umd.edu/~ben/papers/Shneiderman1996eyes.pdf)

**(b) Progressive disclosure.** Nielsen's 1995 pattern: show the few things most people need, defer
the rest behind an explicit control. Current practice writeups describe the same three-tier shape for
dashboards -- *summary / context / detail* -- with three-to-five headline figures at the top, trend
in the middle, and granular tables behind a click.
[IxDF, *Progressive Disclosure*](https://ixdf.org/literature/topics/progressive-disclosure) ·
[UXPin, *What is progressive disclosure*](https://www.uxpin.com/studio/blog/what-is-progressive-disclosure/)

**(c) A point number is nearly meaningless; history is the cheapest context.** Few's core argument in
*Information Dashboard Design* is that a measure of current activity needs context, and that the most
useful context is what came before it. His sparkline guidance adds the necessary corrective: a
sparkline carries **no magnitude** of its own, so label the first and last (or lowest and highest)
values, or band the normal range.
[Few, *Information Dashboard Design*](https://public.magendanz.com/Temp/Information%20Dashboard%20Design.pdf) ·
[Few, *Best Practices for Scaling Sparklines*](https://www.perceptualedge.com/articles/visual_business_intelligence/best_practices_for_scaling_sparklines.pdf) ·
[Few, *Introducing Bandlines*](https://www.perceptualedge.com/articles/visual_business_intelligence/introducing_bandlines.pdf)

**(d) Status pages: one overall banner, then per-component status, then a timestamped timeline.**
The convention that a whole industry converged on is worth copying wholesale: a clear at-a-glance
banner for the overall state; each component listed with its own status, with anything unhealthy
visually pulled out; and a dated incident timeline underneath.
[Atlassian, *Show service status with components*](https://support.atlassian.com/statuspage/docs/show-service-status-with-components/) ·
[Atlassian, *Incident communication*](https://www.atlassian.com/incident-management/tutorials/incident-communication)

**(e) "Where are we on the plan" wants a stepper, not a list.** A horizontal progress stepper is the
standard answer to *where am I in a multi-stage process*; it makes position and what-comes-next
visible at a glance, and the guidance is to keep it to roughly 3-7 stages before cognitive load
outweighs the benefit. Our chain is exactly 7.
[eBay Playbook, *Progress stepper*](https://playbook.ebay.com/design-system/components/progress-stepper) ·
[UXPin, *Progress tracker design*](https://www.uxpin.com/studio/blog/design-progress-trackers/) ·
[Eleken, *32 stepper UI examples*](https://www.eleken.co/blog-posts/stepper-ui-examples)

**(f) Communicating uncertain numbers.** Spiegelhalter and colleagues: use plain language, prefer
**frequency formats with an explicit denominator** ("63 in 100", not "0.6344"), give a point estimate
*with* its range, and admit what is not known -- and the evidence is that doing so does **not** cost
you trust.
[Freeman et al. 2019, *Communicating uncertainty about facts, numbers and science*](https://royalsocietypublishing.org/rsos/article/6/5/181870/95102/Communicating-uncertainty-about-facts-numbers-and) ·
[van der Bles et al. 2020, PNAS](https://www.pnas.org/doi/10.1073/pnas.1913678117) ·
[Spiegelhalter, *Risk and Uncertainty Communication*](https://regulation.org.uk/library/2017-Spiegelhalter-Risk_and_Uncertainty_Communication.pdf)

## 3. The design chosen

Reading order, top to bottom. Each band is there for a named reason.

| Band | What it shows | Why, and from which rule |
|---|---|---|
| **Goal** (small, grey, standing) | The owner's own restatement: a fully functional glass-box AI; reading comprehension is the current front; the board is the instrument, not the objective. | Every number below is otherwise read as the objective. This is the standing frame, so it is present but quiet. |
| **Position** (one big sentence) | The single honest answer to "how are we doing". | (a) overview first; (d) the status banner. One sentence, because if it needs two the writer has not decided what the answer is. |
| **Four figures** | board `63 in 100` with an up/down arrow; what simple rules get on the same questions; how many parts of the board clearly beat them; how many test questions. | (b) three-to-five headline figures, no more. (f) frequency format with the denominator; the floor is shown *beside* the score because a score without its floor is not interpretable here. |
| **The chain** (7 stages, left to right) | word kinds -> word forms -> which word hangs off which -> who did what to whom -> helped/harmed -> who is who -> reasoning. Each with a status colour and **its own honest number**. Clicking one shows what it is in plain words. | (e) the stepper. This is the single biggest change: it replaces "36 abilities in a table" with "here is the pipeline, here is the rung that is weak, here is the front". It also makes the strategy visible -- the weak rung is *why* the work is where it is. |
| **The trend** | the board over the last 24 full checks, with the simple-rule floor as a dashed baseline, and the first and last values labelled. | (c) history is the context a point number lacks; label the ends because a sparkline carries no magnitude. |
| **What moved** (dated) | newest 3 always visible, the rest folded. | (d) the timestamped timeline. |
| **What is running / next / risks** | folded, with a preview line or two. | (b) progressive disclosure. "Risks and corrections" carries the retired figures -- it is the anti-embarrassment section. |
| **Every ability, measured** | the old 36-row table, **unchanged**, behind one line at the bottom. | Nothing is lost; it stops being the first thing. (a) details on demand. |

**Colour is used once, for one meaning**: stage status. `SOLID` green, `IMPROVING` blue,
`WEAK` amber, `NEXT FRONT` blue, `AT RISK` red, `NOT STARTED` grey. Nothing else on the tab is
coloured for decoration, so a colour always means "look here".

### Three honesty rules baked into the rendering

1. **Runs on different question sets are not joined.** `notes/BOARD_TREND.jsonl` mixes 11,218-question
   full boards with 9,300-question partial ones. Drawn naively that reads as a crash from 63 to 61
   and back -- a cross-population comparison, which the measurement bar forbids. Both views mark any
   run whose question count differs from the latest as a **hollow, disconnected** point, and say so
   in words underneath.
2. **Every number carries units in words.** "right 63 in 100", never `0.6344`.
3. **Stage numbers come from the ledger, not from recollection**, and the retired-figures list is
   rendered in "Risks and corrections" so a retired number cannot be quoted from this view.

### What I deliberately did not do

- No new dependency. Tkinter only; the browser view is standard library only. A charting library
  would have bought a nicer sparkline and cost an install on the desktop machine mid-move.
- No animation, no auto-scrolling, no live-tailing log pane: all three are expensive over RDP
  (see §5) and none answers the reader's question.
- Did not delete the ability table. It is the evidence behind the chain; hiding it would have traded
  one complaint for a worse one.

## 4. Keeping it current -- the live document

`notes/HOW_WE_ARE_DOING.md` is the single source. Both views parse it; neither view has content of
its own. It carries a 10-line `HOW TO KEEP THIS CURRENT` comment at the top (invisible in both
views) that states the contract:

> Per landing, edit at most three things: **the stage row that moved**, **one dated line at the top
> of WHAT MOVED**, and **WHAT IS RUNNING**.

That is a few lines per landing, which is the only cadence that survives. Everything expensive is
already generated: the ability table from `tools/scorecard.py`, the trend from
`notes/BOARD_TREND.jsonl`. The strategy session writes only the part that requires judgement.

The parser is strict on purpose, and the smoke test enforces it: the eight headings must be spelled
as they are, column 2 of the plan table must start with one of the six status words, and every stage
needs a number and a plain-words explanation. A renamed heading fails a test rather than silently
rendering an empty band.

## 5. Remote: the two paths, analysed

Over Tailscale there are two genuinely different situations, and they need different answers.

### Path A -- RDP into the desktop (the window itself)

Tkinter draws on the machine it runs on. Over Tailscale that means an RDP session into the desktop,
and the window is the *full* product: it is the only path with the answer box, Send note, Mark DONE
and Copy solver prompt. **Decisions stay here.** What was done for it:

- **No absolute path anywhere.** Both files resolve everything from `Path(__file__).resolve().parent.parent`.
  The repo has already moved once (`D:` -> `C:`) and moves again to the desktop; nothing in this tab
  will notice.
- **Narrow-window layout.** RDP sessions are frequently 1024-1280 logical pixels. The chain strip is
  one row at >= 980px and **wraps to two rows below that** (verified at 900 / 1024 / 1280 / 1600);
  every paragraph re-wraps to the actual width rather than to a hard-coded 1220.
- **Cheap redraws.** RDP ships bitmap deltas, so a static screen costs nothing and an animated one
  costs a lot. The tab refreshes on a 60-second timer and draws no animation. The sparkline is ~60
  canvas items, redrawn only on refresh or resize.
- **Scroll containment.** The mouse wheel is bound only while the pointer is over this tab's canvas,
  so it cannot steal scrolling from the treeviews on the other tabs (a common RDP annoyance where the
  wheel event lands on the wrong widget).
- **Clipboard still works.** "Copy solver prompt" uses the Tk clipboard, which RDP redirects.
- **Fonts.** Segoe UI is present on any Windows desktop; Tk falls back silently if not.
- Launch there exactly as here: `.venv/Scripts/python.exe tools/scorecard_gui.py`.

### Path B -- read it from a phone or laptop on the tailnet (the browser view)

RDP is heavy for "glance at it from the sofa". `tools/how_we_are_doing_web.py` serves the same
document as **one self-contained HTML page**:

```
.venv/Scripts/python.exe tools/how_we_are_doing_web.py                        # 127.0.0.1:8787, this machine only
.venv/Scripts/python.exe tools/how_we_are_doing_web.py --bind 100.91.12.42    # the desktop on the tailnet
```

then open `http://100.91.12.42:8787/` from any device signed into the tailnet -- or
`http://home:8787/` if MagicDNS is on.

**The tailnet as it stands today** (`tailscale status`, 2026-09-14): `home` = `100.91.12.42` is the
**desktop** (the machine the work moves to and where the server should run); `frameworkmpc` =
`100.124.176.29` is this laptop; `pixel-9a` = `100.107.178.7` is the phone, offline for some time.
After the move, run the server on `home` and read it from either of the others. If the addresses
change, `tailscale ip -4` on the desktop prints the one to pass to `--bind`.

- **Standard library only** (`http.server`), **no external asset of any kind** -- no CDN, no web
  font, no script tag; the self-test asserts that no `http://` or `https://` string survives into the
  page. It renders with the viewing device offline from the public internet.
- **Binds to loopback by default.** Exposure is opt-in, and `--bind` takes the *tailnet* address
  specifically rather than `0.0.0.0`, so it is reachable on the tailnet and not on the local LAN or
  any hotel wifi.
- **Security posture:** the tailnet is already private, authenticated and encrypted, so the page
  carries no login. It is also **read-only** -- there is no control on it that can change anything,
  which is the right split: glancing is remote, deciding is in the window.
- **Neater alternative if available:** leave the server on loopback and put
  `tailscale serve http://127.0.0.1:8787` in front of it. Tailscale then terminates TLS and does the
  identity check, and the app never binds to a routable address at all.
- **Windows Defender Firewall** may block the inbound connection on first use. If the page does not
  load from another device, allow the interpreter once:
  `netsh advfirewall firewall add rule name="how-we-are-doing 8787" dir=in action=allow protocol=TCP localport=8787`
  (run from an elevated prompt; delete it with the same command and `delete rule name=...` when the
  server is not in use). Prefer the `tailscale serve` route, which needs no firewall rule.
- **Phone layout:** single column below 760px, the stage strip stacks, 16px side gutters, and it
  follows the device's light/dark setting.
- `/doc.json` serves the parsed model if anything else ever wants it; `/healthz` returns `ok`.

### Why not make the whole GUI a web app?

Tempting, and it would make Path A unnecessary. Rejected for now on cost and risk: the window's other
three tabs write files (answers, notes, DONE verdicts, pasted solver results), and moving those to
HTTP means forms, CSRF, and a write path reachable from the network -- during the week of a machine
move. The cheap version delivers the 90% (reading) remotely today and leaves the 10% (deciding)
exactly where it already works. If the owner ends up using the page more than the window, porting
the questions tab is the next step, not a rewrite.

## 6. Self-tests

| Command | What it proves |
|---|---|
| `.venv/Scripts/python.exe tools/how_we_are_doing_web.py --self-test` | The document parses; all seven sections present; every stage has a known status word and a number; the page renders; **zero external assets and zero scripts**. No socket is opened. |
| `.venv/Scripts/python.exe tools/scorecard_gui.py --parser-smoke` | The same parse, from the GUI's side, **without opening a window** -- so it runs over ssh on a machine with no display. |
| `.venv/Scripts/python.exe tools/scorecard_gui.py --self-test` | Builds the whole window offscreen: the band shows the document's position line, the chain strip has one cell per stage, clicking a stage shows its detail, the trend canvas drew, all five folded sections open and close, the newest movements are visible unfolded, the 36-row table is intact, and the problems tab still copies a kickoff prompt. |

Result at the time of writing: all three pass (7 sections, 7 stages, 7 movements, 24 board runs of
which 16 comparable, 36 abilities, 10 open problems).

## 7. Honest risks in this work

- **The view is only as current as the document.** The window will render a two-week-old position
  sentence with complete confidence. The mitigation is the "last edited" stamp on the risks section
  and the three-line-per-landing contract -- not a guarantee.
- **I chose the seven stages.** They follow the FOCUS MAP in `notes/STATUS.md`, but the chain is a
  simplification of a system with ~90 building blocks. If the owner reads the strip as "seven
  components", that is a misreading this design invites. The "what this is" text on each stage is the
  defence.
- **The trend's hollow points are a compromise.** The correct thing is one line per population; the
  cheap thing is one line with the off-population runs broken out. I chose the cheap thing and
  labelled it. If partial boards become common, split the series properly.
- I did not test the page on an actual phone or over an actual Tailscale hop -- only on loopback.
  The responsive CSS and the bind flag are standard, but that last mile is unverified until the
  desktop move.
