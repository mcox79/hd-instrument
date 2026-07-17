# Pre-reg: read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1

Bands fixed BEFORE running (also embedded in the cell docstring PRE-REG block). Cell:
`experiments/exp_read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1.py`.

## Question (the LAST open state-of-mind door)
Does an HD superposed discourse state earn a real KEEP in the COHERENCE SCALAR-SCORE mode? Accumulate M
propositions (role-filler bindings) into a fixed-size HD bundle; compute a GRADED O(1) similarity (normalized
Hermitian inner product) of a NEW proposition against the whole bundle (Kintsch construction-integration /
BEAGLE). The membership-decode crosstalk ceiling (Frady/Kleyko/Sommer) does NOT apply to a SCALAR readout, so
this is the one mode structurally distinct from the (CLOSED-symbolic) membership door. TASK: discriminate a
COHERENT continuation from a CONFABULATION (contradictory) one by the coherence SCORE, at EQUAL BIT-FOOTPRINT
under genuine overload.

## Design (one variable = the coherence representation)
- Discourse = D_n distinct facts (agent, patient) over 256x256 pools; stream = REPEAT*D_n mentions (coverage +
  recency + frequency).
- q+ = a real fact; q- = a MINIMAL-PAIR CONFABULATION (same agent, a topical role-valid patient, pairing never
  asserted) -> a CONJUNCTION violation. q0 = off-topic (D1 control).
- PRIMARY arm hd_bind: chunk = E[a](x)E[p] (native FHRR bind, PRESERVES conjunction); B = sum_f freq_f*chunk_f;
  score = Re<chunk(q),B>/N. FAIR competitor sym_prop_evict_eq: exact (a,p) tuple store, LRU-evict at C_eq;
  score = 1 if fact retained else 0. Both at IDENTICAL 8*N=8192-byte footprint.
- CONTROLS (conjunction-blind, must be ~0.5 at overload): hd_add (E[a]+E[p], marginal) + sym_pair_marginal.
  Extra bar: sym_prop_evict_2x (2x footprint). Floor: random.
- Metric = rank-AUC (threshold-free) separating q+ from q- (D2 primary) / q+ from q0 (D1 control).
- Overload knob D_n / C_eq in {0.5, 1, 2, 4, 8, 16}; REGIMES = {aggregate (realistic whole-discourse
  coherence, HD's niche), recent (symbolic corner)}. seeds: smoke 2 / full 5. EXPECTED_N_UNITS = seeds*|D|*|regime|.

## Bit-honest footprint (v4-VET discipline; symbolic given its fair equal-BIT budget, cheapest = hardest for HD)
hd bundle = 8N = 8192 bytes (constant in M). symbolic prop = 4 bytes (2x 2-byte ids). C_eq = 8N//4 = 2048;
C_2x = 4096. Codebook / id space amortized + excluded from both state footprints SYMMETRICALLY.

## Bands (envelope-fail)
- HARD_PASS (HD earns a real keep): at >=1 overload D_n (>C_eq), AGGREGATE regime, mean(AUC_D2[hd_bind] -
  AUC_D2[sym_prop_evict_eq]) >= 0.03 AND (mean - 1std) > 0 across seeds AND AUC_D2[hd_bind] >= 0.55.
  HP_SCOPE: hd_bind only.
- HARD_FAIL (settles the ENTIRE state-of-mind overlay = SYMBOLIC): at ALL overload D_n in BOTH regimes, hd_bind
  does NOT beat sym_prop_evict_eq (margin < 0.03 or negative). First-class fully-settled result.
- MIDDLE_BAND: HD wins only in a corner (recent regime, or extreme-overload, or non-robust).
- INVALID_TEST_DESIGN gates: random AUC in [0.4,0.6]; hd_add + sym_pair_marginal ~chance at overload
  (conjunction-sensitivity); sym_prop_evict_eq NOT saturated at top overload aggregate (eviction bites) AND
  exact at low overload (real baseline); D1 topical control hd_bind AND sym >= 0.70; arms_differ.

## Design-gate schema fields
- can_fail_both_ways: TRUE (HD-win reachable per-seed at x4/x8; symbolic-win at low overload + recent).
- real_baseline: sym_prop_evict_eq (exact at low overload AUC=1.0), NOT strawman.
- difficulty_on: overload forces eviction (frac_retained < 1 at D_n > C_eq).
- one_variable: hd_bind vs sym_prop_evict_eq share facts/stream/continuations/footprint/seeds.
- crlb / discriminator_reachability: TRUE (THEORETICAL crossover near 4x; HD SNR = freq/sqrt(M/N), sym AUC =
  0.5 + 0.5*C/D_n). calibration_check: default_ok (threshold-free rank-AUC; no tuning). final_metrics_atomicity:
  tmp_replace. cardinality_ok: TRUE. deterministic_seeding (F.5): fixed-int seeds; no hash()/list(set()).
  storage: no_storage (validity-preflight F.2/F.3/F.4 not_applicable; F.5 honored). progress_logging:
  print_flush_true. P estimate: P=0.40 HYPOTHESIZED (HARD_FAIL/MIDDLE more likely than HARD_PASS).

## OUTCOME (this inline run; CLAIM-VET-pending, NOT self-declared chain-grade)
VERDICT = HARD_FAIL (5 seeds). MEASURED@data/exp_read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1/metrics.json.
hd_bind NEVER robustly beats sym_prop_evict_eq by >=0.03 at equal footprint: sym exact (1.0) and dominant up to
x2; TIE at x4 (+0.000 +-0.046); HD edges +0.029 (+-0.024) at x8 and +0.023 (+-0.024) at x16 -- but below the
0.03 bar AND only where BOTH arms have collapsed toward chance (0.53-0.59). Recent regime: symbolic 1.0
everywhere. Conjunction-blind controls pinned ~0.50 (discriminator is genuinely conjunction-sensitive). CAVEAT
(interpretation, VET-pending): synthetic integer-id corpus; the honest structural limiter is the brutally cheap
4-byte symbolic proposition (equal bytes let symbolic store ~2048 exact facts vs HD's one lossy bundle) -- a
VET should confirm 4 bytes/prop is the right honest unit. Read: the coherence-scalar door closes SYMBOLIC too;
membership AND coherence both go to the symbolic exact-binding layer -> state-of-mind overlay is SYMBOLIC.
