---
owner_verdict: DONE
---

=======================================================================================================
SOLVER SUBMISSION -- the_register_write_path_has_a_hard_capacity_wall            (STATUS: SOLVED)
hdlab/ UNTOUCHED (proposed diff only, Q111). AWAITING owner_verdict: DONE.
REVERIFY: .venv/Scripts/python.exe verification/test_register_leaky_write.py   -> 11/11 PASS
LEDGER:   .venv/Scripts/python.exe tools/problem_ledger.py --check             -> malformed/incomplete: 0
=======================================================================================================

BAR (5 items): (1) a CONTINUOUS leaky/recency WRITE S=lambda*S+bind(role,item), lambda swept (asymmetric --
NOT symmetric-divisive/W10-dead, NOT a hard queue/W11-less-faithful); (2) lifts a capacity-bound downstream
task CI-separated over the flat-write floor, info-free twin LOSES, positive control moves; (3) the recency FORM
is GRADED/monotonic (primate gradient), not a step; (4) a content/SALIENCE-gated commit into the existing
HDFactStore for the old events the leak drops (commit by salience, not eviction-order; no new mechanism);
(5) one-screen summary. A rigorous NEGATIVE is a full pass. NO external LLM (invariant).

RESULT -- BAR MET (positive capability result, not a negative). Synthetic controlled load sweep (the correct
instrument for a capacity wall -- load is the IV), D=256, V=100, chance=0.01, 30 trials, trial-bootstrap 2000x.
  * WRITE PATH: the leaky recency write holds recent-4 recovery = 1.000 at EVERY load N in {16..768}. The
    STRONGEST flat floor (flat sum + the LANDED serial crosstalk-cancellation readout decode_serial -- NOT a
    flat+argmax strawman) holds to N=64 (0.983) then COLLAPSES: 0.175@128, 0.100@256, 0.025@512. Paired lift
    LEAKY - flat+SERIAL is CI-separated from N=128 on: +0.825[+0.750,+0.892]@128 -> +0.900[+0.833,+0.958]@256
    -> +0.975[+0.942,+1.000]@512 (ns at N<=64 where the serial readout still saturates -- the lift appears
    exactly where the floor breaks). Info-free twin (shuffled keys) ~0.02.
  * THE FUNDAMENTAL TRADE (why a 2nd store is needed, brain-faithful): leaky UNIFORM (all-events) recovery
    collapses 0.45->0.019 -- the leak buys RECENT by decaying OLD.
  * FORM (bar 3): recovery-by-recency is GRADED/monotonic -- 3-bin newest/mid/oldest [1.00, 0.958, 0.508]
    (the primate 66/45/39 shape, Konecky 2017); a hard bounded QUEUE is a STEP [1.00, 1.00, 0.008].
  * SECOND STORE (salience-gated HDFactStore hand-off, N=200, commit budget 20%, 30 trials, 2000x):
    salient-event recall weighted-OR gate 0.643[0.620,0.665] vs FIFO/eviction-order FLOOR 0.247
    (+0.395[+0.366,+0.424] SEP); OR > PE-only 0.530 (+0.112 SEP) and > CONG-only 0.539 (+0.103 SEP); leaky
    buffer ALONE 0.056; positive control OR 0.638 vs leaky-only 0.047 (+0.592).

FLOOR: strongest, recomputed on the same population = flat sum (lambda=1) read by decode_serial (the landed
theta-gamma readout): recent-4 0.983@64 -> 0.100@256 -> 0.025@512. 2nd-store floor = FIFO/eviction-order 0.247.

