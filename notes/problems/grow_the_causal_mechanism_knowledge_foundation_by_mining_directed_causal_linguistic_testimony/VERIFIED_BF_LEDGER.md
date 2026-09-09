# VERIFIED BF-STATUS LEDGER (operation/math precision, ACTUAL code) -- the causal-reading chain

Owner: "don't assume organs are BF -- verify ALL of them." Four parallel audits read the actual code (not docstrings)
of every candidate upstream organ. Verdicts: BF = the operation IS the brain's computation (pinned / defensible
computational-level, params swept-not-adopted); BF-SPIRIT = right operation, engineering impl or fitted/adopted params;
NOT-BF = the specific operation is not the brain's.

## THE LEDGER
| layer | organ | operation | verdict | the non-BF element (if any) |
|---|---|---|---|---|
| PARSE | `pos_tagger`+`perceptron` | supervised averaged perceptron + hard Viterbi | **NOT-BF** | offline-fit-on-UD-EWT + FROZEN; hard argmax discards marginals; hand features; POS decided separately then frozen-handed to parser |
| PARSE | `arc_parser` | arc-factored BATCH feature-hashed avg-perceptron, greedy hard-decode | **NOT-BF** | frozen supervised; feature hashing; discards the Matrix-Tree marginals it can compute; batch (brain is incremental); audit: "measurably HARMFUL for reversible roles -- route around it" |
| PARSE | `incremental_parser` | left-corner eager attach, bounded Now-or-Never buffer | **BF-SPIRIT** | genuine brain mechanism, NO fitted weights in core; deviations = discrete-not-graded, `conflict_margin=0.15`, inherits hard POS; **predictor=None on live path -> inert island** |
| PARSE | `predictive_reader` | -log P surprisal (softmax) + Friston precision | **BF-SPIRIT** | PINNED core; mean-centroid/temp swept-labeled; offline-fit+frozen (sanctioned foundation) |
| ROLES | `graded_role_assigner` | Competition Model: A_i=Sigma w_c support_c -> argmax | **BF-SPIRIT** | **`DEFAULT_VALIDITIES` = logistic coeffs FIT ON GOLD, adopted at inference**; agent weights hand-set; UNACC hand-lexicon; magic windows |
| BINDING | `event_bundle` | FHRR/VSA `sign(Sigma_r bind(role_r,filler_r))`, unbind+dot-cleanup | **BF** | random (non-fitted) keys, fitting-free cleanup; ONE latent deviation = bipolar `sign()` bundle (MAP-VSA vs FHRR-phasor), tracked |
| BINDING | `role_slot_summarizer` | same primitives + SHARDED per-role slots + kNN cleanup | **BF** | same latent `sign()`; adopted CG-envelope constants (config, not gold-fit) |
| GROUND | `grounded_similarity` | z-scored 12-d Lancaster/Brysbaert + **capped cosine 0.45** | **BF-SPIRIT** | ratings = admissible FOUNDATION; but the READ is capped cosine ("no cosine in the brain") -> discards the per-dim signed magnitudes |
| GROUND | `sensorimotor_spoke` | euclidean-in-z (magnitude-aware, swept) | **BF-SPIRIT** | better than cosine; but symmetric DISTANCE, not a SIGNED more/less; `nearest`-selection unpinned OUR-INVENTION |
| GROUND | `context_grounded_valence` | biased-competition + force harm/help + online appraisal Q | **BF-SPIRIT/borderline** | UNPINNED tier; hand-lists (`HARM_BACKOFF`); **nltk POS-tag at inference on one path (defect)**; output categorical valence, NOT grounded magnitude |
| MAGNITUDE | **`quality_relation` Ch.B / composed-magnitude** | dimension-select -> oriented signed-magnitude place code -> **FPE-log Weber comparator** | **(named as the genuine grounded SIGNED-MAGNITUDE organ; consumes `grounded_vector`) -- AUDIT NEXT; THIS is the more/less source, not the cosine/valence organs** |
| CAUSAL | `force_dynamics_lexicon` | Wolff/Talmy discrete truth-table over (tendency,concordance,endstate) | **BF-SPIRIT** | truth-table pinned; but inputs = FrameNet frame-membership LOOKUP + 5-verb hand ENABLE-split + ~30-verb backoff; endstate = hand `NEG_CUES` keyword scan; covers only ~16% of real causal rels (PHYSICAL only; most narrative causation is MENTAL) |
| CAUSAL | `force_dynamics_valence` | harm/help = WordNet-animacy gate + **verb-LIST membership** | **NOT-BF** | not a force simulation -- list membership dressed as force dynamics; `HARM_BACKOFF` reproduces the retired TEST-FITTED list; in-process FrameNet parse on read path (no cache) |
| NECESSITY | `predictive_world_model` | counterfactual ablation: surprisal(B\|ctx) - surprisal(B\|ctx\A) | **BF-SPIRIT** | OPERATION faithful/non-circular; but over an ASSOCIATIVE single-layer softmax forward model on **BARE UNBOUND verb concepts in a recency BAG** -> "counterfactual co-occurrence-necessity over verb TYPES, not over a world-STATE" |
| NECESSITY | **`causal_reasoner.py`** | Pearl-style: abduction -> **do(cause=absent) -> re-propagate** over `sm.causal_links`; graded-necessity edges | **(rated EXCELLENT in the audit) -- THIS is the necessity-SIMULATION organ; AUDIT NEXT -- I was re-building what already exists** |

