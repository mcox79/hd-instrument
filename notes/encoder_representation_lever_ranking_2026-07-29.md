# Encoder representation-richness lever ranking — design deliverable (2026-07-29)

Scope: DESIGN ONLY, analysis for hdi_exp_dev to build from. No experiment cell, module,
or GPU touched. Opens the parallel ENCODER/REPRESENTATION workstream alongside (not
gated by) the stateful-core WM workstream. Calibration per
[[feedback-lit-scan-calibration-penalty]]: P estimates deflated 0.15-0.25;
novel-synthesis capped at P<=0.50; CITED@ vs REASONED@ tagged per claim.

Builds on, and does not re-derive: `notes/brain_foundational_component_analysis.md`
(components 1+2 — objective + architecture), `notes/forward_predictive_objective_from_wm_state_design_2026-07-29.md`
(the already-designed WM-COUPLED forward-predictive head), `notes/component_brain_fidelity_ledger.md`
row 3 (29591 representation-geometry metrics, modest band 0.56-0.63), and the banked
primitives `hdlab/concept_encoder.py` (competitive-Hebbian top-K WTA, tested,
banked-but-unwired-into-the-main-encoder) and `hdlab/temporal_trace.py` (Foldiak
exponential trace, tested, banked-but-unwired).

---

## 1. Ranked levers

