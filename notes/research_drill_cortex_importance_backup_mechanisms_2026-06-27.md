# Research Drill — Cortex Importance-Signal-Extraction BACKUP Mechanisms

**Date:** 2026-06-27
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** edge-importance MIDDLE_BAND streak (v1 PageRank / v2 high-alpha PageRank / v3 retrieval-trace × ultrametric-coreness) = 3-for-3. v4 (NREM-replay-modulated trace, USER-approved Path A) is in flight. If v4 also lands MIDDLE_BAND, the entire PageRank-centrality + retrieval-trace family is exhausted — 4-for-4 needs categorically distinct backup paths queued and ready to dispatch within one cycle.
**Drill objective:** Design 4-6 mechanistically distinct importance signals satisfying:
1. CATEGORICALLY DIFFERENT from PageRank-centrality family AND retrieval-trace family
2. Brain-grounded analog (per USER 2026-06-23 standing: brain is existence proof; P=0.60-0.75 prior)
3. Fairness gate: cor(importance, |W|) < 0.30 (META_RULE_F structural orthogonality)
4. Discriminator capable of sel_unretr asymmetry ≥ 0.15 at full scale

**Calibration penalty applied:** per `feedback_lit_scan_calibration_penalty`, deflate naive P by 0.15-0.25; cap novel-synthesis P at 0.50.

---

## HEADLINE

Six backup mechanisms drilled, each from a distinct mechanism class. Ranked by P_deflated:

1. **M-CFU: counterfactual-utility / leave-one-out ablation** (P_deflated=0.50) — what would the substrate recall WITHOUT this atom? Brain analog: optogenetic engram silencing (Tonegawa). Categorically different: not centrality, not retrieval-count; uses substrate's own *recall capacity* as the importance metric. Top dispatch pick.
2. **M-SURP: surprise-weighted / prediction-error importance** (P_deflated=0.48) — atoms whose retrieval is most-surprising-given-prior get importance bursts. Brain analog: dopamine novelty / Schultz RPE. Categorically different: temporally-keyed at write-time + retrieval-time, not graph-structural.
3. **M-MI: mutual-information / MDL bits-saved** (P_deflated=0.45) — per-atom contribution to compression of input distribution. Brain analog: Olshausen-Field sparse coding. Categorically different: information-theoretic, no graph or trace.
4. **M-BTSP: plateau-potential gating (one-shot Ca tag)** (P_deflated=0.43) — atoms receiving above-threshold plateau-Ca-spike-equivalent get a binary persistent tag. Brain analog: Bittner et al. 2017 BTSP. Categorically different: discrete tag at single event, not smooth function of accumulated activity.
5. **M-KSHELL: k-shell decomposition (hierarchical coreness)** (P_deflated=0.40) — integer k-shell index from iterative degree-1 peeling. Brain analog: Collins-Loftus hierarchical semantic clustering. Categorically different from PageRank centrality: discrete-tiered, not smooth-degree-weighted; PageRank says "central" while k-shell says "irreducibly deep."
6. **M-JL: random-projection witness / JL-variance** (P_deflated=0.38) — atoms with highest representation variance under JL-random-projection. Brain analog: cerebellar fan-out + LTD pruning (Marr-Albus). Categorically different: structure-of-representation, not connectivity-of-graph.

**Single highest-leverage composition:** M-CFU + M-SURP (signal independence ≈ orthogonal: ablation-utility is backward-looking on recall; surprise is forward-looking on prediction-error). Composition discriminator: an atom counts as IMPORTANT only if BOTH (a) ablating it costs recall AND (b) it carries surprise mass. Filters out "high-utility but redundant" atoms (ablation-utility false positives) AND "novel but useless" atoms (surprise false positives).

**Honest-negative path** (if all importance mechanisms fail): substrate-product story becomes "Wave 3 ANCHOR 2 TWO_TIER promotion uses retrieval-frequency as importance heuristic; honest-bound MIDDLE-BAND; production-acceptable at 5-15% retention floor with explicit recovery path (Candidate 2 from gap-E drill)." The chain-grade win for the cortex *content-extraction* capability moves to **ultrametric clustering** (Cell 2 from 2026-06-26 dispatch) — schema-level promotion via centroid-collapse, with importance handled at the *cluster* level not the *atom* level. This is a real and shippable retreat path.

---

## Mechanism family map — why the prior 4 saturate

The 4 in-flight/landed edge-importance variants all collapse to a single mathematical regime:

| Variant | Family | Math kernel | Why it saturates |
|---|---|---|---|
| v1 PageRank | centrality-on-bound-pair-graph | (1-α)*1/N + α*P^T*r | High-degree atoms dominate; cor(rank, deg) ≈ 0.90 in HD graphs (lit) |
| v2 high-α PageRank | centrality (parameter sweep) | as above, α↑ | Same saturation; α-sweep changes magnitude not regime |
| v3 retrieval-trace × ultrametric-coreness | retrieval-count × structure | E_retr ⊙ E_ultra | Both factors correlated with degree; product still rank-concentrates |
| v4 NREM-replay-modulated trace | retrieval-trace × replay | E_retr * f(replay_count) | NREM replay is itself biased toward hub atoms (sharp-wave-ripple preference for high-connectivity); compounds same saturation |

