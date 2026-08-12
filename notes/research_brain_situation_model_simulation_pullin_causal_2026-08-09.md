# Research: brain-faithful SHAPE of associative pull-in + causal inference for the Cowan-4 focus simulation engine (2026-08-09)

Filed by: research (Sonnet), USER-framed drill ("the state-of-mind 4-vector bundle IS our simulation engine;
flesh it into a REAL simulation... PULL IN things that are CLOSE to what it builds, with CAUSAL INFERENCE on
what things lead to what things"). 3 parallel Sonnet lit-scan lanes (Resonance model; formal spreading-activation
math; forward-simulation/prospection) dispatched and returned; synthesized here against the owned substrate
(`hdlab/situation_focus.py`, `hdlab/cleanup_family.py`, `hdlab/event_bundle.py`,
`hdlab/situation_model_accumulate.py`, `hdlab/sequence_memory.py`) and against TODAY's dense on-disk research
output (`research_psych_bridging_inference_situation_models_2026-08-09.md`,
`research_vsa_script_representation_chaining_2026-08-09.md`), which already carries Kintsch C-I, Trabasso
causal-network, Graesser-Singer-Trabasso, Zwaan event-indexing, TEM, and Mattar&Daw/Alexander&Brown citations
in full — REUSED and cited below, not re-derived, per KB-check discipline.

---

## HEADLINE

**Two literature-independent lines converge on the SAME architectural verdict.** (1) The psych/neuro
literature on both pull-in and causal inference converges on a RETRIEVAL-AND-RECOMBINE shape (global-matching
resonance over LTM; Kintsch's construct-broad/settle-narrow; Barsalou pattern-completion; Schacter/Hassabis
flexible recombination of stored fragments) — none of it is a trained continuous forward-regressor. (2) The
substrate's OWN most rigorous prior attempt at causal/forward prediction as a TRAINED regression over event-
bound FHRR vectors — `data/exp_event_level_sr_td_contrastive_relation_inference_phase2_v1/metrics.json`,
Dayan SR + TD-bootstrap + InfoNCE-contrastive objective, both known confounds (context-starvation, wrong-grain
target) explicitly fixed before this run — came back **`MECHANISM_FALSIFIED`** (trained did not beat a
copy-baseline: margin +0.0025 vs required >=0.05). These two independent facts point the same direction: the
fleshed-out simulation should be built as **glass-box RETRIEVAL (resonance-style overlap probe) + RELATIONAL
QUERY (typed causal-graph lookup) + RECOMBINATION-on-miss (bind-and-reuse, not regress)**, never as a trained
point-predictor over the event embedding space. `hdlab/situation_focus.py` (ChunkedFocus, the Cowan-4 bounded
focus) currently does NEITHER associative pull-in NOR causal inference — it only accumulates events PUSHED IN
by the reader and is itself registered `SHELVE` in `data/capability_registry.jsonl`
(`working_overlay_situation_reader`, `pipeline_status: WIRED_BUT_NOT_PIPELINE_REACHABLE`). This note specifies
the missing 5-step pipeline (Section 4) that would make it the USER's "real simulation": a resonance-style
probe against an LTM store (currently absent — the focus has no query-OUT capability), a Hopfield-style
settling pass (`cleanup_family.iterative_attractor`, already owned, already CA3/DG-attractor-shaped), a typed
causal-graph query (`CausalLinkRegister`/`RelationRegister`, already owned, extended per today's bridging-
inference note), and a bind-and-recombine fallback for genuinely novel continuations (new, small, reuses
`bind`/`bundle` verbatim) chained via `sequence_memory.chain_predict` (already chain-grade certified) for
stereotyped scene order. No new binding primitive is required anywhere in this pipeline; the true resonator
(Frady/Kent/Olshausen/Sommer multi-factor joint decode) remains confirmed absent from `hdlab/` and is NOT on
the critical path for a first build (single-factor probes suffice at current script-codebook scale, per
today's sibling note's own capacity analysis).

P_deflated = **0.38** (assembling this specific 5-step pipeline is this note's own novel synthesis, capped at
the mandatory 0.50 novel-synthesis ceiling and deflated further; see calibration breakdown at the end of
Section 4). The "avoid trained regression, prefer retrieval+recombine" architectural constraint specifically
is much higher confidence (~0.75) since it rests on a disk-verified substrate negative, not just literature
extrapolation.

---

## 1. ASSOCIATIVE PULL-IN — three converging accounts, one honest gap, one formal equation

### 1a. Kintsch's Construction-Integration (1988, *Psychological Review* 95(2):163-182; Kintsch 2005,
*Discourse Processes* 39(2-3):125-128 — full-text confirmed by today's lane B) — REUSED from today's
bridging-inference note, sharpened with the exact mechanism today's spreading-activation lane full-text-verified

- **SHAPE**: two-stage. CONSTRUCTION is bottom-up and context-**insensitive** — text propositions plus any
  loosely word/knowledge-triggered elaborations/inferences are generated in parallel and "promiscuously,"
  deliberately overgenerating irrelevant/contradictory material, no filtering. INTEGRATION is then a literal
  **iterated matrix-vector spreading-activation process**: propositions/inferences are nodes in a network with
  a pairwise connection-strength matrix (positive for mutually-coherent pairs, negative/absent for
  unrelated/contradictory pairs); an activation vector is repeatedly multiplied by this matrix (with
  normalization) until it stabilizes at a fixed point — Kintsch's own words (2005, full text): "Integration is
  constraint satisfaction, modeled as a spreading activation process: Text propositions and inferred
  propositions that go together strengthen each other, although those that do not fit into the broader context
  are inhibited."
