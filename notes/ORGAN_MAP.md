# ORGAN MAP — every brain organ, its equation, ours, and whether ours is the same one

**LIVING DOC. Dateless filename, updated IN PLACE.** Last updated 2026-08-14. Branch
`dataprep/mcguffey-graded-corpus`. Read-only audit: no `hdlab/` or `experiments/` file was modified,
no experiment was run, no `metrics.json` was touched.

**SUPERSEDES `notes/component_brain_fidelity_ledger.md`** — see §7 for what that doc got right and
where it is now wrong. Do not maintain both.

---

## 0. WHY THIS DOC EXISTS, IN PLAIN LANGUAGE

The USER's framing. This IS the plan; the map exists to serve it:

> "it is also very useful to consider substrate as brain components that do particular things. those
> things are often sub brain components, but always do particular things, and those particular things
> follow clear mathematical operations. recreating those gates and mathematical operations are key to
> recreating the holistic capabilities of the brain."
> "if we can create 'organs' that do the same things as brain organs, we can wire everything together
> to create a glass box 'brain' that should have similar capabilities to the brain"
> "then, once it's all working, we can start implementing capabilities on top of the brain -
> supercharging certain components or capabilities"

And the diagnosis that prompted it — *"i fear that we don't have an organized plan here - that you're
just shooting in the dark."* That was correct. There was no list of which organs exist, which are
faithful, which are switched on, or what equation each is supposed to compute. One component was
audited this way (the semantic comparator) and it produced the session's only real win, largely by
accident. This doc applies that method to the whole substrate.

**An organ = one brain component that does ONE thing, and that one thing has a definable equation.**
Not "integrates information" — *divisive normalisation over a pool? recurrent settling to a fixed
point? multiplicative gain? sparse k-WTA? Hebbian outer product? a successor-representation inverse?*

### THE TWO PHASES — DO NOT BLUR THEM

- **PHASE A — REACH BRAIN PARITY, ORGAN BY ORGAN.** Every step in §6 is Phase A. The gate is the
  BRAIN'S metric for that organ, not a downstream task win.
- **PHASE B — SUPERCHARGE BEYOND THE BRAIN.** NOT STARTED, deliberately. Two legitimate Phase-B
  targets are already visible and are named in §6 so they are not started by accident: representation
  **capacity** (cortex cannot re-dimension itself; we can) and the **coherence monitor** (humans miss
  40-50% of controlled semantic anomalies — an always-on check can structurally beat that, not merely
  match it). Neither enters Phase B until its Phase-A parity is measured against a floor. On today's
  map that is **5 organs of 38**.

### THE FIVE HONESTY RULES THIS DOC OBEYS

1. **UNPINNED is an answer.** Where the literature does not pin the equation, column 2 says UNPINNED.
   That is a finding about the state of neuroscience, not a hole to fill with plausible filler. An
   organ whose brain math is UNPINNED **cannot be scored for fidelity** and is marked UNSCORABLE.
2. **UNTESTED is not "working".** A self-test PASS is not evidence of capability. **A number with no
   floor is not evidence.** Column 7 names the floor or says NO FLOOR.
3. **A floor that cannot fail is not a floor.** Three of the biggest August results had floors that
   were present and non-failable. Presence of a `floor` field is not validity of a floor.
4. **WIRED is decided by RUNTIME, never by grep.** Lazy imports inside function bodies
   (`reading_grounding_loop.py:300-303`) are invisible to grep; a string constant
   (`hd_fact_store.py:70`) and a comment (`grounding_acquisition_loop.py:195`) read as imports.
5. **The capability registry does not frame this audit.** Enumeration is `os.walk` over `hdlab/`;
   the registry is reconciled afterwards. It is known wrong in both directions.

---

## 1. THE TALLY

| quantity | count | basis |
|---|---|---|
| **organs enumerated** | **38** | §4 |
| **fidelity SAME — our equation IS the brain's** | **5 / 38** | DG pattern separation, hippocampal one-shot write, sequence memory, basal-ganglia selection, familiarity/gap signal |
| RIGHT-OP-WRONG-METRIC | 13 / 38 | |
| RIGHT-OP-WRONG-PLACE | 3 / 38 | |
| WRONG-OP | 6 / 38 | |
| **MISSING entirely** | **7 / 38** | successor representation, cascade synapse, discourse bridging, coherence monitor, construction-integration, information foraging, settling (this last one declined on purpose) |
| UNSCORABLE (brain math UNPINNED) | 4 / 38 | |
| **an implementable equation exists in the literature** | **12 / 38** | listed in §2 |
| form pinned, key function/parameter UNPINNED | 12 / 38 | |
| **core operation UNPINNED** | **14 / 38** | |
| **on the LIVE path** | **~23 / 38 organs**, backed by **44 of 155 modules (= 35 of the 141 top-level)** | fresh runtime `sys.modules` trace this pass |
| **UNTESTED — no floored evidence at all** | **16 / 38** | column 7 |
| organs whose only evidence is a self-test PASS | 10 / 38 | column 7 |
| `.py` files in `hdlab/` by `os.walk` | **155** | 142 package root (141 modules + `__init__`) + 7 `learner/` + 5 `dashboard/` |
| modules that import cleanly | **155 / 155**, zero ImportErrors | fresh subprocess per module |
| **modules unreachable from ANY plausible entry point** | **83 / 155 (54%)** | union of 17 candidate drivers reaches only 72 |

**The single-sentence version:** *five of thirty-eight organs compute the equation the brain computes;
sixteen have never been tested against anything that could have failed; seven do not exist at all —
and one of those seven is the organ that decides what to read next, which is why the system cannot
notice what it does not know. Separately, 54% of the code is unreachable from any entry point.*

### The evidence base, measured

**7,625** `metrics.json` files exist under `data/` + `experiments/`. A prioritised set of **946**
cells was read. **HAS_FLOOR 594 / NO_FLOOR 359.** *(⚠️ arithmetic slip, flagged 2026-08-14 and left
uncorrected because the underlying scan has not been re-run: 594 + 359 = **953**, not 946. One of the
three numbers is off by 7. Do not quote the pair as exhaustive until the scan is redone.)*
Of the no-floor set, **134 carry a PASS-flavoured
verdict** — those are headline claims with nothing behind them. Caveat on the method: floor detection
is key-name based, so NO_FLOOR means *"no floor found by name — verify before citing"*, not proof of
absence (several real floors are named `OFF`, `fz`, `brute`, `naive_dual_w`). The reverse error does
not occur.

### The wiring, measured by runtime this pass (not grep, not the registry)

Fresh-process imports + `sys.modules` diff + an AST parent-walk for lazy imports:

- `import hdlab.reading_grounding_loop` → **40** `hdlab.*` entries.
  `import hdlab.grounding_acquisition_loop` → **37**, and it is a **strict subset** — B-only is
  empty. **The "two entry points" are one closure**; the reading loop imports the acquisition loop at
  import time and adds three modules (`closed_class_lexicon`, `gap_detector`, itself).
- **84 lazy hdlab→hdlab import edges exist**, but only **4 modules are genuinely added** by a lazy
  import from inside the live closure: `pos_tagger`, `arc_parser`, `arc_labeler`
  (`reading_grounding_loop.py:305-307`) and **`situation_model_multibank`**
  (`situation_model_accumulate.py:154`). Everything else lazy-from-closure was already eager.
- **LIVE-PATH-CANDIDATE = 44 of 155** (= exactly 35 of the 141 top-level modules), independently
  reproducing the figure in `CLAUDE.md`.
- Both grep false-positives confirmed as false: `definitional_extraction` and `foundation_persistence`
  are **absent from both closures at runtime**. `foundation_persistence` in fact depends on the loop,
  not the reverse.
- **The orphan list is not an artifact of picking two entry points.** Import closures were probed for
  **17** candidate drivers (`three_tier_loop` 42, `gap_driven_reader` 41, `prelim_tier` 39,
  `situation_reader` 36, `goal_achievement` 32, `reasoner` 13, …). **Their union reaches 72 of 155.
  83 modules — 54% of `hdlab/` — are unreachable from any plausible entry point at all**, including
  `definitional_extraction` (which produced the arc's headline facts), `hippocampal_encoder`,
  `modern_hopfield_readout`, `multi_hop`, `kg_traversal`, `metrics`, `learning`, `continual`,
  `predictive_coding`, `dg_pattern_separation`, `sequence_memory`, and all four `director_kb_*`.

### The cross-cutting arithmetic defect, quantified

Every composition step in this substrate ends in a magnitude-destroying quantiser. Measured this pass
across all 155 `hdlab/**/*.py`:

    np.sign / torch.sign call sites:  34, across 12 modules
      reading_grounding_loop 8 | hippocampal_encoder 7 | grounding_acquisition_loop 3
      cleanup_family 2 | concept_encoder 2 | context_retention 2 | ppmi_sparse_encoder 2
      char_positional_encoder 1 | char_trigram_encoder 1 | predictive_coding 1
      role_slot_summarizer 1 | vwfa 1
    per-component complex renormalisation `s / |s|`:  1 site, bundling.py:39

`sign(shared + distinctive) = sign(shared)` wherever `|shared| > |distinctive|`, which is almost
everywhere — mathematically a **prototype extractor**, the signature of a degrading ATL hub (Rogers,
Lambon Ralph, Garrard, Bozeat, McClelland, Hodges & Patterson 2004, *Psychol Rev* 111:205-235). The
earlier audit called this "five sites". **It is 34 sites in 12 modules.**

**And the SUM it is applied to is right.** Baron & Osherson 2011 (*NeuroImage*) find that LATL
conceptual combination — "young man" from its constituents — is **approximately ADDITIVE**. Vector
addition IS the brain's composition operation here. So `bundle()`'s `vectors.sum(0)` is faithful and
only the normaliser that follows it is not. That is a genuinely useful narrowing: **the defect is one
line, not the design.**

---

## 2. THE TWELVE ORGANS WHOSE EQUATION IS ACTUALLY PINNED

Listed so the claim in §1 is checkable, and because these are the only organs where "build the
brain's equation" is a well-posed instruction today.

| organ | the equation |
|---|---|
| B2 cortical pooling | `r_i = x_i^n / (σ^n + Σ_j x_j^n)`, `j` over NEURONS → **scalar denominator** |
| B4 code format | dense, graded, ~4-12 effective dims; IT sparseness index ~0.2-0.3 |
| D1 MTL sparse coding level | ~0.2% of MTL neurons per percept; ~50-150 concepts per neuron |
| D3 hippocampal fast write | one-shot Hebbian outer product on a sparse code |
| **D7 successor representation** | **`M(s,s') = E[Σ_k γ^k 1{s_k=s'}]`, i.e. `M = (I − γP)⁻¹`; grid cells = eigenvectors of M** |
| **D8 cascade synapse** | **TWO transition families, both `~2^-d` (plastic one RESETS depth to 1 in the opposite cascade) → power-law forgetting `t^-α`, α=1 (α=3/4 in Fusi 2005 as published); cascade capacity ~√N. `~N` is Benna-Fusi 2016, a DIFFERENT model: `SNR(t) ~ √N·e^(-t/T)/(√t·√(log T))`, `T = 2^(2m+1)`** |
| **D9 synaptic tag & capture** | **consolidate iff `tag × PRP > θ`; ~5 h co-allocation window** |
| E1' relational binding (TEM) | conjunctive code `p = g ⊗ x` (structural × sensory) |
| E5 theta-gamma buffer | ~7 gamma sub-cycles (~17 ms) per theta cycle (~125 ms), one item per slot |
| F3 thematic roles | Competition Model: cue **validity** (availability × reliability) vs cue **cost** |
| F6 construction-integration | `A(t+1) = normalize(A(t) · W)`, small fixed cycle count *(flagged in source as recalled, not freshly re-verified)* |
| G2 predictive coding | residual `x − x̂` is the learning signal; precision-weighted |
| G4 basal ganglia | WTA disinhibition over Go/NoGo; TD bootstrap |
| B1' hub composition | LATL conceptual combination ≈ **additive** (Baron & Osherson 2011) |

*(14 rows for 12 organs — B1'/E1' are pinned sub-facts of otherwise-UNPINNED organs.)*

---

## 3. THE THREE CORRECTIONS THIS METHOD FORCED ON ITS OWN AUTHOR

Carried forward verbatim because the corrections are the evidence the method works.

**1. Carandini & Heeger was TRANSPOSED.** The pool index `j` ranges over other NEURONS in the same
population at the same moment, **so the denominator is a SCALAR for the whole representation. Cosine
is invariant to a scalar, so canonical divisive normalisation cannot change a two-candidate argmax at
all — "not weakly, identically not at all."** What was implemented and measured NULL (+0.0018,
CI [−0.0030,+0.0065]) was efficient-coding ADAPTATION (Laughlin 1981; Fairhall 2001), a different
real mechanism. **Do not re-propose "apply divisive normalisation to fix the argmax."** Caught by the
next cell's own self-test and filed as a dated prereg AMENDMENT that re-designated the primary arm
*before any arm was scored*, with the superseded prediction retained and still scored — it landed
below baseline, as the amendment predicted.

**2. The log-IDF distinctiveness mechanism was REFUTED by recompute**, in both of its mechanistic
claims: near-cancellation is **4.3× RARER** under weighting (0.68% vs 2.94%), and the per-component
step **TRANSMITS more** of the perturbation than whole-vector L2 (cos 0.9448 vs 0.9897) — both the
opposite of the prediction. Weighting hurts under BOTH normalisers (d′ −0.682 / −0.771), so the
normaliser cannot be what killed it. Real cause: mean k=2.91 features per concept and a weight range
spanning only 2.34× — log-IDF does not carry enough signal to restructure the cosine. **Refuting the
renormalisation does not revive the route.**

**3. A HARD_PASS survived every artifact control and still lost its mechanism claim.** An adversarial
review reproduced the landed run **bit-exactly** (all 19 arms at n=600, zero mismatches; A_SSN 0.6395,
A_GGZ 0.69975, d 0.06025 at full scale), killed five artifact hypotheses (leakage, ties, sentence
length, pool statistics, floor validity) — and then showed:
- the **unmodified `sign()` comparator at d=1024 scores 0.7030, BEATING the graded one at d=256
  (0.69975)**, and the graded advantage shrinks 0.0602 → 0.047 → 0.041 as d goes 256 → 1024 → 4096;
- destroying ALL magnitude in the unprojected term space costs only 0.0165 = **27%** of the effect,
  and query-side magnitude is worth exactly 0.000;
- ~30% of the smoke delta was an uncontrolled ternary/bipolar zero-convention mismatch —
  *"documenting a confound is not controlling for it"*;
- projection-draw sd 0.015 is invisible to the item bootstrap.

**LICENSED: the 0.6395 → 0.6997 number. NOT LICENSED: that per-component magnitude destruction is THE
binding constraint.** The capability stands and is wired; the explanation was withdrawn in all four
places it had been written down. Correct reading: **at d=256 the quantised comparator is
CAPACITY-limited.**

---

## 4. THE ORGAN MAP

Columns: ORGAN · BRAIN'S MATH (cited, or UNPINNED) · OUR MODULE · OUR OP (read from code at HEAD) ·
FIDELITY · WIRED (runtime) · EVIDENCE (+ its floor) · BLOCKS.

### A. INPUT / WORD FORM

**A1 — VWFA: orthography → an invariant lexical code**
- **BRAIN'S MATH:** hierarchical position-tolerant feature detectors; open-bigram coding (Dehaene et
  al. 2005; Grainger & Whitney). **The update rule is UNPINNED.**
