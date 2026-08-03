# Pre-reg: situated goal structure (agent-target-action-valence) vs bundle+category (2026-08-03)

## Origin / reframe being tested
Commit 15dd0da51 (context-accumulation cell) found CONTENT_NEEDED: accumulated gold chapter-context did
NOT disambiguate the near-synonym `unstated_goal` confused subset (n_flipped=0-1 of 3 context-available
items, MEASURED@data/exp_context_accumulation_goal_disambiguation_v1/metrics.json). The cell's own
diagnosis (commit 2cdf3a464 WHERE-note) was that additive BUNDLING (discrete-category pick over an
additive word-bundle) destroys situated structure: it never resolves WHICH agent an action targets
(self-vs-other) or the causal/affective valence of the act. REFRAME under test: represent the inferred
goal as agent -> TARGET(self/other) -> action -> AFFECTIVE VALENCE(harm/help), built via BIND (not
additive bundle), and test whether this decomposition recovers the 4 items the bundle+category mechanism
missed by construction (MEASURED@data/exp_construction_integration_relation_inference_v1/metrics.json:
per_axis.unstated_goal, MECHANISM_accuracy on the 12-item axis = 0.25 < BASELINE_LEXICAL = 0.333).

## Prior-work check (substrate-KB concept-query, mandatory before authoring)
`bash tools/substrate_query.sh "situated goal structure agent target self other affective valence harm
intent revenge care protect binding not bundling"` -> top hit cosine=0.2881 (`notes/research_drillA_
neuro_capacity_structure_2026-07-13.md`, generic "richer internal structure" cap-map discussion, not this
mechanism). All 5 returned hits are BELOW the cosine>0.30 rediscovery threshold. Genuinely novel cell for
this specific representation decomposition, not a rediscovery.

## Item selection (unchanged from the sibling context-accumulation cell, same 4 confused items)
`relinf_unstated_007` (little_women, Jo's spite, correct=REVENGE_PUNISH), `relinf_unstated_010` (little_
women, Laurie testing ice, correct=CARE_FOR_OTHERS), `relinf_unstated_011` (wizard_of_oz, Dorothy vs
Lion, correct=PROTECT_OTHERS), `relinf_unstated_012` (alice, boxing own ears, correct=SELF_DISCIPLINE).
All 4 confirmed MISSED by the parent cell's MECHANISM arm (bundle+category, top-K + integration relax).
Also measured over the full 12-item `unstated_goal` axis for completeness (directional only, n=12 still
small).

## Representation under test (ONE variable = representation)

**Category structural schema (hand-declared, tier-2 primitive per goal-category -- declared, not
earned; this pass tests the FRAME, not earned valence):**
```
CATEGORY_TARGET_VALENCE = {
  MANIPULATE_AVOID_WORK:   (SELF,  NA),   SELF_PRESERVATION_ESCAPE: (SELF, NA),
  CURIOSITY_EXPLORATION:   (SELF,  NA),   COMPLY_AVOID_TROUBLE:     (SELF, NA),
  ESCAPE_BLAME_DECEPTION:  (SELF,  NA),   SELF_DISCIPLINE:          (SELF, NA),
  CARE_FOR_OTHERS:         (OTHER, HELP), PROTECT_OTHERS:           (OTHER, HELP),
  REVENGE_PUNISH:          (OTHER, HARM),
}
```
This maps the confused-4's near-synonym cluster cleanly: REVENGE_PUNISH is the ONLY (OTHER,HARM)
category; CARE_FOR_OTHERS/PROTECT_OTHERS share (OTHER,HELP) (structurally indistinguishable from each
other by this schema -- expected honest residual, noted below); SELF_DISCIPLINE is the only SELF-target
category among 007/010/011's distractor sets, so TARGET alone should already separate it from the other
three (OTHER-target) confused items.

