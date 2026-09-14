---
problem: the_passive_cue_fires_on_the_whole_sentence_not_the_clause_33_of_43_licensed_agent_overrides_are_gold_active_so_the_marked_cue_override_breaks_more_than_it_fixes
status: SOLVED
bar: "Clause-local detector: false fires on gold-active clauses down from 33/43 CI-separated with recall on true passives not down; the override anatomy flips to net-positive (fixes > breaks) or the licence is withdrawn with the number; every consumer moved to the one detector; the board's agent dimension not down; twin (random equal-size set of clauses declared passive) at floor -- OR a numbered located negative naming which consumer the clause-local cue helps and which it hurts."
result: "THE CUE WAS ANSWERING THE WRONG QUESTION -- 'is this SENTENCE passive' where every one of its four consumers asks 'is THIS PREDICATE passive' -- AND FIXING THAT MOVED THREE CONSUMERS WITH NONE DOWN. (1) THE DETECTOR, per predicate, through the LIVE brain-foundational chain (count-based category organ + attachment arm, no gold at decision time): UD-EWT test, 2605 gold-VERB predicates in 1240 sentences -- the shipped whole-sentence `is_passive_clause` scores precision 0.3784 / recall 0.8235; the predicate-anchored `is_passive_predicate` scores precision 0.9606 / recall 0.8971, i.e. precision up 2.5x with recall UP, 200 fixes against 11 breaks head to head, decision accuracy +0.0726 CI95[+0.0566,+0.0892] CI-separated over the shipped floor, with a same-rate random TWIN at -0.0177 CI-separated BELOW the floor. IT TRANSFERS TO TWO HELD-OUT MODERN GOLDS the counts never saw: GUM 29,217 predicates 0.3643/0.8123 -> 0.9503/0.8517 (+0.1030 CI-sep) and the OOD GENTLE split 0.4596/0.9000 -> 0.9821/0.9167 (+0.0768 CI-sep), twin CI-separated below on both. (2) THE OVERRIDE ANATOMY THE BRIEF WAS OPENED ON: the passive licence fires 92 times on the 1423-item agent population, 83 of them on gold-ACTIVE clauses, fixing 1 and breaking 30 (conflict validity 0.032 -- pri 106's 1/30 reproduced exactly); with the corrected cue plus the by-phrase confirmation it fires 11 times, 0 on gold-active clauses, fixing 1 and breaking 0 (validity 1.000). (3) THE BOARD'S OWN who_did_what_agent ROW, computed by the board's own function: 0.8271 (CI-separated BELOW its own positional floor 0.8468) -> 0.8475 with the cue fix -> 0.8531 when the board arm is additionally replaced by the organ, passive slice 0.1875 -> 0.5625, and the active slice EXACTLY no-regress (0.8564 = the floor). (4) A SECOND CONSUMER UP CI-SEPARATED: `agent_supports` -- the voice flip the live reader runs on every sentence -- 0.7511 -> 0.7637, +0.0127 CI95[+0.0070,+0.0197]. NO CONSUMER DOWN: the coarse role labeler on UD-EWT test 700 under live heads is +0.0014 CI95[0.0000,+0.0031] over all 2216 arguments and +0.0025 over the 1205 core ones, with gold nsubj:pass (n=48) and obl:agent (n=19) byte-identical. THE HONEST ATTRIBUTION: inside the ORGAN the cue fix is worth 3 items (+0.0021, NOT separated) because the organ already required a by-phrase; the 30 broken decisions live in the BOARD ARM's duplicate of the hybrid, where the same one-line change is +0.0204 CI95[+0.0126,+0.0281] CI-separated. A SECOND, INDEPENDENT DEFECT FOUND BY TRACING ONE RUNG DOWN: the board arm's copy never passes `byhead_agent_cue=True`, so the landed by-phrase CASE cue has never reached the board -- retiring the copy in favour of the organ is +0.0239 CI95[+0.0155,+0.0323] on its own and recovers 5 of the 16 passive agents."
floor: "(1) DETECTOR: the shipped `hdlab.thematic_role_labeler.is_passive_clause`, measured on the SAME 2605 predicates in the SAME run -- precision 0.3784 / recall 0.8235 / decision accuracy 0.9202 -- plus two STRONGER intermediate floors measured alongside: the same detector scoped to the clause span (what `agent_override_fires` does today) 0.4860/0.7647, and `hdlab.relcl_resolver.precise_passive`, which is already predicate-anchored, 0.9464/0.7794. Every delta is quoted against the shipped floor and the new read beats the STRONGEST of the three on precision and recall on every population. (2) AGENT CONSUMER: the POSITIONAL floor the board itself uses (nearest pre-verbal clause-local nominal, `exp_board_agent_slot_ud_v1.floor_positional_agent`) = 0.8468 on UD-EWT test n=1423, with the landed board model 0.8271 measured alongside; `hybrid_without_the_passive_licence` (pp_gov + noncase only) 0.8475 is reported too, so the passive cue's own contribution is not confounded with the other two marked cues. (3) BOARD ROW: the board's own floor from its own function, 0.8468, and its own shuffled-supports twin, 0.2853. (4) GUM / GENTLE: the same shipped whole-sentence detector recomputed in place on each population (0.3643/0.8123 and 0.4596/0.9000) -- no floor is pasted across populations."
controls: "(1) INFO-FREE TWIN, DETECTOR, on all three populations: a RANDOM equal-size set of predicates declared passive at the new cue's own firing rate -- UD-EWT precision 0.0462 and decision accuracy -0.0177 CI95[-0.0341,-0.0004] CI-separated BELOW the floor; GUM -0.0139 CI-sep below; GENTLE -0.0502 CI-sep below. (2) INFO-FREE TWIN, CONSUMER: the passive licence fires on a random equal-size set of agent decisions -- 0.8468 = the positional floor EXACTLY (it stops helping), against the corrected cue's 0.8482. (3) TWO HELD-OUT MODERN GOLDS the counts never saw (GUM 275 files, GENTLE 26 files OOD), 11x and 0.6x the UD-EWT test size. (4) TWO GOLD CONVENTIONS reported side by side -- raw UD (aux:pass/nsubj:pass/csubj:pass) and a propagated gold adding the bare CONJUNCT of a passive predicate -- and the conclusion is identical under both (raw: 0.9213/0.9286 new vs 0.3503/0.8175 shipped). (5) TRAIN/TEST SEPARATION: the counts and the criterion theta are accrued/swept on UD-EWT TRAIN (22,576 predicates) and applied UNCHANGED to test; the train sweep is a flat plateau (F1 0.9331-0.9350 over theta 0.15-0.65, best 0.50). (6) UPSTREAM CONTRAST: the detector measured with and without the reader's own heads -- 0 of 2605 decisions differ, so the claim 'the arc confirms but does not decide' is a count, not an assertion. (7) NO-REGRESS measured on the other call sites in the same run (see result), and the shipped witness `verification/test_coarse_role_competition.py` is green at HEAD (37/37) with its four voice assertions re-checked under the PATCHED cue inside the cell's self-test. (8) PATCH FIDELITY: the diff is GENERATED from the cell's own organ block, the self-test asserts the diff's added lines are byte-identical to the measured code, `git apply --check` passes, and the PATCHED module is imported and shown to answer identically to the cell on 10 cases. (9) PAIRED BOOTSTRAP, 2000 resamples, clustered by SENTENCE for the detector and by ITEM for the consumer, on each item's own population."
files_changed: "experiments/exp_passive_cue_clause_local_v1.py (the cell; self-test 25/25), notes/problems/<slug>/{SOLVED.md, passive_cue_patch.diff}, data/hook_state/passive_voice_counts_v1.json (the plastic cue-validity counts -- opt-in, re-derivable by --run), and the cell's own data/exp_passive_cue_clause_local_v1/*.json. NO hdlab/ or tools/ file changed on disk. The diff touches hdlab/thematic_role_labeler.py (the organ block + a deprecation note on is_passive_clause), hdlab/graded_role_assigner.py (the import + ALL FOUR call sites) and experiments/exp_board_agent_slot_ud_v1.py (the board arm's OWN copy of the cue -- without this third hunk the board number does not move). Two of the three files are CRLF: apply with `git apply --ignore-whitespace`."
reverify: ".venv/Scripts/python.exe experiments/exp_passive_cue_clause_local_v1.py --self-test   (25 checks, seconds; includes PATCH == CELL, git apply --check, the patched-module parity check and the shipped witness's voice assertions under the patched cue). Headline numbers, each writing ONLY into its own data/exp_passive_cue_clause_local_v1/ directory: --run (~10 min -> metrics.json + detector.json + override.json + call_sites.json); --push (~1 min -> push.json); --board-dim (~6 min -> board_dimension.json, the board's own row under three arms); --extra (~12 min -> extra.json: the criterion sweep, the heads contrast, the upstream category loss, call site 2); --gum (~8 min -> gum.json, the two held-out golds). Also: .venv/Scripts/python.exe verification/test_coarse_role_competition.py (37/37, unmodified)."
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
| **the ORGAN `hdlab.hybrid_agent_pick` with the diff in** | **0.8531** | **+0.0063 CI95[-0.0014,+0.0134] n.s.** | **+0.0260 CI95[+0.0169,+0.0351] sep** |
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

