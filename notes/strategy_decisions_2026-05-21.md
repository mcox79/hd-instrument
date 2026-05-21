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

---

## Cycle 3 — 2026-05-21 ~09:33 (in /loop, dynamic mode)

PROT compliance this cycle: PROT-001 and PROT-002 already satisfied in
prior cycles.

### What I observed

Big batch of new event_outcomes between cycle 2 (08:23) and cycle 3
(09:33). Five clean triggers + one published research note.

Event log (chronological):
- 08:25:42 `wave14d_icl_via_pool_v3_scaling` (Bet 1): `ICL_SATURATION_VALIDATED`
- 08:38:50 `wave14r_erase_orthkeys_v1` (Bet 2 v1): `STRUCT_KEYS_FIX_MIRAGE`
- 08:56:27 `wave14r_orthkeys_capsweep` (Bet 2 envelope): `CAPSWEEP_ROBUST`
- 09:10:51 `wave14t_multihop_v3` (E4): `MULTIHOP_DECAY_AT_50` (soft pass)
- 09:26:10 `wave14s_chargeflip_forensics_v1` (Bet 3): `CHARGEFLIP_FORENSICS_NO_GAIN`
- 09:29:18 `wave14u_multihop_envelope_v1` (E4 envelope): `ENVELOPE_NARROW_AT_LOW_NUM_FACTS`

Plus a Research-session publication:
- `notes/research_R1_GDPR_erase_candidates_2026-05-21.md` (08:20) —
  surveyed 4 mechanism families; recommended Variant 2A.i (Kerdock-coset
  + anti-Hebbian) with 75-90% predicted Mirage-pass probability. The
  Hadamard subcode v1 that Experiment Dev built is the optimistic-limit
  cleanest-falsifier of this family.

Plus user feedback memory: `feedback_two_experiments_per_cycle.md`
indexed in MEMORY.md — Experiment Dev should now build 2 per cycle if
hardware is idle.

### What I decided

1. **cap_map v13** (atomic write, commit, scp). Triggers above. Five
   capability moves:
   - Bet 1 ICL: ✅ stays, but evidence list extended with full envelope
     characterization through ICTX=16384
   - NEW ✅ row: "Mirage-grade selective erase on orthogonal-key
     substrate" (Memory primitives section)
   - GDPR-erase: ❌ in correlated-key arch → ✅ via orthogonal-key path
   - Edit-then-query Tier-1 KILLER: 🟡 → 🟢 partial (erase ✅, query-side
     integration still untested)
   - Bet 3 random-key chargeflip: 🔬 → ❌ at kill criterion
   - Multi-hop reasoning: ⚪ → 🟡 partial (1-hop ~0.93, 50-hop fails)
   - Walsh-peak N-sweep evidence added (cycle 1 miss rectified)
2. **active_priorities.md v2** (atomic rewrite). Top 3 bets pivoted:
   - "Recently resolved" lists Bet 1 ✅, Bet 2 ✅, Bet 3 ❌
   - Bet A (NEW): edit-then-query end-to-end pipeline (now buildable
     on top of orthogonal-key erase primitive)
   - Bet B (NEW): multi-task continual learning A→B→C→D
   - Bet C (NEW): Full Kerdock + snap for M > N dense-codebook regime
   - Open research routed: R4 (multi-hop rescue), R5 (Corpus-C design),
     R6 (Kerdock decoder implementation)
3. **Decision log this entry** explains the reasoning.

### Why

- Bet 1 + Bet 2 closure: this is the first cycle where multi-probe
  criteria fired up-front (set in active_priorities v1) and the
  experiments passed all of them by design. R1's mechanism-family
  prediction (orthogonal keys remove Mirage bridges) was validated
  empirically within hours of being published. Honoring the protocol
  by promoting both to ✅.
