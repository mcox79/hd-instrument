---
problem: the_boards_who_did_what_rows_iterate_gold_verbs_so_a_fifth_of_asserted_clauses_are_outside_their_population_add_the_non_verbal_predication_row_to_the_board
status: SOLVED
bar: "the row published in the board's own metrics schema (both populations, floors, twin, CI), a plain-words scorecard line, the pre/post-pri-113 A/B visible on it, and the aggregate re-baselined (with-and-without) reported -- OR a numbered reason the row cannot be gold-free at decision time. NOT a requirement that the model beat every floor CI-separated (that is a located finding, reported honestly below)."
result: "Standalone cell experiments/exp_board_nonverbal_predication_row_v1.py computes the NON-VERBAL PREDICATION row in the board's per_dimension schema (n/model_acc/overlap_floor/floor_accs/strongest_floor_name/strongest_floor/twin_acc/model_minus_strongest/model_minus_twin/ci_sep_over_strongest/ci_sep_over_twin/population), gold-free at decision time. POPULATION = every gold subject-bearing clause (gold nsubj arc) whose gold predicate head is NOT tagged VERB. GOLD = the clause's subject head (the nsubj dependent) + predicate head (the nsubj arc's gold head). MODEL = the LIVE hdlab.situation_reader.SituationReader's fired event/state at the gold predicate token (its idx, via the reader's own _cached_tag/_extract_events, driven exactly as the pri 113 participant instruments drive it) AND its hdlab.copular_binding.robust_cop (holder,property) pair's holder matching a gold subject token -- a JOINT hit (the reader's structure DOES carry a holder field via bind_entity_states/robust_cop, so the brief's no-holder fallback does not apply; this is stated in the row's own population text). UD-EWT test 700 (n=167 of 762 subject-bearing clauses, verified 762 by construction) is THE board row; GUM/GENTLE cap-1200 (n=366) is the secondary out-of-supply replication, both computed and reported. RESULTS (2000-resample paired bootstrap over clauses, current tree = pri 113 landed/default-ON): UD-EWT n=167 model_acc=0.5269, floor[copula_adjacent_simple_rule]=0.4731 (upos_verb_detector floor=0.0898), twin=0.0659; model-minus-strongest +0.0539 CI[-0.0301,+0.1377] NOT CI-separated (half-width 0.0839); model-minus-twin +0.4611 CI[+0.3772,+0.5391] CI-SEPARATED. GUM n=366 model_acc=0.4290, floor[copula_adjacent_simple_rule]=0.3333 (upos_verb_detector=0.0519), twin=0.0410; model-minus-strongest +0.0956 CI[+0.0410,+0.1503] CI-SEPARATED (half-width 0.0546); model-minus-twin +0.3880 CI[+0.3361,+0.4399] CI-SEPARATED. Predicate-alone recall (informational, no holder requirement) is much higher: UD-EWT model 0.8383 vs floor 0.5329 vs twin 0.1916; GUM model 0.6120 vs floor 0.3880 vs twin 0.1530 -- so most of the joint-hit loss on UD-EWT is in the HOLDER half (copular_binding's (holder,property) binding), not the predicate-firing half; this matches the owner's prior finding that entity-state BINDING, not predicate detection, is the remaining loss (exp_nonverbal_predication_participants_v1.state_binding). LOCATED FINDING (honest, not hidden): on UD-EWT the row is NOT CI-separated over the strongest simple floor on the JOINT (predicate+holder) criterion -- the copula-adjacent simple rule is a strong floor on canonical copular clauses specifically because UD-EWT's non-verbal predicates are overwhelmingly plain copular ADJ/NOUN complements where 'nearest nominal before the copula' is usually right; the row DOES clear that same floor CI-separated on GUM (out-of-supply/out-of-genre, matching pri 110's own finding that this organ's real effect shows up LARGER out-of-supply than in-supply), and clears the information-free twin CI-separated on BOTH populations. The row is a correct, working, gold-free no-regress instrument; it is not (yet) a proof the joint-binding mechanism beats the best hand floor on UD-EWT specifically."
floor: "Two floors recomputed in place on this row's own population, gold-free (built from the reader's OWN tags, never gold): (a) upos_verb_detector -- the shipped UPOS==VERB event detector alone (hit iff the reader's own tag at the gold predicate token is VERB); UD-EWT 0.0898, GUM 0.0519 (expected near-zero by construction: the population is gold-non-verbal, so this only fires on the organ's own tagging mistakes). (b) copula_adjacent_simple_rule -- the strongest SIMPLE decision rule: scan for a copula/linking token (hdlab.attachment_arm.COP_FORMS, reused read-only), predicate = the first content word after it (skipping AUX/PART/DET/ADP/SCONJ/CCONJ/PUNCT), holder = the nearest NOUN/PROPN/PRON before it; a hit requires both heads to match gold. strongest_floor = max(a,b) = (b) on both populations: UD-EWT 0.4731, GUM 0.3333."
controls: "TWIN (information-free, paired): the SAME NUMBER of extra non-VERB-tagged fires as the model produces per sentence, placed on a RANDOM eligible token of that sentence (the exact mechanism exp_nonverbal_predication_participants_agent_v1._arms's own twin uses), with a random NOMINAL token of the sentence standing in for the holder; UD-EWT twin=0.0659, GUM twin=0.0410 -- beaten CI-separated on BOTH populations (UD-EWT +0.4611 CI[+0.3772,+0.5391]; GUM +0.3880 CI[+0.3361,+0.4399]), so the win is the organ's structure, not a firing-rate artifact. ORACLE (self-test): feeding the scoring primitive the gold predicate as the 'fired' set and a gold subject token as the bound holder scores 1.0 on both populations (UD-EWT cap60 n=14, GUM cap60 n=10) -- the hit logic itself is correct. PRE-113 A/B (checklist item 6): SituationReader(nonverbal_predication=False) (equivalent to HDLAB_NONVERBAL_PREDICATION=0) on the SAME items/population: UD-EWT model_acc 0.0659 (== the twin rate almost exactly -- before the landing the event detector essentially never fires on a non-verbal predicate, so the few joint hits it gets are chance-level), current tree 0.5269, delta +0.4610; GUM pre-113 0.0492, current 0.4290, delta +0.3798. This is the landing's effect on the row, now visible for the first time."
files_changed: "experiments/exp_board_nonverbal_predication_row_v1.py (NEW, standalone cell; writes data/exp_board_nonverbal_predication_row_v1/metrics.json via get_output_dir); notes/problems/<slug>/{SOLVED.md,board_nonverbal_row_patch.diff}. hdlab/, tools/, and experiments/exp_situation_model_qa_modern_v1.py are UNCHANGED on disk -- the board-file change is PROPOSED ONLY as board_nonverbal_row_patch.diff (git apply --check passes; NOT applied), adding board_nonverbal_predication_dimension(smoke=False) (delegating to this cell) and registering it in new_board_arms (NOT one of the 7 headline per_dimension rows; strategy promotes it after review, per the brief)."
reverify: "OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe experiments/exp_board_nonverbal_predication_row_v1.py --self-test   (asserts: UD+GUM non-verbal populations non-empty, oracle==1.0 on both, all required per_dimension schema keys present on both rows, floor_accs names both floors, upos_verb_detector floor near-zero, board wrapper returns both named rows). Full numbers: OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe experiments/exp_board_nonverbal_predication_row_v1.py --run   (writes data/exp_board_nonverbal_predication_row_v1/metrics.json: both populations x {current tree, pre-113 arm}, ~112s). git apply --check notes/problems/<slug>/board_nonverbal_row_patch.diff   against experiments/exp_situation_model_qa_modern_v1.py (verified PASS)."
---

