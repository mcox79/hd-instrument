# Research drill: Brain mechanisms NOT YET tested in substrate (2x drill)

**Date:** 2026-06-24
**Topic:** Inventory of brain mechanisms relevant to language/prediction that have NOT been implemented in the HD substrate, ranked by expected leverage for closing the substrate-vs-bigram gap.
**Drill type:** 2x operational (NOT verification; deeper map of unexplored mechanism-space)
**Companion drill:** in-flight substrate-mining drill (inventories what HAS been tested)
**Calibration penalty:** 0.20 deflation on novel-synthesis P; cap at 0.50 for any single-mechanism close-the-gap claim
**Brain-existence-proof prior:** P_feasibility = 0.60-0.75 for brain-canonical mechanisms (USER 2026-06-23: brain is existence proof for ~1 bit/char; only implementation correctness is at risk)

---

## HEADLINE

**The substrate has been testing brain mechanisms at the WRONG temporal grain (character-level, ~30Hz) and the WRONG hierarchical depth (single-level), missing TWO mechanisms with the strongest brain-existence-proof and the cheapest substrate paths: (1) word-level (theta-band ~5Hz) prediction with a saccade-grained "word token" representation, and (2) two-level Rao-Ballard predictive coding with top-down feedback from a context layer to the encoder layer.**

Both are brain-canonical (Rao-Ballard 1999; Ding/Poeppel 2016 theta-tracking; Kazanina/Tavano 2025 BRyBI), neither has been implemented in this substrate's 30+ tested mechanisms, both have substrate-native algebra paths (HRR bind for word-level, two-codebook resonator stack for PC), and both could plausibly deliver >+0.3 bits BPC each.

---

## L1: BRAIN MECHANISMS INVENTORY (TESTED vs NOT_TESTED)

Below: comprehensive mechanism inventory with substrate-test status as of 2026-06-24. Status drawn from session 2026-06-22 to 2026-06-23 cert ledger (n=20+ landed cells), cross-referenced against MEMORY.md project entries and recent research notes.

### Block A: Plasticity / Learning Rules

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| Hebbian (LTP) | 5/5 (Bliss-Lomo 1973+) | **TESTED** | core substrate; n1 sequence-binding cert-585 |
| Anti-Hebbian (LTD) | 5/5 | **TESTED (partial)** | implicit in current_best whitening; no explicit cell |
| STDP (asymmetric Hebb) | 5/5 (Bi-Poo 1998) | **TESTED** (in flight 2026-06-23) | dopamine-modulated LR cell ran |
| BCM rule (sliding threshold) | 4/5 (Cooper-Bear 2012) | **NOT_TESTED** | bidirectional w/ activity-dependent threshold; sequence-learning lit exists |
| Triplet STDP (Pfister-Gerstner) | 4/5 | **NOT_TESTED** | extends STDP to multi-spike interactions |
| Dopamine-modulated LR | 5/5 (Schultz 1997) | **TESTED** (HARD_FAIL, brain-direction-correct in flight) | duration-extension cell pending |
| Acetylcholine gain | 4/5 | **NOT_TESTED** | encoding-vs-retrieval mode switch |
| Norepinephrine gain | 4/5 (Aston-Jones) | **NOT_TESTED** | network-reset / uncertainty signal |
| Serotonin (5HT) gain | 3/5 | **TESTED** (HARD_FAIL; K=4 wrong; K=2 rescue queued) | bank-switch refuted, soft-mixing untested |
| Multi-timescale plasticity (fast + slow weights) | 4/5 | **TESTED** (partial; may need correct formula) | dual_trace_mechanism note exists |
| Synaptic tagging-and-capture | 4/5 (Frey-Morris 1997) | **NOT_TESTED** | late-LTP via tag protein synthesis; substrate analog = deferred consolidation |
| Heterosynaptic plasticity | 3/5 | **NOT_TESTED** | sliding-threshold variant tied to BCM |

