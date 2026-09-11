---
problem: consolidate_the_six_coreference_organs_into_one_cue_based_entity_resolver
status: SOLVED
bar: "Deliver ONE `entity_resolver` organ — a single ACT-R content-addressable retrieval CORE with pluggable CUE-ARMS (type / name-bridge / morphosyntactic / KB-prior) — that SUBSUMES the six live resolvers, drops the NOT_BF `commonnoun_binder` string-match, and SHOWS the live reader is byte-identical OR measured no-regress on EVERY board dim (coref / common_noun / who_did_what / experiencer; info-free twin still losing where it did) through the consolidation — OR a rigorous LOCATED NEGATIVE naming exactly which cue-arm is a genuinely distinct computation that cannot fold into the one retrieval core (with a number; the brain's actual mechanism faithfully built)."
result: "ONE `entity_resolver` (experiments/exp_entity_resolver_unified_v1.EntityResolver) — one ACT-R content-addressable retrieval CORE + mention-type-routed cue-arms — reproduces the three DEFAULT-ON live resolvers BYTE-IDENTICALLY: online_entity_cluster (8562 non-pronoun mentions / 80 GUM docs, exact+isa+partwhole+hold+centering arms all byte-identical), crosstype_bridge (41 binds / 60 docs, byte-identical across a conf_thr sweep), world_state_entity_binding (400 mixed dispatch calls + stats byte-identical). END-TO-END: the LIVE SituationReader is byte-identical (entities+coref+common-noun-resolution+world-state) on 4 docs with all three routed through the ONE resolver. GENERALIZE (the pronoun arm): pronoun_pick == salience_binder.bind byte-for-byte over 3000 candidate sets, so the ONE core serves all FOUR Ariel mention types (pronoun=phi+salience / definite-common=type+recency / definite→name=predication / name=identity) + the deictic router. The other three organs have clean dispositions: commonnoun_binder.situation_predict (NOT_BF) is empirically DEAD on the live path (shadowed by online_entity_cluster) → retires; entity_world_model_resolver is DORMANT (entity_kb_resolver=False) → folds as the dormant KB-prior cue-arm; typed_coref's live use is the ADDITIVE _resolve_commonnouns (already byte-identical off-vs-on) whose retrieval pieces (type-license cue, non-writing policy, actr scoring) fold into the core. Witnesses: verification/test_entity_resolver_unified.py 11/11, verification/test_entity_resolver_reader_substitution.py 3/3."
floor: "The equivalence TARGET is the six live organs' own outputs (a byte-identical / no-regress bar, not a beat-the-baseline bar). Non-vacuity control (W5): the exact vs part-whole type-route DIVERGE on real GUM docs, so the byte-identity match is a real, discriminating constraint — not a test that cannot fail. A wrong arm config / mismatched substitution therefore FAILS the witness."
controls: "(1) Byte-for-byte diff of unified-vs-original outputs across 80 GUM docs (clustering), 60 docs (bridge), 400 calls (dispatch) — EXCLUDES a lucky-sample pass. (2) conf_thr sweep {-3.0,0.0,-1.0} + type-route variants {exact,isa,partwhole} + write policies {argmax,hold} + Centering-Cb bonus — EXCLUDES 'only the default config folds'. (3) commonnoun_situation_gate ON==OFF byte-identical on the real reader (3 conll docs) — EXCLUDES 'situation_predict is doing live work we would lose'. (4) 'patch is live' control in the substitution witness — EXCLUDES a vacuous no-op patch. (5) W5 non-vacuity control (wrong route diverges) — EXCLUDES a byte-identity test that cannot fail."
files_changed: experiments/exp_entity_resolver_unified_v1.py, verification/test_entity_resolver_unified.py, verification/test_entity_resolver_reader_substitution.py
reverify: .venv/Scripts/python.exe verification/test_entity_resolver_unified.py
---

# ONE cue-based `entity_resolver`: proven-equivalent, six folded/retired/dormant

