# Empirical envelope of core VSA operations (bind / bundle / unbind-cleanup) — synthesis for the C build

**One-line summary:** Bind/unbind is lossless and cheap (O(N)); bundling degrades gracefully (no sharp
cliff) with crosstalk onset K* scaling ~N/log(N) (Kanerva form, 2.1-3.5x prefactor) and a real content-driven
cliff around m~24-32 bindings at N=256 (matching the brain's ~10-item SHRUTI/working-memory band once
scaled); the reported "128 bindings/bundle @ N=2048" ceiling is a REAL bundled-capacity number but does
NOT gate the read-bridge's single-hop 1.0 (that map is SHARDED, selected by cosine-exact-match, not
surviving crosstalk); a reader operating at ~0.44-0.56 noise/precision gets a genuine but MODEST graceful-
degradation advantage from HD over brittle symbolic exact-match (+0.13 to +0.28 accuracy in the MIX/WRONG
regimes), no advantage when relations are simply MISSING, and cleanup-memory is a hard STEP not a graceful
curve (collapses between sigma=2.0 and sigma=3.0 noise). ADDENDUM (Section 5): a depth-2, ~4-way-fan-out
quadtree-style nested bundle (the C/vision-relevant regime) sits comfortably inside every measured envelope
found — direct FHRR bind/unbind at depth-2 measures 1.000 (51 links, N=2048) and a same-shaped
recursive-constituency tree via disjoint-band SBC measures 1.000 through L4 (wall only at L8+, and it's a
content-slot wall, not a structural one) — but cross-level crosstalk-COMPOUNDING under shared full-N
bundling, and resonator-based blind (not known-key) hierarchical factoring, are both genuine GAPS. Read-only
synthesis; no new experiments run.

Read-only synthesis per Director request (compile empirical envelope of BIND/BUNDLE/UNBIND from banked
atoms + cert ledger + on-disk metrics, ahead of the "C" live-accumulating-FHRR-reasoning-map build).
Sources are cited by atom ID / commit / metrics path. Anything not found on disk is marked UNVERIFIED
rather than invented. Numbers quoted from atom `description`/`metadata.metrics` fields verbatim where
possible; a few are re-derived from raw curves in the `metrics.json` files themselves (noted as such).

---

## 1. ENVELOPE TABLE

### BIND (FHRR: elementwise complex multiplication of unit-modulus phasors)

| Property | Measured | Source |
|---|---|---|
| Definition | `T2/fhrr_bind`: elementwise complex mult of two unit-modulus phasor vectors, O(N), associative, commutative, has exact inverse (`T2/fhrr_unbind` = elementwise mult by conjugate) | `data/substrate_index/math/atoms.jsonl` L14-15 |
| Noiseless fidelity | Exact / lossless in the algebraic sense — a single bind+unbind round-trip recovers the filler exactly (bridge_fidelity_single = 0.000, i.e. zero error) at N=2048, 5 seeds, 230 facts | atom `math::MM_read_bridge_rolefiller...` (commit f9041a950), metrics `bridge_fidelity_single: 0.0` |
| Mechanism load-bearing (not pass-through) | Wrong-role unbind collapses recall to 0.000 across single-hop, multi-hop, AND conjunctive queries, all 5 seeds (auditor independently extended the control to multi+conj; original report covered only single) | same atom, `wrong_role_single_mean/multi_auditor/conj_auditor: 0.0` |
| Binding-op family invariance (which multiplication rule you pick) | Crosstalk ONSET (K_cliff) is IDENTICAL across Hadamard/binary-bipolar, Circular-Convolution/HRR-real, and FHRR-complex-mul at N=8192, B=16 banks: all three = 750 bindings, shift 0.0% (HARD_FAIL on the "family matters" hypothesis — genuinely invariant, 3 seeds) | `data/exp_substrate_binding_op_x_capacity_v1_seed_{7,13,19}/metrics.json`; cert_ledger L1092 synthesis atom |
| Binding-op family DOES differ in per-unit readout quality | At the SAME sub-cliff load (alpha=0.5, i.e. ~375/750 bindings), top-1 accuracy differs 2.7-3.25x: Hadamard 0.267, Circular-Conv 0.367, FHRR 0.867 (n_seeds=1 for this specific alpha cross-section within the 3-seed cell; cv_across_alpha 0.86/0.69 for HAD/CIR — noisy) | `exp_substrate_binding_op_x_capacity_v1_seed_7/metrics.json` (`top1_at_alpha_0p5`, `K_cliff_hadamard_ref: 1500`) |
| Order/position-binding family invariance (cyclic-shift vs random-permutation vs phase-rotation) | K* (crosstalk onset for the encoding of sequence position) = 500, identical across all 3 order-binding methods, 3 seeds, HARD_FAIL on "method matters" (genuinely invariant) | `data/exp_substrate_order_binding_family_v1_seed_{13,19}/metrics.json` |
| Cost | O(N) per bind/unbind (FHRR); this is a design primitive, not a measured empirical result | `T2/fhrr_bind` metadata |

### BUNDLE (superposition, optionally renormalized)

