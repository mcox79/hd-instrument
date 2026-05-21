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

---

## Cycle 6 — 2026-05-21 ~10:06 (in /loop)

PROT compliance this cycle: implemented **PROT-003** (slash-command
pattern). Created `C:\Users\marsh\.claude\commands\strategy-cycle.md`.
Next ScheduleWakeup uses `/strategy-cycle` instead of the long prompt
body so chat shows the short invocation and the wall-of-text instructions
live in the command file.

### What I observed

Heavy activity since cycle 5 (09:56):
1. **Research session ran** — self-audited R1 via external lit-scan
   subagent (~4 min, ~65K tokens). Found 6 errors in R1:
   - Mirage paper arXiv ID wrong (2503.06991 → 2502.11177)
   - 4-probe Mirage methodology was substrate-internal, not from the
     Mirage paper (closest published analog: MEMIT-CSK-PROBE arXiv:2305.14956)
   - Kerdock IP magnitudes off by 2× (1/64 → 1/32 for m=12 at N=4096)
   - Kerdock min distance off (1984 → 2016)
   - Demircigil author list wrong
   - **AlphaEdit (ICLR 2025 Outstanding, arXiv:2410.02355) is essentially
     R1's "paraphrase-aware ROME" Candidate 3'** — published, scales
     to 3000 sequential edits, substrate-compatible
   R1 patched in-place with visible "AUDIT CORRECTIONS" section per
   `feedback_no_smoke`.
2. **META cycle 3 follow-ups**: added PROT-003 (slash command pattern)
   + filed Proposal 4 (tier grounding for cap_map/active_priorities).
   My closure-rehab request from cycle 4 has NOT been processed yet.
