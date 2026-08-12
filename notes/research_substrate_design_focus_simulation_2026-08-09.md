# Research: fleshing the Cowan-4 focus into a real simulation engine (associative pull-in + causal inference)

**Filed by:** research sub-agent, 2026-08-09. **Drill type:** substrate-design (BUILD pillar), internal code
audit + 3 parallel Sonnet lit-scan lanes (generic-term external search, query-privacy compliant).

## HEADLINE

Every organ this design needs already exists in `hdlab/` and is individually validated at small scale; the
gap is **wiring**, not invention. `CausalLinkRegister` (CAUSE/EFFECT typed chaining, glass-box
`query_cause_of`/`query_effect_of`) has been sitting in `hdlab/situation_model_accumulate.py` unused since
2026-08-02. `iterative_attractor`/`cleanup_family` (CA3-style iterated softmax settle) is "WIRED" only into
offline experiment cells — the live focus (`hdlab/situation_focus.py::ChunkedFocus.query`) still does
one-shot `matmul+argmax` cleanup, never iterated settle. A multi-hop iterated-cleanup retrieval PATTERN
(`experiments/exp_connectivity_resonator.py`) already beats one-shot cleanup at increasing hop depth on a
50-entity knowledge graph but was never promoted into `hdlab/` or pointed at a real content store. The one
time script/causal chaining WAS tried on real narrative text
(`exp_mcscript2_script_chain_predict_gap_fill_v1`, 2026-08-09, MIDDLE_BAND), it chained
`SequenceMatrix.chain_predict` over bare per-sentence bag-of-words vectors
(`hdlab.grounding_acquisition_loop.context_vector`) with **no role structure, no entity binding, no
extracted causal link, and no connection to the focus/EventBundleCodec at all** — and it produced
near-noise signal: `fallback_accuracy_on_residual(real)=0.4401`, BELOW the pre-registered chance floor of
0.45; margin over primary +0.0103, roughly half the pre-registered +0.02 HARD-PASS bar
(`data/exp_mcscript2_script_chain_predict_gap_fill_v1/metrics.json`). All 3 independent lit-scan lanes
converge on why, from completely different literatures (narrative-comprehension psychology, symbolic AI
script theory, vector-symbolic binding-problem theory): **causal/relational structure does not emerge from
raw co-occurrence or sequence-order statistics; it requires an explicit relational/role representation**
(Trabasso causal-network links; Schank/Abelson typed script slots; Plate/Smolensky role-filler binding
against the superposition-catastrophe failure mode). The fix this note designs is exactly that: chain over
`EventBundleCodec` role-filler bundles and `CausalLinkRegister` typed links, not over bare BoW.

## The concrete build

### (1) Associative pull-in

Given the focus's current event bundle (a `ChunkedFocus` entry, itself an `EventBundleCodec.encode_event`
role-slot bundle), pull-in unbinds each role to get filler vectors, then queries a content codebook (concept
store or causal-link store) via **iterated attractor cleanup**
(`hdlab.cleanup_family.iterative_attractor` / `hdlab.iterative_attractor.iterative_cleanup`) instead of the
one-shot `argmax` `ChunkedFocus.query`/`EventBundleCodec.query_role_vec` currently use. Iterated softmax
settle is the CA3/DG pattern-completion analog (Marr 1971; Treves & Rolls 1994) and is what
`exp_connectivity_resonator.py` already demonstrated beats one-shot cleanup on multi-hop retrieval under
crosstalk. A **salience gate** (new, small: a similarity/confidence threshold on the settled state's final
argmax score) decides what actually gets admitted into the bounded focus — this is the piece with **no
existing implementation anywhere in the substrate** and is the primary novel-build risk (see Feasibility
below). Gated admission mirrors ACT-R's fan-diluted spreading activation (Anderson & Reder 1999: the more
facts linked to a cue, the weaker each individual link — off-topic high-fan associates fall below
threshold) and Gernsbacher's Structure-Building suppression of irrelevant activations.

### (2) Causal inference ("what leads to what")

`hdlab.situation_model_accumulate.CausalLinkRegister` already implements exactly the requested primitive:
`add_causal_link(cause_idx, effect_idx)` binds both directions via the SAME validated
`AccumulateRegister` bind/bundle/unbind/cleanup_argmax chain (atom 29609), and `query_effect_of` /
`query_cause_of` decode by unbinding the CAUSE/EFFECT role vector then cleanup-argmaxing over the event-slot
vocabulary. Seeded from the focus's current event, repeated calls to `query_effect_of` ARE multi-hop causal
chaining (chain depth = number of repeated queries) — the exact "what leads to what" mechanism requested,
already built, currently wired to **nothing**: `situation_reader.py::_read_causation` only extracts a flat
connective-adjacency list (`CausalLink` dataclass) into `SituationModel.causal_links`; it never populates or
queries a `CausalLinkRegister`. Wiring this in replaces the flat list with a queryable, chainable store.