| Property | Measured | Source |
|---|---|---|
| Definition | `T2/superposition` = raw vector sum, no renormalization, preserves count/magnitude info; `T2/bundling` = sum + renormalize to unit modulus, standard multi-item HRR/FHRR storage op | atoms L57-58 |
| Degradation shape (cliff vs graceful) | At N=4096, full run, 5 seeds: bundling capacity degradation is MONOTONE and GRACEFUL at every seed (`monotone: true, graceful: true, sharp: false` all 5/5 seeds; `R_at_013 = 1.0` at the tested load); HARD_PASS | `data/exp_capacity_cliff_graceful_full_v3/metrics.json` |
| Crosstalk-onset N-scaling law (sequence-binding-via-HRR, a bundle of positionally-bound items) | K* tracks the Kanerva (2009) conservative bound form K_crit ~ N/(4·log2 N), with an empirical PREFACTOR of 2.1x (N=2048) rising to 3.5x (N=16384) — i.e. actual usable capacity (at a 0.90-recall SAT-band threshold) is 2-3.5x above the conservative closed-form bound. Measured K*: N=2048→100, N=4096→~200-500 (boundary-noisy), N=8192→500, N=16384→1000. Query-noise Q in {1,2,4} does NOT materially shift the cliff — N is the dominant axis. Cross-seed mechanism-stability: 10/12 (N,Q) combos give IDENTICAL K* across 3 independent seeds; 12/12 within +/-1 grid step. CHAIN-GRADE (cert +1) | `T3/EXP_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_CROSS_SEED_CHAIN_GRADE...` (2026-06-28) |
| Bundled role-filler capacity (the number most directly relevant to a live reasoning-map) | At N=2048, 5 seeds, 230-fact toy KB: bundled-map capacity_curve = {128 relations: 0.9703, 192: 0.7677, 256: 0.5687}. Ceiling reported = 128 bound-relations/bundle; discriminator fires (drops below 0.90) already between 128 and 192 | atom `math::MM_read_bridge_rolefiller...` metrics `capacity_curve_5seed_mean` |
| **CRITICAL CAVEAT on the 128 number** | This is a REAL bundled-capacity bound, but it does **NOT** gate the read-bridge's reported single-hop 1.000 at 230 facts. That readout uses a SHARDED map (one vector per fact, not one shared bundle) selected by cosine EXACT-match on a construction-exact query — so the 1.0 at 230 facts is construction-determined, not evidence of surviving 230-way crosstalk. Reconciliation: **128 = the real bundled-superposition ceiling; 230-fact 1.0 = a sharded-map result, a different regime entirely.** Do not conflate. | same atom, `capacity_note: "BUNDLED ceiling; sharded readout NOT gated by it"`, auditor `over_reads_corrected` list |
| Content-blind structural-code capacity cliff (small N, brain-scale) | At N=256: robust through m=24 simultaneous role-filler bindings in one bundle (factored_heldout_vocab=0.9717); first drop at m=32 (0.9267) — "crosstalk cliff begins at m=32." Brain-faithful working sets (m=2-6) sit far inside this envelope. Framed as the SAME crosstalk phenomenon as SHRUTI's classic ~10-binding ceiling (same-limit ACCEPT, not a contradiction) | atom `math::MM_role_filler_factorization_compgen_v1` (`capacity_cliff` field: `robust_through_m: 24, first_drop_m: 32`) |
| Content-correlation x load interaction (does real, correlated content break the cliff sooner) | At m=3 (low load), factorization holds flat (0.55-0.59) across GloVe content-correlation 0.015→0.597 — robust with headroom. At m=10 (higher load), factorization COLLAPSES as correlation rises: F_vocab = 0.708 (corr=0.015) → 0.203 (corr=0.170) → 0.008 (corr=0.597). CAN-FAIL genuinely confirmed: **high load x high content-correlation together break bundled binding**; low load tolerates high correlation; high load only tolerates low correlation | atom `math::MM_role_filler_factorization_realcontent_cg_v1` (2026-07-19), `stress_m3_F_pres_held_by_corr`, `stress_m10_F_vocab_by_corr` |
| Capacity cost vanishes with N (curated real-KB content) | Real ConceptNet-extracted-relations: F_heldout = 0.880 (N=48) → 0.960 (N=64) → 0.994 (N=96) → 1.000 (N=128+); a synthetic control follows the SAME shape — the headroom IS capacity, not difficulty; cost from real relational content vanishes by N~96-128 at m=6 | atom `math::MM_role_filler_factorization_conceptnet_cg_v1` |
| Capacity cost vanishes with N (reader-extracted real narrative content — noisier: names/pronouns) | Real reader-extracted (McGuffey Third Reader) tuples: F_heldout = 0.823 at N=40 (m=6), FLAT baseline 0.005 (BELOW the 0.0625 chance floor — genuine anti-generalization of the naive baseline). realcost_sweep: N40=+0.091 cost → N48=+0.062 → N64=+0.032 → N96=+0.013 → N128=+0.002 → N192/N256=0.000. Reader-extracted narrative content needs roughly 2x the N of curated ConceptNet content to fully vanish the crosstalk cost (N~192-256 vs N~96-128) because names/pronouns are more confusable | atom `math::MM_role_filler_factorization_reader_coupled_cg_v1` |
| Robust cross-encoder capacity predictor | Across 11 sentence encoders (incl. pythia-2.8b), the DIRECT crosstalk moment E[<k_i,k_j>^2] on raw unit-normed keys is the dominant/robust predictor of Hebbian-superposition capacity M_crit (Pearson=0.976, Spearman=0.964, n=11); SVD d_eff and IsoScore are far weaker. NOT a parameter-free law (cleanup-boost `c` unbounded, 5.04x spread across encoders) | `T3/EXP_crosstalk_capacity_law_v1` (MEASURED_MECHANISM, cert 591) |
| Chain-composition shape at small scale (L=2 hop, F=1 filler) | Bimodal (SAT vs floor) with NO cliff-adjacent mid-band — theory-confirmed at this regime, but atom description body is otherwise thin/UNVERIFIED beyond the headline | `T2/EMPIRICAL_BUNDLED_FHRR_CHAIN_COMPOSITION...` (description field empty on disk; headline only) |