| Rank | Lever | Biology | Within invariant? | Expected richness gain | Scale-floor risk | Build cost |
|---|---|---|---|---|---|---|
| **1** | **Encoder-level latent predictive coding (JEPA-style, no WM)** | CITED@Rao&Ballard1999, CITED@Friston2005 (generative top-down prediction); CITED@LeCun2022, CITED@Assran2023 (I-JEPA), CITED@Bardes2024 (V-JEPA2) | YES — operates in d-dim latent space, categorically avoids the v5 full-vocab-logits OOM (no `[B,L,vocab]` tensor anywhere) | HIGH (REASONED@, P~0.40 deflated) — directly fixes the founding-diagnosis objective gap (component 1: every prior objective aligned to a STATIC target; this predicts the STREAM) | MODERATE — collapse risk is capacity-ratio-dependent (model size vs data size), not simply "small data fails" (SCAN 1); genuinely untested at our exact regime (~100-300M tokens) — flagged gap, not resolved | LOW-MODERATE — reuses the EMA-teacher/stop-grad/predictor pattern already scoped in the WM-coupled design; the encoder-level (no-WM) version is a strict subset of that design's machinery |
| **2** | **Hierarchical multi-timescale encoding (Hasson; Chung et al. multiscale RNN)** | CITED@Hasson (temporal-receptive-window hierarchy — word→clause→event; verify exact year, 2008 J.Neurosci vs 2015 TiCS, both describe the same hierarchy, treat as one anchor pending single-source pin); CITED@Chung2017 (Hierarchical Multiscale RNN, ICLR) | YES — architectural, adds layer-specialized timescales on top of existing layers; no borrowed vectors, no external LLM | MODERATE-HIGH (REASONED@, P~0.35 deflated) — Chung et al. is a real quantified anchor (WSJ char-PPL 93.3→73.6, 60% fewer updates to converge) for layer-specialized timescales yielding richer/more efficient reps, though that result is char-LM perplexity, not relational-geometry richness — transfer to our metric is REASONED not CITED | LOW — timescale hierarchy is architectural, largely data-size-agnostic in the cited result (efficiency gain shows at moderate scale) | MODERATE — touches the shared encoder's layer structure (every downstream consumer of `clause_rep`), more invasive than #1 |
| **3** | **Temporal-contiguity / slow-feature auxiliary objective (Foldiak, Wiskott-Sejnowski)** | CITED@Foldiak1991, CITED@Wiskott&Sejnowski2002 | YES — `hdlab/temporal_trace.py` is ALREADY BUILT, tested, banked; wiring cost is "add an existing module," not "design from zero" | LOW-MODERATE (REASONED@, P~0.30 deflated) — SCAN 2 found NO direct slowness-vs-MLM ablation in the literature (genuine gap); the objective is consistently used as an AUXILIARY regularizer alongside a primary objective, never validated as a standalone driver of richness. Motivation (invariance to fast nuisance) is orthogonal-but-modest relative to #1's direct fix of the founding objective gap | LOW — an auxiliary regularizer, not the primary richness lever; unlikely to hit a scale floor because it's cheap/orthogonal, but also unlikely to be the dominant gain | LOW — primitive exists, needs wiring as an auxiliary loss term only |
| **4** | **More/better data within from-scratch (curriculum, quality filtering, BabyLM-style tricks)** | Not a brain mechanism per se — but CITED@BabyLM-challenge literature (10-100M word regime, our exact regime) is the single best-matched empirical anchor found this cycle | YES, if "better" means curriculum/curation/multi-epoch scheduling on the EXISTING 158M-token corpus (not new external data ingestion, which would need separate sourcing authorization) | LOW-MODERATE, BOUNDED (CITED@, moderate confidence) — BabyLM findings: clever curricula/distillation/architecture choices give REAL but BOUNDED gains at this scale; they help at the margin, they do NOT close the gap to large-corpus models. This is the most load-bearing honest finding of the whole scan (see section 3) | **HIGH — this is where the floor risk concentrates.** Data quantity/quality tricks are a real but capped lever; no combination of them known to reach large-corpus richness | LOW-MODERATE — mostly data-pipeline engineering (dedup, curriculum ordering, difficulty scheduling), not new architecture |
| 5 (deprioritized as a RICHNESS lever) | **k-WTA sparsity wired into the main encoding architecture** | CITED@Olshausen&Field (sparse coding), primitive exists (`hdlab/concept_encoder.py`, banked/tested) | YES | LOW (CITED@, SCAN 3) — sparse coding's literature-documented gain is COMPACTNESS/INTERPRETABILITY, not learning sample-efficiency; a "statistical inefficiency of sparse coding" line of literature argues overcomplete sparse dictionaries need MORE data, not less, to learn well. No study found combining k-WTA with a predictive/contrastive SSL objective (genuine gap) — this is a real unknown, not a proven negative, but the prior-literature default expectation is NOT a richness win | LOW-MODERATE — plausibly still useful for something (capacity control, interference reduction) but not evidenced as a richness lever | LOW — primitive exists | 
| 6 (WM-coupled, already designed, sequenced AFTER #1) | Forward-predictive coupling INTO the working-memory gate | see `notes/forward_predictive_objective_from_wm_state_design_2026-07-29.md` | YES | N/A — this is a WM-workstream lever, not an encoder-workstream lever; listed here only to mark the boundary | N/A | Already fully speced; sequenced after the audit-C WM re-smoke, per that note's section 7 |

**Distinguishing #1 (this note) from the already-designed WM-coupled forward-predictive
objective:** the WM-coupled design (`forward_predictive_objective_from_wm_state_design_2026-07-29.md`)
predicts the next CLAUSE's latent from the maintained SLOT STATE — it is a
situation-model-level anticipation mechanism, explicitly gated into the WM's PE-gate, and
its pass/fail criterion is a WM-gate metric (MES/KD deltas). Lever #1 here is the
STANDALONE ENCODER-LEVEL version: predict a masked/withheld SPAN's latent from
CONTEXT alone, with NO slot state, NO working-memory module, trained as a pretraining
objective on the encoder in isolation — closer to I-JEPA/V-JEPA's actual setup (context
latent → predictor → target latent, EMA teacher + stop-grad). **These are not
redundant: #1 is a pretraining-stage representation lever; the WM design is a
maintenance-stage situation-model lever that CONSUMES whatever representation #1
produces.** Per the CRITICAL sequencing question below: #1 should ship as a standalone
representation improvement FIRST, independent of and in parallel to the WM gate,
because it is testable on its own axis (section 4) without needing the WM machinery
to exist or be debugged first — this is exactly the "never confound the two
workstreams" requirement.

---

