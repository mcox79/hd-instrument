# Research 5x-drill 3/5 — Neuroscience deep-drill on brain-analog encoder held-out-synonym HARD-FAIL

**Date:** 2026-07-02
**Author:** research (Opus deep-drill)
**Drills sourced:** 3 parallel Sonnet lit-scans (VWFA/dual-route; ATL hub-and-spoke; CLS + sparsity + sparse-coding-on-text)
**Scope:** why our monolithic sparse-competitive-Hebbian encoder (k=2%, Foldiak-1991 lineage) LOSES to trivial bag-of-char-trigrams on held-out-synonym retrieval over WordNet / Wikipedia — and the concrete brain-analog fix for v2.

---

## HEADLINE

**Monolithic sparse-competitive-Hebbian at k=2% is architecturally the DENTATE-GYRUS side of CLS trying to do a task the ANTERIOR-TEMPORAL-LOBE side owns; it is missing three components — VWFA-analog surface n-gram bank, ATL-hub-analog dense amodal convergence layer, and semantic-control gating. The "trivial bag-of-char-trigrams" is not a caricature — it IS the mid-VWFA computation. v2 architecture must be a 3-stream parallel-cascade, NOT a scaled-up monolith.**

**P_deflated (missing-components verdict): 0.48** (base 0.75 → -0.25 novel-synthesis cap + calibration → 0.50 cap; strongly supported by three independent lit lines: SD lesion + VWFA n-gram tuning + CLS assignment).

---

## 1. Prior-work check — cross-thread synthesis

Substrate-KB prior hits (Director already surfaced these; not re-cited):

| Note | Relevant section | What it said | What THIS drill ADDS |
|---|---|---|---|
| `research_drill_fact_representation_rethink_5x_2026-06-08.md` §2.2 | "Cortical Semantic Memory" | Cortex does distributed semantic storage; hippocampus is episodic | Now names the SPECIFIC CLS mismatch: our k=2% is DG-CA3 parameters, task lives in ATL-hub geometry |
| `wave14d_icl_via_pool_research.md` §7.1 | "Hippocampus-cortex CLS" | CLS-style dual system as generic reference | Now applies CLS to synonym retrieval specifically; assigns synonym task to cortical/DENSE side with lesion evidence (SD) |
| `wave14c_r3_K64_total_collapse_research.md` §7.1 | CLS reference | High-level framing only | Substantively: shows R3-K64 collapse was ALSO wrong-CLS-side symptom |
| `research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md` §3.4 | "Burial depth principle" — load-bearing features generalize, surface features fail on paraphrase | Load-bearing = semantic (buried); surface = orthographic (shallow) | Names the missing burial-machinery: the ATL-hub IS the burial mechanism; without it we ONLY have surface features |
| `data/substrate_index/school/atoms.jsonl` (`Sparse coding (neural)` atom + CLS family) | Sparse coding as brain mechanism | Descriptive | Now the CLS atom needs an amend: sparse coding is DG-only within CLS; cortical semantic is NOT sparse coding |

**What is genuinely NEW here (relative to substrate-KB):**
1. Explicit assignment of held-out-synonym retrieval to ATL-hub (Patterson-Rogers-Ralph 2007) with the specific rTMS-mimics-SD evidence (Pobric et al. 2007 PNAS).
2. VWFA / Local-Combination-Detector (Vinckier et al. 2007 Neuron) as literal brain-analog for char-2/3/4-gram detector bank — bag-of-trigrams is not "trivial," it's the mid-VWFA operation.
3. Quantitative sparsity table pinning k=2% to DG-CA3 territory, not cortical semantic territory.
4. Empirical: NO published existence proof of pure sparse-competitive-Hebbian delivering held-out-synonym retrieval on real corpora (Faruqui, Murphy-NNSE, Arora, SPINE all sparsify AFTER dense distributional stats).
5. Concrete v2 prescription: 3-stream A+B+C parallel-cascade, timings, and hard-fail thresholds.

---

## 2. Brain sparsity by region + task-appropriate sparsity — where does 2% land?