- **OURS:** `hdlab/vwfa.py:208-209` weighted multi-scale n-gram, per (n-gram, scale) hashed bipolar
  HV optionally HRR-bound to position, `acc += weight·Σ_scale`, then `sign()`.
  `hdlab/char_positional_encoder.py:65-79` `sign(Σ_i HRR_bind(char_hd[c_i], pos_hd[i]))` — position
  is a hashed atom, **not a rotation**. `hdlab/char_trigram_encoder.py:92-94` bag of trigrams, order
  destroyed.
- **FIDELITY:** RIGHT-OP-WRONG-METRIC — n-gram coding is the right family; the 1-bit terminal
  quantiser is not.
- **WIRED:** NO
- **EVIDENCE:** registry `hdlab_encoder_cluster_vwfa_ppmi_composed_v3` = SHELVE,
  `superseded_untouched_since_2026-07-03`. **UNTESTED — no floored number.**
- **BLOCKS:** nothing today. The live path never reads characters.

### B. SEMANTIC REPRESENTATION (the hub)

**B1 — ATL amodal hub: the concept representation itself**
- **BRAIN'S MATH:** **UNPINNED as an equation.** Characterised only qualitatively as a deep,
  multi-step nonlinear transformation with recurrent feedback dynamics, whose core operation is
  **pattern completion via a compact abstract "label" feeding back onto shallower unimodal features**
  (Jackson, Rogers & Lambon Ralph 2021 *Nat Hum Behav* 5:774+; Jackson/Orban/Tiesinga 2026). Measured
  dynamics but no dynamical equation: decodable ~200 ms, geometry breakpoint ~473 ms,
  anterior-posterior position predicts degree of change **r²=0.73, p<0.002** (Rogers, Cox, Lu,
  Shimotake et al. 2021 *eLife* 10:e66276). Directional flow VL→Tip ~140 ms, **backward connections
  consistently stronger than forward** (Tiesinga 2023 *Sci Rep*).
  **PINNED SUB-FACT:** conceptual COMBINATION in LATL is **approximately ADDITIVE** (Baron & Osherson
  2011 *NeuroImage*).
  **The only available equations belong to MODELS of the hub, not to the hub**: Jackson 2021 is a
  recurrent ANN with **error-driven (backprop-style) learning**, 3 spokes, two hidden layers,
  ~1 shortcut per 9 indirect-route connections, trained on all 3×3=9 modality-pair tasks. Do not
  over-read this into "training is the right tool" — but equally, do not claim the brain's model is
  Hebbian.
- **OURS:** `hdlab/lexical_similarity.py` — hand-authored `CONCEPT_FEATURES` dict of DOM/ROLE tag
  frozensets over ~230 concepts; concept vector = FHRR bundle of hashed feature vectors;
  `:557-563 _cos_complex = Re(Σ conj(a)·b)/d`. Designed bands: same DOM+ROLE ≈ 1.0, DOM only ≈ 0.5,
  disjoint ≈ 0.0. Feedforward, one-shot, **no recurrence**, **unweighted** (a tag shared by 8
  concepts counts as much as a tag shared by 1).
- **FIDELITY:** WRONG-OP. Unweighted shared-feature overlap is the **precise inverse** of the brain's
  privileging of DISTINCTIVE (few-concept) features. Additionally: **the feature inventory is a
  hand-built lexicon, not learned** — the HD layer only re-encodes it.
- **WIRED:** YES
- **EVIDENCE:** self-test pins `sim(vessel,ferry)=0.634`. **NO FLOOR — UNTESTED as an organ.**
- **BLOCKS:** near-neighbour discrimination; any judgement over the ~99.4% of vocabulary outside the
  hand lexicon (which falls through to B5 and is capped below the decision threshold).

**B2 — Per-occurrence combination: how ONE encounter becomes a vector**
- **BRAIN'S MATH:** graded population rate code (Rolls & Tovee 1995; Panzeri & Treves), pooled as a
  weighted sum then **divisive normalisation with a POOL-SHARED denominator**,
  `r_i = x_i^n/(σ^n + Σ_j x_j^n)` (Carandini & Heeger 2012 *Nat Rev Neurosci* 13:51-62; Heeger 1992).
  Ratios inside the pool PRESERVED. See §3 correction 1 for what this does and does not license.
- **OURS:** `hdlab/grounding_acquisition_loop.py:150-162` — `acc += rng.choice([-1,1], d)` per
  content word (sha256-seeded Kanerva random index), then `out = np.sign(acc)`; `out[out==0]=1.0`.
  **d=256.** A `graded=True` keyword exists (`:158`) and is **DEFAULT FALSE**.
  FHRR path `hdlab/bundling.py:34-39`: `s = vectors.sum(0)` then `s/|s|` **per component**;
  `:41-42` uses whole-vector L2 for real input — **the pool-shared form is present in the same
  function, applied only to the other dtype.**
- **FIDELITY:** WRONG-OP, and the *inverse* of the right one. Measured: **13.85% of dimensions carry
  <10% of p90 evidence and are amplified to full weight** — the operation does not merely discard the
  distinctive signal, it amplifies pure noise to maximum weight at ~1 dimension in 7.
- **WIRED:** YES, live — **with the brain-faithful mode switched OFF by default.**
- **EVIDENCE:** `data/exp_graded_divisive_comparator_v1` **HARD_PASS**, n=4000 held-out.
  LIVE 0.6395 → GRADED 0.6997, **d=+0.0602 CI [0.0440,0.0762]**.
  **FLOORS measured in-cell: scrambled-context 0.4975 / 0.5065; frequency baseline 0.4800;
  chance 0.50.** Mechanism claim WITHDRAWN (§3.3).
- **RELATED ORGAN WE OWN AND DO NOT USE:** `hdlab/random_indexing.py:219` implements the
  **order-sensitive** Sahlgren variant (`C[center] += roll(IDX[other], offset)`), with convergence
  error O(√(log V / N)) ≈ 0.037 at N=8192. The live path uses the unordered bag version
  (`:200-201`). That is a RIGHT-OP-WRONG-PLACE *within* this organ.
- **BLOCKS:** everything downstream. This is the substrate's only encoder on the live path.

**B3 — Across-occurrence accumulation: how encounters become a concept**
- **BRAIN'S MATH:** slow replay-driven cortical consolidation into a **graded synaptic weight
  distribution**; distinctiveness is computed from those frequency statistics (CLS: McClelland,
  McNaughton & O'Reilly 1995; Tyler & Moss CSA — a feature's fate is DISTINCTIVENESS × CORRELATIONAL
  STRENGTH, both frequency statistics). **The distinctiveness WEIGHT FUNCTION is UNPINNED** — nothing
  in the literature says by how much a rare feature is up-weighted, and our one instantiation
  (log-IDF) was refuted (§3.2).
- **OURS:** `hdlab/reading_grounding_loop.py::ConceptSpace.observe` — `self._sums[lemma] += ctx_vec`,
  a genuine graded accumulator, **correct** — then `anchor_matrix:450` returns
  `np.sign(np.stack(...))` and `bundle:460` returns `np.sign(s)`. **The graded quantity is built and
  thrown away one line before use.** A dimension where 36 of 70 encounters agreed becomes
  bit-identical to one where 70 of 70 agreed. `freeze_graded():482` exists, **default OFF**.
- **FIDELITY:** RIGHT-OP-WRONG-PLACE. The information already exists in memory.
- **WIRED:** YES for the destructive path; graded path wired but default-OFF.
- **EVIDENCE — GEOMETRY ONLY, NO TASK FLOOR OF ITS OWN.**
  `experiments/diag_anchor_field_geometry_v1.py`, 400 concepts × 70 held-out sentences, byte-identity
  to the live `context_vector` asserted first: **‖field mean‖/‖anchor‖ = 0.5841 (SIGN) vs 0.3545
  (GRADED); mean pairwise cosine 0.3397 vs 0.1319; participation ratio 126.6 vs 77.0** (sign
  *flattens the spectrum toward noise*). ~~Under the live code **58% of every concept vector's norm
  is the component shared by all 400 concepts.**~~
  🔴 **CORRECTED 2026-08-14: re-measured on the LIVE field (n=2377, d=256) the same ratio is 0.2997
  SIGN / 0.3650 GRADED, and it is a NORM RATIO, not a variance fraction — true shared-direction
  energy 0.1535, PC1 0.0350.** Never restate it as "more than half the variance". Detail at organ
  G3 and in `notes/STATUS_LESSONS.md` CORRECTION C11.
  Its task evidence is B2's cell, where it is not separately attributed.
- **BLOCKS:** near-neighbour discrimination; sense selection.

**B4 — Representation format and capacity**
- **BRAIN'S MATH:** dense, graded, LOW effective dimensionality — first ~4 group PCs define the
  shared space (Huth 2012 *Neuron* 76:1210); ~65 experiential attributes across 14 domains (Binder
  2016); ~two-thirds of temporal-pole electrodes active per exemplar (Tiesinga 2023); IT sparseness
  index ~0.2-0.3. **Explicitly NOT sparse, NOT binary.** Sparse ~0.2% coding is the MTL regime
  (Waydo 2006) — a *different system*; conflating them is a trap. Separately pinned and explicitly
  **not** to be imported: V1's power-law eigenspectrum (Stringer 2019).
- **OURS:** context path **256-dim bipolar ±1** (`grounding_acquisition_loop.py:79`); lexical path
  8192-dim complex64 unit-phase; grounded path 12-dim real graded; `concept_encoder` 4096-dim ternary
  at 2% sparsity; `gsbc_graded_encoder` 32 blocks × 128, top-5 per block, unit-L1 per block
  (active fraction 0.039).
- **FIDELITY:** WRONG-OP (binary where the brain is graded) **and under-capacity**: 2,377 concepts in
  a 256-dim space.
- **WIRED:** YES — d=256 is the live default.
- **EVIDENCE:** `data/exp_capacity_ceiling_near_far_v1` **MIDDLE_BAND_CAPACITY_PARTIAL**, n=4000.
  NEAR by d: QUANT [0.6395, 0.7030, 0.7380], GRAD [0.6980, 0.7495, 0.78225] at d = 256/1024/4096.
  Crosstalk between unrelated random-index codes falls **exactly as 1/√d: 0.0498 / 0.0249 / 0.0125**.
  **FLOORS in-cell: 0.49775 / 0.5095 / 0.4845, chance 0.50.** Between-projection-draw sd reported
  next to the CI (**0.0090**) — item bootstraps are blind to shared-randomness variance and every
  cell built on a random projection must report it.
  **16× the dimensionality buys +0.0843 — more than any mechanism change this program has produced.**
- **BLOCKS:** the LEVEL of every similarity decision in the substrate. **Largest measured lever owned.**

**B5 — Sensorimotor spokes: grounding for concrete concepts**
- **BRAIN'S MATH:** modality-specific cortex feeding the hub. **The hub-spoke combination rule is
  UNPINNED.** Two hard results bound the design: left dorsal ATL represents object-colour knowledge
  in **congenitally blind and sighted alike** — a sensory-independent code coexists with the
  sensory-derived one (Wang, Men, Gao, Caramazza & Bi 2020 *Neuron* 107:383-393); and text-only
  channels recover non-sensorimotor meaning well, sensory poorly, **motor minimally** (Xu et al. 2025
  *Nat Hum Behav*).
- **OURS:** `hdlab/grounded_similarity.py:140-189` — 12-dim vector = 11 Lancaster sensorimotor means
  + Brysbaert concreteness, **z-scored against the whole 39,707-word population** (`:146-150`, which
  is exactly the pool-shared statistic the context path lacks, applied to the wrong 12 dimensions),
  then raw cosine, **capped at 0.45** so it structurally cannot cross the 0.50 link threshold.
- **FIDELITY:** RIGHT-OP-WRONG-METRIC, and mis-applied. The module's own docstring measures that raw
  cosine **cannot separate a synonym from a sibling**: sofa/couch 0.968, happy/joyful 0.962,
  apple/orange **0.952**, dog/cat 0.932. Literature note: sensorimotor distance is among the best
  predictors but *"never the overall best predictor in any single dataset"* (Johns 2023), and the
  claim that norms *collapse* near-synonyms was **theoretically motivated but empirically untested**
  — our measurement above fills that gap.
- **WIRED:** YES — but capped below the decision threshold, so it never decides anything.
- **EVIDENCE:** the self-documented table above. **NO FLOOR.** Sensorimotor-applied-to-abstract was
  previously HARD_FAIL and SHELVED.
- **BLOCKS:** grounding of concrete vocabulary; the ~99.4% of words outside `CONCEPT_FEATURES`.

### C. COMPARISON, SELECTION, CONTROL

**C1 — Semantic comparison: scoring two representations**
- **BRAIN'S MATH:** **"There is no cosine anywhere in the brain."** Comparison is deep recurrent
  nonlinear settling; what is comparable to a similarity is the state's **trajectory**, computed on a
  code already normalised against the concurrently active population. **The trajectory metric itself
  is UNPINNED.** (Jackson 2021; Rogers 2021 *eLife*.)
- **OURS:** `hdlab/reading_grounding_loop.py::canonicalize_fast:708-770` —
  `nb = np.sign(new_raw_sum)` (a THIRD binarisation, of the query, `:736`), then
  `sims = (mat @ nb)/(norms·nn)`: cosine between two ±1 vectors, **which equals `1 − 2·Hamming/d`.
  The decision variable of this entire substrate is a Hamming distance between two 256-bit
  majority-vote patterns.** `ReadoutConfig(graded_query=True)` exists (`:597-616`), **default OFF**.
- **FIDELITY:** RIGHT-OP-WRONG-METRIC. Ranked *below* B2/B3 deliberately: a cosine on a properly
  normalised graded code is a defensible first-order readout; a Hamming distance over prototype
  patterns cannot represent the distinction at all. **Fix the code before litigating the metric.**
- **WIRED:** YES
- **EVIDENCE:** `data/exp_context_conditioned_near_neighbour_v1` **MIDDLE_BAND_FLOOR_HUGGING**,
  n=4000: A1=0.6395; **FLOORS A3(scrambled)=0.4975, A4(frequency)=0.4800, chance=0.50**;
  `mean_winning_cos = 0.1476`. Second-order point worth keeping: `cos(a1,a2)` is LOWER under sign
  than under the graded code at every distinctive:shared ratio — **sign() makes near-neighbours look
  MORE separated while making the separation MEAN LESS.**
- **BLOCKS:** sense selection; every canonicalisation decision.

