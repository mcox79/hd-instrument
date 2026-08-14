# Pre-registration: composed-chain read-out (whiten / pinv-write / coarse-to-fine)

- anchor: `exp_composed_chain_readout_v1`
- prereg committed BEFORE the run. Stage-0 pre-check is a SEPARATE cell
  (`exp_codebook_geometry_precheck_v1`) already committed at `aea33edf2`.
- date: 2026-08-14

## 0. What is being tested

The cert ledger contains four separately-graded stages that no cell has ever composed:

| stage | source cell | its headline (VERIFIED against its own metrics.json) |
|---|---|---|
| whiten | `exp_substrate_last_token_vs_whitening_mean_pool_v1` | capacity 0 / 40 / 122 raw / mean-pool+whiten / last-token+whiten; HARD_PASS |
| pinv write | `exp_hebb_vs_pseudoinverse_write_rule_v1` | at N=512 hebb alpha_c=0.050 pinv alpha_c=0.400 = 8.00x; HARD_PASS |
| coarse-to-fine | `exp_encoder_retained_trace_requery_coarse_to_fine_v1` | recall 0.992 vs 0.992 CEILING, shortlist_hit@0.1=1.000; HARD_PASS |
| near-dup diagnostic | `exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1` | 54/241 atoms (22.4%) with NN>0.99; top pair cos 1.0000; HARD_PASS |

PRIMARY QUESTION: does the composed chain raise the ANCHOR SCORES -- i.e. the target's RANK --
not merely "does it beat argmax". Last night's SNR wall (`exp_sharpening_readout_sister_separation_v1`,
SMOKE_n600) closed cleanup-RULE fixes as a class. This chain is UPSTREAM of that wall: it changes
what the codebook contains and how it is written.

## 1. Baseline, stated exactly and with its scope

From `data/exp_sharpening_readout_sister_separation_v1_SMOKE_n600/metrics.json`:

- `snr_diagnostics.median_rank_of_target_among_all_anchors` = **84.0**
- `snr_diagnostics.n_anchors` = **647**
- `snr_diagnostics.frac_target_outside_top50` = **0.60** (so top-50 fraction = **0.40**)
- `snr_diagnostics.frac_target_rank1` = **0.098333**
- 2AFC `S0` = **0.7083**; scramble 0.4500; frequency 0.5000
- `floors.between_anchor_draw_sd_S0` = 0.030641 from **n_draws = 2**

SCOPE CORRECTION, load-bearing: this baseline is a **SMOKE** run at **647 anchors / n=600 items**.
It is NOT the 5491-anchor space, and its open-vocab hit@1 is 0.0983, NOT the 0.0480 of
`exp_grounding_readout_known_answer_v1` (5491 anchors, n=4000). The two numbers describe DIFFERENT
anchor-set sizes and must never be compared to each other. This cell reproduces the 647-anchor
configuration EXACTLY so that 84/647 and 0.40 are legitimate comparators, and separately sweeps
anchor-set size.

`between_anchor_draw_sd` from n_draws=2 is not a usable dispersion estimate. This cell uses
**n_draws >= 4** and treats any arm delta smaller than that sd as NOT A GAIN.

## 2. What the live read-out actually does (READ, not assumed)

Read from `hdlab/reading_grounding_loop.py`:

- `ConceptSpace.observe` = `self._sums[lemma] += ctx_vec`. The write rule is **pure Hebbian
  accumulation**.
- `ConceptSpace.anchor_matrix` returns those raw sums (`GRADED_COMPARATOR` ON since 2026-08-14;
  previously `np.sign` of them).
- `canonicalize_fast` = `sims = (mat @ nb) / (norms * nn)` then `argmax`. **Plain cosine argmax.**

Therefore, of the four stages: **whitening, pseudoinverse write, and coarse-to-fine read are ALL
ABSENT from the live path.** The one partial exception is `ReadoutConfig` FIX 2
(`anchor_background`), a per-anchor mean/sd z-score = a **diagonal** approximation to whitening; it
is OFF by default and is NOT full covariance whitening. No stage is live.

CORRECTION TO THE TRIAGE NOTE: it flags `experiments/exp_grounding_readout_known_answer_v1.py` as
absent from disk. **It is present** (46379 bytes, 2026-08-14 03:29) and its metrics.json is on disk.

## 3. Arms (built so each stage is separable)

All arms score the SAME items against the SAME anchor set; only the scoring map changes.
`K` = anchor matrix (n_anchors x d), `Q` = query context vectors (n_items x d).

- **A0_BASELINE** -- `cos(Q, K)`, byte-equivalent to `canonicalize_fast`. The live path.
- **A1_WHITEN** -- ZCA whitening fitted on K's covariance, applied to BOTH K and Q, then cosine.
- **A2_PINV** -- pseudoinverse (projection) write: `S = Q K^T (K K^T + lambda I)^-1`. This is the
  heteroassociative form of `W_pinv`'s projector; it decorrelates anchors against each other rather
  than reading each independently as Hebb does.
- **A3_C2F** -- coarse random projection to D_COARSE=128, shortlist top-10% of anchors, fine
  rescore with the A0 cosine inside the shortlist.