**TARGET resolution (structural proxy; declared SCOPE-LIMITED, not the full `hdlab/coreference_
resolver.py` pipeline):** `hdlab/coreference_resolver.py`'s `TrackedEntity`/mention-stream machinery
operates over a multi-mention PASSAGE, which these single-clause `action_text` gold items do not supply
(no passage/mention-stream context exists in the eval schema). Rather than fabricate a fake passage
structure to force-fit the full resolver (would be a scope-mismatch per SCHEMA-VET Gate C), TARGET is
resolved by a declared, generalizable rule that captures the SAME underlying signal the resolver would
compute (same-entity coreference between clause-subject and clause-object): reflexive-marker detection.
```
resolve_target(text):
  reflexive = any of {herself, himself, itself, themselves, oneself, her own, his own, their own, myself}
  if reflexive present:
      OTHER if a causative-other pattern "let <X> ... <reflexive>" is present (agent causes ANOTHER
      party to act on themselves -- the reflexive binds to the CAUSED party, not the unstated agent)
      else SELF (agent acts on their own referent)
  else: OTHER (default -- most items in this axis are other-directed goals; declared BEFORE full-12
      measurement, see calibration_check below)
```
This is HONESTLY declared as a WEAK, biased-toward-OTHER default (not a real parse), and its accuracy is
measured on BOTH the confused-4 subset AND the full-12 (expect confused-4 >> full-12; reported, not
hidden -- this is the exact "don't overclaim on the curated subset" caveat this pre-reg pre-commits to).

**VALENCE resolution (tier-2 hand-bootstrapped lexicon, declared per task's explicit sanction for this
first pass):** generic affect-word counts on `action_text` (NOT the category-prototype word lists, to
avoid circularity with the LEXICAL baseline):
```
HARM_WORDS = {punish, hurt, harm, angry, spite, spiteful, bitter, cross, revenge, vindictive, slap,
              slapped, scold, scolding, blame, trick, deceive, cheat, cheated, pay, wrong, fault, hard}
HELP_WORDS = {care, careful, carefully, protect, protective, safe, safety, rescue, comfort, gentle,
              warm, guard, help, helped, kind, soothe, nurse, shield, defend, softly}
valence = HARM if harm_count>help_count else HELP if help_count>harm_count else NA
```

**HD structural encoding (bind, not bundle; reuses `hdlab/binding.py::bind/unbind` + `hdlab/bundling.py::
bundle` directly, D=256 complex64, digest-seeded per `ci._digest_seed`, own namespace
`ROLE::*`/`FILLER::*` disjoint from the word vocabulary):**
```
situated_vec = bundle(stack([bind(ROLE_TARGET, filler(target)), bind(ROLE_VALENCE, filler(valence))]))
decode: unbind(situated_vec, ROLE_TARGET) -> argmax-cosine cleanup against {FILLER_SELF, FILLER_OTHER}
        unbind(situated_vec, ROLE_VALENCE) -> argmax-cosine cleanup against {FILLER_HARM,FILLER_HELP,FILLER_NA}
```
Self-test asserts 100% round-trip decode fidelity at this 2-slot capacity (real HD bind/bundle/unbind
exercised, not python booleans standing in for it).

## Arms (ONE variable = representation)
1. **BUNDLE_CATEGORY** -- reproduces the parent cell's mechanism VERBATIM (`ci.score_goal_item`,
   construction top-K + integration relax over the additive word-bundle). Expected: 0/4 on confused
   subset (reproduces the known miss; this arm is the CONTROL proving the miss is real and reproducible,
   not a fluke of the sibling cell).
2. **TARGET_ONLY** -- filter candidates to `resolve_target(action_text) == category_target[c]`, then
   argmax `action_cosine` (same `ci.text_bundle`/`ci.bundle`/`ci.cos_sim` construction stream as BUNDLE_
   CATEGORY, restricted to target-matching survivors) -- isolates the TARGET component alone.
3. **SITUATED_STRUCTURE** (full mechanism) -- same TARGET filter, then among survivors:
   `score(c) = action_cosine(c) + VALENCE_WEIGHT * valence_bonus(c)`, `VALENCE_WEIGHT = 0.5` (declared
   fixed constant, chosen for rough magnitude-parity with typical bag-of-word FHRR bundle cosines in this
   D=256 regime -- NOT tuned post-hoc against the verdict). `valence_bonus(c) = +1` if `category_valence
   [c] == decoded_valence`, `-1` if both defined and mismatched, `0` if either is NA. Argmax picks.