### UNBIND / CLEANUP

| Property | Measured | Source |
|---|---|---|
| Bare unbind (no cleanup) | Exact/lossless when the queried role-filler pair is present and the map isn't past its bundled-crosstalk ceiling (see BIND row above) | atom `math::MM_read_bridge_rolefiller...` |
| Classical Hopfield cleanup vs alternatives | At a PC regime (encoder=binary_bipolar, alpha_soft=0.5, beta=8.0, M=100), classical Hopfield cleanup is DOMINATED (worst option) in 3/3 seeds; modern_hopfield (softmax/dense), iterative_cosine, and soft_energy_attractor are all COMPETITIVE alternatives, unanimous ranking (`n_pairs_differ=6/6` every seed). **Design takeaway: do not default to classical Hopfield for cleanup; use a modern/iterative/soft variant.** MM tier (cross-seed n_disc 9-15/80, below the 24/80 chain-grade floor — regime-narrow, not yet CG) | `T3/EXP_substrate_pc_cleanup_family_phase_diagram_v1_3seed_CROSS_SEED_AGG...` (2026-06-30) |
| Modern (dense/softmax) Hopfield capacity | HARD_PASS, N=2048 and N=4096: recall@1 = 1.000 at load P/N=2.0 (twice as many patterns as dimensions) where classical Hopfield is dead (recall=0.000) at the same load — confirms the exponential- vs linear-capacity advantage of modern Hopfield cleanup. At beta=8, recall>=0.95 holds up to at least P/N=4.0 (wide safe operating envelope). **PROVENANCE FLAG: these are LEGACY_EXCERPT / PRE_SUBSTRATE_BUILD-era cells (medium relevance tier) — treat as directionally useful but older/lower-provenance than the 2026-07 cells above** | `T3/EXP_hopfield_capacity_gpu_v1`, `T3/EXP_hopfield_capacity_n4096_gpu_v1`, `T3/EXP_modern_hopfield_beta_capacity_gpu_v1` |
| Cleanup-memory noise tolerance (single-observation recovery vs sigma) | Cleanup is the WEAKEST leg of the whole noise-tolerance battery: single-observation accuracy = 1.0 for sigma in {0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0}, then CLIFFS to 0.029 at sigma=3.0 — a genuine STEP, not a graceful curve. At the collapse point, R-fold (bundle+cleanup, analog averaging, R=3 observations) gives a modest edge over discrete majority vote: R_hd=0.0625 vs R_sym=0.0375 (win = +0.025), but both are near the 1/48=0.021 chance floor there — the win is real but marginal and only visible exactly at the collapse boundary | `data/exp_read_bridge_noise_tolerance_hd_vs_symbolic_v1/metrics.json` (`cleanup_recovery`), atom `math::MM_read_bridge_noise_tolerance_hd_vs_symbolic_v1...` |

---

## 2. THE CAPACITY STORY

Three genuinely different "capacity" numbers appear in the record; they answer different questions and
must not be conflated (this is exactly the reconciliation the Director asked for):

1. **~10-item SHRUTI/working-memory band (brain-referenced, m=2-6 to ~24 robust, cliff starts m=32 at N=256).**
   This is the number that matters for "how many role-fillers can ONE live bundle hold before crosstalk
   bites at all." Measured directly: robust through m=24, first drop at m=32, at N=256
   (`math::MM_role_filler_factorization_compgen_v1`). It generalizes: at higher N the same *relative*
   headroom recurs (m=3 stays robust across correlation at N=4096; m=10 breaks under high correlation at
   the same N) — so this is fundamentally an **m-vs-N-vs-content-correlation** surface, not a single scalar.
   The brain's SHRUTI ~10-binding ceiling sits comfortably inside this substrate's robust band (m<=24 at
   N=256; presumably much higher m at N=2048/4096/8192, though the compgen cell's own high-load stress test
   was run at N=4096 with m<=10, not swept to m=24-32 at that N — the exact m=24-32-equivalent cliff at
   N=4096/8192 is UNVERIFIED, only inferred by analogy to the N-scaling law in row 2 below).