**C2 — Winner selection**
- **BRAIN'S MATH:** graded competition implemented BY the normalisation pool, not a hard argmax
  (Carandini & Heeger 2012). Semantic aphasia shows selection failing specifically when a WEAK TARGET
  must beat a STRONG COMPETITOR (Jefferies & Lambon Ralph 2006 *Brain* 129:2132-2147).
- **OURS:** `canonicalize_fast:770` `int(np.argmax(sims))`, first-max tie-break; same at
  `concept_encoder:564`.
- **FIDELITY:** WRONG-OP in form, **but for a 2AFC accuracy metric argmax IS the deterministic limit
  of the softmax and cannot change the expected score.** Low priority by the brain's own metric.
- **WIRED:** YES
- **EVIDENCE:** controlled, not tested — `readout_disagreements = 0` across the graded cells; LIVE has
  9 ties at n=4000, max possible shift 0.0033, and scoring ties as losses makes the delta LARGER.
  **Adequately excluded as a confound; never independently tested.**
- **BLOCKS:** nothing measurable. Recorded for completeness, not ranked for build.

**C3 — Semantic control: how task/context reshapes the comparison**
- **BRAIN'S MATH:** control does NOT select from a candidate list; it applies **MULTIPLICATIVE GAIN**
  to the task-relevant dimension. DCM: IFG's effective connectivity to the spoke holding the relevant
  feature dimension is selectively boosted, **F(2,34)=3.86, p=.03** (Chiou & Lambon Ralph 2018
  *Cortex*, PMC6006425). Same hub weights + different control settings reproduce context-dependent
  behaviour (Hoffman, McClelland & Lambon Ralph 2018 *Psychol Rev* 125:293-328). Non-dominant
  retrieval recruits a **higher-dimensional** coding regime; dimensionality change mediated **51.7%**
  of the gradient-cognition relationship (Gao 2022 *eLife*).
  **THE GAIN FUNCTION — what sets the per-dimension multiplier — is UNPINNED.**
- **OURS:** context enters **additively, as another point in the same space**
  (`context_vector_masked` → `canonicalize_fast`); `concept_similarity` has **no context port at all**.
- **FIDELITY:** RIGHT-IDEA-WRONG-ALGEBRA.
- **WIRED:** YES for the additive form.
- **EVIDENCE — a positive and a floored negative, the most instructive pair in the map.**
  Adding *any* context port: 0.5390 → 0.6395, **d12 = +0.1005 CI [0.0795,0.1227], scrambled floor
  0.4975.** But the brain-faithful multiplicative version, built and tested:
  `data/exp_task_local_normalisation_pool_v1` **HARD_FAIL_GAIN_HURTS** — gain `g = |a_t − a_d|`
  scored **0.6777, d = −0.0220 CI [−0.0340,−0.0097]**, significantly WORSE. **FLOORS: 0.4953 / 0.5065
  scrambled, 0.4800 frequency.** Both baselines reproduced exactly (R_LIVE 0.6395, R_BASE 0.6997), so
  the read is licensed.
  **MECHANISM OF THE NEGATIVE, and it unifies four separate nulls:** with 70 observations per concept
  in a 256-dim random projection, the dimensions with the largest anchor-difference are
  disproportionately the *worst-estimated*. Every per-dimension REWEIGHTING tried is null or harmful
  — log-IDF null, global-field z-scoring +0.0018, pool-inverse −0.011, contrast gain −0.0220 — while
  **the only thing that helped was removing a per-dimension DESTRUCTION.** That is an
  estimation-noise statement. **It points at B4, not at C3.**
- **BLOCKS:** context-conditioned sense selection. **STRICTLY BLOCKED BEHIND B4.**

**C4 — Settling / stabilisation** *(EXPLICIT NEGATIVE RECOMMENDATION — do NOT build)*
- **BRAIN'S MATH:** recurrent attractor settling to a fixed point; CA3 completion with cue
  re-injection (Hasselmo 2002; Neunuebel & Knierim 2014 *Neuron* 81:416-427); ATL hub settling over
  ~200-500 ms (Rogers 2021).
- **OURS:** NONE in the comparator. We DO own the organs — see D2.
- **FIDELITY:** MISSING — **BY DESIGN. The standing "reuse the owned organ" rule must NOT fire here.**
- **EVIDENCE:** Tyler & Moss Conceptual Structure Account (*TiCS* 2001; Taylor, Devereux & Tyler
  2011): distinctive features are WEAKLY CORRELATED with a concept's other features, and **attractor
  settling is driven by correlational structure** — which is exactly why distinctive features are
  computationally fragile. Adding CA3-style completion to the comparator would make near-neighbour
  discrimination WORSE. And both owned implementations terminate in `np.sign`, so wiring them in adds
  a **fourth** prototype operator. **We already have an attractor network's nonlinearity with none of
  its recurrent weights: all of the prototype drift, none of the completion benefit.**
- **BLOCKS:** nothing. Revisit only after B2/B3/B4 land AND paired with real C3 gain, which is the
  brain's own compensator for this cost.

### D. MEMORY SYSTEMS

**D1 — Dentate gyrus: pattern separation**
- **BRAIN'S MATH:** sparse expansion + strong inhibition → decorrelation. Sparse coding level is
  **pinned**: <2×10⁶ of ~10⁹ MTL neurons (**~0.2%**) per percept; each neuron fires to ~50-150
  concepts (Waydo, Kraskov, Quian Quiroga, Fried & Koch 2006 *J Neurosci* 26:10232). DG activity
  changes **abruptly/nonlinearly** with small environmental change (Neunuebel & Knierim 2014).
  **The nonlinearity type, expansion ratio and threshold are UNPINNED.**
- **OURS:** `hdlab/dg_pattern_separation.py:83-131` — `W = N(0,1)/√input_dim` fixed Gaussian
  expansion (hashlib-seeded, deterministic); keep top-`round(sparsity·expand_dim)` by |magnitude|,
  zero the rest, L2-normalise. Pure feedforward expand-then-kWTA, no learning.
  `hdlab/hippocampal_encoder.py:113-116` does the same into a **sparse ternary** code
  (`mask · sign(dense)`, sparsity ~0.01-0.03).
- **FIDELITY:** **SAME.** Random expansion + k-WTA + normalise is the brain's operation, in the right
  order, at roughly the right sparsity.
- **WIRED:** **NO — `dg_pattern_separation` has ZERO `hdlab/` importers. Orphan.**
- **EVIDENCE:** docstring reports `item_purity ~0.19-0.20`, 35 spawned / 33 grounded. **NO FLOOR —
  UNTESTED.**
- **BLOCKS:** nothing today; required the moment D3 goes on the live path.

**D2 — CA3: pattern completion / auto-association**
- **BRAIN'S MATH:** sparse **auto-associative recurrent network**; estimated capacity ~36,000
  patterns at rodent CA3 connectivity (Treves & Rolls 1992/1994); CA3 output stays closer to the
  stored representation than its degraded DG input (Neunuebel & Knierim 2014). **The update rule is
  not stated in the biology** — Hopfield sign-update and modern-Hopfield softmax are OUR imports.
- **OURS:** `cleanup_family.py:121-179` — classical Hopfield `W = CᵀC/M` (zero diag), `s ← sign(sW)`;
  modern Hopfield `s ← sign(softmax(β·s@Cᵀ)@C)`, **β default 8.0**, ≤8 steps.
  `iterative_attractor.py:104-126` — `state ← L2norm( α·q₀ + (1−α)·(softmax(β·state@Cᵀ)@C) )`,
  **effective β = temp·√D**, tol 1e-3, ≤8 steps, then `argmax(state@Cᵀ)`.
  `hippocampal_encoder.py:191-192` — `settle = sign(W @ cue)`, **one step only**.
- **FIDELITY:** RIGHT-OP-WRONG-METRIC. Op-class is the brain's; **every implementation terminates in
  `sign()`**, adding a prototype operator the brain does not have.
- **WIRED:** `cleanup_family` + `iterative_attractor` **YES** (live, consumed by `gap_detector`).
  `hippocampal_encoder` **NO**.
- **EVIDENCE:** `hippocampal_encoder` self-test 14/14 PASS — **NO FLOOR**. Its live use inside
  `gap_detector` is floored (see H1). **UNTESTED as a completion organ.**
- **BLOCKS:** episodic recall. Explicitly **NOT** near-neighbour discrimination — see C4.

**D3 — Hippocampus: one-shot episodic write / index**
- **BRAIN'S MATH:** *"The hippocampus itself does not contain the content of an experience but it
  does provide an **index**"* — a sparse pointer into distributed neocortical activity (Teyler & Rudy
  2007 *Hippocampus* 17:1158; Goode, Tanaka, Sahay & McHugh 2020 *Neuron* 107:805). One-shot Hebbian
  write on the sparse code (Marr 1971). **The allocation/address rule is UNPINNED.**
- **OURS:** `hdlab/hippocampal_encoder.py:179` `W[np.ix_(nz,nz)] += np.outer(sub,sub)` — sparse
  one-shot outer product, K² cost per write. CLS replay `:304`
  `W_cortex += lr · outer(code, settle(code))`.
- **FIDELITY:** **SAME** (for the write op; the index/allocation half is unbuilt and its brain math is
  UNPINNED anyway).
- **WIRED:** **NO**
- **EVIDENCE:** self-test 14/14 PASS. **NO FLOOR — UNTESTED.**
- **BLOCKS:** episodic memory; makes D4 untestable in its brain-faithful form.

**D4 — Consolidation: replay scheduling**
- **BRAIN'S MATH:** partly pinned, and the pinned parts are damning for what we do.
  ~5-10 sharp-wave ripples/sec during SWS, ~10-30k events over 8 h sleep, and reactivation is specific
  to the subset of **LARGE** SWRs (Liu 2024 PMC11068097; *Neuron* 2025).
  **⚠️ UNSOURCED, CORRECTED:** this line previously said *"each waking experience replayed only 1-3
  times"* and cited PMC11068097. **That source contains no per-experience replay count, and the drill
  found no source anywhere that pins one.** Treat replay count as a **free parameter to sweep, not a
  constant**. The only quantitative claim PMC11068097 supports is *"during postexperience sleep,
  SPW-Rs continued to replay those trial blocks that were reactivated most frequently during waking
  SPW-Rs."* The stronger, better-sourced statement that replaces it: replay is **selective at the
  EVENT level** — only a subset of large-amplitude SWRs carries reactivation, their rate selectively
  rises in post-learning sleep, correlates with performance, and closed-loop optogenetic boosting of
  them causally improves retrieval (Robinson, Todorova, Fernandez-Ruiz et al., *Neuron* 2025/2026,
  doi 10.1016/j.neuron.2025.10.003).
  SWRs phase-locked to the up-state of the 0.5-4 Hz slow oscillation, ~5-10 SWRs per ~1 s up-state
  (**⚠️ UNVERIFIED CITATION** — "Helfrich 2021 *PNAS* 118 e2012075118" could not be confirmed; searches
  return Helfrich 2018/2019 *Nat Commun* / *Neuron* on SO-spindle-ripple coupling, not a 2021 *PNAS*
  carrying this number. Flagged, not re-cited; confidence LOW = absence of confirmation).
  **Only REVERSE replays scale with reward magnitude; forward replays are reward-invariant** —
  *"the number of reverse-ordered, but not forwards-ordered, replays was significantly correlated to
  reward level"* — **Ambrose, Pfeiffer & Foster 2016** *Neuron* 91(5):1124-1136. **⚠️ CORRECTED
  CITATION:** this was attributed to Foster & Wilson 2006 *Nature* 440:680, which **discovered reverse
  replay but never showed reward modulation**. Both papers are needed; only the 2016 one supports the
  claim as stated.
  Optimal rehearsal — **⚠️ CORRECTED AND DOWNGRADED.** Landauer & Bjork 1978's expanding schedules are
  **`0,3,10` and `1,4,10`** (ratios ~4× then ~2.5×), **not "approximately doubling"**; the uniform
  comparators were `(0,0,0)/(1,1,1)`, `(4,4,4)/(5,5,5)`, `~(10,10,10)`. The win is scoped to
  **TEST-type practice** (retrieval attempts) — the paper's own words are that *"uniform spacing was
  slightly better if the information was repeated"* (study-type). And the general superiority of
  expanding is **CONTESTED**: Karpicke & Roediger 2007 and Storm, Bjork & Storm 2010 find equal-interval
  spacing matches or beats expanding at long retention intervals, expanding winning mainly at short
  delays. **So: expanding intervals are PINNED as a real 1978 effect for test-type practice at short
  delay, and UNPINNED as a general optimum. Do not build "expanding, doubling" in as a fixed law.**
  Consolidation timing pinned: lexical competition absent immediately, present after a 12-h interval
  **containing sleep** (Dumay & Gaskell 2007 *Psych Sci* 18:35 — this half was correct and stands).
  **⚠️ OVER-CLAIM CORRECTED:** the meta-analysis is **Schimke, Angwin, Cheng & Copland 2021**
  *Psychon Bull Rev* 28:1811 (25 studies, k=29, n=1,396), and its **`g=0.50` is the OMNIBUS
  sleep-vs-WAKE effect on novel word learning — an interval-CONTENT contrast, not "consolidation vs
  none"**. Its breakdown: recall `g=0.57`, recognition `g=0.52`, **lexical INTEGRATION "a small
  effect"**. The integration measures are the ones that actually index the CLS claim, and they are the
  **WEAKEST** in the analysis. Quoting `g=0.50` as an integration effect over-claims. Honest headline:
  *sleep reliably helps novel-word memory at a moderate effect size, and helps integration measurably
  less.*
  **THE SELECTION FUNCTION — which traces get replayed — is UNPINNED.** *(Confirmed still correct by
  the drill. The leading normative candidate is Mattar & Daw 2018 `priority(s,a) = GAIN(s,a) × NEED(s)`,
  *Nat Neurosci* 21:1609 — but NEED is computed from the successor representation `M = (I − γP)⁻¹`,
  i.e. **organ D7, which we do not have**. So the selection function is not merely unpinned in the
  literature; it is blocked on a missing organ for us specifically.)*
- **OURS:** faithful-ish version `hdlab/continual.py:99-111` — `W += lr·(v_subᵀ @ k_sub)` forward
  plus `W_back += lr·(k_revᵀ @ v_rev)` reverse-orientation replay, triggered every N calls by an NREM
  decorator. **The LIVE loop instead does a single averaging op per cycle**
  (`reading_grounding_loop.py::checkpoint():1291`), ungated, un-interleaved, un-budgeted, with no
  reward scaling and no expanding schedule.
- **FIDELITY:** WRONG-OP-CLASS at the live site. The faithful version exists and is **ISLANDED**.
- **WIRED:** `continual.py` **NO**.
- **EVIDENCE:** `continual.py` docstring claims `+0.57 drift_reduction` as MEASURED_MECHANISM — **no
  floor stated in the module**. The one properly floored result:
  `exp_cls_interleaved_replay_consolidation_pilot_v1` **HARD_PASS**, old-recall `full_cls 0.808` vs
  **floors `naive_dual_w 0.217`, `single_seq 0.217`, 3/3 seeds** — a real, failable floor, and the
  cell is **not wired**. **UNTESTED on real text.**
