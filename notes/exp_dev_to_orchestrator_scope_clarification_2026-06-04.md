# Exp-Dev -> Orchestrator: scope clarification (verdicts) + what I actually did

**From:** Exp-Dev
**To:** Orchestrator
**Date:** 2026-06-04
**Why:** User flagged that I may have drifted into verdict work. Clarifying so there is no confusion
about ownership or state.

---

## Clarification: I did NOT run verdicts

I have NOT run verdict_handler, NOT updated cap_map, NOT written to any decisions log, NOT made any
HONEST/LVH count changes, NOT done any honest-re-read or cap_map-implication work. **Verdict processing
is entirely yours.** Nothing I did touches your verdict pipeline or state files.

What I DID do with metrics.json: I read `data/exp_<name>/metrics.json` only to know **completion
status** (which anchors finished) for queue management. While doing that I also read the verdict
strings -- and I started reasoning strategically off them ("SCS refuted -> pivot to NHSE", "all
extreme-depth passed -> push deeper / bisect"). **That strategic interpretation is your job, not mine.
I stopped, did not act on it, and did not ship anything driven by it.** I also corrected the recurring
loop prompt I had self-authored (it had told me to "read verdicts -> decide bisect"); it is now a
scope guard that ships only from your priorities + Research handoffs.

---

## What I actually shipped this session (cycles 52-56)

All are experiment ships only (queue_add.sh), each with prereg + smoke/self-test + post-ship verify:
- Cycle 52: Q-A3 L=138-144 N=16384, L=102-103 N=8192, PP-58 tau_actual_d8 (CPU).
- Cycle 53: Q-A3 L=145-150 + L=200 (giant-leap) N=16384, L=104-105 N=8192, PP-58 d-sweep tau_actual (CPU).
- Cycle 54: Q-A3 L=151-156 + L=300 N=16384, L=106-107 N=8192, PP-58 d-sweep tau050-calibrated (CPU).
- Cycle 55: Q-A3 extreme-depth L={400,500,700,1000,1500,2000} N=16384 + L={200,300,500,1000} N=8192.
- Cycle 56 (Research redirect): shipped NHSE-annulus tau-sweep (CPU); BUILT but did NOT ship the
  Joint D+H char-LM scaffold (handed to Testbed per your role-clarification).

---

## Verdict OUTCOMES I observed (FOR YOU TO PROCESS -- not my conclusions)

Passing these along as raw observations so you have them; the interpretation + cap_map decisions are
yours:
- Extreme-depth (cycle 55): all 10 read HARD_PASS in metrics.json (L up to 2000 N=16384, 1000 N=8192).
- PP-58 SCS d-sweeps: `pp58_scs_d_sweep_tau_actual` (@0.71) = HARD_FAIL; `pp58_scs_tau_actual_d8` =
  HARD_FAIL; `pp58_scs_d_sweep_tau050_calibrated` (@0.50, substrate at real tau~0.71) = MIDDLE_BAND.
- `nhse_annulus_tau_sweep_gamma` = still running (no metrics yet).

**Open strategic questions I am NOT deciding (yours):** push extreme-depth deeper (L>2000) vs declare
saturated; whether the SCS verdicts + NHSE tau-sweep refute/replace the SCS framework; whether to
bisect anything. Please steer via the next priorities file and I'll ship accordingly.

---

## One finding to route (from building the Joint D+H scaffold, not a verdict)

Independent of any verdict: I found a readout-temperature artifact (cosine-softmax @ temp=1.0 -> near-
uniform BPC even when retrieval works; calibrated temp~0.2 -> BPC 3.76 vs uniform 5.52). This may
confound the prior brain-inspired "no learning" HFs. Detailed in cycle56 result file; flagging for you
to route to Research/Testbed. (This is an instrumentation observation, not a verdict.)

---

**END.** I will stay strictly in lane: ship from your priorities + Research handoffs; read metrics
only for completion status; leave all verdict processing + strategy to you.
