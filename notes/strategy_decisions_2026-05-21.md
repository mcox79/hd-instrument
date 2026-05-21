# Strategy session — decision log

Owner: Strategy session. One entry per cycle. META reads to audit coherence.

## Cycle 1 — 2026-05-21 cold start (~08:00)

### What I observed

- `MEMORY.md` and all linked feedback / project / reference files. No
  surprises; existing protocols apply (no-smoke, value-not-competition,
  multi-probe for memory claims, cap-map update protocol, etc.).
- `substrate_capability_map.md` (mtime 2026-05-21 07:27) is current
  through v11. v11 ended with a retraction batch (soft-trace calibration,
  counterfactual=1.00 tautology, Yonelinas dual-process queued for proper
  re-test).
- `data/session_events.jsonl` on remote (local copy stale at 2026-05-19).
  Last `experiment_outcome` event: 2026-05-21T07:27:02 —
  `wave14yonelinas_roc_v2` mode=full → `YONELINAS_PURE_FAMILIARITY`
  (z-slope=1.11, retraction confirmed).
- `data/needs_verdict.json` (remote) shows 50 experiments completed with
  metrics but without `experiment_outcome` events emitted. Many were
  narratively absorbed by user-driven cap_map updates v9-v11. Three I
  inspected directly via metrics.json:
  - `wave14walsh_peaks_extended` — recall=1.0 at every K in {50..4000}
  - `wave14g_acf K=8192/12288` — both 100% recovery at K/N=2.0 and 3.0
  - `wave14counterfactual_chain` — fidelity=1.0 (confirms tautology;
    same retracted claim as v11)
- `notes/experiment_dev_blocker.md` (mtime 07:57) — Experiment Dev is
  explicitly waiting for `notes/active_priorities.md` (absent until now).
- `notes/meta_audit_2026-05-21.md` (mtime 07:57) — META noted the same
  absences (active_priorities.md, dashboard snapshot, session prompts).
- `notes/next_experiments_recommendations.md` (mtime 2026-05-20 23:26) —
  legacy synthesis-session file; carries useful retraction history but
  is NOT the active_priorities.md the charter specifies for this session.

### What I decided

1. **Updated `substrate_capability_map.md` to v12** (atomic write + commit
   + scp). Three triggers:
   - Yonelinas dual-process: ❌ Closed (event-logged trigger, kill switch
     from v11 fires). The promotion to ✅ in v10 is retracted.
   - Walsh-peak forensics: evidence list extended from "low-K only" to
     "all K in [50..4000] at recall=1.0" (metrics.json strengthens the
     existing ✅ row).
   - ACF rescue: evidence list extended to K/N=2.0 and K/N=3.0 at 100%
     (≥3× the vanilla cliff, ceiling not yet located).
2. **Created `notes/active_priorities.md`** (NEW; unblocks Experiment
   Dev). Top 3 bets:
   - Bet 1: ICL saturation curve at extended N (closes Tier-S #1)
   - Bet 2: GDPR/surgical erase v3 (anti-Hebbian and selective anneal
     both closed by Mirage tests; new mechanism needed)
   - Bet 3: Substrate forensics extended (random-key iterative
     charge-flipping for the high-K gap)
   Plus retracted list, open research questions, open experiment requests.
3. **Did NOT touch** the 47 needs_verdict.json items that lack
   `experiment_outcome` events. Per cap_map protocol, the trigger is the
   events log. Strategy will integrate as event_outcomes land. Flagged
   this gap in v12 update for Visibility's awareness.

### Why (linking to evidence)

- Yonelinas retraction: v11 explicitly framed `wave14yonelinas_roc_v2` as
  the kill switch ("If z-slope ~ 1, it confirms the earlier 'validation'
  was a codebook-size artifact and that claim also gets retracted").
  Full-mode landed at z-slope=1.11. The kill criterion fires. Not
  retracting would violate `feedback_no_smoke` and `feedback_step_back_eval`.
- Walsh-peak / ACF strengthening: v9 and v8 framings were conservative.
  Extended sweeps now show the capabilities hold across the full tested
  range. Per cap_map protocol "Update evidence lists with new experiment
  names" — allowed change.
- Bet 2 framing: two independent negatives this week
  (`wave14d_query_side_integration` 93% leak; `wave14g_erase_under_replay`
  100% replay-erased-visit) + Mirage failures in both anti-Hebbian and
  selective-anneal recipes (`wave14p_erase_multiprobe`,
  `wave14anneal_selective`) mean the next attempt needs a different
  mechanism family, not a parameter tune. Per `feedback_rehabilitation_after_rejection`,
  I listed several axis-combination rescues (Kerdock-structured,
  iterative charge-flipping, ROME-style, per-fact orthogonal-subspace)
  before declaring the capability structurally closed.
- Active priorities length (162 lines) overshoots the charter target
  (50-100). Kept because of the substantial retraction list and
  experiment request set; willing to compress next cycle if META flags it.

### Open items / handoffs

- **Visibility session**: dashboard snapshot file is absent. Several
  downstream sessions reference it. Strategy is unblocked but operating
  on direct remote SSH reads instead.
- **Research session**: see Bet 2's R1 question (which GDPR-erase
  mechanism family) and R2/R3/R4 in active_priorities.md.
- **Experiment Dev**: blocker should be resolved as of this cycle. E1
  through E5 listed in active_priorities.md with multi-probe criteria.
- **Queue Health**: 50 unprocessed needs_verdict items + `session_events.jsonl`
  appears to not be receiving event_outcomes for most experiments. May
  warrant a check for whether the events-emission path is wedged.

### Next cycle plan

- Re-read session_events.jsonl for new outcomes; check
  `wave14d_icl_via_pool_v3_scaling` if it lands.
- Re-read research notes (synthesis output from Research session, if any).
- Audit whether Bet 2's R1 mechanism question has progressed (Research
  output expected).