- **BLOCKS:** learning new material without destroying old learning — i.e. it blocks running the
  growth loop at scale safely.

**D5 — Active working-memory maintenance**
- **BRAIN'S MATH:** persistent-activity attractor WM vs activity-silent synaptic WM (Wang; Stokes;
  Mongillo — short-term facilitation holds the item with *no spiking*). **Which dominates is
  CONTESTED**; content/PE-gated incremental update (PBWM).
- **OURS:** **`hdlab/working_memory.py` CONTAINS NO WORKING MEMORY.** All 116 lines are two
  `ValueError`-raising guard functions plus envelope constants. No bank, no state, no update rule.
  **This is a live trap for anyone auditing by filename.** The actual mechanisms are
  `hdlab/slot_attention_wm.py:151-194` — `scores = einsum("bld,rd->brl", tok_reps, role_query)/√d`,
  `attn = softmax(scores)` over token positions (padding → −inf), `fillers = einsum("brl,bld->brd")`,
  slot address `addr_w = softmax(addr_logits/addr_temp)` across K slots — and
  `hdlab/situation_model_accumulate.py` (see E2).
- **FIDELITY:** `working_memory.py` = **MISSING**. `slot_attention_wm` = RIGHT-OP-WRONG-METRIC (a
  learned softmax attention head is neither attractor persistence nor synaptic facilitation).
- **WIRED:** `working_memory.py` YES *(and it does nothing)*; `slot_attention_wm` NO (gate = SHELVE);
  `situation_model_accumulate` YES.
- **EVIDENCE:** the chain-grade number (K=4096, recall 0.9927, cv 0.0006) belongs to an EXPERIMENT,
  and the module's own docstring warns that arms below `k_per_bank=64` are **saturated BY
  CONSTRUCTION**. **The organ as it exists in `hdlab/` has NO floored evidence.**
- **BLOCKS:** multi-sentence situation-model construction.

**D6 — Sequence / order memory**
- **BRAIN'S MATH:** CA3 asymmetric recurrent weights; theta phase precession compresses sequences
  into a cycle for plasticity. **The precise learning rule is UNPINNED.**
- **OURS:** `hdlab/sequence_memory.py:70,98` — `S += outer(k_next, k_prev)`, reverse store
  `S_back += outer(k_prev, k_next)`; retrieve `S @ k_prev` then `argmax`. **No normalisation, no
  capacity control.**
- **FIDELITY:** **SAME** op-class — asymmetric Hebbian outer product is exactly the standard model.
- **WIRED:** NO
- **EVIDENCE:** `exp_c3_compressed_sequence_replay_v1` HARD_PASS at every depth [1,3,5,7,10]
  (docstring provenance, commit `a27939c5`). **Floor not restated in the module — PARTIALLY FLOORED.**
- **BLOCKS:** nothing today.

**D7 — Successor representation: the predictive relational map** *(MISSING, and its math is FULLY PINNED)*
- **BRAIN'S MATH:** `M(s,s') = E[Σ_{k≥0} γ^k · 1{s_k = s'} | s_0 = s]`, i.e. **`M = (I − γP)⁻¹`**.
  Place cells are rows of M; **grid cells are the eigenvectors of M**. Multi-scale: several γ run
  simultaneously (Dayan 1993 *Neural Computation* 5:613; Stachenfeld, Botvinick & Gershman 2017
  *Nat Neurosci* 20:1643; Momennejad 2017 *Nat Hum Behav*). Personalised PageRank ≡ SR under stated
  conditions. Related and also pinned: TEM's conjunctive code **`p = g ⊗ x`** (structural × sensory),
  where the same structural code g reused across environments gives immediate transitive-inference
  generalisation (Whittington et al. 2020 *Cell* 183:1249).
- **OURS:** **NONE.** The nearest things: `hdlab/kg_traversal.py:89-111` does hard-argmax n-hop
  (`key = E[s]*R[p]`, `scores = E @ (W @ key)`, argmax, feed the argmax entity back in — **no soft
  state between hops**); and `hdlab/multi_hop.py:69-70` has a softmax chain whose **default β = n_dim
  makes the softmax a Dirac delta, i.e. identical to hard argmax** — the module's own code says so at
  `:88-96` and records that **two prior cells were confounded by exactly this.**
- **FIDELITY:** **MISSING**, and the nearest owned organ is silently degenerate.
- **WIRED:** NO
- **EVIDENCE:** none for SR. **UNTESTED.**
- **BLOCKS:** multi-hop relational reasoning; transitive inference; any "what follows from what" query
  over the 1.21M-edge CSKG.

**D8 — The cascade synapse: memory lifetime** *(MISSING, and its math is FULLY PINNED)*
- **BRAIN'S MATH:** *(corrected 12 ways by `notes/drill_cascade_synapse_replay_consolidation_biology_2026-08-14.md`; the pre-correction text had the N exponent, the model attribution and the α all wrong)*
  each synapse carries an internal depth `d` with **TWO transition families, both falling as `2^-d`**:
  a **PLASTIC** one `q_k = q·x^(k-1)` that flips efficacy and **RESETS depth to 1 in the OPPOSITE
  cascade**, and a **METAPLASTIC** one `p_k = q·x^k` that moves `k → k+1` at constant efficacy
  (`x = 1/2`; Ben Dayan Rubin & Fusi 2007 — *"the probability for BOTH transitions decreases
  exponentially as the synapse moves down along the cascade"*). This yields **power-law forgetting
  `f(t) ~ t^-α` with α = 1** (Fusi lab 2007/2021; **α = 3/4** is the number Fusi, Drew & Abbott 2005
  actually published and is what must be quoted whenever that paper is cited — **α = 0.5 belongs to
  Benna-Fusi 2016, a different model, and must not be offered as "the cascade"**) instead of
  `exp(-t/τ)`. **Capacity scaling, corrected — the map previously had this exactly backwards:**

  | model | signal decay | initial SNR | lifetime / capacity |
  |---|---|---|---|
  | binary, fast (`q = O(1)`) | `exp(-q r t)` | `O(1)` | **`log N`** |
  | **cascade (Fusi, Drew & Abbott 2005** *Neuron* 45:599**)** | `1/t` | `√N/n` | **`√N`** |
  | **bidirectional cascade (Benna & Fusi 2016** *Nat Neurosci* 19:1697**)** | `1/√t` | `√N/√m` | **`N`** (`N/log N` optimised) |

  So `~N` is **Benna-Fusi 2016's** headline, not the cascade's — Benna & Fusi say so themselves:
  *"the memory lifetime in previous models of complex synapses with bounded weights scales at most as
  √N."* Continuous version: a chain of variables coupled by leaky integrators with **geometrically
  increasing time constants**, ratio **4× per level** (`τ_k = 2^(2k+1)`, `C_k = 2^(k-1)`,
  `g_{k,k+1} = 2^(-k-2)`), capacity approximately linear in K, and the SNR is

  ```
  SNR(t)  ~  √N · exp(-t/T) / ( √t · √(log T) ),        T = 2^(2m+1)
  ```

  **`√N`, NOT `N`** — the map's prior `N/(√K·t^0.5)` overstated the predicted retention level by a
  factor of `√N`, which at `N = 1024` is **32×**. The `√K` part survives if `K = m`, since
  `√(log T) ~ √m`. **And the comparison baseline was wrong too:** a single-state *bounded* or *binary*
  synapse decays **exponentially** (`τ = 1/(qr)`, `SNR ~ q·√N_syn·exp(-qrt)`), **not** as `N/t`; the
  `√N/t` form is the cascade itself and the Lahiri-Ganguli envelope. The only single-state model with
  a power law is the **unbounded perfect integrator**, `SNR = √(N/t)` — which is the one we
  accidentally own (see D8 **OURS** and the KNOWN-DEFECT register).
  **A predicted, must-observe NEGATIVE:** complex synapses pay an initial-SNR cost of `1/n` (cascade)
  / `1/√m` (Benna-Fusi). An arm that does not show early-retention LOSS is not implementing this organ.
  *(Also corrected: Roxin & Fusi is **2013**, *PLoS Comput Biol* 9(7):e1003146, not 2012 — and its
  multistage model SHARES the cascade's scaling rather than beating it, so it never supported the `~N`
  claim it was cited for.)*
- **🅿️ PARKED-BY-SCALE — CROSSOVER `N > ~1e6` SYNAPSES; WE RUN `d = 256..4096`.** Published cascade
  advantages use 2.5e7 and 5.4e9 synapses. At `n = 10` the cascade only beats simpler multistate
  models above ~1e6. We are **two to four orders of magnitude below the crossover on `d`**, and the
  relevant synapse count is likewise far below it. **A negative result here is THE PUBLISHED
  PREDICTION, not a ceiling and not evidence against the organ.** Do not queue a cascade-vs-single-state
  capacity bake-off expecting a win; if it is run at all, it is run to confirm the predicted null and
  the predicted initial-SNR cost, and it must be pre-registered as such.
- **OURS:** **NONE.** Every store in the substrate is a **single-state weight**: `W += outer(v,k)`
  (`sequence_memory`, `hippocampal_encoder`, `kg_traversal`, `intent_classifier`, `continual`,
  `streaming_attention`). The only multi-timescale-ish object is `hdlab/temporal_trace.py:158-159`
  `trace ← α·x + (1−α)·trace` — **one** exponential timescale, and `excitability.py:60,66` an EWMA
  (η=0.1) with a flat 0.999 decay — again one timescale.
- **FIDELITY:** **MISSING.**
- **WIRED:** NO
- **EVIDENCE:** none. **UNTESTED.**
- **BLOCKS:** retention over long horizons. **This is the pinned equation behind "don't forget", and
  we have none of it.** A consolidation SCHEDULE (D4) on a single-state synapse cannot buy what a
  multi-timescale synapse buys for free.

**D9 — Synaptic tag and capture: which write gets consolidated**
- **BRAIN'S MATH:** persistence = **TAG × PRP product**, both present in overlapping windows (tag
  lifetime ~1-4 h, PRP over hours); RNN implementation consolidates iff **`tag × PRP > θ`**. Memories
  within a **~5-hour window co-allocate** to overlapping engram populations (Frey & Morris 1997
  *Nature* 385:533; Redondo & Morris 2011; Clopath et al. *Comms Biol* 2021).
- **OURS:** `hdlab/excitability.py:60-100` — per-atom importance `E[i] ← (1−η)E[i] + η·use_signal`
  (η=0.1 EWMA), global decay `E *= 0.999`, then downscale the bottom-`threshold_frac` rows by L2 norm
  at a quantile cut. The module's own docstring names CREB / synaptic-tag-and-capture as its analog.
- **FIDELITY:** RIGHT-OP-WRONG-METRIC — a single EWMA is not a **two-factor product**, there is no
  PRP term, and there is no co-allocation window.
- **WIRED:** **NO** — registry: ISLAND, **zero consumer**.
- **EVIDENCE:** none. **UNTESTED.**
- **BLOCKS:** selective consolidation; the "which of today's 11,122 refusals deserve a retry" question.

### E. BINDING AND STRUCTURE

**E1 — Role-filler binding**
- **BRAIN'S MATH:** **UNPINNED and actively CONTESTED three ways** — theta-gamma phase coding (Lisman
  & Jensen), conjunctive mixed selectivity (Rigotti & Fusi), tensor-product representations
  (Smolensky). There is no settled equation to be faithful to. **PINNED adjacent fact:** TEM's
  hippocampal conjunctive code is a **product**, `p = g ⊗ x` (Whittington 2020). **PINNED adjacent
  fact 2:** LATL conceptual combination is **additive** (Baron & Osherson 2011) — which licenses our
  `sum` and indicts only the normaliser after it.
- **OURS:** `hdlab/binding.py` — FHRR bind = elementwise complex multiply (`:27`); HRR bind =
  circular convolution via **full `fft`/`ifft`** (`:35-37`), unbind by conjugate; BSC bind =
  elementwise multiply (self-inverse); `bsc_bundle:104-105` sum then `sign`, ties → +1.
- **FIDELITY:** **UNSCORABLE** (brain math UNPINNED). Recorded honestly rather than claimed SAME.
  What IS scorable: the per-component complex normaliser costs **20-32% of d′** versus whole-vector
  L2 (near/random d′ 4.843 → 6.030; near/disjoint-random 6.070 → 8.959). Scope: those pairs come from
  the hand-authored lexicon, so this describes what the OPERATION does to whatever structure exists,
  not a capability.
- **WIRED:** YES
- **EVIDENCE:** composition mechanism VET-confirmed 4× **given roles**. **The oracle role-key
  derivation has no mechanistic analog** — the least defensible part of the binding story.
- **BLOCKS:** nothing — it works. Its INPUT (roles from syntax) is the gap; see F3/F4.

**E2 — Situation-model register / event indexing**
- **BRAIN'S MATH:** event-indexing with **prediction-error-driven segmentation** (Zwaan; Zacks &
  Franklin SEM — a boundary is posted when prediction error crosses threshold). **The register's
  update rule is UNPINNED.**
- **OURS:** `hdlab/situation_model_accumulate.py:84-103` — `bound = bind(role_vec, idx_vec[event])`
  bundled into a per-entity register; decode by `unbind` then
  `cleanup_argmax = argmax_v Re(Σ conj(vocab_v)·readback)/d`. `CausalLinkRegister` reuses the identical
  organ with CAUSE/EFFECT keys. `situation_model_multibank.py` routes by **deterministic hash**, not a
  noisy-cue argmax (the code says so explicitly). **No PE signal, no segmentation.**
- **FIDELITY:** RIGHT-OP-WRONG-PLACE / PARTIAL — has the register, has none of the PE-driven
  segmentation that decides *when* to write.
- **WIRED:** YES — and `situation_model_multibank` is live too, **lazily**, from
  `situation_model_accumulate.py:154` inside `make_situation_register`. It is one of only four modules
  the whole live path gains from a lazy import.
- **EVIDENCE:** the closest end-to-end measurement, `exp_situation_model_assembly_encoder_backed_v1`:
  maintenance 0.4625 / coref 0.5825 / overwrite 0.4508 against **floors chance 0.05 and a ref_span
  ceiling 0.98** — verdict **LOCALIZED_WALL**. The two organs it depends on (E1 binding, D5 WM) are
  independently confirmed but **were never run together** before this. **Floored and failing.**
- **BLOCKS:** multi-sentence comprehension — the north-star operation.

**E3 — Coreference: which later mention is which earlier entity**
- **BRAIN'S MATH:** **parallel cue-based content-addressable retrieval, not serial search** —
  retrieval speed is flat across dependency distance; cues combine by **weighted parallel constraint
  satisfaction**, not filter-then-rank; degradation is **similarity-based interference** (a crosstalk
  profile, not a combinatorial search cost) (Lewis & Vasishth 2005; McElree SAT; Jäger, Engelmann &
  Vasishth 2017 meta-analysis). **The cue weights and the activation equation are UNPINNED** — the
  literature gives an ORDERING (agreement > implicit causality > grammatical role > recency >
  coherence relation), not numbers. Centering likewise supplies an **ordering** (subject > object >
  oblique; CONTINUE > RETAIN > SMOOTH-SHIFT > ROUGH-SHIFT), **not arithmetic** (Grosz, Joshi &
  Weinstein 1995). Late-maturing reference-set computation (children over-accept until ~10-11 years)
  motivates a **top1−top2 margin gate with abstention** rather than a forced choice.
