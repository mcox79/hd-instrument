---
problem: the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token
status: SOLVED
bar: "PASS = the bound-event-token reader resolves whether two event-mentions co-refer (needs the JOINT: same agent AND time AND place/cause) CI-separated over (a) a LATE-FUSION-OF-MARGINALS baseline (score the separate dimension lists, combine) and (b) a lexical/surface baseline -- with the BINDING-SHUFFLE control (permute the within-event bindings; the marginals are invariant, the joint breaks) LOSING CI-separated, AND the tiered register NOT collapsing at passage scale (the single-superposition 1/sqrt(M) collapse is the can-fail control the tiers must beat). Report CI half-width + null p95 beside every margin; glass-box, inspectable bound token."
result: "JOINT tiered bound-event-token coref = 1.000 (CI half-width 0.000; scorer = balanced accept/reject over positive / hard-neg-recombination / easy-neg event-mention probes; n=900 probes over 30 LitBank passages [226 events/passage, OLD fiction] AND n=10,331 probes over 353 UD-EWT passages [41 events/passage, MODERN web]) vs late-fusion-of-marginals 0.600 [0.600,0.600] LitBank / 0.596 [0.595,0.597] UD-EWT -> CI-separated +0.400 / +0.403."
floor: "strongest REAL floor = late-fusion-of-marginals silo (the reader's ACTUAL per-dimension-list structure): 0.600 LitBank / 0.596 UD-EWT. Lexical/surface floor identical (0.600 / 0.596). Info-free twin null p95 = 0.600 / 0.607. Symbolic per-event-tuple CEILING = 1.000 (the joint's target; the FHRR bound token TIES it, the silo cannot reach it)."
controls: "(1) BINDING-SHUFFLE (permute within-event bindings; marginals identical, joint destroyed) collapses joint 1.000 -> 0.637 [0.621,0.653] LitBank / 0.637 [0.630,0.644] UD-EWT, CI-separated BELOW intact joint; the crisp signature is POSITIVE recognition dropping 1.000 -> 0.122 / 0.182 while marginals untouched (the conjunctive-memory dissociation). EXCLUDES 'the win is marginal frequency, not binding'. (2) INFO-FREE TWIN (random tokens, energy-matched) never accepts (pos 0.000) -> the joint's acceptances are not a decode artifact. (3) PASSAGE-SCALE COLLAPSE: flat single-superposition register 1.000 -> 0.383 at M=256 while multibank-slotted + DG/CA3-tiered hold at 1.000 -> the 1/sqrt(M) can-fail control FIRES; the tiers beat it. (4) TYPE-CARDINALITY curve: joint rejects recombinations at 1.000 for card=1/2/>=3, marginal at 0.000 at EVERY level -> EXCLUDES the brief's 'cardinality-1 joint-recoverable-from-marginals' artifact. (5) FLAT-REGISTER-IS-MARGINALS: corr(flat_score, marginal_count_sum)=0.95 -> one passage-level superposition IS the marginal silo (cannot encode the joint), so the shared token must be TIERED."
files_changed: "experiments/exp_tiered_bound_event_token_coref_v1.py; verification/test_tiered_bound_event_token_coref.py; data/exp_tiered_bound_event_token_coref_v1/metrics.json; notes/problems/the_assembled_reader_is_parallel_silos_assemble_the_tiered_bound_event_token/ (SOLVED.md, SUBMISSION_SUPPORTING_hdlab_wire_and_adjacent_map.md)"
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
2. Follow-on problems (mapped, fidelity-assessed in the supporting note): ECB+ cross-document event-coref gold
   (ecological validity); a downstream QA task that CONSUMES the bound token (features -> comprehension score);
   train `slot_attention_wm` as the active register vs the deterministic multibank; sweep the n400 tau on real
   event content for faithful segmentation.
