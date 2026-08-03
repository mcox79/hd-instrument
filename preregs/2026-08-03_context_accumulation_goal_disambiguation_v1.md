# Pre-reg: context-accumulation vs isolated-snippet on near-synonym unstated-goal disambiguation (2026-08-03)

## Origin / fork being decided
`notes/` construction->integration result (commit a401d0d19, verdict logged at 2b6ebe507) found the
`unstated_goal` axis MISSES on ISOLATED snippets (MECHANISM_accuracy=0.25 < BASELINE_LEXICAL=0.333 on
the 12-item goal axis, MEASURED@data/exp_construction_integration_relation_inference_v1/metrics.json:
per_axis.unstated_goal) -- but that cell used isolated cross-novel snippets with NO accumulated chapter
context (its own Scope decision section states this explicitly, "gate-2 fail"). Two hypotheses:
- (A) CONTEXT-STRIPPING: accumulated chapter-context would disambiguate near-synonym goal categories
  (REVENGE_PUNISH vs SELF_DISCIPLINE vs CARE_FOR_OTHERS vs PROTECT_OTHERS) -> fix is a full-chapter
  harness; the deep-earn content-encoding build may NOT be needed.
- (B) CONTENT-ENCODING: even with context, near-synonym categories can't be told apart without EARNED
  content meaning -> the deep-earn is proven-necessary.
This cell decides with ONE variable = CONTEXT (isolated vs accumulated); goal-inference readout
(construction top-K + integration relaxation, `experiments/exp_construction_integration_relation_
inference_v1.py::score_goal_item`) held EXACTLY fixed and imported verbatim, not reimplemented.

## Prior-work check (substrate-KB concept-query, mandatory before authoring)
`bash tools/substrate_query.sh "accumulated situation-model context disambiguates unstated goal
near-synonym categories"` -> top hit cosine=0.3438 (entity="situated", generic lexical/WordNet
match, not a prior experiment cell). No prior arc cell at cosine>0.30 addresses this specific
context-vs-isolated fork. Genuinely novel controlled test, not a rediscovery.

## Item selection: the near-synonym-confused subset (identified by direct recompute, not assumed)
Recomputed `score_goal_item` over all 12 `unstated_goal` gold items
(MEASURED@ad-hoc python recompute against the existing cell's own functions, same digest-seeded
vectors, same FIXED_RANDOM_SEED). Items whose MECHANISM arm missed AND whose distractor/correct set is
drawn from the near-synonym cluster {REVENGE_PUNISH, SELF_DISCIPLINE, CARE_FOR_OTHERS, PROTECT_OTHERS}
named in the task:
- `relinf_unstated_007` (little_women ch8, Jo's spite) correct=REVENGE_PUNISH, distractors={CARE_FOR_OTHERS,
  SELF_DISCIPLINE, PROTECT_OTHERS} -- ALL THREE distractors are cluster members. MECH picked
  CARE_FOR_OTHERS (miss).
- `relinf_unstated_010` (little_women ch8, Laurie testing ice) correct=CARE_FOR_OTHERS, distractors
  include REVENGE_PUNISH, SELF_DISCIPLINE. MECH picked REVENGE_PUNISH (miss).
- `relinf_unstated_011` (wizard_of_oz ch6, Dorothy vs Lion) correct=PROTECT_OTHERS, distractors include
  REVENGE_PUNISH, SELF_DISCIPLINE. MECH picked SELF_DISCIPLINE (miss).
- `relinf_unstated_012` (alice ch1, boxing own ears) correct=SELF_DISCIPLINE, distractors include
  CARE_FOR_OTHERS, REVENGE_PUNISH. MECH picked CURIOSITY_EXPLORATION (miss) -- this is the exact item
  named in the task ("Alice boxing her own ears").
n=4 confused subset (within the pre-estimated ~4-8 range the task anticipated).

