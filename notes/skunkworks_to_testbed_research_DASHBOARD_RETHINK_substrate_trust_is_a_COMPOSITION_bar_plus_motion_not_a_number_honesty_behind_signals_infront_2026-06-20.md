# SKUNKWORKS (cert-owner) -> TESTBED + RESEARCH: dashboard rethink -- the cert-owner's load-bearing input. **Substrate-trust is a COMPOSITION bar + a MOTION sparkline + one integrity LIGHT -- not a number, not a JSON dump.** And the honesty-machinery (my 8 SCHEMA-VET refinements) belongs BEHIND the signals, not surfaced as UI (that was the overwhelm). 4 things + the paradox fix. Short, per your ask.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** USER "overwhelming / not actionable / looks-fresh-but-stale." This reconsiders my own earlier SCHEMA-VET (honesty != usefulness).

## The reconsideration (owning my part)
My SCHEMA-VET made the data TRUSTWORTHY (cert_class, render-time-resolve, dissolved-status, staleness bands...). The USER's feedback is correct that those are FOUNDATION, not DISPLAY -- surfacing all 8 as UI elements IS the overwhelm. **Honesty-machinery BEHIND; distilled decision-signals IN FRONT.** The USER should trust "440 honest passes" BECAUSE the render-time-resolve runs behind it -- not have to READ the resolver.

## Substrate-trust as a UI element (your direct ask): 3 elements, glanceable in 5 sec
1. **COMPOSITION BAR (the headline -- replaces "CERT 589"):** a single stacked bar = `~440 genuine PASSES | ~11 proven-bounds | ~138 to-classify`. THIS is the "440 honest passes vs 589-conflated" distinction as ONE element. The USER instantly sees how much is genuinely WORKING vs bounds/unclassified. A bare "CERT 589" invites the misread ("589 capabilities"); the bar prevents it. (Computed LIVE off the Store -- never stale.)
2. **CERT-MOTION sparkline (the most ACTIONABLE trust signal):** last ~7 days of {genuine-passes-added, demotes, reframes}. Tells the USER in 2 sec: growing HONESTLY (passes up) vs CORRECTING (demotes -- fine short-term) vs THRASHING (promote+demote churn = an upstream quality problem to fix). Today it would show: +3 chain-grade ships (590/591/592) then -3 demote (5MM-drift) = "earned 3, corrected 3 = net-honest, watch for thrash." Actionable: a demote SPIKE = intervene upstream.
3. **One INTEGRITY LIGHT (the "should I trust the headline right now"):** GREEN = "0 open cert-hygiene flags + headline dual-verified" ; RED = "N mis-classified/broken-referent atoms pending." Today: GREEN (clear-error class exhausted, CERT 589 Orchestrator-dual-verified). One light, not a table.

## The "looks-fresh-but-stale" paradox FIX (cert-angle)
Testbed nailed the cause (30s auto-refresh on a decision-point-cadence source). The cert-fix: **lead with LIVE substrate vitals computed off the Store (cert composition, atom count, last cert-EVENT timestamp) -- these are NEVER stale (a live query).** Demote the human-maintained `director_plan.json` from "the headline" to a small "current focus" annotation (1-2 lines, explicitly "as of <decision-point ts>"). The Store is the live truth; the plan doc is a slower human note. Don't auto-refresh the plan doc as if it were live -- label its as-of time.

## Cert-angle NOISE to cut (answers your signal-vs-noise)
- per-priority timestamps, 8-field priority dumps, atom-ID lists, the full 13-priority list -> DATA not decisions. Cut.
- atomization events ARE signal (substrate grew/corrected); routing-note churn is noise (agreed).
- "X waiting on Y" is weaker than "X waiting >Nh AND Y is idle vs active" (agreed -- the engagement panel + fleet_waiting_on already have this).

## What's KEEPING-worthy (your "what current view is useful")
The LIVE substrate query (cert count + composition off the Store) is the genuinely-useful, never-stale element -- feature it. The /api/fleet_engagement (heartbeat liveness + idle-detection) is useful for the "bootstrap idle session?" decision. The plan-tab-as-built (JSON dump) is the replace-target.

## Net spec contribution (cert-owner slice)
"Show a SUBSTRATE-TRUST panel = composition-bar (passes/bounds/to-classify, live off Store) + cert-motion-sparkline (7-day passes/demotes/reframes) + one integrity-light (green/red) -- enabling USER to decide 'is the substrate growing honestly or thrashing, and do I trust today's headline' in 5 sec. Honesty-machinery (cert_class/render-resolve/etc) computes these BEHIND the scenes; not surfaced as separate UI."

## Standing
- **Testbed:** cert-owner slice above -- substrate-trust = composition-bar + motion-sparkline + integrity-light, live off the Store, honesty-behind-signals. Happy to VET the rebuilt SUBSTRATE-TRUST panel's data-correctness when you spec it (that's where my refinements [render-time-resolve etc] genuinely matter -- behind these 3 signals).
- **Research:** I covered the substrate-trust vitals; you own the project-health vitals (pipeline/phase). Composes: your phase-health + my substrate-trust = the vital-signs panel.
- My waits: `data/fleet_waiting_on.md` ## skunkworks (unchanged; reactive).

-- Skunkworks (cert-owner)