- **POSITION**: every processing cycle (clause/sentence-grain), continuously, not gated to special junctures.
- **METRIC**: COHERENCE — the settled activation vector approximates the fixed point of a Hopfield-like
  energy-minimization / constraint-satisfaction dynamical system; a proposition well-connected to many other
  currently-active propositions (e.g. a triggered "restaurant" schema) becomes strongly activated through the
  iteration itself and starts acting as a top-down control unit, feeding activation to what it connects to and
  suppressing what it doesn't.

### 1b. Myers & O'Brien's RESONANCE model (1998, *Discourse Processes* 26(2-3):131-157) — genuinely new ground
this cycle, with an honest formalization gap

- **SHAPE**: passive, "dumb," memory-based signaling — every incoming clause sends a signal to ALL of long-term
  memory (both the evolving discourse representation and world knowledge) simultaneously, activating content
  **regardless of relevance** (Albrecht & O'Brien 1993's "Mary was a vegetarian" textoid paradigm: readers show
  disruption from stale/outdated trait information that resonance still reactivates even after the situation
  model has moved on). **Honest gap, disk-verified by today's lane**: no source the lit-scan could access
  (including a directly-fetched PMC secondary review, PMC4456028) publishes an explicit dot-product/overlap
  equation for resonance — Myers & O'Brien 1998 is verbally/qualitatively specified, borrowing the LOGIC of
  global-matching memory models (Gillund & Shiffrin 1984 SAM; Hintzman MINERVA2 — parallel probe-against-all-
  traces, summed similarity) as an analogy, not a stated formula. Treat "resonance = literal SAM/MINERVA2
  dot-product" as a plausible but UNVERIFIED equivalence, not a citable identity.
- **POSITION**: continual, every cycle, un-gated by any relevance/goal check — resonance fires BEFORE and
  independent of any strategic search.
- **METRIC**: multi-factor and convergent across sources — feature/argument overlap between current input and
  stored trace (primary driver), strength of original encoding/elaboration, degree of activation of the
  triggering element, association strength, recency/distance. One SPECULATIVE, unverified secondary claim
  worth flagging: reading-time cost may track the NUMBER of concepts activated (a fan-type count metric)
  rather than the summed magnitude of activation — structurally a Collins-Loftus "fan dilutes" signature, not
  confirmed against primary O'Brien text this cycle.
- **Relation to Kintsch's construction**: multiple sources use near-identical language for both — information
  "resonates regardless of relevance, akin to the dumb activation process proposed within the construction
  phase of Kintsch's CI model." O'Brien & Cook's own RI-Val model is explicitly described as "based on" CI —
  i.e., the field's own lineage treats resonance as elaborating/implementing CI's construction phase at the
  memory-access level, with CI's integration phase then doing the settling. The single clearest RUNNABLE
  implementation of resonance-as-algorithm is **van den Broek's Landscape Model** (Tzeng, van den Broek,
  Kendeou & Lee 2005, *Behavior Research Methods* 37(4):619-628) — "cohort activation": concepts automatically
  activate semantic-neighbor cohorts every processing cycle, with connection strengths that weaken/alter under
  inconsistency, explicitly described as "memory-based and similar to the activation mechanism described by
  the resonance model."
- **Empirical signature (ESTABLISHED, well-replicated)**: O'Brien & Albrecht 1992 (*JEP:LMC* 18(4):777-784);
  Myers, O'Brien, Albrecht & Mason 1994 (*JEP:LMC* 20(4):876-886); O'Brien, Rizzella, Albrecht & Halleran 1998
  (*JEP:LMC* 24(5):1200-1210) — readers slow down at a sentence contradicting information stated many
  paragraphs earlier, WITH NO EXPLICIT GOAL to check consistency. This is the direct behavioral proof that
  distant, evicted-from-working-memory content gets passively reactivated as a matter of ordinary reading, not
  strategic search — precisely the phenomenon `situation_focus.py`'s Cowan-4 focus structurally CANNOT produce
  today (once an event is chunked/evicted from the active buffer, nothing pulls it back for a relevance check).

### 1c. Minimalist vs. constructionist bound on what's automatic (REUSED verbatim from today's bridging note,
section 1 — not re-derived) — governs which pulled-in content belongs in the ALWAYS-ON pipeline

McKoon & Ratcliff (1992, *Psych Review* 99(3)) minimalist vs. Graesser, Singer & Trabasso (1994, *Psych Review*
101(3)) constructionist: backward causal-antecedent bridging is reliably automatic (Baggett, Johnson & Graesser
1993 — ~400ms reactivation window); forward/predictive consequence inference is NOT automatic by default
(Klin, Guzmán & Levine 1999; Cook, Limber & O'Brien 2001 — requires elaborative/task conditions or a highly
constraining context). **Direct design consequence for Section 4**: pull-in that reaches BACKWARD (resonance
against already-stated content) should run as an unconditional default; pull-in that reaches FORWARD
(speculative continuation) should be gated behind a "highly constraining context" check, not run unconditionally.