- **OURS:** `hdlab/coreference_resolver.py:192` and `hdlab/state_of_mind.py:247` share the arithmetic:
  `salience = count + β·exp(−λ·(now − last_pos))` with **β=0.5, λ=0.1** fixed, window K=5;
  three modes (salience argmax, strict-Cb `argmax over most-recent subject-like clause`, Principle-B
  filter); **abstain if top-2 relative margin < 0.10** (`:90`). NAME/NOMINAL mentions resolved by
  **normalised-token Jaccard**. `hdlab/coref.py:119-120` weights subject mentions 2.0, others 1.0,
  plus a role-parallelism bonus 0.5.
- **FIDELITY:** RIGHT-OP-WRONG-METRIC. **The brain-side source supplies an ORDERING and we invented
  arithmetic on top of it** — fixed β and λ are ours, not the literature's. The margin-gate abstention
  is a genuine fidelity win (it matches reference-set computation). Token Jaccard is not a semantic
  comparator.
- **WIRED:** YES
- **EVIDENCE:** `exp_read_coref_hobbs_centering_resolver_v1` HARD_PASS at **1.000 — on n=10**, with
  floors FULL-vs-OFF (10 vs 0) and NOGATE precision 0.949. **n=10 is not a capability.**
  `exp_extraction_quality_gate_neural_coref_v2` = **NO_GO** against **floors recency 0.5439 and
  singleton 0.4737** on metric `coref_b3_f1`, **n=57**.
  **⚠️ CROSS-RUN CONFLATION CORRECTED (2026-08-14).** Those two floors are real and DO reproduce on
  disk — but they belong to that ONE experiment, on `coref_b3_f1`, and this doc used them as *the*
  floors for the whole organ. **On the run where our own resolver is actually measured
  (`exp_wire_coref_accumulate_situation_model_v1`, identity-demanding query accuracy over 36 McGuffey
  passages), the same-run floors re-aggregate to recency 0.5614 and singleton 0.3860, and our
  resolver scores 0.7193** (earned 0.6842, oracle 0.9298). **So on the only comparison that is
  same-corpus / same-metric / same-run, WE ARE NOT LOSING TO TRIVIAL BASELINES — we are ~0.16 above
  recency and ~0.33 above singleton.** The prior "we lose to pick-the-last-subject" reading came from
  comparing a resolver score in one run against floors from a different run on a different metric,
  propagated one hop from a stale docstring. **Only the 0.5614 / 0.3860 pair may be set beside the
  0.7193.** The real remaining gap is oracle 0.9298 − earned 0.6842.
  The resolver's confidence signals were VET'd at AUC
  0.65-0.75 for predicting **its own errors** — metacognition, not resolution accuracy.
  **Competitive resolution among 2+ semantically plausible antecedents has NEVER been tested at
  scale.**
- **BLOCKS:** multi-sentence comprehension; all of E4.

**E4 — Discourse / bridging inference**
- **BRAIN'S MATH:** causal/elaborative bridging beyond what is stated (Graesser). **UNPINNED.**
  Standing structural insight to obey: causal bridging IS coreference in disguise — hippocampal
  relational antecedent retrieval — so it must **REUSE E3's organ**, not spawn a new one.
- **OURS:** **NONE**
- **FIDELITY:** MISSING — never attempted; not even a negative result exists.
- **EVIDENCE:** the nearest measurements are the `exp_propara_bridging_*` cells (1 HARD_PASS,
  4 HARD_FAIL) against **floors prior_lesion 0.3176 and majority 0.2378**. Those test bridging on a
  benchmark, not our organ. **UNTESTED.**
- **BLOCKS:** inference beyond the literal text. Presupposes E2 + E3; correctly deferred.

**E5 — Theta-gamma multi-item ordered buffer**
- **BRAIN'S MATH:** one theta cycle (~125 ms) contains **~7 gamma sub-cycles (~17 ms each)**, one
  item per gamma slot, order encoded in theta-phase progression (Lisman & Idiart 1995 *Science*
  267:1512; Lisman & Jensen 2013 *Neuron* 77:1002; Heusser 2016 *Nat Neurosci* 19:1374). **The slot
  count and timing are pinned; the ENCODING OPERATION is UNPINNED** — the `Σ perm^k(x_k)` form is
  Kanerva/Plate HDC, i.e. OUR math imported as the analogue, not measured biology.
- **OURS:** `hdlab/situation_focus.py` — `FlatFocus`: `focus = sign(Σ_j bind(pos_key_j, event_j))`,
  unbounded. `ChunkedFocus`: bounded active buffer **capacity=4, fanout=2**; on overflow the oldest
  `fanout` entries compress into a chunk `sign(Σ_k bind(inner_key_k, sub_k))`; retrieval unbinds slot
  key then each chunk level.
- **FIDELITY:** RIGHT-OP-WRONG-METRIC — a bounded ordered buffer with hierarchical chunking is the
  right shape (it is the Cowan-4 mechanism), but capacity 4 vs ~7 slots is a chosen constant, and the
  brain-side encoding operation is UNPINNED so the chunk algebra is ours.
- **WIRED:** NO
- **EVIDENCE:** none floored. **UNTESTED.**
- **BLOCKS:** ordered multi-item maintenance across a sentence.

### F. LANGUAGE STRUCTURE

**F1 — Lexical category (POS)**
- **BRAIN'S MATH:** **UNPINNED.** Posterior temporal lexical access is localised; no equation.
- **OURS:** `hdlab/pos_tagger.py` (110 lines) — a thin feature-template wrapper over
  `hdlab/perceptron.py` (averaged structured perceptron: Viterbi `argmax`, `w[f] += 1` on gold,
  `cw[f] += c` for the running average) + `data/frontend_assets/pos_tagger_ud_ewt_upos.json` (5.3 MB).
- **FIDELITY:** UNSCORABLE. Charter-compliant: our own learned mechanism, not a bolt-on parser.
- **WIRED:** **YES — LAZILY**, inside `StructuralFrontEnd._load` (`reading_grounding_loop.py:300-303`).
  Invisible to grep and to an eager import trace.
- **EVIDENCE:** no floored number surfaced. **UNTESTED here.**
- **BLOCKS:** nothing directly.

**F2 — Dependency / argument-structure parsing**
- **BRAIN'S MATH:** **UNPINNED.** LIFG/pSTS involvement established; the computation is not. The
  pinned part is an ALGORITHM, not a neural operation: X-bar endocentricity realised as a
  hand-written head-percolation priority table (Collins 1999 App. A), constituent pruning reaching
  99.3% recall (Xue & Palmer 2004).
- **OURS:** `hdlab/arc_parser.py` hashed arc-factored scoring, `_decode:149` per-token
  `margin = best − second`, greedy heads + cycle-break; margin is the calibrated abstain signal.
  `hdlab/arc_labeler.py` same perceptron family.
- **FIDELITY:** UNSCORABLE.
- **WIRED:** YES, lazily (same site as F1).
- **EVIDENCE:** `arc_labeler` self-test PASS. **Floor not established in this audit.**
  ⚠ **`arc_parser.py:19`: head/deprel fields are PLACEHOLDERS in `parse()` — only form and upos are
  read at inference.** Any claim resting on our dependency structure needs to check this first.
- **BLOCKS:** verb/role extraction; F3.

**F3 — Thematic role assignment**
- **BRAIN'S MATH:** MacWhinney **Competition Model** — role assignment integrates probabilistic cues
  weighted by cue **VALIDITY** (availability × reliability) against cue **COST**. This is a real,
  pinned equation. Soft re-ranking over survivors uses information-theoretic **selectional
  association** over WordNet classes (Resnik 1996 *Cognition* 61) — which replaced Katz & Fodor's
  hard selectional restrictions precisely because hard gates are brittle to metonymy ("the White
  House announced"); humans **type-coerce** rather than reject. Animacy is an early,
  **verb-INDEPENDENT** prominence cue (Bornkessel-Schlesewsky eADM); **its combination rule is
  UNPINNED.**
- **OURS:** `hdlab/thematic_role_labeler.py:495-499` — count-based cue weights `w[(f,gold)] += 1`,
  `cw[(f,gold)] += c`, then argmax (perceptron family).
- **FIDELITY:** RIGHT-OP-WRONG-METRIC — the competition shape is right; **raw counts are not cue
  validity**, and cue cost is absent entirely.
- **WIRED:** YES
- **EVIDENCE:** modern-revalidated at **+0.267 but ANIMACY-DOMINANT** — one cue doing the work, which
  is exactly what a validity-weighted model would expose. Related floored negative:
  `exp_syntactic_role_agent_patient_voice_probe_v1` scored **0.1792 / 0.1625 against chance 0.50 and
  shuffled controls 0.513/0.529**, verdict `ENCODER_POSITION_ONLY`.
- **BLOCKS:** verb-frame learning (F4).

**F4 — Frame induction / syntactic bootstrapping**
- **BRAIN'S MATH:** syntactic bootstrapping (Gleitman) — the frame constrains the verb's meaning.
  **UNPINNED as an equation.** The adjacent pinned constraint is semantic bootstrapping's **graded,
  not veto** requirement (Grimshaw 1981; Pinker 1984): a hard entity-hood gate reproduces exactly the
  brittleness that killed hard selectional restrictions.
- **OURS:** `hdlab/frame_induction.py` — feature encoder over `hdlab/learner` MDL selection (G1);
  features are hand lists.
- **FIDELITY:** UNSCORABLE brain-side; **FLOORED AND FAILING on its own task.**
- **WIRED:** YES
- **EVIDENCE:** MIDDLE_BAND on real text and **LOSES to a trivial position-majority baseline**:
  0.833 vs **1.000** (subject), 0.455 vs **0.545** (object). **A genuine floor, and we are below it.**
- **BLOCKS:** verb learning — **but the binding constraint is UPSTREAM**: the foundation contains
  **0 genuine verb definitions in 2,092 facts** (66.7% NOUN / 28.0% PROPN / 2.3% VERB; hand
  inspection of the 48 VERB-tagged rows found zero real verb definitions). Wiring this organ harder
  cannot fix a verb population that does not exist.

**F5 — Coherence monitor (the N400 generator)** *(MISSING — and a legitimate PHASE-B target)*
- **BRAIN'S MATH:** N400 amplitude = **the MAGNITUDE OF UPDATE forced on a running probabilistic
  situation-model representation** by the incoming word — i.e. `‖Δ situation_model‖`, a prediction
  error against the **CURRENT discourse state**, not against a fixed template (Rabovsky, Hansen &
  McClelland 2018 *Nat Hum Behav*; Kutas & Federmeier 2011). **The reference point is pinned; the norm
  and the update rule are UNPINNED.** The error is **precision-weighted** — a gain decides whether it
  drives revision at all (**form pinned: precision × error; the precision estimator UNPINNED**). The
  P600 is a **separate discrete structural-incoherence flag** with **no math at all**, and the field
  disputes whether it is a second mechanism or one graded process read two ways.
- **OURS:** **NONE.** No module computes a running-situation-model update magnitude.
  `self_improving_loop.py:88` computes a `top1 − top2` margin delta over FHRR role decodes and adopts
  the max — a *different quantity*, and its own docstring flags that it over-adopts on zero-gain
  margin spikes when event structure is thin. `gap_detector` measures item familiarity, not
  discourse coherence.
- **FIDELITY:** **MISSING.**
- **EVIDENCE:** none. **UNTESTED.**
- **BLOCKS:** knowing when comprehension has failed. **PHASE-B NOTE:** the human baseline here is
  bad — **~40-50% of subjects fail to notice a controlled semantic anomaly** (Barton & Sanford 1993
  *Mem Cogn* 21:477; Erickson & Mattson 1981 Moses illusion), and the undetected error propagates
  into durable memory. An always-on engineered check can **structurally beat** the brain here, not
  merely match it. That is a real Phase-B opportunity — **after** the Phase-A organ exists.

**F6 — Construction-Integration: settling a multi-sentence interpretation** *(MISSING)*
- **BRAIN'S MATH:** Construction spreads activation loosely; Integration is constraint satisfaction:
  **`A(t+1) = normalize(A(t) · W)`** over a proposition-connectivity matrix W built from argument
  overlap and context fit, run a **small fixed number of cycles** — not to a formal energy minimum
  (Kintsch 1988 *Psychol Rev*; 1998). ⚠ **Flagged in the source: the original matrix-update equation
  could not be freshly verified — "recalled/folklore, not freshly re-verified."** Verify before
  building on it. Companion: the Landscape model's coherence-break repair (passive cohort activation
  + active coherence-based retrieval) is **UNPINNED** — no threshold, no search rule.
- **OURS:** **NONE.**
- **FIDELITY:** MISSING.
- **EVIDENCE:** none. **UNTESTED.**
- **BLOCKS:** multi-sentence integration.
- **ACCEPTED SHARED LIMIT, recorded so it is not mistaken for a bug:** garden-path reanalysis is
  partial in humans — thematic roles assigned along the garden path **linger alongside** the corrected
  parse (Christianson, Hollingworth, Halliwell & Ferreira 2001 *Cogn Psychol* 42:368). Bounded-
  iteration constraint satisfaction converges to *a* stable answer, not the *correct* one. That is
  brain-shared and is not to be engineered around in Phase A.

### G. LEARNING AND PLASTICITY

**G1 — The cortical learning rule**
- **BRAIN'S MATH:** **THE LITERATURE BIFURCATES CLEANLY BY WHAT IS BEING LEARNED.**
  *Sensory/perceptual hierarchies:* the backprop-approximation program is live and mathematically
  serious — NGRAD (feedback induces activity differences that locally approximate error signals;
  Lillicrap, Santoro, Marris, Akerman & Hinton 2020 *Nat Rev Neurosci* 21:335); predictive-coding nets
  with purely local Hebbian plasticity **converge to backprop's updates** (Whittington & Bogacz 2017
  *Neural Computation* 29:1229; Millidge 2022); dendritic error (Sacramento, Costa, Bengio & Senn
  NeurIPS 2018) and burst-probability credit assignment (Payeur 2021 *Nat Neurosci* 24:1010).
  *The negative result matters too:* pure local/Hebbian rules **did not beat fixed random projections**
  at large hidden width (Illing, Gerstner & Brea 2019), and target-prop/feedback-alignment degrade
  sharply beyond MNIST (Bartunov 2018).
  *Lexical-semantic acquisition:* **UNPINNED, deliberately.** The literature's own words — the slow
  phase is *"closer to a Hebbian/statistical-learning process operating over replayed samples than to
  literal backpropagated error at encoding time"*; fast phase = one-shot hippocampal binding.
  **No equation is offered for either half.** (And the strong "fast mapping writes directly to cortex"
  alternative has **collapsed under replication** — Warren & Duff 2014; Cooper, Greve & Henson 2019.)
