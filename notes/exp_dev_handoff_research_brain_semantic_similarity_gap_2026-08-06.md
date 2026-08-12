# exp_dev hand-off -- research: brain semantic-representation gap (lexical-similarity organ)

Filed-by: research sub-agent
Date: 2026-08-06
Trigger: notes/audit_brain_semantic_representation_similarity_2026-08-06.md (deep brain-foundational
audit of hdlab/lexical_similarity.py + hdlab/verb_lexical_similarity.py against the ATL
hub-and-spoke controlled-semantic-cognition literature)
Urgency: MEDIUM -- not blocking any in-flight cell; this is a scope-expansion / next-lever
candidate that closes both a scaling limit (open-vocab coverage) and a brain-fidelity gap
(hand-supplied vs. learned features) in one mechanism.

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only. Experiment design details (cell
grids, hyperparameter values, script paths) are to be authored by exp_dev from the research note +
cap_map context. Do NOT treat the descriptions below as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: auto_induced_feature_substitution_probe_v1

Anchor pointer: Research note Section 4 (Cheap decisive test)
Substrate-product reading: Tests whether an UNSUPERVISED, non-human-named feature basis can
replace the hand-authored `CONCEPT_FEATURES` tags in `hdlab/lexical_similarity.py` and still
reproduce the same tier-separated similarity structure (synonym > related-not-synonym >
unrelated) on the SAME held-out triples the module's own `self_test()` already uses
(`vessel/ferry`, `vessel/dock`, `sister/rival`). CONCRETE PRECEDENT already identified by a
directly antecedent same-day note (`notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md`,
which designed the mechanism this anchor's target module shipped from): Murphy, Talukdar &
Mitchell (2012, COLING, "Learning Effective and Interpretable Semantic Models using Non-Negative
Sparse Embedding," NNSE) run non-negative sparse dictionary learning DIRECTLY on a PPMI
co-occurrence matrix (not on pretrained neural embeddings) and report it matches SVD on
behavioral-prediction tasks while jumping human-rated dimension-interpretability from 46% to
92%. The substrate already owns a PPMI co-occurrence matrix (`hdlab/ppmi_sparse_encoder.py`,
disk-verified closed for a DIFFERENT task -- retrieval-at-scale, not lexical-similarity quality,
so this is not reopening that closure) -- NNSE run on that existing matrix is the concrete,
previously-identified candidate for this anchor's induced feature basis, offered as the leading
candidate algorithm, not a mandate (exp_dev may pick a different induction method if a better one
surfaces). This is the single highest-leverage test in the note: it directly targets the audit's
dominant identified gap (feature SOURCE = hand-supplied vs. learned), and a HARD-PASS would
simultaneously (a) begin closing the open-vocabulary scaling ceiling that motivated this organ's
original promotion (praise/accept/invited OOV failures in hdlab/goal_typing.py) and (b) move the
organ closer to actual brain-fidelity (Rogers & McClelland 2004 error-driven emergent
representations vs. hand-named symbolic tags).
Tier hint: CPU laptop, likely ~1-3 hr (small held-out triple set, existing corpus already on
disk under data/corpora/). Cheap, no GPU needed, no new infra.
Why-now: The organ was just WIRE-DONT-ISLAND promoted this same date (commit context: both
lexical_similarity.py and verb_lexical_similarity.py docstrings already self-flag "General
open-vocabulary feature coverage... is a separate, missing-LEARNING follow-up, not claimed here"
-- this anchor is the direct, cheap, falsifiable follow-up to that self-flagged gap.

Pre-reg bands (from the research note's own pre-registered thresholds):
  HARD-PASS: induced-feature cosine reproduces the same rank ordering (synonym > related >
    unrelated) with delta >= 0.20 on >=80% of the held-out triple set, AND a scramble-control
    delta collapse >= 0.30 under label permutation (same convention as the module's existing
    self_test scramble check).
  MIDDLE-BAND: partial tier separation (delta 0.10-0.20, or scramble collapse present but weaker
    than 0.30) -- suggests the induction signal carries SOME feature-correlational structure but
    is not yet a clean substitute; worth a second iteration on the clustering/filtering step
    before either promoting or discarding.
  HARD-FAIL: delta < 0.10 (no tier separation above chance), OR the induced basis over-links a
    frequently-co-occurring-but-unrelated control pair (e.g. "sailor"/"ship" -- related, not
    synonymous, but co-occur constantly) -- this is the PREDICTED failure signature if the
    induction accidentally reproduces the ATL-null distributional/associative similarity metric
    (Carota, Bozic & Marslen-Wilson 2017) instead of the ATL-tracking feature-correlational one.
    A HARD-FAIL here is itself a valuable, falsifying result: it would redirect follow-up effort
    toward the grounded-multimodal-experience route (the already-open 2026-08-03 "6yo grounded
    foundation" project) rather than a cheaper corpus-co-occurrence shortcut.

### Anchor 2: context_control_reweighting_probe_v1 (secondary, lower priority)

Anchor pointer: Research note Section 4 (secondary test) + Section 3 POSITION/METRIC rows
Substrate-product reading: The audit found the organ has NO analog of the brain's semantic
CONTROL network (IFG/pMTG/AG/dmPFC) that reweights which features dominate similarity per task --
`SIMILARITY_LINK_THRESHOLD` is a single fixed global constant. This probe constructs a small set
of one-word-two-context pairs (e.g. "bank" in a river-context sentence vs. a finance-context
sentence) and tests whether a simple task-conditioned tag-reweighting scheme changes which of two
candidate similarity targets a word links to.
Tier hint: CPU laptop, ~1-2 hr, very cheap (small hand-constructed probe set, no new corpus
scan). Lower priority than Anchor 1 -- run only if Anchor 1 lands and queue capacity remains, or
as a scope-expansion filler.
Why-now: Currently a TOTAL architectural absence rather than a partial approximation, so even a
small probe is informative about whether this is worth building at all given current substrate
use cases (goal-owner attribution, outcome valence, verb-class membership) -- none of which
obviously require task-dependent reweighting yet.

Pre-reg bands:
  HARD-PASS: reweighting scheme measurably changes the winning similarity target on >=1 of the
    constructed context-pairs relative to the fixed-threshold baseline, confirming task-context
    materially matters for this substrate's use cases.
  HARD-FAIL: reweighting makes no measurable difference on any constructed pair -- suggests the
    fixed-threshold design is already adequate for the substrate's current task range; SHELVE
    the control-layer build with this negative result as the revival criterion (revisit only if
    a future use case demonstrably needs context-dependent similarity).

---

## Context pointers (file paths, not summaries)

- Research note (this audit): d:/AI/hd-instrument/notes/audit_brain_semantic_representation_similarity_2026-08-06.md
- Organ under audit (noun lexicon): d:/AI/hd-instrument/hdlab/lexical_similarity.py
- Organ under audit (verb lexicon, sibling module): d:/AI/hd-instrument/hdlab/verb_lexical_similarity.py
- Prior design drill this organ's verb extension was built from: d:/AI/hd-instrument/notes/drill_brain_openvocab_verb_class_membership_2026-08-06.md
- Directly antecedent design doc for the noun organ itself + the NNSE-on-PPMI precedent for Anchor 1: d:/AI/hd-instrument/notes/drill_brain_atl_lexical_semantic_hub_2026-08-06.md
- Existing PPMI matrix Anchor 1 would reuse (disk-verified closed for a DIFFERENT task, retrieval-at-scale, not reopened by this anchor): d:/AI/hd-instrument/hdlab/ppmi_sparse_encoder.py
- Original mechanism proof cell (noun organ's source): experiments/exp_n11c_shared_feature_lexical_similarity_v1.py (commit 7d0a574b4, HARD_PASS)
- Trigger for the verb-extension work (real-prose generalization negative): commit 72f2c16b1 / f496caa51 (exp_real_text_goal_owner_generalization_diagnostic_v1)

---

## Contract section

This handoff proposes 2 anchor candidates. Exp_dev selects based on current queue state, runner
availability, and pause flag. Exp_dev does NOT need to implement both.

SEQUENCING: no hard dependency between the two anchors; Anchor 1 is higher-leverage (targets the
audit's DOMINANT gap) and should be preferred if only one slot is available. Anchor 2 is a cheap
scope-expansion filler, not a blocker for anything.

---

## Autonomy declaration

Exp_dev is autonomous in:
- Choosing which anchor(s) to dispatch first
- Choosing the exact clustering/filtering method for the induced feature basis in Anchor 1 (the
  research note deliberately does not prescribe an algorithm, only the falsifiable outcome
  bands)
- Choosing the exact constructed probe-pair wording for Anchor 2
- Choosing local CPU vs remote CPU routing per standard convention
- Writing experiment scripts per the metrics-required-fields convention and the
  multi-unit-checkpoint/resume convention (CLAUDE.md)

Exp_dev is NOT autonomous in:
- Deciding to swap in a pretrained distributional/co-occurrence embedding model (word2vec, BERT,
  etc.) as a shortcut for Anchor 1's induced feature basis -- the research note gives a specific,
  cited, falsifiable reason this would likely reproduce the WRONG (ATL-null, associative) metric
  rather than the feature-correlational one the organ currently approximates; if exp_dev believes
  this constraint should be relaxed, escalate rather than route around it silently
- Making the WIRE-or-SHELVE promotion decision on either anchor's result (skunkworks/strategy owns
  this at landed-VET)