- **A4_FULL** -- whiten -> pinv -> coarse-to-fine, composed.
- **FLOORS** -- `SCRAMBLE` (deranged queries, same items), `FREQUENCY` (rank by corpus count;
  the sharpening cell measured 0.5000 at 2AFC and the known-answer cell 0.4943; the task brief's
  0.4803 is from neither -- the measured value is reported, not assumed),
  and `BETWEEN_DRAW_SD` over >= 4 independent anchor/eval splits.

Paired bootstrap CIs on every delta (arms share items), 5000 resamples, fixed seed.

## 4. PRE-DECLARED EXPECTED FAILURE MODES (declared BEFORE the run, not discovered after)

**(a) THE PINV STAGE HAS A HARD CAPACITY CEILING OF `d` AND WE ARE 21x OVER IT.**
A pseudoinverse/projection memory is exact only while the stored keys are linearly independent,
i.e. for at most `d` patterns. Our `d = 256` and we have **5491 anchors** -- overcompleteness
**21.4x**; even the 647-anchor smoke space is 2.5x over. `K K^T` (5491 x 5491) has rank <= 256, so
the pseudoinverse guarantee is **void by construction at our scale**, and lambda-regularisation
degrades it continuously toward the Hebbian solution. The ledger's 8.00x was measured at N=512 with
`d` large enough to support it, and Llama-L15's 122 -> 614 was at d=4096.
=> **A null from A2 at 5491 anchors is a SCALE result, NOT a mechanism refutation.** The result
that would show the transfer genuinely fails on OUR CODES (not merely at our scale) is: A2 fails to
beat A0 even in the **anchor-count sweep at n_anchors <= 256**, where the mechanism's precondition
IS satisfied. That sweep is therefore mandatory, not optional. Sweep: n_anchors in
{64, 128, 256, 512, 647, all}.

**(b) THE NEAR-DUPLICATE PRE-CHECK MAY END THIS CELL.** If two concepts arrive bit-identical, no
write rule separates them. Measured FIRST by `exp_codebook_geometry_precheck_v1`, reported either
way. Its DOOM band: `frac(NN>=0.99) >= 0.10` AND still `>= 0.05` after ZCA whitening.
CONTROL THAT MAKES IT INTERPRETABLE: 5491 vectors in d=256 CANNOT be near-orthogonal, so a high
nearest-neighbour cosine is partly geometrically forced. Only the **excess over a same-shape random
null** is interpretable; a raw rate quoted alone is not.

**(c) THE 22% DOES NOT TRANSFER BY ASSUMPTION.** That figure is a 241-atom CURATED math codebook
(`math::T1/probability_space`), not our 5491 corpus-derived anchors. It is carried as a REFERENCE
VALUE only.

**(d) COARSE-TO-FINE CANNOT RAISE ACCURACY, ANALYTICALLY.** Its own cell reports recall 0.992
against a full-fine CEILING of 0.992: it is a **COST** mechanism (0.200 cost ratio), not an
accuracy mechanism. Restricting candidates to a shortlist can only drop competitors (rank
unchanged-or-better) or drop the target (miss). Expected contribution to hit@1 is **<= 0**.
A3 is therefore pre-declared a **COST arm**, and it is included to verify the shortlist retains the
target (`shortlist_hit@0.1`, expected ~1.000), NOT to produce a gain. Reporting an A3 null as a
mechanism failure would be an error.

## 5. Bands (can-fail, committed before the run)

Primary measurand = **median target rank** and **frac in top-50**, vs 84/647 and 0.40.

- **HARD_PASS**: some arm cuts median target rank by >= 33% (84 -> <= 56) AND raises top-50
  fraction by >= +0.10 (0.40 -> >= 0.50), with the hit@1 delta's paired-bootstrap CI excluding 0
  AND the delta exceeding `between_anchor_draw_sd`.
- **MIDDLE_BAND**: rank improves but misses either conjunct, or improves only in the
  n_anchors <= 256 regime of the sweep (mechanism real, does not reach our operating point).
- **HARD_FAIL_NO_EFFECT**: no arm moves median rank by more than the between-draw sd.
- **CODEBOOK_DOOMED**: stage-0 DOOM band fires -> the chain is refuted upstream and the cell
  reports that as its finding.

## 6. Traps handled

- `hdlab/multi_hop.py` `beta=n_dim` makes "soft" softmax a hard argmax. **This cell uses no beta
  and no softmax at all** -- no sharpening stage is in scope. Nothing to report on entropy.
- `content_words` silently drops any token containing a digit -- inherited by the shared corpus
  path; identical across arms, so it cannot differentiate them.
- Importing the main loops runs self-tests (>2 min); `hdlab/situation_reader.py` trains at import
  (205s) and is NOT imported here. A slow import is not a hang.
- Threads pinned (`OMP_NUM_THREADS`/`OPENBLAS_NUM_THREADS`) at the TOP of the file before numpy.
- `sorted(set())` everywhere, never `list(set())`.
- metrics.json written once via tmp + `os.replace`; fresh output dir; smoke to a SEPARATE dir.