2. **N/log(N)-scaling crosstalk onset (Kanerva form, sequence-binding): K*=100 @ N=2048, 500 @ N=8192,
   1000 @ N=16384 (2.1-3.5x above the closed-form conservative bound).** This is a DIFFERENT experimental
   axis (positional/sequence binding into a bundle, not role-filler binding), but it is the best on-disk
   N-scaling LAW because it is chain-graded (cert+1, 3-seed near-exact reproduction). If C's live map behaves
   like a bundle-of-bound-items in the same crosstalk-limited way (there is no on-disk proof it does — it's
   role-filler not positional — but the mechanism class, phasor-unbind crosstalk, is the same), this gives
   the expected ORDER OF MAGNITUDE for how K* should scale with N: roughly linear in N/log(N), prefactor
   ~2-3.5x, not a fixed constant independent of N.

3. **128 bound-relations/bundle @ N=2048 (the number in the Director's prompt).** This is a REAL measured
   bundled-map ceiling (0.9703 at 128, dropping to 0.5687 at 256) from the SAME cell family as (1) above but
   at production N=2048 with a richer toy-KB vocabulary (~200 atoms, 230 facts). **It is NOT the number that
   gated the reported 230-fact single-hop 1.0** — that used a sharded (per-fact vector) map, selected by
   exact cosine match, which sidesteps bundled crosstalk entirely. The 128 number is the right one to use
   for "how big can ONE live bundle be" but the 230-fact/1.0 result says nothing about surviving crosstalk
   at that scale.

**Reconciliation:** all three numbers are consistent once you separate the AXIS. The ~10-24 brain band and
the 128-at-N=2048 number are the SAME kind of measurement (bundled role-filler capacity) at DIFFERENT N
(256 vs 2048) and are roughly consistent with an N-scaling law like (2) — capacity grows with N, with the
128 number sitting where a naive N/256*24 ~ 192 extrapolation would roughly land (128 measured vs ~190
extrapolated — same order of magnitude, not exact, and no cell has directly tested the m-cliff at N=2048
with the SAME cliff-definition as the m=256 cell, so treat this cross-cell extrapolation as INFERRED, not
measured). The 230-fact/1.0 sharded result is a DIFFERENT axis (sharded-map exact-match) and should never be
cited as "the map survives 230-way crosstalk" — it doesn't test crosstalk survival at all.

**Sharding threshold (when to shard to the store).** The direct on-substrate precedent (`notes/research_crux_v3_sharded_recovery_capacity_2026-07-10.md`, drawing on PP-127/128/116/Chain3): monolithic/bundled recall COLLAPSES at S=32 shards'-worth of load (recall=0.060, essentially noise) while per-shard recall holds at 1.000 across shard counts S1-S32 with interference=0.000 (`sharding_scaling_law_cpu_v1`, HARD_PASS). Content-derived shard routing (no privileged oracle) achieves 1.000 routing/e2e/oracle accuracy (`shard_routing_accuracy_cpu_v1`). **Hard design constraint on aggregation:** every genuine on-substrate positive result composes shards by an independent-decode-then-discrete-merge (list/score merge of already-decoded candidates); every attempt at a JOINT vector-level cross-shard operation (tensor-bind + shared matmul: `Op B`, 0.018 accuracy, 50x below random; second-order cross-shard correlation: `Op E`, indistinguishable from noise) HARD_FAILS. This is the single clearest actionable constraint for C's shard-merge design.

---

## 3. THE NOISE STORY (reader-noise-driven degradation of the reasoning map)

Source: `math::MM_read_bridge_noise_tolerance_hd_vs_symbolic_v1` / `data/exp_read_bridge_noise_tolerance_hd_vs_symbolic_v1/metrics.json`, N=2048, 5 seeds, 200 distractors, 230-fact clean-query/clean-gold setup with the STORE corrupted (this tests robustness to store/extraction noise, NOT extraction itself — clean queries throughout).

Three corruption regimes were tested by sweeping p (corruption rate) over {0.0, 0.1, ..., 0.6, 0.8}, and the
metrics file explicitly equates **p = 1 - reader precision**, so the realistic band p in {0.4, 0.5, 0.6}
corresponds to the reader's actual precision range (~0.4-0.6, i.e. the memory-noted 0.500->0.557 zero-recall-cost
reader sits almost exactly here — p~0.44-0.50).

| Corruption type | What it models | HD single-hop @ p=0.5 | Symbolic @ p=0.5 | Advantage @ p=0.5 | Shape |
|---|---|---|---|---|---|
| **MIX** (partial slot corruption) | one binding in a fact corrupted, rest clean | 0.6366 | 0.5244 | **+0.112** (grows with p: +0.13 avg single, **+0.28 avg multi-hop**) | GENTLER slope for HD (slope_hd=-0.730 vs slope_sym=-1.053) — a real rate advantage, not just a level offset |
| **WRONG** (binding replaced with a plausible-wrong value) | reader emits a confident wrong extraction | 0.3049 | 0.1707 | **+0.134** (avg +0.154 single / +0.189 multi; margin over the +0.15 threshold is thin, 0.0037) | Advantage is a LEVEL OFFSET, not a gentler rate — HD's slope (-1.223) is marginally STEEPER than symbolic's (-1.210); HD starts higher and stays higher by roughly a constant amount, it does not degrade more slowly |
| **MISSING** (relation dropped entirely) | reader misses a fact | 0.5756 | 0.5610 | **+0.015 — NO STRUCTURAL ADVANTAGE regime** (honestly reported, not hidden); both substrates fail together | Flat, near-zero gap at every p |