## 2. Honest scale-vs-glass-box verdict (load-bearing, not hand-waved)

**There is no PROVEN hard floor in the literature, and no PROVEN escape from a floor
either — "absence of evidence, not evidence of absence" is the accurate read (SCAN 3).**
Specifically:

- CITED@ Kaplan/Chinchilla-style scaling laws confirm a qualitative low-data regime
  change (early overfitting, diminishing marginal return per token) that LOOKS
  floor-like, but those studies characterize held-out LOSS, not representational
  RICHNESS (graded geometry, relational-neighborhood structure) — the transfer from
  "loss plateaus" to "richness plateaus" is REASONED@, not CITED@, and is a real gap in
  the literature, not just in our own search.
- The single best-matched empirical anchor is CITED@BabyLM-challenge work (10-100M word
  training regime — closely matching our ~158M-token corpus): clever curricula,
  distillation choices, and architecture tweaks produce REAL, MEASURABLE, but BOUNDED
  gains. They consistently narrow but do not CLOSE the gap to large-corpus models on
  the same benchmarks.
- SCAN 1 (JEPA): collapse risk and representation quality are reported as
  CAPACITY-RATIO dependent (model size relative to dataset size), not a simple "small
  data → fails" relationship; SimSiam specifically is reported as "extraordinarily
  sensitive to dataset/model size ratio" in the literature, which cuts against a clean
  floor-at-N-tokens framing and toward a floor-at-(capacity/data)-ratio framing —
  actionable (keep the encoder small relative to the corpus) but still REASONED@ as a
  transfer to our exact setup.

