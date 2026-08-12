# Research: the tractable brain-faithful lever for cross-frame entity re-identification (the DOMINANT half of the 2026-07-30 assembly wall) — 2026-07-31

Scope: level-2 design-synthesis drill, NOT a re-catalog. Builds ON (does not repeat) three dedup files
read in full: `brain_foundational_stack_assessment_2026-07-30.md` (component ledger),
`research_structural_objective_fix_voice_invariant_role_2026-07-30.md` (role-half contrastive fix, ~40
citations, encoder-geometry locus — REDIRECTED by the next file), and
`research_dynamic_reindexing_voice_invariant_role_2026-07-30.md` (role-half reindexing decoder, ~34
citations, COGS-decisive: static readout of encoder geometry cannot hold voice-invariant role; the fix
must live in a constructed OUTPUT, not surface geometry). KB-check (`substrate_query.sh`, 3 queries) found
no prior synthesis at this precision on cross-frame ENTITY stability specifically (top cosine 0.54, all
adjacent pattern-separation/completion background notes, not this question) — genuinely new territory,
confirmed by the harness diagnostics below rather than assumed.

3 parallel Sonnet lit-scans this cycle (generic-terms-only, query-privacy compliant): (A) brain/biology —
discourse referents, complementary learning systems, hippocampal pattern separation/completion, concept
cells; (B) ML — entity-linking/coreference consistency objectives, SimCSE collapse + VICReg/Barlow-Twins
anti-collapse, disentangled role/identity representations; (C) narrower level-2 — recurrent
identity-carrying memory (EntNet/NTM/DNC), gradient-trained Tensor-Product Representations, Hopfield/dense
associative-memory pattern completion, and whether entity-stability and role-separability are one
mechanism or two. Calibration per [[feedback-lit-scan-calibration-penalty]]: P deflated 0.15-0.25,
novel-synthesis capped 0.50, ESTABLISHED/CONTESTED per claim, CITED@/REASONED@ tagged throughout.

---

## HEADLINE

The prior three encoder-objective attempts (contrastive-on-geometry, causal+PE-gate, and the role-half's
own reindexing-decoder note) all made the SAME category error the biology directly refutes: they tried to
make a mention's REP be the identity, when the brain never does that. **The common failure thread:** every
attempt treated "same entity, different frame" as a problem to be solved by making raw encoder
representations converge (or by decoding role off those same representations) — but the brain does not
store-and-match identical raw traces across mentions. It **stores once, sparsely and distinctively (DG
pattern separation), and RETRIEVES by content-addressed pattern completion (CA3 attractor dynamics) into a
persistent slot**, with identity maintained as a stable ADDRESS/index, not as representational similarity
of the surface encoding. Concept-cell literature (Quiroga et al.) is the existence proof: a single neuron
fires for "Jennifer Aniston" whether cued by a photo, her name in text, or a voice recording — wildly
different raw input statistics, same STABLE POINTER, because the pointer lives in a converged
associative-memory attractor, not in surface-feature similarity.

**The 2026-07-30 harness measurement (entity_consistency=0.795, cross-frame query agreement=0.72,
oracle-entity-file recovery capped ~0.74–0.85) confirms this diagnosis structurally, not just
biologically**: it already ISOLATED that a stable-ADDRESS fix (oracle entity-file, decoupled from raw
per-mention decode) is a candidate — that IS the pattern-completion-into-a-persistent-slot move, just not
yet framed as a learned mechanism. The harness's own `entity_file_commit` arm is a hand-built heuristic
version of exactly this; the lever below is what makes it a LEARNED, brain-faithful, generalizing
mechanism instead of a fixed-threshold nearest-centroid rule.

**KEY STRUCTURAL FINDING (this cycle's most load-bearing synthesis, per the Greff et al. 2020 binding
taxonomy — CITED@, "On the Binding Problem in Artificial Neural Networks," a systematic-review framework,
ESTABLISHED as a taxonomy though its specific mechanism claims are individually CONTESTED):** the two
measured halves of the wall are genuinely **TWO DIFFERENT BINDING SUB-PROBLEMS, not one**.
- Entity re-identification = **Representation/Segregation**: keeping WHICH-INSTANCE information distinct
  and re-addressable across time/context (a "sameness" / individuation problem).
- Role/filler attribution = **Composition**: combining a role and a filler into a structured whole in a
  position-free way (a "combination" problem).
