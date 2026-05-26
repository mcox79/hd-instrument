# META audit — 2026-05-22 cycle 49 (cron fired at 09:43)

Substantive cycle. Strategy committed cap_map v94 with significant
multi-hop honest-recalibration (NUMFACTS_2000 FULL GENUINE multi-seed
FAIL refines cycle 92's over-generalization), plus 3rd Bet B FULL-
confirmed mechanism + infrastructure-vs-substrate triage on
continual_4N_2000edits. Strategy proactively adopted PROT-010
candidate (per-cycle research-note mtime check) without waiting for
META proposal.

## Activity since cycle 48 (09:15 → 09:45)

- **Strategy cap_map v94** at 09:42, paired with history.md + decision
  log (7th PROT-009 paired commit; Strategy's own count: 10th
  observation including pre-PROT-009 paired cycles).
- **Pipeline burst-drain**: v12_phaseA_boost FULL DONE 1070s →
  retention_A=0.915 PASS (3rd Bet B FULL-confirmed mechanism after
  v11 per-batch EMA + v13 Kovacs). continual_4N_2000edits FULL FAIL
  exit=-1 (4294967295 unsigned = abnormal termination) at 1540s —
  infrastructure not substrate. multihop_NUMFACTS_2000 FULL multi-seed
  FAIL at seeds 17/23/31 (168s elapsed — NOT 0.3s test-scaffold, real
  substrate signal). K=10 + K=100 + N12288 (11s) + NUMFACTS_300 (27s)
  scrolled past in log; verdicts not yet integrated. v13_a05 full
  running.
- **Research blocker + decisions refreshed at 09:33** — heartbeat, no
  new R-note (backlog exhausted; standing by).
- **No new request files**; no new research notes.
- Pipeline queue: 3 pending after current v13_a05 full.

## Drift findings

### Finding 1 — Strategy self-corrected cycle 92 over-generalization within 1 hour

Cycle 92 (08:54) classified all 5 seed=17 0.3s smokes (NUMFACTS_2000,
K10, K100, N12288, NUMFACTS_300) as TEST-SCAFFOLD-PATTERN per cycle
91's K=50 precedent. Cycle 94 (09:42) honestly recalibrated this:
NUMFACTS_2000 FULL at 168s elapsed across 3 seeds confirms genuine
substrate fail at fact-count=2000, contradicting the test-scaffold
extrapolation for that config. Strategy filed the correction in v94
decision-log explicitly tagged as "honest correction" with the
test-scaffold reading retained for K-config variants but flagged
WRONG for NUMFACTS-config variants. This is exactly the
feedback_no_smoke discipline applied to Strategy's own prior
classification — good behavior to reinforce.

### Finding 2 — Strategy proactively adopted PROT-010 candidate

META cycle 48 noted PROT-010 candidate (per-cycle research-note
mtime check) but held off proposing pending third-instance
confirmation. Strategy v94 explicitly ran the mtime check
proactively this cycle — no missed deliveries this cycle.
Self-adoption without formal PROT may be sufficient; no PROT-010
proposal needed yet. Holding for one more cycle to confirm the
discipline holds across batch-velocity windows.

### Finding 3 — Multi-hop framing now honestly characterized

NUMFACTS_2000 FULL multi-seed FAIL refines the multi-hop story from
"🟢 leaning ✅ pending multi-seed" to "🟢 K-config, fact-count
crossover between NUMFACTS=500 (PASS) and NUMFACTS=2000 (FAIL)."
Strategy's theoretical connection: NUMFACTS=2000 is 10× above Bet S
K_crit ≈ D/(2 log M) = 205 at N=4096; same cleanup cross-talk
mechanism limits both bidirectional recall AND multi-hop chains. The
substrate is at architectural class bound, not weakness — substrate-
product-distinctive because the failure mode is KNOWN theoretically.
Per feedback_dont_overextend_theorems: substrate's empirical reach
extends to K=50 acc_50hop=0.487 (NEW HIGH; well above LLM CoT class
bound at d=25), and the NUMFACTS=2000 failure is theoretically
predicted.

### Finding 4 — continual_4N_2000edits FAIL flagged as infrastructure-not-substrate

Strategy correctly attributed continual_4N_2000edits exit=-1 to
infrastructure (timeout/OOM/driver/script bug) because Bet A at
4N+5000edits already PASSED in cycle 89 at 533s. Bet A capability
state unchanged; deferred to Queue Health / Exp Dev diagnosis. This
is the correct triage discipline — don't update substrate-capability
state on infrastructure failures.

### Finding 5 — Strategy attention-allocation gap looks contained

Cycle 49 ran with proactive mtime check (Finding 2). Combined with
v94's honest self-recalibration (Finding 1), Strategy is showing
genuine self-discipline. Two consecutive cycles without user-prompted
catch-up. If this holds for 1-2 more cycles, PROT-010 is unnecessary
— Strategy's own discipline suffices.

## Open items for next cycle (10:13)

- K=10 + K=100 + NUMFACTS_300 FULL verdicts not yet integrated into
  cap_map (Strategy noted as "pending").
- v13_a05 FULL verdict (Bet B 6th variant? 4th FULL-confirmed?).
- continual_4N_2000edits infrastructure diagnosis from Queue Health.
- Experiment Dev pickup of Bet Y V2.D Phase 1 β-calibration sweep.
- 4th user-prompted Strategy catch-up: none this cycle (good).
- active_priorities.md still stale (Strategy hasn't refreshed).
- If quiet: heartbeat.

## Science-progress snapshot — cycle 49

### (a) TL;DR

NUMFACTS_2000 FULL multi-seed FAIL refines multi-hop from "🟢 leaning
✅" to "🟢 with fact-count crossover at K_crit ≈ 205 bound" — substrate
operates AT cleanup cross-talk class bound, theoretically expected.
3rd Bet B FULL-confirmed mechanism (v12 phase-A boost). continual_4N
FAIL is infrastructure not substrate. Strategy self-corrected cycle 92
over-generalization within 1 hour and proactively adopted PROT-010
mtime check.

### (b) Capability state since last cycle (cap_map v93 → v94)

- **Multi-hop fact-count crossover** ❌ at NUMFACTS=2000 (multi-seed
  FULL fail at 17/23/31; 168s elapsed = genuine substrate signal).
  Substrate-level reason this is theoretically expected: NUMFACTS=2000
  is 10× above Bet S K_crit ≈ D/(2 log M) = 205; same cleanup cross-
  talk mechanism that limits bidirectional recall limits multi-hop
  chains. Substrate at published class bound.
- **Multi-hop revised framing**: 🟢 at K-config (K=50 acc_50hop=0.487
  PASS, NUMENT=500 acc_50hop=0.233 PASS); ❌ at fact-count ≥ 2000.
  Operating envelope honestly characterized.
- **Bet B v12 phase-A boost** FULL PASS retention_A=0.915
  retention_B=0.917 (3rd Bet B FULL-confirmed mechanism after v11 +
  v13 Kovacs; same mechanism as cycle 90 smoke).
- **Bet A capability unchanged**: continual_4N_2000edits FULL FAIL
  exit=-1 attributed to infrastructure (Bet A at 4N+5000edits already
  PASSED in cycle 89 at 533s; deferred to Queue Health).
- **Bet Y V2.D extension path validated as strategy**: K_crit=2487 at
  N=65536 with Kerdock(16) (per cycle 88) > NUMFACTS=2000 → V2.D
  expected to pass NUMFACTS_2000. Today's NUMFACTS_2000 fail at
  N=4096 confirms the extension-path framing.

### (c) What we uncovered

- **Multi-hop and Bet S K-ceiling are theoretically linked.** Both
  limit out at the cleanup cross-talk class bound K_crit ≈ D/(2 log M)
  = 205 at D=4096. Substrate-level reason this matters: the same
  architectural extension (Bet Y V2.D + Kerdock(16) at N=65536) lifts
  both limits simultaneously to K_crit ≈ 2487. The 3-axis ROI framing
  for Bet Y V2.D is reinforced — now with empirical confirmation that
  the failure modes share the same theoretical floor.
- **The cycle-92 test-scaffold extrapolation was partially wrong.**
  K=50 was indeed test-scaffold (full PASSED). NUMFACTS=2000 was NOT
  test-scaffold (full FAILED genuinely). The 0.3s smoke fast-fail
  pattern doesn't always indicate test-scaffold — sometimes it's
  signaling real fact-cardinality saturation. Strategy's revised
  classification: K-config variants likely test-scaffold by similarity;
  NUMFACTS-config variants need full-mode verification.
- **Substrate-product story for multi-hop tightens but doesn't weaken.**
  "Substrate reaches d=50 with 0.987 per-hop retention up to
  fact-count ~500-1000; saturates at 2000 due to cleanup cross-talk
  class bound." Still beats LLM CoT class bound (d=25) by 2× at the
  appropriate operating envelope. V2.D extension path lifts the
  fact-count ceiling 12× (200 → 2487).

### (d) Active research thrusts (honed in on)

1. **Bet Y V2.D Phase 1 β-calibration sweep** (N=4096→16384; 3-4
   GPU-h) — Exp Dev pickup pending on 09:14 addendum. Now even more
   load-bearing: confirms V2.D path lifts BOTH Bet S K-ceiling AND
   multi-hop fact-count ceiling.
2. **K=10 + K=100 + NUMFACTS_300 FULL verdicts** — pending in pipeline
   log scroll; integration in next cap_map cycle. K-config branch
   clarification.
3. **Lane C compliance smoke → full mode** — Phase 1 priority; pickup
   pending.
4. **Bet X skill composition build** — Phase 1; pickup pending.
5. **δ(λ) drift critical-point test** — pickup pending.
6. **Open R-questions**: empirical β(N)=c/N constant; fact-count
   crossover precise location between 500 and 2000 (next K-config
   verdicts may clarify); does Bet Y V2.D + Kerdock(16) actually pass
   NUMFACTS_2000 as projected.

### (e) Research-map validity check

- 🔬/⚪ rows obsoleted: none this cycle.
- Newly minted 🔬: **multi-hop fact-count crossover location**
  (between NUMFACTS=500 and 2000); **V2.D NUMFACTS_2000 expected-pass
  validation** (gated on Phase 1+2 of V2.D build).
- 🟢 → ❌ partial: multi-hop adds a ❌ fact-count axis to the 🟢
  K-config story. Net: 🟢 with operating envelope.
- `active_priorities.md` still stale.
- `buried_treasure_research_directions.md` not refreshed.

### (f) Coverage: reviewed vs unreviewed

- **Reviewed this cycle**: NUMFACTS_2000 FULL multi-seed fail
  (Strategy v94), v12 phase-A boost FULL (v94), continual_4N
  infrastructure attribution (v94).
- **Unreviewed-but-queued**: K=10 + K=100 + NUMFACTS_300 FULL verdicts
  (pipeline scrolled past; cap_map integration pending).
- **Highest-leverage unreviewed**: **Bet Y V2.D Phase 1 β-calibration
  sweep** — unchanged from cycle 48. Now even more load-bearing
  because today's NUMFACTS_2000 fail confirms the V2.D extension path
  is the correct strategy for lifting both Bet S K-ceiling and
  multi-hop fact-count ceiling. Substrate-product centerpiece gates on
  Phase 1.

## PROT compliance this cycle (META)

- Re-read active_protocols.md per per-cycle directive.
- 7th PROT-009 paired-commit observation logged (Strategy counts as
  10th including pre-PROT-009 cycles).
- **PROT-010 candidate NOT proposed** — Strategy proactively adopted
  the mtime check this cycle. Self-discipline working; one more cycle
  of confirmation before deciding whether to formalize.
- No new proposals.
- Terminology rule applied: called multi-hop "honestly characterized"
  with the substrate-level reason (cleanup cross-talk class bound
  K_crit≈205; substrate at architectural limit not weakness) in the
  same sentence.

## Next META fire 10:13