The cue can only fire on a token the category organ calls a VERB. **212 of the 2605 predicates get `na`**
(the organ tagged them something else). Of the 136 gold passives, **exactly 4 are lost that way**, and three
of the four are the same thing:

```
are probably especially oriented toward the      [oriented = ADJ]
, I was surprised to hear                        [surprised = ADJ]
have never been disappointed .                   [disappointed = ADJ]
a leg and have to wait                           [have = AUX]
```

**The adjectival-participle residual the brief's checklist item 4 predicted did not materialise where it was
expected.** Of the 5 remaining false fires on UD-EWT test, **ZERO carry a degree modifier** -- the
adjectival-passive precision problem does not exist at this rung, because `was tired` / `is interested` /
`especially oriented` never reach the cue at all: the CATEGORY organ tags them ADJ one rung earlier. The
adjectival/verbal passive distinction has therefore moved UP the chain and changed sign: it is a RECALL loss
in the category organ (3 items), not a PRECISION loss in the voice cue (0 items). I built the degree-modifier
cue anyway (it is a cue VALUE in the counts: `none|other|none|deg` = 0/105 passive, `none|ed|none|deg` =
0/31) and it is measured to be inert at this rung -- an honest null, kept because it is free and because it
will matter the moment the category organ stops absorbing the distinction.