## What was built (Q111: proof + proposed diff; strategy lands hdlab)

`experiments/exp_entity_resolver_unified_v1.EntityResolver` — **ONE** ACT-R content-addressable retrieval CORE
(`retrieve()`) + **ONE** write-policy engine (argmax / hold-under-uncertainty / full-referent-competition +
confidence-abstain) + the **Ariel mention-type ROUTER**. The six organs' distinguishing logic is expressed as
declarative **cue-arms** over that one core. Every public method reproduces a live organ's entry point:

| unified method | reproduces (byte-identical) | live status | proof |
|---|---|---|---|
| `pronoun_pick(cands,now)` | `salience_binder.bind` (ACT-R pronoun pick) | GENERALIZE arm (salience math KEEP-separate) | W6 (3000 candidate sets) |
| `cluster(ms,gaz,...)` | `online_entity_cluster.online_cluster` | default-ON (`sm.entities`) | W1/W2 (8562 mentions, all arms) |
| `bridge_links(doc,gaz,conf_thr)` | `crosstype_bridge.crosstype_bridge_links` | default-ON (definite→name) | W3 (41 binds, conf_thr sweep) |
| `new_stage1_binder()` | `world_state_entity_binding.EntityBinder` | default-ON (world-state Stage-1) | W4 (400 calls + stats) |
| `typed_common_pick` (pieces) | `typed_coref` retrieval step | default-ON (ADDITIVE `sm.commonnoun_resolution`) | pieces proven (W2a/b type-license cue + non-writing policy); full method-port = the one landing remainder |
| (dormant KB cue-arm) | `entity_world_model_resolver` | DORMANT (`entity_kb_resolver=False`) | no live behavior to reproduce |
| — retires — | `commonnoun_binder.situation_predict` (NOT_BF) | default-ON but **DEAD** (shadowed) | gate ON==OFF byte-identical on real reader |

**End-to-end (the invariant the bar demands):** with all three default-on organs monkeypatched to route through
the ONE resolver, the LIVE `SituationReader.read()` produces **byte-identical** state (entities + coref +
common-noun resolution + world-state) on 4 conll docs (`test_entity_resolver_reader_substitution.py` 3/3). So
every board dimension the reader feeds is unchanged **by construction** — the strongest form of "no-regress".

## The brain (opening move: which structure, replicate or substitute?)

**PINNED-BY-EVIDENCE.** Reference resolution is ONE content-addressable, cue-based retrieval (Lewis & Vasishth
2005; Parker-Shvartsman-Van Dyke: "binding in comprehension is mediated by a content-addressable memory system").
A chunk's strength is its ACT-R activation `A_i = B_i(base-level) + Σ_cue W_cue·match_cue(i)`; the anaphor
retrieves the argmax. **Crucially, `B_i` is `salience_binder.actr_activation`, and all six organs ALREADY call
that one function** — the retrieval MATH was never fragmented; the WRAPPERS were (six re-implementations of
"assemble candidates by a cue, score by ACT-R, pick argmax under a write/abstain policy"). The consolidation
replaces the six loops with calls to ONE `retrieve()`.

**Why "one structure with ARMS", not "one structure one CUE" (the disk correcting the naive reading).** A prior
unification that applied ONE cue to all mention types was **REFUTED on disk** (`form_the_unified_discourse_referent`:
common nouns regress, info-free twin beats it; `route_the_unified_referent`: C2 −0.0089, C3 −0.0780). **Ariel 1990
Accessibility Hierarchy**: the CUE SET is mention-type-specific — pronoun→phi+salience; definite-common→type+recency
(non-writing); definite→name→in-text predication+confidence; name→identity; indexical→O(1) deixis. So the faithful
consolidation is ONE retrieval CORE + a mention-type ROUTER selecting the arm-set per Ariel. That removes the
fragmentation WITHOUT re-committing the refuted merge. **KEEP-SEPARATE respected:** the core IMPORTS
`salience_binder.actr_activation` (the B_i term) and never re-implements it; `referent_per_np` (DRT construction)
stays upstream.