Multi-hop chaining: genuine "double jeopardy" — each of 2 hops can independently break under noise for
symbolic (each needs an exact match), vs HD's chained partial-match tolerance; this is why the multi-hop MIX
gap (+0.28) is larger than the single-hop gap (+0.13). Caveat: of the 82 multi-hop test queries, only ~17
strictly require the cross-fact join (per the earlier auditor correction on the parent bridge atom) — the
multi-hop noise-advantage numbers inherit that same scope caveat.

Both substrates eventually collapse under enough noise: at p=0.8, HD MIX-single drops to 0.424 and
WRONG-single to 0.071 (the pre-registered "must-degrade" control fires — HD is not immune, it is more
graceful, not lossless). Symbolic MIX collapses from 1.0 to 0.503 over the realistic band (its own
"arms differ, one variable" control).

**Cleanup/pattern-completion is the outlier — a cliff, not a graceful curve** (see table in Section 1):
single-observation recall is perfect through sigma=2.0 then collapses to 0.029 at sigma=3.0. The
bundle+cleanup analog-averaging advantage over discrete majority vote (R_hd=0.0625 vs R_sym=0.0375) is real
but modest, and only visible exactly at the collapse boundary — do not expect graceful cleanup degradation
in general; expect a threshold effect.

**Honest scope on the whole noise story:** synthetic STORE corruption with CLEAN queries and CLEAN gold —
this measures robustness to already-encoded noise, not the reader's live extraction process. The atom
explicitly flags the natural next step ("CG revival") as running this same test on REAL reader extraction
noise end-to-end, which has NOT been done.

---

## 4. IMPLICATIONS FOR THE C BUILD (concise)

- **Bundle sizing.** Don't design C around a single scalar "capacity number." Use m (bindings/bundle) vs N
  vs content-correlation as a 3-axis budget: at brain-realistic m (2-6, maybe up to ~10-24 with margin) the
  substrate has wide headroom at any N tested (256 and up); the 128-at-N=2048 number is a reasonable
  provisional ceiling for a SINGLE live bundle if it's storing role-filler bindings at that N, but treat it
  as construction-scoped (only directly measured on a 230-fact/~200-atom-vocab toy KB) and re-verify at C's
  actual N and vocabulary size before relying on it. If C uses N=8192 or larger, expect the true ceiling to
  be well above 128 (by the N/log(N) scaling law) but this has NOT been directly measured for role-filler
  bundles at N>2048 — only for sequence-binding.
- **Shard before the bundle saturates, not after.** The sharding precedent (Section 2) shows a clean
  collapse at S=32-shards'-worth of load with content-derived routing achieving 1.000 — build C to shard
  proactively (e.g. per-document, per-topic, or per-entity) once approaching the measured bundle ceiling,
  using a content-derived key, and merge shards ONLY as a discrete list/score merge across independently
  decoded candidates. Never implement cross-shard merge as a joint vector operation (bind, matmul, or
  second-order correlation across shards) — every on-substrate attempt at that class of operation has
  HARD_FAILED (Op B: 0.018 vs 1.000 sequential; Op E: noise-indistinguishable).