## 1. What this builds

A standalone, gold-free-at-decision-time board cell for the NON-VERBAL PREDICATION row ("who is what / who
is where / who has what"): "the sky is blue" (property), "she is a doctor" (class), "he was here" (location),
"there is no proof" (existence). The board's existing who-did-what AGENT/PATIENT rows iterate
`gold_agent_items` (gold VERB predicates only), the entity rows read mentions, and the STATE row reads the
copular-binding path for a different purpose -- none of them scores the reader's non-verbal-predicate
detector directly, on its own population, the way a board row should. pri 113 (landed, default-ON) was the
largest single gain on exactly this fifth of the text and had zero board visibility until this cell.

## 2. The population (checklist item 1)

Every gold clause with a subject (a gold `nsubj` arc, UD subtypes already stripped by the loader:
`nsubj:pass` -> `nsubj`) whose gold predicate (that arc's head) is NOT tagged VERB in the gold UPOS column.

- **UD-EWT test 700 (the row):** 167 of 762 total subject-bearing clauses (21.9%) -- matches pri 110's own
  count (SOLVED.md section 10e) exactly.
- **GUM/GENTLE cap 1200 (secondary, out-of-supply/out-of-genre replication):** 366 of the capped population.

Both are computed by the SAME cell, SAME code path, differing only in the corpus loader
(`tools.build_attachment_validities.sentences` vs `experiments.exp_one_convention_two_losses_v1.gum_sentences`,
both already-modern, deprels gold, reused read-only).

## 3. The model's answer and the holder field (checklist item 1, the brief's escape hatch)

The brief allows scoring the predicate head alone "if the reader's structure has no holder field." It DOES:
`SituationReader.read()` calls `_read_entity_states` by default (`bind_entity_states=True`), which is
`hdlab.copular_binding.extract_entity_states` / `.robust_cop` -- a set of `(holder_idx, property_idx)` pairs,
the exact structure the pri 113 participant instrument's own `states()` function drives
(`heads = rdr._cached_parse_heads(...); pairs = CB.robust_cop(toks, up, heads, gate=True)`). This cell reuses
that SAME call per sentence. So the escape hatch does NOT apply: a HIT requires **both heads right** --

1. the reader's fired event/state set (`rdr._extract_events`, built from `rdr._cached_tag` +
   `hdlab.attachment_arm.predicate_sites`, the LIVE landed form -- driven exactly as
   `exp_nonverbal_predication_participants_agent_v1._arms` drives it, no monkeypatch) contains the gold
   predicate token, AND
2. `robust_cop`'s pair at that token has a holder index inside the gold subject's token set.

`recall_predicate_only` is also reported per row (informational) so the two halves of the loss are visible
separately -- see section 5.

## 4. Floors and twin (checklist item 1 and "floors recomputed in place")

- **(a) `upos_verb_detector`:** the shipped UPOS==VERB detector alone, gold-free (the reader's OWN tag, not
  gold). Expected near-zero by construction (the population is gold-non-verbal); reported as required.
- **(b) `copula_adjacent_simple_rule`:** the strongest SIMPLE rule -- scan for a copula/linking token
  (`hdlab.attachment_arm.COP_FORMS`, reused read-only, not edited), predicate = first content word after it
  (skipping AUX/PART/DET/ADP/SCONJ/CCONJ/PUNCT), holder = nearest NOUN/PROPN/PRON before it. Gold-free (uses
  the reader's own tags). `strongest_floor` = max(a,b), which is (b) on both populations.
- **Twin:** "a random clause token at the same firing rate" -- implemented as the SAME NUMBER of extra
  non-VERB-tagged fires the model produces per sentence, placed on a random eligible token of that sentence
  (byte-identical mechanism to the participant instrument's own twin), with a random nominal token of the
  same sentence standing in for the holder. Information-free by construction.

## 5. Results (full `--run`, 2000-resample paired bootstrap over clauses)

| population | n | model | floor (name) | twin | model-floor CI | sep? | model-twin CI | sep? |
|---|---|---|---|---|---|---|---|---|
| UD-EWT test 700 (THE ROW) | 167 | 0.5269 | 0.4731 (copula_adjacent_simple_rule) | 0.0659 | +0.0539 [-0.0301,+0.1377] | **NO** | +0.4611 [+0.3772,+0.5391] | YES |
| GUM/GENTLE cap1200 | 366 | 0.4290 | 0.3333 (copula_adjacent_simple_rule) | 0.0410 | +0.0956 [+0.0410,+0.1503] | **YES** | +0.3880 [+0.3361,+0.4399] | YES |

Predicate-alone recall (no holder requirement, informational): UD-EWT model 0.8383 / floor(b) 0.5329 /
upos_verb 0.0898 / twin 0.1916; GUM model 0.6120 / floor(b) 0.3880 / upos_verb 0.0519 / twin 0.1530. The gap
between the joint number and the predicate-alone number (0.8383 -> 0.5269 on UD-EWT) is almost entirely the
HOLDER half -- `copular_binding`'s (holder,property) binding is the dominant residual loss, matching the
owner's own prior drill (`exp_nonverbal_predication_participants_v1.state_binding`: "the highest-yield loss
is SUBJECT-ENTITY binding, not predicate detection").

**Honest located finding:** on UD-EWT the JOINT row is NOT CI-separated over the copula-adjacent simple floor
(+0.0539, CI includes 0). That floor is strong specifically because UD-EWT's non-verbal predicates are
overwhelmingly plain copular ADJ/NOUN complements ("she is a doctor") where "nearest nominal before the
copula" is usually the right holder and "first content word after it" is usually the right predicate -- a
simple rule wins on canonical cases almost by definition. The SAME row DOES clear that floor CI-separated on
GUM (+0.0956), the out-of-supply/out-of-genre population, mirroring pri 110's own finding that this organ's
real mechanism shows a LARGER effect out-of-supply than in-supply (a fitted rule degrades out-of-genre; a real
mechanism does not). Both populations clear the information-free twin CI-separated. This is reported as the
honest result, not narrated away.

## 6. Pre-113 vs current tree (checklist item 6)

Re-running the SAME items/population with `SituationReader(nonverbal_predication=False)` (equivalent to
`HDLAB_NONVERBAL_PREDICATION=0`):

| population | pre-113 model_acc | current-tree model_acc | delta |
|---|---|---|---|
| UD-EWT | 0.0659 | 0.5269 | **+0.4610** |
| GUM | 0.0492 | 0.4290 | **+0.3798** |

The pre-113 number is almost exactly the twin rate on both populations -- before the landing, the event
detector essentially never fires on a non-verbal predicate at all, so the handful of joint hits it gets are
chance-level (an occasional tagger VERB-mistake plus a lucky `robust_cop` binding). This is the landing's
effect on the board, made visible for the first time by this row; it was previously entirely board-invisible
(byte-identical on every existing per_dimension row per the brief's section 3 MEASURED evidence).

## 7. The aggregate, with and without the row (checklist item 6)

The most recent on-disk full board run (`data/exp_situation_model_qa_modern_v1/metrics.json`, current tree,
n=11369 pooled over the 7 headline dimensions): **aggregate_19c_free = 0.6185**. This cell's diff does NOT
touch `_agg` or the 7-dimension headline (the row lives in `new_board_arms` only, per the brief's explicit
instruction -- "NOT in the seven per_dimension rows -- strategy promotes it after review"), so the headline
number is UNCHANGED by landing this cell/diff. For visibility, the ILLUSTRATIVE item-weighted aggregate IF the
UD-EWT row were folded in as an 8th dimension (same `_agg` formula: item-weighted mean of `model_acc`):

    n=11369 (7 dims, current)         aggregate 0.6185
    + n=167 (nonverbal, model=0.5269) -----------------
    n=11536 (8 dims, illustrative)     aggregate 0.6172   (delta -0.0013)

The new row's own accuracy (0.5269) sits just below the current pooled mean, and its population is small
relative to the 7-dimension pool (167 of 11536, 1.4%), so folding it in would move the aggregate by about
one-tenth of a point -- a NEGLIGIBLE headline change, but the row's real value is not the aggregate shift: it
is that a fifth of what a text asserts (non-verbal predication) is now measured at all, with an honest
CI-separated-over-twin margin on both populations and a located, numbered account of where the remaining loss
is (the holder/binding half, not predicate detection). I am NOT retiring the 0.6185 figure or any prior
aggregate myself (the brief's instruction); this section states the new honest baseline the row would imply
for strategy's own promotion decision.

## 8. Self-test

`--self-test` (cap 60 both populations, n_boot=200): non-verbal population non-empty on both (UD-EWT n=14,
GUM n=10 at this tiny cap), the oracle (gold predicate as the fired set, a gold subject token as the bound
holder) scores exactly 1.0 on both -- the hit/scoring primitive itself is correct, independent of the reader
-- every required per_dimension schema key present on both rows, `floor_accs` names both floors,
`upos_verb_detector` floor near-zero (0.0714 at cap 60), and the board wrapper
(`board_nonverbal_predication_dimension`) returns both named sub-rows. All PASS.

## 9. The proposed board patch (NOT applied)

`board_nonverbal_row_patch.diff`: adds `board_nonverbal_predication_dimension(smoke=False)` to
`experiments/exp_situation_model_qa_modern_v1.py` (a thin delegate to this cell's own function of the same
name, mirroring the existing `board_grounding_coverage_quality_dimension` delegate pattern) and registers it
in `run()`'s `new_board_arms` dict (3-line addition, same pattern as every other new-arm registration in that
function) -- NOT in the 7-dimension headline. `git apply --check` against the current
`exp_situation_model_qa_modern_v1.py` PASSES. I did not apply it (hard rule); I also functionally verified the
patched function by constructing the patched module text in memory and exec'ing it from a throwaway copy
(never written to `experiments/`) -- `board_nonverbal_predication_dimension(smoke=True)` returns both named
rows correctly through that exact call path.

## 10. Understanding / improvement probe

**Fully understood?** Yes, with one open question worth flagging to strategy: the UD-EWT floor not being
CI-separated (section 5) is a population-composition fact (UD-EWT's non-verbal predicates are
copula-canonical), not an instrument bug -- confirmed by the oracle (hit logic correct) and by the GUM
contrast (same mechanism, same code, different population, CI-separated). **Opportunities for improvement**
(not built here, out of this brief's remit -- listed for the promotion review): (1) the holder/binding half is
the dominant residual loss (section 5) -- pri 117 (copular subject attachment) and pri 119 (typed attribute)
are the adjacent problems named in the brief's checklist item 7 that would close exactly this gap; (2) the
simple-rule floor could be made modestly stronger (e.g. skip a relative clause before committing to "nearest
nominal") which would sharpen whether the UD-EWT non-sep result survives a harder floor -- flagged, not built,
since the brief asks for "the strongest SIMPLE rule," not an arbitrarily strong one; (3) GUM's larger margin
suggests an out-of-genre robustness story worth a dedicated one-line note on the scorecard alongside the
plain-words line.
