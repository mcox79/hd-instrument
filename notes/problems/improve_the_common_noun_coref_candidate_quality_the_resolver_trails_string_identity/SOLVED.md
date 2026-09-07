---
problem: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
status: SOLVED
bar: "It BEATS same-head string-identity CI-separated on MODERN GUM common-noun coref, floor recomputed on the SAME population (string-identity 0.5412 is the floor to beat; the live URG resolver 0.4879 is the incumbent it must also clear) ... The info-free twin LOSES CI-separated ... NO pronoun-dim regress + NO named-antecedent regress."
result: "BEATS the floor. On the board's OWN common_noun_coref instrument (URG resolver, MODERN GUM TEST=odd docs, n=2855 anaphoric common-noun mentions, metric = picked-referent.dominant_gold_eid == mention.eid), a brain-foundational candidate-generation + identity-representation upgrade scores 0.5671 vs same-head string-identity 0.5412 -- delta +0.0259 CI[+0.0134,+0.0385] CI-separated -- and vs the live incumbent 0.4879, +0.0792. THREE mechanism-driven, brain-faithful levers (each UNEARTHED by diagnosing why the naive versions failed): (1) TYPED CARD VIEW -- score common-noun coref on the referent's NOMINAL identity (name+common mentions), so weak pronoun bindings (~47% accurate) never pollute it; this alone recovers the incumbent +0.0439 CI[+0.0311,+0.0572] to ~parity with string-identity (0.5317). (2) NON-WRITING (Nref hold-under-uncertainty; Nieuwland) DIFFERENT-HEAD BRIDGE -- a definite with no same-head antecedent resolves to the most-salient TYPE-compatible antecedent for THIS reference, but does NOT commit the merge into the shared card; this adds +0.0354 CI[+0.0285,+0.0430] over the typed base and carries the beat. (3) HIGHER-FIDELITY TYPE COMPARATOR -- the bridge candidate set is seeded by the substrate's LANDED sense-resolved typed-spokes organ (hdlab.typed_spokes.coref_type_license: synonym + is-a both directions + part-whole; Lambon-Ralph typed spokes) instead of a crude WordNet 2-hop-hypernym MFS; the organ BEATS the WordNet comparator +0.0053 CI[+0.0023,+0.0087] (0.5671 vs 0.5618) -- strictly more brain-foundational AND higher score, REUSING an existing organ. Controls: the info-free twin (a bridge fires but to a RANDOM gn-compatible antecedent -> the TYPE signal is destroyed) LOSES CI-separated (win-twin +0.0273 CI[+0.0214,+0.0342]); the WRITING version of the same bridge does NOT beat the typed base (0.5082, CI-below) -- confirming the mechanism is the write-pollution, not the resolution (and it worsens with the higher-fidelity comparator, which licenses more bridges -> more pollution when written); NO regress on pronoun (byte-identical +0.0000, mirrored common binding), kb-hardlink (+0.0000), or named-antecedent (+0.0241, IMPROVES). Ceiling context: gold-cluster oracle 0.5825."
floor: "Strongest floor actually run, recomputed on the SAME n=2855 GUM-TEST common-noun population + the SAME board scorer: same-head STRING-IDENTITY = 0.5412 (the floor to beat -- the win clears it +0.0189 CI[+0.0084,+0.0325]). Live incumbent URG unified = 0.4879 (also cleared, +0.0739). Other floors: recency 0.0855; separate 0.4872. Ceilings on the same population: typed-view-only (de-pollution) 0.5317; gold-cluster oracle 0.5825; correct-pronoun-binding upstream ceiling 0.5124."
controls: "(1) INFO-FREE TWIN = when the type-bridge fires, resolve to a RANDOM gn-compatible prior referent (the reach STRUCTURE is preserved, the TYPE information destroyed): LOSES CI-sep (win-twin +0.0206 CI[+0.0146,+0.0268]) -> the gain is the type-compatibility signal, NOT 'any different-head reach helps'. (2) WRITE-vs-NOWRITE ablation isolating the failure mechanism: the WRITING bridge (merges the resolved mention into the shared card) does NOT beat the typed base (0.5236, delta CI incl 0), the NON-WRITING bridge does (+0.0301 CI-sep) -> the cost was the merge-pollution, not the resolution (Nref hold-under-uncertainty is the fix). (3) TYPED-VIEW isolation: the typed view alone recovers the incumbent +0.0439 CI-sep but only TIES string-identity (CI[-0.0203,+0.0007]) -> the de-pollution is not itself the beat; the BEAT is the candidate-generation bridge (excludes 'de-pollution did it'). (4) NO-REGRESS on every other live consumer, mirrored-incumbent common binding making the referent structure byte-identical for pronouns: pronoun +0.0000, kb-hardlink +0.0000, named-antecedent +0.0241 (improves) -> the win costs no consumer. (5) GOLD-CLUSTER ORACLE 0.5825 -> the win (0.5618) closes ~53% of the glass-box-reachable headroom above string-identity; the residual is world-knowledge (the different-head slice is 84.3% world-knowledge / abstract-anaphora, measured -> the sibling P31 entity-type-KB brief). (6) NO test-tuned parameters (structural mechanisms; decay = DEFAULT; bridge is deterministic)."
files_changed: "experiments/exp_commonnoun_candidate_diagnostic_gum_v1.py, experiments/exp_commonnoun_lever_ceilings_gum_v1.py, experiments/exp_commonnoun_clustering_probe_gum_v1.py, experiments/exp_commonnoun_bridge_probe_gum_v1.py, experiments/exp_commonnoun_metric_audit_gum_v1.py, experiments/exp_commonnoun_weighted_cs_resolver_gum_v1.py, experiments/exp_commonnoun_recallsafe_bridge_resolver_gum_v1.py, experiments/exp_commonnoun_diffhead_anatomy_gum_v1.py, experiments/exp_commonnoun_typed_identity_gum_v1.py, verification/test_commonnoun_candidate_diagnostic.py, verification/test_commonnoun_lever_ceilings.py, verification/test_commonnoun_metric_audit.py, verification/test_commonnoun_recallsafe_bridge_resolver.py, verification/test_commonnoun_diffhead_anatomy.py, verification/test_commonnoun_typed_identity.py, data/exp_commonnoun_candidate_diagnostic_gum_v1/metrics.json, data/exp_commonnoun_lever_ceilings_gum_v1/metrics.json, data/exp_commonnoun_clustering_probe_gum_v1/metrics.json, data/exp_commonnoun_bridge_probe_gum_v1/metrics.json, data/exp_commonnoun_metric_audit_gum_v1/metrics.json, data/exp_commonnoun_weighted_cs_resolver_gum_v1/metrics.json, data/exp_commonnoun_recallsafe_bridge_resolver_gum_v1/metrics.json, data/exp_commonnoun_diffhead_anatomy_gum_v1/metrics.json, data/exp_commonnoun_typed_identity_gum_v1/metrics.json, notes/problems/improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity/SOLVED.md. NO hdlab/ writes (Q111 -- proposed wires stated below). Reuses data/corpora/gum/ (pinned V12.1.0, on disk)."
reverify: ".venv/Scripts/python.exe verification/test_commonnoun_typed_identity.py (6/6, the WIN)  AND  test_commonnoun_candidate_diagnostic.py (4/4)  AND  test_commonnoun_lever_ceilings.py (3/3)  AND  test_commonnoun_metric_audit.py (3/3)  AND  test_commonnoun_recallsafe_bridge_resolver.py (6/6)  AND  test_commonnoun_diffhead_anatomy.py (3/3)"
---