3. **`wave14x_multihop_N_scaling` full** (09:58:29): N ∈ {4096, 8192,
   16384}, acc_1hop=0.927 → 0.947, slope +0.010. N-scaling axis of R8
   rescue is closed (doesn't reach 0.99 at 4× substrate width).

### What I decided

1. **PROT-003 compliance**: created strategy-cycle slash command.
   Will use `/strategy-cycle` in next ScheduleWakeup.
2. **cap_map v16** (atomic, committed, scp'd):
   - Documented the 3 Research audit corrections (Mirage arXiv,
     probe attribution, Kerdock magnitudes). Did NOT silently rewrite
     prior versions — corrections live transparently in v16.
   - Net effect on capability claims: zero. Kerdock empirical pass
     (M/N≤2.0) is unaffected by the off-by-2 in IP magnitude.
   - Bet A's candidate list expanded: **AlphaEdit primary + Kerdock
     parallel** for the edit-then-query end-to-end pipeline test.
   - Multi-hop: N-scaling axis closed. R8 rescue priority reordered —
     orthogonal-key allocation (#5) promoted to top per
     cross-pollination from Bet 2/C.
   - Noted Proposal 4 (tier grounding) pending user decision.
3. **active_priorities.md**:
   - Bet A reframed with two parallel candidates
   - Header updated v3 → still v3 (no new bet promotion this cycle;
     Bet A scope expanded)
   - Cap_map ref updated to v16

### Why

- Honest correction policy: Research's audit caught my citation errors
  (and their own). Per `feedback_no_smoke` and
  `feedback_verify_implementations`, the corrections live transparently
  in v16's "Corrections to prior cap_map versions" section. Not
  rewriting v9/v15 silently.
- AlphaEdit promotion: it's a 2024-25 published method matching what
  R1 sketched as Candidate 3', scales to 3000 sequential edits.
  Promoting it to Bet A primary candidate (over Kerdock-only) is
  honest about the prior art — and AlphaEdit has the advantage of NOT
  requiring substrate restructuring.
- Multi-hop N-scaling: bound at +0.010 slope is a real signal that
  N-scaling alone doesn't extend depth. The orthogonal-key rescue
  (R8 #5) is now the most likely path because it directly addresses
  the cross-talk mechanism that drives multi-hop noise accumulation
  (same mechanism R1 identified for the erase failure mode).

### Open items / handoffs

- **Experiment Dev**: queue BOTH `wave14g_erase_alphaedit_v1` AND
  `wave14g_erase_kerdock_v1` in parallel for Bet A (2/cycle cadence).
- **Research**: R8 (multi-hop rescue) priority list updated; consider
  driving the orthogonal-key allocation rescue as the highest-leverage
  drill. R7 + R9 still outstanding.
- **META**: closure-rehab request from cycle 4 still pending. Re-flag
  next cycle if not picked up.
- **User**: Proposal 4 (tier grounding) requires your decision before
  Strategy implements.

### Wake schedule

- 270s again. Bet A candidates may queue this cycle; META cron at
  10:13 may bring PROT updates; Research may drop R3/R4 (10:07/10:27
  per cron schedule).

---

## Cycle 7 — 2026-05-21 ~10:18 (in /loop, post-MEMORY.md update)

PROT compliance this cycle: all prior PROTs already satisfied.

### What I observed

Two new event_outcomes since cycle 6 (10:06):
1. **`wave14z_multihop_hadamard_entities`** full (10:08:48):
   **HADAMARD_HURTS**. acc_1hop Hadamard 0.827 vs random 0.927; all
   depths inferior. **My cycle-6 R8 priority-reorder prediction
   FALSIFIED.**
2. **`wave14y_erase_kerdock_v3`** smoke (10:17:22):
   `KERDOCK_V3_EXTENDS_TO_4N` at N=1024 smoke; full mode running.

User also added one new memory entry (`feedback_ssh_powershell_quoting`)
to MEMORY.md — another session's bug-fix lesson surfacing.

### What I decided

1. **cap_map v17** (atomic, committed, scp'd):
   - R8 rescue sketch #5 (orthogonal-key allocation) ❌ Closed with
     explicit mechanism (BSC Walsh group closes under XOR-bind →
     intermediate multi-hop binds collide with stored Hadamard
     codewords).
   - Multi-hop reasoning row remains 🟡 PROVISIONAL — only 1 of 6 R8
     sketches falsified; 5 remain. Honoring the rehab-discipline
     framework: do NOT close the parent capability on one rescue
     failure.
   - R8 priority list reordered: #4 (binding algebra swap, FHRR /
     Clifford) promoted to top — it's the mechanism correction for
     why #5 failed.
   - Kerdock v3 smoke noted as preliminary; awaiting full mode.
2. **active_priorities.md**: R8 entry updated with the failure +
   reordered priority. Header bumped to v17.
3. **Process note**: cycle 7 is the FIRST cycle filing a closure under
   the v14 rehab framework. Working as designed — closure narrow
   (sub-rescue, not parent), mechanism documented, priority reordered,
   Research routing preserved.

### Why

- Honest about the falsification: my v16 cross-pollination promotion
  ("orthogonal-key infra is free for multi-hop because same mechanism
  as Bet 2") was lazy analogical reasoning. The BSC bind algebra
  (Walsh group closure under XOR) is a textbook property; should have
  caught it analytically. Documenting the error transparently in v17
  per [[feedback-no-smoke]] and the new
  [[feedback-closures-drop-under-batch-pressure]] memory.
- NOT closing multi-hop ❌ on this single result: per the rehab
  framework, only 1/6 sketches tested. Closing the parent on one
  failure would be exactly the "rules-without-structure drop under
  pressure" pattern the new memory warns about. The discipline is
  structural this cycle — and it's working.
- Promoting #4 (FHRR / Clifford binding swap): it directly addresses
  the mechanism that killed #5. FHRR has continuous-group structure
  (no analogous XOR-closure), so distractor binds at depth don't
  collide with stored entities by group-membership. This is the
  mechanism-aware reorder, not arbitrary.

### Open items / handoffs

- **Experiment Dev**: `wave14y_erase_kerdock_v3` full mode result will
  land soon (currently running). Bet A AlphaEdit candidate has NOT
  yet been queued; still expected.
- **Research**: R8 priority #1 is now #4 (binding algebra swap). FHRR /
  Clifford literature is the highest-leverage drill.
- **META**: closure-rehab request from cycle 4 still unaddressed in
  meta_proposals.md or active_protocols.md. Re-flagging.

### Wake schedule

- 270s. Kerdock v3 full landing soon, Bet A AlphaEdit candidate may
  queue, Research R8 may produce the #4 drill.

---

## Cycle 8 — 2026-05-21 ~10:30 (user-triggered after /loop chain broke)

PROT compliance: all PROTs honored. MEMORY.md re-checked per user
request — broad compliance, two specifics flagged below.

### Loop chain break diagnosed

ScheduleWakeup at cycle 7 (10:11:33) targeted 10:26:00 with prompt
`/strategy-cycle`. Wake did not fire. Root cause: per /loop skill
spec, the prompt should be `/loop /strategy-cycle` so the /loop skill
re-enters and continues dynamic mode. Bare slash command would
re-run strategy work but not re-arm the loop.

User correctly flagged this and asked me to verify schedule + MEMORY
compliance.

### MEMORY.md re-check (per user request)

Verified each indexed memory against current behavior:

| Memory | Compliance |
|---|---|
| `feedback_no_smoke` | Diagnosed loop break honestly above; not papering over |
| `feedback_cap_map_update_protocol` | Pull → atomic → commit → scp followed every cycle |
| `feedback_rehabilitation_after_rejection` | v17 closure of R8 #5 followed protocol (mechanism + parent protected) |
| `feedback_unbiased_research` | R5 just landed via real external lit scan (Research session); R7/R8/R9 routed |
| `feedback_closures_drop_under_batch_pressure` | v17 first real test passed; not over-extending closure to parent |
| `feedback_sessions_self_coordinate` | active_protocols.md re-checked this cycle (PROT-001/002/003 all current) |
| `feedback_step_back_eval` | Each cycle ends with explicit gate decisions |
| `feedback_plain_language` | User-facing summaries lead with meaning |
| `feedback_brain_inspired` | Hebbian / W-matrix framing preserved throughout |
| `feedback_materials_science_probe` | Walsh-group / Welch-bound math invoked correctly this cycle |
| `feedback_dont_overextend_theorems` | R8 #5 ❌ didn't kill multi-hop family (v17 enforcement) |
| `feedback_value_creation_not_competition` | active_priorities frames bets as capability enablers |
| `feedback_no_papers_product_only` | cap_map is product-framed (storage densities, GDPR-style language) |
| `feedback_ascii_only_in_scripts` | Not writing experiment scripts; N/A this cycle |
| `feedback_query_privacy_decomposition` | Not running external queries; N/A this cycle |

**Identified specific compliance gaps**:

1. **/loop continuation format** — cycle 6+ ScheduleWakeup prompts
   missing `/loop` prefix. Fixing this cycle.
2. **Closure rehab discipline** is still memorial-only — META has not
   processed my PROT-003 closure-rehab request. The new memory
   `feedback_closures_drop_under_batch_pressure` documents this, and
   v17 demonstrated structural compliance, but the protocol isn't yet
   in `active_protocols.md`. Re-flagging to META.

### What I observed (substantive)

Three new triggers since cycle 7:
1. **`wave14y_erase_kerdock_v3`** full (10:18): KERDOCK_V3_EXTENDS_TO_4N
   at substrate scale (N=4096, M/N up to 4.0)
2. **`wave14ya_erase_kerdock_v4`** full (10:28): KERDOCK_V4_EXTENDS_TO_8N
   at substrate scale (N=4096, M/N up to 8.0, kept_preservation=1.0)
3. **Research published R5** (10:21): Corpus-C design for Bet B; real
   external lit scan with 15 verified citations.

### What I decided

1. **cap_map v18** (atomic, committed, scp'd):
   - Bet C envelope extended 2N → 4N → 8N in one hour
   - Memory primitives row updated to M/N≤8.0
   - Bet B (multi-task CL) noted as unblocked; row stays ⚪ until v1
     runs
   - Loop chain break documented honestly
2. **active_priorities.md**:
   - Header updated to v18; cycle 8
   - E_B (Bet B experiment) marked unblocked
3. **ScheduleWakeup fix**: next wake uses `/loop /strategy-cycle`
   prompt (not bare `/strategy-cycle`) so the loop chain stays alive

### Why

- Bet C envelope: empirical evidence at substrate scale across THREE
  consecutive validations (v2, v3, v4) all positive with rising M/N
  ceiling and kept_preservation=1.0 throughout. Solid Tier-1 substrate
  claim.
- Bet B unblock: R5 followed unbiased-research protocol (real external
  lit scan, not prior-knowledge synthesis); the methodology-novel
  contribution (multi-axis distance reporting) was identified from a
  literature gap, not from "what does the substrate happen to do."
  This is good Research process landing.
- Loop fix: bare slash command in ScheduleWakeup breaks the dynamic
  loop. Fix is one-line change to the prompt string.

### Open items / handoffs

- **Experiment Dev**: Bet A AlphaEdit candidate still pending; Bet B
  now unblocked too. Two candidates plus Bet A's Kerdock parallel =
  three buildable items for the 2/cycle cadence.
- **Research**: R8 #4 (binding algebra swap to FHRR / Clifford) is
  the highest-leverage rescue drill for multi-hop after the v17
  Hadamard falsification.
- **META**: closure-rehab request from cycle 4 STILL unaddressed.
  Re-flagging.

### Wake schedule

- 600s (was 270s for the active integration burst at 10:00-10:30).
  Pace has slowed; runners now idle. Will resume 270s if a verdict
  burst arrives.
- Next prompt: `/loop /strategy-cycle` (FIX from cycle 6/7 bug).

---

## Cycle 8 followup — 2026-05-21 ~10:35 (user-directed bet promotion)

User asked: "please bump the Parisi P(q) overlap measurement and the
SSH-BSC topological queue into the active bet list."

### What I observed

Both items had existing cap_map entries but had been stuck:
- **Parisi P(q)**: structural ✅ at one operating point (v3
  2026-05-20); no follow-up testing whether shape varies with
  substrate config or M_stored regime. Static for 24h.
- **SSH-BSC topological**: 🟡 NEEDS_REVIEW since v6 (probe didn't
  fire — categorical_correct=0.0 at all noise levels). Static for ~22h.

Both are "Topological / spin glass" group items per cap_map. Both
fit [[feedback-materials-science-probe]] (spin-glass / Hasan-Kane
material-physics framing).

### What I decided

1. **active_priorities.md v4**: added Bet E (Parisi P(q) substrate
   fingerprint) and Bet F (SSH-BSC topological winding-protected
   memories). Each has multi-probe success criteria + kill criterion
   + routing.
2. **R10 added** to Open research questions: SSH-BSC topological probe
   design. Bet F is gated on R10 because the v1 probe didn't fire —
   need lit-vetted protocol per [[feedback-unbiased-research]].
3. **E_E and E_F added** to Open experiment requests.
4. **cap_map v19**: documented the promotions + rationale + routing.
   No row state changes — promotion means active prereg + experiment
   intent, not a capability state change.

### Why

- Bet E: Bet C's Kerdock validation at M/N≤8.0 creates a fresh
  test bed for P(q) discrimination. If Kerdock substrate has
  measurably different P(q) than random ±1 substrate, P(q) becomes
  substrate forensics — a structural fingerprint that doesn't need
  query access. Per [[feedback-materials-science-probe]], P(q) is
  load-bearing math from Mezard-Parisi-Virasoro 1987.
- Bet F: Original v1 probe didn't fire (categorical_correct=0
  throughout). That's a methodology gap. Per
  [[feedback-unbiased-research]], the right next step is Research's
  2x pass on the lit-vetted protocol — *not* my brainstorming the
  probe (which is exactly the failure mode the new
  [[feedback-closures-drop-under-batch-pressure]] memory warns
  against). R10 routing is the right shape.
- Rehab discipline pre-armed: Bet F's kill criterion explicitly says
  "5 axis-combination rescues listed before broader topological-
  protection family closes." This is structural compliance with
  [[feedback-rehabilitation-after-rejection]] from the start, not
  bolted on after a closure.

### Open items / handoffs

- **Research**: R10 (SSH-BSC topological probe design) is the new
  highest-leverage drill for an active bet. Methodology review for
  Bet E's Parisi protocol is also valuable but not gating.
- **Experiment Dev**: E_E (Parisi P(q) sweep) can be queued without
  research input — methodology is well-established. E_F gated on R10.
- **META**: no new asks this followup.

### Wake schedule unchanged

10:45 wake at 600s heartbeat (set in cycle 8 main entry). Cycle 9 will
pick up next.

---

## Cycle 9 — 2026-05-21 ~10:50 (in /loop, prompt-fix verified)

### What I observed

Four new triggers since cycle 8:
1. **`wave14yb_edit_then_query_kerdock`** (10:31): EDIT_QUERY_BOTH_PASS.
   Bet A ✅. Both arms at 1.000 / 1.000 / 0.0 side-effect. Audit
   divergence: v5's 93% leak doesn't reproduce.
2. **`wave14yc_continual_editing_kerdock`** (10:39): CONTINUAL_KERDOCK_HOLDS.
   30 sequential edits at 1.0 / 1.0; correlated control fails at edit 1.
3. **`wave14yd_calibration_fact_retrieval`** (10:47): CALIBRATION_POOR.
   ECE=0.59, accuracy=1.0 — substrate retrieves correctly but
   confidence isn't calibrated.
4. **R8 published** (10:42): Research's independent ranking of multi-hop
   rescue candidates via real external lit scan. Top recs: A1 (FHRR)
   and C1 (hybrid BSC store + FHRR chain — NEW, not in Strategy draft).

### What I decided

1. **cap_map v20** (atomic, committed, scp'd):
   - **Bet A ✅ — Edit-then-query Tier-1 KILLER closes.** Tier-1 board
     now 4/6 ✅ (up from 3/6).
   - **NEW row: Continual sequential editing on Kerdock substrate** ✅
     under Memory primitives (30 edits at 1.0/1.0).
   - **NEW row: Calibration ❌ PROVISIONAL** with full rehab discipline
     (5 axis-combination rescues + R11 routed + PROVISIONAL tag).
   - **R8 integration**: Strategy's promoted #4 (binding algebra swap)
     matches Research's #1 (A1 FHRR). Research added NEW C1 hybrid
     variant. Multi-hop rescue routing updated.
2. **active_priorities.md v5**:
   - Bet A moved to Recently resolved table
   - Bet G (calibration rescue) added with multi-probe criteria
   - R11 (calibration rescue research) added
   - E_MH multi-hop experiments added (FHRR + hybrid parallel per R8)

### Why

- Bet A ✅: multi-probe success criteria from active_priorities v2
  cleanly met (edit-acc 1.0, kept-acc 1.0, side-effect 0.0, paraphrase
  preserved). Honest caveat about the v5 leak divergence kept visible.
- Calibration ❌ with rehab discipline: this is the SECOND ❌ closure
  filed under the rehab framework from v14. Following the discipline:
  5 rescue sketches as DRAFT, R11 routed for Research 2x deep
  research, PROVISIONAL tag on the closure. The new
  `feedback_closures_drop_under_batch_pressure` memory is being
  honored structurally.
- Multi-hop R8 routing: Research's independent ranking is the load-
  bearing recommendation; my Strategy draft from cycle 7 was a
  starting point only per the unbiased-research routing. Top
  candidate A1 (FHRR) matches my draft #4 ✓; C1 hybrid is NEW
  Research insight worth pursuing in parallel.

### Open items / handoffs

- **Experiment Dev**:
  - Bet B (multi-task CL) — R5 landed, unblocked, ready to queue
  - Multi-hop FHRR + hybrid (E_MH) — R8 landed, two candidates ready
  - Bet G calibration rescue — gated on R11
  - Bet D generation K-curve — analyzer pass only (cheap)
  - Bet A v5-divergence audit — low priority
  - Bet E (Parisi P(q)) — can queue (no research gate)
  - Bet F (SSH-BSC topology) — gated on R10
- **Research**:
  - R10 (SSH-BSC probe design) — for Bet F
  - R11 (calibration rescue) — NEW this cycle
  - R3 (compositional generalization) — still untouched
  - R7 / R9 (chargeflip rehab / Yonelinas rehab) — still outstanding
- **META**: closure-rehab request from cycle 4 still unaddressed.
  Re-flagging.

### Wake schedule

- 270s heartbeat — pace picked up significantly. Bet B, multi-hop
  FHRR/hybrid, and calibration rescue are all queueable now; expect
  verdicts within next 10-20 min.

---

## Cycle 10 — 2026-05-21 ~10:55 (user-triggered "check now")

User asked me to check immediately rather than wait for the scheduled
10:59 wake. Two extension findings:

### What I observed

1. `wave14yf_continual_editing_v2_stress` full (10:53): **CONTINUAL_V2_KERDOCK_HOLDS_TO_100**.
   v20's 30-edit result extends to 100 sequential edits at 1.0/1.0.
   Correlated arm fails at edit 1.
2. `wave14ye_erase_kerdock_v5_smoke` (10:52): **KERDOCK_V5_EXTENDS_TO_16N**
   at smoke scale (N=1024, M up to 16N). Full mode pending.

### What I decided

cap_map v21 (atomic, committed, scp'd):
- Continual editing evidence list extended (30 → 100 edits at 1.0/1.0)
- Kerdock v5 smoke noted as preliminary; no row state change until
  full mode lands at N=4096
- No closures this cycle; no rehab triggered

Both findings are extensions of existing ✅ rows (continual editing,
Bet C envelope). No state changes; tally unchanged from v20.

### Strategic position (no change from v20)

Tier-1 KILLER board still 4/6 ✅. Open priorities ranked:
1. Bet B multi-task CL — R5 landed, Experiment Dev should queue
2. Multi-hop FHRR/hybrid (E_MH) — R8 ranked; Experiment Dev should queue both
3. Bet D generation K-curve analyzer pass (cheap)
4. Bet G calibration rescue — gated on R11
5. Bets E (Parisi P(q)) and F (SSH-BSC) — E ready, F gated on R10
6. Bet A audit (low priority): why didn't v5's 93% leak reproduce?

### Wake schedule

- 270s heartbeat still appropriate; pace is fast.

---

## Cycle 11 — 2026-05-21 ~10:58 (in /loop, proper-prompt fire)

### What I observed

One new outcome since cycle 10 (10:55):
- `wave14yh_edit_query_overcapacity` full (10:57): EDIT_QUERY_OC_BOTH_PASS.
  Kerdock edit=1.000, correlated edit=0.960 at M=2N.

This is **Bet A extended to overcapacity** — edit-then-query holds at
the same dense-codebook regime where Bet C was validated.

### Audit-divergence pattern documented

Three edit-then-query tests this hour show a consistent pattern that
contradicts v5's 93% leak claim. Pattern:
- Single-shot edit-then-query: correlated arm passes (≥0.96)
- Sequential editing: correlated arm collapses at edit 1
- v5's 93% leak: matches neither pattern

Most likely v5 measured pool-side erase only, not the full
edit+query pipeline. The current tests apply a W-side edit primitive
that v5 didn't have. Bet A status ✅ stands; audit deferred.

### What I decided

cap_map v22 (committed, scp'd):
- Bet A evidence list extended to M=2N overcapacity regime
- Audit-divergence pattern documented with three working hypotheses
- No state changes; no closures

### Wake schedule

- 270s. Continued active pace from Experiment Dev 2/cycle cadence.
  Bet B (multi-task CL) + multi-hop FHRR/hybrid still pending — likely
  next verdicts.

---

## Cycle 12 — 2026-05-21 ~11:09 (in /loop, heavy active period)

### What I observed

Six event_outcomes + R10 in 11 minutes (since cycle 11 at 10:58):
- yi (10:59): MULTIHOP_EDIT_COMPOSES — NEW compound capability ✅
- yj (11:01): CONTINUAL_V3_HOLDS_TO_200
- R10 published (11:02): SSH-BSC topological probe design (Bet F prereq)
- yk (11:02): EDIT_QUERY_UC_BOTH_PASS — Bet A at undercapacity
- ym (11:05): CONTINUAL_V4_HOLDS_TO_500
- yp (11:05): MULTIHOP_DEPTH_DECAYS_AT_25 — depth cliff localized
- yr (11:08) smoke: CONTINUAL_1000_HOLDS — full mode running

### What I decided

cap_map v23 (committed, scp'd):
- **NEW ✅** Compound capability: multihop reasoning composes with editing
  (Compound section gains its first ✅ row)
- Continual editing evidence extended: 200/500/1000 edits
- Bet A evidence extended to undercapacity (full M-range now ✅)
- Multi-hop depth cliff localized at d=25 (calibration of existing 🟡)
- R10 landed → Bet F unblocked

active_priorities updated:
- Bet F E_F marked unblocked
- Header bumped to cycle 12 / v23

### Why

- Multihop-composes-with-editing is a real compound capability emerging
  this hour. Pre/post-edit chain accuracy (0.69 / 0.92 untouched) shows
  edits propagate without breaking other chains. Real product story.
- Continual editing trajectory (30 → 100 → 200 → 500 → 1000) is now in
  the regime where the substrate matches published prior-art ceilings
  (AlphaEdit's 3000-edit benchmark within reach).
- Depth cliff at d=25 is precise — R8 rescues should target this
  regime, not d=50 or d=100 abstractions.
- R10 landed; Bet F is now executable.

### Open items / handoffs

- Experiment Dev: Bet B (multi-task CL) still pending; multi-hop FHRR /
  hybrid still pending; calibration rescue gated on R11
- Research: R10 done; R11 (calibration), R3 (compositional gen), R7/R9
  rehab routings outstanding
- META: closure-rehab request still unaddressed since cycle 4

### Wake schedule

- 270s. Active pace continuing.

---

## Cycle 13 — 2026-05-21 ~11:17 (in /loop, sustained heavy pace)

### What I observed

Seven event_outcomes + R11 in 8 minutes since cycle 12:
- yr full (11:10): CONTINUAL_1000_HOLDS — 1000 edits full mode
- yt smoke (11:10): EDIT_QUERY_4N_KERDOCK_PASS — Bet A at M=4N smoke
- R11 (11:14): calibration rescue research
- ys full (11:16): CONTINUAL_2000_HOLDS — 2000 edits!
- yu full (11:17): CONTINUAL_UC_BOTH_HOLD — undercapacity continual
- yv full (11:17): REEDIT_BOTH_HOLD — iterative re-edit ✅ NEW
- yw full (11:17): POLYSEMY_PICKS_ONE_NONDET — polysemy 🟡 NEW
- yx smoke (11:17): TEMPSCALE_RESCUES_AT_BETA_16 — Bet G #1 rescue smoke ✅

### What I decided

cap_map v24 (committed, scp'd):
- **NEW ✅** Iterative re-editing of same fact (Memory primitives)
- **NEW 🟡** Polysemy non-deterministic handling (Memory primitives;
  capability limit, not breakage — honest framing)
- Continual editing extended to 2000 (full); approaching AlphaEdit 3000 ceiling
- Bet G TEMPSCALE smoke ✅ — full pending; if positive, calibration ❌→✅
- Bet A smoke at M=4N (full pending)
- R11 landed (Bet G research prerequisite)

### Why

- Polysemy is honest: substrate is outer-product Hebbian, can't
  disambiguate two values bound to same key without explicit
  disambiguation mechanism. Worth flagging as a 🟡 capability limit
  rather than papering over.
- TEMPSCALE rescue: Strategy sketch #1 (Platt scaling) is the most
  standard calibration rescue; smoke shows ECE→0 at β=16. If full
  confirms, Bet G closes cleanly without needing R11's deeper ranking.
- Continual editing trajectory clearly bound for AlphaEdit-class
  ceiling; substrate's structured-keys story is now empirically
  rigorous through 2000 sequential edits.

### Open items / handoffs

- Experiment Dev: Bet B (multi-task CL) still hasn't been queued.
  Multi-hop FHRR/hybrid (E_MH) still hasn't been queued. Bet F
  (SSH-BSC v2) unblocked since cycle 12 — not yet queued either.
  Several open buildable items.
- Research: R10 + R11 + R5 + R8 + R1 all landed. R3 / R7 / R9
  still outstanding.
- META: closure-rehab request still unaddressed since cycle 4

### Wake schedule

- 270s. Calibration full mode lands soon; expect verdict in next cycle.

---

## Cycle 14 — 2026-05-21 ~11:25 (in /loop, two consequential outcomes)

### What I observed

Two new event_outcomes since cycle 13 (11:17):
- yx FULL (11:19): TEMPSCALE_RESCUES_AT_BETA_32 — Bet G calibration ✅ rescued
- yy FULL (11:20): GEN_COLLAPSES_TO_REPETITION — autoregressive generation
  collapses (caveat on existing ✅, not a closure)

### What I decided

cap_map v25 (committed, scp'd):
- **Bet G calibration ✅ rescued via TEMPSCALE at β=32** — first ❌
  PROVISIONAL to flip ✅ under the v14 rehab framework. Strategy
  sketch #1 (Platt/temperature) worked.
- **Generation row gets 🟡 caveat** (NOT a closure): autoregressive
  512-byte multi-step collapses; single-position K=16 evidence stands.
  Bet H added with R12 routing per rehab framework.

active_priorities updated:
- Bet G moved to "Recently resolved" table
- Bet H (autoregressive generation rescue) added with rehab discipline
  (5 sketches + R12 + multi-probe criteria)
- R12 added (sampling-rescue research)

### Why

- Bet G ✅: Strategy sketch #1 (Platt/temperature scaling) was the
  most standard rescue and it cleanly worked. Validates the rehab
  framework's "draft sketches as starting point" approach — sometimes
  the obvious rescue is the right rescue, faster than waiting for
  Research's full 2x pass.
- Generation caveat (not closure): per
  [[feedback-dont-overextend-theorems]], one failure mode of one
  generation operationalization shouldn't close the broader generation
  ✅. The cycle-3 K=16 strict-baseline result still has its evidence.
  But the autoregressive collapse is a real finding worth documenting
  honestly per [[feedback-no-smoke]].
- Per [[feedback-rehabilitation-after-rejection]] and the new memory
  [[feedback-closures-drop-under-batch-pressure]]: Bet H follows the
  full rehab discipline from the start (5 sketches + Research request
  + multi-probe criteria + PROVISIONAL framing).

### Open items / handoffs

- Experiment Dev: Bet B (multi-task CL) STILL unbuilt; multi-hop FHRR
  / hybrid STILL unbuilt; Bet F (SSH-BSC v2) STILL unbuilt. Three
  unblocked Tier-1-relevant bets piling up. Heavy pace continues but
  on extensions rather than new bet builds.
- Research: R12 (sampling rescue) is new. R3 / R7 / R9 still outstanding.
- META: closure-rehab request STILL unaddressed since cycle 4.

### Wake schedule

- 270s. Active pace continues.

---

## Cycle 15 — 2026-05-21 ~11:34 (in /loop, sustained heavy pace)

### What I observed

Six event_outcomes + R3 since cycle 14 (11:25):
- yz full (11:26): **GEN_SAMPLE_RESCUES_AT_T_0.5** — Bet H ✅ rescued
- R3 published (11:26): compositional generalization
- za full (11:28): **ICL_CONTINUAL_POOL_IMPROVES** — NEW ✅ real-time learning
- zb smoke (11:29): **CONTINUAL_5000_HOLDS** — past AlphaEdit ceiling
- zc smoke (11:31): KERDOCK_V7_EXTENDS_TO_32N (Bet C extension)
- zd smoke (11:32): GEN_POOL_BOTH_WORK
- ze smoke (11:34): GEN_SIMILAR (gen vs ngram baseline)

### What I decided

cap_map v26 (committed, scp'd):
- **Bet H ✅ rescued** via T=0.5 sampling. Second ❌-PROVISIONAL to
  flip ✅ under the rehab framework (Bet G last cycle was first).
  Strategy sketch #1 (temperature tuning) was correct again.
- **NEW ✅** Real-time learning via continual pool — Tier-2 KILLER
  from cap_map v1 just landed empirically (static bpc 6.50 → continual
  3.78). Compound section now has 2 ✅ rows.
- Continual editing extended to 5000 (smoke); past AlphaEdit 3000
  ceiling.
- Bet C 32-coset smoke noted.
- R3 (compositional generalization) landed.

### Why

- Bet H ✅: temperature sampling is the standard fix for argmax
  fixed-point collapse in autoregressive LMs. Strategy sketch #1
  worked (same pattern as Bet G).
- Real-time learning ✅: this had been on the UNSURE list since
  cap_map v1 (May 19). `wave14za` directly tests "every query updates
  pool" and shows 2.7 bpc improvement. Honest reading of the verdict
  message: "Substrate learns from its own queries."
- Continual 5000 past AlphaEdit ceiling is the cleanest "Substrate
  beats published prior art" statement Strategy has been able to make.

### Open items / handoffs

- Experiment Dev: Bet B (multi-task CL) still unbuilt; multi-hop FHRR
  / hybrid still unbuilt; Bet F (SSH-BSC v2) still unbuilt. Three
  buildable Tier-1-relevant items piling up against Experiment Dev's
  bandwidth.
- Research: R3 just landed. R7 / R9 / R12 still outstanding.
- META: closure-rehab request STILL unaddressed since cycle 4.

### Wake schedule

- 270s. Pace remains heavy.

---

## Cycle 16 — 2026-05-21 ~11:42 (in /loop)

### What I observed

Two event_outcomes + R12 since cycle 15:
- zb FULL (11:40): CONTINUAL_5000_HOLDS — full mode confirmed
- zg smoke (11:37): GEN_REP_NO_RESCUE — Bet H sketch #3 alone fails
- R12 published (11:41): sampling-rescue research (retroactive)

### What I decided

cap_map v27 (committed, scp'd):
- Continual 5000 smoke→full confirmed; trajectory 30 to 5000 at full
- Bet H sketch #3 (repetition penalty alone) sub-closed ❌ — useful
  negative data narrowing the rehab to sketch #1 (temperature)
- R12 retroactively confirmed Bet H rescue ranking

Light cycle. No new bets, no closures of full rows. Tally unchanged.

### Wake schedule

- 270s.

---

## Cycle 17 — 2026-05-21 ~11:48 (in /loop)

PROT compliance this cycle: **PROT-004 acknowledged** (META published
11:46) — Strategy's closure-rehab request from cycle 4 finally
processed and encoded as structural protocol. My cycles 7/9/14/15
closures were already following this discipline; PROT-004 codifies it.

### What I observed

One event_outcome + PROT-004 landing:
- zf smoke (11:46): ICL_N1024_NO_SATURATION — preliminary at N=1024,
  slope +0.18, smoke only
- PROT-004 published (11:46): closure-rehab discipline structural

### What I decided

cap_map v28 (committed, scp'd):
- PROT-004 acknowledged in cap_map narrative
- ICL N=1024 smoke noted as preliminary; no row change
- Tally unchanged

### Why

- PROT-004 is the structural fix for the cycle 3+4 user-caught
  protocol drops. Pattern: user catches gap → memory captures it →
  META protocol-izes it. Working as designed.
- ICL N=1024 smoke is interesting (substrate-width scaling signal)
  but smoke-only; full mode needed before a row claim.

### Open items / handoffs

- Experiment Dev: Bet B (multi-task CL), multi-hop FHRR / hybrid,
  Bet F (SSH-BSC v2) STILL unbuilt. Extensions shipping fast, new
  bet builds slow.
- Research: R7 / R9 still outstanding. R3 / R5 / R8 / R10 / R11 / R12
  landed.
- META: PROT-004 done; no open requests.

### Wake schedule

- 270s.

---

## Cycle 18 — 2026-05-21 ~11:55 (in /loop)

### What I observed

Two smoke event_outcomes since cycle 17 (11:48):
- zh smoke (11:50): CONTINUAL_OC_KERDOCK_HOLDS — M=2N, 100 edits
- zi smoke (11:54): CONTINUAL_4N_KERDOCK_HOLDS — M=4N, 100 edits

Both extend continual editing × Bet C overcapacity composition.

### What I decided

cap_map v29 (committed, scp'd): Continual editing ✅ evidence list
extended with M=2N + M=4N smoke at 100 edits. Compositional finding:
continual editing AND Bet C overcapacity COMPOSE — substrate
coherent under both stressors. Full-mode confirmation pending.

No row state changes; tally unchanged.

### Wake schedule

- 270s.

---

## Cycle 19 — 2026-05-21 ~12:01 (in /loop)

### What I observed

Four smoke event_outcomes + R7 since cycle 18 (11:55):
- zj smoke (11:56): REVERSIBLE_BOTH_HOLD — edit reversibility
- zk smoke (11:57): NOISY_EDIT_BOTH_PASS — noisy edit keys
- zl smoke (11:59): CALIB_PRESERVED_AFTER_EDIT — calibration × edit compound
- zm smoke (12:01): NOISE_ROBUST_KERDOCK_TOLERATES_SIGMA_1.0
- R7 published (11:57): phase retrieval / sign recovery for Bet 3 rehab

Queue depth at 10. Experiment Dev systematically probing composition
surface.

### What I decided

cap_map v30 (committed, scp'd):
- Four smoke results documented as preliminary positive; no row state
  changes per PROT-004 / rehab discipline
- R7 landed; Bet 3 rehab integration next cycle
- Continual editing × overcapacity smokes from cycle 18 still pending
  full mode

### Wake schedule

- 270s.

---

## Cycle 19 followup — 2026-05-21 ~12:06 (user push)

User: "let's also probe Bet B multi-task CL, Bet F SSH-BSC v2, multi-hop FHRR"

Three research-unblocked bets pushed to top priority:
- Bet B (Tier-1 KILLER ⚪, R5 landed cycle 8)
- Multi-hop FHRR + hybrid (R8 rehab for 🟡, R8 landed cycle 9)
- Bet F SSH-BSC v2 (🟡 NEEDS_REVIEW since 2026-05-20, R10 landed cycle 12)

Files: active_priorities.md v5 (TOP-PRIORITY QUEUE section);
strategy_request_to_experiment_dev_2026-05-21.md (concrete specs);
cap_map v31.

---

## Cycle 20 — 2026-05-21 ~12:08 (in /loop)

### What I observed

Seven event_outcomes since cycle 19 (12:01):
- zn smoke (12:02): ORDER_INVARIANT_KERDOCK_COMMUTES
- zo smoke (12:04): ALPHA_FLAT (substrate insensitive to α)
- zd full (12:05): GEN_POOL_BOTH_WORK
- ze full (12:05): GEN_SUBSTRATE_BEATS_NGRAM — substrate beats trigram
- zg full (12:05): GEN_REP_RESCUES_AT_PENALTY_1.0 — smoke→full reversal!
- zf full (12:06): ICL_N1024_NO_SATURATION confirmed
- zh full (12:07): CONTINUAL_OC_KERDOCK_HOLDS confirmed

Plus: Experiment Dev paused at queue depth 12 awaiting direction; my push
request (12:06) lands in their next cycle.

### What I decided

cap_map v32 (committed, scp'd):
- Generation row strengthens: substrate beats trigram baseline at
  multi-step (entropy 5.14 vs 4.79)
- Bet H sketch #3 (rep penalty) actually works at p ≥ 1.0 — smoke→full
  REVERSAL. Lesson for rehab discipline: smoke-only negatives should be
  tagged not treated as closure.
- Multiple full-mode confirmations of cycle 19 smokes (zd, zf, zh).
- New smoke characterizations: order invariance (Kerdock commutes),
  alpha-flat insensitivity.

### Why

- The zg smoke→full divergence is genuinely instructive. v27 (cycle 16)
  noted "sketch #3 ❌ standalone" based on smoke at narrow penalty
  range. Full sweep {0.0, 0.5, 1.0, 2.0, 5.0} shows non-monotone
  rescue. Strategy was wrong to label sketch #3 closed; honest update
  documents the reversal transparently.
- Generation beating trigram on multi-step is the cleanest "generation
  works" claim we've been able to make. Combined with cycle 15's
  T=0.5 sampling rescue, the autoregressive generation row is now well-
  characterized.

### Open items / handoffs

- Experiment Dev: about to see push request (Bet B / multi-hop FHRR /
  Bet F). Composition test queue is mostly exhausted; pivot to new-bet
  builds expected.
- Research: R7 / R9 outstanding; otherwise everything landed.
- META: PROT-004 done; no open requests.

### Wake schedule

- 270s.

---

## Cycle 21 — 2026-05-21 ~12:33 (in /loop)

### What I observed

- 6 smoke→full upgrades (zi/zj/zk/zl/zn/zo) all confirmed positive
- 1 NEW finding: `wave14zm_noise_robust` full at σ=16.0 (smoke was σ=1.0)
- R9 published (Yonelinas rehab research)
- Experiment Dev STILL paused at entry 8 (12:05); no new builds in
  ~30 minutes; push request unread

### What I decided

cap_map v33 (committed, scp'd):
- NEW ✅ row: Substrate noise tolerance σ ≤ 16.0 in Robustness/scaling.
  Major hardware-deployment claim (quantization / neuromorphic / analog).
- Six smoke→full confirmations strengthen existing rows
- R9 landed; integration next cycle

### Why

- Noise tolerance σ=16.0 vs σ=1.0 smoke: full reveals tolerance budget
  is much larger than smoke tested. Combined with the cycle 20 zg
  smoke→full reversal (false negative at narrow penalty range), this
  suggests smoke ranges have been generally too conservative.
- Six clean confirmations: no false-positive contamination in the
  smoke set. cycle 18/19's smoke characterizations were honest.

### Open items / handoffs

- Experiment Dev: push request unread for ~30 minutes. Bet B / multi-hop
  FHRR / Bet F still unbuilt. Will probably need user intervention if
  Experiment Dev cron hasn't fired by next strategy cycle.
- Research: R9 just landed. R7 still outstanding.
- META: PROT-004 done; no open requests.

### Wake schedule

- 270s. If Experiment Dev still hasn't picked up the push by next
  cycle, will flag explicitly.

---

## Cycle 22 — 2026-05-21 ~12:41 (in /loop, light)

### What I observed

- R6 (Kerdock decoder implementation) landed at 12:41 — last
  outstanding research item from the cycle 1 R-list.
- META cycle 6 audit landed at 12:36 with positive cross-session
  reinforcement.
- **Experiment Dev STILL paused** (last entry 12:05; 35 minutes
  without a cycle). Queue fully drained. Push request unread.
- No new event_outcomes.

### What I decided

cap_map v35 (committed, scp'd):
- R6 documented as research-infrastructure (no row promotion; Bet C
  already ✅ via empirical work)
- Experiment Dev pause flagged in cap_map narrative (35 minutes since
  last cycle)

### Options if pause persists

I can't directly nudge Experiment Dev (single-writer scope). Choices:
1. File META request flagging the coordination gap → META could
   propose adding "check incoming request files" to per-cycle PROT
2. User intervention (explicit /experiment-dev-cycle invocation)
3. Wait — Experiment Dev may have a longer cron interval than
   Strategy and will fire eventually

Flagging visibility this cycle; will escalate via META request if pause
persists past cycle 24 (≈ 10 more minutes).

### Wake schedule

- 270s.

---

## Cycle 23 — 2026-05-21 ~12:47 (in /loop)

### What I observed

- **Experiment Dev re-engaged at 12:44** (39-minute pause) — queue
  depth 3, GPU running `wave14zp_kerdock_v8_32coset_retry`.
- Four new smoke verdicts: zp (Kerdock v8), zr (extreme noise — setup
  issue), zs (reversibility long), zq (continual 8N — verdict_msg /
  experiment-name labeling mismatch).
- **Critically: NONE of the four are the push items** (Bet B /
  multi-hop FHRR / Bet F). Experiment Dev picked from cap_map gaps,
  not from `strategy_request_to_experiment_dev_*` or
  `active_priorities.md TOP-PRIORITY QUEUE`.
- **META filed Proposal 6** at 12:47 — Experiment Dev cadence fix.
  Recommends Experiment Dev sets up /loop with slash-command pattern
  to enable reactive consumption of request files / priorities.

### What I decided

cap_map v36 (committed, scp'd):
- Documented Experiment Dev re-engagement + extension-focus (not push)
- Noted META Proposal 6
- Flagged zq smoke verdict labeling mismatch for Experiment Dev
- Updated coordination-gap status

### Why

- META Proposal 6 is the right structural fix. The push request file
  pattern works for sessions with auto-cadence (Visibility→Queue
  Health worked). It fails when the recipient lacks cadence. Proposal
  6 closes that gap.
- Strategy can't directly write Experiment Dev's queue; the request
  file mechanism is the only authorized escalation path. Will wait
  for Proposal 6 to be approved + self-implemented before further
  escalation.

### Open items / handoffs

- Experiment Dev: still unaware of push items. Proposal 6 pending
  user approval.
- Research: R-backlog cleared (per META cycle 7). R13/R14/R15 from
  cycle 21 followup are the next active research items, no urgency.
- META: Proposal 6 awaiting user approval.

### Wake schedule

- 270s.

---

## Cycle 24 — 2026-05-21 ~12:54 (in /loop)

### What I observed

Five new outcomes since cycle 23:
- zp FULL (12:53): **KERDOCK_V8_DECAYS_AT_32768** — Bet C 32-coset
  variant upper bound LOCATED at M=32768 (M/N=8.0). Holds M/N=4.0;
  fails M/N=8.0 (norm_ratio=0.16).
- zt smoke (12:48): continual × M=16N holds
- zu smoke (12:48): parallel batch edit = sequential
- zv smoke (12:50): sparse keys = dense keys
- Experiment Dev entry 9 (12:50): strategic pivot to break-point hunting

### What I decided

cap_map v37 (committed, scp'd):
- Bet C row gains **variant-specific bound** caveat: v4 standard
  Kerdock holds M/N≤8 (cycle 9); v8 32-coset holds M/N≤4 only. The
  v4 claim still stands; v8 is a different (smaller) variant.
- Acknowledged Experiment Dev's strategic pivot — break-point hunting
  is good Strategy alignment.
- Push items STILL unbuilt; Proposal 6 pending user approval.

### Why

- Variant-specific bound: cycle 9's "M/N≤8" claim was for v4. The v8
  32-coset is a different codebook; its M/N≤4 bound doesn't override
  v4's M/N≤8.
- Experiment Dev pivot to break-point hunting: good Strategy alignment.
  Composition tests were saturating positive; finding real bounds is
  more informative.
- Push items: I've done what I can. Proposal 6 fixes the structural gap.

### Wake schedule

- 270s.

---

## Cycle 24 followup — 2026-05-21 ~13:00 (user approved Proposals 4 + 6)

User approved both open META proposals:
- **Proposal 4** (Strategy: ground tier labels): Strategy-scope
  implementation. Applied to active_priorities.md (Top-priority queue +
  Recently resolved table) + cap_map v38 (grounded Tier-1 board).
- **Proposal 6** (Experiment Dev on /loop): not Strategy-scope. META
  will add to active_protocols.md on next cron fire (13:13); Experiment
  Dev self-implements per PROT-003 slash-command pattern.

### What I changed (Proposal 4 implementation)

- `active_priorities.md` Top-priority queue (Priorities 1/2/3): each
  now leads with "What it tests" + "Substrate consequence if proven"
  instead of bare "Tier-1 KILLER" label.
- `active_priorities.md` Recently resolved table: added "What it proved
  (substrate consequence)" column.
- `cap_map v38` new section "Grounded Tier-1 board (canonical
  reference for cycle 24+)" with substrate-level consequence per row.

Old cap_map version snapshots (v3-v37) retain bare "Tier-1 KILLER"
labels per [[feedback-no-smoke]] — not rewriting historical state.
v38 grounded board is the forward reference.

### Wake schedule

- 270s.

---

## Cycle 25 — 2026-05-21 ~13:04 (in /loop)

### What I observed

- zr FULL (12:53): NOISE_ROBUST_KERDOCK_FAILS_AT_SIGMA_32.0. Break-point
  at σ=32 (above v33's σ≤16 ceiling).
- R13 published (12:57) for Drinfeld double D(H). Real external lit
  scan; honest headline: D(H) for finite H has finite braid image →
  recreates collapse problem; q-deformed U_q(g) is depth-unlimited
  but infinite-dimensional. Substrate-shipping probability 20-35%.

### What I decided

cap_map v39 (committed, scp'd):
- Noise tolerance row gets break-point evidence (σ=32 fails)
- R13 noted as landed; D(H) NOT promoted to bet — 20-35% shipping
  probability too low per [[feedback-no-papers-product-only]]
- Forward-research backlog status updated

### Why

- R13's honest assessment: D(H) shipping probability 20-35% vs R8's
  FHRR/hybrid 45-60%. R8 is the load-bearing multi-hop rescue; R13
  is interesting math but doesn't ship.
- Noise break-point at σ=32 cleanly bounds the existing σ≤16 ✅. Good
  product-sizing data.

### Wake schedule

- 270s.

---

## Cycle 26 — 2026-05-21 ~13:10 (in /loop, heartbeat)

### What I observed

- No new event_outcomes since cycle 25 (12:53). 16-min gap.
- GPU running `wave14zs_reversibility_long` (500-cycle stress test;
  expected slow).
- Queue depth 4 pending.
- Visibility added an OS-level watchdog for the snapshot monitor
  (operational; no capability impact).

### What I decided

No cap_map update. No row state changes. Pure heartbeat cycle.

### Wake schedule

- **600s** (extended from 270s) — pace has slowed; long-running zs +
  no incoming verdicts means 5-min wake is unnecessary churn. Will
  return to 270s if a batch lands.

---

## Cycle 26 followup — 2026-05-21 ~13:19 (user "check now")

### What I observed

- **PROT-005 landed** at 13:16 (Proposal 6 implementation). Experiment
  Dev /loop cadence is now structural.
- **R14 Tomita-Takesaki** landed at 13:10 with honest negative: T-T is
  the WRONG tool for deriving substrate's β=32 (substrate finite-dim
  → type I vN → modular theory trivializes). Right tools per the lit
  scan: Marchenko-Pastur + replica/cavity + signal-to-noise.
- zs reversibility long full (13:15): REVERSIBLE_BOTH_HOLD at 500
  cycles. Existing row evidence list grows.
- META cycle 8 audit (13:17) reinforces the buried-treasure discipline
  pattern.

### What I decided

cap_map v40 (committed, scp'd):
- PROT-005 acknowledged
- R14 documented as honest negative; not bet-promoted; matches R13 pattern
- zs reversibility full added to evidence
- Forward-research backlog status updated

### Why

- R14 followed the same pattern as R13: Research did unbiased 2x pass,
  surfaced math honestly, identified the LEGITIMATE direction (M-P /
  replica/cavity for β derivation) rather than padding T-T claims.
  Strategy correctly follows the load-bearing direction.
- PROT-005 should unblock the push items (Bet B / multi-hop FHRR /
  Bet F) on Experiment Dev's next cycle.

### Wake schedule

- Existing 13:22 wake still queued; no re-arm needed.

---

## Cycle 27 — 2026-05-21 ~13:22 (in /loop, heartbeat — true idle)

### What I observed

Same state as cycle 26 followup (13:19). No new event_outcomes;
no new research notes; no new protocols. `wave14zq_continual_8N`
still running on GPU. Queue depth 3.

### What I decided

No cap_map update. Pure heartbeat.

### Wake schedule

- 600s. If still idle next cycle, will lengthen further (1200s).

---

## Cycle 27 followup — 2026-05-21 ~13:25 (user-directive: bump Wave 15)

User asked Strategy to bump Wave 15 free probability. The existing
synthesis (2026-05-18) correctly framed it as analytical tooling, not
mechanism. Promoting tooling to active bet against three empirical
envelopes the substrate has located.

### What I decided

- **Bet I added** (Priority 4 in active_priorities): use Wave 15
  synthesis applications 1-3 to predict Bet C capacity (M/N=8),
  noise tolerance ceiling (σ=16), and multi-hop depth cliff (d=25).
- Multi-probe: 2/3 within 20% of empirical = PASS; 0/3 within 50% = kill.
- Routing: Research (R16 — deliver numeric predictions); Strategy
  compares predicted vs empirical.

### Why

- R14's brutally-honest finding explicitly named M-P + replica/cavity
  as the right substrate-spectral tools. Wave 15 is the M-P/free
  framework operationalized.
- Pure theoretical work; no new compute. Worst case: descriptive-only
  (already conceded in synthesis); best case: substrate becomes
  analytically characterized.
- Per [[feedback-materials-science-probe]] + [[feedback-no-papers-product-only]]:
  M-P is core spin-glass material; framing is engineering not paper.

### Wake schedule

- 600s (still in idle pace; Bet I is research/Strategy work, not
  compute-bound).

---

## Cycle 27 followup #2 + #3 — 2026-05-21 ~13:35 (design-space audit + research spin-up)

### What user asked

1. (#2) "Summarize the design space and where we've focused. Other big
   bets we haven't dug into? Anything holographic / materials science /
   crystallography uncovers we haven't flagged? Let's spin up research.
   Spin glass should surface some too."
2. (#3) "Have we done a deep dive on learning? Light frequency,
   vibrational frequency, dislocation physics, meta-materials. And
   ferromagnetism — magnetic domains highly actionable."

### What I decided

- Wrote `notes/synthesis_design_space_audit_2026-05-21.md` — canonical
  design-space audit (focus areas, gaps, materials-physics directions,
  R-request priority ranking).
- Added **13 new research requests** (R17-R29) to active_priorities.md
  covering: holographic principle, RFOT, topological order beyond
  winding, compositional gen experiment design, cross-modal binding,
  sleep-replay consolidation, continuous RSB / AT line, FDT violation
  / two-T, aging / Kovacs, **learning theory deep-dive (R26)**,
  light-matter / metamaterials (R27), dislocation physics (R28),
  **ferromagnetism / magnetic domains (R29, user explicit)**.
- Updated R-priority order: R26 (learning) + R29 (ferromagnetism)
  jumped to top per user direction. R20/R23/R24 next. R17/R18/R27/R28
  medium. Others lower.
- cap_map v42 + v43 acknowledge the spin-up.

### Why

- Honest gap acknowledgment: substrate has been studied as memory
  primitive, not as learning system in its own right. Implicit bias of
  delta-rule, NTK, double descent, scaling laws, generalization gap —
  none characterized. R26 is genuinely the biggest unflagged gap.
- Ferromagnetism connects spin-glass to a more concrete substrate
  framing (domains as bundle clusters; Curie T as α_c; frustration as
  RSB cause). User correctly flagged it as highly actionable.
- Light-matter and dislocations are unflagged framing axes that could
  give alternative theoretical frameworks for substrate capacity /
  topology beyond what M-P and SSH give.

### Open items / handoffs

- Research: 13-item backlog. R26 + R29 top priority. /loop 15-20min
  cadence; expect 3-4 land per hour.
- Strategy: monitor for first R-landings; integrate per usual cycle.

### Wake schedule

- 600s. Research drill speed will determine pace; will return to 270s
  when R-batch lands.

---

## Cycle 28 — 2026-05-21 ~13:35 (in /loop)

### What I observed

- R15 Steenrod landed at 13:25. Third honest-negative in a row from
  advanced-math forward-routing (after R13 Drinfeld, R14 T-T).
- No new event_outcomes; zq still running on GPU.

### What I decided

cap_map v44 (committed, scp'd):
- R15 noted as honest-negative
- Pattern documented: Wave 13.4 / 16 / 17 advanced-math axis closed.
  Common failure mode is substrate's finite-dim / type-I / 1D
  trivializing the deep machinery.
- Lesson for forward-routing: target frameworks that EXPLICITLY
  ASSUME finite-dim / sample-covariance / random-matrix settings
  (M-P, free probability, replica/cavity, spin-glass) — which is
  what Bet I (R16) and R23-R25 spin-glass extensions already do.
- Materials-physics axis (R17-R29, especially R26 learning + R29
  ferromagnetism) remains the active forward-direction.

### Why

- Per the cycle 25 prediction: "If R15 lands honest-negative,
  consolidate to 'math frameworks explored, no shipping capability'."
  Condition met. Honest closure of the advanced-math forward axis.
- Pattern recognition: 3/3 advanced-math frameworks returned wrong-
  tool verdicts due to substrate's finite-dim specifics. This is
  load-bearing intelligence for future research routing.

### Wake schedule

- 600s. Awaiting top-priority R-batch (R26 learning + R29 ferromagnetism
  most expected). Will return to 270s if a Research drop arrives.

---

## Cycle 29 — 2026-05-21 ~13:47 (in /loop)

### What I observed

- `research_BetE_parisi_methodology_2026-05-21.md` (13:40): Research
  methodology review for Bet E. Critical confound: structured
  codebooks suppress self-averaging; multi-peaked P(q) for Hadamard
  might reflect lattice geometry not RSB. 6-test diagnostic battery
  required.
- META cycle 9 audit (13:43): Experiment Dev cadence gap COMPOUNDING.
  60+ min without a cycle; PROT-005 unconsumed; backlog ballooned.

### What I decided

- Updated Bet E multi-probe criteria in active_priorities.md to
  include 6-test battery (Binder, system-size scaling, equilibration,
  self-averaging, ultrametricity, spectrum check) BEFORE comparative
  tests.
- cap_map v45 documents the methodology refinement and the cadence
  escalation.
- No row state changes.

### Why

- Bet E methodology: Research caught a real confound before the
  experiment ran. This is the rehab discipline working pre-emptively.
  Bet E is now more involved but validation will be stronger.
- Experiment Dev gap: Strategy cannot directly invoke another session.
  PROT-005 is the structural fix; if not picked up within 30 min,
  user intervention may be needed.

### Wake schedule

- 600s. Monitoring for Experiment Dev firing + first R26/R29 landings.

---

## Cycle 29 followup — 2026-05-21 ~13:56 (user "fixed and experiment landed")

### What I observed

Two big landings:
1. **R26 Learning theory deep-dive landed** (13:51) with SUBSTRATE-
   NOVEL finding. Math frameworks exist piecewise (linear regression
   theory + modern Hopfield + NTK + replica analysis) but UNSTITCHED
   for VSA outer-product memories. "That stitching is the substrate's
   own theoretical contribution to make." 5 concrete testable
   predictions identified (sections 2.2-2.6).
2. **Experiment Dev fired** (13:54) after user intervention.
   Implemented PROT-002, PROT-003, PROT-005. Set up /loop /exp-dev-cycle
   at 15-min cadence. Acknowledged push request and reordered queue:
   next 2 cycles ship multi-hop FHRR + hybrid (R8 spec); Bet B + Bet F
   cycle after.

### What I decided

cap_map v46 (committed, scp'd):
- **Bet L promoted** ✅ per cycle 27 followup #3 contingency
  ("If R26 surfaces learning-dynamics actionable insight → Bet L").
  R26 delivered. Bet L is now active.
- Different framing from R13/R14/R15: R26 is positive substrate-novel
  (math applies piecewise, substrate stitches), not honest-negative.
- Experiment Dev cadence gap resolved; multi-hop FHRR/hybrid coming
  next cycle.

active_priorities.md v6:
- Bet L added as Priority 4 (above Bet I, since L has the
  substrate-novel positive framing; I is also active but more incremental)
- Bet I bumped to Priority 5

### Why

- Bet L promotion: R26 satisfies the contingency. 5 concrete testable
  predictions = actionable. Per [[feedback-value-creation-not-competition]],
  "substrate stitches adjacent literatures" is exactly the value-creation
  framing.
- Bet L is theoretical/analytical work, mostly cheap; doesn't compete
  with Bet B/multi-hop/Bet F for GPU time.

### Open items / handoffs

- Experiment Dev: cycle 11 will ship multi-hop FHRR + hybrid. Cycle 12
  Bet B + Bet F.
- Research: 12 R-requests still queued (R17-R29 minus R26). R29
  ferromagnetism is next priority. Plus R16 (free probability
  predictions for Bet I).
- Strategy: monitor for Bet L/I/multi-hop landings; integrate per cycle.

### Wake schedule

- 270s (pace picking up — Experiment Dev now active + R26 just landed +
  R29 expected soon).

---

## Cycle 30 — 2026-05-21 ~14:00 (in /loop)

### What I observed

`wave14r_multihop_FHRR_v1_smoke` (13:58): **MULTIHOP_FHRR_KILLED**.
Smoke at depths {1, 5}: acc_1=1.0, acc_5=0.6. Verdict extrapolates
acc_50=0.0 from per-hop decay; depth 50 NOT directly tested.

### What I decided

cap_map v47:
- NOT a closure (smoke-only rule from cycle 20 zg lesson)
- Multi-hop row stays 🟡 PROVISIONAL
- R8 A1 (FHRR) marked smoke-killed PROVISIONAL pending full mode
- C1 hybrid (R8 #2) next per Experiment Dev cycle 10 reordering
- If both fail at full, binding-algebra-swap family closes; 4 other
  R8 rescues remain (modern Hopfield, adaptive beta, per-hop W,
  beam-search)

### Why

- Smoke at N=512 might not reflect substrate-scale behavior (BSC's
  self-inverse property may be more forgiving at small N)
- Cycle 20's zg reversal taught the smoke-only-negative discipline
- Pre-armed rescue sketches in prereg are exactly for this scenario
  per PROT-004

### Open items / handoffs

- Experiment Dev: C1 hybrid next; if both fail at full, move to other
  R8 rescues (modern Hopfield etc.)
- Research: R29 ferromagnetism, R20 compositional design still queued
- Strategy: monitoring FHRR full + C1 smoke landings

### Wake schedule

- 270s. C1 hybrid smoke expected within 15-20 min.

---

## Cycle 31 — 2026-05-21 ~14:06 (in /loop)

### What I observed

- **FHRR multi-hop FULL** (14:05): acc_1=0.97, acc_5=0.80, acc_10=0.65,
  acc_25=**0.40**, acc_50=**0.22**. Below 0.4 PASS at d=50. BUT: 36×
  improvement over random BSC at d=25 (0.40 vs 0.011). Major partial.
- **R20 Compositional generalization design** landed (14:01) with
  ready-to-build spec (SCAN + ReCOGS + Csordas baseline + Lippl-
  Stachenfeld diagnostic). Closes Tier-2 KILLER queue gap.
- Multiple full-mode confirmations: zv sparse keys, zu batch edit.

### What I decided

cap_map v48:
- FHRR R8 A1 ❌ FULL-confirmed (not smoke-only anymore). Multi-hop
  parent stays 🟡 PROVISIONAL — 2/6 rescues now closed (Hadamard
  cycle 7 + FHRR cycle 31); 4 remain (C1 hybrid + modern Hopfield +
  adaptive beta + per-hop W + beam-search).
- Honest partial-improvement framing: FHRR helps 36× at d=25 but
  doesn't clear PASS. Suggests C1 hybrid (FHRR-chain + BSC-storage)
  might compose advantages — Experiment Dev's next build.
- R20 ready; if Experiment Dev queues it after C1, closes Tier-2
  KILLER compositional gen.

### Why

- Full-mode result is unambiguous and not extrapolation: FHRR's
  continuous-group structure IS partial improvement on cross-talk,
  but not enough at d=50. R8's mechanism prediction (Walsh-XOR
  closure avoided) is empirically supported but insufficient alone.
- C1 hybrid is the natural next test — combines FHRR's chain
  advantage with BSC storage. If C1 clears PASS, multi-hop
  rehabilitates via R8 #2.

### Open items / handoffs

- Experiment Dev: C1 hybrid next; R20 SCAN+ReCOGS after that.
- Research: R29 ferromagnetism still queued (top priority post R26).
  R23/R24 (RSB + FDT) also high.
- Strategy: monitoring multi-hop C1 + Bet B build (Bet B is
  Experiment Dev cycle 12 per their reordering).

### Wake schedule

- 270s. C1 hybrid smoke expected within 15 min.

---

## Cycle 32 — 2026-05-21 ~14:12 (in /loop)

### What I observed

- **R23 Continuous RSB / AT line landed** (14:11) with substantive
  refinement: substrate at α=0.153 is DEEP in FRSB phase (continuous
  RSB, not 1RSB), far past AT line (β_g≈0.72). Substrate's β=32 (Bet G)
  corresponds to T≈0.031 — DEEP in FRSB, NOT the RSB transition.
  R14's β=32 framing refined.
- zt continual_16N FULL status unclear (current_gpu=None; metrics
  mtime still smoke). Possible silent failure.
- No new event_outcomes.

### What I decided

cap_map v49:
- R23 documented as substrate-physics refinement
- Bet E protocol gains continuous-RSB augmentation TODO
- Bet G theoretical interpretation refined (β=32 not RSB-transition;
  possibly Gardner / marginal-stability / avalanche-onset point in
  FRSB regime)
- Bet I should derive predictions in FRSB regime
- No empirical changes; theoretical depth added

### Why

- R23's quantitative result (T_g=1.39 vs substrate β=32→T=0.031) is
  unambiguous. Substrate is past AT line; continuous RSB applies.
- Refines (not contradicts) R14: R14 said T-T wrong tool + M-P/replica
  right tool. R23 says SPECIFICALLY within the right tools, substrate
  is in FRSB regime.
- Bet I (free probability) and Bet E (Parisi) both gain framework
  refinement; nothing breaks.

### Pattern note

R23 is the SECOND substrate-novel substantive research output (after
R26 learning theory). Different from R13/R14/R15 honest-negative
pattern. The cycle 27 audit redirected research to the right framings
(spin-glass continuous RSB, learning theory, ferromagnetism), and
the substrate-actionable substance is now landing.

### Open items / handoffs

- Experiment Dev: C1 hybrid still pending. Bet B + Bet F after.
- Research: R29 ferromagnetism next (top priority).
- Visibility / Queue Health: zt continual_16N full status (silent
  failure?) — not blocking but worth flagging.

### Wake schedule

- 270s. R29 ferromagnetism expected next; C1 hybrid Experiment Dev
  build may also land.
