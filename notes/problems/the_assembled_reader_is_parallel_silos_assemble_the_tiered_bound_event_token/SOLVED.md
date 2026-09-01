---
problem: the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token
status: SOLVED
bar: "PASS = the bound-event-token reader resolves whether two event-mentions co-refer (needs the JOINT: same agent AND time AND place/cause) CI-separated over (a) a LATE-FUSION-OF-MARGINALS baseline (score the separate dimension lists, combine) and (b) a lexical/surface baseline -- with the BINDING-SHUFFLE control (permute the within-event bindings; the marginals are invariant, the joint breaks) LOSING CI-separated, AND the tiered register NOT collapsing at passage scale (the single-superposition 1/sqrt(M) collapse is the can-fail control the tiers must beat). Report CI half-width + null p95 beside every margin; glass-box, inspectable bound token."
result: "JOINT tiered bound-event-token coref = 1.000 (CI half-width 0.000; scorer = balanced accept/reject over positive / hard-neg-recombination / easy-neg event-mention probes; n=900 probes over 30 LitBank passages [226 events/passage, OLD fiction] AND n=10,331 probes over 353 UD-EWT passages [41 events/passage, MODERN web]) vs late-fusion-of-marginals 0.600 [0.600,0.600] LitBank / 0.596 [0.595,0.597] UD-EWT -> CI-separated +0.400 / +0.403."
floor: "strongest REAL floor = late-fusion-of-marginals silo (the reader's ACTUAL per-dimension-list structure): 0.600 LitBank / 0.596 UD-EWT. Lexical/surface floor identical (0.600 / 0.596). Info-free twin null p95 = 0.600 / 0.607. Symbolic per-event-tuple CEILING = 1.000 (the joint's target; the FHRR bound token TIES it, the silo cannot reach it)."
controls: "(1) BINDING-SHUFFLE (permute within-event bindings; marginals identical, joint destroyed) collapses joint 1.000 -> 0.637 [0.621,0.653] LitBank / 0.637 [0.630,0.644] UD-EWT, CI-separated BELOW intact joint; the crisp signature is POSITIVE recognition dropping 1.000 -> 0.122 / 0.182 while marginals untouched (the conjunctive-memory dissociation). EXCLUDES 'the win is marginal frequency, not binding'. (2) INFO-FREE TWIN (random tokens, energy-matched) never accepts (pos 0.000) -> the joint's acceptances are not a decode artifact. (3) PASSAGE-SCALE COLLAPSE: flat single-superposition register 1.000 -> 0.383 at M=256 while multibank-slotted + DG/CA3-tiered hold at 1.000 -> the 1/sqrt(M) can-fail control FIRES; the tiers beat it. (4) TYPE-CARDINALITY curve: joint rejects recombinations at 1.000 for card=1/2/>=3, marginal at 0.000 at EVERY level -> EXCLUDES the brief's 'cardinality-1 joint-recoverable-from-marginals' artifact. (5) FLAT-REGISTER-IS-MARGINALS: corr(flat_score, marginal_count_sum)=0.95 -> one passage-level superposition IS the marginal silo (cannot encode the joint), so the shared token must be TIERED."
files_changed: "experiments/exp_tiered_bound_event_token_coref_v1.py; experiments/exp_grounded_binding_paraphrase_coref_v1.py (the NECESSITY test: grounded binding beats symbolic under paraphrase); experiments/_drill_ca3_completion.py (the CA3-completion wall drill); verification/test_tiered_bound_event_token_coref.py; data/exp_tiered_bound_event_token_coref_v1/metrics.json; data/exp_grounded_binding_paraphrase_coref_v1/metrics.json; notes/problems/the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token/ (SOLVED.md, SUBMISSION_SUPPORTING_hdlab_wire_and_adjacent_map.md)"
reverify: ".venv/Scripts/python.exe verification/test_tiered_bound_event_token_coref.py"
---

# The tiered bound-event-token backbone stores the JOINT the parallel silos cannot -- proven on real event structure, old + modern