**Vector-family note (honest, not hidden):** `ChunkedFocus`/`EventBundleCodec` are bipolar {-1,+1};
`CausalLinkRegister`/`AccumulateRegister` are FHRR complex64. These do NOT share a vector space and no new
cross-family math is needed: `CausalLinkRegister` operates purely over its own integer event-slot index
vocabulary (`idx_vecs`), so a causal query returns "the effect of event 3 is event 7" — an index — which is
then used to look up event 7's actual role-filler content in the (separately-typed) bipolar
`EventBundleCodec`/`ChunkedFocus` side. This is coordination-by-shared-integer-index across two parallel
co-indexed stores, not vector composition across families.

### (3) Integration dynamics

Wrap (1)+(2) in a two-phase construct/settle cycle mirroring Kintsch's Construction-Integration model
(construction floods loosely-relevant candidates; integration is a relaxation that keeps only what fits):
per new event pushed into `ChunkedFocus`, (a) CONSTRUCTION — pull-in via iterated cleanup proposes several
candidate associates/causal-consequences; (b) INTEGRATION — the salience gate + `ChunkedFocus`'s own
existing capacity=4/fanout=2 chunking admits only the highest-relevance items, compressing the rest into the
existing hierarchical chunk (already-validated graceful degradation:
`recent_acc - flat_acc >= 0.10` at load n=8, `hdlab/situation_focus.py::_selftest_flat_degrades_chunked_recovers_recent`).
This orchestration loop does not exist yet — every primitive it calls does.

## Diagnosis: why the prior `chain_predict` probe failed

`exp_mcscript2_script_chain_predict_gap_fill_v1` built one `SequenceMatrix` per TRAIN scenario TYPE by
`bind_sequence`-ing each instance's own **per-sentence `context_vector`** (bag-of-content-words hashlib-seeded
bipolar bundle, D=256, `hdlab.grounding_acquisition_loop.context_vector`) — a representation with (a) no
semantic-role structure (predicate/agent/patient indistinguishable inside the bundle), (b) no explicit
cause/effect extraction, (c) no connection to `EventBundleCodec`/`ChunkedFocus`, and (d) huge within-type
variance (many different literal tellings of "the same" scenario share only topical vocabulary, not a
specific causal chain). `chain_predict(k_start, depth=1)` then predicted a raw next-sentence-BoW vector and
scored candidate answers by cosine to it. Result: `fallback_accuracy_on_residual(real)=0.4401` — WORSE than
random guessing (0.50) and only barely ahead of the SCRAMBLE control's 0.4167. The MANDATORY toy pre-check
(`precheck_chain_predict_toy`) DID fire correctly (`cos_real=0.9955` vs `cos_scramble=0.5658` on a
hand-built 4-step coherent script) — proving `SequenceMatrix.chain_predict` itself works fine on clean,
structured, repeated sequences. The failure is specifically that **bag-of-words sentence vectors on real,
lexically-diverse narrative prose don't carry enough structure for the S-matrix's Hebbian outer-product
transitions to generalize across many different tellings of a "type."** All 3 lit-scan lanes independently
converge on exactly this diagnosis (see Cross-thread synthesis).

## Reuse vs. genuine-new-build