- **Expect graceful-but-modest degradation from reader noise, except on cleanup.** At a reader operating
  near p~0.44-0.56 (matches the current reader's measured precision band), expect roughly 0.30-0.71
  single-hop accuracy depending on WHICH kind of noise dominates (MIX partial-corruption is the most
  forgiving regime for HD; WRONG confident-wrong-extraction is the harshest and HD's edge there is a level
  offset not a rate advantage; MISSING relations get zero structural help from HD — a reader that silently
  drops facts needs a different fix, not a more-graceful bundle). Cleanup/pattern-completion should be
  budgeted as a STEP function (fine to ~sigma=2, collapses by sigma=3), not assumed graceful — if C leans on
  cleanup-memory for recovery, put the operating point well inside sigma<2, and prefer modern/iterative/soft
  cleanup variants over classical Hopfield (measured DOMINATED in 3/3 seeds).
- **Binding-op choice: pick FHRR for the sub-cliff readout-quality margin, not because it moves the cliff.**
  The crosstalk ONSET is invariant across binding families (Hadamard/HRR/FHRR all hit K_cliff=750 at the
  same N/regime) — so switching binding op will NOT buy more raw capacity. But FHRR's per-unit readout
  quality well below the cliff is 2.3-3.25x better than Hadamard/HRR-real at the same load in the one
  cross-section measured (alpha=0.5: FHRR 0.867 vs HAD 0.267 vs CIR 0.367) — this is the strongest reason to
  use FHRR specifically for C's live map, on top of it already being the zero-training / no-learning-step
  target identified by the Stage-1 bridge.

**GAPS — regimes C will depend on that are NOT measured anywhere found on disk:**
1. **Incremental / streaming add-to-bundle.** Every capacity curve found (bundled-ceiling, cliff-graceful,
   m-sweep, N-sweep) builds the full bundle once, then tests — none test adding items ONE AT A TIME over
   time and re-querying after each addition (the actual usage pattern for a live accumulating map). Whether
   incremental construction changes the crosstalk profile (e.g. from FP rounding / renormalization drift
   after many incremental adds) is UNVERIFIED.
2. **Repeated / iterated unbind on the same bundle.** No cell found tests querying the same bundle many
   times in sequence for error accumulation, cache effects, or whether repeated unbind operations
   themselves introduce any drift (FHRR unbind is deterministic and exact per-op in isolation, but this
   substrate has not measured whether many sequential unbinds against a live, possibly-renormalizing bundle
   compound any error).
3. **Consolidation-over-time fidelity.** No cell found tests what happens to fidelity when a bundle is
   periodically "consolidated" (e.g. re-encoded, merged into a coarser representation, or moved from
   short-term bundle into long-term sharded store) across multiple sessions/passes — a capability C's
   design explicitly wants (live map -> consolidated sharded store). The nearest analogs found
   (`T3/EXP_substrate_cortex_hippo_...` cells) test ARCHITECTURAL composition of a cortex layer with a
   Hopfield cleanup layer at one point in time, not fidelity across repeated consolidation events — a
   different question.
4. **Real reader-extraction noise end-to-end (not synthetic store-corruption).** The noise-tolerance result
   in Section 3 is explicitly flagged by its own atom as testing store-corruption with clean queries/gold;
   the harder, more relevant test (a live reader's actual extraction noise feeding the map, scored against
   independent ground truth) is named as the next step and has not been run.
5. **Bundled role-filler capacity cliff at N>2048.** The clean N-scaling law (Section 2, item 2) is measured
   for sequence/positional binding, not role-filler binding; the role-filler bundled-capacity number (128) is
   only measured at N=2048. Whether role-filler bundling follows the same N/log(N) scaling as sequence
   binding is a plausible but UNVERIFIED extrapolation.
6. **Cross-level crosstalk compounding in a hierarchical/nested bundle (C/vision quadtree regime — see
   Section 5).** No cell tests whether level-1 bundling noise measurably corrupts a level-2 unbind when
   shared full-N bundling is used at every depth level (as opposed to disjoint per-level bands, which
   sidesteps the question and has its own separately-measured depth data). Depth-2 itself is safely inside
   two different measured-clean results (Section 5.1), but the COMPOUNDING mechanism specifically is
   untested.
7. **Resonator-based blind (not known-key) factoring of a hierarchically-bound vector (Section 5.3).** Only
   FLAT, single-level blind K-way factorization has been measured (steep collapse K2=1.0/K3=0.7/K4=0.14,
   partial rescue to ~0.46-0.80 with restart-plurality). No cell applies resonator/iterative-cleanup search
   to a nested/tree-structured bind. Not needed if per-level position keys are known in advance (the natural
   quadtree design), but a gap if any part of C's design requires blind structural recovery.

---

## 5. HIERARCHICAL / RECURSIVE-BUNDLE REGIME (C/vision-relevant: quadtree-style nested binding)

**Scope of this addendum (USER-driven, folded in without restarting the note):** the C-adjacent vision idea
depends on encoding a scene as a shallow tree (e.g. depth-2 quadtree: ~4 position-bound sub-bundles, each
itself ~4 position-bound sub-bundles, ~16 leaves), read back by unbinding a position key per level. This
section characterizes that regime from EXISTING data. No cell on disk tests a literal quadtree/scene
structure — the numbers below are the closest measured analogs, honestly scoped.

### 5.1 Depth ceiling for nested/hierarchical binding

Two genuinely different measured results bear on "depth," from two different encoding SCHEMES — do not
conflate them:

- **Direct FHRR bind/unbind at depth-2 (the scheme closest to the quadtree idea): 1.000 accuracy, MEASURED.**
  The nesting-clause atom's offline capacity check (`math::MM_read_nested_clause_relative_third_reader_v1...`,
  550455f5f) ran a genuine depth-2 FHRR bind/unbind readout on 51 emitted nest-links at N=2048:
  `depth2_readout_acc: 1.0`. This is a real bind-then-unbind-through-2-levels test (not by-construction),
  though on a SMALL sample (51 links, 1 configuration) and it is explicitly flagged as a CAPACITY check on
  whatever structure was emitted, not an extraction-correctness measure. **Depth-2 sits safely inside this
  measured-clean result — there is no sign of degradation at depth-2 in this cell.**
- **Recursive-constituency tree depth via block-local disjoint-band SBC (a DIFFERENT encoding scheme —
  sparse binary codes with non-overlapping bands per level, NOT FHRR superposition/bundling):**
  `math::MEASURED_MECHANISM_GRAMMAR_recursive_constituency_plus_function_word_operators...` (N=8192, 3
  seeds, commit 5d48a3844) measured a depth envelope: tree_exact = 1.000 at L1-L4 (cv=0) -> 0.975 at L8 ->
  0.608 at L12 -> 0.054 at L16. **Depth-2 is deep inside the flat, perfect part of this curve too (L1-L4 all
  1.000).** The wall only appears at L8+ and is explicitly diagnosed as a CONTENT-TERMINAL block-capacity
  wall (the disjoint per-level block shrinks as depth grows: block-size/k per level = 1024/20, 512/10,
  341/7, 256/5, 128/3, 85/2, 64/1), NOT a structural-binding wall — structure sub-metrics (attach=0.9967,
  func=0.9665, embed=1.000) still survive at L16 even as terminal-slot recovery degrades (0.739) and
  all-slots-correct tree_exact collapses.