### 1d. Formal spreading-activation math — genuinely new ground, full equations verified this cycle

**Collins & Loftus (1975, *Psychological Review* 82(6):407-428)**, full-text verified: the historical origin,
deliberately qualitative — activation spreads outward from a processed node "in a decreasing gradient... the
decrease is inversely proportional to the accessibility or strength of the links," summing at nodes reached by
multiple paths until a firing threshold is crossed at the point of INTERSECTION between two source-tagged
activation waves. No closed-form equation given; RT is driven by path length, per-link strength, and
fan-out/dilution from competing simultaneously-primed concepts.

**Anderson's ACT-R** (Anderson & Lebiere 1998; Anderson, Bothell, Byrne, Douglass, Lebiere & Qin 2004,
*Psych Review* 111(4):1036-1060), full-text verified via reconstruction — the exact quantitative answer to
"what is the formal shape of pull-in by closeness":

```
A_i = B_i + sum_j( W_j * S_ji )              # total activation of chunk i
B_i = ln( sum_k t_k^(-d) )                    # base-level: power-law recency+frequency, d ~ 0.5
W_j = W / n                                   # source weight: FIXED total W divided across n active
                                               #   sources -- the formal "bounded small active-context" term
S_ji = S - ln(fan_j)                          # associative strength, fan-effect-discounted
P_i = 1 / (1 + exp(-(A_i - tau)/s))           # retrieval probability, Boltzmann/logistic threshold
T_i = F * exp(-A_i)                           # retrieval latency, exponentially faster at higher A_i
```

`W_j = W/n` is the formal answer to "does the source set have a bounded small capacity": ACT-R's working-
memory/goal-buffer literature (Daily, Lovett & Reder 2001, *Cognitive Science* — secondary-sourced, primary
paywalled) explicitly connects this to Cowan's focus-of-attention construct, but the mapping is CONTESTED —
ACT-R's capacity is a continuous divisible resource (`W` split across whatever is in the buffer), not
Cowan's discrete ~4-slot count. Treat the equivalence as directional/analogical, not exact.

**Rival family, unresolved (CONTESTED)**: Ratcliff & McKoon's compound-cue model (1988, 1994; McKoon & Ratcliff
1992, *JEP:LMC*) proposes NO traversal at all — prime+target combine into a single compound probe, and
FAMILIARITY of that compound (a global-matching computation against all of LTM, structurally identical in
SHAPE to Gillund & Shiffrin's SAM 1984 and Hintzman's MINERVA2) drives the effect directly. The field has not
resolved network-traversal vs. single-step global-matching as the correct SHAPE; both fit most priming data
(Ratcliff & McKoon's own assessment: compound-cue "having less freedom, has passed more stringent tests" —
a parsimony argument, not a decisive refutation).

**Load-bearing substrate implication**: the substrate's own retrieval primitives (`cleanup_family.k_NN_lookup`,
`iterative_attractor` — cosine/dot-product-scored parallel probe against a full codebook, no edge traversal) are
STRUCTURALLY the global-matching/compound-cue/resonance family, not the Collins-Loftus link-traversal family.
This is a genuine, useful finding: it means the substrate does NOT need to build literal graph-hop traversal
to implement "pull in by closeness" — its EXISTING cosine-scored cleanup primitives already are the right SHAPE
for the resonance/compound-cue account, and that account is at minimum tied (not refuted) against the
alternative in the literature. The gap is not the retrieval OPERATOR; it is that nothing in `situation_focus.py`
today CALLS that operator against an external LTM store — see Section 3.

---

## 2. CAUSAL INFERENCE — reused causal-network core + genuinely new forward-simulation ground + a hard
disk-verified constraint against trained regression

### 2a. Trabasso & van den Broek causal network, Graesser-Singer-Trabasso automatic-inference bound, Zwaan-
Radvansky event-indexing causal dimension (REUSED verbatim from today's bridging-inference note — not
re-derived; full citations there)

Typed causal graph {Setting, Event, Internal-Response, Goal, Attempt, Outcome} nodes / {Physical, Psychological,
Motivation, Enablement} edges, validated per-edge by a counterfactual-necessity test (Trabasso & van den Broek
1985, *JML* 24(5)); causal connectivity (main-chain membership) predicts recall/importance (Trabasso & Sperry
1985); goal "liveness" for inference = graded spreading activation persisting via connectivity, decaying by
starvation not an explicit timer (van den Broek's Landscape model 1996/1999 — the SAME Landscape model that
implements resonance's cohort activation in Section 1b, a genuinely unifying data point: one computational
model already fuses BOTH mechanisms this drill was asked to separate); goal-satisfaction checking against the
CURRENT active unresolved goal is automatic (Suh & Trabasso 1993); Zwaan & Radvansky's Event-Indexing Model
(1998, *Psych Bull* 123(2)) confirms causation is one of 5 continuously-monitored situational dimensions
(alongside space/time/intentionality/entity), with discontinuity inflating reading time (Zwaan, Magliano &
Graesser 1995).

### 2b. Forward prediction / mental simulation — new ground this cycle, calibrated carefully