- If 3+ needs_verdict items get backfilled with event_outcomes, integrate
  them into cap_map v13.

---

## Cycle 2 — 2026-05-21 ~08:23 (event-driven wake)

PROT compliance this cycle: implemented PROT-002 (wrote
`notes/session_prompts/session_1_strategy.md`); PROT-001 already satisfied
in cycle 1 (active_priorities.md exists as real content, not stub — counts
per protocol intent).

### What I observed

- Other sessions came online between 08:09 and 08:16. New artifacts:
  - `notes/active_protocols.md` (META, 08:13) — two new protocols active
  - `notes/meta_decisions_2026-05-21.md` (META, 08:14) — covered user pushback
    on coordination burden; both PROT-001 and PROT-002 are self-implementing
    by sessions reading active_protocols.md (no user mediation)
  - `notes/visibility_decisions_2026-05-21.md` (Visibility, 08:10) — monitor
    is live; PID 4840 polling at 30s cadence; snapshot at
    `data/local_dashboard_snapshot.json`
  - `notes/queue_health_log.md` (Queue Health, 08:16) — both runners healthy
    idle; no pending experiments
  - `notes/session_prompts/charter.md` + `session_6_meta.md` (META) — prompt
    snapshot infra exists; PROT-002 expects sessions 1-5 to drop their own
- Dashboard snapshot at 08:20:36 confirms: both queues idle, no pending,
  recent_verdicts top-10 includes the Yonelinas retraction and several
  walsh_peaks variants. No new experiment outcomes since cycle 1.
- `experiment_dev_blocker.md` still present (mtime 07:57, before my
  active_priorities.md commit at 08:06). Expecting Experiment Dev to clear
  it on its next cycle.

### What I decided

1. **PROT-002**: dropped `notes/session_prompts/session_1_strategy.md`
   (verbatim session-specific prompt body).
2. **PROT-001**: already satisfied — `notes/active_priorities.md` exists
   with real content from cycle 1, not a stub. The protocol's stated
   trigger ("first cycle in which your primary output file does not
   exist") doesn't apply on subsequent cycles. Marked as satisfied; no
   additional stub.
3. **Did NOT update cap_map v13.** Inspected `wave14cpu_walsh_peaks_N_sweep`
   metrics.json (landed 07:35, predates my v12 commit). Data shows
   recall=1.0 across N ∈ {4096, 8192, 16384} × K/N ∈ {0.02..0.7} — 18
   cells, all 1.0. This is a strengthening / N-invariance finding for
   the WHT-forensics row, but the row is already at ✅ and v12 already
   cites strengthening evidence. No new state change. Will roll into v13
   alongside other accumulation next cycle.
4. **Noted analyzer anomaly**: both `wave14walsh_peaks_extended` and
   `wave14cpu_walsh_peaks_N_sweep` are labeled `PEAKS_FORENSICS_LIMITED`
   with msg "Recall=100.00% at low K. High-K test inconclusive." — but
   the per-K data shows recall=1.0 at EVERY tested K, including high K.
   Verdict label disagrees with data. Not a Strategy problem to fix
   (Experiment Dev / verifier owns analyzer logic), but flagging for
   downstream awareness so the cap_map narrative isn't anchored on a
   wrong label.

### Why

- PROT-002: META's protocol is explicit and one-shot. Cheap to comply.
- Not updating cap_map: the protocol's trigger requires a new event_outcome
  in session_events.jsonl OR a new wave14*_research.md note. The walsh N-sweep
  metrics.json is older than my v12 commit; it was already implicitly
  available evidence when I wrote v12. Re-writing the cap_map for evidence
  I should have caught the first time isn't a state change — it's
  housekeeping, and the protocol forbids housekeeping rewrites.
- Honest framing: I missed the N-sweep on cycle 1. That's a real misstep
  (cycle 1 should have inspected all top-mtime metrics.json files, not
  just the ones flagged by event_outcomes). Noting it here so META can
  audit; will be more thorough on cycle 3.

### Open items / handoffs

- **Experiment Dev**: blocker should clear; active_priorities.md is live.
  Watching for `wave14d_icl_via_pool_v3_scaling` (Bet 1) or any
  GDPR-erase v3 candidate (Bet 2).
- **Visibility / Queue Health**: monitor + heartbeat infra is live; no
  Strategy ask.
- **Research**: still nothing from Research session yet (no
  `notes/research_*` from today). R1 (GDPR-erase mechanism family) and
  R4 (50-hop reasoning protocol) are the highest-leverage drills in
  active_priorities.md.

### Next cycle plan

- Re-check dashboard snapshot for new verdicts.
- Verify Experiment Dev cleared its blocker and queued a prereg.
- If Research drops a synthesis note, integrate.
- Inspect ALL recent metrics.json (top 10 by mtime), not just the ones
  with event_outcomes — to avoid the cycle 1 miss recurring.
- If 2+ strengthening evidence points accumulate, roll cap_map to v13
  with consolidated update.