- **Human/theory reference point (cited, not this substrate's own re-measurement):** the nesting atom also
  carries a `depth_ceiling` field citing a separate STEP-0 probe (D1 accuracy 0.33-0.62 -> D2 0.13-0.20) with
  the annotation "Plate-1995 bounded-depth, human center-embedding ~2-3; brain-faithful, not re-run in this
  VET." **This D1/D2 number is flagged on-disk as NOT re-verified in the same landed-VET and its exact
  source cell was not located in this synthesis pass — treat as UNVERIFIED / a secondary citation, not a
  primary measured number**, distinct from the two solid capacity numbers above. It is consistent in
  direction (depth hurts) with literature (Plate 1995's bounded chunking-tree capacity; human center-embedding
  breaking down at ~2-3 levels) but should not be quoted as this substrate's own measured result without
  locating its underlying cell.

**Verdict on Q1:** depth-2 sits safely and clearly inside the measured-clean zone on BOTH concrete substrate
results found (1.000 at depth-2 FHRR bind/unbind; 1.000 through L4 for the SBC recursive-tree scheme). The
measured walls (L8+ for SBC; untested but presumably present at deeper FHRR nesting) are well beyond depth-2.

### 5.2 Breadth x depth capacity: does ~16 leaves at depth-2 fit inside the clean working set, or does it need high-N / per-level cleanup?

This has NOT been directly measured for a quadtree (4-way fan-out x 2 levels); the honest answer is
constructed from the closest measured pieces, with the compounding step flagged as a gap:

- **Per-node fan-out (m=4 bindings bundled at each node) is trivially inside the measured-robust band.**
  Section 1/2's role-filler bundle-capacity cliff is robust through m=24 simultaneous bindings at N=256 and
  only starts degrading at m=32 (`math::MM_role_filler_factorization_compgen_v1`). A quadtree node bundles
  only 4 children — this is far inside the clean zone at ANY N tested (256 and up), with no correlation-driven
  early failure expected at such low m (the m=3 low-load stress test stayed robust, 0.55-0.59, across the
  FULL correlation range 0.015-0.597 tested — `math::MM_role_filler_factorization_realcontent_cg_v1`).
- **Total structure size (16 leaves via 5 bundles: 1 root + 4 children, each holding m=4) is well inside the
  128-bound-relations-per-bundle ceiling measured at N=2048** (`math::MM_read_bridge_rolefiller...`,
  capacity_curve 128: 0.970), IF the 16 leaves were flattened into ONE bundle rather than nested — but that
  is not what a quadtree does, and is not the relevant comparison (see next point).
- **The compounding question — does level-1 bundling noise feed into level-2 unbind as extra corruption —
  is a GAP, not measured.** A true nested/hierarchical bundle means the level-2 unbind operates on a vector
  that already carries level-1's bundling crosstalk (from the other 3 sibling quadrants superposed in), not
  a clean vector. No cell on disk tests this specific compounding step for HD bind/bundle. The nearest
  ON-SUBSTRATE analog for "does noise compound across sequential/recurrent steps" is from a DIFFERENT
  domain (PFC-basal-ganglia control gating, not VSA binding) but is explicitly flagged in the ledger as a
  cross-mechanism generalization pattern (MM_TENTATIVE, 3rd instance): *"multi-step lookahead COMPOUNDS
  cleanup noise rather than reducing control error — each extra rollout/lookahead step injects fresh cleanup
  noise that dominates any anticipatory benefit"* (composes with resonator convergence-basin-proliferation
  and autonomous-decomposition compounding-error as the other 2 instances). This is a real, if analogical
  (not HD-bind-specific), warning sign that sequential/recursive operations tend to compound noise rather
  than average it away — it should be read as a reason to test the 2-level compounding case directly before
  relying on it, not as proof that it fails.
- **Reconciling with the ~10-item SHRUTI band for the RECURSIVE case:** the SBC recursive-tree result
  (Section 5.1) gives the best AVAILABLE indirect evidence that depth-2 is fine and the crosstalk-compounding
  concern only bites much deeper (L8+) — but that result uses DISJOINT bands (no bundling crosstalk between
  levels by construction), which sidesteps the exact compounding question a superposition-based (bundled)
  quadtree would face. **Two design options are visible in the existing data, not one:** (a) allocate
  disjoint N-slices per depth level (measured clean to L4, avoids compounding entirely, costs shrinking
  per-level capacity as depth grows — proven wall only at L8+); or (b) use shared full-N bundling at every
  level (matches the FHRR mechanism already used elsewhere in the substrate, m=4 fan-out per node is
  trivially safe in isolation, but the 2-level COMPOUND has not been measured). Recommendation for C: prefer
  (a) for a shallow, depth-bounded structure like a depth-2 quadtree, since it is the option with actual
  depth-2-and-beyond measured data; if (b) is preferred for mechanism-uniformity with the rest of the
  substrate, run the 2-level compounding test before relying on it (see Gaps, Section 4, item 1 also applies
  here).