## What this problem asked, and the honest headline
The p4 full-system test proved, byte-exactly, that the assembled reader is N PARALLEL SILOS: each dimension
keeps its own LIST (the set of agents / the set of actions / the set of times) and nothing stores WHICH agent
did WHICH action at WHICH time. That is the BINDING PROBLEM. This problem asked whether ASSEMBLING already-
built hdlab organs into a TIERED bound-event-token backbone -- bind all dimensions onto ONE token per event,
chunk into an active WM register, consolidate to an episodic store -- stores the JOINT the silos cannot, on
REAL event coreference, over a late-fusion-of-marginals baseline, with the binding-shuffle control losing and
the tiered register not collapsing at passage scale.

**YES, on all five gates, on OLD fiction (LitBank) AND MODERN web text (UD-EWT).** The bound-event-token
reader resolves event coreference at 1.000 vs the marginal silo at 0.600 (CI-separated +0.400); the binding-
shuffle control collapses it (positive recognition 1.000 -> 0.12); the info-free twin is the null; and the
tiered store holds at passage scale (M=256) where the flat single superposition collapses to 0.38.

## The brain frame (opening move), copied operation-for-operation
Recognising two mentions as the SAME event is not list-matching -- it is hippocampal pattern completion over
a CONJUNCTIVE code. The brain builds ONE bound event token per event, indexed on all situation dimensions at
once (Zwaan & Radvansky 1998 event-indexing; Franklin et al. 2020 SEM), and a partial re-description
reactivates the stored conjunction via CA3 auto-association (Marr 1971). The decisive evidence is the amnesia
double dissociation (Konkel & Cohen 2009): hippocampal damage spares ITEM/feature memory (the marginals --
the set of agents, the set of times) but destroys RELATIONAL/conjunctive memory (the joint -- which agent went
with which time). That dissociation IS the binding problem, and it is exactly the silo defect p4 proved. So
the faithful operation to copy is BIND -> CHUNK -> CONSOLIDATE -> COMPLETE, each onto a real built organ:
- **BIND** (`hdlab.binding` FHRR = the PINNED basis, SEM/Franklin): token = sum_r bind(ROLE_r, filler_r) over
  {AGENT, PATIENT, PRED, TENSE} -- the ONE bound token.
- **CHUNK** (`hdlab.n400_coherence_monitor` + `hdlab.situation_model_multibank`): segment the event stream at
  prediction-error boundaries (Zacks 2007 EST; the N400), keep a small active register (Cowan) -- because a
  passage-scale superposition collapses ~1/sqrt(M) (Plate/Frady).
- **CONSOLIDATE + COMPLETE** (`hdlab.hippocampal_encoder`, DG-sparse + CA3): flush segments to a pattern-
  separated episodic store; coreference = CA3 completion from a partial cue.

The NON-GAMEABLE test copies the brain's own paradigm: RECOMBINATION. My hard-negative event-mentions are
recombinations (agent from event i, action from event j -- both marginals present, the conjunction absent).
A marginal store accepts them (wrong); a bound-token store rejects them. The BINDING-SHUFFLE control permutes
the stored bindings (marginals identical, joint destroyed) and must collapse the joint reader to marginal
level -- the same manipulation Konkel & Cohen use to isolate conjunctive memory.

## What was built (all four tier organs were built ISLANDS; none was imported by the reader)
`experiments/exp_tiered_bound_event_token_coref_v1.py` assembles three of the four organs + the FHRR bind into
a tiered backbone (the fourth, `slot_attention_wm`, is a learned torch module whose learned addressing is
orthogonal to this claim -- see "NOT established"), driven by the FULLY-ON `SituationReader.read()` on real
LitBank docs and by direct gold-CoNLL-U extraction on modern UD-EWT (no external LLM, no spaCy -- glass-box).
The event-coreference instrument resolves a query event-mention (a partial re-description: 2 bound attributes)
against the passage's stored events: POSITIVE (both attributes from the same real event -> co-refers), HARD-NEG
(recombination -> does not), EASY-NEG (one attribute foreign -> does not).