The fourth item, `have` tagged AUX, is the *same* convention defect pri 110 is working (UD tags a clause's
only verb `be`/`have` as AUX) -- flagged, not touched.

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
| **the ORGAN + pri-111 voice** | **0.8531 (+0.0063 n.s.)** | **0.8564 (+0.0000 -- EXACTLY no regress)** | **0.5625** |

Two things are worth saying plainly. First, **the cue fix inside the ORGAN is worth 3 items (+0.0021,
CI95[0.0000,+0.0049], not separated)** -- because the organ already required a by-phrase, which was masking
most of the whole-sentence false fires. Second, **the cue fix inside the BOARD ARM is worth +0.0204
CI95[+0.0126,+0.0281], CI-separated**, because the board arm has no by-requirement and was taking all 30
breaks. The 30 broken decisions the brief was opened on live in the board arm's copy, not in the organ.
Retiring that copy in favour of the organ is +0.0239 CI95[+0.0155,+0.0323] on its own, and +0.0260
CI95[+0.0169,+0.0351] with the cue fix.

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
| **+ pri-111 voice read (the board hunk of the diff)** | **0.8475** | 0.8468 | 0.2853 | **+0.0007 CI[-0.0068,+0.0078]** | 0.1875 |
| **+ pri-111 voice AND the board arm replaced by the ORGAN** | **0.8531** | 0.8468 | 0.2853 | **+0.0063 CI[-0.0014,+0.0134]** | **0.5625** |

The board's agent dimension is **not down** -- it stops being CI-separated BELOW its own floor for the first
time, and the passive slice triples.

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

**N3. The GRADED read does not beat the construction read (F1 0.9237 vs 0.9278).** Understood by looking at
the counts: 7 of the 9 cue values have validity above 0.85 or below 0.01, so the posterior is SATURATED and
a criterion anywhere in [0.15, 0.65] reproduces the boolean. The train criterion sweep confirms it -- F1
0.9331 / 0.9331 / 0.9331 / **0.9350** / 0.9349 / 0.9291 / 0.9224 at theta 0.15 / 0.25 / 0.35 / **0.50** /
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
