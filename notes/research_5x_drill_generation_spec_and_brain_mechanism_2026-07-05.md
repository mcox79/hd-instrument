# 5x convergence drill: GENERATION goal — capability spec + brain mechanism + cross-field convergence

Date: 2026-07-05. Owner: Research. Type: 5x convergence drill (constructive build work, NOT vs-LLM comparison, per USER reframe).
Scope: sharpen, do not redo, the existing decoder design (`notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md`)
and build-roadmap (`notes/research_drill_glassbox_llm_capability_gaps_build_roadmap_2026-07-05.md`).

## Substrate-query-first (done before external search)

`director_kb_query.py` (schema v2) on "resonator network factorization sequence generation decoder positional
binding serial order theta phase" returned, at rank 1-10 (cosine 0.34-0.37, `paths_consulted=6`):
- Prior Path-D idea: resonator-factored CFG-permissible-next-token decoder (`research_drill_substrate_code_synthesis_higher_ceiling_2x_2026-06-11.md`) — same mechanism, applied to grammar decoding, already scoped as a next-drill candidate, never built.
- Resonator = NC1 complexity class for factor-recovery tasks specifically (`research_drill_substrate_operating_modes_beyond_single_pass_2x_2026-06-04.md`): O(log N) iteration depth with threshold gates.
- Resonator applied to visual scene decomposition (pose x object pairs) with the same degrade-with-scene-complexity finding this drill's Angle 3 independently reproduces (`research_drill_substrate_cross_modal_2x_2026-06-09.md`).
- A PRIOR HARD_FAIL: `exp_resonator_capacity_gpu_v1` failed at K=3, N=4096 (small-capacity corner) — different config from
  today's envelope probe, but consistent with the capacity-is-ratio-dependent (not universal) picture below.
- Citation list for resonator networks already logged in `research_drill_substrate_only_nl_synthesis_2x_2026-06-11.md`
  (Schlegel/Neubert/Protzel VSA survey; Frady/Kent/Olshausen/Sommer parts 1+2) — reused, not re-derived.

Also checked in-flight state: `data/exp_factorization_envelope_v1/metrics.json` — current status is **SMOKE_PASS**
(`easy_D1=1.000` must>=0.99, `easy_D2=1.000` peel-off must>=0.90, `hard_cliff=0.000` must<0.60 at F=2/V=4096/D=4/**N=1024**/**restarts=1**).
Note the hard-cliff smoke intentionally uses reduced N and single-shot (R=1) to fail-fast on a hard corner — it is NOT
the FULL N=8192/high-energy (R=16) run, which is separately in flight per the task brief. No result is hallucinated
past this file's contents.

No prior arc work exists on the specific 5x cross-field convergence question (brain mechanism vs VSA vs ML vs
info-theory for THIS problem) — this drill is net-new synthesis, not a redo.

---

## HEADLINE