4. **LEXICAL** (reference baseline, carried per task instruction) -- raw `action_cosine` argmax over ALL
   candidates, no target filter, no integration (`ci.score_goal_item`'s own `lex_pick`).

## Bands (pre-registered, n=4 confused subset -- directional not magnitude, stated up front)
- **STRUCTURE_HELPS**: SITUATED_STRUCTURE accuracy on the 4 confused items >= 3/4 AND strictly beats
  LEXICAL accuracy on the same 4 -> bundling (not lack of content) was the failure mode; the residual
  content need is precisely affective valence (not generic content-encoding) -> reframes the deep-earn
  arc toward a situated-structure + earned-valence build, not generic text-comprehension.
- **STRUCTURE_INSUFFICIENT**: SITUATED_STRUCTURE accuracy on the 4 confused items < 3/4 -> report which
  items resist and WHY (component attribution below) -- honest, no rescue.
- **Component ablation (mandatory, regardless of verdict)**: per-item, report TARGET_ONLY correct/incorrect
  and SITUATED_STRUCTURE correct/incorrect, to attribute which component (target-filter alone vs
  +valence) flips which item. Specific pre-registered predictions to check against measurement (stated
  as HYPOTHESIZED, to be confirmed/refuted by the run, not assumed true):
  - item 012 (self-directed): HYPOTHESIZED that TARGET_ONLY alone fixes it (target-filter removes 2 of 3
    distractors, leaving a 2-way tiebreak on action_cosine).
  - items 007/010/011 (all OTHER-target): HYPOTHESIZED that TARGET_ONLY alone does NOT fully separate
    them (all three share OTHER-target with at least one same-target distractor), and valence is needed
    to further disambiguate REVENGE_PUNISH(HARM) from CARE_FOR_OTHERS/PROTECT_OTHERS(HELP) -- but the
    hand-bootstrapped LEXICAL valence signal is EXPECTED to be unreliable on at least one of these
    (007's "let her take care of herself" is surface-HELP-worded irony expressing HARM-intent; 011's
    "slapped the Lion" is surface-HARM-worded action serving a HELP-intent toward a third-party
    beneficiary who is NOT the action's grammatical patient) -- if the run confirms these misses, that
    is direct evidence the residual content-need is genuinely semantic (irony / beneficiary-vs-patient
    distinction), not just "add more affect words to the lexicon."
- Full 12-item numbers reported for completeness, explicitly directional-only (same small-n caveat as
  the sibling context-accumulation cell).
- Do NOT overclaim: report per-item MEASURED picks + the TARGET/VALENCE resolver's own accuracy against
  each correct category's ground-truth (target, valence) label (diagnostic only, not fed into scoring)
  on BOTH the confused-4 and full-12, so a lucky confused-4 result cannot be read as a general resolver
  win if full-12 disagrees.

## Arms-must-differ / atomicity / crash-diagnostic
- `arms_differ_verified`: true (hash-compare BUNDLE_CATEGORY / TARGET_ONLY / SITUATED_STRUCTURE /
  LEXICAL per-item (pick, resolved-target, resolved-valence) tuples across the full 12-item run, where
  divergence is expected by construction across >=3 of the 4 arms).
- `final_metrics_atomicity`: "tmp_replace".
- `except SystemExit/KeyboardInterrupt: raise` before `except Exception` (no bare/BaseException).
- `deterministic_seeding`: true (inherits `FIXED_RANDOM_SEED` + sha256 digest word-vectors from the
  imported parent module for all text/category encodings; own `ROLE::*`/`FILLER::*` vectors also
  sha256-digest-seeded; no `hash()`/`list(set())`).
- `cell_chunked`: false (single-shot, well under 2s wall time, n=12 items, no seed axis).
- `start_marker_written` / `crash_diagnostic_present`: true.
- `heartbeat_present`: n/a (well under 60s).
- `crlb_n/a`: "no capacity/noise-floor claim; accuracy-vs-baseline on a fixed 4-item/12-item subset; the
  one quantitative capacity claim (2-slot bind/unbind round-trip decode fidelity) is self-tested directly
  (100% expected at D=256 with 2 roles x 2-3 fillers each, far below any FHRR capacity ceiling)."
- `cardinality_ok`: n/a (no sweep axis; EXPECTED_N_UNITS = 12 items x 4 arms = 48, asserted).
- `real_code_path_and_signature_preflight`: n/a (no live substrate class constructed beyond
  `hdlab.binding.bind/unbind` and `hdlab.bundling.bundle`, plain pure functions bound by direct call, no
  KGStore-style signature risk).
- `progress_logging`: n/a.

## Compute architecture
Sequential-CPU, in-process, well under 2s total wall time (12 items, D=256 complex vectors, 4 arms, no
matmul sweep) -- justification (c), diagnostic measurement not a training fit.

## Numbers tag discipline
All numbers in the completion report tagged MEASURED@<path> (this cell's metrics.json) or
HYPOTHESIZED/THEORETICAL where they are pre-reg predictions, not measurements.