- **OURS:** `hdlab/learner/core.py` — **MDL / Bayesian two-part-code model selection**:
  `entropy_bits`, `null_code_bits`, `:136 best = min(eligible, key=(-compression_ratio, cost_rank))`;
  `per_cluster_gate()` promotes a hypothesis only when it compresses past the null code;
  `glass_box_assert()` refuses a non-inspectable hypothesis. Four plugins (estimation, MDL rule
  induction, GAM, bounded program induction).
  The one place we own a genuine **delta rule** is `hdlab/compose_freq_routing.py:110-111`
  `error = tgt − ctx@Wᵀ; W += lr·(errorᵀ @ ctx)/batch`, with a frequency-routed variant adding an
  antisymmetric STDP term `stdp_w·(outer(tgt,ctx) − outer(ctx,tgt))`. Everything else is pure Hebbian
  (`hdlab/learning.py:68-75`: `delta = arousal · reward; w[pair] += delta` — **reward-gated
  pure-Hebbian, no error term, no normalisation, no LTD**).
- **FIDELITY:** WRONG-OP relative to any named cortical plasticity rule. MDL is a statistical
  model-selection principle, not a synaptic update rule. It may be the right *algorithmic-level*
  description of consolidation; nobody has tested that here.
- **WIRED:** YES (live closure — `hdlab.learner` + 4 plugin entries in `sys.modules`).
  `compose_freq_routing` NO (registry: promoted, **zero consumer**).
- **EVIDENCE:** the module's own docstring: **"THIS IS A REFACTOR. It does not claim any new substrate
  capability."** Acceptance bar was behaviour-preservation against two prior cells. **UNTESTED as a
  learning organ.**
- **BLOCKS:** everything about growth. This is the organ the whole read-and-learn thesis rests on and
  it has never been measured as a learner.

**G2 — Prediction error / surprise gating of plasticity**
- **BRAIN'S MATH:** hierarchical predictive coding — the residual `x − x̂` is the learning signal
  (Rao & Ballard 1999; Friston), **precision-weighted** so that low-precision errors are suppressed.
- **OURS:** `hdlab/predictive_coding.py:49-86` — `predict = sign(W @ key)`;
  `residual = observed − predicted ∈ {−2,0,+2}`; ⚠ **`residual_magnitude = 0.5·(1 − cos(obs,pred))`,
  a COSINE-derived scalar, not the L2 of the residual the docstring implies.**
  `threshold_gate:117` writes iff mag ≥ τ with binary strength; `relative_threshold_gate:176-177`
  fires iff `mag/running_avg ≥ τ`, running average `decay·new + (1−decay)·prev`;
  `:237 W += write_strength · outer(value, key)`.
- **FIDELITY:** RIGHT-OP-WRONG-METRIC — the residual-gated Hebbian shape is exactly the brain's, but
  the residual is computed on a `sign()`-quantised prediction, so a large graded error and a small one
  that flips the same bits are indistinguishable. No precision term.
- **WIRED:** **NO**
- **EVIDENCE:** self-test PASS (asserts the vanilla path matches the outer-product sum). **NO FLOOR —
  UNTESTED.**
- **BLOCKS:** selective consolidation (D4/D9); efficient learning.

**G3 — Neuromodulatory gain**
- **BRAIN'S MATH:** ACh/NE apply **multiplicative gain** to cortical responsivity. **The form is
  pinned; the setpoint control law is UNPINNED.**
- **OURS:** `hdlab/modulators.py` — **five named global SCALARS** (attention, reward, arousal,
  recency, gating), a module-level state holder. Only three live consumers: `bundling.bundle`
  (recency → geometric decay `w_i = (1−recency)^(k−1−i)`), `memory.Codebook.lookup:65-69` (attention
  used as a **hard cutoff** — `return name if score >= attention else None`, not a gain), and
  `learning.update` (arousal × reward as a scalar delta).
  `hdlab/excitability.py` applies `W[mask,:] *= scale` — real multiplicative gain, on rows, offline.
- **FIDELITY:** RIGHT-OP-WRONG-PLACE. Gain is the right operation; ours is a **global scalar on
  bundling recency plus a hard threshold on lookup**, not a per-dimension task-driven gain on the
  representation. **This is precisely the organ C3 needs and cannot currently reuse.**
- **WIRED:** `modulators` YES; `excitability` **NO** (ISLAND, zero consumer).
- **EVIDENCE:** none floored. **UNTESTED.**
- **BLOCKS:** C3's brain-faithful form as a *reuse* rather than a new build.
- **🔑 WHAT THE DECORRELATION DRILL ADDED (2026-08-14) — the reason four reweightings failed.**
  **Whitening IS per-dimension gain, but IN THE RIGHT BASIS.** That single qualifier is exactly what
  our four failed reweighting attempts lacked: every one of them applied a gain **per raw dimension**,
  in the basis the vectors happen to arrive in, which is not the basis in which the correlation lives.
  A per-dimension gain in the wrong basis cannot decorrelate anything — it rescales axes that were
  never the axes of the redundancy. This reclassifies those four negatives: they are **wrong-basis
  implementations, NOT evidence that gain-based decorrelation fails.**
  ~~**Measured on our own code: a 58% COMMON MODE.** More than half the variance is a single shared
  direction every vector carries.~~
  🔴 **CORRECTED 2026-08-14 — THIS PREMISE DOES NOT REPRODUCE, AND IT MIXED TWO QUANTITIES.**
  Measured on the live anchor field (n=2377, d=256,
  `data/exp_rank1_common_mode_removal_v1/metrics.json` `common_mode_measured`): using the SAME
  definition this row quoted, `||mean_i a_i|| / mean_i ||a_i||` = **0.3650 GRADED / 0.2997 SIGN** —
  the sign figure is HALF the claimed 0.5841. And **that definition is a NORM RATIO, not a variance
  fraction**: the actual shared-direction energy fraction is **0.1535**, and **PC1 holds 0.0350** of
  the centred field's variance. So "more than half the variance is one direction" overstates the
  measured quantity by roughly **4x**. (The 0.5841 came from
  `experiments/diag_anchor_field_geometry_v1.py` on a different, smaller field — 400 concepts x 70
  held-out sentences — so the gap is partly scope and partly the definition swap.)
  **The right-basis REASONING above still stands; the MAGNITUDE that made it look urgent does not**
  — and the removal was tried and had **no effect** (`exp_rank1_common_mode_removal_v1`,
  `34b94e8bc`: accuracy 0.6980 → 0.6985, CI includes 0, and a RANDOM rank-1 direction moved it
  identically). See `notes/STATUS_LESSONS.md` CORRECTION C11.
  **What is estimable at our scale, and what is not — this is the whole build decision.**
  **Rank-1 mean removal IS estimable** at `d = 256..4096` with the sample counts we have: one
  direction needs `O(d)` samples. **FULL covariance whitening is NOT** — it needs `O(d²)` samples
  (65k to 16M) that we do not have, so an estimated full covariance would be dominated by its own
  estimation noise and would *add* variance rather than remove it. **So the licensed step is
  rank-1 (remove the common mode), and full-covariance whitening is PARKED-BY-SAMPLE-SIZE with the
  crossover stated as `O(d²)` samples.** Do not queue full whitening; do not read the four prior
  nulls as closing the question.

**G4 — Basal ganglia: Go/NoGo action selection**
- **BRAIN'S MATH:** WTA disinhibition over Go/NoGo pathways; TD learning with bootstrapped value.
- **OURS:** `hdlab/action_selection.py:125-172` — Hebbian operator `W = (Sᵀ @ O)/n`;
  TD `pred = E_cur @ M`, `target = E_next + γ·(E_next @ M)`; adaptive LR from
  `ratio = ‖e‖/median(‖e‖)` clipped; gate = `argmax_i Go_i`.
- **FIDELITY:** **SAME** op-class.
- **WIRED:** NO
- **EVIDENCE:** the docstring records honest decay — **gonogo 0.653 @ depth 4 → 0.075 @ depth 6.**
  That is a self-reported failure profile, not a floored capability. **PARTIALLY FLOORED.**
- **BLOCKS:** nothing today.

### H. METACOGNITION, FORAGING, AND THE STORE

**H1 — Perirhinal familiarity: "do I already know this?"**
- **BRAIN'S MATH:** a fast, graded, **single-dimensional strength signal** available BEFORE
  recollection completes, compared against a criterion (dual-process/SDT). **The criterion-setting
  rule is UNPINNED; the SHAPE is pinned.**
- **OURS:** `hdlab/gap_detector.py:92-191` — run `cleanup_family.iterative_attractor` (temp default
  **8.0**) to pick a winner, then compute the margin from the **UNTOUCHED RAW QUERY**:
  `:117 margin = dot(q_raw, cb[best]) / (‖q‖·‖cb‖)`, deliberately *not* the attractor's settled
  state; `:191 is_gap = margin < floor`. Exact match ⇒ 1.0, shared-2-of-3 ⇒ ~0.5, novel ⇒ noise floor.
- **FIDELITY:** **SAME.** A graded strength read *before* settling, compared to a criterion, is the
  brain's shape — and the module states the design reason explicitly.
- **WIRED:** YES
- **EVIDENCE:** registry `gap_detector_familiarity_gate` = `validated_hard_pass_signal_detection_2026-08-12`;
  the module carries an **ABLATION CONTROL** (the ablated arm replaces the margin with
  `uniform(−1,1)`). `exp_gap_detection_autonomous_confidence_v1`: **AUC 1.000, d′ 5.15**, against
  **floors prereg 0.625, chance 0.50, lesion arm n=40**. **FLOORED AND PASSING — the healthiest organ
  in the map.** Honest caveat: a perfect 1.000 on synthetic probes is suspect-1.000 territory; the
  ablation is real but the items are not real text.
- **BLOCKS:** nothing. **Its output has nowhere to go — see H2. That is the tragedy of this row.**

**H2 — Information foraging: deciding WHAT TO READ NEXT** *(MISSING — and it is step 1)*
- **BRAIN'S MATH:** **UNPINNED.** Candidates exist (LC-NE gain/exploration; dopaminergic
  information-seeking; curiosity as expected information gain) but there is no settled cortical
  equation for "choose the next source given what you don't know." **This is a real gap in the
  literature, not in our reading of it.**
- **OURS:** **NONE.** `hdlab/gap_driven_reader.py:192-200` `rank_material()` exists but is, in its own
  docstring's words, *"intentionally target-agnostic"* — it ranks **only what the caller hands it**.
  Repo-wide there are **zero occurrences** of `select_corpus` / `choose_corpus` / `next_corpus` /
  `pick_corpus` / `corpus_selection` / `corpus_scheduler`. The readable universe is a **hard-coded
  4-entry dict** (`experiments/exp_reading_grounding_loop_cycle2_v1.py:132-137`) plus a `--segment`
  CLI arg, while **`data/corpora/` holds 36 entries** (verified this pass: agreement,
  alice_in_wonderland, arc, base_vocabulary, binder, graded_readers_*, litbank_*, mcguffey_*,
  mcscript2, onestop, openstax_common, process_articles_v1, race, **simplewiki**, social_iqa, six
  OpenStax textbooks, ud_english_ewt, wiqa, worldtree, …). The 251 MB `simplewiki` has been on disk
  since 2026-07-28 and **is already read by a different arc**.
- **FIDELITY:** **MISSING.**
- **WIRED:** **NO.** `gap_driven_reader` has **zero `hdlab/` importers**; its single importer repo-wide
  is one experiment cell.
- **EVIDENCE:** `exp_gap_driven_reader_controlled_v1` = **HARD_PASS**, prereq precision 1.0 against
  **floors ablated 0.0, random baseline 0.125, theoretical chance 0.1667** — **but n_trials = 8, and
  the caller builds 4 synthetic f-string pseudoword templates per trial. The organ has never seen real
  text.** A PASS on synthetic templates is not a floor for corpus selection. **UNTESTED where it
  matters.**
- **BLOCKS:** **ALL self-directed growth.** The loop notices individual *words* it does not know, but
  only among words already in front of it. Measured consequence: **64.5% of every definitional fact
  the substrate has ever produced came from one segment** (`bio_new`, 1,118 of 1,734 distinct terms);
  11,122 refusals over 3,689 distinct lemmas and 10,296 pending items are persisted **and tagged by
  segment** — and **no code anywhere performs the group-by that would make the imbalance visible.**

**H3 — Refusal / confidence gate**
- **BRAIN'S MATH:** metacognitive criterion-setting on a graded evidence variable (SDT). Form pinned;
  **how the criterion is SET is UNPINNED.**
- **OURS:** `reading_grounding_loop.py::_make_grounding_gate:1102` threshold on accumulated-context
  cosine with explicit refusal reasons (`TAUTOLOGY_NO_ANCHOR`, closed-class/low-information filters);
  `hdlab/refuse_gate.py` calibrates τ over every unique calibration score;
  `hdlab/clarify_gate.py:84-85,157` three-band REFUSE / CLARIFY / ACCEPT with clarify_τ = the **10th
  percentile of ambiguous scores**; `hdlab/conformal.py:52-53` split-conformal quantile
  `q = sorted(scores)[⌈(n+1)(1−α)⌉−1]` (the one statistically principled criterion we own).
- **FIDELITY:** RIGHT-OP-WRONG-METRIC — shape is right; the criteria are percentile heuristics except
  in `conformal.py`, which is not wired to the grounding gate.
- **WIRED:** the grounding gate YES; `low_information_filter`, `refuse_gate`, `clarify_gate`,
  `conformal` NO.
- **EVIDENCE:** the gate demonstrably FIRES (11,122 refusals persisted, 7 fields, 100% populated).
  **There is no measurement of whether it refuses the RIGHT things — no floor on refusal correctness.**
  And `state.refusals` is written, counted, reloaded — **and then never consulted by any decision.**
  ⚠ `low_information_filter.py:57,104`: `df_threshold` is explicitly `REPORTED_ONLY -- never a gate`
  — a knob that looks live and is inert.
- **BLOCKS:** nothing directly. A working detector whose output is discarded.

**S1 — Semantic long-term store: write and glass-box read-back**
- **BRAIN'S MATH:** distributed cortical semantic memory; graded synaptic weight distribution.
  **No equation for the store as an addressable object — UNPINNED.** This is arguably a substrate
  engineering organ with no single brain counterpart, and is labelled so.
- **OURS:** `hdlab/hd_fact_store.py:229` —
  `acc += bipolar_bind(role_key(r), sym_vec(filler))` over {REL, ARG0, ARG1, SOURCE, TRUST}, then
  `sign()`. Recovery `:209-210 scores = codebook @ filler_hat; j = argmax` — **cleanup restricted to a
  per-domain codebook, which is the only thing preventing cross-field argmax collisions.** Genuinely
  glass-box: every field, including provenance and trust, recovers by role-query unbind.
