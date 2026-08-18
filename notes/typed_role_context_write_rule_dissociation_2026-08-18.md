# DOES THE GRAMMATICAL RELATION CARRY SUBSTITUTABILITY? FIRST ARM ON THE TYPED-STRUCTURE AXIS.

`exp_typed_role_context_write_rule_dissociation_v1`, FULL, code_version v1.1 (upstream corpus/slot
pass v1.0), commit pending. Pre-registered in
`notes/admissible_supervision_sources_drill_2026-08-18.md` sec 6 and
`notes/PLAN_ORGAN_STEP_LADDERS_2026-08-17.md` sec 6.29(4). Metrics:
`data/exp_typed_role_context_write_rule_dissociation_v1/metrics.json`.

## PRIOR-WORK CHECK

Enumerated by name-level scan over `experiments/` (the drill's own `os.walk` over `data/` established
`tools/substrate_query.sh` is non-functional -- zero bytes, exit 0 -- and is not used here either).
Found `experiments/exp_dependency_context_codebook_location_artifact_v1.py` (2026-07-20, + a
`_weight_sweep_v2`): the SAME hypothesis (window vs dependency-typed co-occurrence, PPMI+SVD),
credited to Levy & Goldberg 2014 and Komninos & Manandhar 2016. **It never landed -- no `data/`
directory -- so it is UNPROVEN, not refuted.** Its feature-building code (a rule-based
preposition/verb-slot trigger table) is NOT reused: that cell had no real dependency parser and a
punctuation-free corpus (its own docstring says so); this project now owns a real, persisted parser
(`hdlab.arc_parser` / `hdlab.arc_labeler` / `hdlab.pos_tagger`), so this cell uses the real parse
instead, a strictly more faithful test of the same idea. Its `build_random_context_cooc`
column-permutation control is the same DESIGN PATTERN this cell's `random_typing` control uses.
Also disclosed up front, again: `exp_selectional_constraint_bridge_v1` already failed on the
selectional-preferences asset for a DIFFERENT task (bridging, not this dissociation instrument).

## REGRESSION GATE

All 8 of `exp_dissociation_score_instrument_v1`'s cached checks reproduced at delta 0.0000 (reused
`exp_predictive_coding_write_gate_dissociation_v1.dsi_regression_gate()` verbatim, not
re-implemented): F_ORTHOGRAPHIC 0.5000, F_FREQUENCY 0.4901, F_SCRAMBLE 0.4664, F_CONSTANT_PROTOTYPE
0.5431, KNOWN_ANSWER 0.9599, RANDOM_VECTOR_STORE 0.4862, INCUMBENT_LIVE_STORE 0.0710,
RAW_COUNT_FULL_ACCUM 0.0510. INSTRUMENT_LICENSED=True. **THE BAR IS `max(four floors)` =
F_CONSTANT_PROTOTYPE = 0.5431, NOT 0.5.**

Population: 242 matched pairs per cell (SET_P/SET_S), 617 distinct words, all NOUNS (scope limit
carried forward unchanged). A0 is DSI's own cached RAW_COUNT_FULL_ACCUM arm, reused not rebuilt:
AUC=0.0510, CI=[0.0334,0.0709].

## THE ARM TABLE (n=242/242, N_BOOT=10000; CI half-width in the fourth column)

| arm | AUC | 95% CI | half-width | vs 0.5 | vs bar 0.5431 |
|---|---|---|---|---|---|
| A0_INCUMBENT (reused) | 0.0510 | [0.0334, 0.0709] | 0.0188 | BELOW | BELOW |
| U1_TYPED_CONTEXT | 0.6669 | [0.6184, 0.7136] | 0.0476 | ABOVE | **ABOVE (CI-separated)** |
| U3_ROLE_ONLY | 0.6466 | [0.5977, 0.6936] | 0.0479 | ABOVE | ABOVE |
| T2_UNTYPED_SAME_COVERAGE | 0.6128 | [0.5614, 0.6622] | 0.0504 | ABOVE | ABOVE |
| T3_COMBINED | 0.3533 | [0.3040, 0.4031] | 0.0495 | BELOW | BELOW |
| N1_LABEL_PERMUTED | 0.5564 | [0.5052, 0.6071] | 0.0509 | ABOVE | NOT_SEPARATED |
| N2_RANDOM_TYPING | 0.5602 | [0.5098, 0.6116] | 0.0509 | ABOVE | NOT_SEPARATED |
| S1_SLOT_COMPETITION | 0.0695 | [0.0475, 0.0940] | 0.0233 | BELOW | BELOW |
| N3_MAGNITUDE_PERMUTED | 0.0591 | [0.0396, 0.0808] | 0.0206 | BELOW | BELOW |
| U1_COVERAGE_MATCHED (n=242/242) | 0.6669 | [0.6186, 0.7157] | 0.0485 | ABOVE | ABOVE |
| S1_COVERAGE_MATCHED (n=201/172) | 0.0664 | [0.0414, 0.0949] | 0.0268 | BELOW | BELOW |