These are dissociable in the taxonomy and in the measurement (entity_consistency 0.795 vs role_attn
0.80-0.96 degrading differently per slot) — **do not conflate them, and do not expect one fix to solve
both.** This corrects an implicit assumption in the two dedup files, which treat "role assignment" as the
single organ; entity persistence is a SEPARATE organ that happens to be the LARGER share of the measured
gap (entity_consistency 0.795 vs the ~0.85-0.96 role/filler decode floor — entity is further from ceiling).

**TOP RECOMMENDATION:** attack the DOMINANT entity-persistence half FIRST. Concretely: keep the existing
content-gated WM (already VET-confirmed, EntNet-analog — see `brain_foundational_stack_assessment`) as the
persistent slot / pattern-completion CONTAINER, and add a **LEARNED cross-mention consistency objective
with a provable anti-collapse floor (VICReg/Barlow-Twins-style variance regularization, not a
heuristic-tuned contrastive margin)** that trains the encoder's OWN mention representations to be
pattern-completion-FRIENDLY (same-entity mentions land in the same attractor basin; different entities
stay measurably separated) — replacing the harness's hand-tuned TAU-threshold nearest-centroid commit rule
with a trained retrieval-key space. This is a LEARNED competence shaping the encoder's own reps (ALLOWED);
it is explicitly NOT a borrowed embedding or bolt-on reader (see Part 3 for the defense). The role/filler
half (Composition) is a SEPARATE, already-scoped problem — the two dedup files' structured-decoder /
canonical-event-tuple direction remains the right lever for it and is not redone here.

---

## 1. Common failure thread across prior encoder attempts (synthesis, not re-catalog)

Reading the three failed/refuted role-half attempts (frozen MLM position-bound entanglement [74d4ea0c1];
forward-prediction objective satisfiable-by-position [refuted, cross-voice 0.017/0.000]; cross-voice
contrastive risk of SimCSE-style erasure-to-invariance [flagged, not yet run]; the dep-head/structural
objective as "voice-conditioned-positional" [Papadimitriou 2022 finding cited in the dedup note]) through
the ENTITY lens (not the role lens they were built for) surfaces one shared assumption:

**All of them ask a single forward pass over the CURRENT mention's tokens to produce a representation that
IS the answer** — either by making it match a canonical geometry (contrastive), by making next-token
prediction pressure induce structure (causal), or by reading role directly off that pass's hidden state
(linear probe). None of them give the model a place to WRITE a persisted identity and a mechanism to
RETRIEVE it on the next mention. This is exactly what COGS (Kim & Linzen 2020, cited in the dynamic-
reindexing dedup note) already demonstrated for the role half — flat, single-pass static readouts cannot
do structural/compositional generalization — and the entity half inherits the identical diagnosis for a
DIFFERENT reason: cross-mention identity is not a property EXTRACTABLE from one mention's tokens in
isolation at all (a fresh mention of "the dog" carries no information distinguishing it from a different
dog unless something outside that single forward pass links it to the first mention). **The common thread:
every prior attempt is a STATELESS, single-pass architecture being asked to solve a problem that is
constitutively STATEFUL (identity is a fact about the DISCOURSE HISTORY, not about the current sentence).**
This is REASONED@ (transfer from the role-half literature to the entity-half diagnosis) and is the load-
bearing insight motivating Part 3.

---

## 2. Biology: how the brain converges different mentions onto the same stable entity representation

CITED@ throughout (lit-scan A, verified via search this cycle; ESTABLISHED/CONTESTED flagged per claim).

1. **Discourse referents / situation models (ESTABLISHED framework).** Discourse Representation Theory
   (Kamp & Reyle) and Kintsch's Construction-Integration model treat a referent as an entry in an evolving
   discourse/situation model, not as a property of the triggering noun phrase's surface form; Zwaan &
   Radvansky's event-indexing model (1998; Zwaan 2025 update, carried from the dedup note) indexes entities
   along space/time/causation dimensions in a representation that is explicitly SEPARATE from the text
   surface. This gives the FORM the identity representation must take (a persistent structured slot) but
   not the retrieval MECHANISM — that is supplied by (2)-(3).
