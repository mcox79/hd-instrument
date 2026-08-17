# SHORTLIST + VERIFIER -- does a real (non-oracle) rejector buy anything on the read-out instrument?

Cell: `experiments/exp_readout_shortlist_verifier_v1.py`. Full run landed, 180.6s (elapsed_s in
metrics), commit to follow this note. `data/exp_readout_shortlist_verifier_v1/metrics.json`.
n=3994 items, N_BOOT=10000, landed OPEN pool, WordNet generous gold, `tools/floor_battery` scorer.

**FILENAME.** `experiments/exp_propose_reject_retrieval_v1.py` is a BLOCKED PATH
(`notes/COMPACTION_HANDOFF_2026-08-17.md:153`) -- not tested, not touched. This cell is the composed
propose-and-reject cell under a distinct name, as authorised.

## 0. THE THREE CEILING FIGURES -- VERIFIED OFF DISK, THEN RE-VERIFIED INSIDE THIS CELL'S OWN REGRESSION GATE

Read directly from `data/exp_readout_ceiling_diagnosis_v1/metrics.json` before writing a line of
this cell: `S2_WHERE_DOES_THE_ANSWER_RANK.curves.EXACT_KEY_COSINE.hit_at_k_optimistic` = `{"1":
0.04807, "5": 0.17151, "10": 0.26039}`; `F_CONSTANT_PROTOTYPE` hit@1 = `0.13896`. All four numbers
are ALSO regression-gated (tol 5e-4) inside this cell's own `run()`, recomputed from scratch on the
full population, and all four PASSED:

| quantity | expected (verified off disk) | this cell recomputed | PASS |
|---|---|---|---|
| partial-cue hit@1 (G0) | 0.0223 | 0.02228 | yes |
| exact-key hit@1 | 0.04807 | 0.04807 | yes |
| exact-key hit@5 (**the k=5 ceiling**) | 0.17151 | 0.17151 | yes |
| exact-key hit@10 (**the k=10 ceiling**) | 0.26039 | 0.26039 | yes |
| exact-key addressing | 1.0 | 1.00000 | yes |
| F_CONSTANT_PROTOTYPE (**the binding floor**) | 0.13896 | 0.13896 | yes |

## 1. THE SHORTLIST HIT-RATE CURVE, REPORTED FIRST AS INSTRUCTED (gates everything below)

Two regimes, computed by the same `hit_at_k_curve` primitive (imported from
`exp_readout_ceiling_diagnosis_v1`, never reimplemented):

| k | 1 | 5 | 10 | 20 | 50 |
|---|---|---|---|---|---|
| **EXACT-KEY oracle ceiling** (best case, addressing solved) | 0.04807 | 0.17151 | 0.26039 | 0.38608 | 0.55658 |
| **PARTIAL-CUE oracle ceiling (THE REAL PRECONDITION)** | 0.02228 | 0.08838 | 0.14171 | 0.22183 | **0.37581** |
| per-item random-ranking null (cue-independent, caveat-free) | 0.01009 | 0.04779 | 0.08972 | 0.16002 | 0.30406 |