- **FIDELITY:** RIGHT-OP-WRONG-METRIC — the fourth prototype operator; the quantiser again.
- **WIRED:** YES
- **EVIDENCE — the plumbing is proven and the meaning is not.**
  Of 3,544 `GROUNDED_MEANING` facts, **2,328 (65.7%) are self-referential tautologies
  `(X, GROUNDED_MEANING, X)`**; the substantive cross-grounded set is 1,216, of which roughly 35%
  meaningful / 25% related / 40% noise by hand audit. The original foundation-validation claim was
  **CIRCULAR** — the grounding target is *selected* by cosine over same-sentence context, then *tested*
  for co-occurrence in that same text; **claim2b and the claim3 ablation cannot fail by construction.**
  ⚠ Two capacity results on this store have **NO FLOOR AT ALL**: `cell4_results` reports
  **recall@1 = 1.0000 at 100,000 facts, HARD_PASS**, with no random-key arm, no scramble, no decoy —
  and a noise sweep 0.05-0.5 that returns 1.0 at every level, i.e. **the sweep never bit**; and
  `exp_hd_fact_store_source_trust_vet_v1` reports **1.000/1.000/1.000, verdict PASS**, no floor.
- **BLOCKS:** every claim that rests on "the foundation knows N things."

---

## 5. THE KNOWN-DEFECT REGISTER

Found while reading the code for this map. None is a hypothesis; each is a line you can open.

| # | site | defect |
|---|---|---|
| 1 | `hdlab/working_memory.py` | **Contains zero WM mechanism** — two assertion guards + constants. Any claim citing it as the WM organ is misattributed. |
| 2 | `hdlab/multi_hop.py:88-96` | Default **β = n_dim** makes the "soft Modern-Hopfield" softmax a **Dirac delta ⇒ identical to hard argmax**. The code records that **two prior cells were confounded by this.** |
| 3 | `hdlab/atoms.py:54,61` | `similarity()` silently returns **two different metrics**: `/n` for FHRR, true cosine for HRR. **Any cross-dtype threshold comparison is unsound.** |
| 4 | `hdlab/metrics.py:34-35` | `capacity_curve` is a live `raise NotImplementedError("Week 7")` stub. |
| 5 | `hdlab/arc_parser.py:19` | head/deprel fields are **placeholders at inference**; only form and upos are read. |
| 6 | `hdlab/low_information_filter.py:57,104` | `df_threshold` is `REPORTED_ONLY -- never a gate` — an inert knob that reads as live. |
| 7 | `hdlab/layer_075_structural_slot_filter.py` | The "filter" is `(hop1 ++ hop2)[:k_final]` — a **truncation**, not a filter. |
| 8 | `hdlab/predictive_coding.py:84-86` | `residual_magnitude` is `0.5·(1 − cos)`, **not** the L2 of the residual the docstring implies. |
| 9 | `hdlab/_scratch_orig_goal_owner_select.py` | 889-line **stale duplicate** of `goal_owner_select.py`; self-test still passes; zero consumers; registry says delete-candidate. |
| 10 | `data/exp_propara_process_keyed_lookup_v1/metrics.json` | `verdict: "HARD_PASS"` while `verdict_msg: "SELFTEST_PASS"` and `run_mode: "self_test"`. **A self-test banked under a result verdict** — it inflates every HARD_PASS count. |
| 11 | `data/cell4_results/metrics.json` | recall@1 = **1.0000** at 100k facts, HARD_PASS, **no comparator of any kind**. |
| 12 | ~30 `exp_substrate_*capacity*` cells (2026-07-03) | HARD_PASS with **no numeric floor key**; spot-checked ones compare only against themselves. **The bulk of the 296 HARD_PASS count and the weakest-evidenced block in the archive.** |
| 13 | `data/exp_reading_grounding_loop_cycle3_groundingfix_v1` | Reports `B1_tautology_rate = 0.6569` — the number that demolished the "3,544 grounded concepts" claim — **with no floor in metrics**; the refutation lives in notes, not in the cell. |
| 14 | corpus defect | `base_vocabulary` loads as **one 74,288-word pseudo-sentence**. Direction of the resulting bias runs *against* the claim it affected, but it is a real defect. |
| 15 | `hdlab/situation_reader.py:108` | `_INDUCED_SUBJ_NAME, _INDUCED_SUBJ_HYP = get_induced_subj_hypothesis()` runs a **full frame-induction training at IMPORT time**, deliberately (comment at :100-107). **Importing this module costs 205 seconds** (190 s in the module body). Anything that imports it pays 3.5 minutes, and it is why two prior census sweeps appeared to hang. |
| 16 | `hdlab/harness.py` | Executes **self-tests as an import side-effect** — `import hdlab.harness` prints `[SELFTEST PASS] …` lines and three env warnings. Not an error, but the module is not side-effect free. |
| 17 | `hdlab/situation_reader.py` | Imports from `experiments._temporal_ordering`, `_temporal_ordering_multiframe`, `_causal_network` — **an `hdlab/` module depends on `experiments/`**, so the repo root must be on `sys.path`, not just the package. That is a layering inversion. |

**The perfect-1.000 cluster, flagged as a class:** `gap_detection` AUC 1.000, `gap_driven_reader`
precision 1.000 (n=8), `coref_hobbs` 1.000 (n=10), `foundation_validation` claim3 1.000/scramble
0.000/ablation 0.000, `propara_*` decode fidelity 1.000, `cell4` recall 1.000. **The
foundation-validation landed-VET proved two of its 1.000/0.000 arms cannot fail by construction. The
same suspicion is unretired for the others.**

---

## 6. THE PLAN — SEQUENCED BUILD ORDER

Ranked by **(blocks the most) × (worst fidelity) × (we already own something to reuse)**.
**Every step below is PHASE A.**

### STEP 1 — H2, INFORMATION FORAGING. *Independent. Start now, parallel with steps 2 and 4.*
- **Organ:** deciding what to read next given what you don't know.
- **Fidelity fix:** MISSING, so this is BUILD + WIRE, not repair. Three connections:
  (a) a `CORPUS_REGISTRY: Dict[str, Callable[[], Sequence[str]]]` enumerating `data/corpora/` — *the
  shelf*, which exists nowhere (~15 lines); (b) call the already-HARD_PASS
  `gap_driven_reader.rank_material()` with candidates from that registry instead of the synthetic
  dict — **a call site, not new code**; (c) a driver binding `state.refusals` / `library_pending` →
  `next_read_target()` → `rank_material()` → the chosen loader (~60-100 lines).
  A **cheap prerequisite detector** ships alongside: add
  `Counter(r["segment"] for r in state.refusals)` and the matching `grounded_by_segment` to the
  growth-curve dict `checkpoint()` already assembles at `reading_grounding_loop.py:1396-1400`. ~6
  lines, one call site, and it makes the 64.5% skew a persisted first-class field instead of an ad-hoc
  query nobody ran for 16 days. **That is a detector, not a fix — say so.**
- **CAN-FAIL TEST:** seed the loop with the current foundation (64.5% biology). Let it choose its next
  corpus from the 36 for N cycles. Measure the share of newly-grounded terms that are EVERYDAY
  (non-biology) vocabulary.
- **FLOOR — two arms, both must be beaten:** (i) **RANDOM corpus choice** over the same 36 — if
  gap-ranked selection cannot beat a coin flip, the organ adds nothing, and this is the arm that kills
  it; (ii) the **FROZEN 4-entry schedule**, which produced the 64.5% / 1,118-term skew. Report per-arm
  CIs and the seed count.
- **Why first:** worst fidelity (MISSING), blocks the largest capability class, and we own every part
  except the shelf. Cheapest failure mode in the plan.
- **Honest caveat:** the brain math here is **UNPINNED**, so this step reaches *function* parity, not
  *equation* parity. State that in the writeup.

### STEP 2 — B4, REPRESENTATION FORMAT AND CAPACITY. *Independent. Strictly before step 3.*
- **Fidelity fix:** make the live path GRADED (`context_vector(graded=True)`,
  `ConceptSpace.freeze_graded()`, `ReadoutConfig(graded_query=True)` — all three already landed, all
  three **default OFF**) and raise `D` from 256.
- **CAN-FAIL TEST:** held-out near-neighbour 2AFC **on the live path, not on a probe** — full anchor
  set, graded field + graded query, at d=1024, with d=4096 as a labelled no-verdict-weight diagnostic,
  against the live d=256 quantised baseline of **0.6395**.
- **FLOOR:** scrambled-context floor **measured in-cell** (must land 0.49-0.51; prior cells give
  0.4975 / 0.5065 / 0.49775 / 0.5095), frequency baseline **0.4800**, chance **0.50**.
  **MANDATORY:** report the **between-projection-draw sd** next to the CI (0.0090 at d=256). Item
  bootstraps are blind to shared-randomness variance; every cell built on a random projection must
  report it.