| Piece | REUSE (verbatim, already exists) | Genuine NEW build |
|---|---|---|
| Bounded focus (Cowan-4) | `hdlab.situation_focus.ChunkedFocus` (capacity=4, fanout=2), `hdlab.event_bundle.EventBundleCodec` | none — fully reused |
| Associative pull-in retrieval | `hdlab.cleanup_family.iterative_attractor` / `hdlab.iterative_attractor.iterative_cleanup` (CA3-style softmax settle, registry status "triaged/WIRED" but only into offline cells); iterated-cleanup-beats-one-shot pattern from `experiments/exp_connectivity_resonator.py::resonator_query_khop` | (a) swap `ChunkedFocus`/`EventBundleCodec`'s one-shot `matmul+argmax` cleanup for iterated settle in the pull-in path — small wiring change; (b) a NEW salience/relevance-gate threshold function — genuinely new, small, and the primary risk surface (nothing like this exists in the substrate today); (c) promote `resonator_query_khop`'s pattern into an `hdlab/` module generalized beyond its current 50-entity toy graph — moderate build (mechanical port + generalize) |
| Causal "what leads to what" chaining | `hdlab.situation_model_accumulate.CausalLinkRegister` (`add_causal_link`, `query_cause_of`, `query_effect_of`) — ALREADY BUILT, unused since 2026-08-02 | (a) wire it into `situation_reader.py::_read_causation` (currently a flat connective-list, never populates a queryable register) — small; (b) chain-depth>1 traversal helper (repeat `query_effect_of`) — trivial (~10 lines) |
| Content/concept store the pull-in draws from | `hdlab.lexical_similarity` (89-concept McRae-style feature-bundle similarity, WIRED into `goal_typing.py`) as a small bootstrap store | genuinely-new / GROWN: a general causal/concept knowledge store at real scale does not exist. Per the USER's standing reframe, this must be GROWN via `hdlab.grounding_acquisition_loop`'s FLAG->LIBRARY->CONSOLIDATE->BANK loop (built TODAY, 2026-08-09, currently scoped only to OOV outcome-verb valence) — extending its scope to causal-link/concept content is a real, non-trivial build (Stage 4 below), not batch-ingest |
| Integration dynamics (construct-then-settle) | `ChunkedFocus`'s existing graceful chunking/degradation (validated); `iterative_attractor`'s softmax settle as the Kintsch-CI "integration" relaxation step | a NEW two-phase construct/integrate orchestration wrapper around the above — doesn't exist yet, though every primitive it calls is reused |
| What NOT to repeat | — | `SequenceMatrix.chain_predict` over bare per-sentence BoW (`grounding_acquisition_loop.context_vector`) is a CONFIRMED negative result on real narrative text (MIDDLE_BAND, near-noise fallback accuracy) — do not re-chain over unstructured bag-of-words; chain over `EventBundleCodec` bundles / `CausalLinkRegister` links instead |

## Staged de-risk sequence

### Stage 1 (cheapest, decisive first test): associative pull-in on a controlled micro-world

Hand-author ~25-30 CAUSE->EFFECT facts across 5-6 scenario clusters (same toy-instance style already used by
the mcscript2 cells, e.g. "cracked egg"->"whisked mixture"->"heated pan"; "clipped leash"->"walked
dog"->"sniffed grass"), stored in one `CausalLinkRegister` + the facts' event content in one shared
`EventBundleCodec`/`ChunkedFocus`. Probe: seed the focus with a current event from cluster X; pull-in must
retrieve the correct causally/topically-linked content via iterated cleanup, gated by the salience threshold.
Mandatory **SCRAMBLE control** (hashlib-seeded CAUSE/EFFECT re-pairing, same convention as
`exp_mcscript2_script_chain_predict_gap_fill_v1`'s `_deterministic_perm` and the M2 "pairscramble" pattern
already validated on the OOV union channel) — same content distribution, destroyed causal structure. Also
probe deliberately OFF-TOPIC cues (a different cluster) to measure false-pull-in rate (does the gate actually
suppress).

- **HARD-PASS:** in-cluster correct-retrieval rate >= 0.70 AND real beats scramble by >= 0.20 absolute AND
  off-topic false-pull-in rate <= 0.15.
- **HARD-FAIL:** real correct-retrieval rate within 0.05 of scramble's (no structure signal — reproduces the
  diagnosed BoW failure even with typed links, meaning the bottleneck is elsewhere) OR off-topic false-pull-in
  rate > 0.40 (gate doesn't discriminate — indiscriminate flooding, the specific failure mode Lane-3's
  intrusion-error / poor-comprehender literature warns is causally linked to worse comprehension).
- **MIDDLE_BAND:** everything between.

Cost: reuses every primitive verbatim, hand-authored micro-world (no corpus dependency), CPU-only,
sub-minute runtime. This is the cheapest possible decisive test of the core mechanism.

### Stage 2: multi-hop causal chaining on the same micro-world

