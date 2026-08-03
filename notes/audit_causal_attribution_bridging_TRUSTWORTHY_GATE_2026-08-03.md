# TRUSTWORTHY-GATE — causal-attribution bridging (commit d3b035e59, exp_causal_attribution_bridging_v1)

Auditor: Skunkworks (cert-owner). Audit-only, no cells authored/dispatched. Target cell:
`experiments/exp_causal_attribution_bridging_v1.py` @ d3b035e59,
`data/exp_causal_attribution_bridging_v1/metrics.json`,
`preregs/2026-08-03_causal_attribution_bridging_v1.md`.

## Method
Independent `.venv` recompute (not read from `metrics.json`'s own summary): reran
`build_chapter_streams` + `bridge_causal_antecedent` + `score_item` for all 12 gold
`unstated_goal` items directly against `hdlab/coreference_resolver.py` and
`hdlab/situation_model_accumulate.py`; instrumented the entity-linking gate to print
gate-passing candidate counts per item; recomputed the 20-seed shuffle control by hand;
`git show d3b035e59 --stat` to check whether `hdlab/coreference_resolver.py` was touched.

## 1. Numbers REAL?
CONFIRMED — recomputed independently, exact match to `metrics.json`:
`confused_4`: BRIDGING=ORACLE=0.750, RECENCY=AUTO_OLD=0.500, TEXT_ONLY=0.250.
`full_12`: BRIDGING=ORACLE=0.417 (5/12), RECENCY=AUTO_OLD=0.333 (4/12), TEXT_ONLY=0.333 (4/12).
Per-item bridge==oracle `prior_block` match holds on all 12 items, independently reproduced.

## 2. Circuit-reuse genuine?
CONFIRMED. `git show d3b035e59 --stat` touches ONLY the new experiment file —
`hdlab/coreference_resolver.py` and `hdlab/situation_model_accumulate.py` are untouched by
this commit. Direct read of `hdlab/coreference_resolver.py:176-236` confirms `TrackedEntity`,
`_pick_strict_cb`, `SUBJECT_LIKE_ROLES` are imported and called with their real signatures, no
shadowing/reimplementation. `_pick_strict_cb` is the literal function coref calls for pronoun
antecedents elsewhere in the same file (lines 404/448/616/728). The "same hippocampal circuit"
claim is honest at the code level — this is genuine reuse, not a copy-paste-and-drift.

## 3. What actually carries the win (the load-bearing adversarial question)
MEASURED, not assumed: instrumented the gate directly. Across **all 12 items**, the
entity-linking+valence filter (`blind_valence==HARM and coreference(patient, query_agent)`)
admits **at most 1 distinct candidate agent**, ever:
```
item 007: gate-passing agents = ['Amy']   (1 candidate)
item 010: gate-passing agents = []        (0 candidates)
item 012: gate-passing agents = []        (0 candidates)
all other 9 items: gate-passing agents = []  (0 candidates)
```
So `_pick_strict_cb` / `_pronoun_strict_cb_margin` — the retargeted Centering-style
"coherence-ranked backward search AMONG competitors," the piece of the mechanism that is
supposed to be the distinctive circuit-reuse contribution — is called on a **singleton list**
in the one case it fires at all, and on nothing in every other case. `max(compat, key=...)`
over a 1-element list is a no-op identity return. **The entire measured win is carried by the
upstream entity-linking FILTER (valence-gate + name-coreference match), not by the
coherence-ranking/argmax logic the pre-reg frames as the core circuit-reuse claim.** The
competitive-selection half of strict-Cb has ZERO test coverage in this cert.

## 4. Construction-determination
Verified by direct code read: `bridge_causal_antecedent` touches only `EVENT_ENTITIES` (GIVEN
agent/patient table) and `resolve_valence_blind` — never `CATEGORY_STRUCTURE`,
`ORACLE_PRIOR_BLOCK`, `correct_category`, or `distractor_categories`. The `reads_category_label:
False` / `reads_prior_block_flag: False` fields in `used` are real, not decorative. So this is
NOT gold-label leakage in the crude sense.
It IS, however, a maximally easy regime for the filter it's meant to test: with only 12 items /
4 chapters and at most 1 gate-passing candidate ever surfacing, BRIDGING and ORACLE are
mathematically forced to agree everywhere the filter is well-posed (0-candidate items on both
sides trivially agree "no prior block"; the 1-candidate item trivially agrees on that 1
candidate). The dataset never poses the question the mechanism's ranking machinery exists to
answer (choose among >=2 simultaneously-qualifying causal antecedents). BRIDGING==ORACLE on
12/12 items is closer to tautological-given-this-event-table than to evidence the retargeted
strict-Cb ranking generalizes to real multi-candidate disambiguation.

## 5. Fairness controls
- No gold-flag leakage: CONFIRMED by code read (section 4).
- Shuffle-degrade control: recomputed independently, byte-for-byte match — 14/20 = 0.70
  survival on item 007 (< 1.0, passes gate). Traced the actual mechanism: with 3 events in the
  chapter (positions 3149/3258/3278) shuffled as (agent,patient,valence) triples across fixed
  positions, the control degrades specifically when the true HARM triple (Amy/Jo/HARM) is
  shuffled onto item 007's OWN query position (~1/3 chance) and is then correctly excluded by
  the backward-only (`position < query_position`) constraint. This is a real, understood,
  non-noise degradation mechanism — genuine, but combinatorially coarse (only 3 elements being
  permuted; not a rich stress test).
- Future-distractor control: confirmed real via code read — the decoy event is placed at
  `query_position + 1` and the `ev["position"] >= query_position: continue` backward guard
  (inherited unmodified from `_pick_strict_cb`'s own `< cur_clause` semantics) is what excludes
  it, not a bespoke special-case.

## 6. Item 007
CONFIRMED: bridging derives `prior_block=True`, `attributed_agent=Amy`, matching oracle exactly
(both derive the SAME candidate via the SAME 1-candidate gate). `GROUNDED_BRIDGING_pick` (and
`GROUNDED_ORACLE_pick`) = `CARE_FOR_OTHERS` != gold `REVENGE_PUNISH`, but traced independently
into `exp_grounded_structure_phase0_probe_v1.classify_grounded`/`brain_fidelity_class`: the miss
is caused by `resolve_valence_blind` classifying item 007's own action text as HELP (fooled by
Jo's spiteful "let her take care of herself" reading as literal care), a PRE-EXISTING Phase-0
valence-classification limitation (tagged `BRAIN_LIKE_MISS_IRONY_FOOLED`), identical for both
BRIDGING and ORACLE arms. This is a separate, already-disclosed issue, not a bridging failure —
confirmed, not merely asserted.

## VERDICT: SURVIVES the trustworthy gate, but only under a MUCH NARROWER honest framing than "BRIDGING_WORKS" suggests

REAL: yes (numbers reproduce off independent recompute). FAIR: yes (no gold-label leakage;
controls are genuine, not vacuous, though combinatorially thin). Brain-faithful at the CODE
level: yes (literal unmodified circuit reuse, verified via git diff + direct read).

HONEST BOUND — what this cert actually demonstrates: an entity-linking FILTER (coref-style
name/patient-coreference + blind-valence gate) correctly separates one true-positive
antecedent-attribution (007: Amy) from one recency false-positive trap it must reject (010) and
nine trivial true-negatives, on a corpus where at most 1 candidate ever survives the filter.
Effectively **2 items carry all the discriminating signal** (007's positive match, 010's correct
rejection); the other 10 items are 0-candidate agreements on both sides.

WHAT IS NOT DEMONSTRATED: the retargeted `_pick_strict_cb` coherence-ranked backward search —
the part of the pre-reg's "same hippocampal circuit" claim doing the most novel conceptual work
(choosing among multiple simultaneously-valid causal antecedents by recency-of-agent-role,
exactly as coref chooses among multiple pronoun-antecedent candidates) — has never been exercised
on more than one candidate anywhere in this cert. Calling this "matches oracle" is accurate for
what was tested, but should not be read as validating multi-candidate causal-antecedent
selection; that capability is unvalidated, not proven.

**KEY CAVEAT FOR BUILDING FURTHER:** before extending or trusting this mechanism on any future
corpus/claim that depends on choosing among >=2 competing candidate antecedent events (its
putative core capability), it must first be tested on a dataset engineered to contain at least
one chapter with 2+ gate-passing HARM-valenced same-patient-coreferring prior agents before a
query event. This cert contains zero such cases. Until that test exists and passes, treat the
"coherence-ranking circuit reuse" claim as an *architecturally faithful but empirically untested*
extension, and treat the demonstrated result as: "entity-linking-gated causal attribution beats
naive recency on 1 item and matches a gold oracle given hand-provided agent/patient/valence
facts on a 12-item corpus with no multi-candidate cases."

## Numbers cited (MEASURED, this audit)
- Independent recompute: confused_4 BRIDGING/ORACLE=0.750, RECENCY/AUTO_OLD=0.500,
  TEXT_ONLY=0.250; full_12 BRIDGING/ORACLE=0.417, RECENCY/AUTO_OLD=0.333, TEXT_ONLY=0.333.
  (exact match to `data/exp_causal_attribution_bridging_v1/metrics.json`)
- Gate-passing candidate counts per item (12/12 items instrumented): item 007 -> 1 candidate
  (Amy); all other 11 items -> 0 candidates.
- Shuffle-control item 007: 14/20 = 0.70 survival, independently reproduced seed-by-seed
  (matches `shuffle_survival_rate: 0.7` in metrics.json).
- `git show d3b035e59 --stat`: touches only `experiments/exp_causal_attribution_bridging_v1.py`
  + `preregs/2026-08-03_causal_attribution_bridging_v1.md` (`hdlab/coreference_resolver.py`
  and `hdlab/situation_model_accumulate.py` NOT modified by this commit).

No atomization performed — this is a scope/framing correction on an already-landed verdict, not
a new cert-worthy result. Recommend Director downgrade the working framing of BRIDGING_WORKS
from "validates coreference-as-bridging circuit reuse" to "validates the entity-linking filter
half of that circuit reuse; the coherence-ranking half remains untested" before building further
on it.