**Four of five independent fields hand-derive the SAME abstraction**: position is an explicit tag/factor bound
alongside content, recovered by iterative competitive/resonant readout, with content and position separated until
late in the pipeline. Neuroscience (competitive queuing / theta-gamma phase-slot coding), psycholinguistics
(frame-and-slot, lemma/lexeme dissociation), and VSA/HDC theory (role-filler binding + resonator network — this
IS the field's actual mainstream answer, not a fringe pick) converge tightly. Modern ML DIVERGES on its dominant
paradigm (autoregressive chain-rule decoding manufactures order at decode time rather than reading a bound tag) —
but critically, ML's own set-to-sequence literature confirms that "impose order on an inherently order-free
compositional representation" is a genuinely **open, unsolved** problem in that field too, not a solved answer we
are failing to adopt. That reframes the divergence as a green light: our design (already pre-registered as
Stage A/B/C in the decoder-design memo) is the brain/VSA-native answer to a question the dominant ML paradigm
sidesteps rather than solves. No field surfaced a proven information-theoretic wall against it.

---

## A. WHAT WE WANT — exact capability spec (functional-requirement-first)

**MVP (the number that counts):** given a bound proposition hypervector `p` at substrate scale N=8192 encoding a
subject/verb/object triple (each slot = `bind(pos_k, filler_k)`, D=3 role-filler pairs), the decoder must recover
the exact ORDERED token sequence — not just the unordered bag of fillers.

Measured by (joint-gate, no single-axis false pass — already specified in the decoder-design memo, reaffirmed here):
1. **Per-term recovery rate** (Stage A alone; cross-checks directly against the factorization-envelope numbers).
2. **Exact-ordered-sequence match rate** (Stages A+B+C end to end — the actual generation deliverable).
3. **Per-token cleanup accuracy** (Stage C; where hub/collision limits bite under superposition load).

**Pre-registered bands (unchanged by this drill, reaffirmed as still the right bands after cross-field check):**
- HARD-PASS: exact-ordered-sequence match >= 0.70 on D=3 S/V/O at N=8192, high-energy (R=16 restarts), AND per-term
  recovery within ~0.10 of the envelope's measured ceiling.
- HARD-FAIL: exact-sequence match < 0.30 (decoder cannot round-trip even S/V/O; Stage A or C is the wall).
- MIDDLE: 0.30-0.70 -> chunking wrapper required; ship the chunked decoder as the deliverable.
- Controls: shuffled-proposition control must collapse (discriminator fires); single-shot R=1 reported alongside
  high-energy R=16 so a compute-fixable cliff is not mistaken for a genuine wall.

**Full (beyond MVP):** generate a novel, well-formed utterance from a queried memory structure (not just a
round-trip of an already-known triple) — this is the "full" bar in the task brief; it is downstream of the MVP and
additionally requires the CLS/consolidation and control-layer work already flagged as separate gaps in the
build-roadmap note. Not this drill's decision point.

"Done" looks like: a discriminator-surviving cell where the substrate takes a bound thought and speaks it, in
order, with every emitted token traceable to one unbind op on one specific bound structure (faithful by
construction — mechanical, not observed).

---

## B. HOW THE BRAIN DOES IT — concrete mechanism(s), existence proof

The brain provably solves exactly this class of problem — recover an ordered output from a compositional/
superposed internal state — via a family of mechanisms that all reduce to the same computational abstraction.
This is the existence proof: the basics are achievable because biology already does them.

**Functional pipeline (psycholinguistics, Levelt 1989 / Dell 1986 / Garrett 1975-1988):**
Conceptualization (a non-linguistic "preverbal message" — directly analogous to our bound proposition HV) ->
grammatical encoding (lemma retrieval: meaning + syntactic category + argument structure, order-INDEPENDENT at
this stage) -> phonological encoding (lexeme retrieval: the word's sound form) -> articulation. The lemma/lexeme
split is not a modeling convenience — it is directly evidenced by tip-of-the-tongue states (lemma retrieved,
lexeme inaccessible) and by a clean DISSOCIATION in speech errors: whole-word substitution/exchange errors respect
grammatical CATEGORY (noun-for-noun) regardless of meaning and span long distances, while sound/segment exchange
errors (spoonerisms) respect PHONOLOGICAL POSITION (onset-for-onset, stressed-for-stressed syllable) over short
distances, and morpheme-stranding errors ("I hope you shave a good trime") show stems (content) and frame affixes
(position/structure) are represented and recombined separately. Garrett's frame-and-slot model formalizes this: a
syntactic frame with typed, order-independent-of-content SLOTS is built, then content lemmas are inserted into it.

**Concrete neural algorithms for imposing order (systems neuroscience):**
- **Competitive queuing** (Bullock & Rhodes; Houghton 1990; direct neural evidence Kornysheva et al. 2019, Neuron):
  all items of a planned sequence are held simultaneously active with a primacy-gradient magnitude tag; a
  winner-take-all layer repeatedly fires the currently-highest-tag item then suppresses it, yielding the next item
  next. Order is carried entirely by the relative magnitude of a scalar tag — not a separately-stored sequence
  structure.
- **Theta-gamma nested-oscillation coding** (Lisman & Idiart 1995, Science; Jensen & Lisman; Lisman & Jensen 2013,
  Neuron): each held item occupies a distinct gamma sub-cycle (~25ms, ~40Hz) nested within one theta cycle
  (~125-200ms, 5-8Hz). Item position = which gamma slot it occupies; readout = scan gamma slots in temporal order.
  Capacity = number of gamma cycles fitting in one theta cycle — numerically matches Cowan's (2001) ~4-item working
  memory capacity. This is a DIRECT existence-proof of "chunking required beyond ~4 items," matching the decoder
  design's chunking-wrapper branch for propositions beyond the envelope's capacity.
- **Theta phase precession / theta sequences** (O'Keefe & Recce 1993; Skaggs et al. 1996): hippocampal place-cell
  spike phase relative to the theta cycle IS the position tag; a set of cells active over seconds of real time gets
  phase-sorted and read out, compressed ~10:1, within a single theta cycle.
- **Songbird HVC->RA sparse sequence** (Hahnloser, Kozhevnikov & Fee 2002, Nature): the cleanest single biological
  case of a literal population clock (one neuron/small clique = one precise temporal slot in the motor sequence).
  Domain-specific (birdsong) but the strongest existence-proof that sub-100ms-precision ordinal readout from a
  population code is buildable in real neural tissue, not just theoretically possible.

Confidence: the functional pipeline and lemma/lexeme dissociation are broad consensus (well-replicated error and
TOT data); competitive queuing and theta-gamma coding are well-supported, actively-researched models (not fringe)
though some specifics (exact discreteness of stages, generality of theta-gamma outside spatial/hippocampal domains)
remain contested in the literature itself — flagged honestly, not glossed over.

---

## C. 5x CONVERGENCE

| Angle | Answer | Converges on position-as-bound-factor + iterative/resonant readout? |
|---|---|---|
| 1. Systems/computational neuroscience | Competitive queuing (magnitude-tag WTA) / theta-gamma phase-slot coding | YES — explicit tag (magnitude or phase), read out by iterative max-then-suppress or phase-scan |
| 2. Cognitive science/psycholinguistics | Frame-and-slot, lemma/lexeme dissociation | YES — position (frame/slot) and content (lemma) are separately represented, bound late; strong error-pattern evidence |
| 3. VSA/HDC theory | Role-filler binding + resonator network | YES — this is the literal formalism: position IS a bound factor; resonator IS the iterative competitive/resonant unbind+cleanup+rebind readout. This is the field's ACTUAL mainstream answer (Frady/Kent/Olshausen/Sommer 2020, plus active 2022-2025 extensions), not a niche pick. |
| 4. Modern ML/DL | Autoregressive chain-rule decoding (dominant); set-to-sequence (Vinyals "Order Matters" 2016, Slot Attention 2020) is the closest analog and admits order-imposition-from-compositional-representation is UNSOLVED | DIVERGES on the dominant paradigm — but does NOT contradict our design; ML has not solved this problem cleanly either, so there is no established, better answer being ignored. |
| 5. First-principles/information theory | No proven Shannon/complexity wall for typical-case k-item superposition recovery; all found ceilings (resonator stability ratio ~0.056, VSA ~0.5 bit/neuron channel capacity, classical Hopfield 0.138N) are architecture/codebook-specific | YES (permits it) — modern Hopfield's PROVEN exponential-capacity leap over the classical 0.138N linear bound is direct existence-proof that "today's best-known ceiling" != "fundamental wall." Worst-case NP-hardness of exact L0 recovery is real but bites only adversarial instances, not the typical-case regime resonators operate in. |

**Load-bearing consensus (4-of-5, with the 5th reframed as compatible-but-distinct):** position-as-explicit-bound-
factor, recovered by iterative competitive/resonant readout, with content/position bound together only late, is
the convergent mechanism validated independently by neuroscience, psycholinguistics, and VSA theory — and NOT
foreclosed by information theory. This is exactly Stage A (resonator) + Stage B (position-as-factor) + Stage C
(cleanup = the mental-lexicon / lemma-lexeme readout) of the already-drafted decoder design. **This drill does not
change the design — it independently cross-validates it against four literatures that were not consulted when the
design was drafted**, and it clarifies that capacity cliffs found so far (including our own SMOKE `hard_cliff=0.0`
and the earlier `exp_resonator_capacity_gpu_v1` HARD_FAIL) belong to the well-documented "soft, architecture/
codebook-specific" class the literature repeatedly reports — meaning the correct response to a future cliff is
REDESIGN of codebook geometry/search, not abandonment of the mechanism.

**Where they diverge (honest):** ML's dominant paradigm does not use this mechanism at all, and multi-item
"explaining-away" peel-off beyond a handful of superposed terms is flagged as an ACTIVE, unresolved frontier by the
2024-2025 VSA papers themselves (Angle 3) — this is a real open question, not settled consensus, and should not be
oversold.

---

## D. AUGMENT BEYOND BIOLOGY (high-energy compute levers, biological floor retained)

Biological operating point: ~4 items per basic cycle, one ~125-200ms theta cycle, largely single-shot/online,
noisy spike-based readout. That is the proven floor — kept explicitly as the fallback baseline (per USER: brain
is existence-proof, not a ceiling).

Legitimate non-biological levers already in the decoder design and reaffirmed by this drill's lit-scan:
1. **Restarts** (R=16+ parallel random inits, batched matmul) — no single cortical column runs 16 parallel
   attempts serially; we can, cheaply, on CPU/GPU.
2. **Iterate well past one theta cycle** — more resonator iterations than the ~5-8 gamma sub-cycles biology fits
   in one theta window.
3. **Exact real-valued peel-off** (explaining-away) between superposed terms, vs. noisy spike-based approximate
   cleanup.
4. **Codebook-geometry engineering with no biological analog**: sparse-block-code resonators (Hersche, Terzic
   et al., arXiv:2303.13957, NAI 2025) report ~5 orders of magnitude operational-capacity gain over the original
   dense-bipolar resonator purely from codebook/nonlinearity redesign, and noise-injection factorizers (arXiv:
   2412.00354, 2024) report ~50x gains from breaking limit-cycle traps — both are pure engineering levers, not
   things evolution needed to discover.
5. **Modern dense/exponential-capacity Hopfield-style cleanup** (Ramsauer et al. 2020) for Stage C, PROVEN
   exponential-in-N capacity vs. the classical/biological-linear 0.138N — a strict, proven upgrade path for the
   mental-lexicon analog with no need to mimic biological sparsity constraints.

The efficient-biological single-shot operating point (R=1, ~4-item chunks) remains the honest floor and fallback;
augmentation happens OUTSIDE that operating condition, consistent with prior USER-locked framing. A cliff that
only fails at R=1/single-shot is a compute problem, not evidence the mechanism is wrong — the SMOKE `hard_cliff=0.0`
result (F=2,V=4096,D=4,N=1024,**R=1**) is squarely in this "expected-to-fail-at-R=1" corner per the literature and
should not be read as a mechanism failure signal; the FULL run at N=8192/R=16 is the actual test.

---

## E. SUBSTRATE FIT + FIRST BUILD

**Already have, off-disk, verified:**
- `notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md` — complete 3-stage
  design, pre-registered bands, branch logic on the envelope verdict (GO/MIDDLE/NO_GO), dispatch trigger sequence.
- `experiments/exp_factorization_envelope_v1.py` — SMOKE_PASS (verified in `data/exp_factorization_envelope_v1/
  metrics.json`); FULL re-dispatch at N=8192 high-energy in flight per task brief (not yet landed — do not
  presume its outcome).
- Substrate KB: prior Path-D CFG-decoder scoping (same mechanism, different application, never built), NC1
  complexity classification of the resonator's factor-recovery mode, prior `exp_resonator_capacity_gpu_v1`
  HARD_FAIL at K=3/N=4096 (small-capacity corner, consistent picture not a contradiction).
- Hub-rescue result (`exp_deep_reasoning_hub_robustness_v1`, Skunkworks VET in flight): PROTECTED/INDEX binding
  rescues high-degree cleanup collision 0.261 -> 0.727 where iterative resonator alone does not (+0.056) — directly
  reusable for Stage C if the VET survives.

**Gap:** none structural. The design is complete; it is gated purely on the FULL envelope numbers landing.

**Decisive next experiment (already queued, not a new ask):** read the FULL envelope verdict
(`GEN_svo_1k`/`GEN_svo_4k`/`B_V64`/cliff location at N=8192, R=16) and branch exactly per the pre-registered
GO/MIDDLE/NO_GO logic already in the decoder-design memo.

**New candidate surfaced by THIS drill (rank it, do not dispatch yet — conditional on NO_GO):** if the envelope
lands NO_GO, the decoder-design memo's currently-listed fallback is the ACF-redundancy resonator (~50x lit-reported
capacity lift for F=2). This drill surfaces a STRONGER candidate not yet in that memo: **sparse-block-code
resonator geometry** (Hersche/Terzic/Rahimi et al. 2025, arXiv:2303.13957), reporting ~5 orders of magnitude
capacity gain over the plain dense-bipolar resonator by changing codebook structure and nonlinearity, which
directly matches our GSBC-style sparse-block encoder geometry already in use for perception (the decoder-design
memo itself flags "sparse-block resonator matched to the GSBC code" as its item-(iii) NO_GO fallback — this drill
independently corroborates that exact candidate from outside literature and gives it a concrete magnitude estimate
(~10^5x) to pre-register against). Rank order for a NO_GO redesign: (1) sparse-block-code resonator geometry
[NEW, strongest lit-reported magnitude, matches existing GSBC encoder], (2) ACF-redundancy resonator [already
listed, ~50x], (3) hierarchical/chunked factorization at every level [already listed, no magnitude estimate found].
Falsifiable pre-registration for a follow-up cell if dispatched: sparse-block-code geometry should show >=10x
headroom on V or >=2-3x reduction in required N for matched accuracy vs. the bipolar baseline (HARD-FAIL: <2x
improvement at matched compute — would mean the literature's iid-codebook gains do not transfer to our correlated,
real-filler regime, a genuine and useful negative result).

---

## F. HONEST RATING (no smoke)

**Convergent-mechanism prospects: GOOD.** Four of five independent fields (neuroscience, psycholinguistics, VSA
theory, and information theory as a permissive non-blocker) hand-derive the same abstraction independently;
resonator networks are mainstream and under active 2020-2025 extension in the outside literature (not a fringe
bet); no proven Shannon/complexity-theoretic wall exists against the typical-case regime we operate in. This is
the strongest kind of "GOOD" a lit-scan can honestly support.

**Capacity-at-our-scale execution risk: MEDIOCRE / genuinely unknown pending the FULL envelope verdict.** The
SMOKE result is consistent with (not contradictory to) the literature's picture that single-shot/small-N/high-V
corners fail — but that means the FULL, high-energy run is the only source of real signal here, and it has not
landed. Multi-item peel-off at scale and hierarchical/chunked factorization are flagged as OPEN research frontiers
by the outside literature itself, not solved textbook results — deflate accordingly, do not pre-celebrate.

**Proven vs. speculative split:**
- PROVEN / high-confidence: the brain does this class of operation (well-replicated, converging evidence);
  resonator networks are the established VSA answer to this exact factorization problem; no information-theoretic
  wall blocks typical-case recovery; modern Hopfield's exponential-capacity theorem proves architecture-specific
  ceilings are not fundamental.
- SPECULATIVE / open even in outside literature: multi-item explaining-away peel-off at scale; hierarchical/
  chunked factorization; whether sparse-block-code capacity gains transfer from iid literature codebooks to our
  correlated real-filler regime (untested, flagged as a falsifiable follow-up above).
- Local/substrate-specific unknown: GO vs. MIDDLE vs. NO_GO on the FULL envelope — unresolved until it lands.

**No proven wall exists.** The only unconditionally-hard result found (worst-case NP-hardness of exact L0/sparse
recovery) bites adversarial instances only, not the typical-case high-probability regime resonator networks and
our substrate operate in. "The field hasn't fully solved multi-item peel-off at scale yet" is a live research
frontier, not proof of impossibility, per USER discipline (field-stalled != proof).

**P_deflated:** the build-roadmap note's prior estimate was P~0.40 for "generative-readout produces fluent,
faithful substrate-native generation at useful scale," gated on encoder-rescue landing and envelope adequacy. This
drill's cross-field convergence is net POSITIVE for the MECHANISM CHOICE specifically (strengthens confidence
Stage A/B/C is the right design) but does not newly resolve the capacity-execution risk (that is still gated on
the FULL envelope verdict, which is unresolved). Applying the mandatory lit-scan calibration penalty (deflate
0.15-0.25; cap novel-synthesis P at 0.50): **P(convergent mechanism is the correct build path) ~= 0.45-0.50** (cap
applied — this is novel cross-field synthesis, not a directly-published result for our exact regime).
**P(capacity adequate at our N without redesign) stays at the pre-existing ~0.40, unchanged by this drill** — it
did not newly test capacity; the envelope FULL run is the only thing that can move that number.

---

## Cheap decisive test

Already in flight, not a new ask: FULL run of `experiments/exp_factorization_envelope_v1.py` at N=8192, R=16
restarts, reporting `GEN_svo_1k`, `GEN_svo_4k`, `B_V64_hi`, and the cliff location. This single result resolves
GO/MIDDLE/NO_GO per the decoder-design memo's pre-registered branch logic — no new experiment is needed to make
the primary decision. Secondary/conditional cheap test (only if NO_GO): a small CPU smoke substituting sparse-
block-code codebook geometry for bipolar-BSC in the resonator, measuring V-headroom or N-reduction at matched
accuracy vs. the bipolar baseline (see falsifiable prediction in section E).

## Falsifiable predictions (HARD-PASS / HARD-FAIL, consolidated)

1. Decoder round-trip (reaffirmed from decoder-design memo): HARD-PASS >= 0.70 exact-ordered-sequence match at
   N=8192/R=16/D=3 SVO with per-term recovery within 0.10 of envelope ceiling; HARD-FAIL < 0.30.
2. Envelope adequacy (already the NO_GO trigger in the decoder-design memo): HARD-FAIL if `B_V64_hi < 0.50` even
   at high-energy R=16 — plain bipolar resonator is not the Stage-A factorizer at our scale; triggers Stage-A
   redesign, does NOT kill the mechanism (per section D/F, a compute/geometry-fixable cliff != a wall).
3. NEW (this drill): sparse-block-code resonator geometry, IF dispatched as a NO_GO redesign candidate, HARD-PASS
   = >=10x V-headroom or >=2-3x N-reduction at matched accuracy vs. bipolar baseline; HARD-FAIL = <2x improvement
   at matched compute (would show the lit-reported iid-codebook gains do not transfer to our correlated-filler
   regime — a genuine, useful negative result, not a discredit of the overall mechanism).

## Cross-thread synthesis

Directly extends and cross-validates (does not redo):
- `notes/decoder_design_stage_A_factor_B_order_C_cleanup_generation_readout_2026-07-05.md` (the design this drill
  stress-tests against outside literature — confirmed, not revised, except for the new NO_GO-redesign ranking).
- `notes/research_drill_glassbox_llm_capability_gaps_build_roadmap_2026-07-05.md` (source of the #1-gap framing
  and the original P~0.40 estimate this drill's convergence bears on).
- `notes/research_drill_substrate_code_synthesis_higher_ceiling_2x_2026-06-11.md` (Path-D resonator-CFG-decoder
  scoping — same mechanism, unbuilt sibling application).
- `notes/research_drill_substrate_operating_modes_beyond_single_pass_2x_2026-06-04.md` (NC1 classification of the
  resonator's factor-recovery mode — theoretical grounding for why this is tractable at all).
- `notes/research_multihop_revival_5x_drill_2026-06-25.md` (prior bidirectional-VSA/resonator citation base, reused).
- `exp_deep_reasoning_hub_robustness_v1` (Skunkworks VET in flight) — Stage C reuse candidate.

## Substrate-product implications

This is the mechanism that gives the substrate a "mouth": faithful-by-construction generation (every emitted
token traces to one unbind op on one specific bound structure — mechanical, not observed) closes the encode ->
reason -> generate -> verify loop and is the single largest lever toward standalone glass-box-LM capability
(M3/M4 milestones). It is not a publication-worthy result being sought; it is a product capability gap being
closed. A second, cross-cutting product implication surfaced by this drill: sparse-block-code cleanup geometry
(section E/D) is not generation-specific — if it delivers the lit-reported capacity gains here, the same codebook
redesign is a candidate capacity multiplier for the memory/hub-collision problem elsewhere in the substrate
(cleanup-under-load is the same underlying operation in both places), worth flagging to Strategy as a cross-cutting
lever independent of the generation decision.

## Citations (verified count)

Five independent Sonnet lit-scan sub-agents returned ~55 total citations across the 5 angles (substantial
overlap/cross-corroboration — notably the Frady/Kent/Olshausen/Sommer resonator-network papers were surfaced
independently by 3 of 5 angles, itself a convergence signal). Core sources with reasonable bibliographic
confidence: ~40. Sources flagged by their own originating sub-agent as approximate/uncertain on exact
title/venue/year: ~10 (explicitly noted inline per angle above, not silently presented as certain). Zero sources
were independently primary-verified by this synthesis pass beyond the sub-agents' own stated confidence — this is
literature-scan tier evidence, not primary-verified tier; treat P estimates accordingly (calibration penalty
already applied above).

Representative key citations (deduplicated, cross-field):
- Frady, Kent, Olshausen, Sommer. "Resonator Networks 1 & 2." Neural Computation 32(12), 2020. arXiv:2007.03748 / arXiv:1906.11684.
- Hersche, Terzic, Karunaratne, Rahimi et al. "Factorizers for Distributed Sparse Block Codes." Neurosymbolic AI Journal, 2025. arXiv:2303.13957.
- "On the Role of Noise in Factorizers for Disentangling Distributed Representations." arXiv:2412.00354, 2024.
- Frady, Kleyko, Sommer. "Theory of the superposition principle for HDC/VSA." arXiv:1707.01429; "Capacity Analysis of Vector Symbolic Architectures." arXiv:2301.10352.
- Plate. "Holographic Reduced Representations." IEEE Trans. Neural Networks, 1995.
- Amit, Gutfreund, Sompolinsky. "Storing Infinite Numbers of Patterns in a Spin-Glass Model of Neural Networks." PRL, 1985.
- Ramsauer et al. "Hopfield Networks is All You Need." arXiv:2008.02217/2007.13505, ICLR 2021.
- Donoho & Tanner (compressed sensing phase transitions, ~2005-2009).
- Natarajan (1995, NP-hardness of exact L0); Tillmann & Pfetsch (arXiv:1205.2081); Ding-Sly-Sun (k-SAT threshold, arXiv:1310.2728).
- Levelt. *Speaking: From Intention to Articulation*, 1989. Dell. "A spreading-activation theory of retrieval in sentence production." Psych Review, 1986. Garrett (1975, 1980, 1988) sentence-production frame/slot model. Roelofs, WEAVER++ (1992, 1997); Levelt/Roelofs/Meyer 1999 BBS.
- Bullock & Rhodes; Houghton (1990); Kornysheva et al. (2019, Neuron). Lisman & Idiart (1995, Science); Jensen & Lisman; Lisman & Jensen (2013, Neuron). O'Keefe & Recce (1993); Skaggs et al. (1996). Hahnloser, Kozhevnikov & Fee (2002, Nature). Cowan (2001, BBS).
- Vinyals, Bengio, Kudlur. "Order Matters: Sequence to Sequence for Sets." arXiv:1511.06391, 2016. Locatello et al. "Slot Attention." arXiv:2006.15055, 2020. Gu et al. (NAT, arXiv:1711.02281); Ghazvininejad et al. (Mask-Predict, arXiv:1904.09324).