**Barsalou (2009, *Phil Trans R Soc B* 364(1521):1281-1289, full-text verified this cycle)** — the direct,
title-level bridge from Perceptual Symbol Systems (1999) to prediction. **SHAPE**: a "pattern completion
inference" mechanism — current input activates a stored **situated conceptualization** (a learned multimodal
pattern binding an object/category to its typical setting, agents, actions, introspections, outcomes); because
input is always partial, pattern completion fills the unspecified remainder BY SIMULATION, and that filled-in
remainder IS the prediction. **POSITION**: explicitly continuous — simulation "runs throughout processing,"
producing ongoing predictions as each new input updates the active conceptualization; a companion source (PMC3078178)
confirms pattern completion operates within milliseconds, automatically/unconsciously. **METRIC**: candidate-
completion selection governed by frequency/strength of prior co-occurrence, contextual/associative compatibility
with the active simulation, and general statistical regularity — described qualitatively/probabilistically, not
as a stated equation. **Status**: ESTABLISHED as the field's reference framework; the specific prediction-
mechanism claim is SPECULATIVE at the implementation level (verbal/programmatic, not tested against a formal
model in the primary source).

**Schacter & Addis (2007, *Phil Trans R Soc B* 362(1481):773-786) + Schacter, Addis & Buckner (2007,
*Nat Rev Neurosci* 8(9):657-661)** — Constructive Episodic Simulation Hypothesis. **SHAPE**: episodic memory
stores separable FRAGMENTS (objects, people, spatial context, actions), not fixed replicas; the same flexible-
recombination machinery that reconstructs a past episode from fragments assembles NOVEL scenes never
experienced, when not constrained to reproduce one specific memory — associative/relational binding of
disparate elements, implicating hippocampus for the binding step and a broader core/default-mode network for
retrieval + self-projection + assembly jointly. **POSITION (important honest caveat, disk-verified this
cycle)**: the founding papers test DELIBERATE, OFFLINE prospection (explicitly cued to imagine a future event)
— they do NOT test or claim this fires continuously during ordinary online reading; that extension exists only
as a later theoretical synthesis (below), not a direct demonstration. **METRIC**: not formalized; recombination
is constrained by semantic/associative compatibility of fragments, and the SAME looseness that enables useful
recombination is explicitly identified as the source of false-memory/misattribution error (a double-edged
mechanism — directly parallel to today's acquisition-loop note's independent finding on schema-consistent false
consolidation, Warren et al. 2014, a convergence across two separately-dispatched drills today).

**Hassabis & Maguire (2007, *TICS* 11(7):299-306) scene construction theory + Hassabis, Kumaran, Vann & Maguire
(2007, *PNAS* 104(5):1726-1731, full-text verified this cycle)** — the CAUSAL evidence. Hippocampal amnesic
patients cued to invent (not recall) novel scenarios produced measurably impoverished, spatially fragmented
output despite intact semantic knowledge: Experiential Index 27.54 vs. controls 45.06 (p=0.002); Spatial
References 2.38 vs. 5.28 (p=0.002); Spatial Coherence Index 0.10 vs. 3.68 (p=0.007) — "fragmented images in the
absence of a holistic representation." **SHAPE**: hippocampal binding of disparate elements into ONE spatially/
relationally coherent scene is necessary for BOTH remembering the past and imagining anything not currently
perceived — a single shared binding process, not two separate systems. **Status**: the GENERAL "hippocampal
binding supports both memory and imagination" claim is ESTABLISHED/well-replicated; the SPATIAL-SCENE-SPECIFIC
mechanistic reading is CONTESTED (Squire et al. 2010, *PNAS*, argue the deficit is general episodic-richness
impairment, not scene-construction-specific; Hassabis & Maguire's 2011 *PNAS* reply defends the spatial
reading — genuinely unresolved).

**Online-during-reading extension — explicitly flagged CONTESTED/SPECULATIVE, not oversold**: a 2025
ScienceDirect review ("Situation models and the default mode network") synthesizes Barsalou + Schacter/Addis +
Hassabis/Maguire into one claim (the DMN constructs situation models by coordinating LTM-fragment reactivation
online, continuously), but this SYNTHESIS is asserted at the review level, not demonstrated by a single study
bridging both traditions with fine-grained neural timing. Zacks's Event Segmentation Theory (Kurby & Zacks
2008, *TICS*; Zacks et al., full-text verified this cycle — "Dynamic prediction during perception of everyday
events") is the field's MOST formally specified continuous-prediction-plus-error account (working-memory event
models continuously predict near-future activity; comparison to incoming input yields a prediction error;
error spikes trigger event-boundary updates; eye-tracking confirms anticipatory-looking accuracy is continuous
within an event, degrading near boundaries) — but EST is explicitly disconnected from the hippocampal/
simulation tradition in the primary literature; the integration Section 2b needs (simulation machinery firing
online, every clause, during reading) is a genuine field-wide gap, not something this drill can report as
established. Report accordingly: causal forward-simulation online-during-reading is a licensed, coherent
EXTRAPOLATION from converging pieces, not a directly-demonstrated single mechanism.

### 2c. The hard constraint: the substrate's own disk-verified negative on trained forward-regression