# SOLVED -- common-noun coref BEATS string-identity via a typed identity view + a non-writing (Nref) type bridge

**STATUS: SOLVED** (solver scope; WIP until the owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written -- the mechanism is proved in `experiments/` + `verification/`; the Q111 wire is proposed below.

The path here is worth stating because it is what actually produced the win: I first hit a wall (no naive candidate/
ranking lever beats string-identity), then **diagnosed WHY each naive lever failed at the mechanism level**, and the two
failure mechanisms handed me the two levers that DO win. The owner's push -- *"do we fully understand why those didn't
pan out?"* -- is exactly what unearthed the solution.

## The result (board's own instrument, GUM modern TEST, n=2855 anaphoric common-noun mentions)

| arm | common-noun acc | vs string-identity (0.5412) |
|---|---|---|
| recency floor | 0.0855 | -- |
| **live incumbent URG** | **0.4879** | -0.0532 (CI-below -- the defect) |
| typed view only (de-pollution) | 0.5317 | -0.0095 (ties; recovers incumbent +0.0439 CI-sep) |
| typed + WRITING type bridge | 0.5082 | (below typed base -- pollution, worse with more relations) |
| typed + NON-WRITING bridge, WordNet-MFS comparator | 0.5618 | +0.0189 CI[+0.0084,+0.0325] CI-sep |
| **typed + NON-WRITING bridge, typed-spokes organ (the win)** | **0.5671** | **+0.0259 CI[+0.0134,+0.0385] CI-SEP** |
| info-free twin (random bridge) | 0.5398 | type signal destroyed -> LOSES to the win, +0.0273 CI-sep |
| gold-cluster oracle (ceiling) | 0.5825 | world-knowledge ceiling |

**No-regress:** pronoun +0.0000 (byte-identical), kb-hardlink +0.0000, named-antecedent +0.0241 (improves).
**Fidelity:** the sense-resolved typed-spokes organ beats the crude WordNet-MFS comparator +0.0053 CI[+0.0023,+0.0087] CI-sep.

## 0. How the brain does this (PINNED vs OUR-INVENTION) -- both winning levers are brain-faithful
- **PINNED (retrieval).** Coreference is incremental content-addressable cue-based retrieval (Lewis & Vasishth 2005): for
  a DEFINITE common noun the dominant cue is descriptive CONTENT/TYPE (Ariel 1990 Accessibility -- a full definite NP
  retrieves a type-identified antecedent, unlike a pronoun which marks the most-active one). The E3 substrate store
  (`substrate_map --organ E3`) states the brain does weighted PARALLEL constraint satisfaction, not hard filter-then-rank
  -- so I built the type cue as candidate GENERATION (reach type-compatible antecedents), not a hard head-gate.
- **PINNED (identity representation).** A discourse referent is a FILE CARD whose IDENTITY is carried by its naming /
  nominal descriptions; pronouns are transient deictic pointers that do not RE-DESCRIBE the entity (Ariel; Gundel-Hedberg-
  Zacharski givenness). -> reading out "which entity is this common noun" should weight the NOMINAL evidence, not the
  transient (and, in our system, only ~47%-accurate) pronoun bindings. This is the TYPED CARD VIEW.
- **PINNED (uncertainty).** Under referential ambiguity the brain HOLDS rather than commits (Nieuwland & Van Berkum Nref).
  -> a low-confidence type-bridge resolves the current reference for comprehension but does NOT corrupt the entity record.
  This is the NON-WRITING BRIDGE.
- **OUR-INVENTION-UNDER-TEST (not adopted as numbers):** which cues seed the bridge candidate set (WordNet 2-hop-hypernym,
  apposition/copula, name-containment); the ACT-R decay (left at DEFAULT). No parameter is tuned on TEST.

## 1. The enumeration + the wall (why the naive levers were needed and why they failed)
`exp_commonnoun_candidate_diagnostic` reproduces the defect EXACTLY (incumbent 0.4879 vs string-identity 0.5412, n=2855)
and localizes it: **66.3% of anaphors are reachable by head** (string-identity 0.817 there, incumbent only 0.736 -- it
LOSES 214 same-head items string-identity gets), **33.7% are different-head only** (string-identity scores ALL 0). The
first pass of levers all failed, and the failures are the story:
- **Same-head SPLITTING is net-negative** on BOTH the board metric and field-standard CoNLL (`exp_commonnoun_clustering_probe`,
  `exp_commonnoun_metric_audit`): modern-GUM same-head groups are mostly single-entity, so splitting breaks more correct
  merges than it fixes. (This also refuted the "the board metric under-penalizes over-merge" hypothesis -- string-identity
  wins on CoNLL too.)
- **The weighted-CS resolver ties, and its info-free twin does NOT lose** -- so the same-head RANKING has no glass-box
  headroom; the same-head content cue is the whole signal and string-identity already has it.

## 2. WHY the naive fixes failed -> the two levers (the owner's question, answered mechanistically)
- **Diagnosis A -- de-pollution recovered common but REGRESSED pronoun.** Turning off pronoun writeback (`rs_nopollute`,
  `exp_commonnoun_recallsafe_bridge_resolver`) recovered +0.045 but crashed the pronoun consumer, because ONE shared
  `dominant_eid` served both consumers. **Mechanism:** the entity's nominal identity and its full mention set are the same
  field. **LEVER (typed card view):** give the card TWO reads -- a NOMINAL dominant (name+common) for the common-noun
  consumer and a FULL dominant (incl. pronouns) for the pronoun consumer. Pronouns still write to the full card (pronoun
  scoring untouched), but never pollute the nominal identity. Result: common recovers +0.0439 CI-sep, pronoun BYTE-IDENTICAL.
- **Diagnosis B -- the different-head bridge netted ~0.** Even the highest-precision in-text bridge (apposition/copula
  "Google is a company") netted -0.0007 (`exp_commonnoun_diffhead_anatomy`), yet each bridged item is scored on the card it
  resolves TO, so a correct bridge should be +1 and a wrong one 0 -- the loss had to be elsewhere. **Mechanism:** MERGING
  the bridged mention into the shared card shifts THAT card's dominant, breaking OTHER (later same-head) items -- the WRITE,
  not the resolution, is the cost. **LEVER (non-writing / Nref bridge):** resolve the definite to the type-compatible
  antecedent for THIS reference decision, score it, but do NOT commit the merge (open the mention's own referent for future
  same-head links). Result: +0.0301 CI-sep over the typed base, carrying the beat over string-identity; the WRITING version
  (0.5236) confirms the write was the cost.

## 3. Controls (all clean)
- **Info-free twin LOSES CI-sep** (`exp_commonnoun_typed_identity`, twin_mode=random_bridge): when the bridge fires it
  resolves to a RANDOM gn-compatible antecedent -- same reach structure, TYPE signal destroyed -> 0.5412 vs the win 0.5618,
  +0.0206 CI[+0.0146,+0.0268]. So the type-compatibility information is load-bearing, not "any different-head reach".
- **No-regress, by construction + measured:** the common binding mirrors the incumbent EXACTLY (hard-gn + most-recent), so
  the referent structure the pronoun pick reads is byte-identical -> pronoun +0.0000, kb +0.0000; named-antecedent +0.0241
  (the typed view + aliaser anchor names better).
- **Write-vs-nowrite ablation** isolates the failure mechanism (the merge-pollution) as the reason the naive bridge failed.
- **No parameter tuned on test** (structural levers; deterministic bridge; decay at DEFAULT).

## 4. Honest scope of the win (what I did NOT establish / would withdraw first)
- **The win is a per-mention RESOLUTION-accuracy gain (the board's dominant-eid instrument), not a cluster-F1 (CoNLL)
  gain.** By design the non-writing bridge HOLDS the merge (Nref), so it does not improve MUC/B3/CEAFe clustering -- it
  improves whether each common-noun mention is resolved to the right entity, which is the board's metric and the
  downstream-relevant quantity (affect/goal/relational binding need the referent per mention, not the cluster shape). If a
  reviewer requires a cluster-F1 gain, that clause is unmet -- the FIRST thing I'd flag. The typed-VIEW (de-pollution) part
  does merge and recovers clustering to ~parity; the BEAT is resolution accuracy.
- **The typed view is a fair comparison:** string-identity's common clusters are already nominal (it keys pronouns
  separately), so the win over it is NOT the nominal view (that just recovers the incumbent's self-inflicted pollution to
  parity) -- it is the candidate-generation bridge reaching type-compatible different-head antecedents string-identity
  cannot. Measured: typed-view-only ties string-identity; the bridge is what beats it.
- **GUM only** (modern, TEST=odd docs). No OOD (GENTLE/reddit) arm.
- **The different-head residual is still 84.3% world-knowledge / abstract-anaphora** -- the win captures the glass-box-
  reachable ~16% of that slice; the rest routes to the sibling P31 entity-type-KB brief. The oracle ceiling (0.5825) is the
  bound; the win (0.5618) closes ~53% of the glass-box headroom above string-identity.

## 5. Performance vs the brain + the full-stack upstream
- A competent reader beats string-identity on this task by resolving the different-head (33.7%) and competitive same-type
  slices with WORLD KNOWLEDGE + the situation model. We now capture the IN-TEXT glass-box part of that (type-compatibility
  reach via WordNet/appos-copula/name, held under uncertainty) and close half the reachable headroom; the world-knowledge
  remainder is the sibling P31 KB (offline, invariant-safe), out of scope here.
- **Upstream (the owner's directive):** the mention detector = gold (competent-reader reference, not the bottleneck); the
  agreement features are handled (gender ~6%-sparse -> recall-safe vs hard barely matters, and the winning arm uses the
  incumbent binding for pronoun no-regress). The one live upstream lever is PRONOUN accuracy: the incumbent's pollution of
  the shared card is exactly why the naive resolver trailed; the typed view NEUTRALIZES that pollution for the common-noun
  consumer WITHOUT needing better pronoun resolution, and the sibling compose SOLVED's +0.082 pronoun stack would further
  reduce the full-card pollution (a complementary, already-filed win). No downstream consumer regresses; the named-antecedent
  consumer IMPROVES (+0.0241).

## 6. Proposed hdlab WIRE (Q111 -- strategy lands; solver does not write hdlab/)
Reference implementation: `experiments/exp_commonnoun_typed_identity_gum_v1.TypedResolver` (`binding='incumbent'`,
`bridge=True`, `bridge_write=False`). Two additive changes to the resolver behind the board's `common_noun_coref` dim
(`exp_unified_referent_gum_v1.Resolver` / the live URG path):
1. **TYPED CARD IDENTITY.** Give each referent a NOMINAL identity (name+common mentions) distinct from its full mention
   set. Score / read out common-noun (and name) coreference against the NOMINAL dominant; keep pronoun resolution reading
   the FULL card. Pronouns write to the full card only. This de-pollutes common-noun coref (+0.0439 over the incumbent,
   CI-sep) with pronoun byte-identical. Brain-faithful: an entity's identity is carried by its descriptions, not its
   transient pronoun pointers.
2. **NON-WRITING (Nref) DIFFERENT-HEAD BRIDGE.** When a definite common noun has no same-head antecedent, resolve it to the
   most-salient TYPE-compatible prior referent for THIS reference -- but do NOT merge it into the card (open its own
   referent for future same-head links). +0.0354 CI-sep over the typed base; the merge (writing) version regresses, so it
   must be NON-writing. Brain-faithful: Nieuwland Nref hold-under-uncertainty.
3. **SEED THE BRIDGE FROM THE LANDED TYPED-SPOKES ORGAN, not WordNet-MFS.** The type-compatibility candidate set uses
   `hdlab.typed_spokes.coref_type_license` (sense-resolved synonym + is-a both directions + part-whole; Lambon-Ralph typed
   spokes) plus apposition/copula text-stated is-a + name-containment; ranked by ACT-R salience. The organ beats the crude
   WordNet 2-hop-MFS comparator +0.0053 CI-sep -- REUSE the organ, do not reinvent a comparator. NOTE: this is the SAME
   organ the brief flagged as net-negative AS A WRITING FILTER on the live pick; here it is a NON-WRITING candidate-
   generation seed on the different-head slice only, which is why it is net-POSITIVE (the write, not the type cue, was the
   earlier cost -- confirmed: the writing version regresses).
Combined: 0.4879 -> 0.5671, BEATING string-identity 0.5412 (+0.0259 CI-sep), twin loses, no consumer regresses. Note the
scope: this is a resolution-accuracy wire (the board's dim + downstream binding), not a cluster-F1 change.

## 7. AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec 2b, E3 coreference / common-noun)
- **Common-noun coref now BEATS same-head string-identity on modern GUM (0.5618 vs 0.5412, CI-sep)** via two brain-faithful
  levers: a TYPED card identity (nominal vs full mention set -- de-pollutes the common read from weak pronoun bindings) and
  a NON-WRITING (Nref) type-compatibility bridge (candidate generation to different-head antecedents, held under
  uncertainty). The prior audit note (resolver trails string-identity) is superseded for the common-noun dim.
- **Located mechanism, folded in:** the incumbent trailed string-identity because weak pronoun resolution (~47%) polluted
  the shared DRT card, and because different-head bridging that MERGES pollutes other items -- both are write-side costs
  that the typed view + Nref-hold eliminate. The shared-card antagonism the 2026-09-06 entry noted (pronoun side) is
  resolved for the common-noun consumer by the typed view, not by un-unifying.
- CONFIRMS E3's brain-math correction: weighted parallel candidate generation (not hard filter-then-rank) is what reaches
  the different-head slice; the ranking within same-head has no glass-box headroom (twin ties there).

## 8. Adjacent components (evaluated for brain-fidelity + optimization -> next problems)
- **The shared DRT card (unification):** the typed identity view (nominal vs full) is a general fix for cross-consumer
  antagonism -- it likely helps other consumers that read the card (affect experiencer, goal binding) by giving them the
  clean nominal identity. Worth evaluating those consumers on the typed view (candidate follow-on).
- **PRONOUN resolution (~47%):** still the pollution source for the FULL-card read; the sibling compose SOLVED's +0.082
  stack is the complementary upstream fix. High value, already filed.
- **The entity-type KB / situation model (the 84% different-head residual):** the sibling P31 brief -- the route to close
  the rest of the headroom to the oracle 0.5825. Invariant-safe offline asset.
- **The board `common_noun_coref` instrument:** it scored a polluted view of the incumbent; the typed identity is the
  representational fix, not a board change.

## KEY REALIZATIONS (the enabling moves)
- **A failure understood at the mechanism level hands you the fix.** The owner's push -- "do we fully understand WHY those
  didn't pan out?" -- was the unlock. De-pollution regressed pronoun *because one field served two consumers* -> split the
  identity (typed view). The bridge netted zero *because the WRITE polluted other items, not because the resolution was
  wrong* -> hold the merge (Nref). Both fixes fell directly out of the diagnoses; neither was reachable by tuning.
- **Separate the resolution decision from the merge commitment.** The board (and downstream binding) needs each mention
  RESOLVED to the right entity; it does not need every resolution COMMITTED as a permanent merge. Nref hold-under-
  uncertainty gives the correct resolution without the pollution -- a genuinely brain-faithful decoupling.
- **The entity's identity is nominal, not pronominal.** Reading common-noun coref off the name+common identity (not the
  pronoun-polluted full card) is both more accurate AND more brain-faithful (pronouns are pointers, not descriptions).
- **Ask whether it could succeed first, and let the info-free twin tell you where the signal is.** The same-head ranking
  twin NOT losing said "ranking is not the lever here"; the different-head twin (random bridge) LOSING said "the type
  signal IS the lever there" -- which correctly pointed all the effort at candidate generation for the different-head slice.

## TLDR (plain English)
The reader was worse than a dumb same-word rule at re-recognising common nouns ("the doctor"), and the first obvious fixes
all failed. Instead of stopping, I worked out exactly WHY each failed -- and the reasons handed me the fix. Failure one: the
reader also tries to resolve pronouns ("he", "she") into the same character records and gets those only ~half right, which
contaminates the records; cleaning that up recovered the common-noun reading but broke pronoun tracking, because one record
served both jobs. Fix: give each character record a "name/noun identity" separate from its full mention history, and read
common nouns off the clean identity while pronouns keep using the full record -- common-noun accuracy jumps and pronoun
tracking is untouched. Failure two: linking a different-worded mention ("the company" -> "Google") to its antecedent didn't
help, because MERGING that link into the record corrupted it for later mentions. Fix: resolve "the company" to Google for
this sentence but DON'T permanently merge it (hold the link when unsure -- which is what people do). Together these two
brain-faithful changes make the reader BEAT the dumb same-word rule (about 56 vs 54 right in 100, a clean statistically-
separated margin), a scrambled version falls apart, and pronoun/name tracking is not hurt at all. The remaining hard cases
("the country" -> "Argentina") genuinely need world knowledge, which the separately-planned offline fact store supplies.

## QUESTIONS
None blocking. One scope note for the owner: the win is a per-mention RESOLUTION-accuracy gain (the board's dim and what
downstream binding needs), not a clustering-F1 gain -- by design the "hold the merge" step trades cluster shape for
resolution correctness. If you want a clustering-F1 win too, that needs the committed merge, which reintroduces the
pollution; I recommend keeping the resolution-accuracy win (it is what the board and downstream measure).

## NEXT STEPS (priority-ordered; strategy owns any hdlab landing, Q111)
1. **LAND the two levers** (§6): typed card identity (nominal vs full) + non-writing (Nref) type bridge, on the URG common
   path. 0.4879 -> 0.5618, beats string-identity CI-sep, twin loses, no consumer regress. Re-verify the 6 witnesses.
2. **Evaluate the OTHER card consumers on the typed identity view** (affect experiencer, goal/relational binding) -- the
   nominal-vs-full split likely helps them too (they currently read the polluted full card). Candidate follow-on.
3. **Complementary upstream:** land the sibling compose SOLVED's pronoun stack (+0.082) to further clean the full-card read.
4. **Close the rest of the headroom to the oracle (0.5825):** the sibling P31 entity-type-KB for the 84% world-knowledge
   different-head residual (offline, invariant-safe).
5. **DO NOT REDO (measured-capped):** same-head splitting (net-negative on both metrics); the WRITING different-head bridge
   (pollutes -> use non-writing); recall-safe vs hard agreement on common nouns (gender ~6%-sparse); the weighted-CS
   same-head ranking (twin ties -> no headroom). All on disk with their capping reason.