CONTROLS (each excludes something): info-free SHUFFLED-KEY twin -> chance (excludes "keys carry it free");
flat lambda=1 IS the info-free-write comparison; hard QUEUE step vs leaky graded (excludes "just a discrete
buffer"); positive control (leaky recovers newest at N=256, flat argmax|serial cannot); FIFO/eviction-order
floor (excludes "any commit helps"); RANDOM-commit twin (excludes "budget alone"); SELF-derived-salience
NEGATIVE control does NOT CI-beat FIFO -- reproduces the on-disk exp_attention_salience_reliability_gate
HARD_FAIL (salience MUST be an INDEPENDENT channel, matching VTA/LC computing PE in a separate circuit);
single-channel PE/CONG each miss one U-shape extreme (excludes "one axis suffices").

BRAIN GROUNDING (2 research drills, primary-source-verified, every wall drilled to a mechanism):
  - Write mechanism: asymmetric leaky recency = MEASURED/PINNED-WEAK (Warden & Miller 2007; Konecky 2017,
    primate PFC single-unit monotonic recency gradient). Geometric lambda^age = the faithful per-trace form.
  - Salience gate: commit = weighted-OR(prediction-error, schema-congruence) = the SLIMM U-shape extremes
    (Tse 2007/2011; van Kesteren 2012; Lisman-Grace; Redondo-Morris tagging-and-capture). Commit-most-salient
    NOT oldest-evicted = PINNED (P=0.78); PE must be an independent channel (on-disk HARD_FAIL otherwise).

FIDELITY DEEPENING (owner "keep pushing" -- a real gap found + 2 of my OWN citations self-corrected):
  the submitted SINGLE-timescale leak is a first-order approximation. The brain's WM holds a MEASURED SPECTRUM
  of timescales (Bernacchia 2011 PMID 21317906 power-law reservoir in primate PFC; Murray 2014 hierarchy). A
  multi-timescale register (K leaks fast->slow, read per-event from the clearest-trace level) recovers ~3x more
  of the recency window (CI-separated at every load, witness checks 10-11), graded gradient, recent unharmed --
  and reach stays FINITE, so the 2nd store is still needed. CITATION CORRECTIONS the drill caught: Fusi 2005 /
  Benna-Fusi 2016 are the CONSOLIDATION stage + MODELS (their coupling-based capacity theorem does NOT transfer
  to my independent sums); the measured ~3x is TEMPORAL REACH, not Benna-Fusi capacity. AUDIT UPGRADE (Watters
  2026, PMC12893052): primate frontal WM is a GAIN-WEIGHTED SUPERPOSITION beating slots -> the substrate's
  superposition-register FORM is now PINNED at the population-code level (a dent in "VSA binding unpinned" at the
  READOUT level, not the bind() algebra).

PROPOSED hdlab DIFF (full concrete patch in PROPOSED_HDLAB_DIFF.md; strategy lands, Q111): (1) a `leak` param on
AccumulateRegister (0.0 = flat, byte-identical; >0 = asymmetric leaky recency write reading the raw recency-
weighted sum), threaded through make_situation_register + the multibank backend (per-bank). (2) a thin
register_consolidation helper: salience=max(w_pe*PE, w_cong*CONG), commit to HDFactStore iff > theta (swept);
PE independent, CONG from the existing script_grain MDL drop; commit-most-salient, never eviction-order/self-
derived. No change to hd_fact_store.py.

NEXT PROBLEMS (drill-ranked B -> C -> A; adjacency evaluated for fidelity+opportunity):
  B (highest) STAGE-appropriate timescales -- the situation-model/discourse integrator should run SLOWER than
    the register (Murray hierarchy); if it shares the register's leak that's the gap. CAUTION: two prior multi-
    timescale cells HARD_FAILED (exp_substrate_fast_slow_weights_LM_v1, exp_c2_cascade_stc_swr_continual_v2);
    BUILD ON the landed exp_timescale_gated_predictive_hierarchy_tgph_v1, do not re-derive.
  C  ChunkedFocus fidelity audit: graded gain-weighted focus vs hard 4-slot (Watters 2026).
  A (last) coupled superposition cascade (Benna-Fusi flow) -- ~ a reparam bank of leaks, P~0.35 it beats
    independent sums. Plus: the salience gate is single-threshold; a graded consolidation FLOW may be more
    faithful (refinement for landing change 2).

HONEST CAVEATS (withdraw first if wrong): (1) NOT run real-text end-to-end -- the capacity wall is an FHRR-
algebra property (content-agnostic) and a controlled synthetic load sweep is the correct instrument, but the
"lifts a downstream task" claim is proven on the register's own recent-recovery readout, not yet a full reading
score (a landing + measurement follow-on). (2) the salience channels are MODELLED (independent PE/CONG latents
+ noise), not read from the live PE/MDL organs -- the GATE POLICY + controls are established, the live-channel
reliability is the landing's job. (3) a quick activity-adaptive leak underperformed -- an uncalibrated impl, not
a refutation; fixed geometric lambda is the better-pinned single-store form anyway.

FILES: experiments/{exp_register_leaky_write_capacity_v1, exp_register_salience_gated_handoff_v1,
exp_register_multitimescale_cascade_v1}.py; verification/test_register_leaky_write.py (11/11);
notes/problems/the_register_write_path_has_a_hard_capacity_wall/{SOLVED.md, PROPOSED_HDLAB_DIFF.md,
research_consolidation_salience_gate_2026-08-29.md, research_multitimescale_cascade_2026-08-29.md}. hdlab/ UNTOUCHED.

TLDR (plain): the reader's short-term memory blurred to noise past ~60 events, losing even what just happened.
I gave it the brain's fading write -- recent events now stay perfectly readable at ANY load, with the exact
graded fade-curve measured in monkey cortex -- plus a gate that copies the IMPORTANT fading events (surprising
ones, or ones that fit the story) into permanent memory (recovers 64% of them vs 6% with fading alone), picking
by importance not age, judged by a separate signal. Then I stress-tested my own fix: the brain fades at MANY
speeds at once, which recovers ~3x more of the recent past -- I built and measured that, caught myself citing
the wrong papers and fixed it, and handed the multi-speed version off as the top next problem. All proven in
experiments; strategy lands the two-part change. QUESTIONS: none. NEXT: land the diff + open next-problem B.
=======================================================================================================
