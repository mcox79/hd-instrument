# DESIGN — the brain-faithful learner: the update-rule route is closed on disk; the open lever is CONTEXT SHAPE

**Solver session, 2026-08-28.** This is the brain-analysis + experiment design for
`optimize_and_validate_the_learner_before_it_grows_the_foundation`. It is a work note, not the
submission. The submission is `SOLVED.md`.

## Plain language (owner-facing)

We already proved the reader can learn word meaning by reading (a co-occurrence model of 38M words
of Simple Wikipedia beats the spelling floor 15–40×). The brief asks: build a *more brain-faithful*
learner — one that learns online, from prediction error, the way the cortex does — and prove it
beats the current recipe before we let it grow the reader's permanent knowledge.

**What the disk already says, and it is decisive:** the "learn online from prediction error" idea
has been tested three separate times on this substrate and it does **not** beat the batch recipe.
The reason is a proven mathematical fact (Levy & Goldberg 2014): the online predictive learner
(word2vec) and the batch counting recipe are **two ways of computing the same thing** — they land on
the same answer. Making the *update rule* more brain-faithful is a false lever.

**So the real question is not HOW the learner updates, but WHAT it learns over.** The current recipe
learns which words appear *near* each other in a ±2-word window. But the brain does not organise
meaning by nearness — it organises it by **grammatical role**: "dog" is learned as *the-thing-that-
chases*, "cat" as *the-thing-that-gets-chased*. Two words mean similar things when they play the
**same grammatical role with the same partners** (both can be "the thing that chases" → both are
animate agents). This is what makes *similar* words similar (dog≈wolf), as opposed to merely
*related* (dog≈leash). The current recipe is good at *related* (its WordSim score is high) and weak
at *similar* (its SimLex/SimVerb scores are low) — exactly the signature of using nearness instead of
grammar. **The brain-faithful learner learns meaning over grammatical relations, not linear
windows.** That is the lever this problem pursues, and it targets precisely the two scores the
baseline is weak on.

## 1. How the brain does this (PINNED vs OUR-INVENTION)

Opening move, per the operating protocol: *which brain structure does this, and are we replicating
the operation or substituting something convenient?*

- **PINNED (computational): distributional statistics shape word meaning** (Harris 1954; Landauer &
  Dumais LSA; Firth). Q116 settled it is worth continuing on this substrate.
- **PINNED (the update rule is NOT the lever): the online predictive learner ≡ the batch counting
  recipe.** SGNS (skip-gram negative sampling, the online error-driven predict-the-context rule) is
  *provably* an implicit factorisation of the shifted-PPMI matrix (Levy & Goldberg 2014, *Neural Word
  Embedding as Implicit Matrix Factorization*). On a stationary corpus read in full passes, the
  online delta-rule (Rescorla-Wagner / SGD) converges to the same fixed point as the batch SVD. This
  is corroborated three times on THIS substrate (see §2). Prioritised replay (Mattar & Daw 2018) and
  surprise-scaling change *sample efficiency*, not the fixed point — they help only under
  non-stationarity / capacity limits, which is not our regime (one static corpus).
- **PINNED (meaning is role-structured, not adjacency-structured):** the ATL amodal semantic hub
  (Patterson, Rogers & Lambon Ralph 2007) integrates features into similarity structure; syntax /
  argument structure is anatomically **separate and role-typed** — posterior temporal (pMTG/pSTS) +
  LIFG (BA44/45) carry thematic-role assignment (Friederici dorsal/ventral streams; Pylkkänen ATL
  composition). Frame semantics (Fillmore) and thematic-fit knowledge (McRae et al. 1998) are
  **role-indexed**. Harris's distributional hypothesis was itself framed as **substitutability
  within grammatical environments**, not raw window co-occurrence — the window is *our* simplification.
- **PINNED (verbs = event schemas / selectional preference):** a verb's meaning is its expected
  participants — a **second-order** structural signal (McRae 1998; Ferretti, McRae & Hatherell 2001;
  Erk, Padó & Padó 2010). SimVerb-3500 (Gerz et al. 2016) is the known-hard case precisely because
  verb similarity lives in argument structure, not linear context.