Chain `query_effect_of` 2-3 hops forward from a seed event; does the predicted downstream event beat chance
and beat scramble at every hop (mirroring the resonator literature's accuracy-vs-hop-depth degradation
curve — Frady/Kent/Olshausen/Sommer 2020 establish this for factorization, but NOT specifically for
multi-hop graph chaining, which is this drill's own extrapolation, flagged accordingly).

- **HARD-PASS:** real 2-hop accuracy stays above scramble at every hop AND degrades gracefully (no cliff to
  chance between hop 1 and hop 2).
- **HARD-FAIL:** real collapses to scramble-level by hop 2, OR hop-1 accuracy itself is at or below Stage-1's
  in-cluster floor (chaining adds nothing beyond single-hop pull-in).

### Stage 3: wire onto real narrative text, re-run the mcscript2 gap-fill test through the structured path

Replace `situation_reader.py::_read_causation`'s flat connective list with `CausalLinkRegister`-backed
storage+query; replace the failed bare-BoW `SequenceMatrix` fallback in
`exp_mcscript2_script_chain_predict_gap_fill_v1` with `EventBundleCodec` role-filler events +
`CausalLinkRegister` chaining, same staged-decision harness, same baselines.

- **HARD-PASS:** staged accuracy margin over primary-only content-matching >= +0.02 (the ORIGINAL
  pre-registered bar the bare-BoW version missed) AND fallback accuracy on residual > 0.55 (clear of the
  [0.45, 0.55] chance band the bare-BoW version fell BELOW) AND real beats scramble.
- **HARD-FAIL:** margin <= 0 OR residual accuracy still in/below the chance band — i.e. the same failure
  recurs even with structure, meaning the bottleneck is NOT representation-shape but something else (the
  cell's own honest-scope note already flags `TEXT_OVERLAP` as unusually strong/dominant on this specific
  lexically-grounded corpus — a real, live possibility independent of this fix).

### Stage 4: acquisition-loop wiring (grow, don't batch-ingest, the content store)

Extend `hdlab.grounding_acquisition_loop`'s FLAG->LIBRARY->CONSOLIDATE->BANK loop (built today, currently
scoped to OOV outcome-verb valence only) to grow the causal-link/concept store the pull-in mechanism draws
from, per the USER's explicit standing reframe against batch-ingest. This is the largest, least-precedented
piece of the whole program (multi-week+) and is correctly sequenced LAST — Stages 1-3 are cheap tests of
whether the retrieval/chaining MATH is sound before committing to growing its content supply.

## Cross-thread synthesis

- **`exp_mcscript2_script_chain_predict_gap_fill_v1`** (2026-08-09, MIDDLE_BAND) is the negative result this
  drill diagnoses and designs the fix for — see Diagnosis above.
- **`exp_situation_model_relation_ablation_v1`** (2026-08-09, HARD_PASS today) validates the SAME
  register-extension pattern this design reuses: `RelationRegister` extends `AccumulateRegister` exactly the
  way `CausalLinkRegister` does (new typed role on the same bind/bundle/unbind/cleanup_argmax chain), and its
  ACHIEVE/CONTRADICT relation queries via `concept_similarity` HARD_PASSed cleanly on a small hand-curated
  item set (11 heldout items) — direct precedent that the register-extension + concept-similarity-query
  pattern this drill proposes for pull-in generalizes on small, controlled probes. Honest caveat carried
  forward: that HARD_PASS explicitly separates `mechanism_design_P~0.55` from `brain_fidelity_P~0.15-0.20`
  for its CONTRADICT leg (computational-, not psychological-, precedent) — the same honesty discipline
  applies here: Lane 1's verdict below is explicit that "iterated attractor cleanup + salience gate feeding a
  bounded buffer" is a plausible ENGINEERING SYNTHESIS, not an established single neuroscience claim.
- **`hdlab/event_centrality_coref.py`'s `query_memory=True`** path is the existing MIRROR-IMAGE precedent:
  it already queries `ChunkedFocus` content (via `hd_centrality`) to score EXTERNAL coref candidates
  (focus-out direction). Pull-in is the reverse direction (external content INTO focus) using the same
  "query the focus" API shape.
- **`notes/research_brain_fidelity_architecture_audit_2026-08-09.md`** (today, adjacent drill) flagged two
  commit-decision mechanisms (MDL, CRP) as convenient-math-mislabeled-as-brain-mechanism. This drill applies
  the same discipline: Lane 1 explicitly flags that "hippocampal single-item attractor settling" and
  "cortical multi-associate spreading activation" being the SAME iterated operation is a live, MINORITY
  position (Lerner, Bentin & Shriki 2012), not consensus — mainstream CA3 models emphasize convergence to
  ONE clean attractor, which sits in tension with a buffer meant to hold several weakly-active competing
  associates simultaneously. Label this design choice HONESTLY as an engineering extrapolation from a
  minority-supported cognitive-science position, not a settled brain fact.
