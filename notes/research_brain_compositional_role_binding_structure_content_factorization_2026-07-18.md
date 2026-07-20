# Research drill — BRAIN-DRILL 5x: compositional/systematic role-filler generalization
(2026-07-18)

USER directive framing: "the brain clearly does this, so we KNOW it can be done" — drill HOW,
then design AROUND that mechanism. Biology-led, 4 parallel Sonnet lit-scan lanes (generic
math/neuro terms only, no substrate-novel terms off-platform per query-privacy discipline),
synthesized here. Lit-scan calibration penalty applied throughout (P deflated 0.15-0.25;
novel-synthesis P capped at 0.50). Prior work credited to build ON, never "taken."

Component under test: the learned text->role ENCODER for the reading pipeline must bind
"who-did-what-to-whom" AND generalize to NOVEL role-filler combinations (a known filler in a role
never seen in before) — the exact COGS/SCAN failure mode of flat architectures (16-35% held-out
vs ~98% for built-in-compositional parsers, per the 07-18 prior-art-scour note). This drill is the
FIRST component of the learned reader + its chain-grade target.

Cross-thread note: this drill is a DIFFERENT cut than the same-day
`research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md` note (which
covered thematic-role assignment via multi-cue competition / SRL / OpenIE — the "how does the
brain decide WHICH role a filler gets" question). THIS drill covers "how does the brain hold the
ROLE apart from the FILLER so a filler never seen in that role still slots in correctly" — the
systematicity/generalization question. The two are complementary halves of one encoder.

---

## HEADLINE

**The brain's answer to Fodor-Pylyshyn systematicity is a two-part, convergent mechanism, and our
substrate already has the algebraic half of it.** (1) The general-purpose NEURAL binding operation
is **conjunctive coding** (a new composite representation for a role-filler pair), NOT
synchrony — the "Synchrony Unbound" critique and null perceptual-binding results substantially
undercut gamma-binding as the general solution; conjunctive coding's clean mathematical
descendant is **outer-product / tensor-product binding**, and VSA's circular-convolution bind
(our substrate's native operation) is a compressed, distributed instance of exactly that
operation. (2) The specific brain system that demonstrably REUSES a fixed relational
scaffold with NEW content — the closest existing account of "held-out role-filler
generalization" — is the **hippocampal-entorhinal cognitive map**, computationally formalized
by the **Tolman-Eichenbaum Machine (TEM, Whittington/Behrens 2020)**: a learned, content-blind
structural code **g** (MEC/grid-cell analog) is bound to a content code **x** via an
outer-product-like conjunction to form the hippocampal code **p = bind(g, x)**, and because g
never encodes filler identity, the SAME learned g-machinery transfers zero-shot to brand-new
content. This is a well-evidenced GENERAL account for spatial/graph/conceptual domains
(confirmed via gridlike codes during purely conceptual and social-hierarchy tasks) but has
**NOT yet been demonstrated for language/symbolic role-filler binding** — that gap is exactly
where our contribution would sit, and it is genuine, not already claimed.

Ranked brain mechanism for the compositional encoder: **(a) TEM-style factorized
structure-scaffold bound to content, IMPLEMENTED via conjunctive/outer-product-class binding
(i.e., our native FHRR bind), trained/refined via Gentner-style comparison across varied
examples (progressive alignment)** — this beats synchrony (weak/critiqued as a general
mechanism) and beats LISA-style hand-engineered structural alignment (unscalable) on both
brain-fidelity and buildability grounds.

---

## (1) BINDING PROBLEM — lane 1 findings + ranking

Three candidate neural binding mechanisms, ranked by empirical support as a GENERAL-PURPOSE
solution (not just a plausible model):

1. **Conjunctive coding (strongest).** Dedicated/distributed neurons responding to specific
   feature/role COMBINATIONS (hippocampal item-place conjunctive coding; PFC mixed selectivity).
   Direct single-unit evidence, scales via coarse/low-order conjunctions (not exhaustive tensor
   blowup — matches VSA literature's "optimal quadratic binding" work on relational expressivity
   without full tensor blowup). Vector-algebra analog: **tensor-product / outer-product /
   circular-convolution binding — a NEW composite vector is created**, supporting approximate
   unbinding via similarity search. This is a static representational solution, not a timing one.
2. **Attention-based binding (dynamic control layer).** Feature Integration Theory (Treisman &
   Gelade 1980): pre-attentive parallel feature maps + a serial attentional spotlight that binds
   features at a location into one object-file; illusory conjunctions under load are the
   diagnostic failure mode. Recent work reads transformer attention as an approximate/soft VSA
   binding operator (queries/keys=roles, values=fillers, attention weights=differentiable
   unbind) — this is the DYNAMIC layer deciding *which* conjunctions form/get read out,
   complementing (1), not competing with it.
3. **Synchrony/gamma binding (weakest as general solution).** Singer/von der Malsburg's
   correlation theory is historically influential but "Synchrony Unbound" (Shadlen & Movshon,
   Neuron 1999) argues no downstream reader of synchrony has been identified, and Thiele &
   Stoner found perceptual binding with NO synchrony change. Capacity is believed NOT to scale to
   deep hierarchical/recursive structure. Best treated as a plausible low-level
   perceptual-grouping signal, not the brain's symbolic-binding solution.

**Working synthesis (lane 1):** conjunctive coding supplies the REPRESENTATIONAL substrate (a
bound vector), attention supplies the DYNAMIC control (which bindings form/are read), synchrony
is a weak/contested perceptual-grouping mechanism only.

---

## (2) VARIABLE BINDING + SYSTEMATICITY — lane 2 findings

Three named theories, each addressing Fodor-Pylyshyn (1988) directly:

- **SHRUTI (Shastri & Ajjanagadde 1993):** role-filler bindings = synchronous rhythmic firing;
  rules are fixed feedforward circuits, so ANY filler (including novel ones) instantly and
  correctly fills a known role in a known rule — genuine but NARROW systematicity. Hard capacity
  ceiling (~10 simultaneous bindings, phase-crosstalk-bounded); shallow rule depth/recursion;
  never scaled past hand-built toy KBs.
- **LISA (Hummel & Holyoak 1997/2003):** synchrony-based role-filler binding across a
  role/filler/sub-proposition/proposition hierarchy; generalization via STRUCTURAL ALIGNMENT
  (relational role-structure, not memorized pairs) — but the alignment/mapping algorithm itself
  (CWSG) is fixed/hand-engineered, and capacity drops fast with more objects/relations/depth.
  Weakest of the three on scalability.
- **Semantic Pointer Architecture / VSA (Eliasmith; Spaun 2012):** binding = circular
  convolution, unbinding = circular correlation, superposition = vector addition, implemented
  down to spiking neurons (NEF). The bind/unbind algebra is FIXED and content-agnostic, so any
  novel filler vector generalizes "for free" through the same operation — the clearest
  "bind now, generalize automatically" story of the three, and it is the direct descendant of
  **Smolensky's tensor-product variable binding (1990)**, itself the original connectionist
  reply to Fodor-Pylyshyn (a reply Fodor & McLaughlin 1990 contested as not yielding causally
  efficacious constituent structure — an unresolved debate, noted honestly).

**Lane-2 ranking:** SPA/VSA (and its tensor-product ancestor) is literally OUR bind/unbind
operation, not merely analogous to it — for novel-combination generalization without retraining
the binding machinery, it and SHRUTI both give the guarantee in principle (fixed algebraic/
temporal operator, content-agnostic), LISA is weakest (hand-engineered mapping, poor scaling).

---

## (3) STRUCTURE-CONTENT FACTORIZATION / COGNITIVE MAPS — lane 3 findings (PRIMARY)

**Grid cells (MEC) vs. place cells (hippocampus)** is the classic biological instance of
structure/content division of labor: grid cells fire in a content-independent periodic hexagonal
lattice (generic metric/relational scaffold); place cells bind that scaffold to environment-
specific sensory content (remapping = same structure, new content).

**Tolman-Eichenbaum Machine (TEM; Whittington, Muller, Mark, Chen, Barry, Burgess, Behrens,
*Cell* 2020)** — the load-bearing citation, confirmed via full-text read:

- A learned structural code **g** (MEC analog) is generated by a transition model that
  path-integrates over actions/edges of a graph; trained across MANY different graphs/
  environments to satisfy two constraints: distinct g at distinct nodes, and IDENTICAL g when
  the same node is revisited via a different path. These transition weights encode only
  **graph topology / action semantics — never sensory identity** — so the same g-generating
  machinery transfers zero-shot to brand-new environments.
- The hippocampal code **p** is formed by a **conjunctive/outer-product-style binding of g and
  x** (content code) — the paper's own supplementary material describes this as "equivalent to
  an outer product." p vectors are stored via simple Hebbian associative learning into a matrix
  M; recall is attractor/pattern-completion dynamics.
- Because M is re-learned per environment while the g-generating weights are SHARED and FROZEN,
  TEM binds one learned relational scaffold to entirely novel content it has never seen bound to
  that structure before — **this is literally TEM's mechanism for zero-shot structural transfer**,
  and it reproduces grid/border/band/object-vector cell types and hippocampal remapping as
  emergent byproducts (not hand-built in).

**Generalization beyond space, confirmed empirically:** Constantinescu, O'Reilly, Behrens
(*Science* 2016) found the SAME hexagonally-symmetric grid signal during purely CONCEPTUAL
navigation (birds varying continuously in neck/leg length, no physical movement) — and a
related result found gridlike codes for social-hierarchy inference. Behrens et al. (*Neuron*
2018, "What Is a Cognitive Map?") and Bellmund/Gärdenfors/Doeller/Behrens (*Science* 2018,
"Navigating Cognition") argue this is a domain-general relational-organization mechanism, not
spatial-navigation-specific.

**Honest gap (do not over-claim):** TEM's own follow-ons (Whittington et al. 2022, showing
TEM's binding/retrieval math is equivalent to transformer self-attention with recurrent
position encoding; and a 2026 hippocampal-inspired world-model paper) stay within
spatial/graph/video world-model domains. **No published work has demonstrated TEM-style
structure-content factorization for language-scale relational reasoning or symbolic
role-filler binding specifically.** Treat "TEM-style scaffold-reuse explains compositional
generalization" as strongly supported for low-dimensional spatial/conceptual/graph structure,
and as an UNTESTED EXTRAPOLATION for language role-binding — which is exactly the gap this
program would fill, honestly flagged as such (not already claimed by anyone).

---

## (4) DEVELOPMENT — lane 4 findings

- **Trajectory is gradual, not innate-and-fixed.** Nonce-verb overhearing paradigms show 5-year-
  olds do NOT generalize a novel argument-structure construction's linking rule to new argument
  combinations under the SAME input that 7-year-olds/adults do generalize from — item-based
  imitation of surface form precedes abstract slot-filling (some earlier-onset findings exist for
  specific alternations, so exact onset age is contested, but the field weight favors protracted
  development). Tomasello's usage-based account: "verb islands" (item-specific frames) gradually
  coalesce into abstract schemas via comparison across many frames — a genuinely LEARNED
  abstraction process, not a switched-on module (nativist accounts contest this as a performance-
  vs-competence issue; reported fairly, unresolved).
- **Comparison/structural alignment (Gentner) is a CAUSAL mechanism, not incidental.**
  Progressive alignment (easy, highly-alignable comparisons first, harder near-misses later) is
  necessary: 3-year-olds only learned relational categories when given BOTH relational language
  AND a progressive-alignment comparison sequence — neither alone sufficed. Comparison across
  varied examples is what extracts shared relational structure while backgrounding surface
  differences.
- **Computational (2020s) confirmation:** compositional generalization in neural sequence models
  is provably tied to DIVERSITY of the training distribution past a threshold, not architecture
  alone (2025 theoretical analysis) — but pure data scaling does NOT guarantee compositional
  generalization in all regimes (visual compositional generalization counter-finding), so some
  minimal representational/attentional capacity likely remains necessary alongside diversity.
- **Not frozen after childhood.** Schema refinement via comparison continues into adulthood;
  critical-period work shows sensitive windows exist but plasticity is not fully shut off.

**Synthesis (honest, inconclusive on exact division of labor):** the mechanism that turns
item-specific memorized combinations into abstract, systematically-generalizing structure is
**(d) a combination weighted toward (b) comparison/alignment**, operating on **(a) sufficiently
diverse examples**, with **(c) some minimal capacity/bias** still probably required — no single
study cleanly isolates these three factors; that is an honest, unresolved literature gap, not a
hedge invented here.

---

## (5) DESIGN VERDICT — ranked brain mechanism + glass-box VSA encoder

### Ranking

| Candidate | Brain-fidelity | Buildability in our VSA substrate | Verdict |
|---|---|---|---|
| **(a) Factorized structure-scaffold bound to content (TEM-style)** | Strong for spatial/graph/conceptual; UNTESTED for language (honest gap) | **HIGH** — the bind operation is literally our native FHRR bind; only the g-generator is new | **WINNER** |
| (c) Semantic-Pointer / VSA learned binding | Strong (SPA is a full spiking-neuron implementation of this exact algebra) | Native — this already IS our substrate | **The implementation layer of (a)**, not a separate candidate — TEM's outer-product conjunction and SPA's circular convolution are the same operation at different compression levels |
| (b) Synchrony/conjunctive binding as literally-synchronous | Weakest for synchrony-as-timing (critiqued); conjunctive-as-representation is strong but that IS (a)/(c) | Buildable but synchrony-as-timing has no natural substrate analog (we are not a spiking/phase system) | Conjunctive-coding-as-representation is folded into (a)/(c); literal phase-synchrony REJECTED as the target mechanism |

**Verdict: (a) and (c) are not competing candidates — they are the same mechanism at two levels
of description** (TEM's outer-product conjunctive bind = the un-compressed neural version;
FHRR circular convolution = the compressed, high-dimensional-vector version of the identical
operation). This convergence across three independent literatures (binding-problem lane 1's
conjunctive-coding winner, variable-binding lane 2's SPA/tensor-product winner, and structure-
content lane 3's TEM outer-product mechanism) is the strongest single finding of this drill: it
is NOT three different opinions, it is the SAME operation surfacing three times from three
different research traditions.

### Concrete glass-box VSA compositional-encoder design

1. **Content code x** — already have this (grounded word/concept vectors, up-front dictionary
   grounding per the current arc).
2. **Structural code g** — a LEARNED, content-blind generator producing a role/slot vector from
   the CONSTRUCTION + POSITION context only (verb-frame identity, argument-slot index, e.g.
   "SVO slot-1" / "ditransitive slot-3"), analogous to TEM's transition model over graph
   topology — g must NEVER see filler identity, only structural/positional context. Trained
   across MANY constructions (the small enumerable Construction-Grammar inventory: SV, SVO,
   SVOO, SVO-PP, passive) to satisfy TEM's two constraints translated to language: (i) distinct
   g for distinct role-slots, (ii) IDENTICAL g when the same role recurs across different
   sentences/fillers/constructions (a role-invariance property that is the direct generalization
   lever).
3. **Bind:** p = bind(g, x) via native FHRR circular convolution — the compressed algebraic
   instance of TEM's outer-product conjunction and of conjunctive-coding's "new composite
   representation."
4. **Store:** superpose/bundle p vectors into the growing situation-model store (Kintsch textbase
   analog; TEM's Hebbian associative matrix M analog); query by unbind — already our native
   operation.
5. **Generalization mechanism (why held-out combinations work):** because g is trained ONLY on
   role/construction-position (never on filler content) and bind is a FIXED algebraic operator
   independent of which content vector is plugged in, ANY filler — including one never
   encountered in that role before — binds correctly by construction. This is TEM's exact
   zero-shot-transfer argument (frozen transition weights + novel environment content) and
   SPA/VSA's exact "fixed bind operator, novel vectors generalize for free" argument, now
   applied to language role-slots instead of graph nodes.
6. **Learning/improving g (per the development lane, so this is FLEXIBLE not frozen):** train g
   with a Gentner-style progressive-alignment / comparison objective — present VARIED
   constructions where the SAME role is occupied by DIFFERENT fillers and enforce (i)
   invariance of g across fillers in the same role (contrastive "pull together"), (ii)
   distinctness of g across different roles (contrastive "push apart"); curriculum orders
   easy/highly-alignable construction pairs before harder near-miss pairs (progressive
   alignment, empirically necessary per lane 4, not optional). g keeps refining with more
   exposure — never locked in early, consistent with the "not frozen after childhood" finding.
7. **Dynamic control layer (optional, lane-1 attention mechanism):** at read/query time, a
   routing step selects which stored p's to retrieve/compose for multi-hop queries — maps to
   our EXISTING reasoning-map/resonator machinery, kept separate from the encoder itself.

### Brain-check — where does OUR substrate hit a REAL bound? (don't pre-assume the outcome)

All three neuro/VSA lines converge on the SAME capacity limit: SHRUTI's ~10-simultaneous-
binding phase-crosstalk ceiling, conjunctive/tensor coding's combinatorial blowup (forcing
coarse, low-order conjunctions), and VSA/SPA's superposition noise scaling with number of
simultaneously-bound pairs — these are THREE INDEPENDENT DERIVATIONS of the same wall: **there
is a real, bounded number of simultaneous role-filler bindings before crosstalk/interference
degrades retrieval, in the brain AND in any VSA-class substrate.** This is a **same-limit ->
ACCEPT** case, not a fixable gap — our FHRR bind/bundle already documents K/N-style
capacity cliffs (cap_map) that are the same phenomenon. Design implication: keep the
per-proposition role-inventory SMALL and enumerable (2-4 roles per verb frame, matching the
Construction Grammar inventory already scoped in the companion thematic-roles note) rather than
trying to bind arbitrarily many simultaneous roles into one vector — this is brain-faithful, not
a workaround.

---

## Cheap decisive test

**A COGS/SCAN-style held-out role-combination split**, adapted to our grounded-word setting:
train the g-encoder + native bind on a corpus covering fillers {A...K} appearing in roles
{agent, patient, recipient, instrument, location} across the small construction inventory, but
WITHHOLD specific (filler, role) pairs from training (e.g., "glass" seen only as
patient/theme, never as instrument or agent) — then test whether the reader correctly assigns
"glass" to instrument/agent role in a novel sentence at test time. Compare against a FLAT
baseline (a bag-of-words or non-factored sequence model mapping sentence -> triple directly,
with no separate g/x factorization) trained on the SAME corpus.

**Design gate check (per experiment-design-gate discipline):**
- Real baseline: flat/non-factored model on the identical corpus, not abstain-all.
- Difficulty ON: the split must actually withhold role-filler pairs (not just novel sentences
  with familiar pairs); include a role-reversal minimal pair ("the dog bit the man" / "the man
  bit the dog") to confirm role-SENSITIVITY, not bag-of-words scoring.
- One variable: hold the corpus and vocabulary fixed; vary ONLY the encoder architecture
  (factored g+bind vs flat).
- Independent gold: relation triples scored against a held-out gold set not generated by the
  same process that trained the model.

---

## Falsifiable predictions

**HARD-PASS:** the factored structure-scaffold encoder (g + native bind) achieves relation-F1 on
HELD-OUT role-filler combinations that is substantially above the flat baseline — target gap
comparable in KIND (not necessarily magnitude) to the published COGS flat-vs-compositional gap
(flat ~16-35% vs compositional-architecture ~98%; we deflate this expectation and would count
**>=15-20 percentage points of relation-F1 gap on held-out combinations** as a genuine pass,
not the full COGS magnitude) — AND the gap should NOT be attributable to overall accuracy
differences on IN-DISTRIBUTION combinations (both models should be comparably strong there;
the gap must be specific to the held-out condition). AND a positive learning curve: held-out
performance improves as training-set role/filler DIVERSITY increases (per the 2025
diversity-threshold finding), not flat/no-improvement with more data.

**HARD-FAIL:** the factored encoder TIES the flat baseline on held-out combinations (both
degrade similarly, e.g. within ~5 percentage points of each other) — meaning the g/x
factorization provides no compositional edge in practice, i.e., either (i) g is not actually
content-blind (leaking filler identity through training shortcuts), or (ii) the bind operation's
generalization guarantee does not survive contact with a learned (not hand-specified) g, or
(iii) held-out role-filler generalization in language is NOT well-modeled by the TEM/spatial
mechanism after all (the honest extrapolation-gap flagged above turning out to be a real wall,
not just an untested claim). A tie is a fully legitimate, informative outcome — it would mean
the brain's spatial-domain mechanism does not port to language role-binding, which is itself a
publishable-quality (product-relevant) negative result per the honest-extrapolation framing
above.

---

## Cross-thread synthesis

- Builds directly on `research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md`
  (thematic-role ASSIGNMENT via multi-cue competition) — that note's GAP was "text -> correct
  role-filler assignment (the encoder)"; THIS drill supplies the mechanism for how that encoder
  should be structured internally (structure-blind g + content-agnostic bind) to generalize to
  NOVEL fillers once assignment happens, closing the loop between "how roles get assigned" and
  "how binding generalizes."
- Cross-validates against `research_vsa_learned_reader_prior_art_scour_2026-07-18.md` and
  `research_prior_art_text_to_relational_meaning_2026-07-18.md` (both independently surfaced
  COGS/SCAN compositional-generalization failure as the one open mainstream gap where native VSA
  binding has a plausible, unproven edge specifically at the text-to-role-assignment stage) —
  this drill now supplies the SPECIFIC brain mechanism (TEM-style factorization) and a concrete
  buildable design where those notes left the claim at "plausible, untested."
- Cross-validates against `research_neurosymbolic_glassbox_read_reason_prior_art_2026-07-18.md`
  (NVSA as the closest published structural analog: fixed VSA algebra + learned front-end +
  glass-box reasoning, vision-only/RAVEN) — NVSA's "learned front-end feeding fixed VSA algebra"
  pattern is architecturally the SAME shape as this drill's "learned g feeding native FHRR bind"
  design; porting NVSA's pattern from vision to text via the g/x factorization is now a concrete,
  literature-grounded path rather than an abstract analogy.
- New citation not previously surfaced in this arc: TEM (Whittington/Behrens *Cell* 2020) and the
  "What Is a Cognitive Map?" (Behrens *Neuron* 2018) / gridlike-conceptual-code (Constantinescu
  *Science* 2016) family — these were absent from all prior 07-18 drills and are the single most
  load-bearing new addition of this cycle.
- Reinforces the existing reasoning-theory anchor (resolution scales with #constraints; single-
  relation is a dead-end) — the design here explicitly keeps small enumerable role-inventories
  per proposition (2-4 roles) which is consistent with, not in tension with, that anchor: the
  COMPOSITION win comes from chaining/querying multiple bound propositions, not from binding
  many roles into one vector.

---

## Substrate-product implications

- If the fair test HARD-PASSes: this becomes the single clearest, most citable Frontier-2
  argument for the whole reading program — "the encoder generalizes to role-fillers it has never
  seen, the way children do and the way flat/memorization-based readers structurally cannot,"
  backed by an explicit, inspectable mechanism (not a black-box claim). Product framing: an
  auditable reader that provably does not need to have seen every word-in-every-role combination
  to use language correctly — a capability gap named in the mainstream literature (COGS/SCAN)
  that this design targets directly, with a mechanism (not just an architecture-badge).
- If HARD-FAIL: still valuable — it would cleanly localize WHERE the brain's spatial-domain
  generalization mechanism stops porting to language (a genuine, honestly-flagged scientific
  question this drill found unanswered in the literature), and redirect effort to LISA-style
  hand-engineered structural alignment or a hybrid, rather than continuing to assume TEM-style
  factorization transfers for free.
- Never framed as publication — product-relevant only: a reader that can be told "you have never
  seen 'glass' used as an instrument before" and correctly compose "the glass broke the window"
  is a concrete, demonstrable, auditable capability difference from black-box LLM readers (which
  also do this, but not inspectably) and from flat/rule-based extractors (which structurally
  cannot, per COGS/SCAN).

---

## Citations (verified count)

4 parallel Sonnet lit-scan lanes returned **~34 distinct sourced citations** (author/year +
real URLs reported by each sub-agent via WebSearch/WebFetch; not independently re-fetched by
the synthesizing agent — treat as sub-agent-verified, one level of indirection):

- Lane 1 (binding problem): 9 sources (Shadlen & Movshon 1999; Scholarpedia binding-by-synchrony;
  hippocampal item-place conjunctive coding J. Neurosci. 2009; mixed-selectivity review Neuron
  2024; optimal quadratic binding arXiv 2204.07186; Treisman & Gelade 1980; PMC attention-binding
  review; JOV 2023 attention-binding revision; "Attention as Binding" arXiv 2512.14709).
- Lane 2 (variable binding): 9 sources (Shastri & Ajjanagadde BBS papers x2; SHRUTI project
  homepage; Hummel & Holyoak LISA overview + full paper; SPA Waterloo page; PLOS ONE spiking-SPA;
  Smolensky 1990 tensor-product PDF; Fodor & McLaughlin 1990 critique).
- Lane 3 (TEM/cognitive maps): 9 sources (TEM *Cell* 2020 + bioRxiv + PMC copy; "What Is a
  Cognitive Map?" *Neuron* 2018; Constantinescu *Science* 2016 gridlike-conceptual-code PMC;
  Bellmund/Behrens *Science* 2018 + PDF; Whittington transformer-relation arXiv 2112.04035;
  structure-abstraction world-model arXiv 2605.15733; grid-cell Wikipedia overview).
- Lane 4 (development): 10 sources (2 Cambridge J. Child Language papers; Tomasello first-steps +
  item-based PDFs; progressive-alignment escholarship; Gentner/Anggoro/Klibanoff structure-mapping;
  theoretical compositional-generalization arXiv 2505.02627; data-diversity OpenReview; visual-
  compgen arXiv 2507.07102; critical-periods bioRxiv).

Lit-scan calibration penalty applied: P estimates in this note are DEFLATED 0.15-0.25 from raw
lane confidence; the design-verdict's overall P(HARD-PASS on the fair test) is capped at
**P_deflated = 0.35** (novel-synthesis cap 0.50 further reduced because language-domain transfer
of TEM's mechanism is an explicitly UNTESTED extrapolation per lane 3's own honest gap-flag, not
a lookup of an established result).