## N5 COVERAGE-MATCHING (n before -> after, COVERAGE_MIN=3, pre-registered before any result seen)

U1 (arc-observation coverage): P 242->242, S 242->242 -- **no attrition at all**; every matched word
had at least 3 typed-context arc observations. S1 (slot-filling coverage): P 242->201, S 242->172 --
the flagged P>S asymmetry (drill sec 4.3, "SET_P 218 vs SET_S 185" on the larger asset) reproduces
qualitatively here on this smaller, independently-built corpus (201 vs 172, P still ahead). Checked
against STOP-IF 6 (full vs coverage-matched AUC must not disagree by more than a CI half-width): S1
full 0.0695 vs coverage-matched 0.0664, delta 0.0031, well under the 0.0233 half-width -- **no
coverage artifact detected for S1.** U1 has no coverage attrition to test against.

## WHAT T2_UNTYPED_SAME_COVERAGE DECIDED (TYPE vs SELECTION)

T2 keeps the exact same arc-connected neighbours as U1 (same coverage, by construction, since it
consumes the identical flattened arc-event list) but strips the relation/direction label, leaving
context = neighbour identity alone. T2 clears the bar on its own (0.6128 CI-separated above 0.5431)
-- **restricting to syntactically-connected words is itself most of the win over full bag-of-words**
-- but U1 beats T2, paired margin +0.0541 [0.0339, 0.0753], CI-separated above zero. **The label adds
real, CI-separated marginal information beyond mere word selection.** That is the ORIGINAL brief's
own decisive question, answered: not "type or selection", but selection carries most of it and type
adds a real, smaller increment on top.

## THE THREE MANDATORY CONTROLS

- **N1_LABEL_PERMUTED** (identity-matched: same parses, same neighbours, same token count, label
  MARGINAL preserved exactly, only the neighbour-to-label correspondence destroyed): 0.5564
  [0.5052,0.6071], NOT separated from the bar. U1 vs N1 paired margin: **+0.1105 [0.0800, 0.1420],
  CI-SEPARATED ABOVE.** The decisive control for U1 survives.
- **N2_RANDOM_TYPING** (iid uniform label draw, marginal NOT preserved): 0.5602 [0.5098,0.6116]. U1
  vs N2: **+0.1068 [0.0696, 0.1449], CI-SEPARATED ABOVE.**
- **N3_MAGNITUDE_PERMUTED** (identity-matched for S1: same magnitude distribution, same 100% write
  rate, only which occurrence gets which delta is shuffled): 0.0591 [0.0396,0.0808]. S1 vs N3 paired
  margin: **+0.0104 [-0.0069, 0.0289], NOT SEPARATED.** S1's small edge over N3 is not attributable to
  the slot-competition signal.

A fourth, non-mandatory check (`N6_PARSE_NOISE`, corrupting 0/10/25/50% of neighbour identities
post-hoc) found U1's AUC barely moves: 0.6669 -> 0.6649 -> 0.6603 -> 0.6507 (spread 0.0162, far under
the 0.10 STOP-IF-7 threshold). **U1 is not fragile to corrupting WHICH word fills the neighbour slot**
-- a second, independent line of evidence for the caveat below, not just a robustness check.

## STOP-IFs FIRED (in the pre-registered order)

1. Licence: PASS, not fired.
2. U1 vs N1: separated above -> **not fired** (typing IS a variable).
3. **U1 ~ U3 FIRED.** Paired margin U1 vs U3 = +0.0203 [-0.0185, 0.0591], NOT SEPARATED. U3
   (relation+direction alone, neighbour IDENTITY DISCARDED) reaches 0.6466, 97% of U1's own margin
   over chance. **Per the pre-registration's own instruction: this must be said plainly and NOT
   reported as a clean context-type win** -- most of U1's power is a coarse ~40-way role/position
   profile, not fine-grained lexical substitutability. The N6 parse-noise insensitivity above is
   independent, converging evidence for the same reading.
4. U1 above N1 AND above bar -> the "margin, not a win" STOP-IF does not apply as worded (U1 DOES
   clear the bar CI-separated); superseded in practice by STOP-IF 3's caveat.