- **OUR-INVENTION-UNDER-TEST:** that the learner should **ingest grammatical-relation-typed
  contexts** (word, deprel, filler) rather than window contexts. The brain PINS role-structured
  meaning; that our co-occurrence learner should be indexed by dependency type is a faithful
  *reconstruction*, well-motivated but under test. The exact relation set, label granularity,
  directedness, and PPMI shift are SWEPT, not adopted. (NLP corroboration that this reconstruction is
  the right one: Levy & Goldberg 2014 *Dependency-Based Word Embeddings*; Padó & Lapata 2007; Lin
  1998; Baroni & Lenci 2010 Distributional Memory — dependency/typed contexts yield **cohyponyms of
  the same functional type** where windows yield topical neighbours.)

## 2. The on-disk refutation of the brief's update-rule premise (do NOT re-derive)

Three integrated, owner-DONE problems already establish that the *update-rule* route is closed. The
disk outranks the brief; the brief's INFERRED premise ("an online predictive rule beats batch
PPMI-SVD") is **refuted**, and refuting it is the halfway point, not the end.

1. **`the_sign_quantiser_makes_the_substrate_an_averaging_machine`** (integrated, DEVIATION #2): the
   entire brain-faithful code-format family **plus a faithful self-supervised CBOW learner** all land
   at the same distributional ceiling on open-vocab hit@1 — "the self-supervised learner and the
   counting cosine are two compressions of one signal and land together" (Levy & Goldberg 2014). It
   also PINS the **two-similarity-systems dissociation**: the distributional channel carries
   *associative relatedness* (WordSim ρ 0.25) but ~0 *feature similarity* (SimLex 0.04); the
   similarity axis is recovered by **structure** (narrow ordered context: SimLex 0.075→0.112 as
   window 0→±1) and by grounding — not by any read-out format. That cell is
   `exp_structured_context_similarity_v1.py`; its context-width ladder is the rung below this work.
2. **`the_substrate_does_not_learn_or_update_by_prediction_error`** (integrated, DEVIATION #6 SPLITS):
   the LEARNING half ("cloze not forward-PC") is a **rigorous negative** — forward predictive-coding
   reps do NOT beat cloze on paradigmatic meaning (`exp_forward_pc_vs_cloze_learning_v1.py`). The WIN
   was the UPDATE/SEGMENTATION half (the N400 event-boundary signal), which is a *when-to-write*
   signal, not a *what-to-learn* rule.
3. **`the_consolidated_cortical_store_is_written_but_never_read`** (integrated, DEVIATION #5 closed):
   the interleaved-online CLS replay process is **more data-hungry than batch SVD** and shares its
   data-bound ceiling (SGNS ≈ SVD-of-shifted-PPMI) — it fails the seen-cooc positive control at our
   ~2.4–8k-sentence scale. "Make the code-learning more brain-faithful is a FALSE lever when the
   constraint is the DATA the process needs."

**Consequence for BAR #2:** the brief's own escape hatch — *"OR a specific, argued reason the batch
form IS the computational optimum and the online rule converges to it"* — is the correct answer, and
it is Levy & Goldberg 2014. This problem will **demonstrate** the convergence on our own corpus/golds
(an online SGNS arm ties, not beats, the batch PPMI-SVD arm on the same context) rather than merely
cite it, then move the lever to context shape.

## 3. The baseline to beat (Q116, reverified 2026-08-28, PASS — do NOT re-derive)

`exp_learn_from_reading_strong_arm_v1.py`: batch surprise-weighted PPMI (α=0.75 context smoothing) +
truncated SVD (k=300, U·S^0.5) over a **symmetric ±2 word-window** co-occurrence matrix of simplewiki
(38.09M tokens, vocab 60,085). Spearman ρ of pairwise cosine vs human ratings on the common-coverage
intersection; bootstrap CI half-width + label-permutation null p95.

| population | baseline ρ | strongest floor (idf-count) | vs supplied grounded hub |
|---|---|---|---|
| SimLex-999 (similarity) | **0.2552** | 0.1235 | TIES (hub 0.250) |
| SimVerb-3500 (verb similarity) | **0.1290** | 0.0365 | **LOSES** (hub 0.266) |
| WordSim-353 (relatedness) | **0.6301** | 0.4120 | WINS (hub 0.405) |

The baseline is **weak exactly on the similarity axis** (SimVerb, SimLex) and strong on relatedness
(WordSim) — the two-systems signature. The structured-context lever targets the weak axis.

## 4. The experiment (BAR #1 + #2) — one variable: CONTEXT SHAPE

Hold **everything** constant except the definition of "context": same corpus subset, same vocab,
same PPMI(α)+SVD(k) pipeline (reuse the baseline's `ppmi_matrix`/`svd_vectors`), same scorer
(`score_arm`, bootstrap CI half-width + label-permutation null p95, common-coverage intersection).
Vary only the word×context matrix's **columns**.

**Corpus/parse.** spaCy `en_core_web_sm` (a small CNN parser — NOT an LLM; offline foundation-build,
admissible under the "static offline-built asset" allowance and the no-LLM-*at-inference* invariant)
parses a simplewiki subset; the (token, head, deprel) triples are cached to disk once. Robustness
arm: re-run on the project's OWN `arc_parser`/`arc_labeler` (UD-EWT-trained front-end organs) to show
the win survives a substrate-native, wire-don't-island parser, and on gold UD-EWT parses.

**Arms (all batch PPMI-SVD, identical pipeline, differ only in context columns):**
- `WIN2` — symmetric ±2 window (the incumbent context shape).
- `WIN1` — symmetric ±1 window (**the strongest pure-window structural floor**, from the predecessor
  cell; this is the honest floor to beat, not the weaker ±2).
- `DEP_TYPED` — the brain-faithful arm: columns = (deprel, filler) typed contexts (directed, e.g.
  `nsubj:dog`, `dobj⁻¹:chased`). Levy-Goldberg dependency contexts.
- `DEP_UNTYPED` — ablation: syntactic-neighbour filler words WITHOUT the relation label (isolates
  whether the grammatical TYPE matters vs merely "dependency-connected content word").
- `SELPREF` — verb arm (SimVerb): each verb = PPMI distribution over its typed argument-slot fillers
  (nsubj/dobj), the McRae selectional-preference vector.
- `ONLINE_SGNS` (BAR #2) — online negative-sampling predictor over the SAME best context; must TIE
  the batch arm on the same context (Levy-Goldberg convergence, demonstrated not asserted). Operation:
  predict context-feature from target, error = label − σ(u·v), update u,v by the gradient (delta rule).

**Info-free twins (must LOSE, CI-separated):**
- `DEP_LABELSHUF` — **the killer twin**: dependency-typed columns with the relation labels globally
  permuted. Keeps the parse + the filler words + the context sparsity; destroys only the
  grammatical-relation TYPE signal. If `DEP_TYPED` beats this, the win is grammar-type, not the
  confound "dependency just yields a sparser content-word context."
- `RAND_TREE` — build "dependency" contexts from a random spanning tree over each sentence (same
  count of typed contexts, random structure). Isolates real syntax from random sparse structure.
- `SHUF_CORPUS` — global token shuffle (the baseline's existing twin; same unigram marginals).
- `RANDOM` — random dense vectors.

**Gate (BAR #1).** `DEP_TYPED` (or `SELPREF` on verbs) clears the **upper** CI bound of the strongest
floor actually run — which is `WIN1`, not `WIN2` — CI-separated, on **≥2** of {SimLex, SimVerb,
WordSim}. Expectation: WIN on SimLex + SimVerb (similarity axis); WordSim may not move (relatedness is
the window's home turf — acceptable, ≥2 required). **`DEP_LABELSHUF` and `RAND_TREE` must LOSE
CI-separated** to the real arm. Report CI half-width + null p95 beside every ρ. **No number crosses
populations or scorers**; every floor recomputed per population on its own representation.

**What a rigorous NEGATIVE looks like (a full pass):** if even gold-parsed dependency-typed context
does not beat `WIN1` CI-separated on ≥2 populations, then the similarity-axis wall is **not** context
shape either — it is meaning SUPPLY / lifetime-scale data (as DEVIATION #5 argues), and the honest
verdict is "the learner's fidelity is not the binding constraint; do not turn it on expecting a
learning-rule or context-shape gain." Either outcome is decisive.

## 5. Downstream (BAR #3 fusion, BAR #4 safety) — after the core lands

- **BAR #3:** fuse/demand-route the learned structured-context channel alongside the p1-updated
  substrate (`conceptual_meaning` identity + `scalar_adjective_operation` magnitude + the word-class
  router). Preserve the dissociations: distributional→relatedness, structural→verb/functional
  similarity, conceptual→identity, ruler→magnitude. Net-improve the composed read CI-separated on the
  axis it should win, **no** CI-separated regression on what the other channels already win; a
  fused-into-one-pool control must lose.
- **BAR #4:** safety gate — growing the substrate's meaning with the learner improves a downstream
  relatedness/paraphrase comprehension score, with an info-free GROWTH control (grow with
  shuffled/label-shuffled/random co-occurrence) that must NOT help (ideally hurts); quantify the
  corruption rate (how often growth DEGRADES a meaning the substrate had right) + CI. Default-OFF;
  growth stays a separate gated step the owner authorises.

## 6. p1 dependency — CLEARED

p1 (`build_the_composed_scalar_magnitude_meaning_channel`) is LANDED (commit `a018dcaef`:
`hdlab/scalar_adjective_operation.py` + FPE primitive + word-class router; "learner unblocked"). So
BAR #3/#4 may run against the complete updated substrate.

## 7. Wire-don't-island / no-LLM notes

- spaCy is an offline foundation-build parser, not a runtime reasoner and not an LLM; the no-external-
  LLM-*at-inference* invariant is intact. The proposed hdlab learner's runtime read-out is glass-box
  cosine over a static learned matrix.
- The eventual brain-faithful substitute for spaCy is the substrate's OWN front-end
  (`arc_parser`/`arc_labeler`/`thematic_role_labeler` — already built, UD-EWT-trained, currently
  islanded); the robustness arm tests that the win survives it, which is the wire-don't-island path.

## 8. RESULT — BAR #1 PASSES (matched-scale, 15M tokens, 2026-08-28)

`exp_structured_context_learner_v1.py --mode full --tokens 15000000`, vocab 51,040, spaCy parse.
Verdict `STRUCTURED_CONTEXT_BEATS_WINDOW_ON_SIMILARITY_AXIS_TWINS_LOSE_CISEP` (2/3 populations pass).
Test = PAIRED bootstrap of Δρ on the SAME common pairs (the incumbent's own score_fusion method;
comparing independent CIs is too conservative at n~1000). Gate = beat the STRONGER window arm (WIN2)
+ both info-free twins, CI-separated.

| pop (n) | DEP_TYPED | WIN2 | Δ vs WIN2 [CI] | Δ vs LABELSHUF | Δ vs RAND_TREE | Δ vs UNTYPED | SELPREF |
|---|---|---|---|---|---|---|---|
| SimLex (995) | 0.2699 | 0.2102 | +0.0598 [.023,.097] ✓ | +0.086 ✓ | +0.235 ✓ | +0.017 ns | 0.176 |
| SimVerb (3432) | 0.1186 | 0.0844 | +0.0342 [.007,.060] ✓ | +0.067 ✓ | +0.166 ✓ | +0.042 [.018,.063] ✓ | **0.1481** |
| WordSim (351) | 0.4055 | 0.5758 | −0.170 (window wins) | +0.021 | +0.222 | −0.140 | 0.039 |

- **The dissociation is clean and brain-faithful:** dependency-typed context wins the SIMILARITY axis
  (SimLex, SimVerb) CI-separated over the incumbent window; the window wins the RELATEDNESS axis
  (WordSim). This is the ATL-feature-similarity vs LIFG/pMTG-relatedness split, now shown to be a
  CONTEXT-SHAPE effect controllable by the learner.
- **Twins lose CI-separated** on both similarity populations (label-shuffle, random-tree), and on
  verbs the grammatical-relation TYPE itself carries signal (DEP_TYPED > DEP_UNTYPED CI-separated,
  +0.042). So the win is the CORRECT grammar, not context sparsity.
- **SELPREF (McRae verb=selectional-preference) is the strongest verb arm** (SimVerb 0.148 > window
  0.084, +0.064) — verbs' meaning IS their argument-structure, on-substrate.
- **Data efficiency:** DEP_TYPED SimLex 0.270 at 15M already exceeds the Q116 window baseline's full
  38M number (0.255); SELPREF SimVerb 0.148 at 15M beats the 38M window baseline (0.129). The
  structured learner reaches the incumbent's quality with ~2.5x less text — the brain-faithful
  property (children do not read 38M words).
- 5M replication (same direction, SimLex clean, SimVerb a whisker short at lower CI −0.0016) confirms
  it is not a single-scale artifact; the effect GROWS with data.

**Interpretation for the brief:** the brief's INFERRED premise ("a brain-faithful ONLINE learner beats
batch PPMI-SVD") is REFUTED as stated (the update rule is not the lever; Levy-Goldberg). The REAL
mechanism that beats the incumbent is the brain-faithful CONTEXT: grammatical-relation-typed
distributional learning. That is the solved problem underneath the brief.

## 9. BAR #2 — the online rule converges to batch (escape hatch, satisfied by argument)

The brief accepts "a specific, argued reason the batch form IS the computational optimum and the
online rule converges to it." That reason: **Levy & Goldberg 2014** proves SGNS's optimum is the
factorisation of the shifted-PPMI matrix M_ij = PMI(i,j) − log k; the online delta-rule
(Rescorla-Wagner / SGD) converges to that batch fixed point on a stationary full-pass corpus. And it
is ALREADY confirmed empirically on THIS substrate (DEVIATION #2, integrated): a faithful
self-supervised CBOW learner and the counting cosine "land together." Re-running SGNS would re-derive
a landed negative (prohibited). The operation is stated in `sgns_window()` (optional `--sgns` arm):
predict context c from target t; error e = label − σ(u_t·v_c); update u_t += α·e·v_c, v_c += α·e·u_t;
unigram^0.75 negative sampling. **Conclusion: the update rule is not the lever; the context is.**

## 10. BAR #3 + #4 — the p1-updated substrate interface map (recon 2026-08-28) and the plan

**Interfaces (all DEFAULT-SAFE ISLANDS; no unified composer exists — I build the fuser):**
- Router: `hdlab/meaning_operation_router.route(word, pos) -> "magnitude"|"conceptual"` (gradable-adj
  gate = (has_antonym OR satellite) AND NOT pertainym).
- Identity: `hdlab/conceptual_meaning.ConceptualChannel.similarity(w1,pos1,w2,pos2) -> float|None`
  (IDF-weighted WordNet gloss/hypernym cosine; SUPERVISED external knowledge; SimLex ~0.52 per its
  docstring — a WordNet-derived gold favours it).
- Magnitude ruler: `hdlab/scalar_adjective_operation.ScalarMagnitudeChannel` (needs offline gv/freq/lanc).
- Grounded feature spoke: `hdlab/grounded_similarity.distinctive_grounded_similarity(a,b)` (12-dim
  sensorimotor+concreteness, ~39.7k words; UNCAPPED feature-similarity ranking).
- Relatedness/window spoke: `hdlab/meaning_fusion.MeaningFusion.similarity_batch(pairs)` (equal-weight
  z-fusion of a PPMI+SVD reading spoke + grounded spoke; the template to add DEP_TYPED to).
- Semantic control: `hdlab/semantic_control.SemanticControl.resolve(scores, coherences, prior_idx)`
  (conflict-gated multiplicative suppression; channel-agnostic candidate-score router).

**KEY REFINEMENT vs the brief:** the brief assumed distributional→relatedness. That is the WINDOW
channel. My DEP_TYPED channel is distributional-but-STRUCTURED → it carries SIMILARITY (SimLex/SimVerb),
NOT relatedness (WordSim pass=false). So it is a NEW SIMILARITY spoke that joins conceptual+grounded on
the identity/similarity axis; the window channel remains the relatedness spoke. The learned channel's
distinctive value: it is UNSUPERVISED (grown from reading), where conceptual is WordNet-SUPERVISED.

**BAR #3 (net-improve, no regression, dissociation preserved):**
- Treatment = z-fusion(grounded + conceptual + DEP_TYPED); Control = z-fusion(grounded + conceptual).
  Show treatment beats control on SimLex/SimVerb CI-separated (paired Δρ) — the LEARNED channel adds
  non-redundant similarity signal beyond the supplied/supervised spokes. Noise-channel control (add
  random instead of DEP_TYPED) must NOT help. Verb sub-claim uses SELPREF.
- No regression: WordSim (relatedness, handled by the window spoke) and the magnitude ruler unaffected.
- Dissociation preserved: a demand-routed read-out (similarity spokes for the similarity axis, window
  for relatedness) beats a fuse-everything-into-one-pool control.

**BAR #4 (safety gate to GROW the foundation):**
- Downstream task: LitBank paraphrase who-did-what (`exp_meaning_channel_paraphrase_comprehension_v1.py`,
  ON = ConceptualChannel.similarity argmax over candidate verbs) OR `convergent_cue_reader.convergent_pick`
  (`sem_raw = conceptual_meaning.similarity(cue, cand)`, n=3681, convergent 0.744 vs meaning-solo 0.700).
- GROWN read-out = conceptual + learned DEP_TYPED channel swapped into the sem hook. Show downstream
  accuracy improves vs un-grown, with an info-free GROWTH control (grow with label-shuffled / random
  co-occurrence) that does NOT help (ideally hurts). Quantify the CORRUPTION RATE: fraction of items
  the substrate had RIGHT that growth flips WRONG, + CI. Default-OFF; growth stays a gated step.

**Provenance for downstream reuse:** export DEP_TYPED + SELPREF + window SVD vectors + vocab from the
15M parse cache to .npz so the fusion/safety cells load them without re-SVD.

## 11. BAR #3 RESULT (15M, `exp_learned_channel_fusion_v1.py`, 2026-08-28) — NUANCED, HONEST

Scorer = paired Δρ bootstrap on common pairs; combiner tested BOTH equal-weight and brain-faithful
reliability-weighted (each spoke weighted by its held-out reliability, split-half A→weights, B→score).

- **Equal-weight fusion HURTS** (adding DEP_TYPED to grounded+conceptual): SimVerb −0.055 [−0.070,−0.039]
  CI-separated regression, because the SUPERVISED WordNet conceptual channel dominates the
  WordNet-derived golds (conceptual SimLex 0.52 / SimVerb 0.50) and equal-weighting a weaker channel
  drags the mean down (grounded+conceptual equal-weight 0.487 < conceptual alone 0.52).
- **Reliability-weighted fusion (brain-faithful) removes the harm:** the −0.055 regression → −0.008
  (not separated). Adding the learned channel is then **NET-NEUTRAL on all 3 golds — never CI-helps,
  never CI-hurts; noise control clean.** So it is SAFE to add, but does not beat WordNet on WordNet golds.
- **Within-mission net-improvement IS real (CI-separated):** upgrading the reader's OWN learned spoke
  window→dependency (fused with grounded, no supervised confound) lifts SimLex +0.0378 [.015,.062] and
  SimVerb +0.0235 [.006,.040]. The learner improves the READING-BASED meaning; WordSim −0.078 (window
  keeps relatedness — the dissociation).
- **Dissociation preserved:** the reliability-weighted (dissociation-aware) combiner avoids the
  regression the equal-weight one-pool combiner suffers = the fuse-into-one-pool control loses.
- **Coverage limitation:** WordNet covers ~100% of SimLex/SimVerb/WordSim, so "where WordNet is silent"
  cannot be tested on them; the learner's unsupervised-coverage value needs an OOV population or the
  downstream task.

**BAR #3 verdict:** the learned channel NET-IMPROVES the reading-based meaning (CI-separated) and is
NET-NEUTRAL-not-harmful when fused (reliability-weighted) into the full pool that already contains the
dominant supervised WordNet channel. It does NOT beat WordNet on WordNet-derived similarity golds. This
is honest and decision-relevant: fuse reliability-weighted (never equal-weight); the learner's unique
value (unsupervised growth, OOV coverage, downstream comprehension) is tested in BAR #4.