- **How it can fail:** if the gain does not survive the full anchor population (2,377+ concepts vs the
  probe's 400), or if memory/latency at d=4096 makes it unusable as a default, the answer is "capacity
  is a probe result, not a live capability."
- **Honest caveat, up front:** at PROBE scale this is already measured (0.7030 sign@1024; 0.78225
  graded@4096). **This is a WIRE-IT test, not a discovery.** Do not report a re-measurement of a known
  effect as a new finding.

### STEP 3 — B1/B2, WHAT THE CONTEXT VECTOR CONTAINS. *Strictly after step 2.*
- **The finding this attacks:** the FAR−NEAR gap is **capacity-INDEPENDENT** — flat to slightly
  growing across a 16× capacity range, CI excludes 0 at every d, **6× the between-projection-draw sd**.
  And at d=4096 FAR accuracy is only 0.8365: **for 16.4% of items the context cue does not identify
  its target even against an UNRELATED distractor.** The comparator's arithmetic is no longer the
  binding constraint; **what the context vector CONTAINS is.**
- **Fidelity fix:** the brain's hub pools **SPOKE (feature) inputs**; ours pools **co-occurring word
  identities**. The literature is unusually direct here: symmetric co-occurrence **cannot** separate
  synonymy from antonymy from co-hyponymy (same frame: "the water is hot/cold"); SGNS is provably
  implicit factorisation of a shifted-PMI matrix, so trained-vs-count is not the axis; and on
  SimLex-999 (human IAA 0.67) what closes the gap is **injecting explicit relational structure** —
  GloVe 0.41 → retrofitting 0.53 → **counter-fitting 0.58**; Paragram-SL999 0.69 → retrofitting 0.68
  (no gain) → **counter-fitting 0.74** (Levy & Goldberg 2014; Levy, Goldberg & Dagan 2015 *TACL*
  3:211; Mrkšić et al. 2016 Table 2). **Counter-fitting — pushing known non-synonyms apart — is the
  lever, and it is not a training-scale lever.**
  Owned and unused: `hdlab/random_indexing.py:219`'s order-sensitive cyclic-shift variant.
- **CAN-FAIL TEST:** change the context vector's CONTENT (structured/relational features) while
  holding its arithmetic and the 2AFC harness fixed, at the d chosen in step 2. Require the
  capacity-independent NEAR/FAR gap to shrink **below the lower bound of its current CI**
  (gap 0.0543 at d=4096, CI [0.0413, 0.0685]).
- **FLOOR:** the unchanged bag-of-words arm at matched d, plus the in-cell scrambled-context floor.
  One variable: content only.
- **Why strictly after step 2:** without a d where capacity is not the limiter, a content effect and a
  capacity effect are confounded — **exactly the mistake this program already made once.**

### STEP 4 — E3, COREFERENCE AS COMPETITIVE RETRIEVAL. *Independent. Parallel with steps 1 and 2.*
- **Fidelity fix:** the brain-side source supplies an **ORDERING**, and we invented arithmetic on top
  of it (fixed β=0.5, λ=0.1). Replace it with genuine **parallel cue-based retrieval with
  similarity-based interference**, scored by the semantic comparator rather than token Jaccard. Keep
  and strengthen the existing **top1−top2 margin abstention** — that part is already brain-faithful
  (reference-set computation). Reuse the resolver's existing confidence signals as the graded evidence
  variable rather than building a new organ.
- **CAN-FAIL TEST:** accuracy resolving a pronoun / definite NP among **≥2 semantically plausible**
  candidate antecedents, on real text, at n in the hundreds — **not n=10.**
- **FLOOR — ⚠️ CORRECTED; USE THE SAME-RUN PAIR.** **most-recent-mention (0.5614)** and
  **singleton/subject-position-majority (0.3860)**, as re-aggregated from
  `exp_wire_coref_accumulate_situation_model_v1` — the run that also measures our resolver, on the
  same 36-passage McGuffey corpus and the same identity-demanding query metric. **Our resolver is at
  0.7193 there, i.e. ABOVE both floors.** The previously-quoted pair (recency 0.5439 / singleton
  0.4737) is real but comes from `exp_extraction_quality_gate_neural_coref_v2` on `coref_b3_f1`, n=57
  — a **different corpus, metric and run**, and must not be placed beside a situation-model score.
  Both floors remain trivial and remain worth beating by a margin — `frame_induction` already **lost**
  to a position-majority baseline (0.833 vs 1.000), so the hazard class is live. But the honest
  statement of the gap is now **oracle 0.9298 vs earned 0.6842**, not "we lose to pick-the-last-subject".
  **This step is therefore a WIDEN-THE-MARGIN step on a working organ, not a rescue.**
- **Why fourth and not later:** genuinely untouched, textbook-necessary, and it is the wall the E2
  assembly hits organically (E2 measured coref at 0.5825 against chance 0.05 with a 0.98 ceiling —
  `LOCALIZED_WALL`). Its *metric* improves once 2-3 land; its *build* does not depend on them.

### STEP 5 — D8 + D4, MEMORY LIFETIME AND REPLAY SCHEDULE. *After step 1. Two arms, not one.*
- **Organ:** sleep — making new learning stick without destroying old learning.
- **Fidelity fix, and note this is the ONE place in the plan where the brain's equation is fully
  pinned and we have literally none of it.** Two separable deficits:
  - **D8, the synapse. 🅿️ PARKED-BY-SCALE — see the crossover note in the D8 organ entry.** Every
    store we own is single-state `W += outer(v,k)`. The brain's is a **cascade**: two transition
    families both `~2^-d`, the plastic one resetting depth to 1 in the opposite cascade, giving
    power-law forgetting `t^-1` and **capacity ~√N** (Fusi, Drew & Abbott 2005); or **Benna-Fusi
    2016's** geometric τ chain, `SNR(t) ~ √N·e^(-t/T)/(√t·√(log T))`, which is where **`~N`** comes
    from. **The cascade only beats simpler multistate models above ~1e6 synapses; we run
    `d = 256..4096`. A negative here is the PUBLISHED PREDICTION.** This step is therefore NOT
    queued as a capacity win — if run, it is run to confirm the predicted null AND the predicted
    initial-SNR COST (`1/n`, `1/√m`), which is the only part observable at our scale.
    **A consolidation schedule on a single-state synapse still cannot buy what a multi-timescale
    synapse buys for free — that claim survives the correction, and it is the reason the organ stays
    on the map rather than being deleted.**
  - **D4, the schedule.** The live loop's single averaging op per cycle is the wrong operation class.
    The faithful version is owned and islanded (`continual.py` forward + reverse-orientation replay).
    The pinned biology to add, **restated after the drill's corrections**: replay is **selective at
    the EVENT level** (large-SWR subset only), not uniform — **replay COUNT is a free parameter to
    sweep, NOT the "1-3 times" this doc previously asserted unsourced**; schedule arms should include
    Landauer & Bjork's **actual** `0,3,10` / `1,4,10` against uniform `(1,1,1)` / `(5,5,5)` /
    `~(10,10,10)`, with **expanding treated as a HYPOTHESIS, not a law** (contested at long retention
    intervals by Karpicke & Roediger 2007); and **only reverse replay scales with reward**
    (Ambrose, Pfeiffer & Foster 2016, *not* Foster & Wilson 2006). The **selection function stays
    UNPINNED** and is blocked on organ D7 for the one normative candidate (Mattar & Daw 2018).
- **CAN-FAIL TEST:** interleaved OLD-vs-NEW retention on real text — after ingesting N new corpora
  (which step 1 makes possible), measure retention of held-out facts from the ORIGINAL foundation
  alongside acquisition of the new ones.
- **FLOOR:** (i) the current `checkpoint()` single-averaging arm; (ii) a no-replay arm; (iii) the
  already-measured `exp_cls_interleaved_replay_consolidation_pilot_v1` floors **naive_dual_w 0.217 /
  single_seq 0.217** against `full_cls 0.808`, 3/3 seeds — a real failable floor that already exists
  and is not wired. **Averaging cannot pass an interleaved-retention test**; that asymmetry is what
  lets the test fail informatively.
- **ONE VARIABLE — ⚠️ THE ORIGINAL SEPARATION WAS ONLY PARTLY SAFE.** Run D8 (synapse) and D4
  (schedule) as **separate arms**; the pinned prediction differs — the cascade should change the
  *SHAPE* of forgetting (power-law vs exponential), the schedule should change the *LEVEL*. That
  framing is confirmed correct by the drill (§4.2). **But the confound is worse than this doc said:
  the SPACING EFFECT is produced by the SYNAPSE ALONE** (Benna-Fusi Fig 7c, an inverted-U in
  inter-repetition interval, with no schedule machinery present at all). So a cascade-only arm run on
  a non-uniform ingest schedule **already shows schedule-like effects**, and a schedule arm run on a
  single-state synapse **cannot show the inverted U at all**. **To keep one variable: the cascade-only
  arm MUST be run at FIXED, UNIFORM inter-repetition spacing, or the two organs must be run as a full
  2×2.** Otherwise the confound runs in the direction that FLATTERS the schedule — i.e. it manufactures
  a false positive for the cheaper organ.
- **Why after step 1:** interleaved retention is untestable without a stream of genuinely new material
  to forget. Today the loop reads the same 4 segments forever.

### ORDERING SUMMARY

```
  STEP 1 (foraging)  ─────────────────────────►  STEP 5 (synapse + replay)
  STEP 4 (coreference)          [independent]
  STEP 2 (capacity)  ───►  STEP 3 (context content)
```
- **Parallelisable now:** 1, 2 and 4 are mutually independent.
- **Strictly ordered:** 2 → 3 (confound). 1 → 5 (nothing new to forget otherwise).
- **NOT scheduled, with reasons:** **C4 settling** — declined on fidelity grounds; it would *worsen*
  the target metric. **C3 control gain** — blocked behind step 2, and its HARD_FAIL's own mechanism
  points at step 2. **E4 discourse** — presupposes E2 + E3. **D7 successor representation** — fully
  pinned and entirely missing, but it serves multi-hop reasoning, which is not on the critical path
  until the foundation carries meaning; **queue it as step 6.** **F5/F6** — queue behind step 4.

### PHASE B — SUPERCHARGE. NOT STARTED.
Recorded so it is not started by accident. Two legitimate targets are visible:
- **Capacity.** Cortex cannot re-dimension itself; we can run d=4096. But raising `d` is currently
  *masking* Phase-A questions (it is why a capacity effect read as a quantisation effect), so it
  **enters Phase A as step 2 and does not count as Phase B.**
- **The coherence monitor (F5).** Humans miss **40-50%** of controlled semantic anomalies and the
  undetected error propagates into durable memory. An always-on check can structurally beat that. But
  F5 does not exist yet, so this is Phase B **after** the Phase-A organ is built and floored.

**No organ enters Phase B until its Phase-A parity is measured against a floor. On today's map that
is 5 organs of 38, and three of those five are not wired.**

---

## 7. WHAT `component_brain_fidelity_ledger.md` GOT RIGHT — AND WHY THIS DOC REPLACES IT

**Right, and carried forward:**
- The core judging shift: **each component is gated on the BRAIN'S metric for that component, not on
  a downstream task win.** A faithful build that loses only a downstream task is KEPT (composition
  problem, not component problem). Preserved verbatim.
- The FORMALIZE sequence: deep-brain analysis → comparison on SHAPE + POSITION + METRIC → name the gap
  → brain-accurate can-fail cell → VET → integration checkpoint.
- **Faithful parts do not auto-compose** — assembly is its own phase with its own criteria. Its
  identification of the *assembly* gap (binding and WM proven separately, never run together) was
  right, and the assembly cell has since been run: `LOCALIZED_WALL` (E2). Prediction confirmed.
- Its call that coreference was completely untouched. Still true; it is step 4.
- Its explicit lurking alternative — experience-poverty rather than mechanism. Retained; **step 1 is
  in effect the test of it.**

**Why it is superseded:**
1. **It named components, not equations.** Its brain column says things like *"CA3 attractor /
   pattern-completion; additive multi-constraint satisfaction"*. That is a label, not an operation.
   The unit of work is the equation — that is the whole point of the USER's framing, and it is what
   produced this session's one real win.
2. **It scored fidelity where the brain math is UNPINNED**, e.g. rating BINDING "PARTIAL" when the
   brain's binding equation is contested three ways. This doc marks those UNSCORABLE.
3. **It had no WIRED column decided by runtime**, so it could not have caught that
   `hdlab/working_memory.py` contains no working memory, that the DG pattern-separation organ has zero
   importers, that `multi_hop`'s soft readout is a Dirac delta, or that the reading loop cannot address
   32 of 36 corpora.
4. **Its evidence column carried verdicts without floors** ("+0.44 forward structure", "0.56-0.63
   band"). Several of its statuses rest on numbers whose floors are not recorded.
5. **It missed seven organs entirely** — successor representation, cascade synapse, synaptic tag and
   capture, theta-gamma buffer, coherence monitor, construction-integration, information foraging.
   **Three of those seven have FULLY PINNED equations and no implementation**, which is the highest-
   value combination on the map and was invisible to a component-level ledger.
6. **Its status tally is now wrong in specific ways.** It reported REASONING as FAITHFUL (banked) —
   the reasoner is since registered `built_2026-07-25_then_abandoned_2026-07-27`, gate SHELVE, **a
   disclosed dead end**, and it TIMES OUT at 180 s on its own self-test. It reported FOUNDATION as
   FAITHFUL-for-role — 65.7% of its grounded facts are tautologies.

---

## 8. DISCLOSURES

- **Right file / right version:** all line numbers read at HEAD on branch
  `dataprep/mcguffey-graded-corpus`, from the cited absolute paths, read directly — not grepped.
  `hdlab/` is clean vs HEAD (`git status --porcelain -- hdlab/` empty), so file contents are HEAD
  contents.
- **Right environment:** `D:/AI/hd-instrument/.venv/Scripts/python.exe` for every measurement. Bare
  `python` on PATH is 3.12.10 and lacks `duckdb`; any audit using it produces false collection errors.
- **Right metric / right arm:** every accuracy quoted is copied from the cell's own `metrics.json`
  `verdict_msg`, with the floor from the same string. Where a number has no floor in its source, this
  doc says NO FLOOR rather than quoting it as evidence.
- **Enumeration order:** filesystem first (`os.walk` over `hdlab/` = 155 `.py`), registry reconciled
  afterwards. The registry has 124 rows; `pipeline_status` = `WIRED_BUT_NOT_PIPELINE_REACHABLE` 57 /
  `N_A` 55 / `WIRED_AND_PIPELINE_USED` 11 / missing 1, and it is known wrong in both directions.
- **Provenance of the brain column:** the five `lit_scan_*_2026-08-13.md` files carry their own
  header — *"VERBATIM sub-agent output... NOT re-derived, re-summarised, or re-checked when filed"* —
  and the standing caveat that **a scanning agent's tags are its own claim about the literature, not
  a replication audit. VET before any tagged claim becomes load-bearing.** The three corrections in §3
  are exactly what happened when that VET was applied to three of those claims. Treat every citation
  in §4 as a pointer to check, not as a checked fact.
- **The WIRED column is fresh runtime evidence taken this pass**, not inherited: fresh-process
  imports of both entry points with `sys.modules` diffs, an AST parent-walk over all 155 files for
  lazy imports (84 edges found), and import-closure probes of 17 candidate drivers. It independently
  reproduces the 35-of-141 figure in `CLAUDE.md` by a different route. Throwaway probe scripts were
  written outside the repo (`%TEMP%/hdprobe/`); nothing in the repo was touched.
- **Known limitation of this map:** the BRAIN'S MATH column is only as good as the lit scans behind
  it (see the provenance note above), and the FIDELITY verdicts follow from it. The OUR-OP column is
  read from code and is the most reliable column here.
- **Read-only:** no `hdlab/` or `experiments/` file modified; no experiment run; no `metrics.json`
  touched.
- **Concurrent session:** the working tree is dirty with another session's uncommitted work. Only this
  file was staged.
- **No tool call was denied during this audit.**

---

## 9. CORRECTIONS APPLIED (living log — newest first)

### 2026-08-14 — 12 biology corrections + 2 evidence corrections

Source: `notes/drill_cascade_synapse_replay_consolidation_biology_2026-08-14.md` (a targeted
literature drill against this map's own citations), plus two disk re-verifications.

**The drill checked 12 claims this map made and found 12 of them wrong.** That is the headline, and
it is a finding about the METHOD, not just the content: a citation copied once into a map is never
re-read, so an error in it compounds silently into every plan that cites the map. The corrections:

| # | organ | what was wrong | now |
|---|---|---|---|
| 1 | D8 | `SNR ~ N/(√K·t^0.5)` — wrong exponent of N | **`√N`**, full form `√N·e^(-t/T)/(√t·√(log T))`, `T=2^(2m+1)`. **32× error at N=1024** |
| 2 | D8 | capacity `~N` credited to the cascade | `~N` is **Benna-Fusi 2016**; cascade is **`~√N`**; fast binary `~log N` |
| 3 | D8 | "vs `N/t` for a single-state synapse" | single-state bounded/binary decays **exponentially**; `√N/t` is the cascade itself |
| 4 | D8 | one write probability | **two** families both `~2^-d`; plastic one **resets depth to 1 in the opposite cascade** |
| 5 | D8 | `α ≈ 0.5-1.0` | cascade α = **1** (or **3/4** as published 2005); **0.5 is a different model** |
| 6 | D8 | "Roxin & Fusi 2012" | **2013**, *PLoS Comput Biol* 9:e1003146 — and it SHARES the cascade's scaling, never supported `~N` |
| 7 | D4 | "each experience replayed 1-3 times" | **UNSOURCED** — not in the cited paper, not found anywhere. **Free parameter, sweep it** |
| 8 | D4 | "expanding intervals, approximately doubling" | actual schedules **`0,3,10` / `1,4,10`** (~4× then 2.5×); scoped to **test-type** practice; **general superiority CONTESTED** |
| 9 | D4 | reward-scaling cited to Foster & Wilson 2006 | **Ambrose, Pfeiffer & Foster 2016** *Neuron* 91:1124. The 2006 paper found reverse replay, never reward modulation |
| 10 | D4 | `g=0.50` quoted as an integration effect | **Schimke et al. 2021**; `g=0.50` is the **omnibus sleep-vs-WAKE** effect; **integration is the WEAKEST** measure in it |
| 11 | D4 | "Helfrich 2021 *PNAS* 118 e2012075118" | **UNVERIFIED** — flagged, not re-cited (LOW confidence = absence of confirmation) |
| 12 | STEP 5 | "cascade→shape / schedule→level cleanly separable" | **spacing effect is produced by the SYNAPSE ALONE** — fix uniform spacing in the synapse arm or run 2×2, else the confound flatters the schedule |

**Evidence correction A — coreference floors were a cross-run conflation.** This map cited recency
0.5439 / singleton 0.4737 as *the* E3 floors and concluded we lose to trivial baselines. Those numbers
are real, but come from `exp_extraction_quality_gate_neural_coref_v2` on metric `coref_b3_f1`, n=57.
On the run that actually measures our resolver
(`exp_wire_coref_accumulate_situation_model_v1`, 36 McGuffey passages), the same-run floors are
**recency 0.5614 / singleton 0.3860 and our resolver scores 0.7193.** **We are NOT losing to trivial
baselines at coreference.** A stale docstring propagated one hop into this map and turned a working
organ into a rescue target. Rule reinforced: **a floor is only a floor on the SAME corpus, metric, run
and arm.**

**Evidence correction B — the floor census has an arithmetic slip.** 594 + 359 = 953, not 946. Flagged
inline at §1; the scan needs re-running before the pair is quoted as exhaustive.

**Addition — the decorrelation drill (recorded at organ G3).** Whitening is per-dimension gain **in the
right basis**; our four failed reweightings were all per-RAW-dimension, i.e. wrong basis, so they are
**not** evidence that gain-based decorrelation fails. ~~Our code carries a **58% common mode**.~~
🔴 **SUPERSEDED 2026-08-14: the 58% does not reproduce (0.3650 graded / 0.2997 sign on the same
definition; true energy fraction 0.1535, PC1 0.0350), and rank-1 removal was TRIED and had NO
EFFECT** (`exp_rank1_common_mode_removal_v1`, `34b94e8bc` — 0.6980 → 0.6985, CI includes 0, random
direction identical). Rank-1
mean removal is estimable at our scale (`O(d)` samples); **full-covariance whitening is not**
(`O(d²)` = 65k-16M samples) and is PARKED-BY-SAMPLE-SIZE — **still not closed by the rank-1 null.**

**Addition — PARKED-BY-SCALE is now a first-class status on this map.** D8's cascade only beats
simpler multistate models above **~1e6 synapses** (published figures use 2.5e7 and 5.4e9); we run
`d = 256..4096`. **A negative there is the published prediction, not a ceiling.** Any organ whose
mechanism pays off orders of magnitude above our scale gets this tag with its crossover stated, and
is NOT queued as a win.

**What did NOT need correcting** (checked and upheld): the "SELECTION FUNCTION is UNPINNED" verdict at
D4 — with the added detail that its leading normative candidate (Mattar & Daw 2018,
`priority = GAIN × NEED`) is blocked for us on missing organ D7; and the per-`d` comparator table at
§B4, which already stated `QUANT [0.6395, 0.7030, 0.7380]` / `GRAD [0.6980, 0.7495, 0.78225]`
honestly. **`0.7495` is the d=1024 GRADED arm — it is NOT the live path.** The live path moved
**0.6395 → 0.6980**. Anyone quoting 0.7495 as a shipped result is quoting an unshipped capacity change.