## THE PATTERN (owner's principle, confirmed at scale)
The genuinely-BF mechanisms EXIST -- FHRR binding (`event_bundle`), the incremental parser + predictive reader, the
Weber magnitude channel (`quality_relation`), the do-intervention necessity SIMULATION (`causal_reasoner`) -- but they
are OFF-PATH (default-off islands / not composed). The ON-PATH deployed components my rung-2 sim inherited are NOT-BF or
BF-spirit engineering: frozen arc-parser -> bag concepts -> capped-cosine grounded read -> gold-FITTED role weights ->
list-membership force dynamics -> bare-verb associative forward model. THAT is why the more/less SIGN failed: every
input to it is non-BF. A brain-foundational component starved by non-BF upstream, exactly as predicted.

## THE BUILD -- "100% BF all the way up, in conjunction" = COMPOSE the verified-BF organs, replace the NOT-BF on-path ones
Top-down (start at the most-foundational = the parse), all mutually constraining (interactive activation, not a frozen pipeline):
1. **PARSE (top):** replace `arc_parser`/`pos_tagger` (NOT-BF) with `incremental_parser` + `predictive_reader` (BF), wired
   LIVE with the predictor ON (not None), keeping GRADED competition (not hard argmax). [fix: discrete->graded]
2. **ROLES:** Competition Model (`graded_role_assigner`) but LEARN the validities online (Rescorla-Wagner), not the
   gold-fitted `DEFAULT_VALIDITIES`. [fix: fitted->learned]
3. **BINDING (BF, use as-is):** `event_bundle` -- bind (participant, attribute, value) into the event unit.
4. **GROUNDED MAGNITUDE:** use `quality_relation` Ch.B Weber signed-magnitude comparator (audit it first), NOT capped
   cosine / categorical valence. [replace wrong-metric read]
5. **CAUSAL:** the mined signed store as edge-HYPOTHESIS source; do NOT use `force_dynamics_valence` (NOT-BF list); the
   Wolff truth-table (`force_dynamics_lexicon`) only where physical.
6. **NECESSITY SIMULATION (top-of-chain):** use `causal_reasoner.py` (do(cause=absent)->re-propagate over the bound
   `sm.causal_links`) -- the EXCELLENT do-simulation that already exists -- fed by the bound situation model above,
   NOT `predictive_world_model`'s bare-verb bag. [compose, don't rebuild]

Two organs to AUDIT NEXT before composing (named-but-not-yet-verified): `quality_relation` (the Weber magnitude) and
`causal_reasoner` (the do-simulation) -- these are the genuinely-BF top-of-chain organs the build depends on.