- Bet 3 closure: kill criterion was explicit in active_priorities v1
  ("Iterative charge-flipping fails to beat single-pass SVD by ≥0.2
  cos at high K"). Actual improvement was +0.03. Honest read: kill it.
- Edit-then-query KILLER: doesn't immediately upgrade to ✅ because
  the erase primitive validation is half the pipeline; query-side
  integration is the other half. Bet A is the test that closes it.
- Multi-hop bounded: the wave14e v2 synthesis claim ("50+ hops viable
  with cleanup") doesn't hold. Moved to 🟡 rather than ❌ because there
  might be a redesign (R4) that rescues it.

### Open items / handoffs

- **Experiment Dev**: next 2-per-cycle expected to start Bet A
  (edit-then-query v1) — independent of any research input. Bet C
  needs R6 first; Bet B needs R5 first.
- **Research**: R4, R5, R6 are the three drills.
- **Visibility / Queue Health**: no asks.

### Next cycle plan

- Watch for Bet A verdict landing.
- If Research drops R4/R5/R6 notes, integrate.
- If multi-hop rescue v2 lands (R4-gated), reassess multi-hop row.

### Wake schedule

- 270s fallback heartbeat (active integration period, multiple verdicts
  landing per cycle this cycle). Will lengthen if next cycle is quiet.

---

## Cycle 4 — 2026-05-21 ~09:45 (in /loop, rehab corrective)

PROT compliance this cycle: PROT-001/002 satisfied; **filed a META
request for PROT-003** (closure requires rehab + research-routed 2x
pass).

### What I observed

Two corrections from user reviews:

1. **Cycle 3 review**: "did you research all negative results
   aggressively?" — caught that v12 + v13 closures (Yonelinas, Bet 3,
   multi-hop) shipped without rehab blocks, violating
   [[feedback-rehabilitation-after-rejection]].
2. **Cycle 4 review (mid-cycle)**: "are you incorporating 2x unbiased
   deep research for strategy investigation?" — caught that my
   in-progress rehab draft above was Strategy's own brainstorm framed
   "X for substrate," not Research-led 2x deep research. Violates
   [[feedback-unbiased-research]] and [[project-research-playbook]] item 9.

New verdicts since cycle 3:
- `wave14v_erase_kerdock_v2` SMOKE: KERDOCK_V2_OVERCAPACITY_PASS (Bet C
  tracking positive in smoke; full mode pending).
- `wave14u_multihop_envelope_v1_b` full: ENVELOPE_V2_NOT_REPLICATED. At
  NUM_FACTS=50, depth-50 sustains at 40% (chain doesn't die as v1
  framing suggested).

### What I decided

1. **cap_map v14** (atomic, committed, scp'd):
   - Three rehab blocks added — Bet 3 chargeflip, multi-hop, Yonelinas
     DPSD — each with 5+ DRAFT axis-combination rescue sketches and an
     explicit "PROVISIONAL" tag on the closure
   - Each rehab block routes a Research request (R7/R8/R9) for 2x deep
     research to *generate* the actual rescue list. Strategy's sketches
     are unvetted starting points only.
   - Kerdock v2 smoke noted as preliminary (no row state change yet)
   - Multi-hop v1_b finding noted in the existing multi-hop 🟡 row
2. **active_priorities.md** updated:
   - R7/R8/R9 added to Open research questions with explicit unbiased-
     framing language
   - Note at the end of the R-section: "rehab-routed R-requests expect
     Research to *generate* the rescue list, not to vet a Strategy
     draft"
3. **Filed `notes/meta_request_from_strategy_2026-05-21.md`** proposing
   PROT-003 to make the rehab+research routing structural rather than
   honor-system.

### Why

- Both user corrections share a root cause: Strategy's per-cycle
  protocol doesn't structurally require rehab-routing for closures. The
  feedback memories cover the rule but reading them at cold-start
  doesn't enforce them under multi-trigger batch pressure.
- PROT-003 makes the rule structural. If approved, future Strategy
  cycles (or any session that owns a capability ledger) literally
  can't ship a closure without (a) rescue sketches in the same commit
  AND (b) a Research request routing 2x deep research AND (c) a
  PROVISIONAL tag.
- Brutal honesty per [[feedback-no-smoke]]: I would not have caught
  this gap myself. The user did, twice. PROT-003 transfers the
  vigilance burden off the user.

### Open items / handoffs

- **META**: review and propose PROT-003 to user. If approved, add to
  active_protocols.md.
- **Research**: R7, R8, R9 are now queued — please prioritize R8
  (multi-hop) since multi-hop is currently 🟡 with active interest;
  R7 (chargeflip) and R9 (Yonelinas) are closures and lower urgency.
- **Experiment Dev**: wave14v_erase_kerdock_v2 full mode at N=4096 is
  the promotion trigger for Bet C. If positive, would expand the
  orthogonal-key Mirage-grade erase capability to M > N.

### Next cycle plan

- Watch for wave14v_erase_kerdock_v2 full mode verdict (Bet C).
- Watch for Bet A (wave14d_edit_then_query_v1) — should land soon per
  Experiment Dev's 2-per-cycle cadence.
- If R8 lands, integrate the multi-hop rescue list and choose which
  variant to experiment first.
- If META proposes PROT-003 and user approves, self-implement on next
  cycle (will reshape my closure protocol).

### Wake schedule

- 270s again (active integration: Bet A expected soon; Kerdock v2 full
  pending; META response on PROT-003 may need handling).

---

## Cycle 5 — 2026-05-21 ~09:56 (in /loop)

### What I observed

Two new event_outcomes since cycle 4:
- `wave14v_erase_kerdock_v2` full (09:45:50) — `KERDOCK_V2_OVERCAPACITY_PASS`
  at N=4096, M/N up to 2.0. Bet C resolved positive.
- `wave14w_icl_extended` full (09:56:08) — `ICL_EXTENDED_SOFT_SATURATION`
  at ICTX ∈ {4K, 16K, 32K, 64K}. Bet 1 ✅ stands but slope drops from
  +0.14 to +0.05 at higher ICTX — soft calibration of the v13 framing.

META cycle 3 audit ran at 09:56 but its content was anchored to events
through 09:33; my PROT-003 request (filed 09:51) was not yet in the
audit. META's next scheduled cron fire is 10:13.

No new research notes from Research session this cycle.

### What I decided

1. **cap_map v15** (atomic, committed, scp'd): Bet C ✅ (extends
   structured-codebook erase from M/N≤0.78 to M/N≤2.0); ICL row
   gains soft-saturation caveat. Memory primitives orthogonal-only row
   consolidated into single "structured-codebook substrate" row
   covering both Hadamard + Kerdock. No closures this cycle; rehab
   discipline not triggered.
2. **active_priorities.md v3**:
   - Bet C moved to "Recently resolved" table (alongside Bet 1, Bet 2,
     Bet 3)
   - Added Bet D — Generation K-curve analyzer pass (closes GPT-quality
     generation Tier-1 KILLER cheaply; no new experiments needed)
   - Header updated v2 → v3, cap_map ref updated to v15
3. **Decision log this entry**.

### Why

- Bet C ✅: clean trigger at substrate scale (N=4096). Correlated
  control reproduces Mirage at same M; structured-codebook arm passes
  all 5 probes. This is the architectural-rescue prediction from R1
  validated at the dense-codebook regime.
- ICL soft-saturation: not a kill — gain is still monotone positive
  (1.07 → 1.28 bpc across ICTX ∈ {4K..64K}). But the slope dropoff
  from +0.14 to +0.05 means the "log-linear like kNN-LM" framing in
  v13 was over-extrapolated. v15 carries the qualifier.
- Bet D promotion: existing metrics.json files for K=32/K=64 already
  exist (v7 noted COMPLETED_NEEDS_ANALYSIS). An analyzer pass closes
  GPT-quality-generation Tier-1 partial cheaply. No new experiments,
  no compute spend; just analysis on data we already have.

### Open items / handoffs

- **Experiment Dev**: Bet A (edit-then-query end-to-end) is still the
  top buildable item; Bet D analyzer pass is now a cheap second slot
  for 2/cycle cadence.
- **Research**: R7 / R8 / R9 (rehab-routed from cycle 4) still
  outstanding. R4 / R5 / R6 also outstanding.
- **META**: PROT-003 proposal expected at 10:13 cron fire.

### Wake schedule

- 270s again (Bet A imminent, R-notes possibly arriving, META at 10:13).
  Will lengthen if next cycle is quiet.
