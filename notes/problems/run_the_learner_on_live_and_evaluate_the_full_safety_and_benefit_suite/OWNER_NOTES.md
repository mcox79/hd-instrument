---
owner_verdict: DONE
---

Problem: run_the_learner_on_live_and_evaluate_the_full_safety_and_benefit_suite — SOLVED (WIP until
owner_verdict: DONE). No hdlab/ touched (Q111 — default-off `learner_growth` diff proposed in SOLVED.md).
Glass-box, NO LLM at inference. Reverify: .venv/Scripts/python.exe verification/test_learner_live_canary_continual_growth.py  (7/7 PASS)

WHAT IT IS: first time the learner runs ON *continually* and live — grow word-meaning by reading 6 rounds
(5M→15M simplewiki), read-out fused through hdlab.cls_growth (keep-both, VERBATIM), and evaluate the FULL
safety+benefit suite at every round on TWO held-out downstreams: LitBank who-did-what (old fiction) AND a
MODERN held-out one I built (UD-EWT web text, 3739 items) — PLUS a distribution-shift round into a new domain
(biology textbook). The capstone only proved a fixed batch; the drift/anchor question only shows up over time.

BRAIN FRAME (drill changed the design). CLS keep-both is PINNED. The anti-drift lever is ONE parameter: the
slow anchor's CONSOLIDATION RATE eta. The offline "aligned" arm's drift (0.114→0.196) was an anchor-DECAY
artifact (running fusion halves the anchor each round), NOT a ceiling. Literature drill (routed to hdi_research)
verdict: a FROZEN original anchor is only PARTIAL fidelity — word meaning is continuously but SLOWLY updated
over a lifetime, so a hard freeze is the LEAST faithful anchor; the faithful one is a slowly-consolidated
small-eta EMA (neocortical slow timescale; Kumaran 2016 / mean-teacher). Honestly labeled: slow-anchor+fuse is
a COMPUTATIONAL-LEVEL SUBSTITUTE for synaptic consolidation (Fusi 2005 / EWC), not the mechanism.

RESULTS (full 5M→15M, 6 rounds, CI over items):
- ALL FIVE GATES PASS at the brain-faithful EMA anchor on held-out MODERN text (n=3040): SAFE corruption 0.116
  CI-upper 0.137<0.15; BENEFICIAL gain +0.110 CI[0.095,0.125] null p95 0.015; twin LOSES (−0.039); NO-DRIFT
  (anchor doesn't climb); ROLLBACK protects (good ACCEPT, naive+adversarial ROLLBACK; 16-seed random control
  fails, 0.127 vs gate 0.0); GENERALIZES (this IS the held-out modern result).
- STABILITY-PLASTICITY FRONTIER (the real deliverable): corruption AND gain both rise monotonically with eta.
  Modern corr[eta=0/.05/.1/.25/.5]=0.077/0.090/0.116/0.193/0.217. The strict-safe eta is CORPUS-DEPENDENT:
  ≤0.1 on modern, 0 (frozen) on old fiction.
- DISTRIBUTION SHIFT (lifelong stress test): reading a NEW domain (biology, 626k tok) adds ZERO CI-separated
  drift to the EMA anchor (corr 0.144→0.144 litbank; 0.116→0.119 modern) and benefit HOLDS/RISES (+0.070/
  +0.142), while the no-anchor DECAY control gets WORSE (0.221→0.266). The anchor holds across the shift.
- CAN-FAIL CONTROL fires: DECAY (eta=0.5) drifts CI-separated above the anchor (+0.077/+0.101).
- SEED-ROBUST (3 SVD seeds): gain/corruption stable, not a single draw.

HONEST NEGATIVE, located: on OLD fiction the EMA arm's corruption CI-UPPER (0.179) clips over 0.15, but the
POINT estimate (0.144) is under — a statistical-POWER / corpus-age artifact, not drift: the base barely knows
archaic verbs (OFF acc 0.073 → base-right n=403 → wide CI), the DECAY control at the SAME n is CI-separably
worse, and the brain's prioritized-protection mechanism (precision-weighted reliability arm) lowered corruption
(0.144→0.137) but did NOT rescue the strict bar. Conservative operating point on old/archaic text = frozen
anchor (safe 0.144); on modern text the faithful EMA is safe AND gains more (+0.010 over frozen, CI-sep).

HONEST BOUNDS: "live" = the faithful in-experiments realization of the wired read-out, NOT literally inside
read() (which consults no meaning store yet — the reader_meaning_channel gap; Q111 bars landing the wire).
"Compose with capable flags" is orthogonal-by-construction (different read-out). One learner family, one
language, three genres; modern golds are text I parsed, not an independent benchmark. Would withdraw the
strict-CI old-fiction safety claim first.

FOR STRATEGY (you land hdlab, Q111): (1) proposed default-off `learner_growth` flag on the meaning read-out —
fuse the grown store via cls_growth with an EMA slow anchor + rollback gate; byte-identical when off; DEPENDS
on reader_meaning_channel wiring the meaning path into read(). (2) Flipping growth ON by default is a separate
OWNER decision on this evidence: turn it on for MODERN reading in a watched/reversible mode at small eta; use
the frozen anchor on hard/archaic text. (3) AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT.md §2b is in SOLVED.md.
FOLLOW-ON PROBLEMS (mapped, with fidelity assessments): prioritized-replay / EWC confirmation-hardened anchor;
the reader_meaning_channel dependency for a truly in-read() canary.

FILES: experiments/exp_learner_live_canary_continual_growth_v1.py (self-test green); experiments/
_parse_shift_corpus_biology.py; verification/test_learner_live_canary_continual_growth.py (7/7);
notes/problems/<slug>/ SOLVED.md + research + supporting notes. (Inert leftover: SOLVED_DRAFT.md — a rm was
guardrail-denied; ledger reads only SOLVED.md, malformed:0.)