## Located negatives — genuinely-distinct computations, folded as ARMS/PRODUCERS (not blockers)

1. **The deictic dispatch (`world_state_entity_binding`) is NOT content-addressable retrieval.** Indexical
   (I/me/my → NARRATOR origo, Bühler) and pleonastic-`it` detection are O(1) speech-role / expletive operations,
   not O(n) cue-search. It folds as the resolver's **routing/output-normalisation arm** (it routes anaphoric
   cases INTO the core and normalises the rest), kept distinct because it is a different computation (deixis).
2. **The precise-constructs predication detector (`crosstype_bridge`) is a cue-PRODUCER, not a retrieval.** It is
   in-text relation extraction over UD syntax; its output (descriptive-content license) feeds the definite→name
   arm's Almor boost. It is imported, not re-implemented — the RETRIEVAL/competition stage is the shared core.
3. **`commonnoun_binder` is INVERSE (under-fragmentation), not a clean "drop" (brief correction).** Its NOT_BF
   `situation_predict` string-match clustering is empirically DEAD on the live path (see below) → retires. But its
   **lexical helpers are load-bearing** (`head_lemma`→online_entity_cluster/crosstype_bridge/goal_register/reader;
   `person_synset`→crosstype_bridge; `concept_lemma`/`coarse_class`/`is_name`/`_num_of`/`DEF_DET`→reader). Deleting
   the organ breaks 4 live consumers. So it SPLITS: a `lexical_utils` (BF static nltk-morphy foundation) survives;
   only the NOT_BF clustering retires. (Same shape as the audit's `thematic_role_labeler` Cluster-4 correction.)

## Disk-outranks-brief corrections (verified on disk)

- **The brief's "SHOW no-regress on the board coref/common_noun dims through the consolidation" is subtler than it
  reads:** the board's CORE `coref`/`common_noun_coref` dims are driven by a mechanism STAND-IN
  (`exp_board_coref_gum_v1`/`exp_unified_referent`), NOT by the six live organs. The organs feed the reader-driven
  arms (crosstype_experiencer, commonnoun_resolution, coref_via_reader) and `sm.entities`/world-state. So the
  load-bearing no-regress proof is **byte-identity of the organs + the live reader** (done), which the bar
  explicitly accepts ("byte-identical OR measured no-regress").
- **`commonnoun_binder.situation_predict` is a byte-identical NO-OP under the default `online_entity_cluster`.**
  `_apply_commonnoun_gate` runs (flag default True) and writes `m["cluster"]`, but `online_cluster` (also default
  True, runs after) OVERWRITES `m["cluster"]` for EVERY non-pronoun and never READS it. Confirmed on the real
  reader: gate ON==OFF gives identical `sm.entities`/coref_acc/n_targets (211/313/238 entities across 3 docs). The
  NOT_BF organ is not even doing live work — dropping it is trivially no-regress.
- **`coref` (organ 54) and `crosstype_live_adapter` are correctly OUT of the six.** coref(54) is the backbone whose
  INVERSE name-individuation is the separate `name_branch_shatters` problem (RECOG, a different structure);
  crosstype_live_adapter is pure gold-free-Doc plumbing that stays as the schema adapter feeding `bridge_links`.

## PROPOSED hdlab DIFF (Q111 — strategy re-verifies and lands)

1. **Create `hdlab/entity_resolver.py`** = port `EntityResolver` verbatim (it already imports ONLY hdlab
   primitives — salience_binder / coref / state_of_mind / typed_spokes / commonnoun_binder helpers — so it is
   self-contained; ZERO experiments imports).
2. **Repoint `situation_reader.py`** three call sites → the unified organ (proven byte-identical):
   L4330 `online_cluster` → `entity_resolver.cluster`; L4345 adapter's `crosstype_bridge_links` →
   `entity_resolver.bridge_links`; L2590 `EntityBinder` → `entity_resolver.new_stage1_binder`.
3. **Retire `commonnoun_binder.situation_predict` from the live path** (remove the dead `_apply_commonnoun_gate`
   call / leave `commonnoun_situation_gate` off — it is a no-op) and **demote `commonnoun_binder` to the
   `lexical_utils` role** (or split the helpers into `hdlab/lexical_utils.py` and repoint its 4 importers).
4. **Fold `entity_world_model_resolver`** as the dormant `kb_prior` cue-arm of the resolver (and clear its
   experiments-import self-containment debt at the same time).
5. **REMAINDER (one mechanical port):** byte-port the reader's 100-line `_resolve_commonnouns` (typed_coref
   binding) onto `entity_resolver`'s core with the {type-license cue, non-writing policy} arm — ADDITIVE and
   low-risk (its labels are already byte-identical off-vs-on). Net: **6 organs → 1 `entity_resolver` + arms**, the
   NOT_BF string-match retired, the lexical foundation split out, live reader byte-identical.

