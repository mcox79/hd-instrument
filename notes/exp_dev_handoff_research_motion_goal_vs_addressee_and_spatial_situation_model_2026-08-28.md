# exp_dev hand-off — research: motion Goal vs Addressee/Recipient PP disambiguation for the spatial location register

**Filed-by:** research sub-agent, 2026-08-28.
**Trigger:** `notes/problems/situation_model_has_no_spatial_location_dimension/research_motion_goal_vs_addressee_and_spatial_situation_model_2026-08-28.md`
— solver-requested drill (via the `situation_model_has_no_spatial_location_dimension` problem) answering how
"to X" PPs are disambiguated between a spatial Goal reading ("went to the door") and an Addressee/Recipient
reading ("said to Alice" / "gave it to her"), plus confirmation/correction of the spatial situation-model
architecture (categorical vs metric, persistence, effortfulness). Finding: the solver's existing two-gate design
(verb-class motion gate + WordNet place-typing) is the right primary mechanism and matches VerbNet's own
Destination-vs-Recipient role split, but is provably insufficient for a specific, real subclass of caused-motion
verbs (throw/send/pass/hand/kick/mail) where verb class carries zero signal — the field's own literature
(Rappaport Hovav & Levin 2008; Xia 2014) shows this. The fix is not a richer WordNet typing rule; it's reusing
the entity-tracking/coreference state the solver already has.

**Pause state:** check `data/orchestrator_paused.flag` before shipping; this hand-off is filed regardless of
pause state per research-role convention — it is not queue authorization by itself.

Per [[feedback-no-experiment-design-in-prompts]]: this file states WHAT to test and WHY (falsifiable bands,
context pointers) — exp_dev/the problem's solver owns exact implementation (which VerbNet class list, exact
threshold, exact cell structure, seeds).

## Anchor candidates (rank-ordered)

### 1. `exp_goal_recipient_ambiguous_verb_gate_v1` (primary — cheapest, directly targets the disclosed wall)

**Anchor pointer:** research note section "Cheap decisive test" + "Falsifiable predictions" + "Substrate-product
implications" points 1–2.

**Substrate-product reading:** if this HARD-PASSes, the spatial location register's motion-detection front end
gets a THIRD gate (prior-discourse-status tie-break) that closes the specific, real gap in the existing
verb-class + WordNet-place-typing two-gate design, without discarding either existing gate — verb class still
resolves the (large) unambiguous majority of tokens; the new gate only fires for the ambiguous caused-motion
subclass. This directly de-risks the register's core "is this a Goal-relocation event or not" classification
before the interval/persistence machinery is built on top of it.

**Tier hint:** load-bearing for the register's motion-event detector specifically — a HARD-FAIL here does not
kill the register (buckets 1–2, the unambiguous verb classes, are expected to already work fine per prediction
1); it means the ambiguous-verb subclass should be scoped OUT (flagged low-confidence / dual-reading) rather
than force-resolved, which is itself a legitimate, useful negative result for the register's design doc.

**Why now:** cheap — no new data collection beyond a ~150–200 token hand-coded gold set from LitBank sentences
already on disk (three VerbNet-class-stratified buckets: pure self-motion, pure communication/transfer,
ambiguous caused-motion). No gradient training, no new external dependency; reuses VerbNet class lookup, the
existing WordNet hypernym typing, and whatever coreference/entity-registry lookup the register or the ToM
stopgap (`experiments/perceptual_access_ledger.py`) already exposes.

**Design (from the research note, exp_dev/solver owns implementation details):**
1. Assemble the three-bucket gold set (VerbNet run-51.3.2/escape-51.1 + WordNet travel/move/go troponyms for
   bucket 1; VerbNet say-37.7/give-13.1-non-caused-motion/point-behavior for bucket 2; VerbNet throw-17.1/
   send-11.1 and lexical neighbors throw/send/pass/hand/kick/mail for bucket 3), hand-labeled Goal vs
   Recipient/Addressee gold.
2. Score **Gate A** (verb-class-only: VerbNet Destination-vs-Recipient role lookup) on all three buckets —
   this validates the EXISTING mechanism first (predictions 1–2 below).
3. Score **Gate B** (Gate A + WordNet person-hypernym-vs-location-hypernym tie-break on the "to X" head noun)
   on bucket 3 only.
4. Score **Gate C** (Gate A + prior-discourse-status tie-break: does the head noun corefer to an
   already-tracked CHARACTER entity vs an already-tracked LOCATION/SCENE entity in the entity registry?) on
   bucket 3 only. For first-mention nouns not yet in the registry, Gate C should fall back to Gate B's WordNet
   typing (this fallback ordering — entity-state first, WordNet typing second — is the concrete design claim
   under test, not just "use both signals").
5. Report accuracy/F1 with CIs for all three gates on bucket 3, plus Gate A's accuracy on buckets 1–2 as the
   sanity check.

**Pre-registered bands (from the research note, verbatim):**
- **HARD-PASS**: buckets 1–2 score Gate A accuracy >95% (n≥100 each) **AND** bucket 3 gold labels are genuinely
  mixed (not >90% one way) **AND** Gate C beats Gate A by a CI-separated margin on bucket 3 **AND** the Talmy
  path-satellite gate (held-out/rare-verb + directional particle combos) scores >90% Goal/departure accuracy.