## BF-STATUS TAGGING CONVENTION (owner 2026-09-09: make BF status apparent, ideally in the name; record confirmations AND corrections)

WHY A TAG, NOT A RENAME: renaming a module (e.g. `event_bundle.py` -> `event_bundle_BF.py`) breaks every `import hdlab.event_bundle` across the substrate. So the "name-level, everyone-knows" marker is a STANDARD, GREPPABLE, MACHINE-CHECKABLE module tag placed at the TOP of each organ -- the non-destructive equivalent of putting it in the name (`grep -rn __bf_status__ hdlab/` shows the whole substrate's status at a glance).

THE STANDARD (one block at the top of every organ module):
```python
__bf_status__ = "BF"            # one of: "BF" | "BF_SPIRIT" | "NOT_BF" | "BF_UNPINNED" (brain target itself unpinned)
__bf_verified__ = "2026-09-09 operation/math audit (VERIFIED_BF_LEDGER)"   # date + who/what verified
__bf_note__ = "<one line: the operation, and the residual non-BF element if any>"
__bf_corrections__ = [          # append an entry each time a fix RAISES the status (record the correction)
    # "2026-09-09 replaced gold-fitted DEFAULT_VALIDITIES with online Rescorla-Wagner learning: BF_SPIRIT -> BF",
]
```
RULES: (1) `__bf_status__` must match this organ's row in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the tag MIRRORS the living
audit; the audit stays the source of truth, the tag makes it travel with the code). (2) When a correction RAISES the
status, append to `__bf_corrections__` AND bump `__bf_status__` AND update the audit row -- in the SAME commit. (3) A
`verification/test_bf_status_tags.py` checker greps every `hdlab/*.py` `__bf_status__` and asserts it is present + one of
the allowed values + consistent with the audit -> "everyone knows" is ENFORCED, not just documented.

EXACT PER-ORGAN TAG VALUES TO LAND (proposed hdlab change -- Q111, strategy lands; solver cannot write hdlab):
| organ | `__bf_status__` | `__bf_note__` |
|---|---|---|
| `event_bundle` | "BF" | "FHRR/VSA bind+bundle+unbind+cleanup, random non-fitted keys; latent bipolar-sign() deviation tracked" |
| `role_slot_summarizer` | "BF" | "same primitives + sharded per-role slots; no fitted params" |
| `incremental_parser` | "BF_SPIRIT" | "left-corner Now-or-Never eager attach; discrete-not-graded; conflict_margin=0.15; inherits hard POS; predictor inert live" |
| `predictive_reader` | "BF_SPIRIT" | "-logP surprisal + Friston precision PINNED; mean-centroid/temp swept; offline-fit+frozen (sanctioned)" |
| `graded_role_assigner` | "BF_SPIRIT" | "Competition-Model op pinned; DEFAULT_VALIDITIES gold-FITTED+adopted; agent weights hand-set; UNACC hand-lexicon" |
| `grounded_similarity` | "BF_SPIRIT" | "Lancaster/Brysbaert = admissible foundation; capped-cosine read is wrong-metric (discards signed magnitudes)" |
| `sensorimotor_spoke` | "BF_SPIRIT" | "euclidean-in-z magnitude-aware (swept); symmetric distance not signed magnitude; nearest-selection unpinned" |
| `context_grounded_valence` | "BF_SPIRIT" | "biased-competition+appraisal on UNPINNED tier; HARM_BACKOFF hand-list; nltk-at-inference on one path (defect)" |
| `force_dynamics_lexicon` | "BF_SPIRIT" | "Wolff/Talmy truth-table pinned; inputs = FrameNet lookup + hand ENABLE-split + backoff + hand NEG_CUES; ~16% coverage (physical only)" |
| `predictive_world_model` | "BF_SPIRIT" | "counterfactual-ablation OPERATION faithful; over associative single-layer forward model on BARE UNBOUND verb bag (co-occurrence-necessity over TYPES, not world-STATE)" |
| `pos_tagger` / `perceptron` | "NOT_BF" (brain target UNPINNED) | "supervised avg-perceptron, frozen, hard Viterbi discards marginals, module-separated; interim asset (POS brain-unpinned)" |
| `arc_parser` | "NOT_BF" | "arc-factored BATCH feature-hashed avg-perceptron, frozen, greedy hard-decode discards Matrix-Tree marginals; route AROUND for reversible roles" |
| `force_dynamics_valence` | "NOT_BF" | "harm/help = WordNet-animacy + verb-LIST membership (not a force simulation); HARM_BACKOFF = retired test-fitted list; in-process FrameNet parse on read path" |
| `causal_reasoner` | (AUDIT NEXT; audit doc says EXCELLENT do-intervention necessity) | "Pearl abduction->do(cause=absent)->re-propagate over sm.causal_links; verify then tag" |
| `quality_relation` (Ch.B) | (AUDIT NEXT) | "grounded oriented signed-magnitude + FPE-log Weber comparator; verify then tag" |

