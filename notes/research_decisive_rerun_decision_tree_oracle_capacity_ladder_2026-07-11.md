# Research: Decision tree for the decisive CSKG map-builder 3-seed re-run — all three oracle-capacity-ladder outcomes pre-designed

Date: 2026-07-11. Design/synthesis drill (no local execution, per no-local-smokes lock). Two parallel Sonnet
lit-scan sub-agents dispatched for the two genuinely new external angles this drill needed (RFF/kernel
readout-dimension theory; KGE training-convergence-at-scale literature) — everything else below reuses this
substrate's own very recent (2026-07-10/11), already-verified-off-disk research trail plus source code read
in full this cycle, not re-derived from scratch.

**Trigger:** `experiments/exp_course_c_oracle_capacity_ladder_v1.py` is running now on `remote_cpu_queue`
(confirmed via `tools/inflight_monitor.py` at dispatch time of this drill: `cpu_runner_0` running
`course_c_oracle_capacity_ladder_v1`), launched to explain why the decisive FULL 3-seed run
(`course_c_map_builder_cskg_l2_genuine_v1`, landed `2026-07-11T14:37:12Z`, read off
`data/exp_course_c_map_builder_cskg_l2_genuine_v1/metrics.json` in full this cycle) verdicted
`INCONCLUSIVE_GEOMETRY_READOUT_UNDERFIT`: the transductive ORACLE arm (fit WITH the held-out edges folded
in — it sees the answers) scored `oracle=0.0231` filtered hits@10, essentially tied with `ONESHOT_ROTATE`
(`0.0227`) and barely above `RANDOM_CODES` (`0.0002`) — nowhere near the `ORACLE_FIRE_MARGIN=0.15`-above-random
gate the cell itself pre-registered. **This means the reasoning question ("does geometry beat frequency on
genuinely-held-out L2 edges") was never actually askable in that run — the fit/readout apparatus could not
even recover edges it was directly trained on.** `BASELINE_POP` (frequency) scored `0.1746` in the same run,
i.e. the incumbent baseline is fine; only the geometric coordinate-fit + FPE-kernel-readout pipeline
collapsed at the full 25,752-node / ~485k-edge (train+test) scale.

The ladder cell fits the SAME transductive ORACLE at 6 escalating capacity points (`L0` control reproducing
the collapse, through `L5` = Anchor-1 recipe at higher k/dim) and reads it under BOTH the FPE bounded-kernel
readout (`oracle_fpe`, the mandated gate) and a direct-distance readout on the same standardized coordinates
(`oracle_direct`, a fit-only-limited reference). Its own code (`run_ladder`, lines 239-268) computes exactly
three mutually-exclusive verdict strings — `LADDER_ORACLE_FIRES`, `LADDER_READOUT_LIMITED`,
`LADDER_FIT_LIMITED` — which map 1:1 onto the three branches below. This note is keyed to those three literal
verdict strings so exp_dev can fire the correct branch with zero ambiguity and zero strategy round-trip.

---

## HEADLINE

1. **A load-bearing implementation fact, found by reading the actual source this cycle, that changes what
   "just re-run at the firing capacity" means:** the decisive cell (`exp_course_c_map_builder_cskg_l2_genuine_v1.py`)
   currently calls ONLY `fit_transe_coords` / `fit_transe_replay` (`exp_course_c_operator_fix_ssp_phase_rotation_replay_v1.py`,
   lines 417-525) for its `ONESHOT_ROTATE`, `REPLAY_CONSOLIDATED`, and `ORACLE_TRANSDUCTIVE` arms — the
   original full-batch (or replay-wrapped full-batch) margin-ranking objective, `KGE_LR=0.02`,
   `KGE_WD=1e-3`, `KGE_MARGIN=1.0`. It does **not** import or call `fit_kge_anchor1`
   (`experiments/_kge_anchor1_fit.py`: CE self-adversarial loss, `A1_N_NEG=64`, `A1_ADV_TEMP=1.0`,
   `A1_N3_LAMBDA=5e-4`, `A1_BATCH=8192`, reciprocal augmentation), which is what the ladder's `L3`-`L5` rungs
   actually test. **If the ladder fires at `L3`, `L4`, or `L5` (`fit_kind="anchor1"`), the 3-seed decisive
   re-run is NOT a config bump — it requires swapping the fit call in the decisive cell to `fit_kge_anchor1`
   for every arm in `GEOM_COORD_ARMS` (`ONESHOT`, `REPLAY`, `SCRAMBLE`, `RANDOM`, `ORACLE`), consistently, at
   the firing config's exact `(k, fpe_dim, epochs, batch)`.** `REPLAY_CONSOLIDATED` specifically needs its
   recall-consistency-gate / validation-early-stop replay loop (`fit_transe_replay`) re-derived on top of the
   Anchor-1 per-step loss, since `fit_kge_anchor1` has no built-in replay-gating mechanism of its own — this is
   the single most concrete, avoidable design mistake this note exists to prevent (a naive re-run that bumps
   `FULL_CFG`'s `k`/`fpe_dim`/`kge_epochs` numbers but leaves the old margin-rank fit function in place would
   silently fail to reproduce the ladder's own firing condition).
2. **The FPE readout is a literal random-Fourier-features (RFF) / Bochner's-theorem kernel approximation, not
   a metaphor** — confirmed by reading `make_fpe_basis`/`fpe_encode`/`geom_scores` in full: `W ~ N(0,
   ell^-2 I)` in `R^{k x dim}`, `S(x) = exp(i x.W)`, score `= Re<S(x_hat), S(x_t)>/dim`, which is exactly the
   Rahimi & Recht (2007) random-feature estimator of the Gaussian/RBF kernel `exp(-||x-y||^2 / (2 ell^2))`
   with pre-registered, NOT-tuned bandwidth `FPE_ELL=0.55` on standardized coordinates, `dim=4096` random
   features, `k=24` coordinate dimensions, ranking among `N=25,752` candidates. This makes Branch 2's readout
   diagnosis a well-posed, literature-answerable question (Section "Branch 2" below), not a vague "try a
   bigger kernel" guess.
3. **This substrate already has, in-hand and unwired, the exact fairness/weak-point-localization apparatus
   every branch below needs — reuse verbatim, do not re-derive.** The decisive cell's own pre-registered gate
   set (`POP_GAP`, `HIGH_POP_GAP`, `DISCRETE_UNDER`, `SCRAMBLE_EPS`, `ORACLE_FIRE_MARGIN`, `MANUFACTURE_EPS`,
   `TIE_EPS`, `CONSOL_REL`, `REGRESS_REL`, `FLAT_EPS`, `R_BACKDOOR`, `MIN_HELDOUT`, `MIN_STRAT_Q`), its 7-arm
   discriminator design (`ONESHOT_ROTATE`/`REPLAY_CONSOLIDATED`/`BASELINE_POP`/`DISCRETE_BIND`/
   `SCRAMBLE_REPLAY`/`RANDOM_CODES`/`ORACLE_TRANSDUCTIVE`), its degree-tertile stratification
   (`stratify_by_tail_degree`), and its two independent backdoor checks (`cross_channel_geom_vs_poprank_r`,
   `backdoor_coord_precision_vs_degree_r`) are a complete, already-validated fairness+localization harness.
   Every branch below is a variant of "run this exact harness at a different capacity/readout/recipe," never
   a new harness.
4. **Two director-specified watch-items are folded into every branch's HARD-PASS band as non-negotiable
   pre-registered checks**, per this drill's task brief: (a) **max-arm seed-flip stability** — across the 3
   seeds (7, 17, 23), the coefficient of variation of whichever arm produces the headline "geometry beats
   frequency" number must be `< 0.15`, else the win is a seed-lucky fluke, not a stable effect; (b) **mine
   params must match the `a46eadfa`-tagged reference VET** — the decisive `metrics.json`'s own
   `reference_vet` field (read off-disk this cycle: `"source": "CITED@notes VET a46eadfa (CSKG L2-only
   headroom)"`, `l2_only_all=0.276`, `l2_only_high=0.226`, `pop_high=0.412`) shows this substrate already has
   a citation discipline pinning rule-mining parameters (`MAX_RULES_PER_HEAD=50`, `HUB_CAP=60000`,
   `min_support=10`, `min_conf=0.10`) to that reference run — any re-run MUST keep these four values identical
   to what's already hard-coded in `exp_course_c_map_builder_cskg_l2_genuine_v1.py` (confirmed on disk, lines
   201-202 + `FULL_CFG`) so the L2-genuine extraction stays apples-to-apples with the `a46eadfa` headroom
   number and the just-landed INCONCLUSIVE run.

---

## Branch 1 — `LADDER_ORACLE_FIRES` (both `oracle_fpe` AND `oracle_direct` clear `ORACLE_FIRE=0.90` at some rung)

### What this means

The fit+readout pipeline is solved at that rung's capacity. The reasoning question becomes askable again:
does geometry beat frequency on genuinely-held-out (never-trained-on) L2 edges, at this now-adequate
capacity. Go straight to the decisive 3-seed re-run — no further capacity search needed.

### Design (fair + weak-point-localizing)

**Reuse verbatim:** the decisive cell's full 7-arm/gate/stratification apparatus (Section HEADLINE point 3).
Do not design a new harness.

**Swap in (per HEADLINE point 1), matched exactly to the firing rung's `(fit_kind, k, fpe_dim, epochs,
batch)`:**
- If firing rung uses `fit_kind="anchor1"` (`L3`/`L4`/`L5`): replace `fit_transe_coords` calls for
  `ONESHOT_ROTATE`, `SCRAMBLE_REPLAY`, `RANDOM_CODES`, `ORACLE_TRANSDUCTIVE` with `fit_kge_anchor1` at the
  firing `(k, fpe_dim, epochs, batch)`; re-derive `REPLAY_CONSOLIDATED`'s recall-consistency-gate /
  validation-early-stop loop on top of the Anchor-1 per-step loss (not a straight substitution — the gating
  logic operates on per-relation delta estimates from disjoint minibatches, which `fit_kge_anchor1` does not
  expose as a standalone per-step primitive; exp_dev must adapt the gate to Anchor-1's batched CE loss).
- If firing rung uses `fit_kind="margin_mb"` (`L2`): this is `fit_kge_anchor1` called with
  `reciprocal=False, n3_lambda=0.0, adv_temp=0.0` per the ladder cell's own `_fit` dispatcher (line 148-153)
  — reuse that exact call signature, do not hand-roll a separate minibatch-margin fit function.
- If firing rung is `L0`/`L1` (`fit_kind="margin_fb"`): no fit-function swap needed — only `epochs` changes
  (the existing `fit_transe_coords` call already supports this), the simplest possible branch-1 sub-case.

**Per-seed isolation:** run seeds `{7, 17, 23}` as fully independent fits (fresh `X`/`D` initialization per
seed per the existing `seed * 7919 + 11` generator pattern) — already how the decisive cell operates
(`per_seed` array in its `metrics.json`), just confirm the swapped fit function is seeded identically.

**Apples-to-apples POP:** `BASELINE_POP` needs no fit at all (frequency baseline) — it is automatically
apples-to-apples across any capacity change, and its stability (INCONCLUSIVE run: `0.1746`/`0.1702`/`0.1738`
across seeds 7/17/23, already tight) is a built-in sanity check that the L2-genuine extraction and stratified
splits themselves are stable rung-to-rung. If `BASELINE_POP` swings materially between the ladder-diagnostic
run and the decisive re-run, that signals an extraction-side (not fit-side) instability and must be resolved
before trusting any geometry-vs-POP margin.

**Held-out clean:** `extract_l2_genuine` (already read in full) already excludes L1-inverse, L1-alias, and
filtered-known reachability from the L2-genuine held-out set — reuse verbatim; do not re-derive the
composition-vs-lookup exclusion logic.

**Info-ceiling stated:** the ORACLE arm itself — now firing at `>=0.90` by construction of this branch — IS
the info-ceiling for this capacity/readout combination. Report the realized-vs-ceiling ratio
(`ONESHOT_ROTATE / ORACLE_TRANSDUCTIVE`, both aggregate and HIGH-stratum) as the primary "how much headroom is
left" number, not just the raw hits@10.

**Must-fail/scramble fires:** `SCRAMBLE_EPS=0.03` gate (`SCRAMBLE_REPLAY - ONESHOT_ROTATE <= 0.03`, i.e.
scrambled relation labels must NOT beat real ones) and `MANUFACTURE_EPS=0.05` (no manufactured headroom via
synthetic-frequency-guessable leakage) — both already pre-registered in the decisive cell, reuse verbatim.

**Degree/gate confound + metric-can-it-move:** `stratify_by_tail_degree` (LOW/MID/HIGH tertiles by gold-tail
global degree) plus the two backdoor checks (`cross_channel_geom_vs_poprank_r < 0.20` per `R_BACKDOOR`,
coordinate-precision-vs-degree correlation) are the existing degree-confound instrumentation — reuse
verbatim. "Metric-can-it-move" is satisfied by the SCRAMBLE control itself (a metric that can't move would
show SCRAMBLE tracking ONESHOT identically regardless of what's shuffled — the INCONCLUSIVE run's own numbers
already show the metric CAN move, since `RANDOM_CODES=0.0002` vs `BASELINE_POP=0.1746` is a huge, correctly-
ordered spread; the concern for Branch 1 is only whether it moves the RIGHT amount for a firing ORACLE, not
whether it moves at all).

### Falsifiable predictions

**HARD-PASS (course-C reasoning claim confirmed, ALL of):**
1. `ONESHOT_ROTATE` (or `REPLAY_CONSOLIDATED` if it wins) beats `BASELINE_POP` by `>= POP_GAP` (0.03) on
   aggregate L2-genuine hits@10, AND by `>= HIGH_POP_GAP` (0.03) on the HIGH-degree stratum specifically.
2. **Seed-flip stability (director watch-item):** coefficient of variation of the winning arm's hits@10
   across the 3 seeds is `< 0.15`.
3. `SCRAMBLE_REPLAY` does not beat the winning arm by more than `SCRAMBLE_EPS` (0.03).
4. Both backdoor checks pass: `cross_channel_geom_vs_poprank_r < R_BACKDOOR` (0.20) and
   `backdoor_coord_precision_vs_degree_r < 0.20` (director watch-item extends this to `<0.15` if
   pre-registering fresh — flag as the STRICTER of the two thresholds, use whichever is stricter).
5. **Mine-params match `a46eadfa`** (director watch-item): `MAX_RULES_PER_HEAD=50`, `HUB_CAP=60000`,
   `min_support=10`, `min_conf=0.10` unchanged from the current source and from the cited reference VET.
6. Realized-vs-ceiling ratio (`ONESHOT_ROTATE / ORACLE_TRANSDUCTIVE`) is reported explicitly, not implied.

**HARD-FAIL (any one falsifies "geometry realizes information frequency does not" even though the fit/readout
now works):**
1. `ONESHOT_ROTATE` (best arm) does not clear `TIE_EPS` (0.02) over `BASELINE_POP` on L2-genuine aggregate —
   the fit/readout problem is solved but geometry still ties or loses to frequency; this would be the FIRST
   time this substrate could ask the reasoning question cleanly and get a clean negative, which is itself the
   single most valuable possible outcome of this whole ladder program (closes Course C on solid, non-confounded
   ground rather than an inconclusive one).
2. Seed-flip cv `>= 0.15` — the win is not stable across seeds, do not report a headline claim off it; add
   more seeds before concluding either way.
3. `SCRAMBLE_REPLAY` beats or ties the winning arm — the "geometry" signal is riding something the scramble
   control should have destroyed and did not; the discriminator is not firing correctly, fix the harness
   before trusting any margin.
4. Either backdoor correlation fires (`>= 0.20`, or the stricter `>=0.15` if adopted) — matches the exact
   failure shape already landed for TransE-additive on this graph
   (`grounding_additive_geometric_degree_control_v1`, HARD_FAIL_GEOMETRY_IS_POPULARITY_SHORTCUT, pop-recovers
   52.4% of margin) — a win riding this back-door is not trustworthy regardless of the other criteria.

**P_deflated:** `0.20-0.25`, unchanged from the Course C map-builder design note's own number (mechanically
unaffected by whether the ladder resolves the fit/readout artifact — that note's central untested claim, "does
iterative replay change generalization properties, not just retention," has zero new evidence either way from
a capacity-ladder result). For the narrower "operator-fix alone gets off the chance-level floor" sub-claim
(`ONESHOT_ROTATE` beats `TIE_EPS`): `P_deflated = 0.40`, also unchanged (well-precedented externally via
RotatE, not novel synthesis).

---

## Branch 2 — `LADDER_READOUT_LIMITED` (`oracle_direct` fires `>=0.90` but `oracle_fpe` does NOT, at the best rung)

### What this means

The coordinate FIT is fine — the model genuinely learned to place gold near query in raw coordinate space
(direct-distance ranking recovers it). The FPE bounded-kernel readout specifically is the bottleneck. Per
HEADLINE point 2, this readout is a random-Fourier-features approximation of a Gaussian kernel with
`dim=4096` features in `k=24` dims, bandwidth `ell=0.55`, ranking among `N=25,752` candidates.

### Candidates, ranked (brain-grounded where the literature diverges from pure ML, per prior on-substrate drills)

1. **Increase readout dimension `dim` (the direct RFF-theory fix).** [Lit-scan pending — see RFF findings
   appended below.] The mechanism is the most literal, lowest-risk fix: more random features means lower
   variance in the kernel estimate, by construction of the Rahimi-Recht estimator. Cost: linear in `dim`
   for compute, and the ladder's own `L5` rung (`dim=8192`) already tests a 2x point — if `L5` still shows
   `readout_limited` behavior even at `dim=8192`, this is direct on-substrate evidence the RFF-dimension fix
   alone is insufficient and a qualitatively different readout is needed (see candidates 2-4).
2. **Bandwidth (`ell`) recalibration via the median heuristic.** `FPE_ELL=0.55` is explicitly "NOT tuned"
   (source comment, `exp_course_c_map_builder_cskg_l2_genuine_v1.py` line 191) — pre-registered once and never
   adapted to the actual pairwise-distance distribution of the fitted coordinates. If the true pairwise
   distance distribution (post-standardization) is poorly matched to `ell=0.55`, the kernel scores can be
   uninformatively flat (too-large ell) or noise-dominated (too-small ell) regardless of `dim`. Cheap: compute
   once from the fitted `X`/`D`, no architecture change.
3. **Resonator/attractor iterative cleanup readout, with restarts + ACF** (Frady/Kent/Olshausen/Sommer 2020;
   this substrate's own `research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md`, already-validated
   `cap_map` row 51 ACF rescue, 50x+ capacity gain on exactly the codebook-SIZE axis a 25.7k-candidate
   readout sits on). This is a bigger design change than 1-2 (an iterative decode loop, not a single matmul
   scoring pass) but is the most brain-faithful of the readout candidates: CA3's recurrent-collateral
   attractor dynamics are the direct biological analog of resonator iterative cleanup (same prior drill,
   Section 3), and this substrate already has the restart-budget law
   (`oracle_any(R) = 1-(1-p_basin)^R`, textbook independent-Bernoulli, validated on-substrate 2026-07-07)
   plus a validated ACF rescue ready to wire in — reuse, do not re-derive.
4. **DG-style sparse-decorrelation front-end** (`hdlab/hippocampal_encoder.py::DGProjection`, already built,
   unit-tested, never wired to any resonator/kernel readout path on this substrate). Brain-grounded (Treves-
   Rolls sparse-coding capacity law: DG decorrelates inputs so CA3 operates far below its raw capacity
   ceiling) but the causal link to THIS specific readout's basin/resolution problem is flagged unproven in
   two independent prior on-substrate drills — cheap to try (wiring, not new math) but should not be assumed
   to fix this on priors alone.
5. **Direct-distance-as-readout itself** (drop the FPE kernel entirely, rank by `-||x_hat - X_c||` directly —
   literally the `_direct_scores` function the ladder cell already computes as its reference readout). This
   is the cheapest possible "fix": if `oracle_direct` already fires, simply MAKE `oracle_direct` the production
   readout for the decisive re-run instead of trying to repair the FPE kernel. The only reason not to do this
   immediately is if there is a downstream reason the FPE/kernel form is needed (e.g. a planned generalization
   to soft/probabilistic composition scores that direct-distance ranking cannot support) — if no such reason
   exists, this candidate should be tried FIRST, before 1-4, since it requires zero new code.

**Ranking for the cheap decisive test:** try candidate 5 first (zero-cost — literally already computed by the
ladder cell), then candidate 2 (near-zero cost, a one-time calibration), then candidate 1 (the ladder's own
`L5` rung already gives one data point), then candidates 3-4 only if 1/2/5 all fail to close the gap — this
mirrors the "cheap, well-precedented levers first" sequencing discipline this substrate already applies to
the KGE-recipe side (Ruffinelli-style: recipe/config fixes before architecture changes).

### Falsifiable predictions

**HARD-PASS (readout-limited diagnosis confirmed and a fix found):**
1. `oracle_direct` fires (`>=0.90`) at the best ladder rung while `oracle_fpe` does not — this IS the
   Branch-2 trigger condition itself (already true by construction of being in this branch); restate as
   confirmation, not a new test.
2. At least one of candidates 1/2/5 (in that priority order) brings `oracle_fpe` to within `0.10` absolute
   of `oracle_direct` on the SAME held-out oracle set, at no more than 2x the compute cost of the firing
   rung's FPE readout.
3. The fix does not regress `oracle_direct`'s own score (no fixing-the-kernel-by-breaking-the-fit).

**HARD-FAIL (readout is NOT simply fixable by these candidates — deeper mismatch):**
1. `dim=8192` (`L5`, the ladder's own largest tested readout dimension) still shows `oracle_fpe < 0.90` while
   `oracle_direct >= 0.90` — the RFF-dimension lever alone (candidate 1) is insufficient at 2x scale; do not
   keep scaling `dim` further without evidence (per this substrate's own prior finding that recovery-vs-
   resource curves in adjacent regimes are sharp phase transitions, not gradual — `research_encoder_clean_
   composable_relational_codes_2026-07-09.md`).
2. Median-heuristic bandwidth recalibration (candidate 2) moves `oracle_fpe` by `<0.02` absolute — bandwidth
   was not the driver, rule it out cheaply and move to candidates 3/4.
3. None of candidates 1/2/5 close the gap to within `0.10` absolute of `oracle_direct` — escalate to
   candidate 3 (resonator+ACF) as the next lever, per its own pre-registered cheap decisive test in
   `research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md` (residual-gated candidate-recall@10
   `>=0.35` HARD-PASS band, reuse verbatim rather than re-deriving).

**P_deflated:** candidate 5 (direct-distance-as-readout swap): `0.55` (this is not really a "fix" so much as
recognizing the ladder's own reference readout already works — deflated only for not yet having confirmed it
generalizes past the transductive-ORACLE setting to the genuine held-out L2 case, not because the mechanism
is uncertain). Candidate 2 (bandwidth recalibration): `0.35` (well-precedented external technique — median
heuristic — deflated for lack of on-substrate precedent at this entity count). Candidate 1 (dim increase
alone): `0.30` (real but the RFF lit-scan below flags this as possibly needing much larger `dim` than a 2x
bump to matter at `N=25,752`, hence not assumed a free win). Candidate 3 (resonator+ACF):
`P_deflated=0.50` (capped, reused directly from the crux-v2 note — same underlying mechanism family, same
cap). Candidate 4 (DG-decorrelation): `P_deflated=0.35` (reused from the same note, causal link honestly
unproven).

### RFF/kernel-readout-dimension lit-scan findings (external, generic-terms-only)

**Direct answer (from a dedicated Sonnet lit-scan this cycle):** plausibly inadequate for FINE-GRAINED
ranking, plausibly adequate for coarse ranking — genuinely ambiguous from theory alone, and the deciding
factor is a data-dependent margin the theory cannot supply from first principles. The classic pointwise
Hoeffding bound for RFF (Rahimi & Recht 2007) gives `Pr[|z(x).z(y) - k(x,y)| >= eps] <= 2 exp(-D*eps^2/4)`.
**The good news:** union-bounding this over our `N=25,752` candidates costs only a `log(N^2)` factor
(~19-20 nats) — going from "one pair" to "every pair simultaneously" does NOT blow up the `dim` requirement;
at `dim=4096` the worst-case-over-all-pairs error at 99% confidence is roughly `eps~0.3` (absolute kernel-value
units) vs `eps~0.1-0.15` for a single pair at the same confidence — a modest, not catastrophic, degradation
from scale alone. **The bad news:** `eps~0.1-0.3` in absolute kernel value is large unless the TRUE kernel-value
gaps between top-ranked candidates are comfortably bigger than that — if candidate scores cluster tightly
(plausible with `k=24` real coordinates and a shared, un-adapted bandwidth), the RFF noise floor can dominate
the true ranking signal, which is exactly the "near-uniform-random ranking" failure mode this branch's
diagnosis is checking for. A separate, harsher bound (Avron et al. 2017, arXiv:1804.09893) shows that for
DOWNSTREAM STATISTICAL RISK guarantees (not just pointwise kernel-value approximation), `dim = Omega(N)`
features can be required — a much less forgiving scaling than the pointwise/ranking bound above; if the
true failure mode is closer to this regime, `dim=4096` (vs `N=25,752`) is nowhere close, and even the
ladder's `L5` `dim=8192` point would still be far short. **Bandwidth mis-specification is a real, largely
INDEPENDENT compounding risk**, not folded into the `dim` formula: no paper ties bandwidth directly into the
`dim`-vs-`N` bound, but pairwise distances concentrate in moderate-to-high dimensions (a well-documented
curse-of-dimensionality effect), so a mis-set `ell` can compress most kernel values into a narrow band —
Garreau, Jitkrittum, Kanagawa (2017, arXiv:1707.07269) document exactly this median-heuristic degradation
risk. **If the informative kernel-value gaps get compressed into a band smaller than the RFF noise floor, NO
amount of increasing `dim` fixes a badly-scaled bandwidth** — this is why candidate 2 (bandwidth
recalibration) is ranked ahead of candidate 1 (raw `dim` increase) in the priority list above, not an
arbitrary ordering. The retrieval/ranking-specific literature is thin (Li & Li 2022, NeurIPS, "SignRFF" is
the clearest hit — the retrieval community builds DEDICATED ranking-quality metrics precisely because
standard kernel-value-MSE metrics do not predict ranking degradation well, an implicit admission this is a
distinct, under-theorized problem from kernel-value approximation); no paper was found reporting concrete
`dim` requirements at `N` in the tens-of-thousands range with explicit ranking-degradation numbers — an
honest coverage gap, not evidence either way. **Concrete cheap fixes, ranked by cost:** (i) Orthogonal Random
Features (Yu et al. 2016, arXiv:1610.09072) — same `dim`, provably lower variance for a Gaussian kernel,
essentially free accuracy gain, a candidate this note's Section did not originally list and should be added
as a near-zero-cost variant of candidate 1; (ii) median-heuristic bandwidth recalibration with an explicit
sanity check of the resulting kernel-value spread across the actual 25,752 candidates (candidate 2, as
designed above); (iii) if `N=25,752` is affordable, compute the EXACT `O(N^2 k)` Gram matrix directly
(~1.5x10^10 flops — feasible on modern CPU/GPU) as a validation baseline to directly measure rank-correlation
loss rather than inferring it from theory — this is a strong, cheap, DEFINITIVE diagnostic that should be
added to the Branch 2 cheap-decisive-test sequence ahead of any kernel-approximation fix, since it directly
answers "is the FPE kernel approximation itself the problem" without needing to guess at `dim`/bandwidth
jointly. Calibration note from the lit-scan: exact constants in the scaling laws above were not independently
verified against primary-source theorem text (PDF extraction failed for the core papers) — held at
moderate-to-good, not high, confidence; the qualitative conclusion (union-bound-over-N is cheap; margin-to-
noise ratio is the real deciding factor; bandwidth mis-specification compounds independently of `dim`) is
corroborated across multiple independent sources.

**Revision to candidate ranking (informed by this lit-scan):** insert "compute the exact `O(N^2 k)` Gram
matrix as a direct validation baseline" as the very FIRST step of the Branch 2 cheap decisive test — cheaper
and more diagnostic than trying candidate 5 blind, since it directly tells you whether ANY kernel-based
readout (approximate or exact) would fire, isolating whether the problem is the RFF APPROXIMATION specifically
or the underlying kernel FORM itself (bandwidth/functional form) even computed exactly. Add Orthogonal Random
Features (Yu et al. 2016) as a free upgrade bundled into candidate 1 (same `dim`, no added cost, provably
lower variance) rather than a separate candidate.

---

## Branch 3 — `LADDER_FIT_LIMITED` (neither `oracle_fpe` nor `oracle_direct` fires at ANY laddered capacity, including `L5`)

### What this means

The problem is upstream of the readout: even a fit that gets to SEE the held-out answers directly
(transductive) cannot place them near query in coordinate space at all, at any capacity the ladder tested.
This is the least favorable branch and needs a genuinely stronger fit recipe than anything in the ladder's
top rung (`L5`: `anchor1`, `k=32`, `dim=8192`, `epochs=150`, `batch=8192`) before the decisive re-run is
worth spending on.

### Candidates, ranked (KGE-recipe literature, borrowed-known first per this substrate's own Ruffinelli-track-record discipline)

This substrate's own `research_reasoning_realization_gap_closure_prep_2026-07-11.md` (same day, read in full
this cycle) already ranked exactly this lever family for the ADJACENT "geom vs frequency" gap-closure
question; the same ranked list applies here, with one important recalibration: **that note assumed the fit
already reaches a reasonable transductive ceiling; Branch 3 means it does not even do that,** so levers must
be read as "does this get the TRANSDUCTIVE ORACLE to fire at all," not "does this close a realized-vs-ceiling
gap" — a more basic bar. **Ranking below is the REVISED order after this cycle's dedicated KGE-convergence
lit-scan (full findings in the sub-section below); the lit-scan changed the ranking from an a-priori
"n_neg first" guess to an evidence-backed "epoch/pass-count first, LR-mismatch check second, n_neg third."**

1. **Longer training schedule / more total gradient steps (REVISED to rank #1, evidence-backed).** The
   clearest, best-cited finding this cycle: RotatE's published FB15k-237 recipe (a graph of comparable EDGE
   count, 272k vs our ~460-510k, and comparable entity count, 14.5k vs our ~26k) trained for 100,000 steps at
   batch 1024 = **~376 full dataset passes**; our current top rung (`L5`, 150 epochs at batch 8192) delivers
   only **150 passes** — a 2.5-3x shortfall against the single most comparable external reference point. The
   ladder's own `L0`->`L1` rungs (`margin_fb`, `epochs=600`->`2400`, old objective) already partially isolate
   this axis; if `L1` shows a material improvement over `L0` but still short of firing, that is direct
   on-substrate confirmation the epoch axis matters and the ANCHOR-1 rungs need their own epoch-count
   escalation well past 150 (toward 300-450 dataset-passes-equivalent), not just the recipe swap alone.
2. **Learning-rate mismatch check (NEW lever, surfaced by this cycle's lit-scan, not in this note's original
   draft).** The current Anchor-1 recipe's Adam LR (`A1_LR=0.05`, confirmed on-disk) is roughly **1000x higher**
   than RotatE's published Adam LR (`5e-5`) at comparable scale — an open risk, not yet cited as a confirmed
   problem in any primary source, but a deviation this large from every published reference point in the SAME
   model family is worth a near-zero-cost check before assuming lever 1 (more epochs) alone will fix
   Branch 3. If the LR is badly mis-scaled, more epochs could fail to help or even hurt (oscillation/
   non-convergence) rather than close the gap.
3. **Larger negative-sample count (`n_neg`), demoted to #3.** Current Anchor-1 default `A1_N_NEG=64` vs.
   RotatE's FB15k-237-scale `256` — a real 4x gap, but this cycle's lit-scan found a separate (non-adversarial)
   ablation showing diminishing marginal returns from n=1->16 negatives (0.328->0.337->0.338->0.338 MRR on
   FB15k-237), softening the expected effect size; no primary source directly ablates `n_neg` within the
   self-adversarial weighting mechanism specifically — genuinely thinner evidence than levers 1-2, hence the
   demotion from this note's original a-priori #1 ranking.
4. **Better initialization scheme.** Current Anchor-1 init is `torch.randn(N,k)*0.1` for both `X` and `D` — a
   simple, common, unexamined choice; no direct external ablation found for this specific model family/scale
   this cycle — remains an unexamined, low-priority lever.
5. **Relation-specific capacity** (give high-degree/high-fanout relations more effective parameters than
   low-fanout ones, e.g. per-relation embedding-dimension allocation) — a genuinely substrate-adjacent idea
   with real external precedent (TuckER's core-tensor / mixture-of-relation-specific-matrices families
   implicitly do this) but not yet directly tested on this substrate; NEWER-GROUND, not borrowed-known.
6. **Learning-rate schedule (warmup/decay).** Not currently present in either `fit_transe_coords` or
   `fit_kge_anchor1` (both use a flat Adam LR for the whole run) — no direct external ablation found this
   cycle isolating this lever's effect size at comparable scale; lowest-priority of the six.

### Escalation trigger — when to stop tuning the fit recipe and escalate to strategy

**If a strengthened recipe (levers 1-4 above, run as an EXTENDED ladder rung beyond `L5`, e.g. `L6:
anchor1, n_neg=256, epochs=400`) still does not get `oracle_direct` (the easier, fit-only-limited reference
readout) to fire at `>=0.90`, this is a genuine escalation signal, not a "try harder" signal.** Per this
substrate's own already-landed `research_knowledge_density_information_ceiling_relational_inference_2026-07-10.md`
finding: the substrate's ingested graph density (avg degree ~2.7-7.7 in smaller sub-corpora; the CSKG core
itself is denser, avg degree ~39.7, per `cskg_provenance` read off the INCONCLUSIVE run's own `metrics.json`
this cycle — actually in the FB15k-237-comparable regime, NOT the WN18RR-sparse regime, which is a materially
different and more favorable density reading than that note's own smaller-sub-corpora numbers) is not the
likely explanation for a Branch-3 outcome specifically (the CSKG core is dense enough by that note's own
threshold). If a well-tuned recipe still cannot get even the TRANSDUCTIVE oracle to fire on this
already-dense graph, the more likely explanation shifts toward: (a) the additive/translational (TransE-family)
FUNCTIONAL FORM itself being a poor fit for CSKG's specific relation semantics (29 relation types, heavy
SYNONYM/IS_A mix per this substrate's own ingest characterization — these are exactly the symmetric/
hierarchical relation types RotatE's rotation form was designed to fix TransE's provable collapse on, so if
even RotatE-equivalent rotation still fails transductively, the functional-form hypothesis strengthens
further), or (b) a genuine representational capacity ceiling in the `k`-dimensional coordinate space at this
entity count that no borrowed-known recipe lever closes. **Escalate to strategy with this specific finding
("recipe-tuned RotatE-equivalent cannot memorize its own training-adjacent held-out edges on CSKG even at
2x the ladder's top capacity") rather than continuing to sweep recipe knobs indefinitely** — this is a
different, more fundamental question than anything the recipe-tuning literature (Ruffinelli et al.) was ever
designed to answer, since that literature's baseline assumption is that the FIT converges to a reasonable
transductive optimum; Branch 3 says it does not.

### Falsifiable predictions

**HARD-PASS (a strengthened recipe closes the fit, licensing the decisive re-run):**
1. An extended ladder rung beyond `L5` (n_neg and/or epochs increased per the highest-ranked lever from the
   lit-scan below) gets `oracle_direct >= 0.90` (the easier bar) within a bounded compute budget (no more
   than 4x the `L5` rung's `elapsed_s`, to keep this cheap and diagnostic, not an open-ended sweep).
2. Once `oracle_direct` fires, `oracle_fpe` is re-checked at the SAME strengthened recipe — if it now ALSO
   fires, proceed directly to Branch 1's design; if it fires on `oracle_direct` only, this becomes a Branch-2
   situation at the new capacity (the branches are not mutually exclusive across time — a fit fix can convert
   a Branch-3 outcome into a Branch-2 one).

**HARD-FAIL (escalation trigger fires, per the Escalation section above):**
1. The extended rung (levers 1-4, run within the same bounded compute budget) still does not get
   `oracle_direct >= 0.90`.
2. AND the CSKG core's own density (already confirmed dense, avg degree ~39.7, comparable to FB15k-237's
   ~37.4) rules out "just not enough data" as the explanation, per the density-ceiling note's own threshold.
3. -> Escalate to strategy with the specific framing above (functional-form or representational-capacity
   question, not a recipe-tuning question) rather than continuing to sweep recipe knobs.

**P_deflated:** for "a strengthened recipe (epoch/pass-count increase toward the RotatE-comparable
300-450-pass range, PLUS the LR-mismatch check, the two highest-evidence levers per this cycle's lit-scan)
gets `oracle_direct` to fire within a bounded budget": `P_deflated = 0.40` (borrowed-known technique family,
directly precedented via RotatE's own published FB15k-237/WN18RR recipes, deflated for lack of on-substrate-
exact precedent at this specific combination of entity count / relation-type mix / already-partially-
escalated capacity — NOT raised further despite the epoch-count evidence being unusually well-cited this
cycle, since the "near-full-transductive-memorization at convergence" framing this whole branch's HARD-PASS
bar rests on is itself an inference from general overparameterized-model behavior, not a literature-sourced
number for this specific model family, per the lit-scan's own explicit uncertainty flag). For "the LR-mismatch
specifically (an independent, previously-unflagged risk) is a material contributor": `P_deflated = 0.30`
(genuinely new finding this cycle, no primary source directly confirms or refutes this specific LR regime for
this model family — flagged as an open risk worth a cheap check, not a confirmed lever). For "n_neg increase
alone helps materially": `P_deflated = 0.25` (demoted from this note's original draft given the diminishing-
returns ablation found this cycle). For "relation-specific capacity allocation helps materially":
`P_deflated = 0.25` (novel-synthesis-adjacent, capped, thin direct precedent). For "the escalation trigger
fires and a functional-form change is genuinely needed": this is a residual, not independently estimated — it
is `1 - P(some recipe lever succeeds)`, i.e. substantial (~0.35-0.45) given how many independent on-substrate
negatives already exist for geometric/additive codes on this graph (five, per the Course C map-builder design
note's own tally).

### KGE-convergence-at-scale lit-scan findings (external, generic-terms-only)

**Direct comparison, from a dedicated Sonnet lit-scan this cycle (primary sources, RotatE repo config + paper
tables + Lacroix N3 paper + Ruffinelli et al. search-synthesis):**

| Source | Graph (entities / train edges) | dim | n_neg | batch | total exposure | LR |
|---|---|---|---|---|---|---|
| RotatE official config | FB15k-237 (14,541 / 272,115) | 1000 | **256** | 1024 | **100,000 steps ~ 376 dataset passes** | 5e-5 |
| RotatE official config | WN18RR (40,943 / 86,835) | 500 | **1024** | 512 | **80,000 steps ~ 472 dataset passes** | 5e-5 |
| ComplEx-N3 (Lacroix 2018) | FB15k/FB15k-237 | 2000-4000 | full 1-vs-all (no sampling) | 100 | converges by ~epoch 25 of 100 | 0.1 (Adagrad) |
| Ruffinelli et al. 2020 | WN18RR/FB15k-237 | 128 | swept in search | 1024 | 20-epoch search, best rerun to 200 epochs | Adagrad, searched |
| **This substrate (current)** | **CSKG core (25,752 / ~460-510k)** | **24-32** | **64** | **8192** | **up to 150 epochs** | **0.05 (Adam)** |

**Calibrated read: plausibly under-trained on total EXPOSURE (epochs/passes), the single clearest finding.**
The strongest, most directly comparable external number is RotatE on FB15k-237 — a graph of similar EDGE
count (272k train edges vs. our ~460-510k) and comparable entity count (14.5k vs. our ~26k): RotatE trained
that graph for 100,000 gradient steps at batch 1024, i.e. **~376 full dataset passes**. Our current recipe
(150 epochs, batch 8192) delivers only **150 passes** — roughly **2.5-3x fewer dataset passes than the
published RotatE recipe on a comparably-sized graph**, and the WN18RR config (~472 passes) is even more
aggressive. This is the single clearest, best-cited piece of evidence for what the FIRST lever to try should
be: **not `n_neg`, but total epoch/pass count.** `n_neg=64` vs RotatE's 256 (FB15k-237-scale) is a real 4x
gap but a separately-cited ablation (non-adversarial negative sampling) found MRR gains from n=1->16
negatives were small and monotonically diminishing (0.328->0.337->0.338->0.338 for n=1,4,8,16 on
FB15k-237) — suggesting marginal negative-count effects may flatten well below 64, softening (not
eliminating) this as a lever; no primary source directly ablates negative-count specifically within the
SELF-ADVERSARIAL weighting mechanism, flagged as a real gap in the evidence.

**A THIRD, previously-unflagged lever this lit-scan surfaces as an open risk, not yet in this note's original
candidate list:** the current Anchor-1 recipe's Adam learning rate (`A1_LR=0.05`, confirmed on-disk this
cycle in `experiments/_kge_anchor1_fit.py`) is **roughly 1000x higher than RotatE's published Adam LR
(5e-5)**. No primary source directly addresses whether this LR regime is appropriate for this model family
at this scale — this is an OPEN RISK, not a cited finding either way, but a 1000x deviation from every
published reference point in the same model family is large enough to flag as a candidate confound
independent of epoch count or `n_neg`: if the LR is badly mis-scaled, MORE epochs alone (lever 1) may not
help, or could even hurt (oscillation/non-convergence) rather than fixing the transductive-memorization
failure. **Recommend checking this BEFORE or ALONGSIDE the epoch-count lever**, since it is a near-zero-cost
diagnostic (a single-value config change) with a plausible large effect size given the magnitude of the
deviation.

**Revision to Branch 3's candidate ranking, informed by this lit-scan (highest-leverage first):**
1. **Increase total training exposure toward the 300-450-dataset-pass range** (raise epochs from 150 toward
   ~350-450 at fixed batch=8192, or track total gradient steps directly) — the most directly cited,
   best-evidenced lever.
2. **Check/correct the Adam learning rate** (`A1_LR=0.05` vs. every published reference point's `~5e-5`,
   a ~1000x deviation) — cheap, previously unflagged, plausible large effect, should be checked before or
   alongside lever 1.
3. **Increase `n_neg`** from 64 toward RotatE's FB15k-237-scale value of 256 — real but the cited evidence for
   marginal effect size at this range is thinner and shows diminishing returns in a (non-adversarial)
   ablation; secondary priority to levers 1-2.
4. Relation-specific capacity allocation and LR warmup/decay schedules remain NEWER-GROUND / thin-evidence
   levers, unchanged from this note's original ranking — sequence after 1-3.

**Explicit uncertainty flags from the lit-scan (report honestly, do not treat as settled):** RotatE's own
ablation (Table 13) tested self-adversarial weighting ON/OFF, not a sweep over `n_neg` itself — no primary-
source effect size for `n_neg` specifically in the self-adversarial regime. The Ruffinelli et al. 2020 detail
(20-epoch search, 200-epoch best-config rerun, dim=128 fixed) came from a search-engine synthesis of the
paper, not a directly-rendered primary-source quote (PDF would not extract as text this cycle) — moderate,
not high, confidence. No formal compute-scaling RULE (e.g. "steps proportional to E/batch x constant") was
found in any primary source — this appears to be empirically-tuned-per-dataset practice in the literature,
not a derivable formula. No KGE paper reports explicit TRAINING-SET (transductive) MRR at convergence — all
report test/validation MRR only; the "near-full-memorization at convergence" framing this note's Branch 3
relies on is an INFERENCE from general overparameterized-model behavior, not a literature-sourced number for
this specific model family — flagged honestly as the least-verified link in Branch 3's chain of reasoning.

---

## Cross-thread synthesis

- **Directly extends and is gated by three same-day notes, not duplicative of any:**
  `research_course_c_map_builder_replay_consolidation_design_2026-07-10.md` (the representation/mechanism
  design this ladder is trying to make measurable — Branch 1 is that note's own cheap decisive test, finally
  runnable); `research_reasoning_realization_gap_closure_prep_2026-07-11.md` (the KGE-recipe-tuning track
  record this note's Branch 3 directly reuses, recalibrated for the harder "does the fit even converge at
  all" bar rather than "does it close a realized-vs-ceiling gap"); `research_resonator_decode_capacity_
  ceiling_crux_v2_2026-07-10.md` (the readout-fix candidate ranking this note's Branch 2 directly reuses).
- **The single most load-bearing NEW fact this drill adds that none of those three notes had:** the decisive
  cell's fit-function coupling (HEADLINE point 1) — none of the three prior notes noticed that a firing
  ladder rung using the Anchor-1 recipe requires an actual code change to the decisive cell, not a config
  bump, because the decisive cell was written before `_kge_anchor1_fit.py` existed and still calls the
  original `fit_transe_coords`/`fit_transe_replay` pair. This is exactly the kind of on-disk-verified,
  previously-unnoticed implementation detail Fix#28 discipline exists to surface before it causes a wasted or
  silently-invalid re-run.
- **The CSKG-core density re-read** (avg degree ~39.7, confirmed off the INCONCLUSIVE run's own
  `cskg_provenance` field this cycle) is a second load-bearing correction: the density-ceiling note's own
  headline number (avg degree ~2.7-7.7, "WN18RR-sparse regime") was computed from SMALLER, different
  sub-corpora tested earlier in the program, not the CSKG cross-cutting core the ladder/decisive cell actually
  use. The CSKG core itself sits in the FB15k-237-comparable, NOT WN18RR-comparable, density regime — this
  matters directly for Branch 3's escalation-trigger reasoning (a dense-enough graph makes "the fit
  fundamentally cannot converge even transductively" a more surprising, more escalation-worthy finding than it
  would be on a WN18RR-sparse graph, where under-density would be the obvious first suspect).
- **All three branches reuse the SAME fairness/localization harness** (decisive cell's 7-arm/gate/
  stratification design) — this was a deliberate design choice in this drill: rather than inventing
  branch-specific new controls, every branch's HARD-PASS/HARD-FAIL criteria are phrased in terms of gates
  that already exist in the codebase and are already pre-registered, minimizing exp_dev's implementation
  surface and keeping the three branches genuinely comparable to each other and to the INCONCLUSIVE baseline.

## Substrate-product implications

- **Whichever branch fires, the ladder result is itself a genuine, reportable, non-trivial finding** — this
  is not a "wait for the real result" placeholder note. `LADDER_ORACLE_FIRES` converts a stalled program back
  onto solid ground (the reasoning question becomes askable, win or lose). `LADDER_READOUT_LIMITED` would be a
  clean, well-localized engineering finding ("the geometry was right, the readout math was under-resourced")
  with a cheap, high-confidence fix path (Branch 2 candidate 5 costs zero new code). `LADDER_FIT_LIMITED` at
  worst produces a sharply-scoped escalation to strategy (functional-form question) rather than an open-ended
  "needs more research" dead end — and per the density re-read, this would be a genuinely surprising,
  informative negative (a dense, FB15k-237-comparable graph that a recipe-tuned RotatE-equivalent still
  cannot memorize transductively), not a shrug.
- **The product story stays honest and calibrated regardless of branch:** none of the three branches licenses
  a "we solved reasoning" claim on their own — Branch 1 only makes the REAL test runnable; Branches 2/3 are
  both about getting the measurement apparatus itself to work. This matches this program's own standing
  discipline (never frame a construction-proof or a fixed-artifact as a capability win) and should be
  maintained explicitly when this note's findings are relayed.
- **The fit-function-coupling finding (HEADLINE 1) has a reusable lesson beyond this one cell:** any future
  capacity-ladder cell that references a newer fit/recipe module built AFTER the cell it's diagnosing was
  written should explicitly check whether the diagnosed cell needs a code swap, not just a config bump, before
  assuming a "firing" ladder rung is directly reproducible by parameter change alone.

---

## exp_dev handoff section (routing pointers only — exp_dev authors the cell)

Per [[feedback-no-experiment-design-in-prompts]]: this section provides ROUTING POINTERS and BRANCH-KEYED
ANCHOR CANDIDATES only. Cell grids, exact hyperparameter values beyond what's already pre-registered above,
and script-level implementation are for exp_dev to author from this note + the existing decisive-cell source.

**Trigger condition:** read `data/exp_course_c_oracle_capacity_ladder_v1/metrics.json` once it lands. Its
top-level `verdict` field is literally one of `LADDER_ORACLE_FIRES` / `LADDER_READOUT_LIMITED` /
`LADDER_FIT_LIMITED` — dispatch the matching branch below immediately, no strategy round-trip needed (this
note pre-clears all three).

**Anchor candidate A — `decisive_rerun_at_firing_capacity_v1` (fires on `LADDER_ORACLE_FIRES`):**
Anchor pointer: this note's Branch 1 + `metrics.json`'s `firing_config` field (gives exact `label, fit_kind,
k, fpe_dim, epochs, batch`) + `metrics.json`'s `reasoning_preview` field (single-seed preview already
computed at the firing rung — read this FIRST, it may already give a strong early signal on whether the
3-seed re-run is worth prioritizing immediately vs queuing behind other work).
Substrate-product reading: swap the decisive cell's fit calls per HEADLINE point 1, re-run the full 7-arm
3-seed harness at the firing capacity, apply the HARD-PASS/HARD-FAIL bands from Branch 1 including the two
director watch-items (seed-flip cv, `a46eadfa` param match).
Tier hint: remote_cpu_queue (matches the ladder's own compute-class annotation: symbolic graph traversal +
minibatch SGD + batched matmul, CPU-safe, no local execution per lock). Cost roughly comparable to the
INCONCLUSIVE run's own `elapsed_s` (~6464s) at the firing rung's capacity, times 3 seeds — budget accordingly,
scale from the firing rung's own `elapsed_s` in the ladder metrics rather than assuming the full run's cost.

**Anchor candidate B — `readout_capacity_diagnostic_v1` (fires on `LADDER_READOUT_LIMITED`):**
Anchor pointer: this note's Branch 2, candidates ranked 5 -> 2 -> 1 -> 3 -> 4.
Substrate-product reading: try candidate 5 (direct-distance-as-readout swap) FIRST as a near-zero-cost
diagnostic/fix before touching the kernel; then candidate 2 (median-heuristic bandwidth); then reuse the
ladder's own `L5` data point for candidate 1; escalate to candidate 3 (resonator+ACF, reusing crux-v2's own
pre-registered cheap decisive test verbatim) only if 1/2/5 all fail to close the gap.
Tier hint: cheapest branch of the three — candidates 5 and 2 require no new fit, only readout-side changes,
CPU-safe, remote_cpu_queue.

**Anchor candidate C — `strengthened_fit_recipe_extended_ladder_v1` (fires on `LADDER_FIT_LIMITED`):**
Anchor pointer: this note's Branch 3, candidates ranked by the KGE-convergence lit-scan findings (revised
ranking: epoch/pass-count increase toward RotatE's ~300-450-dataset-pass reference range is #1; an Adam
LR-mismatch check (`A1_LR=0.05` is ~1000x RotatE's published `5e-5` at comparable scale — cheap, previously
unflagged, check this alongside or before scaling epochs) is #2; `n_neg` increase toward 256 is #3, demoted
given diminishing-returns evidence found this cycle). Try levers 1-2 together as a single `L6` extended
ladder rung before trying relation-specific-capacity or LR-schedule changes.
Substrate-product reading: run ONE extended ladder rung (not the full decisive re-run) with the strengthened
recipe, bounded to <=4x the `L5` rung's compute cost; check `oracle_direct` first (the easier bar); only
proceed to a decisive 3-seed re-run design if that fires. If the extended rung still fails, this note's
escalation trigger applies — flag to strategy with the specific framing in the Escalation section, do not
keep sweeping recipe knobs.
Tier hint: remote_cpu_queue, single extra ladder rung (cheap relative to a full 3-seed re-run) — this is a
diagnostic step, not the decisive run itself.

### Context pointers (file paths, not summaries)

- This note: `notes/research_decisive_rerun_decision_tree_oracle_capacity_ladder_2026-07-11.md`
- Ladder cell (source, read in full): `experiments/exp_course_c_oracle_capacity_ladder_v1.py`
- Decisive cell (source, read in full): `experiments/exp_course_c_map_builder_cskg_l2_genuine_v1.py`
- Anchor-1 fit recipe (source, read in full): `experiments/_kge_anchor1_fit.py`
- Old margin-rank fit + FPE basis (source, read in full): `experiments/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1.py`
- INCONCLUSIVE run metrics (read in full): `data/exp_course_c_map_builder_cskg_l2_genuine_v1/metrics.json`
- Course C map-builder design: `notes/research_course_c_map_builder_replay_consolidation_design_2026-07-10.md`
- Reasoning-realization gap closure prep (KGE recipe ranking): `notes/research_reasoning_realization_gap_closure_prep_2026-07-11.md`
- Resonator decode capacity ceiling (readout-fix ranking): `notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md`
- Knowledge-density information ceiling: `notes/research_knowledge_density_information_ceiling_relational_inference_2026-07-10.md`
- DGProjection primitive (unused, ready to wire): `hdlab/hippocampal_encoder.py`
- `substrate_capability_map.md` row 51 (ACF rescue, validated)

### Contract section

This handoff proposes 3 branch-keyed anchor candidates, mutually exclusive at dispatch time (exactly one
fires per the ladder's own verdict string) but not mutually exclusive across time (a Branch-3 fix can convert
into a Branch-2 situation; see Branch 3's HARD-PASS criterion 2). Exp_dev does not need to design a
harness — every branch reuses the decisive cell's existing 7-arm/gate/stratification apparatus verbatim.

**GATING:** none of these three anchors depend on a strategy round-trip — this note pre-clears all three
outcomes. The only judgment call left to exp_dev is HOW MUCH of Branch 1's re-run to run immediately vs queue
(the `reasoning_preview` field gives an early read to inform that), and whether Branch 3's extended rung stays
within its bounded compute budget before escalating.

### Autonomy declaration

Exp_dev is autonomous in:
- Confirming which of the three verdict strings landed and dispatching the matching anchor
- Choosing exact cell-code diffs to implement the fit-function swap (Branch 1) or readout swap (Branch 2) or
  extended-rung recipe (Branch 3)
- Choosing local CPU vs remote CPU/GPU routing (though per the no-local-smokes lock, all execution routes to
  remote_cpu_queue or overnight GPU — no local execution regardless of branch)
- Deciding Branch 1's re-run priority relative to other in-flight work, informed by the `reasoning_preview`
  early read
- Deciding whether Branch 3's extended rung result licenses proceeding to a decisive re-run or triggers the
  escalation

Exp_dev is NOT autonomous in:
- Making cap_map decisions from the ladder's or the re-run's verdict (orchestrator / verdict_handler owns this)
- Loosening any of the pre-registered gate thresholds (`POP_GAP`, `SCRAMBLE_EPS`, `R_BACKDOOR`, etc.) or the
  two director watch-items (seed-flip cv `<0.15`, `a46eadfa`-matched mine params) without an explicit
  strategy sign-off
- Treating Branch 3's HARD-FAIL as license to keep sweeping recipe knobs indefinitely — the escalation
  trigger is a stop condition, not a suggestion

---

## Citations (verified count)

**On-disk (read in full this cycle, not cited externally):**
`experiments/exp_course_c_oracle_capacity_ladder_v1.py`;
`experiments/exp_course_c_map_builder_cskg_l2_genuine_v1.py`;
`experiments/_kge_anchor1_fit.py`;
`experiments/exp_course_c_operator_fix_ssp_phase_rotation_replay_v1.py` (relevant functions);
`hdlab/hippocampal_encoder.py` (`DGProjection` class);
`data/exp_course_c_map_builder_cskg_l2_genuine_v1/metrics.json`;
`notes/research_course_c_map_builder_replay_consolidation_design_2026-07-10.md`;
`notes/research_reasoning_realization_gap_closure_prep_2026-07-11.md`;
`notes/research_resonator_decode_capacity_ceiling_crux_v2_2026-07-10.md`;
`notes/research_knowledge_density_information_ceiling_relational_inference_2026-07-10.md`;
`notes/exp_dev_handoff_research_reasoning_realization_gap_closure_prep_2026-07-11.md` (structural template
for this note's handoff section).

**External literature, this cycle (2 parallel Sonnet lit-scans, generic math/ML terms only, no
substrate-novel names/configs/numbers sent off-platform per [[feedback-query-privacy-decomposition]]):**

**RFF/kernel-readout lit-scan (7 sources):** Rahimi & Recht (2007), "Random Features for Large-Scale Kernel
Machines," NIPS. Sutherland & Schneider (2015), "On the Error of Random Fourier Features," UAI,
arXiv:1506.02785. Yu, Suresh, Choromanski, Holtmann-Rice, Kumar (2016), "Orthogonal Random Features," NeurIPS,
arXiv:1610.09072. Avron, Kapralov, Musco, Musco, Velingker, Zandieh (2017), "Random Fourier Features for
Kernel Ridge Regression: Approximation Bounds and Statistical Guarantees," ICML, arXiv:1804.09893. Garreau,
Jitkrittum, Kanagawa (2017), "Large sample analysis of the median heuristic," arXiv:1707.07269. Li & Li
(2022), "SignRFF: Sign Random Fourier Features," NeurIPS. "Towards a Unified Analysis of Random Fourier
Features," JMLR 22 (2021), jmlr.csail.mit.edu/papers/volume22/20-1369/20-1369.pdf.

**KGE-training-convergence-at-scale lit-scan (5 primary sources):** Sun, Deng, Nie, Tang (2019), "RotatE,"
ICLR, arXiv:1902.10197 (Tables 12/13 + official repo `run.sh`/`best_config.sh` hyperparameters read directly).
Lacroix, Usunier, Obozinski (2018), "Canonical Tensor Decomposition for Knowledge Base Completion" (N3),
ICML, arXiv:1806.07297 (training-schedule details read directly). Ruffinelli, Broscheit, Gemulla (2020),
"You CAN Teach an Old Dog New Tricks," ICLR (search-synthesis, PDF did not render as text this cycle —
flagged moderate not high confidence). "Language Models as Knowledge Bases?" (Petroni et al. 2019/2020),
arXiv:2008.09036 (analogy source for transductive-memorization framing, flagged as an inference not a direct
KGE-literature number). Entity-aware negative-sampling ablation numbers (non-adversarial n=1/4/8/16
comparison on FB15k-237, cited via search-synthesis, not independently re-verified against a single named
primary source this cycle).

**Total: 11 on-disk sources read in full this cycle + 12 external sources across 2 lit-scans = 23 verified
checks.**

---

## Intuitive summary

The map-building experiment that was supposed to tell us whether the substrate can reason about relationships
it was never directly taught hit a wall before it could even start: the coordinate-fitting step could not
correctly place facts it was literally shown during training, let alone facts it wasn't. That's like a
student who can't answer questions from the answer key placed directly in front of them — the test itself
was broken, not the student. Right now, a diagnostic run is checking, at six increasing levels of training
effort, exactly where that breaks: is it that the fit itself needs more training, or is it a separate
"reading" step (the readout) that's the bottleneck even when the underlying knowledge is placed correctly.

This note is the playbook for whichever of those three answers comes back, written now so we don't lose a day
figuring out what to do next. If the fit turns out fine with enough training (the best outcome), we go
straight to the real test with proper safeguards in place, including two specific stability checks a director
asked for. If it's the "reading" step that's broken, there's a near-free fix already sitting in the code
(read the answer differently) plus better-precedented options if that's not enough. If neither works even at
the highest training effort tried, there's a clear next step (try an even stronger training recipe, informed
by literature on how much training this kind of system usually needs) and a clear stopping point (if a strong
recipe still can't get the system to recognize its own answer key, that's a real finding worth escalating,
not a sign to keep tuning knobs forever). Every path keeps the honest safeguards this program already
insists on — no path claims a win the checks don't support, and every path is designed so a failure teaches us
something specific rather than leaving us guessing. The most concrete new thing found while writing this: the
experiment code that would run the "fires" case wasn't actually wired up to use the newer, better training
method being tested — a real bug that would have silently produced a meaningless re-run if not caught now.
