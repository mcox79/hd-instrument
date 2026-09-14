---
problem: the_passive_cue_fires_on_the_whole_sentence_not_the_clause_33_of_43_licensed_agent_overrides_are_gold_active_so_the_marked_cue_override_breaks_more_than_it_fixes
status: SOLVED
bar: "Clause-local detector: false fires on gold-active clauses down from 33/43 CI-separated with recall on true passives not down; the override anatomy flips to net-positive (fixes > breaks) or the licence is withdrawn with the number; every consumer moved to the one detector; the board's agent dimension not down; twin (random equal-size set of clauses declared passive) at floor -- OR a numbered located negative naming which consumer the clause-local cue helps and which it hurts."
result: "THE CUE WAS ANSWERING THE WRONG QUESTION -- 'is this SENTENCE passive' where every one of its four consumers asks 'is THIS PREDICATE passive' -- AND FIXING THAT MOVED THREE CONSUMERS WITH NONE DOWN. (1) THE DETECTOR, per predicate, through the LIVE brain-foundational chain (count-based category organ + attachment arm, no gold at decision time): UD-EWT test, 2605 gold-VERB predicates in 1240 sentences -- the shipped whole-sentence `is_passive_clause` scores precision 0.3784 / recall 0.8235; the predicate-anchored `is_passive_predicate` scores precision 0.9606 / recall 0.8971, i.e. precision up 2.5x with recall UP, 200 fixes against 11 breaks head to head, decision accuracy +0.0726 CI95[+0.0566,+0.0892] CI-separated over the shipped floor, with a same-rate random TWIN at -0.0177 CI-separated BELOW the floor. IT TRANSFERS TO TWO HELD-OUT MODERN GOLDS the counts never saw: GUM 29,217 predicates 0.3643/0.8123 -> 0.9503/0.8517 (+0.1030 CI-sep) and the OOD GENTLE split 0.4596/0.9000 -> 0.9821/0.9167 (+0.0768 CI-sep), twin CI-separated below on both. (2) THE OVERRIDE ANATOMY THE BRIEF WAS OPENED ON: the passive licence fires 92 times on the 1423-item agent population, 83 of them on gold-ACTIVE clauses, fixing 1 and breaking 30 (conflict validity 0.032 -- pri 106's 1/30 reproduced exactly); with the corrected cue plus the by-phrase confirmation it fires 11 times, 0 on gold-active clauses, fixing 1 and breaking 0 (validity 1.000). (3) THE BOARD'S OWN who_did_what_agent ROW, computed by the board's own function: 0.8271 (CI-separated BELOW its own positional floor 0.8468) -> 0.8489 with the cue fix at all its call sites -> 0.8552 with the board arm's duplicate RETIRED in favour of the organ, which is +0.0084 CI95[+0.0007,+0.0157] -- CI-SEPARATED ABOVE its own floor for the first time; passive slice 0.1875 -> 0.6250 and active slice 0.8344 -> 0.8579 against a 0.8564 floor (no regress). (4) A SECOND CONSUMER UP CI-SEPARATED: `agent_supports` -- the voice flip the live reader runs on every sentence -- 0.7511 -> 0.7637, +0.0127 CI95[+0.0070,+0.0197]. NO CONSUMER DOWN: the coarse role labeler on UD-EWT test 700 under live heads is +0.0014 CI95[0.0000,+0.0031] over all 2216 arguments and +0.0025 over the 1205 core ones, with gold nsubj:pass (n=48) and obl:agent (n=19) byte-identical. THE HONEST ATTRIBUTION: inside the ORGAN the cue fix is worth 3 items (+0.0021, NOT separated) because the organ already required a by-phrase; the 30 broken decisions live in the BOARD ARM's duplicate of the hybrid, where the same one-line change is +0.0204 CI95[+0.0126,+0.0281] CI-separated. A SECOND, INDEPENDENT DEFECT FOUND BY TRACING ONE RUNG DOWN: the board arm's copy never passes `byhead_agent_cue=True`, so the landed by-phrase CASE cue has never reached the board -- retiring the copy in favour of the organ is +0.0239 CI95[+0.0155,+0.0323] on its own and recovers 5 of the 16 passive agents; RETIRED in this diff (phase 7 Q1). PHASE 7 (probe, 2026-09-14 13:50) additionally: every break, miss and lost passive agent named and attributed to its rung (17.1/17.2); the two hybrids' four code differences decomposed one at a time (17.3); the six in-repo voice detectors enumerated with file:line, consumers and a measured verdict each -- two foldable now (the patient board 0.8120 -> 0.8135, the byhead gate's firing rate halved 32 -> 16), one DEAD on the live path (arc_labeler's voice correction changes 25 labels alone and ZERO with COMPETITION_ROLES live), one needing its own brief (17.5); the validity table RE-ACCRUED twice and shown NOT to be pri 111's number (17.6); and a fidelity defect in my own phase-6 harness found and corrected (call site 2 had been left shipped, which UNDER-reported the result -- 17.7). PHASE 7b (2026-09-14 14:30): D2 (`precise_passive`) and D4 (`participle_bypp_gate`) FOLDED onto the one organ and D5 (`arc_labeler.label_voice_correct`) DELETED, all inside this diff (5 files; zero call sites in tools/, enumerated). Measured with the fold OFF and ON in one run: the board's AGENT row 0.8271 -> 0.8559, +0.0091 CI95[+0.0014,+0.0168] CI-SEPARATED above its own floor, passive slice 0.1875 -> 0.6250, active 0.8344 -> 0.8586; the board's PATIENT row 0.8120 -> 0.8135 but its own floor also rises 0.7203 -> 0.7227, so the MARGIN is flat (-0.0008) -- D2 is a consolidation, not a win, and the recomputed-in-place floor is what caught that; the labels rung with `label_voice_correct` deleted is BYTE-IDENTICAL on all three populations (0.6995 / 0.5417 / 0.6316), so the deletion is a measured no-op. NINE shipped witnesses run with the fold OFF then ON: 7 GREEN both, 2 RED both and both PRE-EXISTING at HEAD (`test_arc_labeler_fastpath_hdlab_landing` 2/4 with identical failure lines and counts before and after, and its failing checks pass voice_correction=False so they never touched the deleted code; `test_byhead_agent_cue_landing` raises a TypeError in its OWN line 80, i.e. the byhead cue's landing witness has not been executing at all). ZERO witnesses go red because of the fold, and none pins the old detector's number. INTEGRATION (2026-09-14 16:10): with the 5-file diff LANDED, the now-executing byhead landing witness caught a REAL DEFECT IN D4 and it is repaired in this folder's diff. D4's first fold folded a CONSTRUCTION detector (`participle_bypp_gate` -- is there a V-en with a demoted agent in a by-phrase) onto a FINITE-CLAUSE VOICE READ (`is_passive_predicate`, which requires an auxiliary), so it dropped every REDUCED participial passive: 7 of 7 lost items on QA-SRL's clean agent-post slice have the identical signature (cue `none`, pre-fold gate True, folded gate False, suffix-participle True) -- `those used BY non-human animals`, `a display performed BY the male`, `mass divided BY volume`. Gate recall 62/90 -> 53/90; the byhead pick 0.6667 -> 0.6000. THE REPAIR is this organ's own story read in the other direction (the auxiliary OPENS the expectation, the by-phrase CONFIRMS it -- with no auxiliary the confirmation carries the construction alone): a by-governed NP plus EITHER the organ's voice read OR participial morphology, a strict SUPERSET of the pre-fold gate. RE-MEASURED: clean agent-post 0.6000 -> 0.6778 (above the pre-fold 0.6667, 63 gate fires vs 62), full non-canonical 0.6617 -> 0.6866 (above the pre-fold 0.6816), canonical no-regress n=845 back to 0.7077 with ZERO disagreements, UD agent gate fires 16 -> 33 (one MORE than the pre-fold 32), and the board's agent row unchanged at 0.8552, +0.0084 CI95[+0.0007,+0.0157] still CI-separated above its floor. AND THEN (b) IS ALSO TRUE: after the repair the organ differs from the experiment's copy on exactly ONE row per passive slice, the same row, and the ORGAN IS RIGHT -- `They are led by head coach Monreal` (gold `head coach Monreal`; organ `head`, experiment `They`), because `led` is an irregular participle the copy's suffix test cannot see. The witness's byte-faithfulness check should be RE-PINNED to the organ's arm, not weakened. WITHDRAWN from the phase-7b record: the D4 'firing rate halves 32 -> 16, a 2x precision gain' claim -- it was half precision gain and half recall loss, and the UD aux:pass gold could not tell them apart because the construction this gate detects is invisible to it. INTEGRATION ROUND 2 (16:05): (Q1) `byhead_twin_repair.diff` emitted (NOT applied) -- the same repair for the experiment's copy, so the witness's byte-faithfulness check is restorable rather than merely re-pinnable. (Q2) D2 given the SAME construction-population check: on UD-EWT test (2605 predicates, 126 gold passive) the organ read ALONE gains 17 true passives and LOSES 3 -- `especially oriented`, `was surprised`, `never been disappointed`, all three because the CATEGORY organ tags the participle ADJ one rung above. The fold is therefore WIDENED to a strict superset (organ read OR the pre-fold window+suffix route): detector true positives 117 -> 120 (recall 0.929 -> 0.952) for 5 more false fires, and at the consumer -- the board's who-did-what PATIENT row by the board's own function, floor recomputed in place -- model 0.8135 pre-fold / 0.8151 organ-only / 0.8167 superset with margins +0.0932 / +0.0924 / +0.0940, all CI-separated; both relcl witnesses exit 0 either way. The superset is NOT CI-separated from the organ-only fold (half-width ~0.02 vs 0.0016); it ships because it is the only form that cannot lose a firing either predecessor had, which is the guarantee a fold onto one organ has to make, and D4 is the evidence for taking that guarantee seriously. THE METHODOLOGICAL FINDING, above any single number: a detector folded onto a shared organ must be checked on the population of the CONSTRUCTION IT DETECTS, not on the gold its consumer happens to be scored against -- I folded D2 and D4 having measured both only on UD's aux:pass gold, which is blind to the reduced participial passive and to the participle/adjective boundary, so both folds looked like clean precision gains while quietly losing recall; two consumer-level witnesses on DIFFERENT corpora caught them, and for D4 the board could not have (the narrow fold was +1 item on the board while it was -7 on QA-SRL). FOLD TO A STRICT SUPERSET unless the narrowing is itself measured on the construction's own population."
floor: "(1) DETECTOR: the shipped `hdlab.thematic_role_labeler.is_passive_clause`, measured on the SAME 2605 predicates in the SAME run -- precision 0.3784 / recall 0.8235 / decision accuracy 0.9202 -- plus two STRONGER intermediate floors measured alongside: the same detector scoped to the clause span (what `agent_override_fires` does today) 0.4860/0.7647, and `hdlab.relcl_resolver.precise_passive`, which is already predicate-anchored, 0.9464/0.7794. Every delta is quoted against the shipped floor and the new read beats the STRONGEST of the three on precision and recall on every population. (2) AGENT CONSUMER: the POSITIONAL floor the board itself uses (nearest pre-verbal clause-local nominal, `exp_board_agent_slot_ud_v1.floor_positional_agent`) = 0.8468 on UD-EWT test n=1423, with the landed board model 0.8271 measured alongside; `hybrid_without_the_passive_licence` (pp_gov + noncase only) 0.8475 is reported too, so the passive cue's own contribution is not confounded with the other two marked cues. (3) BOARD ROW: the board's own floor from its own function, 0.8468, and its own shuffled-supports twin, 0.2853. (4) GUM / GENTLE: the same shipped whole-sentence detector recomputed in place on each population (0.3643/0.8123 and 0.4596/0.9000) -- no floor is pasted across populations."
controls: "(1) INFO-FREE TWIN, DETECTOR, on all three populations: a RANDOM equal-size set of predicates declared passive at the new cue's own firing rate -- UD-EWT precision 0.0462 and decision accuracy -0.0177 CI95[-0.0341,-0.0004] CI-separated BELOW the floor; GUM -0.0139 CI-sep below; GENTLE -0.0502 CI-sep below. (2) INFO-FREE TWIN, CONSUMER: the passive licence fires on a random equal-size set of agent decisions -- 0.8468 = the positional floor EXACTLY (it stops helping), against the corrected cue's 0.8482. (3) TWO HELD-OUT MODERN GOLDS the counts never saw (GUM 275 files, GENTLE 26 files OOD), 11x and 0.6x the UD-EWT test size. (4) TWO GOLD CONVENTIONS reported side by side -- raw UD (aux:pass/nsubj:pass/csubj:pass) and a propagated gold adding the bare CONJUNCT of a passive predicate -- and the conclusion is identical under both (raw: 0.9213/0.9286 new vs 0.3503/0.8175 shipped). (5) TRAIN/TEST SEPARATION: the counts and the criterion theta are accrued/swept on UD-EWT TRAIN (22,576 predicates) and applied UNCHANGED to test; the train sweep is a flat plateau (F1 0.9345-0.9366 over theta 0.15-0.65, best 0.50). (6) UPSTREAM CONTRAST: the detector measured with and without the reader's own heads -- 0 of 2605 decisions differ, so the claim 'the arc confirms but does not decide' is a count, not an assertion. (7) NO-REGRESS measured on the other call sites in the same run (see result), and the shipped witness `verification/test_coarse_role_competition.py` is green at HEAD (37/37) with its four voice assertions re-checked under the PATCHED cue inside the cell's self-test. (8) PATCH FIDELITY: the diff is GENERATED from the cell's own organ block, the self-test asserts the diff's added lines are byte-identical to the measured code, `git apply --check` passes, and the PATCHED module is imported and shown to answer identically to the cell on 10 cases. (9) PAIRED BOOTSTRAP, 2000 resamples, clustered by SENTENCE for the detector and by ITEM for the consumer, on each item's own population."
files_changed: "experiments/exp_passive_cue_clause_local_v1.py (the cell; self-test 25/25), notes/problems/<slug>/{SOLVED.md, passive_cue_patch.diff, byhead_twin_repair.diff}, data/hook_state/passive_voice_counts_v1.json (the plastic cue-validity counts -- opt-in, re-derivable by --run), data/hook_state/coarse_role_validities_pri111_{shipped,patched}_perceived_w_v4.json (phase 7 Q2, NOT proposed for landing; the live asset was never written), and the cell's own data/exp_passive_cue_clause_local_v1/*.json. NO hdlab/ or tools/ file changed on disk. The diff touches hdlab/thematic_role_labeler.py (the organ block + a deprecation note on is_passive_clause), hdlab/graded_role_assigner.py (the import + ALL FOUR call sites) hdlab/relcl_resolver.py (phase 7b: `precise_passive` folded to a delegate), hdlab/arc_labeler.py (phase 7b: VOICE_CORRECTION / _BE_AUX / label_voice_correct DELETED, `voice_correction=` kept accepted-and-ignored so no caller churns), and experiments/exp_board_agent_slot_ud_v1.py, whose duplicate `hybrid_agent_pick` is RETIRED to a thin call to the organ (phase 7 Q1 -- without that hunk the board number does not move). FIVE files; there are no call sites in tools/ (enumerated). Two of the three files are CRLF: apply with `git apply --ignore-whitespace`."
reverify: ".venv/Scripts/python.exe experiments/exp_passive_cue_clause_local_v1.py --self-test   (33 checks, seconds; includes PATCH == CELL, git apply --check, the patched-module parity check, the shipped witness's voice assertions under the patched cue, and -- phase 7b -- a COMPILE of every patched file from the patched text plus assertions that the three deletions and the delegate are really there). Headline numbers, each writing ONLY into its own data/exp_passive_cue_clause_local_v1/ directory: --run (~10 min -> metrics.json + detector.json + override.json + call_sites.json); --push (~1 min -> push.json); --board-dim (~6 min -> board_dimension.json, the board's own row under three arms); --extra (~12 min -> extra.json: the criterion sweep, the heads contrast, the upstream category loss, call site 2); --gum (~8 min -> gum.json, the two held-out golds). PHASE 7: --detectors (~12 min -> detectors.json: the six-detector inventory, the patient board row under D2, the byhead gate under D4, the arc-labeler count under D5); --reaccrue both (~18 min -> two NEW tables under data/hook_state/, the live asset never written); --labels (~1 min -> labels.json, the labels rung under all four table x cue combinations); --fold (~9 min -> fold.json, every consumer of D2/D4/D5 with the fold OFF and ON); --witnesses (~10 min -> witnesses.json, the nine shipped witnesses run twice each, in process, hdlab/ never written); --repair (~12 min -> d4_repair.json, the D4 repair on the byhead witness's own three slices + the board row + the UD gate-firing count); --d2-check (~9 min -> d2_check.json, D2's construction-population check: the detector per item, the patient board under three forms, and the two relcl witnesses); --emit-twin-patch (instant -> byhead_twin_repair.diff). NOTE (2026-09-14 16:10): strategy LANDED the 5-file diff, so `passive_cue_patch.diff` now carries only what is still OUTSTANDING against the tree -- the single D4 repair hunk in hdlab/graded_role_assigner.py. Also: .venv/Scripts/python.exe verification/test_coarse_role_competition.py (37/37, unmodified)."
---