### 5.3 Resonator / iterative-cleanup factoring of a hierarchically-bound vector

**This is a genuine GAP — no cell on disk resonator-factors a hierarchically/recursively-bound (quadtree-like)
vector.** What exists, and why it is NOT a direct substitute:

- **If the position keys at each level are KNOWN in advance** (e.g. a small fixed codebook of 4 quadrant
  labels x depth, which is the natural design for a quadtree), reading back a level does not require a
  resonator/blind-search at all — it is a direct unbind with the known key, exactly the mechanism already
  characterized in Sections 1-2 (BIND row) and 5.1 (the depth-2 FHRR check, 1.000). A resonator is only
  needed when you do NOT know a priori which of several codewords was used and must search jointly for it.
- **The on-disk resonator data is for BLIND, SIMULTANEOUS K-way factorization (a harder, different task),
  and it is NOT gentle:** `math::MEASURED_MECHANISM_resonator_K_way_factorization_collapse...` (N=4096, M=30
  codebook per factor, MAXIT=60) measures K2=1.000, K3=0.700, K4=0.142 — a steep, proven-mechanism collapse
  (proven NOT margin-driven; diagnosed as convergence-basin-proliferation among up to M^(K-1) competing
  spurious joint fixed points in iterative alternating-projection search). A follow-up rescue
  (`math::MEASURED_MECHANISM_resonator_K4_external_reset...`, Glauber finite-T dither + R=10 restart
  plurality vote, 3 seeds) lifts K4 from a single-shot 0.133 to a plurality-vote 0.464 at best T0=0.35, with
  an ORACLE ceiling of 0.80 (i.e. the true fixed point IS reachable in 80% of restarts, but raw plurality
  only harvests 46% of that due to restart-decorrelation, not unreachability) — genuine partial rescue, still
  well short of 1.0, and still a fundamentally different (blind, simultaneous) task than a quadtree's
  known-key sequential read.
- **Net assessment:** if C's quadtree design uses KNOWN per-level position keys (the natural design), the
  relevant capacity data is the BIND/UNBIND and bundle-capacity numbers already in Sections 1-2, not the
  resonator numbers — and depth-2 is safely inside the measured-clean zone (5.1). If any part of the design
  requires BLIND recovery of which position/child a piece of content belongs to (rather than a known,
  fixed small alphabet), treat that as needing resonator-class machinery, and budget for the steep K-way
  collapse above (fine at K=2, real trouble by K=4) rather than assuming graceful behavior.

**Bottom line for the C/vision fan-out x depth question:** a depth-2, ~4-way-fan-out (~16 leaf) quadtree
with KNOWN per-level position keys is comfortably inside every measured envelope found (per-node fan-out
m=4 vs. robust-to-24; depth-2 direct-unbind measured 1.000; SBC recursive-tree measured 1.000 through L4).
The two things NOT measured and worth a cheap direct test before relying on them: (1) whether level-1
bundling crosstalk measurably corrupts the level-2 unbind when using shared full-N bundling at every level
(vs. the disjoint-band alternative, which sidesteps this and has direct depth data); (2) resonator-style
blind factoring of a nested structure, which is not needed if position keys are known but would be
expensive (K-way collapse) if required.

---

## Provenance notes / honesty flags

- All 2026-07 atoms cited above carry `cert_status: proven_bound` (MEASURED_MECHANISM tier) with
  off-disk/independent-recompute verification per their `verified_off_data` fields — treated as solid.
  The Hopfield-capacity legacy cells (`T3/EXP_hopfield_capacity_gpu_v1` etc.) are flagged
  `provenance_quality: LEGACY_EXCERPT`, `era: PRE_SUBSTRATE_BUILD`, `relevance_tier: MEDIUM` on disk —
  directionally trustworthy (exponential vs linear capacity is a robust, well-known result independently)
  but older and less rigorously re-verified than the current substrate's own cells.
- The `T2/EMPIRICAL_BUNDLED_FHRR_CHAIN_COMPOSITION...` atom's headline (bimodal, no mid-band) is cited but
  its on-disk `description` field is empty — the claim is UNVERIFIED beyond the atom name/title and should
  not be leaned on without locating its metrics file.
- The binding-op-family and order-binding-family "invariance" cells are formally HARD_FAIL results (they
  disproved the hypothesis that op-family changes capacity) but are reported here as substantively useful
  POSITIVE findings (invariance is itself information) — this mirrors how the cert ledger's own synthesis
  atom (`math::T3/META_synthesis_binding_family_capability_invariance...`, cert_status
  `measured_mechanism_tentative`) frames them: TENTATIVE (narrow surface: 3 ops/axis, 2 axes, WM regime only,
  2-3 seeds) pending expansion (seed-7 completion, 5 ops/axis, a new binding class) before promotion to
  MM-standard or chain-grade.
- Numbers under "THE NOISE STORY" are read directly from `metrics.json` `curves` arrays (not re-derived by
  the author of this note beyond simple subtraction for the advantage column) — cross-checked against the
  atom's own headline decision_numbers where present and consistent.