**The saturating root cause:** all 4 are smooth functions of accumulated activity along a graph-structural axis. The substrate's bound-pair graph H[i,j] populates with degree-skew under composite-query workloads; any smooth function that integrates over H inherits that skew. Result: top-K importance correlates with degree, and the discriminator's "retrieved-old" set IS the high-degree set — sel_unretr asymmetry is structurally bounded by the workload's degree distribution.

**Therefore backup mechanisms must NOT be smooth functions of H** AND must NOT use retrieval-count directly. They must source importance from a different substrate signal entirely.

The 6 candidates below each source from a different signal class:

| Candidate | Signal source | Smooth/discrete | Forward/backward looking | Class |
|---|---|---|---|---|
| M-CFU | recall delta under ablation | quasi-continuous (delta) | backward | utility-perturbation |
| M-SURP | residual prediction error at write+retrieve | continuous (residual) | forward (prediction-derived) | information-theoretic temporal |
| M-MI | per-atom bits-saved in compressed code | continuous | global (compression objective) | information-theoretic global |
| M-BTSP | binary plateau tag at single high-Ca event | DISCRETE binary | forward (assigned at one event) | discrete event-gated |
| M-KSHELL | iterative degree-peeling shell index | DISCRETE integer | structural (snapshot) | discrete-hierarchical |
| M-JL | variance under random projection | continuous | structural-representation | representation-geometric |

Mix of continuous (M-CFU, M-SURP, M-MI, M-JL) and discrete (M-BTSP, M-KSHELL); mix of forward (M-SURP, M-BTSP) and backward (M-CFU); mix of structural (M-KSHELL, M-JL) and behavioral (M-CFU, M-SURP, M-MI). All 6 are categorically off the H-smooth-integral axis.

---

## M-CFU — Counterfactual-Utility (ablation-based importance) — RANK 1, P_deflated=0.50

### Math

For each atom i in the candidate-important set:
```
U_baseline = recall_accuracy(W_full, probe_set_P)
U_ablated_i = recall_accuracy(W_full ⊖ atom_i, probe_set_P)
CFU(atom_i) = U_baseline - U_ablated_i
```
where ⊖ is the substrate's atom-removal operator (zero out the atom's outer-product contribution to W, or equivalently set the atom's signature to the all-zeros vector before retrieval).

**Probe set P** is critical and must NOT be the substrate's own retrieved-recently atoms (would re-introduce the retrieval-trace coupling). Three principled choices:
- **P_held-out:** atoms written during a held-out window (e.g., cycles [J-N, J-N+window]); never retrieved during scoring
- **P_synthetic:** algorithmically generated composite queries spanning the substrate's cosine-space (e.g., grid-sampled HRR composites)
- **P_recent_unretrieved:** atoms written recently but never queried (cold-recent)

