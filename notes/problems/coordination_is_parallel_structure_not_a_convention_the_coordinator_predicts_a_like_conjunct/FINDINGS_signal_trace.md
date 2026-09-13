# Coordination — the full-stack-upstream signal trace (measured, 2026-09-13)

Baseline (UD-EWT test 700, gold categories, current asset `attachment_validities_v1.json`):
map1 conj **0.300**, UAS 0.6034; incr conj 0.288. Confirmed.

## Where the signal is lost, input by input (`experiments/scratch_conj_anatomy.py`, n=233 gold conj arcs)

| trace point | number | reading |
|---|---|---|
| arm conj recall | 0.300 | the wall |
| `coord` construction fires the EXACT gold arc | **0.245** | the arm is never even OFFERED the right arc 75% of the time |
| cross-category conjuncts (different UPOS) | 0.215 | strict same-UPOS gate rejects 1 in 5 outright |
| 2nd conjunct run starts with a modifier | 0.300 | "first content word after cc" grabs DET/ADJ, not the head noun |
| first conjunct itself correctly attached | 0.481 | half the time the conjunct would inherit an upstream head error (drags the phrase; not a conj-recall cause but a downstream one) |
| **TEACHER posterior mass on the gold conj arc** | **mean 0.054, median 0.023, frac>0.3 = 0.009, frac<0.05 = 0.644** | **THE SMOKING GUN: the acquisition teacher is coordination-blind. The `coord` cue's validity is trained on ≈zero positive signal.** |

## The diagnosis (brain-foundational)
The coordination arm is a real brain mechanism (parallel-structure facilitation — Frazier, Munn, Taft & Clifton 2000; prediction — Levy 2008; cue-based retrieval of a like-category antecedent — Lewis & Vasishth 2005; slot-sharing — the conjuncts jointly fill one governor slot as a plural set). It fails because the UPSTREAM component it relies on — the ACQUISITION TEACHER (co-occurrence SelfSupEM + semantic-bootstrapping) — has NO model of coordination. It never generates a coordination posterior, so the learned `coord` validity is ~flat. Plus the read-time construction mis-identifies the parallel heads (modifier bug, cross-category, nearest-not-head).

Owner's thesis realized: "a truly brain-foundational component not working properly ⇒ an upstream component it relies on is not 100% brain-foundational." The teacher lacks the parallel-structure prediction the brain has.

## The fix (both halves brain-foundational, both treebank-free)
1. **Teacher (upstream):** add PARALLEL-STRUCTURE PREDICTION to the acquisition teacher — when a coordinator sits between two like-class phrase heads, boost R→L (conj) and cc→R in the teacher's score matrix. Derived from coordinator position + category parallelism, NOT from trees.
2. **Read-time construction:** identify the PARALLEL HEADS correctly — R = head of the phrase after cc (last NOUN/PROPN of the nominal run / the verb), L = nearest preceding content head of R's parallel CLASS (coarse: nominal {NOUN,PROPN,PRON,NUM} / predicate {VERB,ADJ} / adverbial {ADV}). Slot-sharing L-selection (the co-argument that shares R's governor, via the semantic-bootstrapping plausibility) is the lever past the ~0.54 nearest-same-class ceiling.

## SMOKE result (cap 1200, test 200) — the mechanism works, controls decisive
| arm | conj map1 | conj incr | UAS |
|---|---|---|---|
| base (floor) | 0.287 | 0.279 | 0.5885 |
| **full** (teacher+construction) | **0.419** (paired CI [0.062, 0.202]) | **0.411** | 0.5960 (↑; nmod 0.404→0.482, obj 0.653→0.677) |
| scramble twin (parallelism removed, density-matched) | 0.194 | 0.171 | 0.5892 |
| shuffled-strengths twin (3 seeds) | 0.0/0.05/0.11 | — | UAS 0.10/0.10/0.22 |

The scramble twin (coordination machinery pointed at WRONG parallel heads) lands at 0.194 — *below* base — so PARALLELISM is decisively load-bearing, not merely "having a coord cue". The full-scale run (cap 6000, test 700, incl. slot-sharing arm) is running; headline numbers land there.

## Construction-fire diagnostic (test 700, gold conj arcs n=233)
- OLD `coord_arcs` proposes the gold conj arc: 0.245
- NEW parallel `coord_sites`: 0.313 (fixes the modifier + cross-UPOS bugs)
- NEW + slot-sharing L: 0.283 (WORSE — slot-sharing sometimes moves L off the gold head; likely helps conj recall LESS, to be settled by the full_slot arm)

Key reframe: conj recall (smoke 0.419) EXCEEDS the corrected construction's fire-rate (0.313), because the DOMINANT lever is the parallelism TEACHER — it reshapes the general cue strengths (locality/catpair for L→R attachments) beyond the explicitly construction-fired sites. The `teach_only` vs `constr_only` ablation quantifies the split.