## What was measured (full run; CI = 2000x bootstrap over passages)
| arm | LitBank (old, n=900 probes) | UD-EWT (modern, n=10,331) | what it is |
|---|---|---|---|
| **JOINT (tiered bound token)** | **1.000 [1.000,1.000]** | **1.000 [1.000,1.000]** | the assembled backbone |
| late-fusion-of-marginals (silo) | 0.600 [0.600,0.600] | 0.596 [0.595,0.597] | floor a (reader's ACTUAL structure) |
| lexical/surface | 0.600 | 0.596 | floor b |
| binding-shuffle control | 0.637 [0.621,0.653] | 0.637 [0.630,0.644] | must LOSE (it does) |
| info-free twin (random tokens) | 0.600 (pos 0.000) | 0.607 (pos 0.000) | null p95 |
| symbolic per-event-tuple | 1.000 | 1.000 | CEILING (joint ties it) |

- **JOINT over marginal = +0.400 / +0.403, CI-separated** (joint CI-lo 1.000 > marginal CI-hi 0.600). Over
  lexical = +0.400 / +0.403. Over shuffle = +0.347 / +0.356. Twin null p95 = 0.600 / 0.607 (joint is far above).
- **The binding-shuffle signature is the crisp one:** shuffling within-event bindings drops POSITIVE
  recognition 1.000 -> 0.122 (LitBank) / 0.182 (UD-EWT) while leaving the marginals untouched -- the reader can
  no longer recognise a genuine event mention once its bindings are scrambled. That is the conjunctive-memory
  dissociation, on real text.
- **MUST CHUNK (passage scale):** a single FLAT superposition register decodes 1.000 -> 0.383 as events
  accumulate to M=256 (the 1/sqrt(M) collapse); the multibank-slotted and DG/CA3-tiered registers hold at
  1.000. Real passages are in the collapse zone (LitBank 226, UD-EWT 41 events/passage).
- **TYPE-CARDINALITY (rules out the brief's artifact):** the joint rejects recombinations at 1.000 for
  card=1, card=2 AND card>=3; the marginal fails (0.000) at EVERY level -> the win is the binding, not a low-
  cardinality design leak. (n=290/48/22 LitBank; 3918/207/47 UD-EWT.)

## DEEPENING (owner ask): cued event retrieval + the DG separation-vs-completion trade-off
A coreferent mention rarely restates every attribute, so the brain-foundational test is CUED RETRIEVAL /
pattern completion: recover the correct event from a DEGRADED mention (drop 1-2 attributes). Measured hit@1
over uniquely-identifying partial cues (LitBank / UD-EWT):

| arm | drop0 | drop1 | drop2 | what it shows |
|---|---|---|---|---|
| bound token (FHRR cleanup) | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | content-addressable; graceful; ties symbolic |
| DG+CA3 episodic | 0.95 / 0.99 | 0.68 / 0.81 | 0.72 / 0.80 | under-completes partial cues (see below) |
| **MARGINAL silo** | **0.004 / 0.010** | **0.004 / 0.010** | **0.004 / 0.010** | **chance (1/M): STRUCTURAL capability gap** |

- **The silo is at chance at EVERY level** -- cued event retrieval is a capability class it LACKS entirely (it
  has no per-event token to address), not merely a lower score. The JOINT enables a whole family of operations
  (cued recall, pattern completion, "what did X do") the silo cannot do at all. This is a stronger statement
  than the accept/reject gap and it is the operational reason reasoning (p6) needs the bound token.
- **The bound token degrades gracefully** (1.00 at every drop) -- it is content-addressable, the neurally-
  realizable property a passage-marginal list is not.
- **HONEST FIDELITY WALL, DRILLED TO ROOT CAUSE (`experiments/_drill_ca3_completion.py`):** the DG+CA3
  episodic layer UNDER-completes very partial cues. Research drill (Marr 1971; Treves & Rolls 1994; O'Reilly &
  McClelland 1994): CA3 completion is RECURRENT attractor dynamics, and crucially DG separation is an
  ENCODING operation (orthogonalize distinct memories) -- RETRIEVAL in the brain is EC->CA3 DIRECT (perforant
  path), BYPASSING DG, because separating a PARTIAL cue pushes it AWAY from the stored pattern. My assembly
  did the un-faithful thing: it DG-separated the retrieval cue. Measured (UD-EWT, hit@1 at drop-1):
  DG-encode-cue + 1 CA3 settle rises MONOTONICALLY as DG separation is REDUCED (sparsity 0.02/0.05/0.10 =
  0.24/0.50/0.60) -- direct evidence that DG separation is what hurts partial-cue retrieval; ITERATING the CA3
  settle makes it WORSE at every sparsity (~0.01-0.03: the Hebbian net collapses to a dominant attractor); but
  the **DIRECT completion path (compare the cue to the stored bound tokens by similarity, no DG re-separation)
  = 1.00 at every sparsity**. **Conclusion: the fix is brain-faithful and
  understood** -- retrieve via the direct EC->CA3 similarity route (which the bound token natively supports and
  which completes perfectly), and reserve DG separation for ENCODING. This does NOT weaken the SOLVED claim
  (the coref bar + capacity curve use the direct/bound-token path); it CORRECTS the `hippocampal_encoder`
  retrieval path and seeds a well-scoped follow-on (a faithful CA3 completer: EC->CA3-direct retrieval + sparse
  attractor dynamics that do not collapse to a dominant attractor under iteration).

## NECESSITY (owner push): where the brain-faithful bound token BEATS a symbolic dict, not just ties it
The coref bar shows binding is SUFFICIENT (the FHRR joint ties the symbolic per-tuple ceiling at 1.00). The
regime where the brain's mechanism is NECESSARY is GRADED/PARAPHRASE matching: a coreferent mention rarely
repeats the exact words. So I built `experiments/exp_grounded_binding_paraphrase_coref_v1.py`: bind GROUNDED
sensorimotor vectors (Lancaster norms -- a static model of the ATL-hub conceptual code; Patterson 2007) via a
similarity-preserving Spatial Semantic Pointer encoding (Komer & Eliasmith), and test coref when the verb is
swapped for a WordNet synonym (WordNet defines paraphrases INDEPENDENTLY of the grounded space -- not circular).
Real UD-EWT, 5190 instances / 458 passages:

| arm | EXACT control | PARAPHRASE (verb->synonym) |
|---|---|---|
| **grounded bound token (ATL-hub concept + bind)** | 1.00 | **0.404 [0.391, 0.418]** |
| arbitrary-symbol FHRR (the main cell's codec) | 1.00 | 0.232 (chance) |
| symbolic exact-string tuple | 1.00 | 0.234 (chance) |
| grounded-SHUFFLED twin (info-free) | 1.00 | 0.227 (chance) |
| chance (uniform over candidates) | 0.234 | 0.234 |

- **NECESSITY ESTABLISHED:** under paraphrase ONLY the grounded distributed token is above chance; the symbolic
  dict, arbitrary-symbol binding, and the grounding-destroyed twin are ALL at chance. Grounded-over-symbol
  margin +0.169 [0.153, 0.185] CI-separated. The EXACT control (all arms 1.00) proves the advantage is SPECIFIC
  to graded matching -> the brain-faithful DISTRIBUTED + GROUNDED bound token does something a symbolic
  list-of-dicts structurally cannot: recognise a paraphrased event.
- **HONEST LIMIT + DRILL (the coarseness wall, understood deeply):** 0.404 is well above chance but far from
  1.00 -- the 11-dim Lancaster SENSORIMOTOR space is a COARSE proxy for the concept hub. Drilled the wall
  (`experiments/exp_grounded_distributional_fusion_paraphrase_v1.py`, smoke; full-scale run dispatched to the
  GPU queue): the brain-faithful fix is the ATL COMPLEMENTARY FUSION (embodied grounding + distributional
  context; Patterson 2007). Adding a DISTRIBUTIONAL spoke (PPMI-SVD from UD-EWT, no LLM) and FUSING gives
  hit@1 0.44 > grounded-alone 0.41 > distributional-alone 0.29. The MECHANISM is complementarity: the two
  spokes are NEAR-INDEPENDENT (correctness correlation -0.04), each solving cases the other misses
  (grounded-only-right 0.32, distributional-only-right 0.17), with an either-right CEILING of 0.61 -- far
  above either alone. This is a direct demonstration of the DUAL-ROUTE hub-and-spoke theory of meaning
  (embodied 'how' + distributional 'context'), and the concrete brain-foundational reason the reader needs the
  meaning-channel FUSION, not one spoke. The naive z-concat fusion (0.44) does not yet reach the 0.61 ceiling
  -> a learned/reliability-weighted fusion is the mapped follow-on. NOTE: heavy full-scale numbers land from
  the remote GPU run (`REMOTE_RUN_REQUEST_exp_grounded_distributional_fusion_paraphrase_v1.md`); the smoke
  values here are coverage-limited (distributional vocab grows with corpus scale).

## KEY REALIZATIONS (the enabling moves)
1. **A single passage-level superposition IS the marginal silo -- provably.** The flat register's readout for
   a probed conjunction (v1,v2) is LINEAR = count(events with r1=v1) + count(events with r2=v2), a function of
   the MARGINALS ALONE. Measured: corr(flat_score, marginal_count_sum) = 0.95. So a real joint and a frequency-
   matched recombination get identical flat scores -- one bound token superposed over the passage cannot encode
   the joint. **This is the concrete data-structure reason the reader's flat per-dimension registers are silos,
   and why the faithful shared token must be TIERED (kept separable: chunked + pattern-separated), not one
   superposition.** It converts the brief's "must chunk" from an assertion into an identity.
2. **The recombination hard-negative is the whole game.** The joint's entire advantage lives on hard negatives
   (marginal 0.000 there); on positives and easy-negatives the marginal silo already succeeds. Building the
   negatives as brain-style recombinations (same items, rebound) made the test non-gameable AND made the
   binding-shuffle control a clean analog of the amnesia dissociation.
3. **The extraction noise does NOT threaten the mechanism claim.** Both arms read the SAME (noisy) extracted
   tuples, so the +0.40 joint-vs-marginal gap is a representational fact independent of extraction quality --
   which is why it holds identically on messy old fiction and clean modern web text.
4. **DG's prior HARD_FAILs were on the wrong tier.** On the ACTIVE-read tier DG saturates; on the EPISODIC
   store (its faithful job) DG/CA3 holds retrieval flat to M=256. The brief's re-scope is confirmed on disk.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b -- strategy folds in on re-verify)
See `SUBMISSION_SUPPORTING_hdlab_wire_and_adjacent_map.md` section C. Summary: three of the four tier organs
(multibank + n400 + hippocampal) + FHRR bind are ASSEMBLED into a tiered bound-event-token backbone that
proves the JOINT on real event structure; DG/CA3 confirmed faithful on the EPISODIC tier (re-scope upheld);
new logged deviation = the n400 tau under-segments some long-coherent passages (OUR-INVENTION, sweepable);
new analytic record = one superposition == the marginals (realization 1 above).

## FOR STRATEGY: the proposed hdlab wire (Q111 -- you land it)
`SUBMISSION_SUPPORTING_hdlab_wire_and_adjacent_map.md` section A: a default-off `bind_event_tokens` flag on
`SituationReader` that builds `sm.event_tokens` + a tiered episodic store via a new thin
`hdlab/bound_event_backbone.py` assembler (composes existing organs only; byte-identical when off, wired like
the other dimension flags right before `read()`'s `return sm`). Flipping it ON by default is a separate owner
decision. This is the step from "features" to "understanding" -- the reader gains ONE bound, queryable event
representation, the prerequisite for reasoning (p6) over the story.

## What I did NOT establish / would withdraw first
- **The result is a REPRESENTATIONAL ceiling (1.000), not a hard task score.** Once you have per-event bound
  tokens, the associative-recognition decode is near-perfect at D=1024 -- that is what the bound token BUYS.
  The realism lives in (a) the extraction (shared by all arms) and (b) the passage-scale capacity (where the
  flat register genuinely collapses). I would withdraw any implication that "coref is now solved end-to-end"
  FIRST: this proves the mechanism stores the joint, not that it lifts a downstream comprehension score (that
  needs the wire + a QA task consuming the joint -- a follow-on).
- **This is the ASSOCIATIVE-RECOGNITION / cued-recall operationalisation of event coreference** (does this
  exact event -- this agent, this action -- occur?), on REAL extracted structure with brain-style recombination
  negatives. It is NOT a hand-annotated cross-document coref gold; ECB+ (named by the p4 submission, not on
  disk) is the applied follow-on that would add ecological cross-doc coreference clusters.
- **"Live" = the faithful in-experiments realization of the wired read-out**, driven by `read()`, NOT literally
  inside `read()` (Q111 bars me from landing the wire; the proposed default-off flag is exactly this backbone).
- **`slot_attention_wm` was NOT trained/used** -- it is a learned torch module whose learned addressing is
  orthogonal to the binding/coref claim, which the untrained faithful multibank register carries. Follow-on.
- **The n400 segmenter under-segments some long-coherent passages** (max segment 283/384 events at tau=1.5);
  median segment is 6/11 (Cowan-faithful). tau/decay are OUR-INVENTION and need a real-content sweep. This does
  not affect the main claim (the episodic store holds all events regardless of segmentation).

## TLDR (plain English)
Our reader tracked a story as separate lists -- who the people are, what happened, when -- but never linked
them, so it could not tell that "Mary arrived in the morning" and "John left at night" are different events
rather than a jumble of people, times and moves. We assembled parts we had already built into one memory that
binds everything about a single event into one linked tag, keeps a few recent events active, and files the rest
into a longer-term memory. We then tested whether it can do what the separate lists cannot: decide whether a
described event actually happened, when the trick is that the person and the action are each present in the
story but never together. The linked-memory version gets this right every time; the separate-lists version is
no better than a coin-flip on exactly those trick cases; and if we scramble the links (keeping the same people
and actions) it fails -- proving it was using the links, not just the lists. It works the same on 100-year-old
novels and modern web writing, and it keeps working when the story gets long, where the naive "one big blur"
memory falls apart. This is the step from the reader HAVING features to the reader UNDERSTANDING which goes
with which.

## QUESTIONS
None blocking. One decision is the owner's: whether to flip the `bind_event_tokens` wire ON by default (this
problem produces the evidence; the flip is a separate owner call and needs the wire landed first, Q111).

## NEXT STEPS
1. Strategy re-verifies (`verification/test_tiered_bound_event_token_coref.py`) and, if landing, adds the
   default-off `bind_event_tokens` flag + `hdlab/bound_event_backbone.py` per the proposed wire -- byte-
   identical when off.
2. Follow-on problems (mapped, fidelity-assessed in the supporting note; ranked by leverage):
   - **A brain-faithful CA3 completer** (NEW, DRILLED to root cause): the `hippocampal_encoder` retrieval path
     DG-separates the cue and single-steps CA3 -> under-completes (0.24-0.56), and iterating collapses to a
     dominant attractor (0.02). The fix is architectural, not a parameter sweep: EC->CA3-DIRECT retrieval
     (bypass DG separation at recall; DG is for ENCODING) + sparse attractor dynamics that do not collapse.
     The direct similarity path already completes at 1.00; the follow-on is making the CA3 net itself faithful.
     High-value, concrete, adjacent -- this is an `hippocampal_encoder` fidelity problem in its own right.
   - **Semantic fillers** (the corruption/paraphrase regime): bind SEMANTIC vectors (distributional meaning)
     instead of random symbols, so a paraphrased/pronominal mention still matches -- the regime where the
     bound token's graded similarity beats symbolic exact-match. Ties into `reader_meaning_channel`.
   - ECB+ cross-document event-coref gold (ecological validity beyond constructed recombination probes).
   - A downstream QA task that CONSUMES the bound token (features -> comprehension score, the p6 reasoning link).
   - Train `slot_attention_wm` as the active register vs the deterministic multibank; sweep the n400 tau on
     real event content for faithful segmentation (max segment 283/384 today).