# SOLVED -- the auxiliary is the cue, the suffix is not, and the cue belongs to ONE predicate

**Status: SOLVED (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed on disk; the exact diff is
`passive_cue_patch.diff` in this folder, generated FROM the cell's own organ block (`--emit-patch`), and the
cell's self-test asserts the diff's added lines are byte-identical to the code that was measured.

---

## 1. The bar, restated in my own words

The system decides who did what by keeping the high-validity word-order default ("the first thing named is
the doer") and letting a MARKED cue overturn it. One of those marked cues is "this clause is passive". The
detector that answers that question looks at the WHOLE sentence. So a passive anywhere -- in a relative
clause, in a coordinate clause, in an adjectival participle -- tells every predicate in the sentence that it
is passive. The bar is: make the cue read the clause of the predicate being decided; show the false fires on
gold-ACTIVE clauses collapse without losing recall on real passives; show the override stops breaking more
than it fixes; move every consumer to the ONE detector; break nothing else; and show a same-rate random
"passive" twin at the floor.

## 2. The chain this cue sits in, and the brain-foundational status of each rung AS THE DISK SHOWS IT

`notes/bf_status_registry.jsonl` + each module's `__bf_status__`, read first-hand, and the live frontend
(`hdlab.frontend.describe()` -> `categories=counts heads=attachment_arm`).

| rung | organ | BF status on disk | what it hands DOWN | what the voice cue READS |
|---|---|---|---|---|
| tokens -> categories | `hdlab/lexical_categories.py` | BF_SPIRIT (live default) | a full category POSTERIOR per token | **the argmax only** -- the cue asks "is this token VERB / AUX / ADV" |
| categories -> lemma | `hdlab/morphology.py` | **BF** (0 divergences vs morphy over 6.3M) | the lemma | **nothing** -- the cue never needed it (section 6.3) |
| categories -> heads | `hdlab/attachment_arm.py` | BF_SPIRIT (live default) | a single-root tree + `P(head\|dep)` marginals | the aux->predicate ARC, as CONFIRMATION only |
| voice cue | `hdlab/thematic_role_labeler.py::is_passive_clause` | BF_SPIRIT (module) -- **the cue itself was NOT**: a sentence-wide window search | ONE boolean for the sentence | -- |
| roles / agent | `hdlab/graded_role_assigner.py` | BF_SPIRIT | the coarse role posterior; the agent pick | the boolean, at four call sites |
| the board | `experiments/exp_board_agent_slot_ud_v1.py` | the measuring arm | `who_did_what_agent` | its OWN copy of the hybrid and of the cue |

## 3. How the brain does this -- and the one thing the shipped detector had backwards

**The structure.** Voice is a cue of the Competition Model (Bates & MacWhinney 1989; MacWhinney, Bates &
Kliegl 1984). A cue is evaluated FOR THE PREDICATE whose arguments are being assigned, it enters at its
VALIDITY (availability x reliability), and English is order-dominant so only a HIGH-validity marked cue may
overturn word order. The clause is the unit: argument assignment is clause-bounded (Fodor & Bever 1965
click-displacement; Frazier & Fodor 1978's two-stage packager). The passive itself is a stored CONSTRUCTION
(Goldberg 1995) whose form side is `[NP be/get V-en (by NP)]`, realised on ONE predicate by ONE auxiliary
chain. Comprehenders use voice morphology EARLY as an actor/undergoer cue (Bornkessel-Schlesewsky &
Schlesewsky 2006/2009, eADM -- the citation the substrate already uses for `arc_labeler.label_voice_correct`).

**THE KEY REALIZATION, and it is an ordering fact about the evidence.** The shipped detector searches the
sentence for a PARTICIPLE and treats a nearby `be` as confirmation. The brain cannot work that way, because
the participial suffix is *not* evidence: English `-ed` is systematically ambiguous between the simple past
and the participle. That ambiguity is the entire reason the reduced-relative garden path exists ("the horse
raced past the barn fell" -- Bever 1970; Trueswell, Tanenhaus & Garnsey 1994). What carries the cue is the
AUXILIARY, which is heard FIRST and opens a passive expectation for the predicate it attaches to
(incremental interpretation, Marslen-Wilson 1973; anticipatory use of the verb/auxiliary, Altmann & Kamide
1999). The very next non-adverbial word then CONFIRMS the expectation (a participial main verb) or CANCELS
it (a determiner -> the auxiliary was a copula; an infinitival `to` -> a new predicate opens; `-ing` -> the
construction is PROGRESSIVE, i.e. active). **So the operation is an unbroken LEFT CHAIN from the predicate,
not a window search over the sentence** -- and the by-phrase, when it arrives, is confirmation of the
demoted agent rather than a requirement.

That single re-ordering is what the whole result is made of. It also explains, without any list, three
things the shipped detector had to hand-enumerate and still got wrong: it needs no irregular-participle
table (the `-ing` test alone separates progressive from passive under a `be`), it needs no window parameter
(the chain terminates itself), and it cannot leak across clauses (a determiner, a nominal or a preposition
is exactly what a clause boundary puts between two predicates).

**Graded, never frozen.** Additive cue activation -> logistic IS the Bayesian posterior for cue integration
(McClelland 2013), so the deployable form of the cue is `P(passive | cue values)` read off COUNTS, with one
`observe_voice_outcome` call per understood predicate. That is built, accrued and measured (section 5.4).

## 4. What was built

One organ block, in `hdlab/thematic_role_labeler.py` (the module the brief names as the single home of this
cue), reading only tokens + categories + optionally the reader's own heads:

| function | what it computes |
|---|---|
| `voice_cue_value(toks, pos, v, heads)` | the cue VALUE at predicate `v`: `be_arc` / `be_chain` / `get_arc` / `get_chain` / `be_inv` / `conj` / `prog` / `none` / `na` |
| `morph_value` / `by_value` / `degree_value` | the three secondary cue values: participial morphology (`ing`/`ed`/`en`/`other`), the clause-local by-phrase, and the adjectival-passive degree modifier (Wasow 1977) |
| `voice_posterior(..., counts)` | `P(passive \| the four cue values)`, Dirichlet-smoothed to the aux-value marginal and then to the base rate (the shrinkage IS the backoff) |
| `observe_voice_outcome` / `load_voice_counts` / `save_voice_counts` | the online path: one count per understood predicate; the asset is `data/hook_state/passive_voice_counts_v1.json` |
| `is_passive_predicate(toks, pos, v, heads, counts, theta)` | the boolean the four call sites need. `counts=None` (the shipped default) = the construction read; with counts = the graded read at a criterion |

Five auxiliary-chain facts are what make it work, each a cancellation the brain performs and the shipped
detector did not: an infinitival `to` stops the chain; a determiner or nominal stops the chain; `-ing` under
a `be` is progressive, not passive; a fronted participle may take its finite auxiliary to the RIGHT
("Attached is a spreadsheet"); and a bare conjunct shares the first conjunct's auxiliary across the
coordinator ("the artworks were selected and EXHIBITED").

## 5. The numbers

### 5.1 The detector itself -- UD-EWT test, per predicate, through the LIVE brain-foundational chain

Population: every gold-VERB predicate in UD-EWT test, **n = 2605 in 1240 sentences**, 126 gold passive
(`aux:pass`/`nsubj:pass`/`csubj:pass`) and 136 under the propagated gold (a bare CONJUNCT of a passive
predicate; UD annotates the shared auxiliary once, and the second conjunct of "were selected and exhibited"
IS passive for every consumer of this cue). Categories from `lexical_categories`, heads from
`attachment_arm` -- no gold at decision time. Paired bootstrap over SENTENCES, 2000 resamples, on the
per-predicate voice DECISION.

| arm | fires | precision | recall | F1 | accuracy | accuracy vs the shipped floor |
|---|---|---|---|---|---|---|
| **FLOOR -- shipped whole-sentence `is_passive_clause`** | 296 | **0.3784** | 0.8235 | 0.5185 | 0.9202 | -- |
| shipped detector scoped to the clause span (what `agent_override_fires` does today) | 214 | 0.4860 | 0.7647 | 0.5943 | 0.9455 | +0.0253 CI95[+0.0158,+0.0365] **sep** |
| `relcl_resolver.precise_passive` (already predicate-anchored) | 112 | 0.9464 | 0.7794 | 0.8548 | 0.9862 | +0.0660 CI95[+0.0503,+0.0830] **sep** |
| **NEW -- `is_passive_predicate` (construction read)** | 127 | **0.9606** | **0.8971** | **0.9278** | **0.9927** | **+0.0726 CI95[+0.0566,+0.0892] sep** |
| NEW -- graded read at theta 0.5 | 125 | 0.9600 | 0.8824 | 0.9195 | 0.9919 | +0.0718 CI95[+0.0560,+0.0885] sep |
| NEW -- without the coordination cue | 121 | 0.9669 | 0.8603 | 0.9105 | 0.9912 | +0.0710 CI95[+0.0547,+0.0878] sep |
| **TWIN -- a random equal-size set of predicates declared passive** | 130 | 0.0462 | 0.0441 | 0.0451 | 0.9025 | **-0.0177 CI95[-0.0341,-0.0004] sep BELOW** |

**Precision 0.3784 -> 0.9606 with recall UP 0.8235 -> 0.8971.** Head to head against the shipped cue on the
same 2605 predicates: **200 fixes, 11 breaks.** On the raw (unpropagated) gold the new read is
0.9213 / 0.9286 and the no-coordination variant 0.9669 / 0.9286, i.e. the conclusion does not depend on
which of the two golds is used.

> **CHAIN-STATE NOTE, and it is a robustness datum rather than a caveat.** Another session landed pri 110's
> `PREDICATE_SLOT` revision into `hdlab/lexical_categories.py` + `hdlab/attachment_arm.py` at 13:10 local,
> in the middle of this session. **Every number in this record was therefore re-measured from scratch on the
> POST-13:10 chain, all arms together**, and the detector table above is byte-identical to the pre-13:10
> measurement (same precision, recall, F1, accuracy, fixes/breaks and cue-value counts). What the upstream
> landing did change is visible and in the right direction: the predicates the category organ does not call
> VERB, where this cue must abstain, fell from **212 to 132 of 2605**, and the coarse-role consumer's
> absolute accuracy rose (0.6940 -> 0.6986 shipped, section 5.5). The consumer deltas are quoted from the
> post-13:10 run.

### 5.2 The cue's own validity, learned from counts (UD-EWT train, live chain, 22,576 predicates)

This is the Competition Model's own quantity, and it is the reason the licence was breaking things.

| cue value | n | P(passive) |
|---|---|---|
| `be_arc` (a BE auxiliary the reader's parse attached to this predicate, reached by an unbroken chain) | 1280 | **0.9656** |
| `be_inv` (fronted participle + postposed finite be) | 22 | 1.0000 |
| `get_arc` / `get_chain` (the get-passive) | 20 / 17 | 0.9500 / 0.8824 |
| `be_chain` (chain reached, arc says otherwise) | 7 | 0.8571 |
| `conj` (a bare conjunct sharing the auxiliary) | 45 | 0.6222 |
| `none` | 16609 | 0.0059 |
| `prog` (`be` + `-ing`) | 2947 | 0.0003 |
| *(the shipped whole-sentence read, same population)* | *296 fires on test* | ***0.3784*** |

The Competition Model says a cue enters at its validity. The auxiliary-attachment cue has validity **0.966**
and the sentence-wide search has **0.378**; that ratio is the whole problem, stated in the theory's own terms.

### 5.3 The consumer -- the board's who-did-what AGENT decision (UD-EWT test, n = 1423)

Every arm is the SAME hybrid (word-order default, Competition-Model competition on a marked cue) with ONE
thing changed: which voice read licenses the passive cue. Floor = the positional pick the board itself uses.
Paired item bootstrap, 2000 resamples.

| arm | accuracy | vs the positional floor 0.8468 | vs the landed board model 0.8271 |
|---|---|---|---|
| **positional floor** (nearest pre-verbal candidate, no override of any kind) | **0.8468** | -- | -- |
| the hybrid with the passive licence REMOVED (pp_gov + noncase only) | 0.8475 | +0.0007 n.s. | +0.0204 sep |
| **landed: whole-sentence licence (what the board scores today)** | **0.8271** | **-0.0197 CI95[-0.0309,-0.0091] sep BELOW** | -- |
| clause-scoped licence | 0.8320 | -0.0148 CI95[-0.0246,-0.0049] sep BELOW | +0.0049 sep |
| clause-scoped + by-phrase required | 0.8468 | +0.0000 n.s. | +0.0197 sep |
| **NEW predicate-anchored licence (the board hunk of the diff)** | **0.8475** | **+0.0007 CI95[-0.0070,+0.0084] n.s.** | **+0.0204 CI95[+0.0126,+0.0281] sep** |
| NEW + by-phrase required | 0.8482 | +0.0014 CI95[-0.0063,+0.0091] n.s. | +0.0211 sep |
| NEW graded read | 0.8475 / 0.8482 | +0.0007 / +0.0014 n.s. | +0.0204 / +0.0211 sep |
| **the ORGAN `hdlab.hybrid_agent_pick` with the diff in** (call sites 2 AND 3, as shipped) | **0.8552** | **+0.0084 CI95[+0.0007,+0.0162] CI-SEP** | **+0.0281 CI95[+0.0190,+0.0379] sep** |
| TWIN -- the passive licence fires on a random equal-size set | 0.8468 | +0.0000 -- **exactly the floor** | +0.0197 sep |

*(The "hybrid with the passive licence removed" row exists so the passive cue's own contribution is not
confounded with the other two marked cues: `pp_gov` and `noncase` together are worth +0.0007 on their own,
and the corrected passive licence adds +0.0007 on top of that. Against the LANDED model every arm is
CI-separated up -- including the twin -- which is why the floor, not the landed model, is the comparison
that decides anything here.)*

**THE OVERRIDE ANATOMY -- the brief's own instrument.** Decisions where the PASSIVE cue ALONE licenses the
override (no `pp_gov`, no `noncase`):

| voice read | n | fixes | breaks | neutral | fired on a gold-ACTIVE clause | conflict validity |
|---|---|---|---|---|---|---|
| **landed whole-sentence** | 92 | **1** | **30** | 61 | **83** | **0.032** |
| clause-scoped | 57 | 1 | 23 | 33 | 48 | 0.042 |
| clause-scoped + by required (the ORGAN today) | 12 | 1 | 2 | 9 | 3 | 0.333 |
| **NEW predicate-anchored** | 14 | 1 | 1 | 12 | **3** | 0.500 |
| **NEW + by required (what the diff ships in the organ)** | **11** | **1** | **0** | 10 | **0** | **1.000** |
| NEW graded + by required | 11 | 1 | 0 | 10 | 0 | 1.000 |

*(pri 106 reported this partition restricted to the decisions where the override actually CHANGED the pick:
n=43, fixes 1, breaks 30, neutral 12, gold-active 33. My `fixes 1 / breaks 30` reproduce it exactly; my
larger `n` and `gold-active` counts every licence firing, changed or not. Same population, wider window.)*

**The bar's own numbers: gold-active false fires 83/92 -> 0/11; fixes 1 > breaks 0; recall on true passives
UP, not down; twin at the floor.**

### 5.4 The plastic arm

`data/hook_state/passive_voice_counts_v1.json`: 41 cue configurations, 22,576 predicates accrued on UD-EWT
train through the live chain, base rate 0.0680, Dirichlet alpha swept (4.0). The graded read scores
0.9603 / 0.8897 against the construction read's 0.9606 / 0.8971 -- **statistically the same organ** (127 vs
126 fires). It earns its keep in exactly one place, and the counts say where: the coordination cue splits
into `conj|ed` = 21/29 = 0.72 and `conj|other` = 3/11 = 0.27, so the graded read fires on the first and
abstains on the second, which the boolean cannot do.

**SHIPPED DEFAULT = the construction read (`counts=None`), deliberately.** `data/` is gitignored, so an
organ whose default depends on an uncommitted asset would silently become a DIFFERENT organ on any machine
that lacks it -- the precise hazard the hard rules name. The counts are therefore the opt-in plastic arm,
re-derivable by `--run`, with `observe_voice_outcome` as the online path. **On the bigger held-out corpus
the graded read does win** (GUM F1 0.9020 vs 0.8983, precision 0.9622 vs 0.9503 -- section 8), so a consumer
that has the asset should pass it; the default is a shipping decision, not a claim that the boolean is
better.

### 5.5 No-regress on the other consumers

| consumer | population | shipped | patched | delta |
|---|---|---|---|---|
| **call site 1** -- `coarse_role_cues` `voice_order` (UD-EWT test 700, live heads, the shipped v4 validity table UNCHANGED) | all labelled arguments, n=2216 | 0.6986 | 0.6999 | +0.0014 CI95[0.0000,+0.0031] n.s. |
| | core arguments, n=1205 | 0.7477 | 0.7502 | +0.0025 CI95[0.0000,+0.0059] n.s. |
| | gold `nsubj:pass`, n=48 | 0.5417 | 0.5417 | 0.0000 |
| | gold `obl:agent`, n=19 | 0.6316 | 0.6316 | 0.0000 |
| **call site 2** -- `agent_supports`, the voice FLIP of every candidate's preverbal/byagent support; scored as the competition's own pick on the agent population | UD-EWT test, n=1422 | 0.7511 | **0.7637** | **+0.0127 CI95[+0.0070,+0.0197] CI-SEPARATED UP** |
| **call site 3** -- `agent_override_fires` | see 5.3 | -- | -- | the licence: 92 firings / 83 gold-active -> 11 / 0 |
| **call site 4** -- `agent_override_licensed`'s `want` class | (reads the same cue; changes which role class the calibrated probability is taken over) | -- | -- | moved to the one detector in the diff; no independent population |

Call site 2 is the second consumer up CI-separated, and it is the one the *reader* uses on every sentence
(`situation_reader` -> `agent_competition_pick_conf` -> `agent_supports`): the whole-sentence boolean was
switching off the preverbal support and switching on the by-phrase support for EVERY candidate of EVERY
predicate in any sentence that contained a passive anywhere.

Call site 1 had a real risk of regressing and it is worth saying why it did not: the `voice_order` cue VALUE is
a key into a validity table that was accrued with the OLD detector, so changing the detector changes which
counts a decision reads. It does not regress because the change is almost entirely a reduction in
`passive_weak_*` false firings, and `passive_weak` is the low-validity value the table already distrusts.
**The table was NOT re-accrued** -- the number above is the honest as-if-landed-today number; re-accruing it
with the corrected cue is a named follow-on (section 11).

*(Call site 1 also carried a latent defect the diff fixes: `is_passive_clause(toks, pos, h)` passed the head
INDEX `h` into the function's `window` parameter, so the search widened with the predicate's position in the
sentence. It fires 293 times against the nominal call's 294 on UD-EWT test -- near-identical, which is why
it never showed up as a bug, and wrong for a different reason than the one this brief is about.)*

## 6. THE STATUS PROBE -- where the signal is lost, chain by chain, with counts

*"How are we performing against the brain, and where do we lose signal upstream? Are all upstream components
brain-foundational?"*

### 6.1 The signal the end read needs, in one sentence per consumer

| end consumer | its one-sentence signal requirement |
|---|---|
| the agent decision (`hybrid_agent_pick`) | "for THIS predicate, is the surface subject the undergoer, so that the agent is somewhere else?" |
| the coarse role labeler (`coarse_role_cues`) | "for the head governing THIS nominal, is the clause passive, so that a pre-verbal nominal is `nsubj:pass` and a by-NP is `obl:agent`?" |
| `agent_supports` | "for THIS predicate, should the preverbal support be switched off and the by-phrase support switched on?" |
| `agent_override_licensed` | "for THIS predicate, is the role class we should be scoring `BY_AGENT` or `SUBJ`?" |

**Every one of the four is about ONE predicate. All four were being answered about the SENTENCE.** That is
the loss, and it is total in the sense that matters: the answer was not degraded, it was about a different
question.

### 6.2 Hand-off by hand-off: produced / read / LOST

| hand-off | what is PRODUCED | what the next rung READ | LOST |
|---|---|---|---|
| category organ -> voice cue | a per-token category POSTERIOR | the argmax category of the predicate and of the chain tokens | the posterior. **Counted: 212 of 2605 predicates are not tagged VERB by the category organ, and the cue returns `na` for every one of them** (section 6.4) |
| attachment arm -> voice cue | a tree + `P(head\|dep)` | (before) nothing at all; (now) the aux->predicate arc as confirmation | **Counted: the arc confirms 111 of 113 firings (`be_arc` 111 vs `be_chain` 2) and changes ZERO decisions** -- the surface chain and the arc agree, so the arc is currently a free confirmation, not a source of signal |
| voice cue -> the four consumers | one SENTENCE boolean | a per-PREDICATE question | **the predicate identity.** Counted: 296 sentence-level firings vs 127 predicate-level firings on 2605 predicates; 184 of the 296 are false on the propagated gold |
| voice cue -> agent override | the boolean | the licence | **Counted: 92 licences, 83 on gold-ACTIVE clauses, 30 broken decisions, 1 fixed** |
| agent override -> the pick | the marked-cue licence | the competition's pick | see 6.5 -- the NEXT rung is where the remaining loss is |

### 6.3 Brain-foundational status of each upstream component AS IT RELATES TO THIS SIGNAL

- **`lexical_categories` (BF_SPIRIT, live default).** Hands down a graded posterior; the voice cue takes a
  point estimate. That is a REAL graded->hard hand-off, and it is the cue's largest remaining loss (6.4).
- **`attachment_arm` (BF_SPIRIT, live default).** Hands down a posterior; the cue reads the MAP arc only, and
  only as confirmation. Measured to change nothing today, so this is a hand-off that is currently lossless
  *because the surface chain already carries the same information* -- not because the cue uses the posterior.
- **`morphology` (BF).** Not on this path at all, and that is the right answer, not an omission: the brain
  does not identify the passive from the participle's morphology (section 3), so a lemma/participle lookup is
  not a missing input. The shipped `_is_participle` hand-list (`_PARTICIPLE_IRREGULAR`, ~60 forms) is
  therefore a SUPPLY the corrected cue does not need at all -- it is replaced by the `-ing` test.
- **`thematic_role_labeler::is_passive_clause` -- NOT brain-foundational as a cue** (a sentence-wide window
  search answering a predicate-level question), inside a module the registry calls BF_SPIRIT. That is the
  defect this brief names, and it is now fixed at the computation, not papered over downstream.

### 6.4 The one upstream loss that is still open, counted -- and it is NOT what the brief predicted

The cue can only fire on a token the category organ calls a VERB. **132 of the 2605 predicates get `na`**
(the organ tagged them something else). Of the 136 gold passives, **exactly 3 are lost that way, and all
three are the same thing**:

```
are probably especially oriented toward the      [oriented = ADJ]
, I was surprised to hear                        [surprised = ADJ]
have never been disappointed .                   [disappointed = ADJ]
```

*(Measured BEFORE pri 110's `PREDICATE_SLOT` landed at 13:10 this number was 4 of 136, and 212 predicates got
`na`; the fourth was `have` tagged AUX. **pri 110's upstream landing fixed it and removed 80 of the 212
abstentions** -- a clean instance of an upstream brain-foundational repair paying off at a downstream cue
that was measured on both sides of it.)*

**The adjectival-participle residual the brief's checklist item 4 predicted did not materialise where it was
expected.** Of the 5 remaining false fires on UD-EWT test, **ZERO carry a degree modifier** -- the
adjectival-passive precision problem does not exist at this rung, because `was tired` / `is interested` /
`especially oriented` never reach the cue at all: the CATEGORY organ tags them ADJ one rung earlier. The
adjectival/verbal passive distinction has therefore moved UP the chain and changed sign: it is a RECALL loss
in the category organ (3 items), not a PRECISION loss in the voice cue (0 items). I built the degree-modifier
cue anyway (it is a cue VALUE in the counts: `none|other|none|deg` = 0/105 passive, `none|ed|none|deg` =
0/31) and it is measured to be inert at this rung -- an honest null, kept because it is free and because it
will matter the moment the category organ stops absorbing the distinction.



### 6.5 What the reader's own heads actually contribute -- counted, and it is zero decisions

The brief asks for the auxiliary chain "attached to h", with `_cached_parse_heads` available. Built and
measured: under live heads the cue value is `be_arc` (the parse attached that auxiliary to this predicate)
**111** times against `be_chain` (chain reached, arc disagrees or absent) **2** times -- and the number of
DECISIONS the arc changes is **0 of 2605**. The surface chain and the attachment arm agree on essentially
every auxiliary. So the arc is retained as a cue VALUE (it separates a 0.966-validity configuration from a
0.857-validity one in the counts) but the organ does not depend on it, which is why the diff does not widen
`agent_supports`'s signature to thread heads through: it would be a signature change buying zero decisions,
and an un-passed argument at a builder call site is exactly how an organ silently ships different.

### 6.5 The research: how the brain handles this signal mathematically, chain by chain down

- **At the cue.** Cue validity = availability x reliability (Bates & MacWhinney 1989). Availability of the
  auxiliary cue is the fraction of passives that carry an auxiliary; reliability is P(passive | the cue
  fired). Measured on UD-EWT train through the live chain: availability (recall) 0.897, reliability 0.966.
  The sentence-wide read has the same availability and reliability 0.378. **The theory's own quantity
  separates the two reads by a factor of 2.6, and predicts exactly the observed damage** -- a cue whose
  reliability is 0.38 must not be allowed to overturn a cue (word order) whose reliability on this
  population is 0.85.
- **At the integration.** Ernst & Banks 2002 / Fetsch et al. 2011 / Ma et al. 2006: a consumer weights each
  input by its reliability, trial by trial. The graded form (`voice_posterior`) is that weighting made
  explicit, and the counts show it matters exactly where the cue's reliability is intermediate (`conj` 0.62).
- **At the decision.** McClelland 2013: additive cue activation -> softmax IS the Bayesian product. The
  organ's `net_activation` already does this; what it needed was a cue VALUE that is about the right object.
- **One rung further down** (section 7): Wolff/Talmy is not the relevant theory here; the relevant one is
  CASE. Once voice says "the agent is elsewhere", the by-phrase is the case marker of the demoted agent
  (Bates & MacWhinney's case-marking cue, high-validity where present). The substrate already has that cue
  (`byhead`/`by_governs`, landed 2026-09-06) and the board's copy of the hybrid was not passing it.

## 7. THE QUALITY PUSH -- the cue is fixed, so where does the signal go next?

The passive licence can only ever touch the gold-PASSIVE items of the agent population, and there are
**16 of 1423** (UD's `obl:agent` by-phrases; agentless passives have no agent to recover and are excluded by
the board's own gold recipe). So the arithmetic bound on this entire lever at this consumer is 16 items =
0.0112. I therefore traced the signal one rung DOWN, on that subpopulation.

| arm (gold-passive subpopulation, n=16) | accuracy | vs floor |
|---|---|---|
| positional floor (word order) | **0.0000** | -- |
| the board arm's competition -- `agent_competition_pick` with `byhead_agent_cue` **FALSE** (its default; the board arm never passes it) | 0.1875 | +0.1875 n.s. |
| the SAME competition with `byhead_agent_cue` **TRUE** (what `hdlab.hybrid_agent_pick` passes) | 0.5000 | +0.5000 CI95[+0.2500,+0.7500] **sep** |
| the board arm's hybrid as landed | 0.1875 | +0.1875 n.s. |
| the board arm's hybrid with the pri-111 voice read | 0.1875 | +0.1875 n.s. |
| **the ORGAN `hdlab.hybrid_agent_pick`** (requires the by-phrase, passes `byhead`) | **0.5625** | **+0.5625 CI95[+0.3125,+0.8125] sep** |
| the same organ with the pri-111 voice read | 0.5625 | +0.5625 sep |
| ORACLE -- pick the candidate governed by `by` (the ceiling the case cue could reach) | 0.7500 | +0.7500 sep |

**The finding, and it is independent of this brief's cue.** The board's `who_did_what_agent` dimension does
not call the organ; it calls its own older copy, and that copy loses **5 of the 16 passive agents purely by
not passing `byhead_agent_cue=True`**. The by-phrase CASE cue is landed (2026-09-06), it is default-ON in
`hdlab.hybrid_agent_pick`, and the board has never seen it. On the full population:

| | full n=1423 | active-only n=1407 | gold-passive n=16 |
|---|---|---|---|
| positional floor | 0.8468 | 0.8564 | 0.0000 |
| board arm as landed | 0.8271 (-0.0197 sep BELOW) | 0.8344 (-0.0220 sep BELOW) | 0.1875 |
| board arm + pri-111 voice | 0.8475 (+0.0007 n.s.) | 0.8550 (-0.0014 n.s.) | 0.1875 |
| the ORGAN | 0.8510 (+0.0042 n.s.) | 0.8543 (-0.0021 n.s.) | 0.5625 |
| **the ORGAN + pri-111 voice (both call sites, as shipped)** | **0.8552 (+0.0084 CI95[+0.0007,+0.0162] CI-SEP)** | **0.8579 (+0.0014, no regress)** | **0.6250** |

Two things are worth saying plainly. First, **the cue fix inside the ORGAN is worth 3 items (+0.0021,
CI95[0.0000,+0.0049], not separated)** -- because the organ already required a by-phrase, which was masking
most of the whole-sentence false fires. Second, **the cue fix inside the BOARD ARM is worth +0.0204
CI95[+0.0126,+0.0281], CI-separated**, because the board arm has no by-requirement and was taking all 30
breaks. The 30 broken decisions the brief was opened on live in the board arm's copy, not in the organ.
Retiring that copy in favour of the organ is +0.0239 CI95[+0.0155,+0.0323] on its own, and +0.0281
CI95[+0.0190,+0.0379] with the cue fix at both call sites (section 17.3 decomposes it one difference at a time).

The corrected cue's recall AT THIS CONSUMER is **16/16**: it fires on every gold-passive item in the agent
population. The remaining 7 of 16 that the organ still misses are not a voice-cue problem -- the oracle
by-governed pick gets 12 of 16, so 4 more items are reachable by the case cue alone and 4 are not reachable
by either. That is a bounded, named hand-off to the agent competition's weights, not to this cue.

## 8. GENERALIZE -- two more modern golds the counts never saw

The counts were accrued on UD-EWT TRAIN only. GUM (275 files, multi-genre modern) and GENTLE (26 files, the
deliberately out-of-domain companion -- dictionary entries, esports commentary, legal text) are held out
entirely, and GUM is **11x the size of the UD-EWT test population**. Same live chain, same instrument,
paired bootstrap over sentence clusters, 2000 resamples.

| arm | GUM: 29,217 predicates, 2131 gold passive | | | | GENTLE (OOD): 1653 predicates, 120 gold passive | | | |
|---|---|---|---|---|---|---|---|---|
| | P | R | F1 | acc vs floor | P | R | F1 | acc vs floor |
| FLOOR -- shipped whole-sentence | 0.3643 | 0.8123 | 0.5030 | -- | 0.4596 | 0.9000 | 0.6085 | -- |
| `precise_passive` | 0.9321 | 0.7982 | 0.8600 | +0.0981 sep | 0.9397 | 0.9083 | 0.9237 | +0.0732 sep |
| **NEW construction read** | **0.9503** | **0.8517** | **0.8983** | **+0.1030 CI[+0.0994,+0.1068] sep** | **0.9821** | **0.9167** | **0.9483** | **+0.0768 CI[+0.0629,+0.0895] sep** |
| NEW graded read | 0.9622 | 0.8489 | **0.9020** | +0.1036 sep | 0.9909 | 0.9083 | 0.9478 | +0.0768 sep |
| NEW without the coordination cue | 0.9622 | 0.8367 | 0.8951 | +0.1028 sep | 1.0000 | 0.9000 | 0.9474 | +0.0768 sep |
| **TWIN** | 0.0664 | 0.0610 | 0.0636 | **-0.0139 sep BELOW** | 0.0678 | 0.0667 | 0.0672 | **-0.0502 sep BELOW** |

The result transfers: precision 0.36 -> 0.95 on GUM and 0.46 -> 0.98 on the OOD split, with recall up on
both, the twin CI-separated below the floor on both, and the new read beating `precise_passive` (the
strongest existing predicate-anchored detector) on precision AND recall on every population.

**And on the bigger held-out corpus the GRADED read earns its keep**: GUM F1 0.9020 vs the construction
read's 0.8983 (precision 0.9622 vs 0.9503). So a consumer that has the counts asset should pass it; the
shipped default stays the construction read for the reason in 5.4 (the asset is gitignored, and an organ
whose default silently changes with an absent file is the hazard the hard rules name).

## 9. The board's own row

Computed by the board's own function `exp_board_agent_slot_ud_v1.board_agent_dimension` (its own
sentence-cluster bootstrap, its own floor, its own twin), run three times with only `hybrid_agent_pick`
swapped. This is the `who_did_what_agent` row, not a re-implementation of it.

| arm | model | floor | twin | model - floor | passive slice (n=16) |
|---|---|---|---|---|---|
| **landed (today's board)** | **0.8271** | 0.8468 | 0.2853 | **-0.0197 CI[-0.0317,-0.0090]** | 0.1875 |
| **+ pri-111 voice read (call sites 2 + 3 + the board hunk)** | **0.8489** | 0.8468 | 0.2853 | **+0.0021 CI[-0.0057,+0.0094]** | 0.2500 |
| **+ the board arm's duplicate RETIRED (thin call to the organ)** | **0.8552** | 0.8468 | 0.2853 | **+0.0084 CI[+0.0007,+0.0157] CI-SEP** | **0.6250** |

The board's agent dimension is **not down**: with the duplicate retired it is **CI-separated ABOVE its own
positional floor for the first time**, and the passive slice goes from 3/16 to 10/16. *(Updated 2026-09-14
14:20 -- the first version of this table was measured with call site 2 (`agent_supports`) left SHIPPED, which
under-counted the diff by 0.0021 on the row and by 1 item on the passive slice. Section 17.6 says how I found
that and what it cost.)*

## 10. Every negative, researched until it is understood -- with the mechanism and the number

**N1. The reader's own heads change ZERO decisions (2605/2605 identical).** Not a failure of the arc; a fact
about English. An auxiliary is adjacent to its predicate modulo adverbs, so the surface chain and the MAP
arc carry the same information. The arc is kept as a cue VALUE (it separates validity 0.966 from 0.857 in
the counts) and the organ is built not to depend on it -- which is also why the diff does not widen
`agent_supports`'s signature.

**N2. Reading COORDINATION off the heads instead of the coordinator: 34 false fires against the surface
read's 12 (gold heads, UD-EWT test).** Mechanism, not noise: an arc says "v depends on h"; it never says
"this is coordination". A head-based inheritance therefore also inherits voice across `xcomp` / `ccomp` /
`advcl` -- "he was told to LEAVE" makes `leave` passive, "another sign IS that ... have BEGUN joining" makes
`begun` passive (the copula's head is the clausal predicate). Built, measured, discarded; the surface
coordinator is the cue, and it is also the incremental one.

**N3. On UD-EWT test the GRADED read does not beat the construction read (F1 0.9195 vs 0.9278) -- though on the 11x-larger held-out GUM it does (0.9020 vs 0.8983).** Understood by looking at
the counts: 7 of the 9 cue values have validity above 0.85 or below 0.01, so the posterior is SATURATED and
a criterion anywhere in [0.15, 0.65] reproduces the boolean. The train criterion sweep confirms it -- F1
0.9345 / 0.9345 / 0.9345 / **0.9366** / 0.9362 / 0.9304 / 0.9237 at theta 0.15 / 0.25 / 0.35 / **0.50** /
0.65 / 0.75 / 0.85, a flat plateau with the best at 0.50 (selected on TRAIN, applied unchanged to test). The
graded form's value is therefore NOT accuracy; it is (a) plasticity, (b) the one place it can act that the
boolean cannot (`conj|ed` 0.72 vs `conj|other` 0.27), and (c) handing a GRADED number down instead of a
boolean, which is the standing discipline.

**N4. "An aux-less `V-ed` with a by-phrase is a reduced passive" -- REFUTED with counts: 7/193 = 0.036 on
UD-EWT train.** This was my own best candidate for recovering the remaining false negatives and it is wrong
on this gold, for a reason worth recording: UD does not mark a participial MODIFIER as passive ("a book
written by him" is `acl`, no `aux:pass`). So the configuration genuinely is not the target here -- and for
the consumer it should not be, because a participial modifier is a different construction from the finite
clause whose agent is being decided. The recall plateau at ~0.90 is therefore partly a gold-convention
boundary, and I have NOT tuned against it.

**N5. The brief's predicted adjectival-participle residual is ZERO at this rung** (0 of the 5 remaining
false fires carry a degree modifier). It has moved one rung UP and changed sign: the category organ tags
`oriented` / `surprised` / `disappointed` as ADJ, so they never reach the cue, and the distinction costs 3
items of RECALL rather than any precision. The degree-modifier cue was built anyway and is measured inert
(`none|*|none|deg` = 0/136 passive on train) -- kept because it is free and becomes live the moment the
category organ stops absorbing the distinction.

**N6. Inside the ORGAN the cue fix is worth 3 items (+0.0021, CI95[0.0000,+0.0049], NOT separated).** The
organ already required a by-phrase, and that requirement was masking 80 of the 92 false licences. The 30
broken decisions the brief was opened on live in the BOARD ARM's copy of the hybrid, which has no
by-requirement -- and there the same one-line change is +0.0204 CI-separated. Stating this plainly matters:
the brief's headline damage was in a duplicate of the organ, not in the organ.

**N7. The by-governed ORACLE is BELOW the floor on the full population (0.8391 vs 0.8468, -0.0077).** Because
`by` occurs in active clauses ("by the way", "by 2010"). This is the mechanical reason the case cue must be
voice-gated (`participle_bypp_gate`, `byhead` self-gating) and a direct confirmation that voice is the
upstream cue the case cue depends on -- exactly the chain this brief repairs.

**N8. Always-competing (`cm_byhead`, no hybrid) is 0.7547 against the 0.8468 floor, -0.0921 CI-separated
BELOW.** This reproduces the landed 2026-09-06 register finding and is the reason the hybrid exists: on
modern canonical prose word order is near-ceiling, so a cue that always fires loses. The byhead case cue is
worth +0.31 on the passive slice and -0.10 on the whole population; it is only usable INSIDE a marked-cue
branch. That is the Competition Model's own prescription and it is measured here twice.

**N9. THE OOD SPLIT FOUND A REAL FALSE-FIRE CLASS, AND MY FIRST EXPLANATION OF IT WAS WRONG.** On GENTLE
(the deliberately out-of-domain GUM companion) the first build's precision fell to 0.8397 against
`precise_passive`'s 0.9397 -- the only population in this record where the shipped-quality floor beat it. My
hypothesis was the clitic `'s` / `'re`, which is genuinely ambiguous between BE and HAVE ("he's finished" =
perfect OR passive), and an ablation that dropped contracted auxiliaries from the inventory appeared to
confirm it (+0.22 precision on a 4-file sample). **COUNTING the false fires by cue value instead of
narrating them showed the real cause: 19 of the 21 were `gon na`** -- "gonna" tokenized as two tokens, so
the host `gon` is not an `-ing` form and `is gon na start` reads as `[be + participle]`. The contraction
ablation had "worked" only because it removed `'m gon na` / `'re gon na` as a side effect. *Count, don't
narrate* -- the move that broke this one.
**The fix is the brain's, not a patch:** `na` and `ta` occur in English only as the reduced infinitival
marker of `going to` / `got to` / `want to`, and no passive participle is ever followed by one -- so a
predicate whose NEXT token is `na`/`ta` is the host of a reduced semi-modal (a future/modal periphrasis),
which is the same cancellation as the `-ing` test one position to the right. Cue value `semimodal`; it
appears 1 time in UD-EWT test (so it changes nothing there) and removes 19 of the 21 GENTLE false fires.
Section 8 has the re-measured numbers.

## 11. Components interacted with, and their brain-foundational status

| component | touched how | BF status | note |
|---|---|---|---|
| `hdlab/thematic_role_labeler.py::is_passive_clause` | **deprecated in place** (kept, documented, callers moved) | was NOT BF as a cue | a sentence-wide window search answering a predicate-level question; per-predicate precision 0.3784 |
| `hdlab/thematic_role_labeler.py` -- NEW `voice_cue_value` / `voice_posterior` / `is_passive_predicate` / `observe_voice_outcome` | **added** (the organ block) | **BF**: Competition-Model cue, predicate-anchored, clause-local, incremental left chain, graded from counts with an online observe path | pinned operation (cue validity), swept parameters (criterion, chain-crossable categories) |
| `hdlab/thematic_role_labeler.py::_is_participle` + `_PARTICIPLE_IRREGULAR` | **not used by the new cue** | a hand-authored SUPPLY | the corrected cue needs no participle list at all -- the `-ing` test under an auxiliary replaces it |
| `hdlab/graded_role_assigner.py` -- 4 call sites | **repointed** | BF_SPIRIT | call site 1 also had `h` passed into the `window` parameter (latent) |
| `hdlab/graded_role_assigner.py::voice_cues` / `robust_passive` / `participle_bypp_gate` | read, measured, **left alone** | BF_SPIRIT | predicate-anchored already; `robust_passive` scores P 0.2656 per predicate and should not be used as a decision (it is a RECALL arm by design) |
| `hdlab/relcl_resolver.py::precise_passive` | measured as a floor | BF_SPIRIT | already predicate-anchored: P 0.9464 / R 0.7794. The new cue dominates it on both |
| `hdlab/arc_labeler.py::label_voice_correct` | read, **not touched** | BF_SPIRIT | a FIFTH voice detector: arc-based aux child + `.endswith(("ed","en"))` |
| `hdlab/lexical_categories.py` | consumed (live default) | BF_SPIRIT | hands down a posterior; the cue reads the argmax. 4 of 136 gold passives lost here |
| `hdlab/attachment_arm.py` | consumed (live default) | BF_SPIRIT | hands down a posterior; the cue reads the MAP arc, as confirmation only, changing 0 decisions |
| `hdlab/morphology.py` | deliberately NOT consumed | BF | the brain does not read voice off the participle's morphology; see section 3 |
| `experiments/exp_board_agent_slot_ud_v1.py::hybrid_agent_pick` | measured, one-line hunk in the diff | the measuring arm | a duplicate of the organ, missing the by-requirement AND the `byhead` case cue |

## 12. AUDIT UPDATE for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`

**ONE BRAIN STRUCTURE, SIX IMPLEMENTATIONS.** English voice perception is currently computed in six places
in `hdlab/`, each with a different operation and a different answer:

| # | where | operation | per-predicate precision on UD-EWT test |
|---|---|---|---|
| 1 | `thematic_role_labeler.is_passive_clause` | sentence-wide window-3 search | 0.3784 |
| 2 | `relcl_resolver.precise_passive` | BE within 3 left + participle suffix | 0.9464 |
| 3 | `graded_role_assigner.voice_cues` / `robust_passive` | union of 5 predicate-anchored cues (recall arm) | 0.2656 (union), 0.8760 (strong/get/being) |
| 4 | `graded_role_assigner.participle_bypp_gate` | participle + a by-governed NP anywhere | (a construction gate, not a voice read) |
| 5 | `arc_labeler.label_voice_correct` | aux CHILD of the head + `ed`/`en` suffix | (labels, not measured here) |
| 6 | `predicate_argument_frontend` | delegates to #2 | -- |

This brief ships #1 corrected and repoints its four call sites. **The consolidation to ONE organ with arms
(#2, #3, #5 folded into `voice_cue_value`) is a named follow-on, not done here**, because #3 and #5 have
live consumers with their own witnesses and folding them is a strategy-side landing. The relevant audit line
is that the voice cue is a cue VALUE of the ONE Competition-Model organ and should have ONE computation.

## 13. Evaluation of the most successful improvement -- which chain was cracked, rung by rung

The biggest single number is **precision 0.3784 -> 0.9606 with recall UP**, and the reason it was available
is the owner's usual one: the mathematically brain-foundational chain was cracked to the TOP of this cue.
Rung by rung, what was cracked and what was not:

| rung | cracked? | what it took |
|---|---|---|
| **the QUESTION the cue answers** | **YES** | "is this SENTENCE passive" -> "is THIS PREDICATE passive". Everything else follows from this one substitution; nothing downstream had to change. |
| **the EVIDENCE ORDER** | **YES -- this is the load-bearing one** | the brain does not read voice off the participial suffix, because `-ed` is ambiguous (that ambiguity IS the reduced-relative garden path). It reads it off the AUXILIARY, heard first, confirmed or cancelled by the next word. Inverting the search direction removed the need for a participle list, a window parameter, and a clause-boundary heuristic all at once. |
| **the CANCELLATION set** | **YES** | a determiner, a nominal, an infinitival `to` and `-ing` each cancel the passive expectation. These are not heuristics: each is the point at which the brain's expectation is disconfirmed. |
| **the CUE VALIDITY** | **YES** | measured from counts, in the theory's own currency: 0.966 for the auxiliary cue vs 0.378 for the sentence search. That single ratio explains the 30 broken decisions without any appeal to the consumer. |
| **the CLAUSE unit** | **YES, and by construction rather than by a boundary list** | the AUXILIARY read is clause-local because the chain cannot cross a determiner, a nominal, a preposition or an infinitival `to` -- which is what a clause boundary puts between two predicates. It therefore does NOT depend on `clause_bounds`, and that matters: `clause_bounds` deliberately does not treat relativizers as boundaries (the main-clause subject precedes them), which is exactly why the clause-scoped floor still fires on 48 gold-active clauses. `clause_bounds` is still used for the by-phrase scan and the inversion check, where a span genuinely is needed. |
| **the CATEGORY rung above** | **NO** | the cue still takes the argmax of a posterior. 4 of 136 gold passives are lost there, 3 of them the adjectival/verbal participle distinction. |
| **the CONSUMER rung below** | **NO** | once voice is right, the competition still has to pick the by-NP; it gets 9 of 16 where the oracle case cue gets 12. |
| **the DUPLICATES** | **NO** | six implementations of one structure remain (section 12). |

## 14. ALTERNATE PATHS -- other ways to do this read that are as or MORE brain-foundational

**A. Voice as a running EXPECTATION in the incremental pass, not a per-predicate query.** *Structure:*
eADM stage 1/2 (Bornkessel-Schlesewsky & Schlesewsky) + Marslen-Wilson's incrementality. *Computation:* one
left-to-right pass maintains a `voice_expectation` that the auxiliary raises, adverbs carry, and the next
non-adverbial word consumes or cancels -- so the cue is available AT WORD t, not on demand. *What it would
take:* an array alongside `hdlab.incremental_parser.incremental_subject_before`, and a check that it equals
my per-predicate read (it should: my chain never looks right except for `be_inv`). *Why not now:* an
expected null on accuracy; the gain is fidelity to the owner's "organs take data in order" discipline and
the ability to use voice DURING the parse rather than after it. **This is the one I would build next.**

**B. Voice as a CONFIGURATION value of the one role competition, not a separate cue.** *Structure:*
Construction Grammar (Goldberg 1995) -- the passive is a stored form-meaning pairing, and in the Competition
Model a construction is the CONFIGURATION within which validities are read. The substrate already does this
for the existential (`cfgkey + "_ex"` in `coarse_role_cues`). *Computation:* add `_pass` to the
configuration key and let the validity table learn the passive configuration's whole role distribution
directly, instead of a boolean feeding a `voice_order` value. *What it would take:* re-accruing
`coarse_role_validities` (a `tools/` builder). *Why not now:* it changes the cue alphabet and the asset, so
it is a strategy-side landing, and it should be done in the same pass as the re-accrual noted in 5.5.

**C. INDUCE the auxiliary inventory instead of listing it.** *Structure:* Gleitman's syntactic bootstrapping
+ closed-class acquisition from distribution; the substrate has `closed_class_lexicon` and the category
organ's AUX counts. *Computation:* "which AUX-tagged tokens precede a non-`-ing` VERB and predict an
undergoer subject?" -- induced, not authored. *What it would take:* an induction pass over the AUX counts.
*Why not now:* `_BE_FORMS`/`_GET_FORMS` is a genuinely closed class and the recall it would add
(`become`/`remain`/`seem` passives) is ~0 items on UD-EWT test. Worth doing for fidelity, not for the number.

**D. Marginalise the cue value over the CATEGORY posterior.** *Structure:* Ma, Beck, Latham & Pouget 2006 --
the population's gain IS its precision, so the consumer should integrate over the distribution, not the
argmax. *Computation:* `P(passive) = sum over category assignments of P(passive | cats) P(cats)`. *Bound,
measured:* 4 of 136 gold passives are lost to the argmax, so the ceiling is +0.029 recall. *Why not now:*
pri 103 already measured that marginalising the ROLE read over the HEAD posterior LOSES (0.7224 -> 0.6952)
because that posterior is broad and mis-centred; the category posterior may behave differently, but this
must be measured, not assumed.

**E. Let the affected ENTITY feed back.** *Structure:* the situation model's state register already knows
which entity has been changed. If a clause's surface subject is already a tracked undergoer, that is
top-down evidence for passive voice. *Why not now:* it inverts the dependency this brief just repaired and
would need the recurrent loop (`close_the_recurrent_predictive_coding_loop...`) to be live first.

## 15. Priority next steps (for strategy)

1. **Land the diff.** Three files; `git apply --ignore-whitespace` (two of the three are CRLF).
2. **Retire the board arm's copy of the hybrid and call the organ** -- worth +0.0239 CI95[+0.0155,+0.0323]
   on the agent dimension on its own, independently of this brief, because the copy does not pass
   `byhead_agent_cue=True` and loses 5 of the 16 passive agents to a cue that has been landed since
   2026-09-06. This is the largest number in this record and it is a landed-not-live defect.
3. **Re-accrue `coarse_role_validities` with the corrected `voice_order` cue** (section 5.5): the table was
   fitted with the old detector, and the +0.0014 / +0.0025 measured above is the as-if-landed-today number,
   not the number after the table learns the corrected cue.
4. **Consolidate the six voice detectors to one organ with arms** (section 12).
5. **The category organ's adjectival/verbal participle boundary** (3 items here; it is also the
   `nsubj:pass` recall story) -- and the `have`-as-AUX convention, which is pri 110's.
6. **The agent competition's by-NP pick**: 9 of 16 against an oracle 12 of 16 on the passive slice.

## KEY REALIZATIONS -- the enabling moves, not the result

1. **THE EVIDENCE RUNS THE OTHER WAY ROUND.** The shipped detector searched for a PARTICIPLE and treated a
   nearby `be` as confirmation. The brain cannot, because `-ed` is ambiguous -- that ambiguity IS the
   reduced-relative garden path. The auxiliary is the evidence and the participle is the confirmation.
   Inverting the search direction removed the need for a participle list, a window parameter and a
   clause-boundary heuristic simultaneously; the detector got SHORTER and much better.
2. **A CANCELLATION IS A MECHANISM, NOT A HEURISTIC.** Every place the chain stops -- a determiner, a
   nominal, an infinitival `to`, an `-ing` suffix, a reduced `na`/`ta` -- is a point at which the listener's
   passive expectation is disconfirmed by the next word. Writing them as cancellations rather than as
   exceptions is what made them generalise to two held-out corpora.
3. **MEASURE THE CUE IN THE THEORY'S OWN CURRENCY.** Computing cue VALIDITY from counts (0.966 for the
   auxiliary cue, 0.378 for the sentence search) explained the 30 broken decisions without touching the
   consumer, and predicted in advance which arms would and would not move.
4. **COUNT THE FALSE FIRES, DO NOT NARRATE THEM.** My explanation of the OOD precision drop (the ambiguous
   clitic `'s`) was wrong, and an ablation appeared to confirm it. Counting false fires BY CUE VALUE showed
   19 of 21 were `gon na`. The ablation had "worked" by accident.
5. **AFTER FIXING A CUE, PRICE IT AT ITS CONSUMER BEFORE CLAIMING THE WIN.** The passive licence can only
   touch 16 of 1423 agent decisions -- the whole lever is bounded by arithmetic at 0.0112 -- and tracing one
   rung further down found a bigger, unrelated defect (a landed case cue the board has never seen).
6. **GENERATE THE PATCH FROM THE MEASURED CODE.** `--emit-patch` splices the cell's own organ block into the
   target files and the self-test asserts byte-identity, so "the arm that was measured is the arm that would
   ship" is a check, not a promise.

## 16. What I would withdraw first if it turned out to be wrong

The **coordination inheritance cue** (`conj`). It is the only part of the detector that reasons about a
predicate other than the one being decided, it rests on a propagated gold rather than the raw UD annotation,
and it is worth exactly 5 items of recall (0.8603 -> 0.8971) at a precision cost of 0.0063. Everything else
-- the auxiliary chain, the cancellations, the `-ing` test, the inversion case -- is measured on the raw
gold as well and does not depend on the propagation. `is_passive_predicate(..., use_conj=False)` turns it
off and scores P 0.9669 / R 0.8603.

The **second** thing I would withdraw is the claim that the graded read is better than the construction
read. It is not; it is the same organ with a plastic arm, and I have said so with the numbers.

---

# 17. PHASE 7 (strategy probe, 2026-09-14 13:50) -- every number understood, and the three consumers built

## 17.1 (1a) THE 11 BREAKS, each named, with the construction and the rung

"Breaks" = the decisions where the SHIPPED whole-sentence cue was right and the new predicate-anchored cue
is wrong, head to head on UD-EWT test (against the propagated gold; the shipped cue has 200 the other way).
All eleven, with the cue value the organ produced and the category organ's posterior where the rung is the
tagger:

| # | context | cue value | tag | gold | THE RUNG |
|---|---|---|---|---|---|
| 1 | They are probably especially **[oriented]** toward the Salafi school | `na` | ADJ | passive | **category organ** -- posterior ADJ 0.950 / VERB 0.050 |
| 2 | that Irish , I was **[surprised]** to hear | `na` | ADJ | passive | **category organ** -- ADJ 0.517 / VERB 0.481 (a near tie) |
| 3 | I have never been **[disappointed]** . | `na` | ADJ | passive | **category organ** -- ADJ 0.745 / VERB 0.244 |
| 4 | beef is revered , respected , and **[praised]** . | `none` | VERB | passive | **detector -- coordination depth**: the cue walks left to the coordinator and looks for ONE verb before it; here it finds `respected`, which itself carries no auxiliary (it is the second member of a three-member list). The rule is not transitive. |
| 5 | be taken care of and **[loved]** by a professional staff | `none` | VERB | passive | **detector -- coordination blocked**: walking left from `loved` the scan hits `of` (ADP) before reaching the first conjunct `taken`, and an ADP stops it. |
| 6 | Indian - administered Kashmir and **[belonged]** to the outlawed Lashkar | `none` | VERB | (passive) | **MY OWN propagated gold is wrong here** -- `belonged to` is active; the propagation inherited voice from the `administered` conjunct. On the RAW UD gold this is not a break. |
| 7 | arm and a leg and **[have]** to wait forever . | `none` | VERB | (passive) | **same gold-propagation artifact** (`have to wait` is active; inherited from `charged`). |
| 8 | I think that he 's **[got]** class tonite | `be_arc` | VERB | active | **detector -- the `'s` clitic**: `'s` is ambiguous between `is` and `has`; here it is the perfect `has got`, which takes a direct object. |
| 9 | I thought my name was **[shut]** up . | `be_arc` | VERB | active | **gold convention** -- `was shut up` reads as a passive; UD does not mark it `aux:pass` here. |
| 10 | All you can do is **[take]** each section | `be_arc` | VERB | active | **detector -- pseudo-cleft**: `[what you can do] is [take X]`, a specificational copula with a bare-infinitive complement. |
| 11 | We got **[upgraded]** to a corner suite | `get_arc` | VERB | active | **gold convention** -- a real get-passive that UD does not mark `aux:pass`. |

**The account, in counts: 3 category organ / 2 my own gold propagation / 2 UD convention (the cue is
arguably right) / 4 detector (2 coordination-depth, 1 clitic, 1 pseudo-cleft).** Only **four** of the eleven
are the detector's own chain-walk rule, and all four are named constructions rather than noise. Dropping the
coordination cue removes breaks 4 and 5 and costs 5 items of recall (section 16); the clitic and the
pseudo-cleft are each 1 item and both need the same missing evidence -- **does the participle have a direct
object of its own** (a perfect/specificational reading) -- which is the verb-frame rung, not this cue.

**The 5 remaining FALSE FIRES** are items 8, 9, 10, 11 plus `Attached are clean and **[blacklined]** drafts`
(cue `conj`: the coordination cue inherits across an ADJ conjunct, `clean and blacklined`). **ZERO carry a
degree modifier**, which is the measurement that relocated the brief's predicted adjectival residual to the
category organ (section 6.4).

## 17.2 (1b) THE 16 GOLD-PASSIVE AGENTS: which 3 the oracle gets and the organ does not, and at which rung

The organ gets 9/16 (0.5625), the by-governed oracle 12/16 (0.7500). Every one of the 16 is enumerated in
`data/exp_passive_cue_clause_local_v1/` and the probe output; the voice cue fires on **16/16** and the
by-phrase gate on 15/16, so the loss is entirely BELOW this cue. The three the oracle gets and the organ
does not:

| item | organ picks | gold | rung |
|---|---|---|---|
| `... it being followed by a **Vikash** Chand Abdul Shakur .` | `Chand` | `Vikash` | **NP-head inside the by-phrase**: a flat multi-token NAME. UD heads a `flat` name on its FIRST token; the competition has no cue for which token of a name is its head, so it picks by its other cues. |
| `... groups are being " picked up " by **al** - Qaeda .` | `Qaeda` | `al` | **same** -- a hyphenated name, headed on the first token. |
| `an airplane carrying Winston Peters was **blown** up by a **bomb**` | `Peters` | `bomb` | **`participle_bypp_gate`'s suffix list**: `_is_participle("blown")` is FALSE (`blown` is not in `_PARTICIPLE_IRREGULAR`), so the gate did not fire and the byhead CASE cue was never emitted -- the positional pre-verbal name won. **This is the same defect this brief fixes, in a fifth detector** (see 17.5, D4). |

**And the four that NEITHER gets** -- `by an extremist **form** of the Wahhabi school`, `by my better
**half**`, `by Gravity CEO **Kim** Jung-Ryool`, `by two space **businessmen**` -- are all the same missing
computation: **the head of the by-NP**. English common-noun NPs are right-headed (`space businessmen` ->
`businessmen`) while flat names are left-headed (`Vikash Chand` -> `Vikash`), and the competition has no cue
for either. **BUILT AND MEASURED: a naive right-headed rule with a name exception (`oracle_by_nphead`: the
first PROPN of the by-NP if there is one, else the LAST noun) scores 0.7500 on the slice -- exactly the same
12/16 as `first by-governed`, and -0.0063 on the full population.** So the residual 4 are not reachable by a
positional head rule at all; they need real NP-head parsing, which is the attachment arm's job. **Bounded and
handed over, not guessed at.**

## 17.3 (1c) WHY 3 ITEMS INSIDE THE ORGAN AND +0.0204 IN THE DUPLICATE -- the exact code difference

`experiments/exp_board_agent_slot_ud_v1.py:134` and `hdlab/graded_role_assigner.py:1881` were two
implementations of one route. **Four differences; two of them live at default:**

| | the board arm's copy | the organ | live? |
|---|---|---|---|
| **(A) voice scope** | `is_passive_clause(toks, up)` -- the WHOLE SENTENCE, no clause scope, no by-phrase | `agent_override_fires`: `is_passive_clause(toks[lo:hi], pos[lo:hi])` **and** a `by` inside the clause | **YES** |
| **(B) the by-phrase CASE cue** | `agent_competition_pick(...)` with `byhead_agent_cue` **omitted -> False** | `byhead_agent_cue=True` is the organ's default | **YES** |
| (C) construction cues | absent | `construction=` (existential / first-conjunct), opt-in, default OFF | no |
| (D) the pri-106 confidence gate | absent | `heads=` -> `agent_override_licensed`, opt-in, default OFF | no |
| (E) candidate list | positional base from `cands`, competition over the case-filtered `cm_cands` | ONE list for both (what `situation_reader` passes) | -- |

**The decomposition, measured one difference at a time** (UD-EWT test n=1423, floor 0.8468):

| arm | full | active-only (n=1407) | gold-passive (n=16) | step |
|---|---|---|---|---|
| board arm as landed | 0.8271 | 0.8344 | 0.1875 | -- |
| + (A) the corrected voice read | 0.8475 | 0.8550 | 0.1875 | **+0.0204 CI95[+0.0126,+0.0281] sep** |
| + (B) `byhead_agent_cue=True` | 0.8503 | 0.8543 | **0.5000** | +0.0028 full, **+0.3125 on the passive slice** |
| + (A'') the by-phrase requirement | 0.8510 | 0.8550 | 0.5000 | +0.0007 |
| = the ORGAN with the diff in (E too) | **0.8531** | **0.8564** | **0.5625** | +0.0021 |

**So the answer is: the two hybrids fail differently.** (A) is worth +0.0204 in the duplicate because the
duplicate takes ALL 30 broken decisions -- it has no by-phrase requirement, so its passive licence fires 92
times. The organ's licence already required a by-phrase, which was masking 80 of those 92, so inside the
organ the same fix moves only 3 items (+0.0021, not separated). Conversely (B) is worth nothing in the organ
(it already passes it) and +0.3125 on the passive slice in the duplicate. **Neither implementation was
strictly better; each was missing what the other had, which is exactly the cost of having two.**

## 17.4 (Q1) THE DUPLICATE IS RETIRED -- the board's own row after the retirement

`experiments/exp_board_agent_slot_ud_v1.hybrid_agent_pick` becomes a thin call to
`hdlab.graded_role_assigner.hybrid_agent_pick` (the hunk is in `passive_cue_patch.diff`). The row below is
computed by the board's OWN `board_agent_dimension` -- its own sentence-cluster bootstrap, its own floor,
its own shuffled-supports twin -- with only that function swapped:

| arm | model | floor | twin | model - floor | passive slice n=16 | active slice n=1407 |
|---|---|---|---|---|---|---|
| **landed (today's board)** | **0.8271** | 0.8468 | 0.2853 | **-0.0197 CI[-0.0317,-0.0090]** | 0.1875 | 0.8344 |
| + the pri-111 voice read only (all its call sites) | 0.8489 | 0.8468 | 0.2853 | +0.0021 CI[-0.0057,+0.0094] | 0.2500 | 0.8550 |
| **+ the duplicate RETIRED (thin call to the organ)** | **0.8552** | 0.8468 | 0.2853 | **+0.0084 CI[+0.0007,+0.0157] CI-SEP** | **0.6250** | **0.8579** |

The board's `who_did_what_agent` row goes from **CI-separated BELOW its own floor** to **CI-separated ABOVE
it**, the passive slice goes 3/16 -> 10/16, and the active slice is +0.0014 above its own floor rather than
-0.0220 below it. Retirement alone (independent of the voice fix) is +0.0239 CI95[+0.0155,+0.0323] on the
paired item bootstrap; with the voice fix it is +0.0281 CI95[+0.0190,+0.0379].


*(The 17.4 table above was first written from a run in which call site 2 was left SHIPPED -- see 17.6. The
corrected figures are: voice read only **0.8489** (+0.0021, passive slice 0.2500); duplicate retired
**0.8552**, **+0.0084 CI[+0.0007,+0.0157] -- CI-SEPARATED ABOVE the floor**, passive slice **0.6250**,
active slice 0.8579 against a 0.8564 floor. The row is no longer merely "not below" its floor; it is above
it, separated.)*

## 17.5 (Q3) THE SIX VOICE DETECTORS, their consumers, and what each is worth with the ONE organ in

| # | detector | file:line | consumers | measured with the ONE organ substituted | verdict |
|---|---|---|---|---|---|
| **D1** | `is_passive_clause` | `hdlab/thematic_role_labeler.py:428` | `graded_role_assigner.py:659` (coarse_role_cues), `:1584` (agent_supports), `:1765` (agent_override_fires), `:1874` (agent_override_licensed), `exp_board_agent_slot_ud_v1.py:149` | this brief: detector P 0.3784 -> 0.9606; agent row 0.8271 -> 0.8552; labels +0.0014 n.s.; `agent_supports` +0.0127 CI-sep | **FOLDED HERE** (all 5 call sites in the diff) |
| **D2** | `precise_passive` | `hdlab/relcl_resolver.py:58` | `relcl_resolver.py:72` two_line_patient, `:134` resolve_patient, `graded_role_assigner.py:197` hybrid_role_patient, `predicate_argument_frontend.py:454,710`, `situation_reader.py:2294` (patient confidence), `exp_valency_labeled_patient_v1.py:229` = **the BOARD's patient arm** | the board's own `board_patient_dimension`: model **0.8120 -> 0.8135**, floor 0.7203 unchanged, twin 0.6430/0.6454, model-floor +0.0916 CI[+0.0708,+0.1114] -> **+0.0932 CI[+0.0721,+0.1137]**, both CI-separated; ceiling (gold parse) unchanged | **FOLDABLE NOW** -- +0.0015 (~2 items), no regress anywhere, and the organ dominates it on P AND R on all three corpora. Small, so it is a tidy-up, not a win |
| **D3** | `voice_cues` / `robust_passive` | `hdlab/graded_role_assigner.py:78` / `:99` | `:658` coarse_role_cues (the `strong` half), `:154` cue_supports (`passive_strong` / `passive_weak`), `verb_subcat.py:95`, `situation_reader.py:1549`, and **`exp_valency_labeled_patient_v1.py:69` -- the DEPLOYED FLOOR** | NOT substituted, deliberately: `robust_passive` is the voice of the patient arm's own FLOOR (`_deployed_structural_patient_pick`), and changing a floor is not a measurement. Per-predicate P/R measured for the record: `robust_passive` 0.2656/0.8810, `voice_cues` strong-get-being 0.8760/0.8413, against the organ's 0.9606/0.8971 | **NEEDS ITS OWN BRIEF.** Folding it changes the cue VALUES `DEFAULT_VALIDITIES` was fitted to (`passive_strong` 3.2317, `passive_weak` -2.9927), so it requires a refit of those validities and a re-measure of `hybrid_role_patient` -- a labels-rung job, not a cue job |
| **D4** | `participle_bypp_gate` | `hdlab/graded_role_assigner.py:1473` | `:1754` agent_supports -- the gate on the byhead by-phrase CASE cue | with the organ's voice in place of the `_is_participle` suffix test: the gate's firing rate **HALVES, 32 -> 16 of 1423** (it now fires only where the predicate really is passive) and the agent row goes **0.8552 -> 0.8559**; the gold-passive slice is unchanged at 0.6250 | **FOLDABLE NOW**, and it is the same defect: `_is_participle("blown")` is False, which is why the `by a bomb` item in 17.2 was lost. +0.0007 (1 item) and a 2x precision gain on the gate |
| **D5** | `label_voice_correct` | `hdlab/arc_labeler.py:59` | `ArcLabeler.label()` with `VOICE_CORRECTION=True` -> every label consumer | **counted on UD-EWT test 700: it changes 25 labels with the competition OFF and ZERO labels with `COMPETITION_ROLES` live** | **RETIRE, do not fold.** It is DEAD CODE on the live path -- the Competition-Model organ (landed 2026-09-12) already decides every label it would change. Retiring it is a no-op by measurement, which is the cleanest possible case for deleting a duplicate |
| **D6** | `predicate_argument_frontend` | `hdlab/predicate_argument_frontend.py:454,710` | -- | delegates to D2; not an independent computation | follows D2 |

**So: two can be folded now on numbers (D2, D4), one is already dead and should simply be deleted (D5), and
one needs its own brief because folding it invalidates a fitted validity table (D3).** I have NOT put D2, D4
or D5 in this diff: each touches an `hdlab/` file outside the four call sites this brief names, and D5 in
particular is a deletion that deserves its own witness. They are handed to strategy with the numbers above.

## 17.6 (Q2) RE-ACCRUING THE VALIDITY TABLE -- BUILT, AND IT IS NOT PRI 111'S NUMBER

Two tables were rebuilt with the builder's OWN math (`tools/build_coarse_role_validities.py` imported and
reused, never edited, never written over: its `OUT` constant was redirected into `data/hook_state/` and the
same flags the live v4 table carries -- `--perceived --weight --v4`, `min_conf 0.5`, `m_config_backoff 0.0`
-- were used). **TWO**, because a single re-accrual would confound my cue with pri 110's upstream landing at
13:10: one with the SHIPPED cue and one with the CORRECTED cue, both on today's chain.

| population (UD-EWT test 700, live heads) | live table + shipped cue | live table + corrected cue | **re-accrued SHIPPED-cue table** | **re-accrued CORRECTED-cue table** |
|---|---|---|---|---|
| all labelled nominals, n=2216 | 0.6986 | 0.6999 (+0.0014 n.s.) | 0.7004 (+0.0018 n.s.) | 0.7004 (+0.0018 n.s.) |
| core arguments, n=1205 | 0.7477 | 0.7502 (+0.0025 n.s.) | 0.7535 (+0.0058 n.s.) | 0.7535 (+0.0058 n.s.) |
| active `nsubj`, n=721 | 0.7698 | 0.7712 | 0.7725 | 0.7739 |
| `obj`, n=400 | 0.7400 | 0.7450 | **0.7550 (+0.0150 CI[+0.0025,+0.0297] SEP)** | 0.7525 (+0.0125 n.s.) |
| **`nsubj:pass`, n=48** | **0.5417** | **0.5417** | **0.5417** | **0.5417** |
| **`obl:agent`, n=19** | 0.6316 | 0.6316 | **0.5263 (-0.1053, 2 items)** | **0.5263 (-0.1053, 2 items)** |

**THE ANSWER: the landing number does NOT need a re-accrued table, and the counterfactual proves it.** The
only CI-separated movement (`obj` +0.0150) appears in the **SHIPPED-cue** re-accrual too -- it is pri 110's
upstream landing being learned, not my cue. The 2-item `obl:agent` cost likewise appears under both re-accrued
tables. On the corrected-cue table my cue is worth +0.0000 on `all_nominals` and `core` against the
shipped-cue table built the same day. **So section 5.5's +0.0014 / +0.0025 against the LIVE table is the
right landing number**, and re-accruing the table is pri 110's follow-on, not pri 111's. The two assets are
on disk (`data/hook_state/coarse_role_validities_pri111_{shipped,patched}_perceived_w_v4.json`) for whoever
picks that up; **neither is proposed for landing and the live asset was never written.**

**AND THE MECHANISM FOR THE NULL, COUNTED.** Of 3698 argument heads on UD-EWT test 700, **133 (3.6%) change
their `voice_order` value**: 120 are `passive_weak_* -> active_*` (the false-fire correction) and 13 are
`active_* -> passive_weak_*` (the recall gain). The swap is not small in the table -- the mean max
|strength difference| across the 8 roles is **3.59 nats**. But look at WHICH nominals move: gold `nsubj` 33,
`obl` 22, `obj` 21, `nmod` 16, `xcomp` 7 ... and **`nsubj:pass` 5, `obl:agent` 0**. *The nominals whose voice
cue changes are overwhelmingly not the passive-class ones.* They are ordinary arguments in sentences that
merely CONTAINED a passive somewhere -- which is precisely the defect -- and at the MAP their corrected cue
helps about as often as it hurts. **That is why the labels rung is flat and the AGENT decision is not: the
agent route uses voice as a LICENCE (a gate that fires or does not), where a false fire costs a whole
decision; the labels rung uses it as one graded contrast among nine, where a wrong contrast is usually
outvoted.** Same cue, two consumers, and the consumer's ARCHITECTURE decides what the fix is worth.

## 17.7 A FIDELITY DEFECT IN MY OWN PHASE-6 MEASUREMENT, FOUND AND CORRECTED

While building the Q3 substitution harness I found that **every agent-consumer number in sections 5.3, 7 and
9 had been measured with call site 2 (`agent_supports`, line 1584) left SHIPPED** -- I had patched only the
override (call site 3), so the competition inside the override was still flipping every candidate's
preverbal/byagent support on the whole-sentence boolean. The diff patches both. Re-measured with **both**
call sites installed (a context manager that binds `is_passive_clause` to the predicate-anchored answer for
the duration of the `agent_supports` call -- exact, because line 1584 is that name's only use inside the
function, so there is no copy of the body to drift):

| | measured in phase 6 (call site 2 shipped) | **as the diff actually ships** |
|---|---|---|
| organ hybrid, full n=1423 | 0.8531 (+0.0063, n.s.) | **0.8552 (+0.0084 CI[+0.0007,+0.0162] CI-SEP)** |
| organ hybrid, gold-passive n=16 | 0.5625 | **0.6250** |
| organ hybrid, active-only n=1407 | 0.8564 (= floor) | **0.8579 (+0.0014 above floor)** |
| the board's own row | 0.8531 (+0.0063, n.s.) | **0.8552 (+0.0084, CI-SEP above its floor)** |
| vs the landed board arm | +0.0260 | **+0.0281 CI[+0.0190,+0.0379]** |

**I had under-reported my own result, and the corrected number crosses the line the earlier one did not: the
board's agent row is now CI-SEPARATED ABOVE its own positional floor.** Recorded here rather than silently
corrected upstream, because the lesson is the one the hard rules state: *the arm that is measured must be
the arm that would ship*, and a diff with five call sites needs all five installed in the harness. The
detector numbers (section 5.1), the GUM/GENTLE transfer (section 8), the anatomy (5.3) and the labels rung
(5.5, 17.6) are unaffected -- none of them runs through `agent_supports`.

## 17.8 EXHAUSTED OR NOT

**Not exhausted, and I can name exactly what is left and what it is worth.** What IS exhausted at this rung:

- the DETECTOR itself. 5 false fires and 14 misses on UD-EWT test, every one named and attributed in 17.1;
  4 of the 11 head-to-head breaks are the detector's own rule and each is a named construction with a known
  cost (coordination depth 2 items and worth 5 items of recall; the `'s` clitic 1; the pseudo-cleft 1). The
  criterion is on a flat plateau (F1 0.9345-0.9366 over theta 0.15-0.65). Precision 0.96-0.98 on three
  corpora with recall up. There is no configuration of this cue left to sweep.
- the AGENT consumer. The whole lever is bounded by arithmetic at 16 items; the cue now fires on 16/16 and
  the organ converts 10 of them against a floor of 0. The remaining 6 are BELOW this cue (17.2).
- the LABELS consumer. Flat, with the mechanism counted (17.6): only 5 of the 133 changed nominals are
  gold `nsubj:pass`.

What is NOT exhausted, with the number and the owner:

1. **The by-NP's head** (17.2) -- 6 of 16 passive agents, and a positional head rule is measured NOT to
   reach 4 of them. Owner: the attachment arm / the entity layer. **The biggest remaining item on this row.**
2. **D3, `voice_cues` / `robust_passive`** (17.5) -- needs a refit of `DEFAULT_VALIDITIES`; its own brief.
3. **D5, `label_voice_correct`** -- dead code, delete it (0 live label changes).
4. **The category organ's participle/adjective boundary** -- 3 items of recall here, posteriors 0.95 / 0.52 /
   0.75 ADJ (17.1). The 0.52 one is a near tie a graded read would take.
5. **Re-accruing the validity table on the post-13:10 chain** -- `obj` +0.0150 CI-sep, `obl:agent` -2 items.
   **pri 110's follow-on, not this brief's** (17.6).
6. **The clitic `'s` and the pseudo-cleft** (1 item each) -- both need the same missing evidence, *does the
   participle take a direct object of its own*, which is the verb-frame rung.


---

# 18. PHASE 7b (strategy, 2026-09-14 14:30) -- D2 and D4 folded, D5 deleted, and the verdict

## 18.1 What the diff now contains: FIVE files, ONE voice computation

`passive_cue_patch.diff` grew from 3 files to 5. **There are no call sites in `tools/` -- enumerated, not
assumed** (`grep` over `tools/*.py` for `precise_passive|participle_bypp_gate|label_voice_correct|
voice_correction` returns nothing), so the diff is complete on the shipped path.

| hunk | file | what it does |
|---|---|---|
| D1 | `hdlab/thematic_role_labeler.py` | the organ block + `is_passive_clause` deprecated in place |
| D1 | `hdlab/graded_role_assigner.py` | the import + all four call sites |
| **D2** | `hdlab/relcl_resolver.py` | **`precise_passive` becomes a thin delegate to `is_passive_predicate`** -- the NAME is kept so none of its six consumers churns; the COMPUTATION is the organ's |
| **D4** | `hdlab/graded_role_assigner.py` | **`participle_bypp_gate`'s `_is_participle` suffix test replaced by the organ's voice read** |
| **D5** | `hdlab/arc_labeler.py` | **`VOICE_CORRECTION`, `_BE_AUX` and `label_voice_correct` DELETED**; `voice_correction=` stays on `label()` accepted-and-ignored so no caller churns (three call sites in `verification/test_arc_labeler_fastpath_hdlab_landing.py` pass it, and they still mean what they say: there is no voice correction) |
| Q1 | `experiments/exp_board_agent_slot_ud_v1.py` | the duplicate `hybrid_agent_pick` retired to a thin call |

The cell's self-test now **compiles every patched file from the patched text** and asserts the three deletions
and the delegate are really there (32/32).

## 18.2 The fold, measured at every consumer, with the fold OFF and ON in one run

**D2's biggest consumer -- the board's `who_did_what_patient` row, by the board's own function:**

| arm | model | **floor** | twin | model - floor | ceiling (gold parse) |
|---|---|---|---|---|---|
| landed | 0.8120 | 0.7203 | 0.6430 | +0.0916 CI[+0.0708,+0.1114] sep | 0.9610 |
| **D2+D4+D5 folded** | **0.8135** | **0.7227** | 0.6454 | **+0.0908 CI[+0.0701,+0.1107] sep** | 0.9610 |

**And this is the honest reading, which the recomputed-in-place floor is what caught:** the model rises
+0.0015 **and its own floor rises +0.0024**, because the deployed floor
(`_deployed_structural_patient_pick`) has a net-safe `hybrid_role_patient` fallback that reads
`precise_passive` too. The MARGIN is therefore flat (-0.0008, well inside the CI). **D2's fold is a
consolidation, not a win at this consumer** -- exactly what I called it in 17.5, now confirmed with the
floor moved in place rather than pasted.

**The board's `who_did_what_agent` row, by the board's own function:**

| arm | model | floor | model - floor | passive n=16 | active n=1407 |
|---|---|---|---|---|---|
| landed | 0.8271 | 0.8468 | -0.0197 CI[-0.0317,-0.0090] BELOW | 0.1875 | 0.8344 |
| phase 7a (voice + the organ) | 0.8552 | 0.8468 | +0.0084 CI[+0.0007,+0.0157] **sep** | 0.6250 | 0.8579 |
| **+ D2 + D4 + D5 folded** | **0.8559** | 0.8468 | **+0.0091 CI[+0.0014,+0.0168] sep** | 0.6250 | **0.8586** |

**D5's consumer -- every label consumer, via `ArcLabeler.label()`, UD-EWT test 700 under live heads:**

| population | landed | with `label_voice_correct` DELETED | delta |
|---|---|---|---|
| all labelled nominals, n=2216 | 0.6995 | **0.6995** | **+0.0000** |
| gold `nsubj:pass`, n=48 | 0.5417 | **0.5417** | **+0.0000** |
| gold `obl:agent`, n=19 | 0.6316 | **0.6316** | **+0.0000** |

**Byte-identical on all three.** The deletion is a no-op by measurement, which is the strongest case a
deletion can have: the Competition-Model organ already decides every label the rule would have changed.

## 18.3 THE WITNESSES -- nine run, each with the fold OFF then ON. NOT ONE GOES RED BECAUSE OF THE FOLD.

Found by `grep` over `verification/*.py` for the four names (plus the four the brief listed). Each is executed
in-process twice -- once at HEAD, once with the fold installed -- so `hdlab/` is never written.
**Result: 7 GREEN both, 2 RED both (pre-existing). Zero caused by the fold.**

| witness | HEAD | folded | verdict |
|---|---|---|---|
| `test_coarse_role_competition.py` | exit 0 | exit 0 | **GREEN both** |
| `test_labeled_patient_landing.py` | exit 0 | exit 0 | **GREEN both** |
| `test_modern_board_landing.py` | exit 0 | exit 0 | **GREEN both** |
| `test_noncanonical_agent_bymorph_organ.py` | exit 0 | exit 0 | **GREEN both** |
| `test_noncanonical_role_assigner.py` | exit 0 | exit 0 | **GREEN both** |
| `test_precision_defer_landing.py` | exit 0 | exit 0 | **GREEN both** |
| `test_valency_labeled_patient_landing_organ.py` | exit 0 | exit 0 | **GREEN both** |
| 🔻 `test_arc_labeler_fastpath_hdlab_landing.py` | **2/4 at HEAD** | **2/4, identical lines** | **RED BEFORE AND AFTER -- pre-existing, not mine** |
| 🔻 `test_byhead_agent_cue_landing.py` | **raises** | **raises, same line** | **RED BEFORE AND AFTER -- a bug in the witness itself** |

**The two reds, diagnosed rather than reported:**

- `test_arc_labeler_fastpath_hdlab_landing.py` fails at HEAD with `FAIL L2 ... [341 mismatches / 4575 arcs]`
  and `FAIL L3 ... [1217 mismatches / 18346 arcs]` -- **the same two lines, the same counts, with the fold
  in.** Both failing checks call `label(..., voice_correction=False)`, so they never exercised the deleted
  code at all; they are comparing the fast plan against the reference `_predict_label` and that equality is
  broken for another reason. **Confirmed by running it as a plain subprocess at HEAD: 2/4 checks passed.**
  Nothing for me to re-pin -- this is a standing red that predates this brief and deserves its own look.
- `test_byhead_agent_cue_landing.py` raises `TypeError: not all arguments converted during string
  formatting` at **its own line 80** (`"ON=%s" % a_on`, where `a_on` is not a single value). Also confirmed
  as a plain subprocess at HEAD. **So the landing witness for the byhead CASE cue has not been executing** --
  which is worth knowing precisely because D4 is that cue's gate, and because the board arm's failure to pass
  `byhead_agent_cue=True` (17.3) is exactly the kind of drift a working witness would have caught.

**No witness pins the OLD detector's number, so there is nothing for strategy to re-pin.** The one witness
that could have -- `test_coarse_role_competition.py`, which asserts `voice_order == passive_strong_pre`,
`prep == by_passive`, `nsubj:pass` and `obl:agent` on *"The dog was bitten by the man"* -- is GREEN both ways,
because those assertions run through `voice_cues` (D3, untouched), not through the folded detectors.

## 18.4 (Q2) THE VALIDITY-TABLE RE-ACCRUAL IS ROUTED AWAY

Confirmed and closed here per strategy's ruling: **the `coarse_role_validities` re-accrual routes to pri 114
(organ-tagged acquisition) / pri 110's follow-on, not to this brief.** The evidence is in 17.6 -- the only
CI-separated movement (`obj` +0.0150) reproduces under the **shipped-cue** re-accrual, so it is the upstream
landing being learned and not this cue. The two assets stay on disk for whoever picks it up
(`data/hook_state/coarse_role_validities_pri111_{shipped,patched}_perceived_w_v4.json`); **neither is
proposed for landing and the live asset was never written.** No further work here.

## 18.5 (Q3) BRIEF-READY LEAD, NOT BUILT: the by-NP head on flat names belongs to the attachment arm

> **PROBLEM (draft):** the agent competition cannot say which token of a by-phrase NP is its head, so a
> passive agent that is a multi-word NAME is picked at the wrong token -- `by a **Vikash** Chand Abdul
> Shakur` and `by **al** - Qaeda` are both lost to the second token, and four more by-NPs are lost to the
> head-final/head-initial split.
>
> **THE POPULATION, counted:** UD-EWT test, the board's who-did-what AGENT gold, **16 gold-passive items**
> (`obl:agent`). The positional floor gets **0/16**. The organ with this brief's voice cue gets **10/16**.
> The by-governed oracle gets **12/16**. The 6 that are lost split exactly two ways:
> - **2 are flat NAMES** headed on their FIRST token by the UD `flat` convention (`Vikash Chand Abdul
>   Shakur`, `al - Qaeda`) -- the competition has no cue for which token of a name is the head;
> - **4 are common-noun NPs whose head is not the first by-governed token** (`by an extremist **form** of
>   the Wahhabi school`, `by my better **half**`, `by Gravity CEO **Kim** Jung-Ryool`, `by two space
>   **businessmen**`).
>
> **THE NEGATIVE THAT IS ALREADY MEASURED, so nobody re-runs it:** a positional head rule does NOT reach
> them. I built `oracle_by_nphead` -- the first PROPN of the by-NP if there is one, else the LAST noun, i.e.
> right-headed English NPs with a left-headed name exception -- and it scores **0.7500 on the slice, exactly
> the same 12/16 as "first by-governed"**, and **-0.0063 on the full 1423-item population**. It trades the
> two name items for two common-noun items. **The head of a by-NP is not recoverable positionally; it needs
> the attachment arm's own `flat` / `compound` / `nmod` decisions.**
>
> **WHY IT BELONGS TO THE HEADS RUNG:** `flat` is an attachment convention (which token of a name governs
> the others), and the arm already decides it; the agent competition is simply not reading it. The likely
> shape is a JOIN, not a new computation -- the candidate generator should offer the by-NP's *head* as one
> candidate rather than every token of it as several.
> **BOUND:** 6 of 16 items on this row = +0.0042 on the full agent population, with 2 of the 6 (the names)
> the cheap half.

## 18.6 THE VERDICT: EXHAUSTED AT THIS RUNG

**YES -- with D2 and D4 folded and D5 deleted, this brief is EXHAUSTED at this rung.** The claim is not
"I ran out of ideas"; it is that every remaining item has been located at a *different* rung, with a number
and an owner:

| what | status | evidence |
|---|---|---|
| the voice COMPUTATION | **done** | one organ; precision 0.3784 -> 0.9606 with recall up, on three corpora, twin CI-separated below on all three; criterion on a flat plateau |
| its CONSUMERS | **done** | all four hdlab call sites + the board arm's duplicate retired; agent row 0.8271 -> 0.8559, CI-separated ABOVE its own floor; `agent_supports` +0.0127 CI-sep; labels flat with the mechanism counted; patient board consolidated |
| the DUPLICATES | **5 of 6 resolved** | D1 folded, D2 folded, D4 folded, D5 deleted (a measured no-op), D6 follows D2 |
| D3 (`voice_cues` / `robust_passive`) | **handed over** | folding it requires refitting `DEFAULT_VALIDITIES` (`passive_strong` 3.2317 / `passive_weak` -2.9927) and it is the patient arm's own FLOOR's voice -- its own brief |
| the by-NP head | **handed over, 18.5** | 6 of 16 items; the positional rule is measured NOT to reach 4 of them |
| the category organ's participle/adjective boundary | **handed over** | 3 items of recall, posteriors 0.950 / 0.517 / 0.745 |
| the validity-table re-accrual | **routed to pri 114 / pri 110** | 17.6, 18.4 |
| the `'s` clitic + the pseudo-cleft | **handed over** | 1 item each; both need *does this participle take an object of its own* -- the verb-frame rung |
| two standing RED witnesses | **reported, 18.3** | both pre-existing; `test_byhead_agent_cue_landing.py` has not been executing at all |

**What would change my answer:** if the attachment arm's `flat` decisions were exposed to the agent
candidate generator, the by-NP head lead (18.5) would come back to this row and be worth up to +0.0042 more.
Until then there is nothing left inside this cue that a sweep, a control, or a stronger brain build reaches
-- I have run the sweep (flat), the twin (below floor on three corpora), the oracle ceilings (by-governed
12/16, by-NP-head 12/16), the OOD split, and the head-to-head attribution of every single break.


---

# 19. INTEGRATION (strategy, 2026-09-14 15:45 -> 16:10) -- the byhead witness caught a REAL defect in D4, and it is repaired

**THE ANSWER IS BOTH (a) AND (b), IN THAT ORDER. D4's first fold really did lose 6-7 true by-agents, and the
experiment's copy really is a stale twin -- but only AFTER the repair, and only by one item.** I got D4
wrong, the witness caught it, and the repair is in this folder's diff.

## 19.1 (a) THE FIRST FOLD LOST REAL BY-AGENTS -- all 7, attributed, and every one has the SAME signature

Reproducing the witness's own slice (`_qasrl_slices()["clean_agent_post"]`, n=90) against the landed tree:
`landed_byhead 0.6000, experiment 0.6667, 8 disagreements -- the organ loses 7 and wins 1.` All seven:

| verb | organ's voice cue | pre-fold gate | folded gate | suffix-participle | organ picked | experiment picked | gold |
|---|---|---|---|---|---|---|---|
| Dissolved gases become **trapped** by thick magma | `none` | True | **False** | True | gases | magma | magma |
| mass (kg) **divided** by volume (m3) | `none` | True | **False** | True | kg | volume | volume |
| other forms ... such as those **used** by non-human animals | `none` | True | **False** | True | those | animals | animals |
| External fertilization , **employed** by most frogs and toads , involves ... | `none` | True | **False** | True | fertilization | toads | toads |
| a type of display , usually **performed** by the male | `none` | True | **False** | True | this | male | male |
| evidence , usually tested and **confirmed** by many different people | `none` | True | **False** | True | evidence | people | people |
| Banks **considered** by analysts likely to be classified ... | `none` | True | **False** | True | Banks | analysts | analysts |

**Seven for seven: `cue=none`, `old_gate=True`, `new_gate=False`, `suffix_participle=True`.** Every one is a
**REDUCED participial passive with no auxiliary at all** -- a reduced relative (`those used by...`), a
participial adjunct (`employed by most frogs and toads,`), a post-nominal modifier (`a display performed by
the male`), a `become`-passive, or a nominal `divided by`. Gate recall on the slice fell **62/90 -> 53/90**.

**WHY I GOT IT WRONG, precisely.** `participle_bypp_gate` is a **CONSTRUCTION detector** -- "is there a V-en
with a demoted agent in a by-phrase here" -- and I folded it onto a **FINITE-CLAUSE VOICE READ**:
`is_passive_predicate` requires an AUXILIARY, by construction, because the auxiliary is what opens the
passive expectation (section 3). A reduced participle has no auxiliary to open it. **The two are different
questions and I treated them as one.** Worse, I had the evidence in my own hands and read it the wrong way
round: negative **N4** (section 10) measured `none|ed|by|none` as passive only 7/193 = 0.036 *on UD's
`aux:pass` gold* and I concluded the configuration "genuinely is not the target here". That is true for
UD's finite-clause marking and **false for this gate**, whose target is the demoted agent, not the finite
clause. The 32 -> 16 firing-rate halving I reported in 17.5 as "a 2x precision gain" was **half precision
gain and half recall loss**, and the UD `aux:pass` gold could not tell me which.

## 19.2 THE REPAIR, and it is this organ's own story read in the other direction

Section 3 says: *the auxiliary OPENS the passive expectation and the by-phrase CONFIRMS it.* **So when there
is no auxiliary to open the expectation, the confirmation carries the construction by itself.** The repaired
gate fires on a by-governed NP plus **EITHER** the organ's voice read (an auxiliary opened it -- which also
catches the irregular participles the suffix test cannot see) **OR** participial morphology (the reduced
passive). It is a **strict SUPERSET of the pre-fold gate**, so it cannot lose a firing the old one had.

```python
    low = [t.lower() for t in toks]
    if not any(by_governs(low, pos, i) for i in range(len(toks))
               if (pos[i] if i < len(pos) else None) in _BYHEAD_NOM):
        return False
    if is_passive_predicate(toks, pos, v0 + 1):
        return True
    return _is_participle(toks[v0], pos[v0] if v0 < len(pos) else None)
```

## 19.3 THE NUMBERS ON BOTH SLICES, PLUS THE CANONICAL NO-REGRESS SLICE

| slice | experiment copy | **D4 first fold (landed)** | pre-fold suffix gate | **REPAIRED** |
|---|---|---|---|---|
| clean agent-post, n=90 | 0.6667 | **0.6000** (8 disagree, 53 fires) | 0.6667 (62 fires) | **0.6778** (1 disagree, **63 fires**) |
| full non-canonical, n=201 | 0.6816 | **0.6617** (6 disagree, 50 fires) | 0.6816 (55 fires) | **0.6866** (1 disagree, 57 fires) |
| canonical no-regress, n=845 | 0.7077 | 0.7053 (4 disagree, 5 fires) | 0.7077 (14 fires) | **0.7077** (**0 disagree**, 14 fires) |
| UD agent population gate fires / 1424 | -- | 16 | 32 | **33** |

**The repair restores both passive slices ABOVE the pre-fold numbers and restores the canonical slice to
byte-identical.** The board's `who_did_what_agent` row, by the board's own function:

| gate | model | floor | model - floor | passive n=16 | active n=1407 |
|---|---|---|---|---|---|
| D4 first fold (landed) | 0.8559 | 0.8468 | +0.0091 CI[+0.0014,+0.0168] sep | 0.6250 | 0.8586 |
| pre-fold suffix | 0.8552 | 0.8468 | +0.0084 CI[+0.0007,+0.0157] sep | 0.6250 | 0.8579 |
| **REPAIRED** | **0.8552** | 0.8468 | **+0.0084 CI[+0.0007,+0.0157] sep** | **0.6250** | 0.8579 |

**The board row is unchanged by the repair (0.8559 -> 0.8552, 1 item) and still CI-separated above its own
floor.** The first fold's extra board item was bought for seven QA-SRL by-agents -- **a bad trade, and the
board alone could not see it.** That is the argument for the witness.

## 19.4 (b) AND NOW THE EXPERIMENT'S COPY IS A STALE TWIN -- the per-row diff, one item

With the repair in, the organ and the experiment's copy disagree on **exactly one row on each passive
slice, and it is the same row, and the ORGAN is right**:

```
"They are led by head coach Monreal , with assistant coach ..."
   gold           = head coach Monreal
   organ          = head          (CORRECT)
   experiment     = They          (wrong -- the surface subject)
   suffix_participle = False   <- `led` has no -ed / -en suffix
   organ voice cue   = be_chain <- the auxiliary chain sees `are led`
   repaired gate = True    pre-fold gate = False
```

**`led` is an irregular participle with no `-ed`/`-en` ending, so `_is_participle` cannot see it** -- which
is the very defect this brief was opened to fix, one rung over. The experiment's copy
(`exp_noncanonical_agent_bymorph_v1.passive_agent_gate`) still uses the suffix test, so it never gates the
byhead cue here and falls back to word order.

➡️ **RECOMMENDATION FOR THE WITNESS:** the `landed hdlab byhead == validated experiment byhead PER-ROW
(byte-faithful)` check should be **re-pinned to the organ's arm**, not weakened. The organ is now **one item
BETTER** than the twin on each passive slice (0.6778 vs 0.6667; 0.6866 vs 0.6816) and byte-identical on the
canonical slice. If strategy prefers to keep a byte-faithfulness check at all, the honest form is
"the organ is a superset of the experiment's picks on the gated rows" rather than equality -- or
`exp_noncanonical_agent_bymorph_v1.passive_agent_gate` gets the same one-line repair, after which the two
agree again. **I have not touched the experiment's copy; that is strategy's call.**

## 19.5 WHAT THIS CHANGES IN THE RECORD ABOVE

- **17.5 / 18.1-18.2 (D4)**: the "gate firing 32 -> 16, a 2x precision gain" claim is **WITHDRAWN**. The
  correct statement is: the first fold traded 16 false firings for 9 true ones on QA-SRL, and the repaired
  gate fires **33** of 1424 on the UD agent population -- one MORE than the pre-fold gate, not half.
- **N4 (section 10)** stands as a measurement but its *conclusion* was over-generalised: the aux-less
  `V-ed ... by NP` configuration is not a finite passive on UD's gold, but it **is** the demoted-agent
  construction, and a gate whose consumer is the by-phrase case cue must fire on it.
- **18.6's EXHAUSTED verdict stands**, with one correction to its confidence: it was reached with a defect
  in the shipped diff that only a consumer-level witness on a *different corpus* (QA-SRL, not UD-EWT) could
  see. **The lesson for the record: I measured D4 only on the UD `aux:pass` gold, where the construction it
  gates is by definition invisible.** The right instrument for a construction detector is the construction's
  own population, and the byhead witness is that instrument.


---

# 20. INTEGRATION, ROUND 2 (strategy, 2026-09-14 16:05) -- the twin repair, D2's construction check, and the close

## 20.1 (Q1) THE TWIN'S REPAIR, EMITTED NOT APPLIED: `byhead_twin_repair.diff`

One hunk for `experiments/exp_noncanonical_agent_bymorph_v1.passive_agent_gate`, the same
construction-plus-voice repair the organ got, plus the one import it needs. `git apply --check` passes; **I
have not applied it.** With it, the copy gates byhead on `They are **led** by head coach Monreal` (an
irregular participle its suffix test cannot see), which is the single row where the organ and the copy still
disagree -- so the witness's per-row byte-faithfulness check becomes restorable rather than merely re-pinnable.

## 20.2 (Q2) THE SAME CONSTRUCTION-POPULATION CHECK FOR D2 -- and it DID lose real items, so the fold is widened

**The D4 lesson, applied:** measure a folded detector on the population of the construction it detects, and
on its consumers' own witness slices, not on a gold that cannot see it.

**(i) The detector, per item** -- UD-EWT test, 2605 predicates, 126 gold passive, live chain:

| | fires | true positives | false fires | recall | precision |
|---|---|---|---|---|---|
| pre-fold `precise_passive` (window + suffix) | 112 | 103 | 9 | 0.817 | 0.920 |
| **the fold, organ read ALONE (landed)** | 127 | 117 | 10 | 0.929 | 0.921 |
| **the STRICT SUPERSET (shipped now)** | **135** | **120** | 15 | **0.952** | 0.889 |

31 disagreements between pre-fold and folded: **17 true passives GAINED, 3 LOST**, 5 false fires removed, 6
added. **All three lost items have the same signature, and it is NOT D4's:**

| item | organ cue | by-agent? | rung |
|---|---|---|---|
| They are probably especially **oriented** toward the Salafi school | `na` | no | **category organ** (tags it ADJ) |
| that Irish , I was **surprised** to hear | `na` | no | **category organ** |
| I have never been **disappointed** . | `na` | no | **category organ** |

Not reduced passives (D4's class) and **none carries a demoted agent** -- these are the three
participle/adjective items already named in 6.4 and 17.1, lost one rung ABOVE this cue. The pre-fold
condition caught them only because its suffix test never consults the category at all.

**(ii) The consumer -- the board's who-did-what PATIENT row, by the board's own function, floor recomputed
in place each time:**

| arm | model | floor | twin | model - floor |
|---|---|---|---|---|
| pre-fold | 0.8135 | 0.7203 | 0.6438 | +0.0932 CI[+0.0730,+0.1129] sep |
| the fold, organ read alone (landed) | 0.8151 | 0.7227 | 0.6462 | +0.0924 CI[+0.0726,+0.1121] sep |
| **the STRICT SUPERSET** | **0.8167** | 0.7227 | 0.6486 | **+0.0940 CI[+0.0741,+0.1138] sep** |

**(iii) The relative-clause consumers' own witnesses**, run pre-fold and folded in process:
`test_relcl_resolver_organ.py` **exit 0 both**, `test_noncanonical_role_assigner.py` **exit 0 both**.

**THE DECISION, and the honest label on it.** The superset is the best of the three on both the model
(0.8167) and the margin (+0.0940) -- **but it is NOT CI-separated from the organ-only fold** (half-width
~0.02 against a 0.0016 difference). I am shipping it anyway, and the reason is not the number: **it is the
only one of the three that cannot lose a firing either predecessor had**, which is the guarantee a fold onto
one organ has to make. D4 is the evidence for taking that guarantee seriously -- there the same "small,
defensible" narrowing cost seven real by-agents on a slice the UD gold could not see. The hunk is in
`passive_cue_patch.diff`; the comment in it carries all three numbers so nobody has to take my word.

## 20.3 THE FINAL VERDICT FOR THE RECORD

**EXHAUSTED at this rung, and now with the consumer-population check done on every folded detector.**

| detector | folded onto the organ | construction-population check | outcome |
|---|---|---|---|
| D1 `is_passive_clause` | yes, 5 call sites | UD-EWT + GUM + GENTLE, 3 corpora | precision 0.3784 -> 0.9606, recall up; agent row CI-separated above its floor |
| D2 `precise_passive` | yes, **widened to a strict superset** | patient board + 2 relcl witnesses (20.2) | 3 real items lost by the narrow fold, recovered; consumer 0.8135 / 0.8151 / **0.8167** |
| D4 `participle_bypp_gate` | yes, **repaired to a strict superset** | QA-SRL byhead slices (19) | 7 real by-agents lost by the narrow fold, recovered; clean slice 0.6000 -> **0.6778** |
| D5 `label_voice_correct` | **deleted** | every label consumer, UD-EWT test 700 | byte-identical on all three populations -- a measured no-op |
| D3 `voice_cues` / `robust_passive` | **not folded** | -- | needs a `DEFAULT_VALIDITIES` refit; its own brief |
| D6 `predicate_argument_frontend` | follows D2 | -- | -- |

**The methodological finding I would put in the ledger above any single number:** *a detector folded onto a
shared organ must be checked on the population of the construction it detects, not on the gold its consumer
happens to be scored against.* I folded D2 and D4 having measured both only on UD's `aux:pass` gold. That
gold is blind to the reduced participial passive (D4's target) and blind to the participle/adjective
boundary (D2's), so both folds looked like clean precision gains and both were quietly losing recall.
**Two consumer-level witnesses on different corpora -- QA-SRL for byhead, the patient board for the
relative-clause route -- are what caught them, and in D4's case the board could not have: the narrow fold
was +1 item on the board while it was -7 on QA-SRL.** The rule that follows: **fold to a strict superset
unless the narrowing is itself measured on the construction's own population.**

**Still open, unchanged from 18.6, each with a number and an owner:** the by-NP head (6 of 16; the
attachment arm's `flat` convention; `byhead_twin_repair.diff` and 18.5 are ready); D3's refit; the category
organ's participle/adjective boundary (**now worth naming twice** -- it is the 3 items of 17.1 AND the 3
items of 20.2, the same three); the validity-table re-accrual (pri 114 / pri 110); the `'s` clitic and the
pseudo-cleft (verb-frame rung); and the two standing red witnesses of 18.3.

