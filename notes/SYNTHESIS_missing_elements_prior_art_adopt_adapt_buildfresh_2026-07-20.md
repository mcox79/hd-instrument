# SYNTHESIS: prior-art scour of every missing element — ADOPT / ADAPT / BUILD-FRESH (2026-07-20)

Director synthesis of the 3 build+prior-art scours (Scour-A foundation aeef2cf2, Scour-B self-monitoring a3b8ca39, Scour-C second-order a2c24245) + the metacognition empirical test. USER-directed: "drill each missing element 3x, and see if there are examples of doing this out there we can gain from." ANSWER: nearly every element is ADOPT/ADAPT from credited glass-box prior work; the missing learning-and-self-monitoring layer is buildable from RECOMBINATION, not novel research. Credit prior work (learn-from/build-on, never steal).

## THE TABLE

| ELEMENT | TIER | ADOPTABLE PRIOR ART (credit) | CALL | SEQUENCING | BUILDABLE NOW? |
|---|---|---|---|---|---|
| **Learned codebook** (similarity-structured content codes) | FOUNDATION | Random-Indexing (Kanerva/Sahlgren), BEAGLE (Jones-Mewhort), PPMI-weighting | **ADOPT** | prerequisite for the loop | **YES** (co-occurrence over our corpus) |
| **Contrastive coherence loop** (entity-recurrence target) | FOUNDATION | Entity-grid (Barzilay-Lapata) + Guinaudeau-Strube out-degree; ALBERT-SOP negatives; ELECTRA/InfoNCE contrastive | ADOPT+ADAPT | needs codebook first | YES (CAVEAT: read arXiv 2110.07198 shuffle-gameability critique first — don't build a cheatable coherence signal) |
| **Homeostatic scaling** (loop safety) | FOUNDATION | Oja's rule (primary); BCM; weight-normalization | **ADOPT** | into the loop | YES |
| **Metacognition / abstain** | SELF-MON | Chow reject-rule; OOD margin/entropy; meta-d' (Fleming); CONFORMAL (Vovk/Angelopoulos); hdlab/conformal.py | **ADOPT** (+3 cheap additions to conformal.py) | independent | **YES — already tests POSITIVE** (reader learned-score cuts confident-wrong 33%, VET running) |
| **Attention / salience** | SELF-MON | Precision-weighting=Kalman-gain (Feldman-Friston); divisive-normalization (Reynolds-Heeger); sparsemax; IDF/Itti-Koch | ADOPT | independent | YES — and LIKELY ALREADY PARTIALLY BUILT (our surprise signal = IDF family); delta = reliability multiplier + hard-gate |
| **Neuromodulatory gating** (multi-axis learning control) | 2ND-ORDER | Yu-Dayan ACh/NE 2-axis; Mathys HGF; Behrens volatility-Kalman | ADOPT | **base-loop-gated** | after loop |
| **Hierarchical multi-timescale** | 2ND-ORDER | HTM temporal pooler; Hasson TRW; MTRNN (Yamashita-Tani) | ADAPT | **base-loop-gated** | after loop |
| **Consolidation / schema-replay** | 2ND-ORDER | CLS-theory (McClelland); prioritized replay; generative/brain-inspired replay (van de Ven) | ADAPT | **base-loop-gated** | after loop |
| **Learned structure-derivation** (derived not stipulated) | 2ND-ORDER | Successor-Representation eigenvectors (Stachenfeld-Botvinick-Gershman); Oja-PCA; slow-feature | ADAPT | **INDEPENDENT** | **YES — cheap standalone test runnable now** |

## KEY FINDINGS
1. **Almost nothing is build-fresh.** Every element maps to credited glass-box prior art (RI/BEAGLE, entity-grid, Oja, conformal, Kalman-precision, HGF, HTM, CLS-replay, SR-eigenvectors). The missing layer = credited RECOMBINATION.
2. **The foundation core is buildable NOW** on our existing corpus, no novel math — but it's an AND-gate (all 3 must work; integrated P~0.50). Codebook FIRST (loop prerequisite).
3. **Self-monitoring is the cheapest + partly already-there.** Metacognition already tests POSITIVE (reader learned-score, 33% confident-wrong cut, VET-running); attention is likely partially built (surprise=IDF family) + a small delta; conformal.py exists (needs 3 cheap additions).
4. **Second-order sequencing CONFIRMED:** 3 of 4 (neuromod, hierarchy, consolidation) are strictly base-loop-gated — nothing to wire until the loop exists (validates the dependency-order). Structure-derivation (SR-eigenvectors/Oja-PCA) is the ONE exception: base-loop-INDEPENDENT + cheap-test-now.

## BUILD PLAN (dependency-ordered, from adopted prior art)
- **STEP 1 (FIRE NOW, the gated prerequisite per the CPCL VET):** build the learned similarity-structured CODEBOOK (Random-Indexing/BEAGLE+PPMI over our corpus) + VALIDATE it generalizes (held-out true-vs-random > chance). This is the gate the CPCL null demanded ("structured codes must generalize before any full loop"). Cheap, decisive, adopted.
- **STEP 2 (if codebook passes):** the contrastive coherence-loop (entity-grid/SOP target) on top of the codebook + Oja homeostatic safety = the integrated foundation core. Read arXiv 2110.07198 first (coherence-gameability guard).
- **PARALLEL (cheap, independent, now):** metacognition abstain (adopt conformal + reader learned-score, VET-running) + attention reliability-gate + structure-derivation SR/Oja cheap test.
- **AFTER the loop works:** neuromod gating (HGF), hierarchical prediction (HTM+TRW), consolidation (CLS+replay).

## VERDICT (one line)
The missing learning-and-self-monitoring layer is NOT a research problem — it is an ENGINEERING recombination of credited glass-box prior art (RI/BEAGLE + entity-grid/SOP + Oja + conformal + Kalman-precision + HGF + HTM + CLS-replay + SR-eigenvectors), dependency-ordered with the codebook+loop foundation first; the codebook prerequisite is the disciplined first build and is firing now.