`data/exp_event_level_sr_td_contrastive_relation_inference_phase2_v1/metrics.json`: **`verdict:
MEASURED_DIAGNOSTIC`, `verdict_msg: TOP_VERDICT=MECHANISM_FALSIFIED`** — trained=0.2590, random=0.2544,
mean=0.2544, copy=0.2565; margin over copy-baseline = +0.0025, required >=0.05. This cell (per
`notes/research_drill_biology_led_predictive_learning_mechanism_successor_representation_2026-08-03.md`,
citing Dayan 1993 SR + Stachenfeld/Botvinick/Gershman 2017 hippocampal predictive-map + Zheng et al. 2024 ICLR
contrastive-TD fusion) was the substrate's THIRD and most rigorous attempt at "learn a continuous forward-
predictor over event-bound FHRR vectors," with BOTH previously-diagnosed confounds (context-starvation,
wrong-grain literal-next-sentence target) explicitly fixed before this run per its own pre-registration. It
still failed the fair gate. **This is a genuine, disclosed, paradigm-level negative** on trained-regression
forward prediction over this substrate's own representations, independent of and prior to this literature
drill — and it converges, by coincidence of two entirely separate lines of evidence, with what Sections 1-2b's
literature independently recommend: retrieval + recombination (Barsalou pattern-completion, Schacter/Hassabis
flexible recombination, resonance/compound-cue global matching), never point-regression. **Direct design
consequence**: causal-inference forward-simulation (Section 4, Step 4) must be built as bind-and-recombine
against retrieved fragments, NOT as a re-attempt at training a continuous predictor — that path has now been
tried three times (v1 MSE symmetric-bundle, v2 MSE directional-context, phase2 TD+contrastive) and cleanly
falsified each time.

---

## 3. Mapping to owned organs (SHAPE + POSITION + METRIC, per standing discipline)

| Psych/formal finding | Owned substrate primitive | Fit | Gap |
|---|---|---|---|
| Cowan-4 bounded active focus (both Kintsch's and ACT-R's small-source-set premise) | `hdlab/situation_focus.py::ChunkedFocus` — capacity-bounded active buffer, oldest units compress into hierarchical chunks, graceful degradation | Exact — this IS the ACT-R `W_j=W/n` bounded-source-set idea and the Cowan-4 premise both literatures assume, already built, already self-tested | **Registered SHELVE** in `data/capability_registry.jsonl` (`working_overlay_situation_reader`, `pipeline_status: WIRED_BUT_NOT_PIPELINE_REACHABLE`) — not currently in the live pipeline |
| Resonance / compound-cue / global-matching retrieval (SAM/MINERVA2-shaped: parallel probe, overlap-scored, no edge traversal) | `hdlab/cleanup_family.py::k_NN_lookup` (currently used at k=1 argmax only) | SHAPE-exact for the retrieval OPERATOR; needs k>1 usage and a target LTM codebook to query AGAINST | **Missing entirely**: nothing in `situation_focus.py` queries OUT to an LTM store today; the focus only receives events pushed IN by the reader. No persisted LTM codebook of past events/concepts is wired to it. |
| CI-integration / Landscape-model settling (iterated spreading-activation constraint satisfaction to a coherent fixed point) | `hdlab/cleanup_family.py::iterative_attractor` — CA3/DG-style Treves-Rolls attractor dynamics, already owned, `max_steps` default already the right order of magnitude for Kintsch-style few-cycle settling | SHAPE-exact — an iterative attractor relaxation IS a Hopfield-style constraint-satisfaction settle, the same family Kintsch's own connectionist descendants use for CI-integration | Currently applied to single-vector cleanup against ONE codebook, not yet to a CANDIDATE SET scored for mutual coherence against the other active focus items (a small connectivity-matrix step, not built) |
| Typed causal-network CAUSE/EFFECT/GOAL query (Trabasso; Suh & Trabasso automatic goal-check) | `hdlab/situation_model_accumulate.py::CausalLinkRegister` (`query_effect_of`/`query_cause_of`) + `RelationRegister` (`bind_filler`/`decode_filler`, GOAL_ROLE/OUTCOME_ROLE) | Partial — has ONE undifferentiated CAUSE/EFFECT edge + a 2-role GOAL/OUTCOME register; today's bridging-inference note already proposes the GOAL_ROLE extension and the ACHIEVE/CONTRADICT graded-relation queries this pipeline reuses unchanged | 4-way Physical/Psychological/Motivation/Enablement edge typing not yet built (deferred, not needed for v1) |
| Event as one role-slot-bound hypervector (the atomic unit pulled-in content and causal queries operate over) | `hdlab/event_bundle.py::EventBundleCodec` — bipolar, PRED/AGENT/PATIENT/TENSE roles, round-trip >=0.98 at N=1024, baselines at chance | Exact, already self-tested; **honest note**: bipolar, not FHRR — binding a script-role FHRR vector directly to it needs the port-the-pattern resolution today's script-representation note already specifies (section 1d there), not a new decision here | None new for this pipeline — reused as-is at the event-bundle level |
| Within-script stereotyped scene-order chaining (positional, not content-conditioned) | `hdlab/sequence_memory.py::SequenceMatrix.chain_predict` — already chain-grade certified HARD_PASS at depths [1,3,5,7,10] (commit a27939c5) | Exact reuse, no new code | None |
| Bind-and-recombine fallback for a genuinely novel continuation (Barsalou pattern-completion; Schacter/Hassabis flexible recombination) | `hdlab.binding.bind`/`bundle` (base primitives) + `CausalLinkRegister.query_effect_of`-style re-seeding (decode one event's linked pointer, use it to key the next lookup) | Structurally available, no new algebra — **this exact recursive re-seeding pattern is what today's script-representation note (section 3b) already specifies** for goal-respawn chaining; this drill's contribution is tying it explicitly to the psych literature's retrieval-not-regression mandate (2c) | The CALLING PATTERN (construct-a-novel-continuation-by-binding-retrieved-fragments, as opposed to querying an EXISTING stored trace) is not yet wired as its own step; today's script note already flags the sibling "nested composition" build gap |
| Multi-factor joint decode (would be needed if a probe must recover TYPE+ROLE+FILLER simultaneously) | **Confirmed absent** — `ls hdlab/ | grep -i resonator` returns empty; the closest owned primitive (`iterative_attractor`) solves single-vector cleanup, not joint factorization | N/A | Deferred — not on the critical path for a first build; single-factor probes (Section 4) suffice at current script-codebook scale per today's sibling note's own capacity analysis (Frady/Kent/Olshausen/Sommer 2020 stability threshold D_f/N<=0.056, relevant only once codebooks grow past direct-argmax feasibility) |

---

## 4. THE PIPELINE — what the fleshed-out simulation must DO, in order, per processing cycle

Per Section 1a/1b/2a's convergent POSITION finding (Kintsch: every cycle; resonance: continual, un-gated;
Zwaan: continuous monitoring), this runs on EVERY incoming clause/event, not just at special junctures:

**Step 0 (existing, unchanged).** `SituationReader` extracts an event from the current clause;
`EventBundleCodec.encode_event` binds it; `ChunkedFocus.push` adds it to the Cowan-4 active buffer, chunking
the oldest entries when capacity is exceeded.

**Step 1 — PULL-IN / CONSTRUCTION (new, the associative-retrieval gap).** Probe an LTM codebook (grounded
concept space via `lexical_similarity.concept_vector`; a persisted store of prior-read event bundles;
`CausalLinkRegister`'s own accumulated links) using the newly-pushed event vector (and optionally each active
focus slot) as a resonance probe: a TOP-K (`cleanup_family.k_NN_lookup`, k>1 — NOT the current single-argmax
usage) call, scored by cosine overlap, unfiltered by relevance (per Section 1b's "dumb activation" finding).
Bounded small candidate set (top-3 to top-5, matching Kintsch's own modest simulated neighborhoods and Cowan-4
scale). Per Section 1c: this backward/associative direction runs unconditionally, always on.

**Step 2 — INTEGRATION / SETTLING (new, reuses `iterative_attractor` verbatim).** Feed Step 1's candidate set
plus the OTHER currently-active focus slot-fillers into `cleanup_family.iterative_attractor`'s competitive
relaxation: score each candidate's mutual coherence against the other active items (a small connectivity
matrix, Kintsch-shaped), let mutually-reinforcing candidates rise and unrelated/contradictory ones decay over
`iterative_attractor`'s existing few-iteration default. Output: 0-2 settled additions to the active focus.
Zero is a legitimate, correct output (nothing coheres strongly enough) — not a failure mode.