- **MIDDLE_BAND**: buckets 1–2 pass, bucket 3 is genuinely mixed, but Gate C does not CI-separate from Gate A
  (entity-tracking state doesn't help either) while Gate B also fails to separate from chance — real signal on
  the easy classes, but the ambiguous subclass genuinely requires event construal/world knowledge not
  recoverable from the signals tested here. Correct response: scope the ambiguous subclass OUT (emit both
  readings with a confidence split, or defer to a downstream consumer) rather than searching for a fourth gate.
- **HARD-FAIL**: buckets 1–2 score <85% on Gate A (the "easy" verb-class cases are not actually easy in real
  prose — a more basic problem than the one under test, report before touching bucket 3), OR Gate B's CI on
  bucket 3 overlaps 50%-chance (confirms Xia 2014 — do not ship WordNet-typing-only as the fix), OR the
  path-satellite gate falls below 90% (the existing PINNED "no manner-verb whitelist" design needs revisiting).

### 2. Spatial-register architecture corrections (secondary — folds into the register build directly, not a
separate experiment)

**Anchor pointer:** research note "Substrate-product implications" points 4–6.

**Substrate-product reading:** three design corrections/confirmations for whoever builds the location register
itself (same problem, `situation_model_has_no_spatial_location_dimension`): (a) represent location categorically
(scene/room-ID as an entity, with containment nesting) and NOT as coordinates — already the PROBLEM.md's
design, now independently re-confirmed by Rinck, Hähnel, Bower & Glowalla (1997) Exp 1–2 and Radvansky's
event-horizon model; (b) treat SPACE as a lazily-populated dimension (query/verify-on-demand) rather than an
eagerly-maintained one of equal cost to TIME, per Zwaan, Langston & Graesser (1995)'s finding that spatial
discontinuity is the weakest and most easily eliminated of the five event-indexing dimensions; (c) persistence-
at-a-distance is empirically well supported (Rinck & Bower 1995/1997) and already matches the problem's own
measured 0.99-at-K=0..20 result — no design change needed here, just confirmation.

**Tier hint:** informational/design-input, not a separate can-fail test — these should be read as constraints
on how anchor #1's register is built, not shipped as their own experiment.

## Context pointers (files, not summaries)

- `notes/problems/situation_model_has_no_spatial_location_dimension/research_motion_goal_vs_addressee_and_spatial_situation_model_2026-08-28.md`
  — full synthesis, all 4 lit-scan citation lists, HEADLINE, falsifiable bands, cross-thread synthesis
  (including a flagged possible citation-year mismatch on "Papafragou 2008" vs the verified Papafragou 2010),
  and substrate-product implications 1–7.
- `notes/problems/situation_model_has_no_spatial_location_dimension/PROBLEM.md` — the parent problem brief:
  the register's overall bar (per-entity presence intervals, CI-separated over the strongest floor, positive
  control, wire-don't-island into the ToM observation-cue front end).
- `experiments/perceptual_access_ledger.py` — the existing inline presence tracker (PATH-satellite + deixis
  logic) to generalize; PRIOR WORK, not to reproduce.
- `hdlab/coreference_resolver.py` — the mention-resolution seam (~0.65 on real narrative) that Gate C's
  prior-discourse-status tie-break depends on; degrade gracefully, per the parent problem's own note.
- `hdlab/situation_model_accumulate.py`, `hdlab/factorized_entity_store.py`, `hdlab/graded_temporal_context.py`,
  `hdlab/event_bundle.py` — the (entity, role, event) binding the location register composes with (do not
  rebuild; add the location dimension composably, FHRR-compatible).
- `hdlab/goal_typing.py` (~line 1155, `_request_object_is_addressee`) — a DIFFERENT, pre-existing addressee-
  typing mechanism in this codebase (embedded-request objects, not "to X" PPs) — not directly reusable, flagged
  for awareness only.
- `data/corpora/litbank_coref_conll` — source for the three-bucket gold set (real literary prose, already the
  parent problem's designated evaluation corpus).

## Contract section

- exp_dev/solver owns: exact VerbNet class list per bucket, exact gold-labeling procedure (single-coder vs
  double-coded), exact cell/file naming, exact entity-registry lookup API used for Gate C, exact fallback
  ordering implementation.
- Research (this hand-off + parent note) fixes: the three-bucket stratification by VerbNet class, the
  HARD-PASS/MIDDLE_BAND/HARD-FAIL bands above, the mandatory sanity check on buckets 1–2 before trusting any
  bucket-3 result, the mandatory Talmy path-satellite check, and the glass-box/no-LLM-at-inference invariant —
  every mechanism named above (VerbNet lookup, WordNet hypernym typing, coreference resolver) is a lexical/
  symbolic resource, not a black box.
- Honest asymmetry (carry into the pre-reg): buckets 1–2 (pure motion, pure communication) are expected to be
  low-risk/high-confidence per VerbNet's own role-split design; bucket 3 (ambiguous caused-motion) is the
  genuinely open question and its result should be reported separately, not folded into one combined accuracy
  number — folding them together would hide whether the register's design is solid-with-a-known-scoped-gap
  (good) vs solid-only-on-the-easy-cases (needs more work).

## Autonomy declaration

exp_dev/solver decides the exact VerbNet class enumeration, exact gold-set size beyond the n≥100/n≥150 minimums
stated in the bands, exact entity-registry lookup implementation for Gate C, and whether to build this as a
standalone experiment cell or fold it directly into the location register's motion-event detector. The
three-bucket stratification, the HARD-PASS/MIDDLE_BAND/HARD-FAIL bands, the mandatory buckets-1-2 sanity check,
and the separate-reporting requirement for bucket 3 are NOT exp_dev's to loosen or drop without flagging the
change explicitly in the pre-reg.