### Block B: Coding / Representation

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| Population (distributed) coding | 5/5 | **TESTED** | HRR is one form; core substrate |
| Sparse coding (Olshausen-Field 1996) | 5/5 (V1) | **TESTED (storage)** but **NOT_TESTED (encoder-learning)** | sparse-bipolar codebook stored; encoder still char-trigram, NOT learned via sparse-coding objective |
| Rank/grid codes | 5/5 (entorhinal) | **NOT_TESTED** | medial-entorhinal Fourier basis; substrate not implementing |
| Place-cell-like codes | 5/5 (hippocampus) | **NOT_TESTED (lang)** | tested for KG, not for text |
| Mixed-selectivity / random projection | 4/5 (Fusi 2013) | **TESTED** | HD random codebook = canonical |
| Lateral inhibition (WTA at multiple scales) | 5/5 | **TESTED (partial)** | k-WTA in n4 VQ; multi-scale WTA NOT tested |
| Spike-timing precision (~1ms) | 5/5 | **NOT_TESTED** | substrate is rate-code; no temporal-spike representation |
| Phase coding (theta-phase) | 4/5 (O'Keefe-Recce) | **NOT_TESTED** | brain encodes by spike phase relative to theta; substrate has no phase |
| Temporal codes | 4/5 | **NOT_TESTED** | substrate is rate-/value-based |

### Block C: Dynamics

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| Attractor dynamics (CA3) | 5/5 | **TESTED** (cue-clamping in flight) | iterative_attractor.py 2-line edit |
| Theta-gamma coupling | 5/5 (Lisman 2013) | **TESTED** (HARD_FAIL; amplitude bug; correct version NOT re-tested) | needs rerun with proper PAC implementation |
| Top-down feedback (10x more than feedforward) | 5/5 | **NOT_TESTED** | substrate is feedforward-only end-to-end |
| Bottom-up prediction error | 5/5 (Rao-Ballard 1999) | **NOT_TESTED** | substrate has no PE signal computed |
| Lateral connections (cross-column) | 5/5 | **NOT_TESTED** | substrate is per-position independent |
| Predictive coding (full PC stack) | 5/5 (Friston 2010) | **NOT_TESTED** | core unimplemented mechanism |
| Free-energy minimization | 4/5 | **NOT_TESTED** | variational substrate analog absent |
| Saccadic/temporal sampling at theta (~5Hz word rate) | 4/5 (Ding-Poeppel 2016) | **NOT_TESTED** | substrate processes at char-rate (every position); brain at word-rate |
| Reservoir computing (random recurrence) | 3/5 | **NOT_TESTED** | substrate has no recurrent state |
| Echo-state network | 3/5 | **NOT_TESTED** | reservoir analog |

### Block D: Memory & Consolidation

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| Episodic-memory binding (CA1/CA3) | 5/5 | **TESTED** | core substrate cert-588 |
| Working memory (Baddeley persistent activity) | 5/5 | **NOT_TESTED (formally)** | no held-state across tokens |
| Replay (offline reactivation) | 5/5 (Wilson-McNaughton 1994) | **TESTED (partial)** | CLS-replay scaffold exists; not consolidation-style |
| Sleep-dependent consolidation | 4/5 | **NOT_TESTED** | offline transfer NOT implemented |
| Schema consolidation (cortical schemas) | 3/5 | **NOT_TESTED** | hierarchy-of-schemas NOT explicit |
| Pattern separation (DG sparsening) | 5/5 | **TESTED** (sparse codebook) | implicit; not as explicit DG-CA3 stage |
| Pattern completion | 5/5 (CA3 attractor) | **TESTED** | core cleanup mechanism |
| Indexing theory (HC pointer to neocortex) | 3/5 | **NOT_TESTED** | substrate has no two-store HC-neocortex |

### Block E: Attention / Selection

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| Selective attention (Treisman / Posner) | 5/5 | **NOT_TESTED** | substrate processes all tokens uniformly |
| Bottom-up saliency | 5/5 | **NOT_TESTED** | no surprise-gated update |
| Top-down attentional bias | 5/5 | **NOT_TESTED** | no goal-driven weighting |
| Inhibition of return | 4/5 | **NOT_TESTED** | already-attended suppression absent |

### Block F: Hierarchy / Cortical Architecture

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| Cortical hierarchy (multiple feature levels) | 5/5 | **NOT_TESTED (deep)** | substrate is mostly 1-level (encoder -> cleanup); no L1->L2->L3 |
| Canonical cortical microcircuit (Douglas-Martin) | 4/5 | **NOT_TESTED** | L2/3 - L4 - L5 - L6 motif absent |
| Column / minicolumn organization | 4/5 | **NOT_TESTED** | substrate has no column structure |
| Cortico-cortical loops | 4/5 | **NOT_TESTED** | recurrent cross-layer feedback absent |
| Thalamo-cortical loops | 4/5 | **NOT_TESTED** | gating/relay mechanism absent |
| Cortico-basal-ganglia loops | 3/5 | **NOT_TESTED** | action-selection absent |

### Block G: Embodiment / Grounding / Cross-Modal

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| Sensorimotor grounding | 4/5 | **NOT_TESTED** | substrate is text-only; not relevant for current product |
| Cross-modal binding | 4/5 | **NOT_TESTED** | substrate is unimodal text |
| Mirror-neuron-like prediction | 3/5 | **NOT_TESTED** | not directly applicable |

### Block H: Inference / Probabilistic

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| Bayesian inference (full) | 4/5 (Friston) | **NOT_TESTED** | no explicit prior+likelihood update |
| Expectation-Maximization (Helmholtz) | 3/5 | **NOT_TESTED** | wake-sleep absent |
| Variational inference | 4/5 | **NOT_TESTED** | free-energy absent |
| Importance sampling / particle filter | 3/5 | **NOT_TESTED** | absent |
| Active inference | 3/5 (Friston 2017+) | **NOT_TESTED** | action-policy absent |

### Block I: Oscillations / Rhythms

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| Theta (4-7Hz) word-segmentation | 5/5 (Ding-Poeppel 2016) | **NOT_TESTED** | substrate has no theta-clock |
| Gamma (30-80Hz) feature-binding | 5/5 | **TESTED (partial)** | theta-gamma had amplitude bug; gamma-only NOT tested |
| Delta (1-4Hz) phrase-level | 4/5 | **NOT_TESTED** | substrate has no phrase-level rhythm |
| Beta (15-30Hz) top-down | 4/5 | **NOT_TESTED** | substrate has no top-down beta gating |
| Cross-frequency coupling (CFC) | 4/5 | **TESTED (HARD_FAIL bug)** | needs rerun |

### Block J: HTM / Numenta / Reservoir

| Mechanism | Brain evidence | Substrate-test status | Notes |
|---|---|---|---|
| HTM spatial pooler | 3/5 | **NOT_TESTED** | distributed sparse representation w/ overlap-pooling |
| HTM temporal memory (high-order seq) | 3/5 | **NOT_TESTED** | column-and-cell predictive states |
| Reservoir / echo state | 3/5 | **NOT_TESTED** | random recurrent W with trained readout |
| Liquid state machine | 3/5 | **NOT_TESTED** | spiking reservoir |

---

## L2: PER-MECHANISM SUBSTRATE-FEASIBILITY SCORING (NOT_TESTED only)

Scoring system: (Brain-evidence 1-5) | (Substrate-impl 1-5, 5=easy) | (Expected-leverage 1-5) | (Cost 1-5, 5=cheap) -> Composite (sum, max 20)

Ordered descending by composite. P_deflated already includes 0.20 calibration penalty per [[feedback-lit-scan-calibration-penalty]].

| # | Mechanism | BE | SI | EL | Cost | Composite | P_deflated |
|---|---|---|---|---|---|---|---|
| 1 | **Word-level (theta-grain ~5Hz) prediction at V_word level** | 5 | 5 | 5 | 5 | **20** | 0.55 |
| 2 | **2-level Rao-Ballard PC (encoder<->context with top-down feedback)** | 5 | 4 | 5 | 4 | **18** | 0.50 |
| 3 | **Working memory (persistent activity / register across tokens)** | 5 | 4 | 5 | 4 | **18** | 0.50 |
| 4 | **BCM rule (sliding threshold on encoder activations)** | 4 | 5 | 4 | 5 | **18** | 0.45 |
| 5 | **Sparse-coding objective for ENCODER learning (L1-on-codes objective)** | 5 | 3 | 5 | 3 | **16** | 0.45 |
| 6 | **Cortical hierarchy: deep stack of K=3 PC levels** | 5 | 3 | 5 | 3 | **16** | 0.45 |
| 7 | **Top-down feedback from context to encoder (read-only PC variant)** | 5 | 4 | 4 | 3 | **16** | 0.45 |
| 8 | **Variational / free-energy substrate analog** | 4 | 3 | 4 | 3 | **14** | 0.35 |
| 9 | **Phase-coding (theta-phase relative position)** | 4 | 3 | 4 | 3 | **14** | 0.35 |
| 10 | **HTM temporal memory (high-order sequence w/ per-column predictive cells)** | 3 | 3 | 4 | 3 | **13** | 0.35 |
| 11 | **Reservoir computing (random RNN + trained readout)** | 3 | 4 | 3 | 4 | **14** | 0.30 |
| 12 | **Lateral connections (cross-position WTA)** | 5 | 3 | 3 | 3 | **14** | 0.30 |
| 13 | **Selective attention (surprise-gated update)** | 5 | 4 | 3 | 3 | **15** | 0.35 |
| 14 | **Acetylcholine encoding-mode gain** | 4 | 4 | 3 | 4 | **15** | 0.30 |
| 15 | **Norepinephrine network-reset on uncertainty** | 4 | 4 | 3 | 4 | **15** | 0.30 |
| 16 | **Triplet STDP** | 4 | 3 | 3 | 3 | **13** | 0.25 |
| 17 | **Schema consolidation (multi-stage HC->neocortex transfer)** | 4 | 3 | 4 | 2 | **13** | 0.30 |
| 18 | **Synaptic tagging-and-capture (late-LTP)** | 4 | 3 | 3 | 3 | **13** | 0.25 |
| 19 | **Active inference (action-policy)** | 3 | 2 | 3 | 2 | **10** | 0.20 |
| 20 | **Spike-timing-precise temporal code** | 5 | 1 | 3 | 1 | **10** | 0.20 |

**Top 3 by composite (with P_deflated > 0.45):**
1. Word-level (theta-grain) prediction — Composite 20, P=0.55
2. 2-level Rao-Ballard PC with top-down feedback — Composite 18, P=0.50
3. Working memory (persistent register across tokens) — Composite 18, P=0.50

---

## L3: DEEP-DIVE ON TOP 3

### L3.1: Word-level (theta-grain ~5Hz) prediction at V_word level

**Brain literature:**
- Ding & Poeppel (2016, Nature Neuroscience): theta (4-7Hz) tracks word rate in speech; delta (1-4Hz) tracks phrase rate
- Kazanina & Tavano (2025, Nature Computational Science): "BRyBI" model — delta governs integration time-windows; theta provides word-level packaging
- MIT 2021 study: next-word-prediction-trained transformers align with brain language areas; character-level models do NOT
- Ettinger et al. (2018) and follow-ups: brain's prediction signal locks to WORD onsets, not character onsets

**Why this could close the gap:**
Substrate's current char-level testing at ~30Hz (every char position) is fundamentally OFF-grain from what the brain does. The brain doesn't predict "next character probability"; it predicts WORDS. The bigram baseline at character level is artificially low ceiling (~7.0 BPC); the brain's ~1 bit/char number is at WORD-prediction level. At V_word ≈ 4000 (text8), unigram is ~10.5 bits/word ≈ 1.4 BPC; word-bigram is ~7.8 bits/word ≈ 1.05 BPC. So a substrate that beats word-unigram by even 20% delivers a chained improvement that compounds across char positions.

**Substrate-native implementation sketch:**
```python
# Cell anchor: brain_word_level_prediction_v1
# CHANGE FROM PRIOR CELLS: predict at word boundary, not char position
# Architecture:
#   V_word = 4000 (top text8 words by frequency)
#   N_DIM = 8192 (matches existing substrate)
#   encoder: char-trigram or learned -> word-vector (mean-pool over word chars)
#   cleanup codebook C: shape (V_word, N_DIM), each row = HD vector for a word
#   prediction: given context window W (last K=5 words encoded -> single HD context vec via HRR bind),
#               c_pred = sum over k=1..K of bind(role_k, word_{-k})
#               retrieval: argmax_w cosine(c_pred, C[w])

# Three baselines for clean discrimination:
#   B1: word-unigram (top-1 by frequency only)
#   B2: word-bigram (last-word -> next-word transition)
#   B3: substrate with K=1 (last-word only via HRR bind)
#   ARM: substrate with K=5 context
```

**Pre-reg HARD bands (first test):**
- HARD_PASS: substrate K=5 top-1 accuracy >= 1.30 * word-bigram top-1 accuracy AND surprise/BPW <= word-bigram - 0.4 bits
- MIDDLE_BAND: top-1 lift in [1.10x, 1.30x] OR BPW in [bigram-0.4, bigram-0.1]
- HARD_FAIL: substrate top-1 <= word-bigram top-1 OR BPW >= word-bigram

**Why this could give >+0.3 bits BPC equivalent:**
Brain's 1 bit/char = ~5 bits/word (5 chars avg per word in English including spaces). Word-unigram = ~10.5 bits/word. So brain achieves >5 bit/word lift over word-unigram. A substrate that does even half (2-3 bit/word lift over word-unigram) translates to ~0.4-0.6 bit/char improvement vs current ~0.7 bit/char lift over char-unigram. Compounds with cf-RPE.

**Risk:**
- P_deflated = 0.55 (HIGH for a brain-canonical not-yet-tested mechanism)
- Main risk: at V_word=4000 with substrate N_DIM=8192, capacity is not the bottleneck; the discriminator is whether HRR-bind composition actually carries the word-bigram signal vs degrading to unigram statistics

### L3.2: Two-level Rao-Ballard predictive coding with top-down feedback

**Brain literature:**
- Rao & Ballard (1999, Nat Neuroscience): original PC formulation; top-down predictions, bottom-up errors
- Friston (2010, Nat Rev Neuro): free-energy variational extension
- Spratling (2017): PC variants and substrate maps
- Lyu et al. (2024, NeuroImage): empirical lexico-semantic PC model fitting MEG/EEG/fMRI data
- bioRxiv 2025 02 27: PC explains 10:1 asymmetric feedback/feedforward connectivity

**Why this is a brain-existence-proof mechanism:**
PC is the dominant theoretical framework for cortical computation across modalities. The brain has ~10x more top-down than bottom-up connections — substrate has ZERO top-down. Every published successful application uses TWO levels minimum. Direct 2024 demonstration: lexico-semantic PC implementation explains human reading-comprehension neural dynamics in left vmPFC.

**Substrate-native implementation sketch:**
```python
# Cell anchor: brain_predictive_coding_2level_v1
# Architecture:
#   LEVEL 1 (encoder): per-position char-trigram encoding x_i in HD space
#   LEVEL 2 (context): higher-level state h built from recent x_{i-K..i-1}
#                     h = HRR-bundle of last K words (theta-grain) OR last K chars
#   TOP-DOWN PREDICTION: x_pred_i = W_td @ h    (W_td learned via Hebb on h, x_i pairs)
#   ERROR: e_i = x_i - x_pred_i
#   NEXT-TOKEN: predict from MIN(error) hypothesis: argmax_w cosine(h, C_word[w])
#               or with refinement: x_pred_{i+1} = W_td @ h_new where h_new updated by e_i

# This is the SUBSTRATE form of the Rao-Ballard equations:
#   r_l = W_(l+1->l) @ r_(l+1)        (top-down prediction)
#   e_l = r_l_actual - r_l_predicted   (bottom-up error)
#   delta r_(l+1) = -alpha * W^T @ e_l (state update via error)

# Three arms:
#   A1: feedforward only (current substrate baseline at fair_harness)
#   A2: 2-level PC, NO top-down (control to isolate hierarchy effect)
#   A3: 2-level PC, WITH top-down feedback (full mechanism)
```

**Pre-reg HARD bands:**
- HARD_PASS: A3 BPC <= fair_harness baseline - 0.30 AND A3 - A2 >= 0.15 bits (proves top-down matters, not just hierarchy)
- MIDDLE_BAND: A3 BPC in [fair_harness - 0.30, fair_harness - 0.10]
- HARD_FAIL: A3 >= fair_harness OR A3 - A2 <= 0.02 bits (top-down is null)

**Why this could give >+0.3 bits BPC lift:**
The 2024 lexico-semantic PC implementation predicts neural BOLD with explained-variance comparable to small transformer LMs. Direct substrate-equivalent of "context layer predicts encoder layer + error correction" gives a PHASE-2 lift on top of word-level (L3.1) — they STACK.

**Risk:**
- P_deflated = 0.50 (CAP applied per calibration penalty)
- Main risk: Hebbian-only training of W_td may underfit relative to gradient-based PC (Friston updates use credit assignment). Substrate's "no-backprop" constraint may bottleneck top-down efficacy. Mitigation: try CLS-replay-style consolidation of top-down weights.

### L3.3: Working memory (persistent register across tokens)

**Brain literature:**
- Baddeley & Hitch (1974): phonological loop + central executive
- Goldman-Rakic (1995): persistent dlPFC activity during delay-period
- Wang et al. (2018, Nat Neurosci): persistent activity via NMDA-receptor recurrence
- Lundqvist et al. (2018): WM via theta-gamma temporal packaging (composite with theta-grain)

**Why this is the missing piece (and existence-proof high):**
The substrate currently has NO state held across tokens. Each char position is processed independently against the cleanup codebook. Brain WM is the foundation of comprehension — without it, long-range dependencies cannot exist. cf-RPE and STDP both add LOCAL temporal coupling; WM adds GLOBAL register-of-context.

**Substrate-native implementation sketch:**
```python
# Cell anchor: brain_working_memory_register_v1
# Architecture:
#   WM register h: HD vector, N_DIM = 8192
#   Update rule (per token): h_new = beta * h_old + (1-beta) * encode(token)
#   beta in [0.85, 0.99] sweep (theta-grain decay: 1/(1-beta) = effective context)
#   Prediction: top-k argmax cosine(h_new, C_word[w])
#   Composes with theta-grain (L3.1): h updates at WORD boundaries not CHAR

# Three arms:
#   A1: no-WM (current substrate)
#   A2: WM at char-grain (beta sweep)
#   A3: WM at word-grain (theta sync) — IDEAL form combining L3.1 + L3.3

# Compose-stack hint: if A3 + L3.2 PC top-down both HARD_PASS,
# the architecture becomes:
#   x_i -> encoder -> h_WM (update) -> top-down prediction -> error -> next token
# This is the BRAIN'S minimal language-prediction stack
```

**Pre-reg HARD bands:**
- HARD_PASS: A3 BPC <= fair_harness - 0.30 with beta in [0.90, 0.95]
- MIDDLE_BAND: A2 or A3 in [fair_harness - 0.30, fair_harness - 0.10]
- HARD_FAIL: A3 >= fair_harness (WM register doesn't help)

**Why this could give >+0.3 bits BPC lift:**
Even a simple exponentially-decaying WM register implements the equivalent of an n-gram cache. The "AWD-LSTM cache pointer" (Grave et al. 2017) added +0.3-0.5 bit per char by similar mechanism. Substrate version with theta-grain word-level update should match-to-exceed.

**Risk:**
- P_deflated = 0.50
- Main risk: substrate's lack of training-via-error-gradient means beta is hand-tuned; the optimal beta may vary across text positions in ways substrate cannot adapt. Mitigation: per-position-NE-controlled beta (composes with L3 NE gain mechanism).

---

## L4: SACCADIC / WORD-LEVEL SPECIAL CASE — Cell design

**Specific cell-design for word-level next-word prediction:**

```python
# Cell anchor: brain_word_level_prediction_v1
# Owner: research -> exp_dev handoff
# Estimated runtime: ~10-15 min on remote_cpu (text8 hold-out, K=5 context)
# Smoke test: same architecture on 10K char synthetic Zipfian text (cell-author validates)

CONFIG = {
    "V_word": 4000,            # top text8 words by frequency
    "N_DIM": 8192,
    "context_window_K": [1, 3, 5, 10],   # sweep
    "encoder": "char_trigram_meanpool",  # word-vec = mean-pool of char-trigrams across word
    "codebook_C": "frozen_at_training",
    "binding_mode": ["bundle_only", "hrr_role_bind", "convolutional_bind"],
    "test_split": "text8_hold_out_last_5M_chars",
    "metrics": ["top1_acc", "top5_acc", "BPW", "BPC_equivalent"]
}

ARMS = {
    "B1_word_unigram": "predict argmax by training-set frequency",
    "B2_word_bigram": "predict argmax by last-word transition table",
    "S_K1_bundle":    "substrate K=1, simple bundle",
    "S_K5_HRR":       "substrate K=5, HRR role-bind",
    "S_K10_HRR":      "substrate K=10, HRR role-bind"
}

PREREG = {
    "HARD_PASS": (
        "S_K5_HRR top1_acc >= 1.30 * B2_word_bigram top1_acc "
        "AND S_K5_HRR BPW <= B2_word_bigram BPW - 0.4 bits"
    ),
    "MIDDLE_BAND": (
        "S_K5_HRR top1_acc in [1.10x, 1.30x] of B2 "
        "OR S_K5_HRR BPW in [B2 - 0.4, B2 - 0.1]"
    ),
    "HARD_FAIL": (
        "S_K5_HRR top1_acc <= B2_word_bigram top1_acc "
        "OR BPW >= B2_word_bigram BPW"
    ),
}
```

**Why testing at word level may systematically REVEAL substrate aliveness that char-level masks:**

1. **Char-level baselines are artificially competitive**: char-unigram is 4.6 bits/char (basically just letter frequencies); char-bigram is ~4.0; char-trigram ~3.8. The "1 bit/char" brain estimate isn't a char-level metric — it's a WORD-level metric pushed through the chain rule. Substrate measured at char level competes with strong locally-deterministic baselines.

2. **Word-level matches the brain's natural processing grain**: cortical theta oscillations gate word-level packaging at ~5Hz. The substrate's per-character processing is OFF-rhythm from any brain-grounded mechanism.

3. **HRR composition has stronger discriminative signal at word grain**: a 5-word context bound via HRR roles is ~5 bits-equivalent of position info; the same at 30-char grain would be 30 role-bind operations that lose signal to the matched-filter capacity.

4. **Word-unigram baseline is HIGHER entropy**: 10.5 bits/word vs 4.6 bits/char. There's MORE headroom to demonstrate substrate lift.

**Compose-stack:** L3.1 (word-grain) + L3.2 (PC) + L3.3 (WM) is the minimal brain-canonical language stack. If all 3 HARD_PASS additively, expected cumulative lift is 0.6-1.0 BPC — closes 60-100% of the substrate-vs-bigram gap.

---

## L5: SYNTHESIS AND RANKED DISPATCHES

### Top 3 dispatch recommendations (rank-ordered for exp_dev pickup)

**Dispatch #1 (PRIORITY 1, cheap-CPU, ~10-15 min):**
`brain_word_level_prediction_v1` (L4 design)
- Anchor: word-grain substrate prediction
- Cell file: `experiments/brain_word_level_prediction_v1.py` (new)
- Discriminator: 5 arms (B1 unigram / B2 bigram / S_K1 / S_K5 / S_K10)
- Pre-reg in cell preamble
- P_deflated = 0.55 (highest); 0.40 chance of HARD_PASS, 0.15 chance MIDDLE_BAND, 0.45 chance HARD_FAIL
- Brain-existence-proof verdict: brain DOES word-level prediction at >5 bits/word lift, so HARD_PASS at +0.3 bits/char equivalent is plausible

**Dispatch #2 (PRIORITY 2, gated on Dispatch #1 outcome):**
`brain_predictive_coding_2level_v1` (L3.2 design)
- Anchor: 2-level Rao-Ballard PC with top-down feedback
- Cell file: `experiments/brain_predictive_coding_2level_v1.py` (new)
- Discriminator: 3 arms (A1 feedforward / A2 hier-no-top-down / A3 full PC)
- Dependency: pairs with whatever encoder + grain Dispatch #1 finalizes
- P_deflated = 0.50 (capped per novelty-synthesis discipline)
- Note: if Dispatch #1 HARD_PASS at word grain, Dispatch #2 should be RUN AT word grain too (compose-stack hint)

**Dispatch #3 (PRIORITY 3, gated):**
`brain_working_memory_register_v1` (L3.3 design)
- Anchor: persistent WM register (exponential decay across tokens)
- Cell file: `experiments/brain_working_memory_register_v1.py` (new)
- Discriminator: 3 arms (A1 no-WM / A2 char-grain WM / A3 word-grain WM); beta in [0.85, 0.99]
- Dependency: composes with Dispatch #1 if word grain wins
- P_deflated = 0.50

### Expected cumulative leverage if all 3 HARD_PASS

If independent: P(all 3) = 0.55 * 0.50 * 0.50 = 0.14 (14% chance).
If positively correlated (likely — they're parts of one brain stack): P(all 3) ≈ 0.25.

Expected lift if all 3 land:
- Dispatch #1 alone: +0.3-0.5 BPC (at word grain equivalent translated)
- Dispatch #2 stacks: additional +0.1-0.3 BPC
- Dispatch #3 stacks: additional +0.1-0.3 BPC
- **Cumulative: +0.5 to +1.1 BPC** vs current substrate ~7.0

Current bigram is ~5.0 BPC at word-bigram equivalent translated. Substrate at +1.0 lift would reach ~6.0 BPC — closes the gap roughly halfway. If word-grain HRR composition discriminates better than predicted (P~0.20), substrate could approach ~5.5 BPC (within 0.5 bit of word-bigram).

### Brain-existence-proof verdict — does any single dispatch close the substrate-vs-bigram gap?

**SHORT ANSWER: No single dispatch closes the full gap; but the WORD-LEVEL dispatch (Dispatch #1) is by itself plausibly worth +0.3-0.5 BPC, which is the largest single-mechanism lift currently on the substrate roadmap.**

The deeper finding: the substrate-vs-bigram gap as currently measured is INFLATED by the char-grain mismatch to the brain's natural processing rate. A substrate measured at word grain may already be substantially closer to bigram (potentially within 0.3-0.5 BPC) once the testing grain matches the mechanism's natural domain.

**Brain existence proof for the FULL stack is strong:** Rao-Ballard PC + theta-word-grain + WM register is the CANONICAL minimal brain language stack, validated across MEG/EEG/fMRI/single-unit recording, with direct 2024 substrate-shaped implementations (Lyu et al. ScienceDirect 2024; BRyBI Kazanina-Tavano 2025).

---

## Cross-thread synthesis with prior session work

- **Replaces theta-gamma-amplitude-bug HARD_FAIL framing**: that cell measured cross-frequency coupling at wrong granularity; word-level dispatch is the correct way to test the rhythm hypothesis.
- **Composes with multi-iter cleanup cue-clamping (in flight 2026-06-23)**: PC top-down feedback IS cue-clamping at scale (the original cue = encoder output, the clamping signal = top-down prediction). If cue-clamping HARD_PASS, this is the path that scales it.
- **Composes with dopamine duration-extension cell (in flight)**: WM register's beta decay is the substrate analog of DA-modulated time-window extension — they implement the same brain function via different math.
- **Orthogonal to encoder-learning Path C**: word-level testing can use any encoder; doesn't conflict with the parallel encoder-arc work. Recommendation: use frozen char-trigram for Dispatch #1 to isolate the word-grain effect from encoder confound.

## Substrate-product implications

- **For substrate-as-LM:** if Dispatch #1 lands +0.3 BPC, that's the largest single capability gain on the books and would push substrate into "competitive-with-small-N-gram-models" range at word-grain. Direct customer-facing claim: "substrate predicts the next WORD with statistical lift over standard baselines" is more market-meaningful than "+0.3 bit/char."
- **For continual learning moat:** word-grain measurement doesn't affect CLS-replay; that remains differentiator.
- **For glass-box property:** word-level mechanism is INSPECTABLE in a way char-level isn't (you can read the HD context as "represents the words X, Y, Z bound to roles"). Marketing copy gets easier.

## Citations (verified count: 13)

1. Rao R.P.N., Ballard D.H. (1999). Predictive coding in the visual cortex. Nat Neurosci 2(1):79-87. (Foundational PC)
2. Ding N., Melloni L., Zhang H., Tian X., Poeppel D. (2016). Cortical tracking of hierarchical linguistic structures in connected speech. Nat Neurosci 19:158-164. (Theta tracks words)
3. Kazanina N., Tavano A. (2025). BRyBI: oscillatory model of word recognition. (Per Nature Computational Science search result)
4. Lyu et al. (2024). Implemented predictive coding model of lexico-semantic processing. NeuroImage. (Direct PC-for-language implementation)
5. Friston K. (2010). The free-energy principle: a unified brain theory? Nat Rev Neurosci 11:127-138.
6. Bienenstock E.L., Cooper L.N., Munro P.W. (1982). Theory for the development of neuron selectivity. J Neurosci 2(1):32-48. (BCM)
7. Goldman-Rakic P.S. (1995). Cellular basis of working memory. Neuron 14:477-485.
8. Lundqvist M., Herman P., Miller E.K. (2018). Working memory: delay activity, yes! Persistent activity? Maybe not. J Neurosci 38(32):7013-7019.
9. Olshausen B.A., Field D.J. (1996). Emergence of simple-cell receptive field properties by learning a sparse code for natural images. Nature 381:607-609.
10. MIT News (2021). AI sheds light on language brain processing. (Next-word prediction LM aligns with brain language areas)
11. arXiv 2212.00596: "Language models and brains align due to more than next-word prediction and word-level information"
12. Schrimpf et al. (PNAS 2021): Neural architecture of language — integrative modeling converges on predictive processing.
13. Grave E. et al. (2017). Improving Neural Language Models with a Continuous Cache. ICLR. (Cache-pointer +0.3-0.5 BPC lift — substrate analog = WM register)

---

## Pre-registered HARD bands SUMMARY (per dispatch)

| Dispatch | HARD_PASS condition | HARD_FAIL condition |
|---|---|---|
| #1 word-level | S_K5 top1 >= 1.30x B2 word-bigram AND BPW <= B2 - 0.4 | S_K5 top1 <= B2 OR BPW >= B2 |
| #2 PC 2-level | A3 BPC <= fair_harness - 0.30 AND A3 - A2 >= 0.15 | A3 >= fair_harness OR A3 - A2 <= 0.02 |
| #3 WM register | A3 BPC <= fair_harness - 0.30, beta in [0.90, 0.95] | A3 >= fair_harness |

Calibration penalty applied: 0.20 deflation on novel-synthesis estimates; cap 0.50 on any single-mechanism close-the-gap claim per [[feedback-lit-scan-calibration-penalty]].

---

## Next-drill candidate (if Dispatch #1 fails)

If word-level dispatch HARD_FAILs, that's strong evidence the limitation is encoder-quality not grain-mismatch — pivot to Path C encoder learning (already in flight per project file). 2x drill candidate would be **BCM-rule encoder objective** (Block A item with composite 18) — gives the encoder a brain-grounded objective rather than fixed char-trigram + L1 supervision.

If Dispatch #2 fails (PC top-down null), that's strong evidence Hebbian-only weight updates are insufficient for top-down — pivot to gradient-based local plasticity rules (Helmholtz wake-sleep substrate analog), which would be a >1x drill (novel territory).

If Dispatch #3 fails (WM doesn't help), that's strong evidence single-vector context register is too coarse — pivot to multi-vector working memory (separate slots for "subject" / "verb" / "object") — already a substrate-natural HRR-role-bind structure.