## Context source (GIVEN GOLD events, sidestepping extraction confound)
Per item, ONE variable changes: whether the construction-stage input vector is built from the isolated
`action_text` alone (ISOLATED) or from the isolated action_text bundled with a GENUINE, GOLD-CITED
surrounding-chapter event (ACCUMULATED). No extraction/parsing is performed -- context text is either
(a) an existing gold-verified sibling record in the SAME gold file describing a nearby event in the
SAME chapter/scene, or (b) the verbatim redacted clause quoted inside the target item's own
`why_inferred` field (still gold-verified metadata of the same record, not fabricated). Where NEITHER
exists, the item gets NO added context (ACCUMULATED == ISOLATED for that item) -- reported honestly,
not papered over with an invented sentence (would violate the public-domain/no-fabrication + MEASURED
discipline).
- `relinf_unstated_007`: context = `relinf_thwart_002.event_b` verbatim text ("Yes, I did! I told you
  I'd make you pay for being so cross yesterday, and I have, so...", ch8 line 3161-3162) -- Amy's own
  gold-cited declaration of the revenge motive active in this scene, chronologically BEFORE item 007's
  line 3278.
- `relinf_unstated_010`: context = `relinf_thwart_003.distractor_text` verbatim text ("Keep near the
  shore. It isn't safe in the middle.", ch8 line 3274) -- Laurie's gold-cited safety warning, four
  lines before item 010's own citation, same scene.
- `relinf_unstated_011`: context = the verbatim redacted clause quoted in item 011's own gold
  `why_inferred` field ("fearing Toto would be killed") -- part of the SAME original sentence as the
  action_text, deliberately excluded from the citation by construction-cell design; using it as
  accumulated (not isolated) context is exactly the CONTEXT-STRIPPING manipulation the task specifies.
- `relinf_unstated_012`: NO surrounding gold-context record exists in the corpus for this exact
  citation (checked `gold_relation_inference_v1_UNVERIFIED.jsonl` / `_hardened_UNVERIFIED.jsonl` for
  additional alice_in_wonderland ch1 items near line 207 -- none found). ACCUMULATED == ISOLATED for
  this item. Flagged explicitly: this item's disambiguating signal ("cheated HERSELF ... against
  HERSELF") is ALREADY inside the given action_text, so it is a poor test of the context hypothesis at
  all -- a construction/lexical-weighting question, not a context-availability question. Reported
  separately, not blended into the "context helped/didn't" headline number.

## Mechanism (goal-inference readout HELD FIXED, imported not reimplemented)
Import `score_goal_item`, `CATEGORY_PROTOTYPES`, `text_bundle`, `cos_sim`, `relax`, `margin_of`,
`K_GOAL`, `REFUSE_MARGIN`, `FIXED_RANDOM_SEED` directly from
`experiments/exp_construction_integration_relation_inference_v1.py` (sys.path insert, not copy-paste).
ONE variable changed: the action vector fed into the SAME top-K-narrow -> relax pipeline.
- ISOLATED arm: `action_vec = text_bundle(action_text)` (bit-identical call to the original cell).
- ACCUMULATED arm: `action_vec = hdlab.bundling.bundle(stack([text_bundle(action_text),
  text_bundle(context_text)]))` when context exists (item 012: falls back to the ISOLATED vector,
  bit-identical, since there is nothing to accumulate) -- reuses the VALIDATED accumulate-via-bundle
  organ primitive (atom 29609 / `hdlab/situation_model_accumulate.py`'s underlying bundle call) applied
  directly to two already-built content vectors, rather than re-deriving a new bundling formula.
- LEXICAL baseline: `argmax(cos_sim(action_vec, proto_vec))` with NO integration relaxation, computed
  on the SAME action_vec as each arm above (isolated-lexical and accumulated-lexical both reported) --
  carried for reference per task instruction, not a new discriminator claim.

## Bands (pre-registered, n=4 confused subset -- SMALL-N, directional not magnitude, stated up front)
Of the 4 confused items, 3 have genuine added context (007, 010, 011); item 012 has none (control /
non-applicable, reported separately). Bands apply to the n=3 context-available subset:
- **CONTEXT_HELPS**: ACCUMULATED flips >=2 of the 3 context-available items from miss to correct
  (accuracy 0/3 -> >=2/3) AND ACCUMULATED_accuracy > ISOLATED_accuracy by >= 0.33 absolute on that
  subset -> the shortfall was context-stripping; recommend the full-chapter harness, HOLD the deep-earn.
- **CONTENT_NEEDED**: ACCUMULATED flips <2 of the 3 (i.e. stays at 0/3 or only 1/3) -> accumulated
  chapter context (at least of this citation-adjacency kind) does NOT carry near-synonym
  disambiguation -> the goal axis needs EARNED content meaning; the deep-earn becomes evidence-forced.
- Full 12-item and full-4-item numbers reported for completeness but explicitly marked directional-only
  (n=3-4 is far too small for a magnitude claim; a single item flipping changes the reported accuracy by
  33 percentage points).
- Do NOT overclaim: report per-item MEASURED picks, not just aggregate accuracy.

## Arms-must-differ / atomicity / crash-diagnostic (reused template, unchanged from parent cell)
- `arms_differ_verified`: true (hash-compare ISOLATED vs ACCUMULATED per-item prediction vectors).
- `final_metrics_atomicity`: "tmp_replace".
- `except SystemExit/KeyboardInterrupt: raise` before `except Exception` (no bare/BaseException).
- `deterministic_seeding`: true (inherits `FIXED_RANDOM_SEED` + sha256 digest word-vectors from the
  imported module; no `hash()`/`list(set())`).
- `cell_chunked`: false (single-shot, <2s, n=4 items x 2 context-arms x lexical-reference, no seed axis).
- `start_marker_written` / `crash_diagnostic_present`: true.
- `heartbeat_present`: n/a (well under 60s).
- `crlb_n/a`: "no capacity/noise-floor claim; accuracy-vs-baseline on a fixed 4-item confused subset."
- `cardinality_ok`: n/a (no sweep axis; EXPECTED_N_UNITS = 4 items x 2 context-arms = 8, asserted).
- `real_code_path_and_signature_preflight`: n/a (no live substrate class constructed beyond
  `hdlab.bundling.bundle`, a plain pure function bound by direct call, no KGStore-style signature risk).
- `progress_logging`: n/a.

## Compute architecture
Sequential-CPU, in-process, <2s total wall time (4 items, D=256 complex vectors, no matmul sweep) --
justification (c), diagnostic measurement not a training fit.

## Numbers tag discipline
All numbers in the completion report tagged MEASURED@<path> (this cell's metrics.json) or
HYPOTHESIZED/THEORETICAL where they are pre-reg thresholds, not measurements.