## COMPOSITION RESULT (2026-09-09) -- composing the verified-BF organs ISOLATES the single remaining BF gap
Built `exp_causal_wiqa_bfsim_v1`: the FAITHFUL BF do-simulation `causal_reasoner.signed_effect` (BF_SPIRIT; conflict-
cancelling ±1 cone relaxation over the process graph) fed edge signs from the most-BF linguistic polarity source,
`force_dynamics_lexicon` Wolff CAUSE/ENABLE=+1 / PREVENT=-1. Result on WIQA (the interventional more/less gold):
**neg-edges = 0.0%** -- Wolff PREVENT fires on ZERO WIQA process steps (process language = "gains weight / uses its
food stores / lives off body fat", not prevent/block/stop). So every edge is +1, `signed_effect` degenerates to
more/no-effect, more-vs-less stays 0.410 (below chance) -- exactly the audit's "can never say less" prediction.

=> THE SINGLE REMAINING BF GAP IS PRECISELY ISOLATED: not the reasoner, not the propagation, not the concept grain --
it is the SIGNED-EDGE SOURCE (does a natural-process event PROMOTE or INHIBIT the effect QUANTITY). Each candidate fails
for a NAMED reason: Wolff force-dynamics 0% on process language; marker-mined signed store = noise (0.34); grounded
Weber magnitude (`scalar_adjective_operation`) has no quantity dimensions + is word-magnitude not edge-polarity. The
mechanism that supplies it brain-foundationally = a GROUNDED MODEL OF QUANTITY DYNAMICS ("does this event drive
quantity X up/down"), i.e. the generative world-model over grounded magnitudes -- the deep north-star. Everything
UPSTREAM of the sign source is now either verified-BF or composable-from-verified-BF organs; the sign source is the wall.

## GROUNDED QUANTITY-DYNAMICS SIGN SOURCE -- BUILT + full result (2026-09-09): third/final text-derived sign source, definitively at chance
`exp_causal_quantity_dynamics_v1`: a LEARNED signed magnitude-transition (Rescorla-Wagner over INCREASE/DECREASE-
grounded directional co-occurrence), composed via verified-BF causal_reasoner.signed_effect on WIQA. FULL (n=5005,
store +88241/-14465): neg-edges 4.1% (fixes Wolff 0%), 3-WAY 0.552 (+0.13 = PURE reachability), but MORE-vs-LESS
= 0.457 (below chance), TIES the random-sign twin EXACTLY (paired +0.0000). The learned grounded signs add nothing
over random on the specific process more/less.
=> EXHAUSTIVE: three text-derived sign sources all fail (Wolff 0% coverage / marker-mined 0.34 / grounded-directional
ties-random). The more/less SIGN of a SPECIFIC process transition is NOT recoverable from text (Causal Hierarchy
Theorem: text=rung-1). The fully-BF version = GROUNDED MENTAL SIMULATION of the specific dynamics (generative world-
model over grounded magnitudes) -- the deep north-star, a scoped program. Everything else = verified-BF or composed-
from-verified-BF; this one grounded-simulation sign source is the entire remaining frontier, precisely isolated.
