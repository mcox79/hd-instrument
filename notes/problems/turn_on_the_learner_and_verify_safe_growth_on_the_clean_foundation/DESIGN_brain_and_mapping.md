# DESIGN — turn the learner ON on the clean foundation (brain framing + the honest representational mapping)

Solver design note (scope: `experiments/`, `verification/`, this folder). Written BEFORE building, per the
operating protocol's opening move: *"how does the BRAIN do this, and are we replicating it or substituting
something convenient?"* — and to lock the one non-obvious decision (the representational mapping) so it does
not drift mid-build.

## 1. THE OPENING MOVE — how the brain grows knowledge by reading without corrupting what it knew

- **PINNED (replicate the COMPUTATION):** COMPLEMENTARY LEARNING SYSTEMS (McClelland, McNaughton &
  O'Reilly 1995; Kumaran/Hassabis/McClelland 2016). A fast hippocampal store holds specifics; a slow
  neocortical store integrates them GRADUALLY, INTERLEAVED WITH REPLAY, KEEPING BOTH STORES — which is
  precisely what prevents catastrophic forgetting. **Already reproduced on-substrate** by the validated
  safe-growth work: a keep-both-stores ENSEMBLE cuts corruption 0.256→0.079 (−0.177 CI-sep) keeping 71% of
  the +0.078 gain; a rate-limited blend (α=0.25) keeps 84% at 0.185. That mechanism is DONE and validated —
  I build ON it, I do not re-derive it.
- **PINNED (the NEW piece this problem adds):** SCHEMA-GATED CONSOLIDATION (Tse et al. 2007, *Science*,
  "Schemas and memory consolidation"; McClelland 2013; Winocur & Moscovitch trace-transformation). Cortical
  consolidation rate is **schema-dependent**: information CONGRUENT with an existing schema consolidates
  fast (Tse's rats learned new flavour-place pairs in ONE trial once a schema existed); information that
  VIOLATES the schema is gated / consolidated slowly / rejected. Systems consolidation over-writes toward
  the schema/gist, protecting consistent knowledge. **This is the brain's "clean foundation" mechanism:** it
  is not that the input text is pre-scrubbed — it is that the consolidation step ITSELF gates on
  schema-congruence. The prediction-error / novelty signal (N400; hippocampal CA1 `gap_detector`) is the
  gate's trigger.
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt):** the congruence score's exact form, the gate threshold
  τ, the acceptance tolerance, and the rollback probe fraction.

So the brief's "clean foundation" is, mechanistically, **schema-gated consolidation**: when the reader grows
by reading, each new candidate fact is admitted to the slow store only if it is congruent with the schema the
store already holds (or belongs to a domain the store has NO schema for — novelty in an empty schema is
learned freely; only schema-VIOLATIONS are gated). The p4 consistency organ IS this schema gate
(schema-congruence conflict energy); the p1 clean extraction reduces the rate of schema-violating garbage
reaching the gate in the first place.

## 2. THE HONEST REPRESENTATIONAL MAPPING (disk-outranks-brief)

The brief says *"feed from the landed tense-agnostic extraction; gate consolidation eligibility with the p4
consistency score."* **On the disk this is a representational mismatch, and I say so:**

- The VALIDATED safe-growth learner (`exp_growth_cls_ensemble_v1`, `exp_learner_safety_gate_v1`) grows a
  **distributional SELPREF similarity space** over **simplewiki verb×(arg-slot,filler) edges** (5M→15M
  tokens). Its downstream comprehension read-out is LitBank who-did-what verb-paraphrase.
- The p1 clean-extraction organ (`the_extraction_front_end…`, recall 0.33→0.95) and the p4 consistency
  organ operate on the reader's **situation-model / is-a knowledge base** (who-did-what triples; (subject,
  isa, genus) facts). **Neither literally feeds the SELPREF simplewiki learner.**

The brief tells me to BUILD ON the validated cells. So the disk-respecting move is **Route A: port the p4
COMPUTATION (schema-congruence conflict energy, strict leave-one-out) and the p1 PRINCIPLE
(extraction-reliability) onto the learner's OWN edges as a consolidation-eligibility gate** — because the
learner's edges ARE the store the validated safe-growth mechanism actually grows. I test the brief's *actual
scientific question* (does cleaning the consolidated input change the corruption/gain tradeoff?) on the
representation the mechanism lives in, and I document the mapping rather than pretend the organs plug together.