2. **Complementary Learning Systems, CLS (McClelland, McNaughton & O'Reilly 1995; O'Reilly & Norman 2002
   update — ESTABLISHED, foundational).** Two systems: a fast hippocampal system that stores sparse,
   pattern-SEPARATED traces of individual episodes (so two different entities don't blur together even
   after a single exposure), and a slow neocortical system that extracts structured, generalizable
   regularities. The load-bearing transfer here: identity-tracking needs the FAST, sparse,
   pattern-separated storage regime, not the slow structure-learning regime the role/syntax half needs —
   this is independent evidence for treating entity-persistence and role-composition as separate
   mechanisms (Part 0's key structural finding), because CLS itself argues they're handled by different
   learning systems with different statistics.
3. **Hippocampal pattern separation (dentate gyrus) and pattern completion (CA3 recurrent attractor
   network) — ESTABLISHED as the core retrieval mechanism, exact biophysical parameters CONTESTED.**
   Pattern separation (DG) orthogonalizes similar inputs into distinct sparse codes on WRITE; pattern
   completion (CA3's recurrent collaterals form an attractor network) reconstructs the FULL stored pattern
   from a PARTIAL or NOISY cue on RETRIEVE. This is precisely "a new, noisy mention of an already-known
   entity converges back onto the SAME stored representation" — the brain's literal mechanism for exactly
   the measured failure (entity_consistency 0.795: a fresh mention should snap back to the stored
   identity, not drift to a nearby-but-different address). Marr's 1971 original theory and its modern
   computational instantiations (attractor networks, and their ML descendant — modern Hopfield / dense
   associative memory, Ramsauer et al. 2020, lit-scan C) are the SAME mathematical object: content-
   addressable memory with a basin-of-attraction retrieval rule.
4. **Concept cells / invariant entity coding (Quiroga, Reddy, Kreiman, Koch & Fried 2005, Nature — 
   ESTABLISHED, replicated).** A single medial-temporal-lobe neuron responds to "Jennifer Aniston" across
   photographs, sketches, AND the printed/spoken NAME — radically different raw input statistics
   converging on ONE stable unit. This is the closest existing empirical proof that "same entity in a
   totally different framing (image vs. text-label, i.e. structurally analogous to statement-frame vs.
   question-frame vs. tag-frame) converges to the same address" is a real, achieved brain competence, and
   that it is NOT achieved by making the raw sensory/linguistic representations themselves similar
   (a photograph and a printed name have ~zero raw-feature overlap) — the convergence happens at a
   DOWNSTREAM associative/attractor layer, exactly matching (3)'s pattern-completion account and
   contradicting the "make raw reps match" framing of the failed contrastive-on-geometry attempts.
5. **Predictive-coding / recurrent entity-tracking (REASONED@ transfer from ML analogs, CONTESTED as an
   exact brain mechanism, but structurally convergent).** Computational psycholinguistic models of pronoun/
   coreference resolution and the ML entity-tracking line (Recurrent Entity Networks / EntNet — Henaff et
   al. 2017, lit-scan C) instantiate the same idea in a differentiable form: a set of KEYED memory slots,
   each updated by CONTENT-based (cosine/attention) addressing rather than positional addressing, so a new
   mention updates the slot whose KEY it best matches. This is the ARCHITECTURE-level analog of (3).

**One-paragraph answer (the direct question):** the brain does NOT make two mentions of "the dog"
converge because their raw linguistic/perceptual encodings become similar; it converges them because a
downstream, content-addressable associative memory (hippocampal CA3-style pattern completion, generalized
in concept-cell coding) retrieves the SAME stored attractor/address from any sufficiently-correlated
partial cue, having first written a pattern-SEPARATED (sparse, distinctive) trace for that entity at first
mention (DG-style). Identity lives in the ATTRACTOR the retrieval process converges to, not in surface
representational similarity across mentions — which is exactly why "pull raw encoder reps together"
(the geometry-based framing all three prior attempts share) is the wrong FORM of fix, independent of
whether the specific loss used to do it were tuned better.

---

## 3. Ranked levers, evaluated against the biology + failure-thread

Candidates from the task brief, genuinely re-assessed (not rubber-stamped) against Parts 1-2 and lit-scans
B/C.

**(b) Recurrent/situation-model state carrying entity identity forward — RANK 1 (foundation, already
partially built).** Per Part 2 point (3)/(5), this is the actual brain-mechanism CONTAINER: a persistent,
content-addressed slot memory is what pattern completion writes into and reads from. The project already
has a VET-CONFIRMED instance of this class (`brain_foundational_stack_assessment` #4: content-gated
overwrite WM, EntNet-analog, WM_PROVEN 88d050955) — this is not a new build, it is the reused substrate.
Lit-scan C (EntNet, NTM/DNC content-based addressing, and the Greff taxonomy) confirms this architecture
family is the standard, LEARNED (gradient-trained end-to-end) way to implement content-addressed slot
retrieval — none of it is hand-coded, all of it is a differentiable key-value read/write with a learned
similarity metric. **What's MISSING is not the container, it's the KEY SPACE**: the WM already has slots,
but the encoder's own mention representations (the things used to decide WHICH slot a new mention updates)
are exactly the fragile, position/context-entangled reps measured at entity_consistency=0.795. This is why
rank 1 alone (the container) is necessary but not sufficient — it motivates rank 2.

**(a) Cross-mention/cross-frame consistency objective with a MANDATORY anti-collapse guard — RANK 1
(paired with (b), this is the actionable NEW piece).** Directly targets the measured quantity
(entity_consistency, cross_frame_query_agreement). Lit-scan B is decisive on the mechanism and the risk:
- Entity-linking / biencoder entity representations (BLINK-style, Wikipedia2Vec-style — ESTABLISHED
  practice) already demonstrate that a LEARNED encoder can be trained so that mentions of the same entity
  in different contexts land near a shared entity vector, via a contrastive mention-to-entity (or
  mention-to-mention) objective — this is the closest existing ML precedent for exactly this loss shape.
  CAVEAT (CONTESTED for our regime): these are typically trained with LARGE closed or semi-closed entity
  inventories and heavy negative mining; generalization to NOVEL, never-seen-at-train entities (our
  held-out-entity crux) is comparatively under-tested in that literature.
- Coreference architectures (Lee et al. e2e-coref and successors — ESTABLISHED) pull span representations
  of co-referring mentions together via the antecedent-scoring training signal; this is evidence the
  "same-cluster mentions should be representationally close" signal is learnable from a moderate corpus
  with a real (not synthetic) supervision structure.
- **The anti-collapse requirement is the crux, and here the literature gives a STRICTLY BETTER answer than
  the naive InfoNCE margin used in the role-half dedup note.** SimCSE (Gao et al. 2021, ESTABLISHED) shows
  contrastive pull-together without sufficient structural counter-pressure collapses to a
  content-blind/near-uniform solution — this is the exact risk flagged (correctly) in both role-half dedup
  files. VICReg (Bardes, Ponce & LeCun 2022) and Barlow Twins (Zbontar et al. 2021) — ESTABLISHED,
  reasonably mature — replace a tuned negative-sampling margin with an explicit, PROVABLE
  variance-floor + covariance-decorrelation term: each representation dimension is forced to maintain a
  minimum variance across the batch, and dimensions are decorrelated. This is a STRONGER, non-heuristic
  anti-collapse guarantee than "push different entities apart by margin m" (which is exactly what the
  role-half note's SimCSE-collapse worry could not fully rule out) — it guarantees the representation space
  stays INFORMATIVE (can't collapse to a point or a low-rank subspace) independent of how well negatives
  happen to be sampled. **This is the one clear, citable upgrade this cycle contributes beyond the two
  dedup files' contrastive framing**: swap a margin-based negative-push for a VICReg/Barlow-style
  variance/decorrelation floor as the anti-collapse term paired with the cross-mention pull.
- Disentangled/object-centric representation learning (Slot Attention — Locatello et al. 2020, ESTABLISHED
  for vision, REASONED@ transfer to text) and Smolensky-style TPR give the complementary move: an
  explicit, architecturally-separate IDENTITY sub-vector (not the whole mention representation) is what
  gets pulled/pushed — avoiding entangling identity-consistency pressure with the content the mention also
  needs to carry (its role, its filler value). This directly answers the task's "internal IDENTITY-SLOT"
  framing: a small dedicated identity-key head on top of the encoder's existing latent, trained with the
  cross-mention + VICReg objective, feeding the WM's content-addressing — NOT a generated description
  string (which would reintroduce a bolt-on-reader-shaped dependency on a second text-generation/parsing
  step).

**(c) Role-separability structural objective — RANK 2, correctly SEPARATE, not this cycle's target.** Per
the Key Structural Finding (Part 0) and Greff et al.'s taxonomy, this is the Composition sub-problem, not
Segregation. The two dedup files already carry a well-developed, independently-ranked plan for it
(contrastive/structured-decoder for role; TPR-style output binding). Lit-scan C's TPR-RNN (Schlag &
Schmidhuber 2018 — a GRADIENT-TRAINED, not hand-coded, tensor-product binding mechanism, ESTABLISHED as a
working architecture) is a useful additional citation for that thread's Part 3 #2 (dependency-head
auxiliary / structured output) but does not change its ranking. Left untouched here to avoid re-doing
already-adequate work; the substrate's native FHRR bind/unbind already serves as the TPR-analog output
container per the existing ledger.

**(d) Combinations — the ACTUAL recommendation.** Rank 1 is (b)+(a) together: reuse the existing
content-gated WM (b) as the persistent pattern-completion container, and add the cross-mention
VICReg-guarded identity-consistency objective (a) as the LEARNED key-space that decides which WM slot a
new mention addresses. (c) stays a separate, already-scoped follow-on for the Composition half. This
is explicitly NOT "attack both halves with one objective" — Part 0's structural finding is that this would
repeat the conflation error.

### Allowed vs. forbidden — explicit defense

The top pick (cross-mention consistency + VICReg anti-collapse floor, feeding the existing WM's
content-addressing) is a **LEARNED competence shaping the encoder's OWN representations**: the loss trains
the SAME encoder (or a small identity-head on top of it) end-to-end on its own latents; at inference there
is no external model, no pretrained entity-embedding table, no parser, and no generated natural-language
description used as an intermediate identity key. This is explicitly distinguished from the FORBIDDEN
pattern per [[feedback_no_bolt_on_existing_reader_earn_comprehension_own_mechanism]] and
[[feedback_borrowed_embeddings_glove_bge_never_the_encoder]]: it is not GloVe/BGE/a transformer sentence-
embedding bolted in as the entity key, and it is not an external coreference/entity-linking model's output
consumed at inference. The BLINK/Wikipedia2Vec/e2e-coref literature cited above is used only as
METHODOLOGICAL precedent for the LOSS SHAPE (mention-consistency contrastive objective), exactly as the
role-half dedup notes used LISA/Strubell as methodological precedent for aux-loss shape — not as a
component to import. The identity sub-vector is a head trained jointly with (or lightly fine-tuned on top
of) the substrate's own frozen-or-lightly-tuned encoder latents, matching the allowed pattern already
established in the role-half notes (train-time gold/self-supervised target = the thing being learned;
inference-time = no external reader).

---

## 4. Cheap can-fail test — tied to the ACTUAL harness fields

Both harness files were read for real field names (not invented). Fields used below come directly from
`exp_situation_model_assembly_encoder_backed_v1.py` (`stage["entity_consistency"]`,
`bands.stage_role_attn_mean.entity_consistency`) and `exp_situation_model_assembly_entity_file_v1.py`
(`bands.entity_consistency_main`, `bands.entity_file_consistency_commit`,
`bands.cross_frame_query_agreement_commit`, `bands.oracle_entity_file_mean`, `bands.main_enc_mean`,
`bands.ref_span_mean`, `bands.addr_gap_closed_frac`, `ORACLE_RECOVER_BAR=0.85`, `COMMIT_MARGIN=0.15`,
`COMMIT_APPROACH_BAR=0.70`).

**Design (design-only; exp_dev owns pre-reg):** replace the entity-file cell's `entity_addr="commit"` arm
(hand-tuned single TAU threshold on FROZEN role_attn reps) with a NEW arm, `entity_addr="learned_commit"`:
a small identity-head trained with (i) a cross-mention pull term (same true entity's ENT-slot reps across
tag/name-event/query frames, InfoNCE or simple L2-to-running-centroid), (ii) a VICReg-style variance floor
+ covariance decorrelation term over the identity-head output (the anti-collapse guard, NOT a tuned
margin), (iii) held-out entities never seen during identity-head training. Everything else (fillers/marks
via role_attn, the WM loop, the five deterministic floors, POOLED_READER) reused UNCHANGED — one variable.

**HARD-PASS (pre-registered, tied to real fields):**
- `entity_consistency` (the `stage_role_attn_mean` field, currently MEASURED 0.795) rises to **>= 0.90**
  on HELD-OUT entities under the learned identity-head, i.e. a clear, non-marginal lift over the frozen
  baseline (not just noise around 0.795).
- The entity-file-ladder recovery gap closes substantially: `addr_gap_closed_frac` (as computed by the
  entity-file cell, `(learned_commit_mean - main_mean)/(ref_span_mean - main_mean)`) **>= 0.70** on ALL
  THREE query types (a/b/c), i.e. the learned-commit arm recovers at least 70% of the oracle-vs-main gap
  — matching or beating the existing `COMMIT_APPROACH_BAR=0.70` logic already pre-registered in that cell,
  but now on a LEARNED key space instead of the fixed TAU heuristic, and specifically on HELD-OUT entities
  (the commit cell as built does not split held-out vs trained entities — this is the one new axis the new
  arm must add).
- Anti-collapse guard holds: `entity_file_consistency_commit` (i.e. the learned-arm's analog) **>= 0.90**
  AND the identity-head's held-out inter-entity separation stays measurably high — operationalized as
  mean within-entity cosine minus mean cross-entity cosine on held-out entities **>= 0.30** (the same
  regime TAU-calibration in the entity-file cell already measures via `within`/`cross`, generalized as an
  explicit reported band rather than only used to set a threshold).

**HARD-FAIL (pre-registered):**
- `entity_consistency` on held-out entities stays **<= 0.80** (no better than the already-measured frozen
  baseline within noise) — the learned objective added nothing.
- OR `addr_gap_closed_frac` **<= 0.30** on any query type even though within-batch (non-held-out) entity
  consistency looks high — the SimCSE-style memorization/overfit-to-trained-entities signature (the direct
  entity-half analog of the role-half's "passes on trained verbs only" flag).
- OR the anti-collapse guard fails: within-minus-cross cosine on held-out entities **<= 0.10** (near
  chance-separable) even if `entity_consistency` reads high — collapse-to-a-point disguised as a pass
  (the entity-half analog of the role-half's within-voice-collapse flag). This is the SPECIFIC failure
  mode VICReg is chosen to prevent, so it MUST be checked explicitly, not assumed fixed by construction.

**PARTIAL/MIDDLE (report explicitly):** held-out `entity_consistency` in [0.80, 0.90] with
`addr_gap_closed_frac` in [0.30, 0.70] and the anti-collapse guard holding — direction confirmed
(pattern-completion-style retrieval is learnable on real reps), not yet at the bar. Given the biology
(pattern completion is a WELL-established retrieval mechanism, but no published work — per the honest gap
below — combines this exact three-term objective for held-out NL entity identity) this MIDDLE outcome is
assessed as at least as likely as HARD-PASS.

**Construction-artifact flags:** (1) held-out split is the only valid pass surface — same-entities-seen-
at-train pass is worthless (memorization). (2) verify the identity-head isn't leaking positional shortcuts
(a head that just encodes "this was the Nth entity introduced" would look like consistency without being
identity-based — check by permuting entity-introduction order across the eval set and confirming
consistency is order-invariant). (3) verify VICReg's variance floor doesn't itself degrade downstream
filler/role decode (role_attn S/P accuracy must stay within the already-measured 0.88-0.96 band — a
regression there would mean the identity-head's gradient is corrupting the shared encoder in an
unintended way, if the head is not sufficiently decoupled from the trunk).

## P estimate (deflated)

**P_deflated(HARD-PASS on held-out entities) = 0.30.** Base REASONED@ ~0.48: the biology gives strong,
convergent, ESTABLISHED support for content-addressed pattern-completion retrieval as the right FORM
(CLS + DG/CA3 + concept cells, four largely independent literatures converging on the same computational
account); the ML precedent for the LOSS SHAPE (entity-linking/coreference consistency objectives,
VICReg/Barlow-Twins anti-collapse) is mature and well-replicated in its OWN domains. Minus ~0.18
lit-calibration penalty: (a) no published work combines cross-mention pull + inter-entity push + a
VICReg/Barlow-style variance floor specifically for NATURAL-LANGUAGE entity identity across
statement/question/tag FRAMES — this is a genuine (incremental, not wild) synthesis across domains, not a
drop-in; (b) entity-linking/coreference precedent is typically evaluated with much larger corpora and
denser supervision than our synthetic harness provides, so scale-transfer is uncertain; (c) held-out-entity
generalization specifically (as opposed to held-out-mention-of-known-entity) is the least-tested axis in
the cited literature, mirroring the role-half's Petty-2022 novel-verb crux. Below the 0.50 novel-synthesis
cap. **MIDDLE/PARTIAL assessed >= as likely as HARD-PASS (P~0.40)** — a genuine lift in consistency without
full closure of the oracle gap is the most probable real-world outcome for a first attempt at this exact
combination. A HARD-FAIL would remain ambiguous between "the objective is right but under-scaled/under-
trained" and "cross-mention pull alone cannot substitute for genuine episodic pattern-separation-on-write"
(i.e., a SINGLE forward-pass identity head may still be too stateless even with a good loss — the
Part 1 diagnosis in its strongest form) — must be reported as such if it occurs, not as clean refutation.

## Honest gap (flagged per task instruction)

No single cited work runs the EXACT combination proposed: (cross-mention consistency pull) + (inter-entity
push) + (VICReg/Barlow-style provable variance floor, not a margin) + (natural-language entity identity,
not vision objects or a closed/large entity inventory) + (held-out/novel-entity generalization as the
primary evaluation axis) + (feeding a persistent content-addressed WM slot rather than being evaluated
standalone). Each PIECE is independently well-established; the COMBINATION is this cycle's synthesis and
is explicitly, honestly novel-synthesis-tier, not a literature replication. This is the load-bearing driver
of the P_deflated cap above and should not be smoothed over in any downstream framing.

## Cross-thread synthesis

- Corrects an implicit conflation in the two role-half dedup notes: entity re-identification
  (Segregation, per Greff et al.'s taxonomy) is a SEPARATE mechanism from role/filler attribution
  (Composition), not a sub-case of it — both notes' "voice-invariant role" framing does not automatically
  transfer to the entity-consistency measurement, and this note supplies the entity-specific diagnosis and
  lever those notes did not attempt.
- Reuses (does not re-litigate) `brain_foundational_stack_assessment_2026-07-30.md`'s #4/#8 verdicts: the
  content-gated WM (EntNet-analog) and native FHRR binding are BOTH already-proven organs; this note's
  contribution is the missing KEY-SPACE objective that lets the WM's content-addressing work on REAL,
  noisy, frame-varying mention reps instead of oracle ids or a fixed-TAU heuristic.
- Directly extends the entity-file cell's own strategic fork ("(A) discourse entity-file mechanism vs.
  (B) retrain encoder for context-invariant entity reps") by dissolving the false dichotomy: the lever
  here is BOTH — a discourse entity-file (the existing WM, kept) addressed by a LEARNED (not retrained-
  from-scratch, not oracle) context-invariant-ish identity key.
- Consistent with the standing invariants: no borrowed embeddings, no bolt-on reader/parser at inference,
  glass-box (the identity head's cosine-similarity commit decision is inspectable exactly like the existing
  hand-built commit arm), acquired/learned competence only.

## Substrate-product implications

This is the line between "the substrate can be TOLD which slot an entity lives in" (today's oracle/fixed-
heuristic ceiling, capped ~0.74–0.85) and "the substrate RECOGNIZES a returning entity from its own noisy
representations across however it's later mentioned" — the product-relevant difference between a scripted
demo and something that behaves like it remembers who it's talking about. A HARD-PASS or even a clean
MIDDLE result de-risks the entity half of the assembly wall independently of the role half, and gives the
existing WM (already the product's memory organ) a real, learned front door instead of a fixed threshold.

## Anchor candidates for pickup (ranked; exp_dev owns pre-reg — no inline experiment design)

1. **PRIMARY** — add a small identity-head on the existing frozen/lightly-conditioned v2 encoder's ENT-slot
   `role_attn` reps, trained with (cross-mention consistency pull across tag/name-event/query frames) +
   (VICReg-style variance-floor + covariance-decorrelation anti-collapse term), held-out-entity split
   mandatory. New arm `entity_addr="learned_commit"` on
   `experiments/exp_situation_model_assembly_entity_file_v1.py`, reusing its harness, floors, and TAU-
   calibration machinery as the fixed-heuristic control arm (`entity_file_commit` stays as a baseline
   comparator, not replaced). Fair-test = Part 4's thresholds tied to the cell's own real fields. Why now:
   directly targets the DOMINANT, just-measured half of the wall (entity_consistency 0.795, capped oracle
   recovery ~0.74-0.85) with the cheapest added head + loss term, zero architecture change to the WM.
2. **SECONDARY (unblocked, independent track)** — the role-half reindexing-decoder anchor already ranked
   PRIMARY in `research_dynamic_reindexing_voice_invariant_role_2026-07-30.md` remains the right next step
   for the Composition half; it is untouched by this note and should proceed on its own schedule, not
   sequenced strictly after #1 (the two halves are independent per Part 0's structural finding).
3. **TERTIARY (only if #1 lands PASS/PARTIAL)** — once the identity-head is trained, re-run the entity-file
   cell's `oracle_entity_file` arm ceiling check to confirm the LEARNED arm approaches (not just beats
   MAIN) the oracle ceiling, and consider whether the identity-head's key space can ALSO seed the role-half
   decoder's canonical event-tuple (shared representational substrate for both halves at the OUTPUT layer,
   even though the training objectives stay separate).

Context pointers: `experiments/exp_situation_model_assembly_entity_file_v1.py`;
`experiments/exp_situation_model_assembly_encoder_backed_v1.py`;
`notes/brain_foundational_stack_assessment_2026-07-30.md`;
`notes/research_structural_objective_fix_voice_invariant_role_2026-07-30.md`;
`notes/research_dynamic_reindexing_voice_invariant_role_2026-07-30.md`; `hdlab/slot_attention_wm.py`.

## Citations (verified count)

Biology thread (lit-scan A) — Kamp & Reyle (DRT); Kintsch Construction-Integration; Zwaan & Radvansky 1998
+ Zwaan 2025 (event-indexing situation models, carried); McClelland, McNaughton & O'Reilly 1995 (CLS,
Psych Review) + O'Reilly & Norman 2002 (Trends Cogn Sci update); Marr 1971 (original hippocampal-memory
theory); pattern separation/completion DG/CA3 computational literature (Rolls, Treves, Yassa & Stark
reviews); Quiroga, Reddy, Kreiman, Koch & Fried 2005 (Nature, concept cells, ESTABLISHED/replicated).
ML thread (lit-scan B) — BLINK / Wikipedia2Vec-style entity-linking biencoders (ESTABLISHED practice); Lee
et al. 2017/2018 (e2e coreference resolution); Gao, Yao & Chen 2021 (SimCSE, EMNLP, collapse risk, carried
from role-half note); Bardes, Ponce & LeCun 2022 (VICReg); Zbontar, Jing, Misra, LeCun & Deny 2021 (Barlow
Twins); Wang & Isola 2020 (alignment-uniformity analysis of contrastive objectives); Locatello et al. 2020
(Slot Attention, object-centric); Smolensky 1990 (Tensor Product Representations, carried).
Recurrent/binding thread (lit-scan C) — Henaff, Weston, Szlam, Bordes & LeCun 2017 (Recurrent Entity
Networks / EntNet); Graves et al. 2014/2016 (NTM/DNC content-based addressing); Schlag & Schmidhuber 2018
(TPR-RNN, gradient-trained tensor-product binding); Ramsauer et al. 2020 (modern Hopfield networks / dense
associative memory); Greff, van Steenkiste & Schmidhuber 2020 ("On the Binding Problem in Artificial
Neural Networks," systematic taxonomy — Representation/Segregation vs Composition, the load-bearing
structural distinction this note builds on).
Carried from dedup notes (not re-verified this cycle): Kim & Linzen 2020 (COGS); Papadimitriou, Futrell &
Mahowald 2022; Petty, Wilson & Frank 2022; Strubell et al. 2018 (LISA); St. John & McClelland 1990
(Sentence Gestalt); Vosse & Kempen 2000.
**Verified count this cycle: ~27 distinct works across 3 threads**, plus 6 carried/unre-verified from the
two dedup notes. ESTABLISHED/CONTESTED flagged per-claim throughout; the weakest links (held-out-entity
generalization for entity-linking/coreference objectives; no published exact-combination precedent for the
three-term identity objective; VICReg's transfer from vision/self-supervised-image regimes to a small NL
synthetic-harness regime) are named explicitly and drive the P_deflated cap.