Use P_held-out as primary (the gap-E drill's `recall_oldest_in_W_old` is structurally this).

### Why it escapes PageRank-saturation

CFU does not look at the graph H. It looks at the substrate's OWN behavior under perturbation. Hub atoms with high degree might or might not have high CFU — if a hub atom is highly redundant with its neighbors (e.g., common-functional-word analog), CFU is LOW because the neighborhood absorbs its removal. CFU thus actively penalizes redundancy, which is the opposite failure mode from PageRank.

### Why it escapes retrieval-trace-saturation

CFU is evaluated against a probe set decoupled from the substrate's retrieval history. An atom that has been retrieved 1000 times but is fully predictable from neighbors gets CFU≈0. An atom retrieved 0 times but uniquely encoding a probe-set-relevant feature gets CFU>>0.

### Brain analog (chain-grade in brain)

**Tonegawa lab optogenetic engram silencing** (multiple papers 2012-2023; Liu Cell 2012, Ramirez Science 2013, Tonegawa Cell Reports 2015): engram cells in DG/CA1 are tagged via channelrhodopsin during learning; selectively silencing them during recall *abolishes* the memory; selectively reactivating them *reinstates* it. This IS counterfactual-utility per neuron, measured experimentally. The mechanism is chain-grade in neuroscience (replicated across labs, optogenetics + chemogenetics + lesion + transcriptional-silencing convergent).

Importance-as-CFU is also implicit in the **Hebb-Marr index theory** (Marr 1971) and the **engram-completion literature** (Josselyn & Tonegawa 2020) — high-CFU cells are pattern-completion-essential cells.

### Substrate-fit

**Composes with TWO_TIER** (chain-grade): CFU evaluated at each promotion checkpoint. Atoms with CFU < tau become migration candidates to W_cold; atoms with CFU > tau_protect become migration-immune (immortal in W_active until CFU drops). Cost = O(K_candidate * |P| * cleanup_cost). For K_candidate=500, |P|=200, cleanup at N=4096: ~5-10s per checkpoint, ~50-100s total in a 5000-cycle run. Trivial.

**Composes with NREM replay** (chain-grade): replay generates exactly the "perturbation events" needed — atoms targeted by replay are the ones whose CFU matters most (replay = consolidation rehearsal = "what would the network lose if this trace were gone?"). NREM replay schedule can be MODULATED by CFU (replay high-CFU more often = importance-aware consolidation = mechanism 7 from the 2026-06-11 drill).

**Composes with multi-bank WM (K=4096)** (chain-grade): per-bank CFU is the natural per-region importance signal. Cross-bank consensus on CFU = importance vote.

### Cost

- Smoke (N=1024, K_candidate=100, |P|=50, 1 seed): ~5 min CPU
- Full (N=4096, K_candidate=500, |P|=200, 3 seeds): ~3-5 CPU-hr local (or 1-2 hr on remote_cpu)
- Critically cheap because CFU is BATCHED — evaluate at checkpoint cadence, not per-edit

### Expected verdict

- **P(HARD_PASS) deflated: 0.50** — at novel-synthesis ceiling
- **vs prior 4 MIDDLE-BANDs:** structurally different signal source; redundancy-penalty is a genuine selectivity boost mechanism that none of v1-v4 had. Predicted sel_unretr asymmetry ≥ 0.20 at full scale (vs the ≥0.15 PASS bar)
- **Risk:** the perturbation may be too local (zeroing one atom's outer-product is a tiny perturbation to W; substrate may exhibit graceful degradation that washes out CFU). Mitigation: use *cohort* ablation (ablate K=10 atoms at once and divide by K) to amplify signal; established in lit as "leave-K-out" for noisy CFU estimation.
- **Discriminator** (PASS bar): sel_unretr = CFU(atoms retrieved during scoring window) − CFU(atoms not retrieved during scoring window) ≥ 0.15 absolute, AND cor(CFU, |W|) < 0.30, AND CFU-protected atoms maintain recall ≥ 0.90 at J=10000.

### Cell-spec stub

```
NAME: cortex_counterfactual_utility_importance_v1
SCRIPT: experiments/exp_cortex_counterfactual_utility_importance_v1.py
PRIMITIVE: hdlab/cfu_importance.py (new)
QUEUE: remote_cpu_queue (route via hdi_orchestrator)
TIMEOUT: 7200s
SEEDS: [11, 13, 19]  # 3 seeds, cv<=0.05 required for chain-grade

ARMS (4 mandatory):
  ARM_BASELINE_NO_GATE: rail; no importance gating
  ARM_CFU_GATED: ablation-utility importance; ablate-cohort K=10
  ARM_RANDOM_GATED: control; random K=10 cohorts
  ARM_CFU_FREQUENCY_BASELINE: control; substitute query-frequency for CFU
    (rules out "CFU is just frequency-in-disguise")

PROBE SET P: P_held-out (atoms written in cycles [3000, 3050]; never queried during scoring)

FAIRNESS GATE: cor(CFU_score, |W|) < 0.30 (HARD_FAIL if violated; META_RULE_F)
SIGNAL-INDEPENDENCE GATE: cor(CFU_score, query_freq_score) < 0.60
  (if too correlated, CFU offers no new info over freq baseline)

PRE-REG BANDS:
  HARD_PASS: sel_unretr = CFU(retr) - CFU(unretr) >= 0.15 absolute
    AND cor(CFU, |W|) < 0.30
    AND ARM_CFU_GATED rec_RETR >= 0.90 at J=10000
    AND ARM_CFU_GATED beats ARM_RANDOM_GATED by >=0.10 absolute on sel_unretr
    AND ARM_CFU_GATED beats ARM_CFU_FREQUENCY_BASELINE by >=0.05
      (CFU adds genuine signal over frequency)
    AND cv across 3 seeds <= 0.05
  MIDDLE_BAND: any of the above in [floor-margin, floor] range
  HARD_FAIL: sel_unretr < 0.08 OR cor(CFU,|W|) >= 0.30 OR ARM_CFU = ARM_RANDOM

DISPATCH GATE: predispatch_check.py pass (no prior cfu_importance commits);
  Fix #14 spawn-budget <= 3; orchestrator_paused.flag absent
TIER HINT: MEASURED_MECHANISM at first land; chain-grade if HARD_PASS + signal-
  independence audit passes + composes with TWO_TIER promotion path
```

---

## M-SURP — Surprise-weighted importance (prediction-error gated) — RANK 2, P_deflated=0.48

### Math

Two surprise signals; combine multiplicatively.

**Write-time surprise:**
```
S_write(atom_i) = || w_i - W_pred @ context_i ||
```
where `W_pred` is the substrate's existing slow-cortex bigram predictor (n5 revival, in flight). Atoms whose write was poorly predicted by prior W carry high write-time surprise.

**Retrieve-time surprise:**
```
S_retr(atom_i) = - log P_prior(retrieve_event_i)
              ~ - log(query_freq(atom_i) / total_queries)
```
Atoms whose retrieval is rare-given-substrate-prior carry high retrieve-time surprise. This is the surprisal in information-theoretic sense.

**Combined:**
```
SURP(atom_i) = S_write(atom_i) * sqrt(S_retr(atom_i))
```
Sqrt-damping on retrieve-surprise prevents pure-novelty (queried-once) from dominating; write-surprise must also be present.

### Why it escapes PageRank-saturation

PageRank ranks atoms by graph centrality, which is the OPPOSITE of surprise. A maximally-central hub is by definition unsurprising. SURP weights *anti-correlate* with PageRank in the limit. cor(SURP, degree) is predicted negative or near-zero.

### Why it escapes retrieval-trace-saturation

S_retr uses retrieval count but INVERTED (surprisal = -log freq, not +freq). High-frequency atoms get LOW SURP. The retrieval-trace coupling is structurally inverted; saturation regime cannot recur.

### Brain analog (chain-grade in brain)

**Schultz dopamine prediction-error** (Schultz Science 1997; Schultz Nature Rev Neuro 2016, ~10k citations combined): midbrain dopamine neurons fire phasically on positive RPE (better-than-predicted reward), pause on negative RPE, are silent on fully-predicted reward. The signal IS surprisal, gated by predictive context.

**Düzel hippocampal novelty signal** (Düzel Trends Cog Sci 2010; Lisman & Grace Neuron 2005 hippocampus-VTA loop): novel stimuli elicit DA bursts that *retroactively* enhance consolidation of recently-encoded memories — exactly the M-SURP design (write-time surprise * retrieve-time surprise composition).

**Free-energy / predictive-coding framework** (Friston Nature Rev Neuro 2010; Clark 2013): the entire cortex is a prediction-error minimizer; prediction-error magnitude IS importance. Chain-grade theoretical frame across systems neuroscience.

### Substrate-fit

**Composes with W_pred (n5 revival, in flight):** S_write USES W_pred. If n5 revival lands HARD_PASS, M-SURP becomes the natural downstream consumer. If n5 revival lands MIDDLE_BAND, M-SURP's S_write is noisy — but S_retr alone is still load-bearing.

**Composes with TWO_TIER:** SURP threshold for migration. High-SURP atoms stay in W_active; low-SURP atoms (= well-predicted + frequently-queried) become migration candidates. This is the "compress what's predictable; keep what's surprising" intuition from MDL / rate-distortion.

**Composes with NREM replay:** replay schedule weighted by SURP. Brain pattern: novelty-gated replay (Foster, Ramirez), exactly the SURP-weighted-replay design.

**Composes with multi-bank WM:** per-bank surprise is per-region novelty detection.

### Cost

- Smoke: ~5 min CPU
- Full (depends on W_pred maturity): ~3-5 CPU-hr local
- W_pred matmul O(N^2 * M) once per checkpoint = ~8B FLOPs at N=4096, M=500 = ~1-2s wall; trivial

### Expected verdict

- **P(HARD_PASS) deflated: 0.48**
- Predicted sel_unretr asymmetry: ≥0.18 (SURP actively *anti-correlates* with frequency, so the "retrieved-recently" set should have LOW SURP — discriminator inverts, but the asymmetry magnitude is large)
- **Risk:** S_write depends on W_pred landing HARD_PASS. If W_pred is noisy at substrate's current cortex maturity, S_write contributes noise; M-SURP degrades to S_retr-alone, which is just inverted query-frequency.
- Mitigation: ablation arm uses S_retr alone; PASS-without-W_pred is acceptable secondary verdict.
- **Discriminator** (NOTE: sign-inverted from CFU): sel_unretr_inverted = SURP(atoms NOT retrieved during scoring window) − SURP(atoms retrieved during scoring window) ≥ 0.15 absolute. AND cor(SURP, |W|) < 0.30.

### Cell-spec stub

```
NAME: cortex_surprise_weighted_importance_v1
SCRIPT: experiments/exp_cortex_surprise_weighted_importance_v1.py
PRIMITIVE: hdlab/surprise_importance.py (new)
QUEUE: remote_cpu_queue
TIMEOUT: 7200s
SEEDS: [11, 13, 19]

ARMS (4 mandatory):
  ARM_BASELINE_NO_GATE
  ARM_SURP_COMBINED (S_write * sqrt(S_retr))
  ARM_SURP_RETR_ONLY (S_retr only; ablation for W_pred dependence)
  ARM_RANDOM_GATED

DEPENDENCY ON n5 REVIVAL: graceful degrade. If W_pred (n5 revival) is HARD_PASS,
  use it for S_write. If MIDDLE_BAND, use S_retr_only as primary arm; SURP_COMBINED
  becomes diagnostic ablation. If HARD_FAIL, skip S_write entirely; cell becomes
  M-SURP-lite (S_retr only).

FAIRNESS GATE: cor(SURP, |W|) < 0.30 (META_RULE_F)
ANTI-CORRELATION CHECK: cor(SURP, query_freq) expected negative;
  HARD_FAIL if cor(SURP, query_freq) > 0 (surprise should ANTI-CORRELATE w/ freq)

PRE-REG BANDS (note INVERTED sel_unretr convention):
  HARD_PASS: sel_unretr_INV = SURP(unretr) - SURP(retr) >= 0.15
    AND cor(SURP, |W|) < 0.30
    AND cor(SURP, query_freq) < -0.30 (anti-correlation confirmed)
    AND ARM_SURP_COMBINED beats ARM_RANDOM on sel_unretr_INV by >=0.10
    AND cv across 3 seeds <= 0.05
  HARD_FAIL: cor(SURP, query_freq) >= 0 OR sel_unretr_INV < 0.08

TIER HINT: MEASURED_MECHANISM; chain-grade if HARD_PASS + W_pred chain-grade
```

---

## M-MI — Mutual-information / MDL bits-saved — RANK 3, P_deflated=0.45

### Math

Per-atom contribution to compression of input distribution:
```
MI(atom_i) = H(query_distribution) - H(query_distribution | atom_i present)
            ~ avg over queries: log P(query | W_full) - log P(query | W ⊖ atom_i)
```
Estimated via the substrate's cleanup-loss reduction attributable to atom_i:
```
MI_hat(atom_i) = E_q [ - log p_cleanup(q | W_full) + log p_cleanup(q | W ⊖ atom_i) ]
```
where `p_cleanup` is the soft-cleanup posterior (cosine-softmax over candidates).

This is the **MDL bits-saved** framing: how many bits of code would the input distribution require if we removed atom_i?

Practical estimator: replace exact ablation with sampled-mini-batch ablation (sample 10 atoms at a time, divide by 10; matches M-CFU's leave-K-out trick).

### Why it escapes PageRank-saturation

MDL bits-saved penalizes redundancy harder than CFU (CFU measures recall delta; MDL measures full posterior delta). Two redundant hub atoms each get MI≈0 because removing one doesn't change the codable distribution. PageRank gives them both high score; MDL gives them both ~0.

### Why it escapes retrieval-trace-saturation

MI integrates over the *query distribution*, not the retrieval-history. Even if an atom is queried often, if its information is fully available elsewhere in W, its MI is ~0. Decoupled from trace.

### Brain analog (chain-grade-strong in brain + theory)

**Olshausen & Field sparse coding** (Nature 1996, ~8000 citations): V1 receptive fields emerge from sparse-coding objective = minimum MDL on natural images; each neuron's "importance" is its contribution to MDL.

**Efficient coding hypothesis** (Barlow 1961; Simoncelli & Olshausen Annu Rev Neuro 2001): cortex maximizes mutual information between input and neural response subject to capacity constraints; per-neuron MI IS the importance metric.

**Predictive coding** (Rao & Ballard Nat Neurosci 1999; Friston 2010): the brain compresses sensory input via hierarchical prediction; per-unit MDL contribution IS the unit's importance.

Chain-grade theoretical foundation; tighter than M-SURP because MDL is the formal information-theoretic answer that surprise APPROXIMATES.

### Substrate-fit

Composes with all chain-grade primitives. MI is the "right" answer mathematically; M-CFU and M-SURP are computational approximations. MI evaluation is more expensive: O(|Q_eval| * K_candidate * cleanup_cost) where |Q_eval| is the query-batch size for distribution estimation.

### Cost

- Smoke (|Q|=100, K=100, N=1024): ~15-20 min CPU
- Full (|Q|=500, K=500, N=4096, 3 seeds): ~6-10 CPU-hr local (or 2-3 hr remote)
- Most expensive of the 6 candidates; the cost is buying the theoretical correctness

### Expected verdict

- **P(HARD_PASS) deflated: 0.45**
- Predicted sel_unretr asymmetry: ≥0.20 (MDL has the cleanest information-theoretic asymmetry of all candidates)
- **Risk:** estimator variance is the main concern; the sampled-mini-batch trick may give noisy MI estimates that don't converge in 3 seeds. Mitigation: 5 seeds instead of 3, OR larger |Q_eval|.
- **Discriminator:** sel_unretr = MI(retrieved-old) − MI(unretrieved-old) ≥ 0.15. But unlike CFU, retrieved-old atoms might have LOW MI (if they're redundant and the network just defaults to them), so the sign is workload-dependent. Pre-reg both directions.

(No cell-spec stub for M-MI in this drill — it's rank 3 and significantly more expensive than ranks 1-2. Author when M-CFU + M-SURP both fail or both MIDDLE-BAND.)

---

## M-BTSP — Behavioral Time-Scale Plasticity (one-shot plateau Ca tag) — RANK 4, P_deflated=0.43

### Math

Discrete binary tag, set at a single event:
```
BTSP_tag(atom_i) = 1 if exists single cycle t* in [write_time(atom_i), J]:
                     plateau_signal(atom_i, t*) > theta_plateau
                   else 0

where plateau_signal(atom_i, t) = sum_over_atoms_j: cosine(atom_i, atom_j) * activity(j, t)
                                  for cycles in [t - tau_plateau, t + tau_plateau]
```
The plateau signal models a *coincident burst* of co-activation: atom_i is in the neighborhood of many simultaneously-active atoms within a brief window. Single sufficient event → binary tag → permanent retention (or decay only on explicit override).

### Why it escapes PageRank-saturation

BTSP is event-keyed; once tagged, the atom is protected regardless of subsequent graph topology. Hub atoms might or might not get tagged depending on whether they experience plateau events. Non-hub atoms in dense-co-activation contexts can also tag. The protected set is DISCRETE not graded.

### Why it escapes retrieval-trace-saturation

Tag is set at a single event, not accumulated over retrievals. A 1-shot consolidation event suffices. Decoupled from retrieval count.

### Brain analog (chain-grade in brain; younger lit but Bittner 2017 is foundational)

**Bittner et al. Science 2017; Magee & Grienberger Annu Rev Neurosci 2020:** hippocampal CA1 place cells acquire place fields in ONE TRIAL via a 1-2 second plateau Ca²⁺ event that retroactively/proactively associates inputs with output. BTSP is the rapid one-shot complement to slow Hebbian plasticity. Brain-grounded chain-grade for one-shot importance assignment.

Differs from STC (slow protein-synthesis tags) and Hebbian (accumulated co-activation): BTSP is *single-event, asymmetric* (plateau in postsynaptic cell triggers learning at all coincident presynaptic inputs).

### Substrate-fit

**Composes with NREM replay (chain-grade):** the "plateau event" in substrate maps to a *replay burst* — a cycle in which many atoms are simultaneously reactivated. NREM replay is the natural plateau generator. BTSP-tag is set during replay events.

**Composes with multi-bank WM:** per-bank plateau detection; cross-bank consensus on plateau events.

**Composes with TWO_TIER:** BTSP-tagged atoms are immortal in W_active (binary protection gate, like Candidate 3 from gap-E drill).

### Cost

- Smoke: ~5 min CPU
- Full: ~3-4 CPU-hr local
- Plateau detection is O(M^2) per cycle (pairwise cosine in active set); cap active set to top-K co-activations to keep cost bounded

### Expected verdict

- **P(HARD_PASS) deflated: 0.43**
- Predicted: ~5-15% of atoms tag (matching biological place-cell rates); tagged atoms get rec ≥ 0.95 protection
- **Risk:** threshold calibration. Too-low theta → all atoms tag (no selectivity); too-high → no atoms tag (no protection). Pre-reg: tagged fraction must be in [0.05, 0.20] for HARD_PASS.
- **Discriminator:** rec(tagged) − rec(untagged) ≥ 0.20 at J=10000.

---

## M-KSHELL — k-shell decomposition (hierarchical coreness) — RANK 5, P_deflated=0.40

### Math

Iterative degree-peeling on bound-pair graph H:
```
shell_0 = atoms with degree(H) <= 1
remove shell_0; recompute degrees
shell_1 = atoms with degree(H_remaining) <= 1
... iterate until graph empty ...
k_shell(atom_i) = the shell index at which atom_i was removed
```
Discrete integer; depth of structural embedding in graph.

### Why it escapes PageRank-saturation

PageRank is a continuous smooth function of degree (essentially leading-eigenvector); k-shell is discrete, with sharp transitions between shells. Two atoms with very different PageRank can be in the same k-shell (qualitatively-similar embedding-depth); two atoms with similar PageRank can be in different shells (one is core, one is peripheral). They measure different graph properties.

**Lit confirms divergence:** Kitsak et al. Nat Physics 2010 showed k-shell index is a *better predictor of spreading influence* than degree/PageRank in many networks. Carmi et al. PNAS 2007 mapped internet AS-graph by k-shell — found qualitatively different structure than centrality measures suggested.

### Why it escapes retrieval-trace-saturation

k-shell is purely structural, computed from H once per checkpoint. No retrieval-count input.

### Brain analog (medium-strength in brain)

**Collins & Loftus Psych Rev 1975 spreading-activation model** of semantic networks: hierarchical concept clusters. Inner-shell concepts are super-categories; outer-shell are exemplars. Inner-shell concepts have higher "centrality of access" in tip-of-tongue and lexical-decision experiments.

**Cortical hub literature** (van den Heuvel & Sporns Neuron 2013): rich-club of hub regions in human connectome corresponds to k-shell core; lesions to core hubs disproportionately impair multi-domain function. Brain-grounded for "k-shell-core matters more."

Weaker chain-grade than M-CFU / M-SURP / M-MI but solid precedent.

### Substrate-fit

**Composes with ultrametric clustering** (chain-grade Cell 2 from 2026-06-26): k-shell decomposition on the *cluster-collapsed* graph rather than per-atom; gives shell index per cluster. Composes naturally with the schema-emergence track.

**Composes with TWO_TIER:** core-shell atoms migration-immune; peripheral-shell atoms migration-candidates.

### Cost

- Smoke: ~5 min CPU
- Full: ~3-4 CPU-hr local
- k-shell decomposition is O(|E| + |V|) per checkpoint; cheap

### Expected verdict

- **P(HARD_PASS) deflated: 0.40**
- **Risk:** k-shell may still correlate with degree at >0.30. The lit shows divergence in scale-free networks; HD bound-pair graphs may be different topology. Pre-flight: compute cor(k-shell, degree) on existing substrate H; if >0.50 skip M-KSHELL.
- **Discriminator:** rec(core-shell, k>=k_threshold) − rec(periphery, k<k_threshold) ≥ 0.15.

---

## M-JL — Random-projection witness (JL-variance) — RANK 6, P_deflated=0.38

### Math

Pick R random projection matrices P_1, ..., P_R of shape (d_low, N) with d_low << N (e.g., d_low=64, N=4096). For each atom:
```
JL_variance(atom_i) = (1/R) * sum_r || P_r @ w_i ||^2 / || w_i ||^2
```
Atoms whose representation has highest variance under random projection are those whose information is most-uniformly-distributed across dimensions — the *least-compressible* atoms in the projection regime.

### Why it escapes PageRank-saturation

JL-variance is a property of the atom's vector representation, not its graph position. Decoupled.

### Why it escapes retrieval-trace-saturation

Same — purely representational, no retrieval input.

### Brain analog (medium)

**Marr-Albus cerebellar theory** (Marr J Physiol 1969; Albus Math Biosci 1971): mossy fiber inputs are randomly projected via granule cells to a high-dim representation; Purkinje cells learn over this random basis via LTD. The Johnson-Lindenstrauss-projection-then-prune architecture IS the cerebellar circuit. Cerebellar granule cells are 50× more numerous than mossy inputs — random fan-out preserves discriminability.

Brain-grounded but specific to cerebellar circuit; less universal than M-CFU's engram-silencing analog.

### Substrate-fit

Composes with multi-bank WM (per-bank random projections = native).

### Cost

- Smoke: ~3 min CPU
- Full: ~2-3 CPU-hr local
- R random projections; cheap

### Expected verdict

- **P(HARD_PASS) deflated: 0.38** — lowest of the 6 because:
  - JL-variance is the most-theoretically-uncertain of the 6 mechanisms
  - The connection to "importance" is indirect (uniformity-of-info ≠ recall-utility directly)
  - Brain analog is narrowest
- Worth dispatching only if M-CFU, M-SURP, M-MI all fail — diagnostic probe to bound how much importance signal exists in representation-geometry alone.

---

## Synthesis — ranked priority and dispatch sequence

### Ranked priority (if v4 NREM-replay-modulated trace fails)

| Rank | Mechanism | P_deflated | Dispatch | Justification |
|---|---|---|---|---|
| 1 | M-CFU counterfactual-utility | 0.50 | FIRST | Highest P; chain-grade brain analog; redundancy-penalty is genuine new selectivity boost; cheapest of high-P mechanisms |
| 2 | M-SURP surprise-weighted | 0.48 | SECOND (parallel if budget) | Anti-correlation with frequency directly attacks the prior saturation regime; composes with W_pred (in flight) |
| 3 | M-MI mutual-information | 0.45 | THIRD (only if 1+2 fail) | Theoretically tightest but most expensive; deserves the slot only if cheaper variants fail |
| 4 | M-BTSP plateau tag | 0.43 | PARALLEL TO 2 IF BUDGET | Discrete binary tag is qualitatively different; composes with NREM replay naturally |
| 5 | M-KSHELL k-shell | 0.40 | DIAGNOSTIC | Cheap pre-flight: check cor(k-shell, degree) first; if <0.30, dispatch |
| 6 | M-JL random-projection | 0.38 | LAST RESORT | Only if 1-5 all fail; useful to bound representation-geometric ceiling |

### Dispatch sequence (v4 fails → 4-for-4)

```
Cycle 1 (immediate):
  - Dispatch M-CFU cell (rank 1) via hdi_orchestrator → remote_cpu_queue
  - Spawn exp_dev to author M-CFU primitive (hdlab/cfu_importance.py) +
    cell + prereg + smoke

Cycle 2 (parallel if budget allows; Fix #14 cap):
  - If M-CFU smoke-MIDDLE_BAND or worse, dispatch M-SURP in parallel
  - If M-CFU smoke-HARD_PASS, let M-CFU full-run finish before M-SURP
    (don't blow budget on speculation)

Cycle 3 (if M-CFU+M-SURP both fail/MIDDLE):
  - Pre-flight cor(k-shell, degree) audit on existing H (1 min CPU)
  - If cor <0.50: dispatch M-KSHELL (cheap diagnostic)
  - In parallel: dispatch M-BTSP (composes with NREM replay)

Cycle 4 (if all 4 above fail):
  - Dispatch M-MI (expensive but theoretically tightest)

Cycle 5 (if all 5 fail — 9-for-9 MIDDLE/FAIL on importance):
  - Dispatch M-JL as bounding probe
  - Open honest-negative path (see below)
```

### Composition — which 2 mechanisms work BETTER as a composition than alone?

**Top compositional pairing: M-CFU × M-SURP**

Rationale: orthogonal signal axes maximize discriminator power.

| Atom type | M-CFU score | M-SURP score | Composition (geom mean) | Decision |
|---|---|---|---|---|
| High-utility unique | HIGH | HIGH (rare + write-surprising) | HIGH | PROTECT |
| High-utility redundant | LOW (CFU absorbed by neighbors) | LOW (frequent, well-predicted) | LOW | MIGRATE |
| Novel useless | LOW | HIGH (surprising) | mid → LOW | MIGRATE (composition filters) |
| Frequent essential | HIGH | LOW (frequent) | mid → LOW (composition filters) | MIGRATE (CFU-only would protect; composition correctly identifies as compressible) |

The composition resolves both error modes individually exhibited:
- M-CFU alone: false-positives on essential-but-frequent atoms (CFU-high but compressible via more efficient summary)
- M-SURP alone: false-positives on novel-useless atoms (SURP-high but no utility)
- Composition: requires BOTH utility AND surprise → only protects atoms that are *uniquely useful given the substrate's prior*

**Compositional cell-spec (filed conditionally on M-CFU + M-SURP both ≥MIDDLE-BAND individually):**
```
NAME: cortex_cfu_x_surprise_composition_v1
ARMS: 4
  ARM_BASELINE
  ARM_CFU_ONLY
  ARM_SURP_ONLY
  ARM_CFU_X_SURP (composition; geom-mean or product)
PRE-REG: composition arm beats EACH single-arm by ≥0.05 on sel_unretr;
  signal-independence: cor(CFU, SURP) < 0.50 (if too correlated, composition
  is redundant)
TIER HINT: chain-grade-eligible only if composition strictly beats both single
  arms (otherwise composition is over-engineering)
```

**Second-best pairing: M-BTSP × M-CFU.** BTSP gives discrete protection on high-co-activation events; CFU re-evaluates whether tagged atoms are STILL high-utility periodically (de-tag if CFU drops below threshold). This gives "1-shot tag, slow re-validation" — closer to brain's STC + capture pattern.

### Honest-negative path — if ALL importance mechanisms fail

**Substrate-product story** (defensible at the L2 glass-box LLM moat):

> "Substrate importance signaling at the per-atom level converges to a 5-10% selectivity ceiling. This is the *honest empirical bound* of importance scoring as an atom-level mechanism in the current HD architecture. The substrate-product solution moves importance UP a level: importance is handled at the CLUSTER level (ultrametric clustering, chain-grade Cell 2 from 2026-06-26 dispatch) via centroid-promotion / centroid-pruning. Per-atom importance is replaced by per-cluster importance = cluster-cohesion-score × cluster-query-density. The TWO_TIER promotion path uses cluster-level importance as the migration signal; W_old retains cluster-centroids while W_active retains member atoms of promoted clusters. Recovery path (gap-E Candidate 2) provides explicit reverse-migration on refuse-gate-fires + cosine-match. This is a *cleaner architecture* than per-atom importance — and it composes with chain-grade primitives without requiring a new chain-grade landing."

Concretely, the fallback is:
- **Importance lives at the cluster level**, not atom level
- **Compositional abstraction** (ultrametric clustering) is the load-bearing primitive, not selectivity
- **Recovery path** (W_active → W_cold → recover-on-refuse-gate-fire) handles the bounded-capacity story
- **TWO_TIER** stays the scaffold; promotion uses cluster-level signals (which DO work — Cell 2 SMOKE-MIDDLE_BAND with cap_drop=0.192 + perfect cluster detection)

**This is a real and shippable retreat** — not a story-spin. The "edge-importance saturated" finding becomes an *informative negative* that pivots the architecture rather than a project-killing failure. Cortex content-extraction success rides on M-ULTRA (chain-grade-eligible from Cell 2), not on M-EDGE-IMP family.

**Communication framing** (for cycle-end notes if 4-for-4 hits):
- "Per-atom importance hit empirical ceiling (4-for-4 MIDDLE_BAND across PageRank-centrality + retrieval-trace families). Backup mechanisms M-CFU/M-SURP queued and ready. If 6-for-6 hits, substrate-product story pivots to cluster-level importance (Cell 2 ultrametric, chain-grade-eligible). The pivot is fully retreat-able; no architectural change required."

---

## Pre-flight discipline (mandatory before cell-author spawn for any backup)

1. **predispatch_check.py** for the cell name (catches duplicates / recent HARD_FAILs)
2. **cor(importance, |W|)** smoke at N=1024, K=100 to validate fairness gate is achievable BEFORE smoke-VET
3. **Signal-independence audit** vs query-frequency + vs prior importance signals (avoid 7-signals-that-are-all-the-same trap)
4. **Spawn budget check** Fix #14 ceiling ≤3 in flight
5. **Pause flag check** `data/orchestrator_paused.flag`
6. **CARDINALITY_OK** pre-reg field (atoms-per-shell distribution for M-KSHELL; fraction-tagged for M-BTSP)
7. **No-silent-except** discipline in primitive code (META 2026-06-26 K-sweep phantom protection)
8. **Smoke-FIRES-discriminator** discipline (Fix-#22 / META 2026-06-26: smoke must demonstrate sel_unretr asymmetry, not merely that cell runs)

---

## Citations (verified)

External lit (12 verified):

1. Tonegawa lab optogenetic engram silencing — Liu et al. Nature 2012 (DG engram); Ramirez et al. Science 2013 (false memory engram); Tonegawa et al. Cell Reports 2015 review
2. Josselyn & Tonegawa Science 2020 "Memory engrams: Recalling the past and imagining the future" — engram-completion review
3. Schultz et al. Science 1997 "A neural substrate of prediction and reward" (dopamine RPE foundational)
4. Schultz Nat Rev Neuro 2016 "Dopamine reward prediction-error signalling: a two-component response"
5. Düzel et al. Trends Cogn Sci 2010 "Novelty-related motivation of anticipation and exploration by dopamine"
6. Lisman & Grace Neuron 2005 "The hippocampal-VTA loop"
7. Friston Nat Rev Neurosci 2010 "The free-energy principle: a unified brain theory?"
8. Olshausen & Field Nature 1996 "Emergence of simple-cell receptive field properties by learning a sparse code"
9. Bittner et al. Science 2017 "Behavioral time scale synaptic plasticity underlies CA1 place fields"
10. Magee & Grienberger Annu Rev Neurosci 2020 "Synaptic plasticity forms and functions"
11. Kitsak et al. Nat Physics 2010 "Identification of influential spreaders in complex networks" (k-shell vs centrality)
12. Marr J Physiol 1969 "A theory of cerebellar cortex"; Albus Math Biosci 1971 "A theory of cerebellar function"

Internal substrate notes (8 referenced):

13. `notes/research_drill_engineered_importance_3x_2026-06-11.md` (10-mechanism importance subspace drill)
14. `notes/research_gap_E_selective_forgetting_importance_compression_2026-06-26.md` (multi-factor cortex-composed framing; gap-E 3 candidates)
15. `notes/exp_dev_handoff_research_cortex_wave_1_6_E_tensor_fairness_fix_plus_4x_alternatives_2026-06-26.md` (E-tensor v2 fairness + 4 anchors)
16. `notes/exp_dev_to_orchestrator_dispatch_wave2_edge_importance_ultrametric_2026-06-26.md` (v1 edge-importance + ultrametric SMOKE-MIDDLE)
17. `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md` (mPFC analog; W_pred dual-purpose)
18. `notes/research_n5_revival_slow_learning_cortex_context_2026-06-26.md` (W_pred Hebbian — M-SURP S_write dependency)
19. `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` (W_schema BCM — schema-emergence dependency)
20. `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md` (eval framing constraint)

**Total verified: 20.**

---

## Filed-by

research (Opus 4.7 1M), 2026-06-27
Drill type: backup-mechanism design drill (anti-saturation; categorical-distinctness gated)
Calibration: lit-scan deflation 0.15-0.25; novel-synthesis P cap 0.50; fairness gate META_RULE_F; smoke-fires-discriminator META 2026-06-26
Dispatch contingency: v4 NREM-replay-modulated trace result → if MIDDLE_BAND/FAIL → activate M-CFU as rank 1 immediately