**Honest verdict: a SOFT floor is likely.** The encoder-level levers ranked above
(latent-PC, multi-timescale, temporal-contiguity, data curriculum) plausibly deliver
REAL, MEASURABLE representation-richness gains over the current MLM baseline — none of
them are ruled out, and #1 in particular directly repairs a diagnosed mechanism gap
(objective aligned to stream vs static target) rather than chasing an unproven scaling
trick. But per the BabyLM anchor, the CEILING on what these levers can buy at
~158M tokens is BOUNDED — they are unlikely to lift our from-scratch encoder to
large-corpus-model richness. This is a genuine architecture/objective-vs-data-scale
tension, not a solved problem, and should be reported as such rather than either
(a) claiming the floor is fatal (defeatist, against the brain-is-existence-proof
standing discipline — the brain achieves rich representations on comparably modest
"data" in developmental terms, so richness in principle is achievable; the constraint
is OUR corpus + OUR compute, not a law of nature) or (b) claiming these levers will
close the gap to internet-scale-model richness (overclaiming against BabyLM's own
finding that its best tricks still don't close that gap).

**Strategic implication (this is the single most decision-relevant finding of the
cycle):** the soft-floor finding VALIDATES the existing "prove the text-only slice
first, then EXPAND GROUNDING" sequencing over an "encoder-alone can get us to full
richness" bet. Encoder-level levers (this note) EXTRACT MORE representational
structure from the information already present in the 158M-token text stream — they
raise the ceiling on how much of that information is captured, but they cannot inject
information the text stream never contained. GROUNDING EXPANSION (KB/relational
supply, per the standing PIVOT anchor) is the lever that ADDS information beyond what
text alone carries. The two are complementary, not substitutes: ship encoder levers
now (cheap, no data-sourcing dependency, directly fixes a diagnosed mechanism gap) in
PARALLEL with continued grounding-expansion work, and do not expect either one alone
to fully close the richness gap.

---

## 3. Independent representation-quality measurement plan (separate from the WM gate)

**Principle:** the encoder workstream must be judged on the ENCODER'S OWN geometric
properties, computed on a FROZEN snapshot of the encoder, with NO working-memory
module, NO slot state, and NO situation-model judge in the loop — this is what keeps
the two workstreams from confounding each other. The WM gate (MES/KD, per the
stateful-core design) measures whether MAINTAINED state improves comprehension
behavior; this measurement measures whether the ENCODER'S per-item representation is
richer, full stop.

**Metrics (reuse the 29591-style battery, `component_brain_fidelity_ledger.md` row 3,
rather than inventing a new one):**

1. **Graded neighborhood geometry.** For a fixed probe set of concept/relation pairs
   with known graded similarity structure (near/mid/far, drawn from the existing
   relational-KB used for grounding, but used HERE only as a READ-OUT probe, never as
   a training target — this is the exact distinction that separates this measurement
   from relObj's failed contrastive-alignment-to-KB training objective), measure
   cosine-neighborhood rank-correlation (Spearman) between the encoder's embedding
   distances and the KB's graded relational distance. This is diagnostic-only use of
   the KB (read, not trained-toward) — consistent with "KB as SEED/teacher for
   encoding learned downstream," per component 12 of the foundational analysis, not a
   re-run of the relObj failure mode.
2. **Held-out-NEW generalization** (reuse 29591's existing protocol): does the encoder
   place novel/unseen concept instances in geometrically sensible neighborhoods
   relative to trained concepts, without having seen them during training.
3. **Linear-probe transfer** on 1-2 held-out relational tasks NOT used in training
   (per BabyLM/SCAN-3 convention) — probe accuracy as a function of encoder variant,
   with a frozen linear head (so gains are attributable to representation quality, not
   probe capacity — mirrors the readout-can't-cheat lesson from component 4 of the
   foundational analysis).
4. **Intra-concept coefficient of variation** (already an established metric in
   `hdlab/concept_encoder.py`'s selftest suite) as a cheap sanity check that variance
   hasn't collapsed.

**Can-fail baselines (mandatory, per design-gate discipline):**
- **Random-init encoder** (same architecture, untrained weights) — the floor; any
  candidate encoder MUST clear this by a pre-registered margin or the "improvement" is
  not real.
- **Known-good reference** = the CURRENT MLM-bidirectional-stateless encoder (29591
  baseline, 0.56-0.63 band) — the improvement target; candidate levers are judged by
  delta over THIS reference, not over random-init alone (random-init only rules out
  vacuous/degenerate results).
- **NAIVE_WTA_SAMPLING-style falsified control**, reused where applicable, if the k-WTA
  lever is tested at all (per section 1 rank 5, this is deprioritized, but if tested,
  it must clear its own already-established control, per `concept_encoder.py`
  selftest 9).

**Pre-registered thresholds (deflated per calibration discipline):**
- HARD-PASS candidate encoder objective/architecture: Spearman graded-geometry
  correlation improves by >=+0.10 over the 29591 baseline AND clears random-init by
  >=+0.15, AND held-out-NEW generalization does not regress, in >=1 of 2 seeds with the
  other non-negative.
- HARD-FAIL: candidate ties baseline AND random-init within +/-0.03 on the composite
  (same no-effect signature pattern used elsewhere in this program) — report as
  FAIL-BY-NO-EFFECT, or if geometry metrics improve while intra-concept CV/variance
  collapses, report as FAIL-BY-COLLAPSE (distinct diagnosis, do not conclude the
  mechanism class is wrong, cf. the WM-coupled design's own collapse-vs-no-effect
  distinction).

---

## 4. Answers to the three end-of-cycle questions

**(a) Single highest-leverage next encoder build:** encoder-level latent predictive
coding (lever #1) — a JEPA-style masked-span latent predictor (context latents →
predictor MLP → predicted target-span latent, EMA-teacher stop-grad target, VICReg
variance guard as the primary collapse defense given the small-scale-sensitivity
finding on SimSiam-style pure stop-grad from SCAN 1) trained as a STANDALONE
pretraining objective on the encoder, with NO working-memory module involved. It
directly repairs the founding-diagnosis objective gap (predicts the stream, not a
static target), is categorically OOM-free (no vocab-sized tensor), and is measurable
on its own axis (section 3) without depending on the WM gate's build/debug status.

**(b) Honest scale-vs-glass-box verdict:** a SOFT floor, not a hard wall and not a
non-issue. No literature proves richness is capped at our exact ~158M-token scale, but
the best-matched empirical anchor (BabyLM, same order-of-magnitude regime) shows
clever objective/architecture/curriculum tricks give real-but-BOUNDED gains that
narrow, not close, the gap to large-corpus richness. Implication: build the encoder
levers (they are real, brain-faithful, and evidenced), but do not bet the program on
them alone reaching full richness — the complementary lever is grounding-expansion
(adds information text alone lacks), which should proceed in parallel, not be
deprioritized in favor of "just fix the encoder."

**(c) Sequencing vs the WM gate:** PARALLEL, with separate measurement, by design.
Lever #1 (encoder-level latent-PC) is tested on the section-3 geometry/probe battery,
on a frozen encoder snapshot, with NO WM module in the loop — it can be built, smoked,
and verdict-read entirely independently of the stateful-core WM build's status. The
WM-coupled forward-predictive design (already speced, sequenced after the audit-C
WM re-smoke per its own note) consumes whichever encoder is current at build time; it
does not need to wait for lever #1's verdict, and lever #1 does not need to wait for
the WM gate. If both later ship, the WM-coupled design's ablation should be re-run
against whichever encoder scored better on the section-3 battery, but that is a
future sequencing decision, not a current blocker either way.

---

## Citations (CITED@ = literature-verified this cycle via 3 parallel Sonnet lit-scan
sub-agents, generic-term search per query-privacy discipline; REASONED@ = this
session's own inference/transfer, not independently verified off-platform)

- Rao & Ballard (1999); Friston (2005) — hierarchical predictive coding — CITED@,
  carried from `brain_foundational_component_analysis.md`.
- LeCun (2022 position paper); Assran et al. (2023, I-JEPA/V-JEPA) — CITED@, carried +
  reconfirmed SCAN 1 this cycle.
- Bardes et al. (2024, V-JEPA2) — CITED@, NEW this cycle (SCAN 1).
- SimSiam sensitivity to dataset/model-size ratio — CITED@, NEW this cycle (SCAN 1),
  P_deflated ~0.30 on direct transfer to our regime (genuine ablation gap: no isolated
  JEPA-vs-MLM text comparison at 100-300M tokens found).
- Foldiak (1991); Wiskott & Sejnowski (2002, Slow Feature Analysis) — CITED@, carried +
  reconfirmed SCAN 2.
- Hasson et al. (temporal-receptive-window hierarchy; exact year unverified between
  2008 J.Neurosci and 2015 TiCS restatement — flag as a citation-pinning TODO, not a
  substantive gap) — CITED@ with a minor pin-down caveat, SCAN 2.
- Chung et al. (2017, ICLR, Hierarchical Multiscale RNN) — CITED@, NEW this cycle
  (SCAN 2), quantified anchor (WSJ char-PPL 93.3→73.6, 60% fewer updates).
- Olshausen & Field (sparse coding) — CITED@, carried, reconfirmed SCAN 3; "statistical
  inefficiency of sparse coding" finding — CITED@, NEW this cycle (SCAN 3).
- Kaplan et al. / Hoffmann et al. (Chinchilla) scaling laws — CITED@ for the loss-curve
  claim; REASONED@ (deflated, this is the load-bearing REASONED transfer of the whole
  note) for the loss-plateau-implies-richness-plateau inference.
- BabyLM Challenge literature (10-100M word regime) — CITED@, NEW this cycle (SCAN 3),
  the single best-matched empirical anchor for our exact data regime.

Verified citation count this cycle: 10 anchors (6 carried/reconfirmed CITED@, 4 new
CITED@ this cycle) + 1 explicitly flagged REASONED@ load-bearing inference (loss-floor
→ richness-floor transfer) + 1 minor citation-year pin-down TODO (Hasson). Lit-scan
calibration penalty applied throughout: all REASONED@ probability estimates deflated
0.15-0.25 from face value; novel-synthesis claims (the strategic-implication paragraph
in section 2, the lever-1-vs-WM-design distinction) capped at P<=0.50.