Quantitative table (sources: lit-scan #3 above; Marr 1969; Leutgeb 2007; Barth-Poulet 2012; Rolls-Tovee 1995; Olshausen-Field 1996; Rigotti 2013; Cayco-Gajic-Silver 2019; Litwin-Kumar 2017):

| Region | Sparsity (% active) | Function | k=2% match? |
|---|---|---|---|
| Cerebellum granule | 1–5% | pattern separation for motor error correction | YES |
| DG (dentate) | 2–4% | pattern-separated episodic index | **YES — this is where we are** |
| CA3 pyramidal | 2–5% place-active | recurrent episodic completion | YES |
| CA1 pyramidal | 5–10% | HC output; interfaces cortex | high |
| MTL "concept cells" | lifetime-sparse (Quiroga) | invariant recognition; NOT bulk semantic | lifetime≠population; not directly comparable |
| V1 lifetime | 5–15% | sparse coding of natural images (Olshausen-Field) | too sparse |
| IT / face patches | ~10–20% | invariant visual recognition | too sparse |
| Neocortex L4 (granular) | dense | thalamic input relay | wildly too sparse |
| Neocortex L2/3 pyramidal | 1–5% spontaneous; task-dependent | associative computation | close, but different DYNAMICS |
| Neocortex L5 (output) | denser sustained firing | motor / decision output | too sparse |
| PFC / association | dense, mixed-selectivity (Rigotti 2013) | task-flexible cognition | wildly too sparse |
| ATL semantic hub | DENSE distributed (Rogers-McClelland 2004 PDP model) | amodal semantic geometry | **wildly too sparse — inverted regime** |

**Litwin-Kumar et al. 2017 Neuron "Optimal Degrees of Synaptic Connectivity":** optimal sparsity for expansion-layer associative computation is **intermediate ~5–10%**, not 1–2%. Extreme sparseness shrinks coding subspace (Cayco-Gajic & Silver 2019 Neuron) and HURTS pattern separation past a point.

**2% verdict:** k=2% sits in the **DG-CA3 sparse-orthogonal episodic-indexing regime.** For held-out-synonym retrieval — which requires overlap-based interpolation across distributional neighbors — this is a fundamental architectural mismatch. Cortical semantic geometry is DENSE distributed by design; sparse-orthogonal codes deliberately MINIMIZE overlap → they cannot generalize by feature overlap.

The brain uses **different sparsity per region** (L4 dense, L2/3 sparser, L5 denser, ATL DENSE, DG sparse). Our monolithic k=2% is architecturally too rigid; it imposes a single regime globally.

---

## 3. VWFA / bag-of-substrings — the brain HAS a literal char-n-gram encoder

**Char-trigram-BoW is NOT trivial. It is the mid-VWFA computation.**

Key evidence (Dehaene 2005 TICS; Vinckier et al. 2007 Neuron; Glezer-Jiang-Riesenhuber 2009 Neuron; Woolnough et al. 2021 Nat Hum Behav):

- **Vinckier 2007 fMRI-adaptation ladder** (false-font → infrequent letters → freq letters/rare bigrams → freq bigrams/rare quadrigrams → freq quadrigrams → real words) showed a **monotonic posterior→anterior gradient** — posterior VWFA responds to letter-like shapes; mid-VWFA to bigram statistics; anterior VWFA to quadrigram + lexical statistics. Peak surface tuning: **2–4 characters (bigram–quadrigram range)** = exact "trigram" regime.
- **Bigram-frequency BOLD scaling:** Binder 2006; Vinckier 2007; Woolnough 2021 iEEG all show VWFA activity scales monotonically with letter-string bigram frequency even for pseudowords → VWFA caches language-specific n-gram statistics.
- **Local Combination Detector (LCD) model** (Dehaene 2005) — hierarchy of oriented bars → letter-shape (case-invariant) → local bigrams → quadrigrams / short morphemes / small word forms. This IS a learned hashed-n-gram filter bank feeding a lexicon.
- **Grainger & Whitney 2004 open-bigram model:** letter-position coding via unordered set of contiguous + non-contiguous ordered pairs — explains transposed-letter priming (jugde primes JUDGE). This is more permissive than sparse-hashed trigram BoW but same family.
- **Pure alexia** (VWFA lesion): letter-by-letter reading, but **synonym retrieval preserved** in auditory modality (Coslett & Saffran 1989). Diagnostic: the surface-orthographic stage is **separate** from the semantic system.

**The substrate skipped the entire surface-encoding stage.** Our sparse-competitive-Hebbian encoder tries to jump straight from raw text to a sparse-orthogonal semantic-ish code with NO intermediate n-gram-statistics tier. The bag-of-char-trigrams baseline outperforms us because it emulates the VWFA/LCD tier, which is a well-tuned surface-statistics representation.

**What is missing from our encoder relative to VWFA:**
- Hierarchical composition (bar→letter→bigram→quadrigram)
- Position-conditioned + open-bigram coding
- Case/font/character-identity normalization
- Language-specific n-gram frequency caching
- Separate semantic system DOWNSTREAM (see §4)

---

## 4. ATL hub-and-spoke — the semantic organ we're missing

**Patterson-Nestor-Rogers 2007 Nat Rev Neurosci** ("Where do you know what you know?") + **Lambon Ralph-Jefferies-Patterson-Rogers 2017 Nat Rev Neurosci** ("neural and computational bases…"): ventrolateral ATL = amodal semantic hub; modality-specific spokes (vision/audition/motor/orthographic-lexical/olfaction) fan into hub, hub fans back out. Hub distills modality-INVARIANT conceptual similarity.

Load-bearing evidence for hub-as-synonym-organ:

- **Semantic dementia (SD) — bilateral ATL atrophy.** First-to-break tasks: synonym judgment, Pyramids-and-Palm-Trees (Howard-Patterson 1992), Camel-and-Cactus (Bozeat 2000), feature-listing, category verification. **Preserved:** single-word repetition, digit span, syntax, phonology, episodic memory, VWFA-based reading of regular words (Woollams et al. 2007 Psych Rev). Empirical delta: synonym-retrieval loss ~40–60 percentage points in moderate-severe SD (Jefferies-Lambon-Ralph 2006 Brain; Jefferies-Patterson-Jones-Lambon-Ralph 2009). **This is EXACTLY the failure profile: surface reading preserved, synonym retrieval collapsed.**
- **Pobric-Jefferies-Lambon Ralph 2007 PNAS:** rTMS to bilateral ATL in healthy adults **mimics SD synonym-judgment deficits.** Causal role, both hemispheres needed.
- **Hub is DENSE, not sparse.** Rogers et al. 2004 Psych Rev PDP simulation: the ATL hub layer in the winning computational model is **densely coded (distributed activation, not sparse WTA).** Damage produces graded feature-drift, over-regularization to prototypes, preserved coarse category — signature of DISTRIBUTED not localist codes. **k-WTA at 2% cannot exhibit the graded-similarity behavior on which "synonym = same meaning" depends.**
- **MVPA / RSA evidence:** Peelen-Caramazza 2012 J Neurosci — ATL patterns discriminate object categories independent of input modality (word vs. picture) → truly amodal. Bruffaerts 2013 — RSA in ATL matches semantic-feature similarity structure orthogonal to visual/lexical similarity.
- **Graph-theoretic hub:** Jackson et al. 2016 J Neurosci; Xu et al. 2017 J Neurosci — ventrolateral ATL has **disproportionately high nodal degree** in whole-brain semantic network. Hub is defined by its fan-in topology, not just its function.
- **Second system: semantic control** — Lambon-Ralph 2017 update names a **second interacting system**: left IFG + pMTG for task-biased semantic control. Without it, hub retrieval is uncontrolled → over-regularization.

**Our substrate has NO hub analog.** The sparse-competitive-Hebbian monolith operates at "spoke depth" — surface-form statistics only. Held-out synonyms require crossing the spoke→hub barrier, and that barrier requires (a) dense amodal convergence layer, (b) fan-in from multiple spokes, (c) graded semantic geometry.

---

## 5. CLS analysis — right family, wrong side

**McClelland-McNaughton-O'Reilly 1995 Psych Rev** + **Kumaran-Hassabis-McClelland 2016 TICS** update. The theory PRESCRIBES two systems:

| System | Coding | Learning | Task |
|---|---|---|---|
| Hippocampus (DG-CA3-CA1) | **Sparse, pattern-separated, orthogonal** (~2%) | Fast, one-shot, episode-specific | Episodic retrieval, pattern separation |
| Neocortex (semantic) | **Dense, distributed, overlapping** | Slow, interleaved, statistical-regularity extraction | Semantic gist, category, generalization |

**Norman & O'Reilly 2003 Psych Rev** — concrete network instantiation: hippocampus subnet uses k-WTA + DG pattern separation; MTLC subnet is a distributed autoencoder giving a FAMILIARITY scalar. **Semantic retrieval (synonyms, gist, category) lives in MTLC/cortex, NOT hippocampus.**

**Verdict:** our concept_encoder is architecturally the CORTICAL-slow-dense side (task is semantic overlap), but we implemented it with HIPPOCAMPAL sparse-orthogonal parameters. **Right family (bio-plausible learning), wrong CLS side for the task.**

This is not a hyperparameter issue. Running k-WTA at 2% on a semantic task is **running the DG algorithm on a task the ATL is built for.** No CLS-family paper puts synonym retrieval on the sparse hippocampal component. The vocabulary-mismatch problem (Furnas et al. 1987 CACM) is the CANONICAL documented failure of sparse-token codes on synonym tasks; the field's diagnosed fix was **DENSE latent** (Deerwester 1990 LSA; Landauer-Dumais 1997 Psych Rev "Plato's problem" — dense LSA matches TOEFL synonyms at near-human level).

**No published existence proof of pure sparse-competitive-Hebbian on held-out synonyms over real corpora.** Every successful sparse-text method — Faruqui et al. 2015 ACL "Sparse Overcomplete Word Vector Representations"; Murphy-Talukdar-Mitchell 2012 COLING NNSE; Arora et al. 2018 TACL discourse atoms; Subramanian et al. 2018 AAAI SPINE — sparsifies AFTER a DENSE distributional statistic (PPMI, GloVe, skip-gram). Foldiak 1990 Biol Cybern flagged capacity + generalization limits at inception. Modern Hopfield (Ramsauer et al. 2020) EXPLICITLY moved away from discrete WTA to dense softmax — precisely because sparse WTA does not scale to retrieval-generalization.

---

## 6. Multi-stream parallel composition — reading + semantics are NOT serial

Timing hierarchy from MEG/iEEG (Tarkiainen 1999; Maurer 2005; Hauk 2006; Lau-Phillips-Poeppel 2008 Nat Rev Neurosci; Chen 2013 iEEG; Woolnough 2021):

- ~100 ms: V1/V2 low-level retinotopic
- **~150–200 ms:** VWFA orthographic (M170) — surface n-gram statistics
- ~200–250 ms: sublexical grapheme-phoneme assembly
- **~250–400 ms:** N400 semantic access (ATL + angular gyrus)
- ~400–600 ms: post-lexical integration, P600

**Not strictly serial.** Woolnough 2021 iEEG: orthographic-semantic activity **overlaps**; top-down feedback into VWFA arrives by ~250 ms. Architecture is CASCADED-INTERACTIVE.

**Dual-route reading (Coltheart et al. 2001 Psych Review DRC model):** lexical route + sublexical GPC route in PARALLEL. Sublexical wins on novel words / misspellings; lexical wins on irregular words. Double dissociation (surface dyslexia vs phonological dyslexia) confirms neural separability.

**Bag-of-trigrams wins on our task because it emulates the always-available sublexical/mid-VWFA route.** Our substrate skipped it entirely and tried to do everything with one sparse-orthogonal layer. Monolithic 2% k-WTA does all four brain jobs (surface, morphological, semantic-hub, episodic) alone at 2% and fails at all four. The failure isn't "brain-analog was wrong" — it's "we picked ONE brain mechanism and asked it to do FOUR jobs."

---

## 7. NEUROSCIENCE VERDICT

**MISSING COMPONENTS.** The brain-analog mechanism family (sparse-competitive-Hebbian) is not architecturally wrong; it is one legitimate component (the DG-analog / episodic pattern-separator). The FAILURE MODE is that we implemented it as a MONOLITH doing 4 jobs, three of which the brain assigns to DIFFERENT anatomical regions with DIFFERENT sparsity, DIFFERENT coding regime, and DIFFERENT connectivity.

Specifically missing:
- **VWFA/LCD-analog:** hashed char-n-gram detector bank (dense, hierarchical, position-conditioned)
- **ATL-hub-analog:** dense amodal convergence layer with fan-in from ≥2 spokes and divergent projections back
- **Semantic-control-analog (pMTG/IFG):** task-biased retrieval gating
- **CORRECT ASSIGNMENT:** current k=2% Hebbian is legitimate as an EPISODIC / hippocampal component but MISASSIGNED to the semantic-retrieval task

Brain-best-in-class prior UPHELD: brain solves the exact task the substrate is failing at (SD patients before ATL atrophy pass PPT/CCT at >98%; controls pass synonym judgment at ceiling). We just picked the wrong ONE of the brain's mechanisms for the job.

---

## 8. CONCRETE EMULATION PRESCRIPTION FOR v2 ARCHITECTURE  ***(LOAD-BEARING SECTION)***

### 8.1 Three-stream architecture

**Mechanism A — VWFA/LCD-analog surface encoder** (SPOKE — orthographic)
- **Brain region:** VWFA (left mid-fusiform, MNI ≈ −42,−57,−15)
- **Job:** fast parallel surface-orthographic n-gram statistics; the "posterior VWFA to anterior VWFA" gradient of bigram→quadrigram
- **Substrate implementation:**
  - Hashed char-2/3/4-gram bank (~65K buckets, MurmurHash or FeatureHasher)
  - Letter-identity normalization (lowercase, ASCII fold, optionally NFD then strip diacritics — this is the case-invariance / retinotopic normalization the brain does upstream)
  - **Optional refinement:** open-bigram support (Grainger-Whitney 2004) — allow gaps of 1–2 chars for transposed-letter robustness
  - **DENSE representation** — no k-WTA on Mechanism A. Occupancy of hash buckets is graceful and matched to the ~2–4 character bigram-quadrigram tuning of Vinckier 2007.
  - Trained (or fixed) on the same corpus; TF-IDF or PPMI weighting on n-gram counts is the parallel to language-specific frequency caching (Woolnough 2021).
- **Composition:** projects into hub (Mechanism B) via random projection or shallow MLP to dim = hub_dim (e.g. 512–1024).

**Mechanism B — ATL-hub-analog dense amodal semantic layer** (HUB)
- **Brain region:** ventrolateral ATL apex, bilateral
- **Job:** amodal semantic convergence; graded similarity geometry; the organ semantic dementia destroys
- **Substrate implementation:**
  - **Distributed DENSE projection layer** — dim 512–2048, NO k-WTA, NO hard sparsity constraint. Soft L2 normalization only.
  - **Fan-in from ≥2 spokes.** Minimum v2 spokes: A (VWFA/n-gram), plus a distributional spoke (see below). Optionally add character-position spoke.
  - **Distributional spoke input:** PPMI (positive point-wise mutual information) matrix from co-occurrence on the same corpus, dim-reduced by SVD to ~256 dims. This is the "slow interleaved cortical learning" of McClelland 1995 CLS — extracts statistical regularity across many contexts. Dense by construction.
  - **Cross-modal Hebbian binding rule** (or simple concatenation + shallow projection): for each corpus item, integrate A-spoke pattern + PPMI-spoke pattern → hub attractor. This is the convergence-divergence-zone operation of Damasio 1989 / Meyer-Damasio 2009.
  - **Interleaved training:** slow multi-pass, small learning rate. This is the McClelland-1995 anti-catastrophic-interference mechanism, absent from one-shot Hebbian.
- **Composition:** dot-product or cosine over hub geometry gives synonym retrieval directly.

**Mechanism C — Semantic-control gating** (Ralph-2017 "second system")
- **Brain region:** left pMTG + left IFG (pars triangularis)
- **Job:** task-biased retrieval; suppresses irrelevant hub competitors; controls semantic access
- **Substrate implementation:**
  - Query-conditioned **softmax attention** over hub retrieval (this is EXACTLY the Ramsauer et al. 2020 modern-Hopfield update rule — dense continuous softmax over stored patterns).
  - Temperature τ controls competition sharpness; τ→0 gives WTA (bad), τ ≈ 1 gives graded (good), τ→∞ gives uniform (bad). Learned or set per-task.
  - **This slot is where "modern Hopfield" lives in the brain-analog frame:** hub retrieval via softmax IS the ATL-hub-controlled-by-pMTG-IFG operation.
- **Composition:** applies to Mechanism B output at query time; not a separate encoding stage.

### 8.2 KEEP: episodic hippocampal-DG-analog (RENAMED, RE-SCOPED)
- **Brain region:** DG-CA3-CA1
- **Job:** one-shot episodic binding, pattern separation for distinguishing similar-but-distinct items
- **Substrate implementation:** current sparse-competitive-Hebbian at k=2% is legitimate HERE — but for episodic tasks (recall this specific fact, distinguish similar entities), NOT for held-out-synonym generalization.
- **This is a role re-assignment**, not a deletion. The mechanism was correctly brain-analog; the DEPLOYMENT was mis-targeted.

### 8.3 Composition rule (PARALLEL, not serial)

```
       Query text
           │
           ├─────────► A (VWFA n-gram) ─────► spoke output A
           │                                       │
           ├─────────► PPMI spoke        ─────► spoke output PPMI
           │                                       │
           │                                       ▼
           │                              B (ATL hub — dense)  ◄── Hebbian bind
           │                                       │
           │                                       ▼
           │                              C (softmax control, τ)
           │                                       │
           └─────────► D (DG episodic sparse) ─────┤ (optional, for episodic tasks)
                                                   ▼
                                          retrieval output (synonyms)
```

Retrieval score = softmax over cosine(hub(query), hub(candidate_i)) with temperature τ, tie-broken by A-spoke n-gram overlap for surface-similar competitors. This is CASCADED-INTERACTIVE per Woolnough 2021 iEEG timing.

### 8.4 Falsifiable predictions (with HARD-PASS + HARD-FAIL) — calibration penalty applied

Held-out synonym top-1 retrieval on WordNet synset pairs, ~10K test pairs, corpus = English Wikipedia sub-sample. Baselines: current sparse-competitive-Hebbian encoder; char-trigram BoW.

| Mechanism | HARD-PASS threshold | HARD-FAIL threshold | P_deflated |
|---|---|---|---|
| **A alone (VWFA-analog n-gram)** | matches char-trigram baseline within 2 pts top-1 | worse than char-trigram by >3 pts | 0.55 |
| **A + B (n-gram + dense PPMI-SVD hub)** | beats char-trigram by ≥5 pts top-1 (novel-synthesis regime — see calibration cap) | ≤2 pts over char-trigram | **0.40** (base 0.60 → -0.20 novel-synthesis + calibration → capped 0.40) |
| **A + B + C (add softmax control)** | beats A+B by ≥2 pts top-1 | flat / degrades | 0.30 |
| **Full: A+B+C beats current sparse-monolith by ≥10 pts** | ≥10 pt improvement over current | ≤3 pt improvement | **0.35** (deflated) |

Novel-synthesis cap applied at 0.50 per [[feedback-lit-scan-calibration-penalty]].

### 8.5 Substrate-product implications

- **cap_map:** row "brain-analog monolithic encoder" should be marked **STRUCTURALLY-CLOSED with rescue path** — the CORRECT rescue is component-decomposition (A+B+C), NOT parameter-tuning of the monolith.
- **Product framing:** the substrate's "brain-inspired encoder" story survives — we just move from "one mechanism does everything" to "multiple brain-inspired mechanisms composed as the brain composes them." The pitch strengthens because we can now cite specific brain regions per component.
- **Kills:** the belief that scaling k, sparsity, or dimensionality on the CURRENT sparse-competitive-Hebbian will fix held-out-synonym retrieval. It won't. Litwin-Kumar 2017 + Cayco-Gajic-Silver 2019 formally rule out extreme sparseness even in expansion-layer regimes.

---

## 9. Cheap decisive test  (≤1 hour on local_cpu — MANDATORY)

**Test name:** `spoke_plus_hub_vs_monolith_synonym_ablation`

**Setup:** WordNet synset held-out pairs (≥5K), Wikipedia sub-sample corpus (~100MB tokenized).

**Three arms:**
1. **Monolith (current):** sparse-competitive-Hebbian at k=2%.
2. **Trigram spoke only (A):** char-trigram BoW, TF-IDF weighted, L2 normalized, cosine retrieval.
3. **Spoke + Hub (A + B):** concat(A_vector, PPMI-SVD-256 vector) → L2 normalize → cosine retrieval.

**Metric:** top-1 accuracy on held-out synonym pairs.

**Arbitration:**
- If **Arm 3 > Arm 2 by ≥5 pts top-1 AND Arm 3 > Arm 1 by ≥10 pts:** MISSING-COMPONENTS verdict CONFIRMED. Proceed to v2 architecture as prescribed (§8.1). Trigger `hdi_exp_dev` spawn for full v2 build.
- If **Arm 3 ≈ Arm 2 (within 2 pts):** the PPMI-SVD hub is NOT delivering the semantic-generalization win — dense hub needs richer training signal than raw PPMI (e.g. skip-gram or transformer-derived). Missing-components verdict still holds but hub-implementation prescription needs upgrade.
- If **Arm 3 < Arm 2:** either the concat integration is broken (integration = shallow projection instead), or PPMI hub is not learning the right geometry. Investigate hub before re-verdict.

**Cost estimate:** PPMI-SVD-256 on 100MB Wikipedia sub-sample: ~15 min single-core. Trigram BoW: ~5 min. Retrieval + eval: ~5 min. Total ~30 min → safely inside 1h budget.

**This test is decisive because:** the current failure mode ("2% sparse-competitive-Hebbian < char-trigram") could in principle be (i) missing components, or (ii) monolith parameters wrong, or (iii) both. Test isolates hypothesis (i) by adding the minimal hub component. If it moves the needle >5 pts, hypothesis (i) is confirmed and prescription §8.1 is the path. If it doesn't, we've falsified the hub-analog-is-load-bearing claim and must re-drill.

---

## 10. Citations — verified count 40+

Grouped by lit-scan angle.

### VWFA / dual-route (15)
1. McCandliss BD, Cohen L, Dehaene S. 2003. TICS 7:293–299.
2. Dehaene S, Cohen L, Sigman M, Vinckier F. 2005. TICS 9:335–341.
3. Vinckier F et al. 2007. Neuron 55:143–156.
4. Cohen L, Dehaene S et al. 2000. Brain 123:291–307.
5. Glezer LS, Jiang X, Riesenhuber M. 2009. Neuron 62:199–204.
6. Woolnough O et al. 2021. Nat Hum Behav / PNAS.
7. Coltheart M, Rastle K, Perry C, Langdon R, Ziegler J. 2001. Psych Rev 108:204–256.
8. Jobard G, Crivello F, Tzourio-Mazoyer N. 2003. NeuroImage 20:693–712.
9. Taylor JSH, Rastle K, Davis MH. 2013. Psych Bull 139:766–791.
10. Grainger J, Whitney C. 2004. TICS 8:58–59.
11. Whitney C. 2001. Psychon Bull Rev 8:221–243.
12. Laszlo S, Federmeier KD. 2010. Psychophysiology 47:1099–1108.
13. Coltheart M, Patterson K, Marshall JC. 1980. *Deep Dyslexia*. Routledge.
14. Plaut DC, Shallice T. 1993. Cognitive Neuropsych 10:377–500.
15. Hauk O et al. 2006. NeuroImage 30:1383–1400.

### ATL hub-and-spoke (13)
16. Warrington EK. 1975. QJEP 27:635–657.
17. Damasio AR. 1989. Cognition 33:25–62.
18. Hodges JR, Patterson K, Oxbury S, Funnell E. 1992. Brain 115:1783–1806.
19. Howard D, Patterson K. 1992. *Pyramids and Palm Trees Test*.
20. Bozeat S et al. 2000. Neuropsychologia 38:1207–1215.
21. Rogers TT et al. 2004. Psych Rev 111:205–235.
22. Rogers TT, McClelland JL. 2004. *Semantic Cognition: A PDP Approach*. MIT Press.
23. Patterson K, Nestor PJ, Rogers TT. 2007. Nat Rev Neurosci 8:976–987.
24. Pobric G, Jefferies E, Lambon Ralph MA. 2007. PNAS 104:20137–20141.
25. Meyer K, Damasio A. 2009. TINS 32:376–382.
26. Binder JR, Desai RH. 2011. TICS 15:527–536.
27. Peelen MV, Caramazza A. 2012. J Neurosci 32:15728–15736.
28. Lambon Ralph MA, Jefferies E, Patterson K, Rogers TT. 2017. Nat Rev Neurosci 18:42–55.

### CLS + sparsity + sparse-coding-on-text (16)
29. Marr D. 1969. J Physiol 202:437–470.
30. Cayco-Gajic NA, Silver RA. 2019. Neuron 101:584–602.
31. Leutgeb JK et al. 2007. Science 315:961–966.
32. Quiroga RQ et al. 2005. Nature 435:1102–1107.
33. Olshausen BA, Field DJ. 1996. Nature 381:607–609.
34. Barth AL, Poulet JFA. 2012. TINS 35:345–355.
35. McClelland JL, McNaughton BL, O'Reilly RC. 1995. Psych Rev 102:419–457.
36. Kumaran D, Hassabis D, McClelland JL. 2016. TICS 20:512–534.
37. Norman KA, O'Reilly RC. 2003. Psych Rev 110:611–646.
38. Landauer TK, Dumais ST. 1997. Psych Rev 104:211–240.
39. Faruqui M et al. 2015. ACL:1491–1500.
40. Murphy B, Talukdar P, Mitchell T. 2012. COLING.
41. Foldiak P. 1990. Biol Cybern 64:165–170.
42. Ramsauer H et al. 2020. NeurIPS / arXiv:2008.02217.
43. Rigotti M et al. 2013. Nature 497:585–590.
44. Litwin-Kumar A et al. 2017. Neuron 93:1153–1164.
45. Furnas GW et al. 1987. CACM 30:964–971.

**Verified count: 45 primary references.** All from the three parallel lit-scans; no synthesis-time added citations.

---

## Return summary line (for chat)

```
research: delivered 5x_drill_3_neuroscience → notes/research_5x_drill_3_neuroscience_substrate_content_HF_2026-07-02.md ; HEADLINE: monolithic sparse-competitive-Hebbian at k=2% is DG-CA3 regime running an ATL-hub task — MISSING VWFA-analog + ATL-hub-analog + semantic-control; v2 needs 3-stream A+B+C parallel-cascade; P_deflated=0.48; concrete v2 mechanisms: A=hashed char-2/3/4-gram bank (dense, VWFA-analog), B=dense amodal semantic hub (PPMI-SVD or skip-gram fan-in, ATL-analog, no k-WTA), C=softmax-controlled retrieval (modern-Hopfield / pMTG-IFG-analog); cheap decisive test: 3-arm ablation Wikipedia+WordNet held-out synonyms, A+B beats trigram-alone by ≥5 pts arbitrates MISSING-COMPONENTS verdict
```