- **Lit-scan Lane 2 (causal chaining)** independently derives, from Trabasso's causal-network psychology +
  Schank/Abelson script theory + Plate/Smolensky binding-problem theory, the SAME structural claim the
  mcscript2 post-mortem reaches empirically: causal/relational structure requires explicit role-typed
  representation, not raw co-occurrence. Lane 2's own honest caveat: no source it found ran the EXACT
  ablation (bag-of-words next-item prediction vs. structured causal chaining on a narrative task) — this is
  "strongly-indicated-but-extrapolated," and `exp_mcscript2_script_chain_predict_gap_fill_v1` is in fact the
  closest thing to a direct empirical test of exactly this claim that exists anywhere (on THIS substrate).
- **Lit-scan Lane 3 (integration dynamics)** grounds the construct-then-settle orchestration
  (Kintsch CI) as a well-replicated BEHAVIORAL regularity, and grounds relevance-gated selective integration
  as necessary via convergent evidence (event-segmentation gating, structure-building suppression, and
  clinical evidence that suppression deficits causally co-occur with worse comprehension via intrusion
  errors — Pimperton & Nation 2010). This is the strongest-evidenced of the three lanes.

## Substrate-product implications

If Stages 1-3 clear their bars, the product gets a genuinely NEW capability class: answering "what happens
next" / commonsense-gap questions with a fully AUDITABLE trace (which facts were pulled in, from where, at
what similarity score, via which causal link, at what chain depth) — the differentiator against an LLM's
opaque prediction. If Stage 3 specifically HARD-FAILs (a real, flagged possibility given the mcscript2
corpus's unusually strong lexical-overlap baseline), the fallback product value is still real: Stages 1-2
passing would prove the retrieval/chaining MATH is sound and auditable even where it doesn't yet win
accuracy on this particular benchmark — matching the "auditability edge, not an accuracy edge" positioning
already adopted for the adjacent goal-achievement arc. Either way this is NOT a publication-shaped
result; it's a direct build-vs-abandon decision on whether "flesh the focus into a simulation engine" is
wiring (cheap, do it) or a much bigger content-supply program (Stage 4, correctly sequenced last, expensive).

## Falsifiable predictions (consolidated)

**HARD-PASS the whole program:** Stage 1 HARD-PASS AND Stage 2 HARD-PASS AND Stage 3 HARD-PASS (all three
bands as specified above). This would mean the design genuinely fixes the diagnosed bare-BoW failure and
recovers real accuracy on a benchmark that already showed the naive approach fails.

**HARD-FAIL the whole program:** Stage 1 HARD-FAIL (the core retrieval mechanism itself doesn't discriminate
real causal structure from scramble even with typed role/link representation) — this would be the more
serious result, since it would falsify the CENTRAL diagnosis (representation-shape, not raw co-occurrence, was
the bottleneck) and force a rethink of what actually broke the prior probe.

**Honest calibration (per lit-scan calibration discipline, deflate 0.15-0.25, cap novel-synthesis P at
0.50):** Stage 1 (pure wiring of already-separately-validated primitives on a hand-authored micro-world) —
gut estimate ~0.70, deflated and capped to **P~0.50**. Stage 2 (multi-hop chaining, extrapolated from
factorization-only resonator literature) — gut ~0.55, deflated to **P~0.35**. Stage 3 (real narrative text,
against a corpus whose own honest-scope note flags an unusually strong lexical baseline) — gut ~0.35,
deflated to **P~0.20**. These are independent stage-conditional estimates, not a joint probability; a
Stage-1 HARD-FAIL should stop the sequence before Stages 2-3 are attempted (cheap-decisive-first ordering).

## Honest feasibility / capacity read

Every individual primitive this design needs (`ChunkedFocus`, `EventBundleCodec`, `CausalLinkRegister`,
`iterative_attractor`/`cleanup_family`, the resonator multi-hop pattern) already exists and is individually
validated at small scale — Stage 1 is genuinely a wiring exercise, not a research problem, and should be
attempted regardless of the rest of the program's fate. The genuinely hard, unprecedented pieces: (a) the
**salience gate** does not exist anywhere in the substrate today; per Lane 1, ACT-R needed a carefully
fan-diluted, decades-refined formula to get this right, and a first cheap threshold pass will likely be
crude — this is the primary risk surface for false floods vs. missed real associations. (b) **Capacity/SNR
at real scale is untested**: `ChunkedFocus`'s only validated envelope is load n=8 (2x capacity=4) with a
modest 0.10-absolute recovery margin; a real multi-paragraph passage generating several pull-in candidates
PER SENTENCE could mean load=20-50 candidates competing for 4 slots, an order of magnitude beyond anything
measured — Stage 1's off-topic false-pull-in-rate measurement is the FIRST real data point on this curve,
not a confirmation of an already-known bound. Per Lane 1 and Lane 3 explicitly: the mapping from
vector-superposition capacity math (Hopfield/HRR/compressed-sensing capacity curves) onto Cowan's
psychological ~4-item bound is "an analogy, not a tested equivalence" in the literature generally, and is
equally untested on THIS substrate's specific chunking+gate combination. (c) **Scaling the content store**
(Stage 4, the acquisition loop) is a genuinely multi-week-plus build, correctly sequenced last so Stages 1-3
can cheaply falsify the core mechanism before that investment. (d) Stage 3's own comparison point
(`exp_mcscript2_script_chain_predict_gap_fill_v1`'s baselines) already discloses that plain
text-overlap/content-matching is unusually strong on this specific corpus (`text_overlap_acc=0.5859` on
commonsense questions vs. a `majority_acc` floor of 0.4565) — so even a mechanically-correct causal-chaining
fix could legitimately fail to move the needle on THIS benchmark specifically, which would not refute the
mechanism, only its product-relevance on this one corpus. Overall: pull-in + causal-chaining as WIRING is
high-feasibility and should be attempted near-term (days); as a general-purpose "simulation engine" that
demonstrably improves real narrative comprehension, it is a multi-stage program whose hardest,
least-precedented piece is the salience gate and the content-store scaling, not the retrieval/chaining math
itself, which is already built and separately validated.

## Citations (verified count: 37 unique across 3 independent lit-scan lanes)

Lane 1 (associative pull-in + capacity): Anderson, Bothell, Byrne, Douglass, Lebiere & Qin (2004, *Psych.
Review*, ACT-R); Anderson & Reder (1999, fan effect); Marr (1971, *Phil. Trans. R. Soc. B*); Treves & Rolls
(1994, *Hippocampus*); Kesner & Rolls (CA3 quantitative theory, *Neurosci. Biobehav. Rev.*); Lerner, Bentin
& Shriki (2012, *Cognitive Science*); Frady, Kent, Olshausen & Sommer (2020, *Neural Computation*, resonator
networks 1&2); Cowan (2001, *BBS*); Plate (1995/2003, HRR); Kanerva (1988, Sparse Distributed Memory);
Krotov & Hopfield (2016, *NeurIPS*); Demircigil et al. (2017, *J. Stat. Physics*); Ramsauer et al. (2020,
ICLR); Myers & O'Brien (1998, *Discourse Processes*, resonance model of comprehension).

Lane 2 (causal chaining / script inference): Trabasso & van den Broek (1985, *JML*); Trabasso & Sperry
(1985, *JML*); Trabasso, van den Broek & Suh (1989, *Discourse Processes*); Suh & Trabasso (1993, *Discourse
Processes*); Schank & Abelson (1977, *Scripts, Plans, Goals, and Understanding*); Cullingford (1978, SAM,
Yale PhD); DeJong (1979, FRUMP, Yale PhD); Zwaan & Radvansky (1998, *Psych. Bulletin*); Zwaan (2025,
25-year retrospective); McKoon & Ratcliff (1992, *Psych. Review*); Smolensky (1990, *Artificial
Intelligence*, tensor-product representations); Greff, van Steenkiste & Schmidhuber (2020, arXiv:2012.05208,
binding problem); Chambers & Jurafsky (2008, ACL, narrative event chains).

Lane 3 (WM integration dynamics): Kintsch (1988, *Psych. Review*); Kintsch (1998, *Comprehension*); Cowan
(2010, *Current Directions*); Souza & Oberauer (2013, *Frontiers in Human Neuroscience*); Amit, Gutfreund &
Sompolinsky (1985, *PRL*); Donoho (2006, *IEEE Trans. Info. Theory*); Zacks & Swallow (2007, *Current
Directions*); Gernsbacher (1990, *Language Comprehension as Structure Building*); van den Broek et al.
(1996 et seq., Landscape Model); Pimperton & Nation (2010, *JML*).

(Plate 1995/2003, Cowan 2001, Krotov & Hopfield 2016, and Ramsauer et al. 2020 recur across lanes as
independent convergent citations — counted once each in the unique total.)