**Pre-registered threshold: PRECOND_ABS_THRESHOLD = 0.05 at k=50, written before this cell ran.**
`0.37581 >= 0.05` -- **PRECONDITION_FAILURE = False.** The proposer is right often enough, under the
real partial cue, for a shortlist of 50 to contain the gold on **37.6% of items** (vs 4.8x less,
2.2%, for today's single argmax) -- **7.5x the incumbent's own hit@1**, and still clearly above its
own random-ranking null at every k (e.g. 0.376 vs 0.304 at k=50). **STOP-IF (ii) did NOT fire.**
Rejector work is licensed.

## 2. ARM-BY-ARM MARGINS -- CI half-width and analytic null half-width beside every one

Binding floor (recomputed on this population, on the PARTIAL cue, all four floors): F_ORTHOGRAPHIC
0.08731, F_FREQUENCY 0.01853, F_SCRAMBLE 0.01077, **F_CONSTANT_PROTOTYPE 0.13896 (binding)**.
`R2/R3` NONE clear it; `R1` NONE clear it either -- **STOP-IF (i) did NOT fire, no arm here is a
capability win.**

| arm | acc | vs G0 (0.0223) | vs matched N1 | vs binding floor (0.1390) |
|---|---|---|---|---|
| G0_ARGMAX (incumbent) | 0.0223 | -- | -- | -0.1167, BELOW |
| R1_ATTESTATION k5 | 0.0306 | **+0.0083 [0.0036,0.0132] hw=0.0048 ABOVE** | **+0.0058 [0.0009,0.0108] hw=0.0050 ABOVE** | -0.1084 BELOW |
| R1_ATTESTATION k10 | 0.0342 | **+0.0120 [0.0066,0.0175] hw=0.0054 ABOVE** | **+0.0157 [0.0101,0.0213] hw=0.0056 ABOVE** | -0.1047 BELOW |
| R1_ATTESTATION k20 | 0.0375 | **+0.0152 [0.0094,0.0212] hw=0.0059 ABOVE** | **+0.0232 [0.0174,0.0291] hw=0.0059 ABOVE** | -0.1015 BELOW |
| R1_ATTESTATION k50 | 0.0409 | **+0.0187 [0.0125,0.0250] hw=0.0063 ABOVE** | **+0.0274 [0.0215,0.0334] hw=0.0060 ABOVE** | -0.0980 BELOW |
| R2_PROFILE k5 | 0.0193 | -0.0030 NOT_SEPARATED | -0.0055 NOT_SEPARATED | -0.1197 BELOW |
| R2_PROFILE k10 | 0.0195 | -0.0028 NOT_SEPARATED | +0.0009 NOT_SEPARATED | -0.1195 BELOW |
| R2_PROFILE k20 | 0.0190 | -0.0033 NOT_SEPARATED | +0.0047 NOT_SEPARATED | -0.1200 BELOW |
| R2_PROFILE k50 | 0.0190 | -0.0033 NOT_SEPARATED | **+0.0055 [0.0003,0.0108] hw=0.0053 ABOVE** | -0.1200 BELOW |
| R3_COMBINED beta0.25 | 0.0223 | +0.0000 NOT_SEPARATED | **+0.0080 ABOVE** | -0.1167 BELOW |
| R3_COMBINED beta0.50 | 0.0261 | +0.0038 NOT_SEPARATED | **+0.0118 ABOVE** | -0.1129 BELOW |
| R3_COMBINED beta0.75 | 0.0304 | **+0.0081 [0.0022,0.0142] ABOVE** | **+0.0161 ABOVE** | -0.1086 BELOW |

Analytic null half-widths (0.0039-0.0063) sit close to the CI half-widths throughout -- these are
real, well-powered margins, not underpowered noise.

**THE HONEST FOURTH READING, not one of the five pre-registered stop-if branches: R1_ATTESTATION
beats BOTH G0_ARGMAX and N1_RANDOM_REJECTOR, CI-separated, at every swept k, growing with k (+0.0083
at k5 to +0.0187 at k50 over G0) -- a real, small, non-random signal -- but never comes close to the
binding floor (still ~3.4x-3.7x short). R3_COMBINED inherits this at higher beta (more R1 weight);
R2_PROFILE mostly ties G0 and only barely beats N1 at k50.** This is not STOP-IF (i) (floor not
cleared), not (iii) (R1 DOES beat N1, so the gain is not merely "any shortlist pick beats the
incumbent" -- N1 itself is consistently at or below G0), and not a capability win. It is evidence
that the coordination-pattern signal carries real information the proposer and a random shortlist
pick do not, at a magnitude far too small to matter on this instrument.

## 3. N1_RANDOM_REJECTOR and N2_PROPOSER_AS_REJECTOR

**N1 (floor that matters most):** 0.0248/0.0185/0.0143/0.0135 at k=5/10/20/50 -- BELOW or roughly at
G0 (0.0223) throughout, confirming a naive "any pick from the shortlist helps" story is false; R1's
margin over N1 is therefore a real property of R1's signal, not an artifact of the shortlist alone.

**N2 (validity arm):** verified to reduce to G0_ARGMAX **bit-for-bit** (`np.array_equal` assertion,
not merely a close match) at every k in (5,10,20,50) -- both in the main run and pre-registered in
`self_test()` on synthetic data at k in (1,3,5,9). **STOP-IF (iv) did not fire; the cell is not
void.** This is mathematically guaranteed (a shortlist derived from a score always contains that
score's own top-1) and is asserted, not merely observed.

## 4. SIGNAL INDEPENDENCE FROM THE PROPOSER -- measured, not merely claimed

Pearson correlation of each rejector's raw score against the proposer's own score, over the shared
shortlist entries (paired, n=19,970 to 199,700 depending on k):

| | r vs proposer (k=5) | r vs proposer (k=50) |
|---|---|---|
| R1_ATTESTATION | **0.108** [0.094,0.123] | **0.109** [0.102,0.117] |
| R2_PROFILE | **0.613** [0.606,0.620] | **0.589** [0.586,0.591] |

Both are CI-separated ABOVE zero (some positive relation is expected -- both partly derive from the
same underlying vocabulary and store), but R1 is only weakly coupled to the proposer (r~0.11) while
R2 is strongly coupled (r~0.59-0.61), because R2 is literally a profile built FROM the same store
matrix the proposer scores against. **This is the likely mechanism behind section 2's asymmetry**:
R1 behaves like a genuinely separate verifier in practice; R2, despite being a mathematically
distinct object (profile-of-profile vs raw cosine), tracks the proposer too closely to add much.

## 5. ORTHOGRAPHIC AND WORD-LENGTH CORRELATION (standing rule 12)

Checked on every arm that cleared anything (beat the floor or beat N1): all 4 R1 arms, R2@k50, all 3
R3 betas.

- **Orthographic:** every arm NOT_SEPARATED from zero (r=0.001 to 0.025, CIs straddling zero). Mean
  trigram-cosine of winners 0.024-0.029, nowhere near the orthographic floor's own reference (~1.0).
  **No arm clears anything via a disguised spelling channel.**
- **Word length:** CI-separated **BELOW zero** for most arms (e.g. R1@k5 r=-0.036 [-0.065,-0.008],
  R1@k50 r=-0.044 [-0.075,-0.012], R2@k50 r=-0.037 [-0.065,-0.008]) -- R1@k20 and R1@k10 are the
  two exceptions at NOT_SEPARATED. **A negative correlation is the opposite of a length-gaming
  story** (gaming would look like a positive correlation, i.e. gains concentrated on longer/fancier
  words as a crude register proxy); here gains skew slightly toward SHORTER winning words. Reported
  in full rather than only checking the "ABOVE" direction, per rule 12's own instruction not to
  adopt a floor (or here, a margin) without understanding it -- but it does not constitute the
  leakage rule 12 is written to catch.

**STOP-IF (v) did NOT fire.**

## 6. WHICH STOP-IF FIRED

None of the five cleanly. **(ii) did not fire** (precondition curve well above threshold). **(i) did
not fire** (no arm clears the binding floor). **(iii) did not fire** (R1 beats N1, so its gain over
G0 is not "any shortlist pick would have done it"). **(iv) did not fire** (N2 reduces to G0
bit-for-bit, verified). **(v) did not fire** (no orthographic or positive length leakage). The
landed verdict string is `NO_REAL_REJECTOR_CLEARS_AND_NO_PRECONDITION_FAILURE__NULL_ON_THIS_ARCHITECTURE`,
with the honest fourth reading from section 2 recorded alongside it rather than folded into a bare
NULL label.

## 7. DOES A VERIFIER THAT IS NOT THE GENERATOR BUY ANYTHING HERE?

**A qualified, small yes for R1, a no for R2, on this instrument.** The architecture is validated
(N2 reduces to G0 exactly; the shortlist genuinely contains recoverable signal per section 1) and
one of the two candidate rejector signals (coordination-pattern attestation) produces a real,
CI-separated, non-frequency-shaped, non-orthographic lift over both the incumbent and a random pick
from the identical shortlist -- growing with shortlist size (+0.008 at k=5 to +0.019 at k=50 over
G0). But the lift is roughly an order of magnitude too small to approach the binding floor (accuracy
0.041 vs floor 0.139), so **this is not the "first genuine read-out win" the dispatch's STOP-IF (i)
was watching for.** The second candidate signal (second-order profile) mostly fails to separate from
the incumbent at all, and the measured correlation in section 4 gives a concrete reason why: it
tracks the proposer's own score too closely (r~0.59-0.61) to act as an independent verifier, unlike
the attestation signal (r~0.11). **The result licenses one narrow, honest continuation**: a rejector
signal that is TRULY independent of the store (as R1 is, being built from raw corpus text rather
than the vector store) is where whatever headroom exists in this architecture lives; a signal built
from the same matrix the proposer already scores (R2) adds little regardless of its formal
mathematical distinctness. It does **not** license building further on this specific R1 implementation
as-is -- its own magnitude is far too small -- and per the brain-fidelity shelve/revival criterion
declared in the cell's docstring, the honest next step (not taken here, a Director decision) is a
genuine register/formality rejector signal, not a bigger sweep of this cell's own two proxies.

## 8. WHAT THIS RUN DOES NOT CLAIM

- No number here crosses scorers, pools or populations; everything is hit@1 tie-corrected over 5,491
  anchors on 3,994 items, the landed OPEN pool, WordNet generous gold -- identical to the diagnosis
  cell's own population by construction (same `RCD.build_population()` call, imported not
  reimplemented).
- G1_SHORTLIST_ORACLE is an ORACLE ceiling and is never quoted as, or mistaken for, a capability.
- `verdict_bar_check.py` was not additionally invoked; STOP-IF logic is native to the cell, evaluated
  arm-by-arm in `MARGINS`/`STOP_IF`, not delegated to a tool with four false passes on record.
- This cell does not wire anything into `hdlab/` -- promotion is the Director's call.
- The K1_KNOWN_ANSWER "own-address preference" numbers for R1/R2/R3 (all 0.0) are reported as
  INFORMATIONAL, not a failed gate: both signals explicitly exclude self-comparison by construction
  (documented in the cell), so a "must prefer its own identity" bar does not apply to them. The
  BINDING K1 gate (KA_SELF_ADDRESS on the store, 1.0000, hard-enforced) passed.

## Organ reuse, runtime-witnessed

`exp_readout_ceiling_diagnosis_v1.build_population` / `.hit_at_k_curve` / `.random_ranking_hit_at_k`
/ `.install_grounded_similarity_tripwire` / `.self_test` / `._halfwidth`; `exp_readout_second_order_v1
.second_order_scores` / `.self_test`; `exp_cue_to_store_translation_v1` cache/aux loaders + ruler
gate; `exp_cue_binarised_readout_transfer_v1.pearson_ci_bootstrap`; `exp_definitional_grounding_v5
.load_corpus_v5`; `tools/floor_battery` (every floor, the scorer, the bootstrap); `hdlab
.reading_grounding_loop.normalize_lemma`; `tools/exp_checkpoint`. All IMPORTED, none edited
(`ORGAN_REUSE_RUNTIME_WITNESS` in the metrics, `sys.modules`-witnessed, not grep).

## Prior-work check (standing rule)

`bash tools/substrate_query.sh "propose and reject shortlist verifier read-out rejector attestation"`
returned no output within 20s, consistent with the documented `hd_director_kb_continuous_ingest`
livelock recorded elsewhere this session. Fell back to enumeration: `ls experiments/` filtered on
readout/rerank/hub/csls/normal/argmax/rank/write/second_order/profile/selection/shortlist/verifier/
reject/propose/attest/coordination. No existing cell operates a propose-and-reject architecture on
THIS instrument (the WordNet-gold 5,491-anchor open-pool read-out). `exp_feeling_match_rejector_v1`
validates the ATTESTATION/PROFILE-REJECTOR concepts on a DIFFERENT population (verb-argument
slot-filling) and is credited as the source of those concepts, not code-reused (its data structures
do not transfer); this cell builds fresh, population-appropriate implementations of both signals.
This is not a rediscovery.
