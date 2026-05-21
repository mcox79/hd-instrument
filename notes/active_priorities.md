# Active priorities

Owner: Strategy session. Updated atomically; downstream sessions (Experiment
Dev, Research, Visibility, Queue Health, META) read this.

**Last updated:** 2026-05-21 — cold-start cycle 1
**Cap map version this refers to:** v12 (pending — see Strategy cycle 1 below)

---

## Top capability bets (in priority order)

### Bet 1 — ICL saturation curve (close Tier-S #1 gap)

**Claim.** Substrate ICL scales log-linearly with the number of *relevant*
in-context examples N at fixed pool composition, mirroring kNN-LM behavior,
through at least N=16384 at N=4096 substrate width.

**Why now.** ICL is at ✅ for the regime tested (N≤2048 ALPHA=0.3; N≤256
ALPHA=1.0) but [[cap_map_v7]] caveat notes "scales with relevant-example
count, NOT total pool size; gain inverts as pool fills with irrelevant items."
The saturation envelope is currently 🟡 because the close-test
(`wave14g_icl_saturation_extended`) failed on the augment_pool bug. Closing
this either confirms the kNN-LM story or bounds the substrate-specific
saturation point.

**Multi-probe success criteria** (all required):
- bpc gain at N ∈ {64, 256, 1024, 4096, 16384}, ALPHA=1.0, 3 seeds each
- slope on log2(N) > +0.10 across the tested range (vs the
  `wave14f_icl_scaling_pool` pool-sweep slope of −0.067)
- positive gain at N=16384 (no collapse to noise)
- corpus large enough that the relevant-example pool isn't exhausted
  (failure mode flagged in wave14f_icl_scaling_pool implication)

**Kill criterion.** Slope on log2(N) ≤ 0 across N ≥ 1024, OR gain at N=16384
≤ gain at N=4096 by more than 1σ. Either retracts the "kNN-LM-like ICL
scaling" framing and drops ICL to "small-N capability only."

**Who acts.** Experiment Dev (build `wave14d_icl_via_pool_v3_scaling` with
augment_pool fix); Visibility (surface verdict when it lands).

---

### Bet 2 — GDPR/surgical erase v3 (Tier-1 KILLER, currently ❌)

**Claim (target).** A new erase primitive (architecture TBD; anti-Hebbian
rank-1 alone is closed) reduces leak rate to <10% under multi-probe
verification on correlated keys.

**Why now.** Two independent negatives this week: pool-only erase leaks 93%
of facts via W ([[wave14d_query_side_integration]]); pool erase + replay
fails ([[wave14g_erase_under_replay]]). Anti-Hebbian rank-1 W edit and
selective thermal anneal both pass argmax but fail Mirage probes
([[wave14p_erase_multiprobe]]). Selective forgetting under correlated keys
is harder than the v8 recipe suggested — needs a new mechanism, not a
parameter tune.