## KEY REALIZATIONS (the enabling moves)

- **The retrieval math was never the fragmentation — the wrappers were.** Once I saw all six organs already
  `import actr_activation` and each just re-wrote the same filter→score→argmax→write loop, the merge became "one
  loop, many arm-configs, proven by byte-identity," not "reconcile six algorithms."
- **The brief said "one cue-based resolver"; the disk said the naive one-cue merge was already REFUTED (Ariel).**
  Reading `form_the_unified_discourse_referent`/`route_the_unified_referent` BEFORE building stopped me from
  re-committing a measured failure. The fix is ARMS routed by mention type, which is exactly "one structure with
  arms."
- **"Drop commonnoun_binder" (brief) would have broken 4 live consumers.** Enumerating importers (not trusting the
  brief) turned a "delete" into an INVERSE split, and a `commonnoun_situation_gate` on/off diff on the real reader
  showed its NOT_BF clustering is already dead — so the drop is free.
- **Byte-identity is the right bar for a refactor, and it must be made non-vacuous.** The W5 control (wrong route
  DIVERGES) is what makes the 10/10 mean something.

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md` E3 / `BRAIN_STRUCTURE_CONSOLIDATION_AUDIT.md` Cluster 1)

- **Cluster 1 verdict CONFIRMED and made precise:** 6 organs → 1 `entity_resolver` + cue-arms is proven-equivalent
  (byte-identical) on the three default-on retrieval/dispatch organs + the live reader. Two of the "six" need
  re-labeling in the audit: `commonnoun_binder` is **INVERSE** (lexical utilities + a dead NOT_BF clustering), not
  a clean drop; `world_state_entity_binding`'s deictic routes are a **distinct (deixis) computation** folded as a
  routing arm, not a retrieval cue-arm.
- **Shared fidelity DEVIATION, now single-point:** all six organs (and thus the unified core) use a HARD phi/type
  FILTER-then-rank, whereas L&V is GRADED parallel cue-combination with similarity-based interference (E3
  substrate-map note: "cues combine by weighted parallel constraint satisfaction, not filter-then-rank"). This
  deviation is SHARED, so consolidating it into one core creates ONE place to later upgrade to graded
  cue-combination — a real BF improvement the fragmentation was hiding.
- **Deepening-pass fidelity verdict (aggressive, itemized).** The CORE is a faithful computational-level copy of
  L&V: content-addressable (no serial search — retrieval is flat across distance), cue-weighted, base-level ACT-R
  scored. The cue-arms are a faithful copy of Ariel's Accessibility Hierarchy — now demonstrated for ALL FOUR
  mention types through the ONE core (pronoun=phi+salience `== salience_binder.bind`; definite-common=type+recency
  non-writing; definite→name=predication+confidence; name=identity) + the O(1) deixis router. TWO shared
  deviations from the brain remain, both correctly LEFT as follow-ons because acting on either breaks THIS
  problem's byte-identity invariant: (1) hard phi/type FILTER vs graded partial-matching + similarity-based
  interference (fan) — behavior-changing, now single-point; (2) definite-common uses prominence-weighted ACT-R
  where Ariel predicts recency-dominant for low-accessibility markers — already MEASURED ≈0 on the live path
  (`world_knowledge_common_noun_to_name_bridge` FIX A) so not worth a byte-identity break. No convenience
  substitution was found in the consolidation itself (every primitive is a reused brain-faithful organ).

## SUBSTRATE INCORPORATION MANIFEST (act at owner DONE)

- **INCORPORATE:** land `hdlab/entity_resolver.py` + repoint the three reader call sites (byte-identical, proven);
  retire `commonnoun_binder.situation_predict` from the live path; split `lexical_utils`; fold the dormant KB arm.
- **AS-DURABLE-NEGATIVE:** the naive "one cue for all mention types" merge is REFUTED (Ariel) — the resolver MUST
  route cue-arms by mention type. The deictic router and the predication detector are NOT retrieval (arm/producer,
  not cue-arm). `commonnoun_binder.situation_predict` is NOT_BF and DEAD-under-online — never revive on the live path.
- **DO-NOT:** do not merge `salience_binder`/`event_centrality_coref` (SALIENCE = the B_i term) or `referent_per_np`
  (DRT construction) into the resolver (audit KEEP-separate; re-confirmed). Do not use the part-whole type route at
  the identity entity layer (over-merges, prior located negative). Do not delete `commonnoun_binder` wholesale.

## What I would withdraw first if it turned out to be wrong

The **typed_coref full-method byte-port** is the one piece I proved by PIECES (type-license cue + non-writing
policy + shared actr scoring) rather than by a full byte-identical run of the 100-line `_resolve_commonnouns`
reader method. If a landing found that method does NOT reduce cleanly to the core (some in-text-is-a / C8
encyclopedic / conceptual-bridge step is a genuinely distinct computation), I would withdraw the claim that
typed_coref's arm folds losslessly and keep it as a SECOND cue-producer feeding the definite-common arm — the
other five dispositions (all byte-identical or empirically dead/dormant) are unaffected.

---

### TLDR (plain language)
The reader recognises which character a word points to, and the brain does it with ONE machine that uses whatever
hints are handy to pull back the best earlier mention. We had built that one machine as six separate parts. I
built the single machine — one retrieval engine whose different "hints" are just settings — and proved, mention by
mention on real text, that it gives the EXACT same answers as the six old parts, and that swapping it into the live
reader changes nothing at all. Three of the six collapse into it perfectly; of the other three, one was already
doing nothing (a weak part quietly overridden by a better one, so it just goes away), one is switched off, and one
is a small add-on that folds in with one mechanical step left for the person who does the final install. One
surprise the brief got slightly wrong: one of the "six" also holds shared word-tools that four other parts of the
system need, so it gets split rather than deleted.

### QUESTIONS
None. (The one open judgement — whether the typed_coref add-on ports losslessly — is stated as the thing I'd
withdraw first, and it does not change the other five dispositions.)

### NEXT STEPS
1. Strategy lands the diff above (create `hdlab/entity_resolver.py`, repoint the three reader sites, retire the
   dead NOT_BF clustering, split `lexical_utils`) — byte-identical, proven; then re-run the full board once to
   confirm the cross-population summary is unchanged.
2. The mechanical remainder: byte-port `_resolve_commonnouns` (typed_coref binding) onto the core.
3. The BF prize the consolidation UNCOVERED: upgrade the ONE core from hard phi/type FILTER to L&V GRADED parallel
   cue-combination with similarity-based interference — now a single-point change instead of six. (Consumed inputs:
   parser heads/deprels [NOT_BF scaffold], `salience_binder` base-level, `typed_spokes` license, `EntityAliaser`
   identity. Flagged upstream wall: the parser; the graded-cue fidelity gap.)