5. **S1 vs N3 FIRED (NOT separated).** Second independent negative on prediction-error / cue
   competition as a write-rule mechanism -- a DIFFERENT site and target from the 6.21 null (slot
   population, not self-history; signed 100%-write delta, not a binary gate) and it is STILL a null.
6. Coverage-matched vs full: **not fired** for S1 (delta 0.0031 << half-width 0.0233); not applicable
   to U1 (zero attrition).
7. N6 spread 0.0162 << 0.10 -> **not fired**; parse quality (UAS cited 0.7868 from
   `data/exp_depparse_hashed_cpu_v1/metrics.json`, not recomputed) is not the binding constraint.
8. **FIRED, with the STOP-IF-3 caveat attached: U1 CI-clears the bar (0.5431) above all four floors
   AND both its mandatory controls (N1, N2).** Read together with (3): Organ A's closure is reopened
   for a coarse typed-ROLE-PROFILE effect, not demonstrated for genuine lexical/neighbour-level
   substitutability. The next cell this motivates is U3 alone, scaled and scrutinised on its own,
   not a rerun of U1.

## T3_COMBINED (added mid-run on the coordinator's instruction, Komninos & Manandhar 2016)

Concatenating the L2-normalised bag channel (this cell's own occurrence data, delta=1 uniformly) with
U1's typed channel, then L2-renormalising, gave **0.3533 [0.3040,0.4031] -- BELOW chance, and
CI-separated BELOW U1 alone** (paired margin -0.3136 [-0.3476,-0.2812]). It still beats A0
(+0.3023 [0.2563,0.3497]) but the combination actively hurts relative to the typed channel by itself.
Read plainly: on this instrument, the bag channel's dominant co-occurrence content pulls the combined
representation back toward SET_S (the syntagmatic, co-occurring pole) hard enough to outweigh what the
typed channel contributes, the opposite of the published best-of-both-worlds result. Disclosed rather
than omitted, per the coordinator's instruction to add T3 and report it either way.

## ARMS-MUST-DIFFER / CONSTRUCTION SANITY

9 of 9 score-vector digests distinct (sha256 over concatenated P+S scores per arm). No degenerate
duplicate construction.

## PROCESS NOTE: A STALE-CHECKPOINT RISK, CHECKED AND CLOSED

The coordinator flagged, correctly, that this cell's first self-test run resumed a `SLOT_DIST`
checkpoint written 40 seconds before a code edit, under a FIXED scratch path and an unchanged
`CODE_VERSION`. Checked off disk: the intervening edit (a bad self-test fixture fix) never touched
`build_global_slot_distribution` or anything upstream of it, so the resume was semantically safe --
but the process hazard (a version tag that only protects if bumped) was real. Fixed two ways, not
one: (1) the self-test's own scratch path is now a **fresh, uniquely-named directory every
invocation** (`_selftest_scratch_<pid>_<ns>`), making stale reuse structurally impossible rather than
policy-dependent; (2) the file now carries **two version tags** -- `UPSTREAM_VERSION` (keys the
expensive corpus-wide `SLOT_DIST` and per-word `OCC` passes) and `CODE_VERSION` (keys everything
downstream, bumped to v1.1 when `T2_UNTYPED_SAME_COVERAGE` and `T3_COMBINED` were added) -- so a
downstream-only change can no longer share a key with an upstream-affecting one, and does not force a
wasteful recompute of the ~5-minute corpus pass when it does not need to. A prior smoke attempt was
separately abandoned mid-run (piped through a shell `timeout` + `tail`, which reported a misleading
exit code and silently truncated the run); replaced with detached `Start-Process`, separate
stdout/stderr, a PID file, and a bounded in-turn poll loop, per the coordinator's correction. No
number in this note was ever read from that abandoned attempt.

## SCOPE LIMITS

All 242 matched pairs are NOUNS; every number here is a conclusion about nouns, not the lexicon.
`exp_selectional_constraint_bridge_v1` already failed on the selectional-preferences asset for a
DIFFERENT task (bridging vs this dissociation instrument), disclosed above per the pre-registration's
own instruction, not as an afterthought.

## ONE PLAIN SENTENCE

The grammatical job a word does (which typed slot it fills, and to a lesser but real extent which
specific word fills it) carries a genuine, statistically separated signal above every floor and above
two decisive scrambled controls -- but most of that signal turns out to be *which kind of slot*, not
*which word*, so the honest claim is narrower than "grammar carries substitutability": it is closer to
"knowing a word's syntactic role-profile predicts its substitutability class about as well as knowing
its typed neighbours does," and that distinction, not a flat yes/no, is this cell's actual result.