**Why this is faithful, not convenient:** the p4 organ's own LOO-clean honest signal is its DISTRIBUTIONAL
arm (AUC ~0.77) — "does the subject's usage look like the usage of other terms of that type." The direct
analog for a verb-argument edge is: *does this new filler resemble the fillers this verb's established schema
already licenses?* That is selectional-preference schema-congruence, computed strictly from the pre-growth
(5M) store and judging only 10M-growth edges (LOO by construction). Schema-violating fillers (parse errors,
contradictions, over-generated adjuncts — exactly p1's "over-generation" failure) score low and are gated;
schema-consistent novel fillers ("pursue" when "chase" is licensed) score high and consolidate.

## 3. THE MECHANISM (what I build)

**Schema (built from 5M only):** a general word embedding `base_emb` (5M ±2-window PPMI-SVD, reused verbatim
from `S.build_cooc`) for filler similarity, and per verb v a centroid `vcen[v]` = mean `base_emb` over the
fillers v's 5M SELPREF edges already license. `vcen[v]` is v's established selectional schema.

**Consolidation-eligibility gate** on each 15M edge (v, slot, f):
- if (v, slot, f) already licensed at 5M → **keep** (reinforcement, no novelty risk);
- elif v has NO 5M schema (vcen undefined) → **keep** (novelty in an empty schema — learn freely, Tse);
- else congruence(v,f) = cosine(vcen[v], base_emb[f]); **keep iff congruence ≥ τ**, else **gate out**
  (schema-violating novelty).

`CLEAN15` store = SELPREF over the kept edges. Everything else identical to the naive 15M build.

## 4. ARMS (all scored on the SAME LitBank paraphrase items — CORE_COMMON; no number crosses populations)

| arm | store | tests |
|---|---|---|
| `OFF` | SELPREF 5M | growth-off baseline |
| `NAIVE15` | SELPREF 15M all-edges | noisy overwrite (reference corruption 0.256) |
| `CLS_NOISY` | ENSEMBLE_MEAN(5M, NAIVE15) | validated safe switch, NOISY foundation |
| `CLS_CLEAN` | ENSEMBLE_MEAN(5M, CLEAN15) | **safe switch, SCHEMA-GATED clean foundation** |
| `CLS_RANDGATE` | ENSEMBLE_MEAN(5M, RANDGATE15) | drop the SAME count of candidate edges at RANDOM (gate twin) |
| `CLS_INFOFREE` | ENSEMBLE_MEAN(5M, FILLERSHUF15) | info-free growth twin (must NOT help) |
| `RANDOM_floor` | random vectors | floor |

## 5. THE FIVE BAR POINTS → the test that answers each

1. **BENEFICIAL** — `CLS_CLEAN` gain vs `OFF` CI-separated above 0 (paired bootstrap).
2. **REAL** — `CLS_INFOFREE` gain vs `OFF` NOT CI-separated above 0 (the info-free twin loses).
3. **SAFE** — `CLS_CLEAN` corruption (right→wrong among OFF-correct) CI **upper** bound < the
   **PRE-REGISTERED bound 0.15** (below the unacceptable naive 0.256; a conservative engineering tolerance),
   reported with the confidence split (must not be confidence-separable churn — report both halves).
4. **ROLLBACK** — a held-out KNOWN-CORRECT probe (frozen 40% split of OFF-correct items); a candidate update
   is ACCEPTED iff its probe corruption < tolerance, else ROLLED BACK to the prior (keep-both) store.
   Demonstrate: `CLS_CLEAN` update accepted; a NAIVE-overwrite and an ADVERSARIAL (filler-corrupted) update
   detected + rolled back. Decision made on the probe, EFFECT verified on the disjoint working set
   (generalization, not probe-overfit). Info-free control: a random accept/reject decision does not protect
   the working set.
5. **CLEAN-FOUNDATION EFFECT** — the brief's INFERRED question:
   - `CLS_CLEAN` corruption vs `CLS_NOISY` corruption, paired, CI-separated **below** = cleaning lowers
     corruption;
   - `CLS_CLEAN` gain vs `CLS_NOISY` gain, NOT CI-separated below = gain NOT sacrificed (lower corruption at
     equal gain — the hoped-for result);
   - `CLS_CLEAN` corruption vs `CLS_RANDGATE` corruption, CI-separated **below** = the reduction is the
     SCHEMA signal, not merely "less data."

**A rigorous NEGATIVE is a full PASS.** Possible honest negatives, each precisely located: the gate lowers
gain (throws away signal); the corruption is representation-reorganization not noisy-input (so cleaning ≈
random-drop, bar-5 twin not separated); the corpus is already clean enough that the gate barely fires. Any of
these is reported as "not yet net-beneficial-via-cleaning, and here is exactly why," keeping the growth switch
OFF for a named reason.

## 6. PRE-REGISTERED before running
- Acceptable corruption bound (bar 3): **CI upper bound of CLS_CLEAN right→wrong corruption < 0.15.**
- Rollback tolerance (bar 4): probe corruption **< 0.15** to accept an update.
- Clean-effect direction (bar 5): CLEAN reduces corruption vs NOISY **AND** vs RANDGATE, at gain not
  CI-separated below NOISY. Any other outcome is a located negative, reported as such.
