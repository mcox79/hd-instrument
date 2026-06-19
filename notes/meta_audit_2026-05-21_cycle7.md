# META audit — 2026-05-21 cycle 7 (cron fired at 12:43)

Snapshot in chat is primary deliverable; this captures audit-side findings.

## Activity since cycle 6 (12:15 → 12:45)

- Strategy cycles 21-22, cap_map v33 → v35 (skipped v34 intermediate).
- Research published R6 (Kerdock decoder implementation) — last
  outstanding R-question from cycle 1.
- Substrate noise tolerance ✅ at σ ≤ 16.0 (hardware-deployment claim).
- 6 smoke→full confirmations (zi/zj/zk/zl/zn/zo).
- **Experiment Dev paused 35+ min** (no decision log entry since 12:05).
- New experiment wave14zp_kerdock_v8_32coset_retry started at 12:44
  (Kerdock follow-up, NOT one of the three Strategy-requested items).

## Drift findings

### Finding 1 — Cross-session coordination gap (FILE PROPOSAL 6)

**Observation**: Strategy filed `strategy_request_to_experiment_dev_2026-05-21.md`
at 12:06 with concrete specs + multi-probe criteria for Bet B, Bet F,
and multi-hop FHRR. Experiment Dev's last decision log entry is 12:05
(38 min before this audit). GPU queue was empty 12:14:56 → 12:44:37
(30 min idle), violating the user's continuous-pipeline cadence.

**Diagnosis**: Strategy is on /loop dynamic; Research is on /loop 15min;
META is on cron 30min. Experiment Dev appears to be user-triggered
only. Without an automatic cadence, Experiment Dev can't reactively
consume incoming request files; the system has a coordination hole.

**Severity**: medium-high. The system's whole architecture assumes
self-coordination via files; if one session lacks cadence, the
infrastructure has a single-actor bottleneck.

**Action**: Filed **Proposal 6** — Experiment Dev sets up /loop with
slash-command pattern (PROT-003), checks queue depth + request files
each fire, queues from active_priorities or request files when depth
is low.

### Finding 2 — Smoke ranges may be systematically conservative

**Observation**: Two cases this hour where smoke-range testing produced
false negatives:
1. Bet H sketch #3 (repetition penalty): smoke at narrow penalty range
   → labeled closed; full sweep → works at p ≥ 1.0
2. Noise tolerance: smoke at σ=1.0 → "passes"; full at σ ∈ {1, 2, 4,
   8, 16, 32} → tolerance budget actually 16, not 1

Strategy noted the pattern in cycle 21: "smoke ranges have been
generally too conservative."

**Severity**: low (Strategy caught both reversals; PROT-004 now
prevents smoke-only closures). Worth a one-line addition to PROT-004
or the prereg template, but not urgent.

**Action**: not filing a new PROT this cycle. Will revisit if a third
false-negative pattern appears.

### Finding 3 — R-backlog cleared

**Observation**: R6 publication completes the cycle-1 R-question
backlog. All of R1-R12 now reviewed with real external lit scans
(post-R1-audit discipline).

**Action**: not META's place to direct Research's next focus, but
flagged in the snapshot's coverage section. Research is unblocked to
pivot to buried-treasure waves (15/16/17/13.4) or to generate
R-questions from new active bets.

## Reinforcement

- **Strategy**: clean cycle 21/22 work; honest documentation of
  Experiment Dev pause; deferred to META for structural fix per
  single-writer rule.
- **Research**: R6 landed; backlog cleared. R-side of the system is
  caught up.
- **Experiment Dev**: when it finally fires (wave14zp at 12:44), it's
  building substantive work (Kerdock v8 retry). The pause appears to
  be cadence-bound, not motivation-bound.

## Open items for next META fire (13:13)

- Did Experiment Dev consume Strategy's request file (Bet B / Bet F /
  multi-hop FHRR queued)?
- Did Bet C v8 32-coset full mode land?
- Proposal 6 user decision?
- If quiet: heartbeat.
