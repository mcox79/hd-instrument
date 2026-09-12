# RESEARCH / SPEC — the ATTACHMENT organ (heads rung of the reading chain), 2026-09-12

**Owner:** "Make sure we fully understand what this organ should be doing, and are working to implement mathematical BF processes
for all potential consumers. How does the brain separate signals optimally?" This note is the spec the build must satisfy.

## 1. What the organ must compute (computational level)
For every word w_j in a sentence: a graded belief over WHICH OTHER WORD IT DEPENDS ON (its head h_j, or the root), jointly
constrained so the beliefs form a tree — and it must hand that belief DOWN as a distribution, never only an argmax.

**The brain's version (PINNED at the computational level, implementation-level details marked MODEL):**
- **Incremental constraint satisfaction / cue competition (PINNED).** Attachment is decided by the parallel integration of
  multiple partially reliable constraints — lexical (the head's argument frame / valence), categorial (what attaches to what),
  positional (locality), morphological (agreement), prosodic (boundaries), semantic (plausibility, thematic fit) and referential
  (discourse) — each weighted by its experienced reliability (MacDonald, Pearlmutter & Seidenberg 1994; Trueswell & Tanenhaus;
  Spivey & Tanenhaus 1998; the Competition Model, Bates & MacWhinney). This is the SAME structure as the role competition we
  landed today: cue values → learned strengths (log-validities) → additive activation → normalised posterior.
- **Memory-limited cue-based retrieval (PINNED, Lewis & Vasishth 2005).** When a dependent needs a head, candidates are
  RETRIEVED from working memory by cue match; activation decays with distance and suffers similarity-based interference. This is
  why LOCALITY is a cue (Gibson's DLT) and why the distance penalty in our scorer is the right shape (log-distance decay).
- **Keep alternatives alive, weighted by probability (PINNED: surprisal/rational parsing; Hale 2001, Levy 2008).** The
  comprehender maintains a graded distribution over analyses and reanalyses when a later word makes the current one
  improbable. The EXACT posterior over trees given additive arc scores is the Matrix-Tree marginal (MODEL: the normative limit of
  keep-alternatives-alive; `hdlab.graded_parser.single_root_marginals`). Incremental left-to-right maintenance with reanalysis
  is the brain's implementation; the batch Matrix-Tree is our fast equivalent and the graded signal it hands down is the same
  object (P(head | sentence) per token).
- **Learning = distributional acquisition from reading, never a treebank at inference (PINNED).** Category-pair attachment
  tendencies, verb frames and locality preferences are accrued from exposure; the self-supervised EM over the tree posterior
  (the cached reading-learned scorer) is a defensible MODEL of "the posterior teaches the cue statistics". Plastic: counts keep
  accruing (observe → consolidate), as the role labeler's validities now do.
- **Optimal separation of signals (the owner's question) — four principles the brain uses, each with our counterpart:**
  1. **Reliability weighting** (precision-weighted integration; Ernst & Banks; Ma & Pouget): each cue's vote = its learned
     log-odds validity. Counterpart: learned strengths, never hand-set.
  2. **Decorrelation before combination** (Barlow redundancy reduction; divisive normalisation): redundant cues must not be
     double-counted. Counterpart: the configuration-conditioned CONTRASTS we found necessary for roles (two overlapping
     post-verbal cues double-counted and sent "give me a call" to OTHER until merged into one coalition).
  3. **Normalisation into a population code** (softmax / divisive normalisation): the posterior over candidates, not a winner.
  4. **Global consistency by exact marginalisation** where the constraint is hard (one head per word, a tree): the Matrix-Tree
     marginal distributes the evidence optimally across competing arcs instead of greedy commitment.
  5. **Pre-lexical form knowledge enters as constraints, not as words**: punctuation = written prosody → boundary cue and
     "never a head"; numerals = form class. Measured today: 0.463 → 0.476 on the full-scale scorer; 0.012 → 0.036 on the
     fine-category chain (the punctuation class had been crowned root by a frequency-driven root prior).

## 2. The cues (values read from toks / categories / heads-so-far; strengths learned)
| cue | value | brain basis | status in our stack |
|---|---|---|---|
| locality | log distance, direction | DLT / activation decay | in SelfSupEM (λ·log(d+1)) — keep, learn λ |
| category pair | (cat_head, cat_dep, dir) | distributional acquisition | in SelfSupEM (cpair) — keep; needs the functional coarse classes (fine 70-way fails; see hand-off probes) |
| lexical frame / valence | head lemma's argument frame (takes obj? recipient? complement?) | verb-frame knowledge (learned) | EXISTS for roles (`frame` cue, `verb_subcat`) — NOT in the attachment scorer yet |
| form class | head candidate is punctuation / numeral → cannot head | orthographic route | measured +0.007 / +0.024 today; to land |
| prosodic boundary | # of punctuation marks the arc spans | closure at boundaries | measured +0.006 (full) / +0.022 (fine) today; to land |
| agreement | number match subject–verb (morphology) | morphological cue | available (`gn` morphology in the reader) — not in the scorer |
| animacy / plausibility | dependent animacy × head frame | thematic fit (Competition Model) | animacy lexicon exists — not in the scorer |
| pre-verbal slot / clause edge | is the pre-verbal slot filled; clause boundaries | first-noun strategy | in the role competition — shareable |
| referential context | definiteness / prior mention of the dependent | Altmann–Steedman | entity tokens exist downstream — later |

## 3. Consumers and their SIGNAL REQUIREMENTS (what a BF consumer needs from heads)
| consumer | needs | reads today | loss at the hand-off |
|---|---|---|---|
| role competition (`coarse_role_cues`: head class × order) | P(head) per nominal → marginalise the configuration over heads | the parser's hard head | 0.083 on GUM (v13 decomposition); `graded_parser.marginals` exists, not consumed |
| predicate-argument frontend (patient / agent slots) | the verb's nominal dependents with attachment confidence | hard heads + labels; `_argstruct_learned_pick` can take marginals | head errors = 12% of gold patients mis-attached (diag) |
| copular binding (state) | the copula's predicate + its subject dependent | hard heads | copular subjects 0.72–0.78 |
| entity mention source (`referent_per_np`) | NP spans: compound/flat/amod attachments | hard heads | unmeasured |
| affected-entity resolver | clause-mate co-argument (Principle B), same-clause membership | hard heads | part of the −0.0117 HEADS loss on the 596 items |
| temporal / causal / negation extraction | clausal attachments (advcl, ccomp, mark) | hard heads | unmeasured on this chain |
Every one of them should read `P(head)` (and the derived P(dependents of v)) — the hand-off repair pattern is the same as for
labels: consume the distribution, threshold inside the consumer, keep abstention as a value.

## 4. Build plan (REUSE, one structure): attachment as an arm of the Competition-Model organ
1. **Cue functions** `attachment_cues(toks, cats, i, h)` in `hdlab/graded_role_assigner.py` (the cue-competition organ):
   locality (binned log-distance × direction), category pair (coarse functional class of head and dependent), frame (head lemma's
   valence from the learned per-lemma counts), form class (candidate is punctuation/numeral), boundary (marks spanned),
   agreement (number), animacy × frame. Values categorical; strengths = configuration-conditioned contrasts learned by the SAME
   learner machinery (`strengths_from_counts`, plastic `observe`).
2. **Learning without a treebank:** the outcome for each (dependent, candidate) pair is the Matrix-Tree POSTERIOR of the current
   model (self-supervised EM: the posterior teaches the counts) — the cached `SelfSupEM` EM rounds are exactly this for the
   category-pair cue; generalise to all cues (soft counts weighted by the arc marginal).
3. **Combination:** arc score = Σ cue contrasts (+ root score); exact tree posterior via `single_root_marginals`; MAP via CLE
   only where a consumer insists on a point.
4. **Hand-down:** `graded_parser.marginals`-shaped `P(head | token)`; the role competition marginalises its head-class cue over it
   (the `coarse_role_posterior_tagmarg` pattern, for heads); the frontend's `_argstruct_learned_pick` already accepts marginals.
5. **Measurement ladder:** UD-EWT test UAS (gold categories first, then reading-induced), adjacent-right floor + shuffled twin;
   then the 596-item decision (probe v13) and the board's who-did-what / state rows.
Today's baselines to beat: cached scorer 0.4626 (gold POS, λ=0.3, Naseem prior pw=3.0 = a hand-authored linguistic prior, to be
REPLACED by the learned cues), +form +boundary 0.4755; supervised 0.782; floor 0.285.

## 5. Sources
MacDonald, Pearlmutter & Seidenberg 1994 (constraint-based lexicalist); Trueswell, Tanenhaus & Garnsey 1994; Spivey & Tanenhaus
1998; Lewis & Vasishth 2005 (cue-based retrieval); Gibson 1998/2000 (DLT, locality); Hale 2001, Levy 2008 (surprisal /
rational parsing); Kjelgaard & Speer 1999 (prosodic boundaries); Altmann & Steedman 1988 (referential context); Ernst & Banks
2002, Ma & Pouget 2006 (reliability-weighted integration); Barlow 1961 (redundancy reduction); Carandini & Heeger 2012
(divisive normalisation); Koo et al. 2007 / Smith & Smith 2007 (Matrix-Tree marginals for dependency parsing).

## 6. Measured against the spec (2026-09-12, same day)
| build | UAS (UD-EWT test 700, gold categories) | note |
|---|---|---|
| adjacent-right floor | 0.285 | |
| cached reading-learned scorer (teacher; hand-authored Naseem prior pw=3) | 0.4626 | pri-2's best |
| teacher + form-class constraint + prosodic boundary (decode-time) | 0.4755 | constraints measured first |
| **attachment CUE COMPETITION, r0 (taught by the teacher's tree posterior)** | **0.4715** | no hand-authored prior; learned conditioned contrasts |
| **attachment cue competition, r1 / r2 (anchored self-teaching)** | **0.4801 / 0.4834** | the best label-free attachment in the substrate; twin 0.092 |
| unconditioned additive cues (smoke) | drifted 0.41 → 0.37 | decorrelation by conditioning is load-bearing |
| shuffled-strength twin (smoke) | 0.03 | |
| lexical cue at 1.5k sentences (smoke) | −0.02 | too sparse; needs volume (lever 1 before lever 2) |
| heads → roles hand-off (role competition over P(head)) | 0.8075 → 0.8091 role accuracy | small on UD-EWT; GUM next |
Open: experience volume (probe v20: 20k/60k Simple-Wiki sentences), the lexicon at scale, meaning feeding structure, incremental
prediction; then hand the posterior down to every consumer in §3 and re-measure the 596-item decision and the board rows.

## 7. LANDING GATE (owner 2026-09-12: "brain-foundational, compatible with the way we hold knowledge, efficient")
1. **BF bootstrap, no indirect hand-authored knowledge.** The v18 student was taught by a cached teacher whose EM used the
   Naseem universal prior (pw=3, a hand-written head-dependent table) → contamination by proxy. GATE: the student must reach its
   number when bootstrapped from a PRIOR-FREE learner (categories + locality only; `SelfSupEM(prior_weight=0)`), or from its own
   cues with a uniform start. Test first (probe v18 variant), land only what passes.
2. **One knowledge form, one lexicon.** Strengths stored as COUNTS → `strengths_from_counts`-style pure function → plastic
   `observe(...)` / `save(...)` exactly like the role validities (soft counts are floats in the same table shape). Per-lemma
   attachment preferences (the lexical cue) JOIN the existing verb-frame table (`verb_subcat` / the role labeler's lemma_frames):
   ONE per-lemma frame entry {transitivity, recipient propensity, dependent-class × direction preferences}, registered in
   `notes/KNOWLEDGE_ASSET_REGISTER.md` as grown knowledge — not a second frames asset (anti-fragmentation).
   DISK TODAY (audit 2026-09-12): THREE per-lemma tables already exist — `data/verb_subcat_supply_optimized_v2/verb_subcat_final_avg.json`
   (trans_ratio = mean of a WordNet-frame ratio and corpus counts; read by `verb_subcat.transitivity`), `data/frontend_assets/
   verb_subcat_frames_ud_ewt.json` (298 lemmas: infinitival complement counts), and the role labeler's `lemma_frames` inside the
   validity asset (recipient share). The attachment lexical cue would be a FOURTH. Landing = ONE `lexicon_argument_frames` grown
   asset (lemma → transitivity, recipient, complement, dependent-class × direction preferences; counts, plastic) with one accessor
   in the Competition-Model organ; the three tables fold into it (byte-identical consumers first, then the merged read).
3. **One organ, one cue pass.** Attachment is an ARM of `graded_role_assigner` (the Competition-Model organ): cue extraction per
   sentence ONCE (vectorised numpy over the n×n candidate grid: distance bins, category pairs, boundary counts from a punctuation
   cumsum, form mask) shared by the attachment and the role competitions; the head posterior (Matrix-Tree) computed once per
   sentence and READ by every consumer (§3) — no consumer re-parses. The probe's per-arc Python loops are measurement-only.
4. **Efficient learning.** Soft counts accrue online (plastic); the self-teaching anchor (α) and the EM round count are swept
   parameters; consolidation periodic, not per sentence; the reading budget grows with the corpus the category learner already
   reads (same pass).
Nothing lands until 1 passes and 2–3 are the implemented form.