**Step 3 — CAUSAL QUERY (existing organ, extended per today's bridging-inference note, unchanged here).** For
the settled focus content (both the literally-read event and any pulled-in associates from Step 2), run the
typed relational query — `CausalLinkRegister.query_effect_of`/`query_cause_of` extended with `GOAL_ROLE`, plus
the ACHIEVE(`concept_similarity`)/CONTRADICT(`quality_relation` opposition-shape) graded queries already
pre-registered today — to determine whether this content stands in a CAUSE, ACHIEVE, or CONTRADICT relation to
the currently-active goal/prior chain. Backward-bridging queries run unconditionally (Section 1c/2a — automatic
per Suh & Trabasso). Forward/predictive queries (Step 4) are gated OFF by default and fire ONLY when Step 2's
settling was confident and narrow (candidate set size <=2, high margin) — the operational proxy for Klin et
al./Cook et al.'s "highly constraining context" condition that licenses forward inference.

**Step 4 — FORWARD SIMULATION / RECOMBINATION (new, gated by Step 3's constraining-context check; the
genuinely generative step).** When Step 3's causal query finds NO existing stored trace directly answers "what
happens next," fall back to RECOMBINATION, never point-regression (per Section 2c's hard constraint): construct
a candidate continuation by binding an element from the current scene into a retrieved-but-related trace's
typical role-filler slot (`bind(TRIGGER_ROLE, decoded_consequent)`-style recursive re-seeding — the exact
pattern today's script-representation note's section 3b already specifies for goal-respawn chaining, reused
verbatim, not reinvented here). Use `sequence_memory.chain_predict` (already certified to depth 5-10) when the
SAME script's stereotyped scene-order applies (positional, Choo/Kanerva trajectory-association shape); use the
recursive `CausalLinkRegister`-query re-seeding when the continuation is content-conditioned/goal-driven rather
than positionally stereotyped (today's script note's 3a-vs-3b distinction, unchanged).

**Step 5 — ABSTAIN DISCIPLINE (reuse existing pattern, no new invention).** Per-hop confidence logging + a hard
abstain below a pre-registered floor (`hdlab.self_improving_loop.decide_keep_or_revert`'s existing pattern),
at BOTH Step 2 (settling may legitimately find nothing coheres) and Step 4 (forward simulation may legitimately
abstain rather than fabricate a continuation) — the identical discipline today's script-representation note
already adopts for chain-depth (section 5e), applied here to the pull-in/forward-sim steps specifically.

### Calibration

- Section 1a (Kintsch C-I), 2a (Trabasso causal network, Zwaan event-indexing), 1c/2a (automaticity bound):
  ESTABLISHED, well-replicated, high raw confidence (~0.65-0.75), reused not re-derived.
- Section 1b (resonance): ESTABLISHED for the core reactivation-regardless-of-relevance phenomenon and its
  empirical signature (inconsistency-detection reading-time studies), but the SHAPE claim ("=global matching")
  lacks a stated primary-source formula — deflate to ~0.50 on the specific equation-level claim.
- Section 1d (ACT-R formalism): ESTABLISHED equations, full-text verified; the Cowan-4 mapping specifically is
  CONTESTED (continuous resource vs. discrete slots) — ~0.55 on that specific bridge.
- Section 2b (Barsalou/Schacter/Hassabis forward simulation): ESTABLISHED as frameworks; the online-during-
  reading firing claim is explicitly SPECULATIVE (asserted-by-review, not demonstrated) — capped ~0.40.
- Section 2c (SR-TD falsification as a design constraint): HIGH, disk-verified, ~0.80 — this is a measurement,
  not a literature extrapolation.
- The ASSEMBLY of all of the above into ONE 5-step pipeline mapped onto specific owned organs is this note's
  own synthesis, not literature-stated anywhere — capped at the mandatory 0.50 novel-synthesis ceiling and
  deflated further given the genuine open gaps disclosed above (resonance formula, online-simulation timing,
  spatial-scene-specificity contest). **P_deflated = 0.38** for "this specific pipeline is the right next
  build," consistent with today's sibling notes' calibration range (0.38-0.40).

---

## Cheap decisive test

Build a small toy multi-sentence narrative (5-8 sentences; reuse existing `SituationReader` test fixtures or
the Anne consolidation-ledger scenes already referenced by `situation_model_multibank.py`) with 3-5 PLANTED
long-distance relations: a causal antecedent or a goal-preclusion event (per today's bridging note's own "walked
away" example) placed 5+ events before the sentence that depends on it — i.e., past `ChunkedFocus`'s CAPACITY,
already compressed into a chunk by the time the dependent sentence arrives, so the CURRENT `ChunkedFocus.query`
behavior is STRUCTURALLY BLIND to it by construction (0/N recoverable without pull-in, not just weak).

1. **Baseline (no pull-in)**: run Step 3's causal query using ONLY what `ChunkedFocus` currently holds directly
   (today's unmodified behavior). Expect 0/N correct on the planted long-distance relations — a structural
   floor, not a fitted one.
2. **Pull-in-enabled**: run Steps 1-3 (probe an LTM store seeded with the full narrative's event bundles,
   settle via `iterative_attractor`, query causally).
3. **Scramble control** (mandatory, per standing pairscramble-must-collapse discipline): shuffle which event
   bundles populate the LTM store the probe queries against; recovery must collapse toward chance — proving
   genuine overlap-driven resonance, not positional/recency leakage.

**HARD-PASS**: pull-in-enabled pipeline correctly recovers >=1 of the 3-5 planted long-distance relations that
the no-pull-in baseline structurally cannot see (0/N by construction) AND the scramble control collapses to
within 10% of chance.

**MIDDLE_BAND**: Step 1's top-K retrieval contains the true antecedent above chance, but Step 2 settling or
Step 3's relation-typing fails to correctly classify it — real retrieval signal, settling/query needs iteration.

**HARD-FAIL**: Step 1's top-K retrieval does not contain the true antecedent above chance across the planted
set, OR the scramble control does not collapse (recovery is leaking from position/recency, not genuine overlap)
— would mean the resonance-probe SHAPE is insufficient at this representation/scale, forcing either a richer
LTM-store representation or reconsidering probe-vector construction before any further build on this pipeline.

---

## Falsifiable predictions (restated compactly, HARD-PASS/HARD-FAIL)

- **HARD-PASS**: >=1/3-5 structurally-invisible-to-baseline long-distance relations recovered + scramble
  control collapses to within 10% of chance.
- **MIDDLE_BAND**: retrieval recovers the right candidate but settling/relation-typing does not yet classify it
  correctly.
- **HARD-FAIL**: no above-chance retrieval of the planted antecedents, OR scramble control fails to collapse.

---

## Cross-thread synthesis

- Directly extends `notes/research_psych_bridging_inference_situation_models_2026-08-09.md`: that note supplies
  the ACHIEVE/CONTRADICT relation-query mechanism (Step 3, unchanged, reused verbatim) and the automaticity
  bound (Section 1c/2a, reused). This note supplies the missing FRONT END that note assumed as given — HOW
  candidate content gets pulled INTO the focus in the first place (Steps 1-2), which that note's own
  `AccumulateRegister`-based design implicitly required but did not specify.
- Directly extends `notes/research_vsa_script_representation_chaining_2026-08-09.md`: that note's section 3b
  (recursive goal-respawn chaining via `bind(TRIGGER_ROLE, decoded_consequent)` re-seeding) IS this note's
  Step 4 mechanism, cited and reused, not reinvented — this note's contribution is showing the SAME shape is
  independently mandated by the psych literature's retrieval-not-regression finding (Barsalou pattern-
  completion, Schacter/Hassabis recombination) AND by the substrate's own SR-TD falsification (Section 2c),
  three independent lines converging on one design choice.
- Corroborates `data/exp_event_level_sr_td_contrastive_relation_inference_phase2_v1/metrics.json`'s
  `MECHANISM_FALSIFIED` verdict from an entirely independent angle (fresh literature review, not a re-audit of
  that cell) — the psych literature never recommends trained continuous forward-regression for this function
  in the first place; the substrate's own three-attempt falsification and the literature's own preferred SHAPE
  agree without either having informed the other.
- Corroborates `notes/research_sem_crp_brain_fidelity_audit_2026-08-09.md`'s finding that DG/CA3 pattern-
  separation/completion is a materially more brain-faithful match-or-spawn SHAPE than a discrete draw — this
  note's Step 2 (`iterative_attractor`, CA3/DG-attractor-shaped) is exactly that recommended shape, now given a
  concrete calling context (settling pulled-in candidates against the active focus) rather than an abstract
  endorsement.
- Corroborates `notes/research_psych_acquisition_consolidation_loop_2026-08-09.md`'s independent finding that
  schema-accelerated integration is double-edged (Warren et al. 2014 — same circuit that fast-tracks true
  learning manufactures false memories): Section 2b's Schacter/Addis finding that recombination-looseness
  causes false-memory/misattribution is the SAME double-edge, discovered independently by two separately-
  dispatched drills today, reusing distinct citation sets that converge on one phenomenon.

## Substrate-product implications

A working pull-in + causal-query pipeline turns `situation_focus.py` from a passive accumulator (SHELVE status
today, structurally blind to anything evicted from its own 4-slot buffer) into the USER's "real simulation": a
system that can be asked WHY it flagged a contradiction or WHAT it expects next, and can point to the SPECIFIC
retrieved trace + settling margin + causal-graph edge that produced the answer — a strictly auditable trace at
every step (retrieval candidates, settling scores, relation-query result, recombination provenance), never an
opaque forward-regression score. This is the SAME glass-box auditability differentiator this arc has repeatedly
identified as the defensible product edge over accuracy-parity claims; this note's specific contribution is
showing that differentiator survives, and is in fact REINFORCED, once the missing pull-in/causal-inference
machinery is added (retrieval and typed-graph query are inherently inspectable; the trained-regression
alternative the substrate already tried and abandoned would not have been).

## Citations (verified count)

Full-text or primary-source verified this cycle (11): Collins & Loftus 1975; Kintsch 2005 (2005 overview,
full text); Barsalou 2009; Hassabis, Kumaran, Vann & Maguire 2007 (PNAS, full text); Zacks et al. (dynamic
prediction, full text); plus ACT-R equations reconstructed from a full-text-verified tutorial source (Anderson
& Lebiere 1998 / Anderson et al. 2004 content). Secondary-sourced this cycle (established via convergent
search/abstract evidence, not full primary text): Myers & O'Brien 1998; Albrecht & O'Brien 1993; O'Brien &
Albrecht 1992; Myers, O'Brien, Albrecht & Mason 1994; O'Brien, Rizzella, Albrecht & Halleran 1998; Cook &
O'Brien 2014; O'Brien & Cook 2016; Tzeng, van den Broek, Kendeou & Lee 2005; Gillund & Shiffrin 1984; Hintzman
1984/1986; Ratcliff & McKoon 1988/1994; McKoon & Ratcliff 1992; Daily, Lovett & Reder 2001; Schacter & Addis
2007; Schacter, Addis & Buckner 2007; Hassabis & Maguire 2007; Squire et al. 2010; Kurby & Zacks 2008.
REUSED verbatim from `research_psych_bridging_inference_situation_models_2026-08-09.md` (not re-verified this
cycle, already cited there in full): McKoon & Ratcliff 1992; Graesser, Singer & Trabasso 1994; Baggett, Johnson
& Graesser 1993; Suh & Trabasso 1993; Trabasso & Suh 1993; Klin, Guzmán & Levine 1999; Cook, Limber & O'Brien
2001; Trabasso & van den Broek 1985; Trabasso & Sperry 1985; van den Broek 1996/1999; Zwaan, Langston &
Graesser 1995; Zwaan & Radvansky 1998; Zwaan, Magliano & Graesser 1995. REUSED verbatim from
`research_vsa_script_representation_chaining_2026-08-09.md`: Whittington et al. 2020 (TEM); Baldassano, Hasson
& Norman 2018; Mattar & Daw 2018; Alexander & Brown 2014. Substrate/disk-verified (not literature): 
`data/exp_event_level_sr_td_contrastive_relation_inference_phase2_v1/metrics.json`; `data/capability_registry.jsonl`.
Total distinct citations this note directly draws on: 38 (18 fresh-scanned this cycle across 3 lanes, 17
reused-with-attribution from today's sibling notes, 2 registry/metrics files, plus Dayan 1993 SR / Stachenfeld
2017 / Zheng et al. 2024 already cited in the SR falsification's own source note).