**Multi-probe success criteria** (per arXiv:2503.06991 "Mirage of Model
Editing" — all four required):
- argmax leak rate < 10% (necessary, not sufficient)
- rank metric: erased item's rank in cleanup output > 100 (or absent)
- norm_ratio: ||W·k_erased|| / ||W·k_kept|| < 0.15
- cos: cos(predicted_v, target_v_erased) < 0.10 under correlated-key probes
- paraphrase_leak: < 5% under structurally-similar key perturbations
- side effects: ≤ 5% degradation on 100 random kept entries

**Kill criterion.** No candidate (Kerdock-structured codebook + W edit,
iterative charge-flipping, full ROME-style optimization, alternative) passes
all four probes within 4 cycles. Then GDPR-erase moves from "❌ until W-side
edit added" to "❌ structural — requires architecture change beyond rank-1
edits."

**Who acts.** Research (drill the mechanism space — Kerdock vs ROME-style vs
iterative charge-flipping); Experiment Dev (build with multi-probe from
inception); Strategy (close the row at ❌-structural if 4 cycles fail).

---

### Bet 3 — Substrate forensics extended (NEW ✅, upgrade vs v10 "LIMITED")

**Claim.** With structured (Hadamard) keys, the substrate is fully auditable
via WHT diffraction — 100% recall of stored key indices up to K/N≈0.98
without any queries. For random keys, iterative charge-flipping closes the
high-K SVD gap (currently cos=0.09 at high K, target ≥0.3).

**Why now.** [[wave14walsh_peaks_extended]] landed: recall 100% at every
tested K up through K=4000 (N=4096). The v10 "PEAKS_FORENSICS_LIMITED at
low K" framing is conservative — the extended sweep shows the capability
holds across the entire usable K range for structured keys. Pairs cleanly
with the WHT-structured-keys row already at ✅. Iterative charge-flipping
remains 🔬.

**Multi-probe success criteria**:
- WHT-peak (structured): per-K recall, position-accuracy, no false peaks
  → all confirmed by extended sweep
- Charge-flipping (random): cos(recovered_v, true_v) at K ∈ {50, 200, 500,
  1000, 2000}; key-index recall@10; iteration-count to convergence
- Hybrid: does charge-flipping initialized from SVD partial-recovery beat
  either alone?

**Kill criterion.** Iterative charge-flipping fails to beat single-pass
SVD by ≥0.2 cos at high K (≥1000) over 3 seeds. Then random-key forensics
stays 🔬 and the product story is "auditable IFF structured keys."

**Who acts.** Experiment Dev (charge-flipping iterator); Research (audit
Oszlanyi-Suto 2004 vs newer Sayre-eq variants); Strategy (cap_map upgrade
for Walsh-extended once event_outcome lands).

---

## Recently retracted (do NOT re-propose without architectural redesign)

| Claim | Retracted by | Lesson |
|---|---|---|
| Yonelinas dual-process dissociation | `wave14yonelinas_roc_v2` full mode: z-ROC slope=1.11 → pure familiarity. Earlier "dissociation" was asymmetric-codebook artifact. | Equal codebooks + z-ROC slope is the proper DPSD probe |
| Soft-trace calibration gain | `wave14calibration_v2`: Brier_soft=0.294 > Brier_clipped=0.212 under proper test | Use softmax(N·cos/σ²) + Brier + adaptive-ECE; not cos-only |
| Counterfactual=1.00 as Pearl L3 | Bundle arithmetic identity (b−x vs b' where b'=b−x): trivially 1.0 | Need downstream-retrieval test, not bundle-cos |
| Anti-Hebbian rank-1 W edit as GDPR-grade | `wave14p_erase_multiprobe`: passes argmax (76.7pp leak reduction) but rank/norm/cos/paraphrase all fail | All erase claims require Mirage 4-probe battery from prereg |
| Selective thermal annealing as GDPR-grade | `wave14anneal_selective`: same Mirage failure mode | Same — argmax-only is not evidence |
| RSB tree-walk practical algorithm at P=1024 | `wave14f_rsb_tree_walk`: recall 0.77 but 28× slower than brute force | Revisit only if pool grows past ~50K |
| SimHash / BinaryIVF LSH at our sim regime | `wave14e_lsh_for_bsc` / `wave14e_lsh_v2_binaryivf`: recall 2% / 18.6% | Brute force is the only retrieval at our pool scale |
| R3-Laplace concept bias as substrate-unique | `r3_disjoint_K64`: delta −0.0003 at K=64 (vs +0.025 at K=4) | K=4 product appendix only; not substrate-unique |
| K/N invariance (B=2 cliff at K/N=0.56 across N) | `wave14g_decompose_K_cliff_N8192`: cliff at K/N=0.50 at N=8192 | Production sizing needs N-dependent correction |

## Open research questions (routed to Research session)

- **R1**: Which mechanism family is the right GDPR-erase candidate after
  anti-Hebbian and selective anneal both Mirage-failed? Drill: Kerdock-coset
  structured-codebook + W edit; iterative charge-flipping erase; full
  ROME-style optimization; per-fact orthogonal-subspace allocation. Output:
  short comparison note with multi-probe-survivability argument for each.
- **R2**: Self-supervised concept discovery without PPMI — math survey
  beyond sparse_dictionary (which has Python-loop infra block).
- **R3**: Compositional generalization test design — no clean held-out
  compositional eval has been proposed yet.
- **R4**: 50+ multi-hop reasoning evaluation protocol — `wave14e_multi_hop_v2`
  reported acc_1hop=0.98 but never tested >1 hop. Need hop-depth sweep
  design + cleanup-budget tradeoff math.

## Open experiment requests (routed to Experiment Dev)

- **E1 (Bet 1)**: `wave14d_icl_via_pool_v3_scaling` with augment_pool fix.
  Multi-probe per Bet 1.
- **E2 (Bet 2, gated on R1)**: GDPR-erase v3 candidate (mechanism TBD by
  Research). Multi-probe from prereg per Bet 2.
- **E3 (Bet 3)**: Iterative charge-flipping forensics on random keys.
  Multi-probe per Bet 3.
- **E4**: Multi-hop reasoning v3 with hop-depth sweep {1, 5, 10, 25, 50}
  and per-hop cleanup. Tier-2 KILLER probe.
- **E5 (infra, not capability)**: Vectorize `learn_sparse_dictionary`
  (Python-loop bottleneck blocks R2 self-supervised concept test).

## Items deliberately NOT on the priority list

- **Edit-then-query end-to-end pipeline** — blocked behind Bet 2 GDPR-erase.
  Re-add once erase primitive lands ✅.
- **RSB tree-walk algorithm** — closed at P=1024; revisit only at P≥50K.
- **R3 rescue variants, MIR-style replay, C3 factored, basis_modification,
  iterative Hopfield, pre-shift bpc gains** — all closed by prior evidence;
  do not re-propose.
- **Compound R3 × R10 × replay stacking** — closed by four-argument
  convergence (shared evidence base).
