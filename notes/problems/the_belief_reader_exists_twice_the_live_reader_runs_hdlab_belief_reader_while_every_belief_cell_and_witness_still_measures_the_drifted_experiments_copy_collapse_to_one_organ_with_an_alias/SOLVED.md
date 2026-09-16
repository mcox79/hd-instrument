---
problem: the_belief_reader_exists_twice_the_live_reader_runs_hdlab_belief_reader_while_every_belief_cell_and_witness_still_measures_the_drifted_experiments_copy_collapse_to_one_organ_with_an_alias
status: SOLVED
bar: "1. One organ: experiments/_belief_reader.py is a sys.modules alias of hdlab.belief_reader (every public name IS the organ's object; a witness that asserts identity, not equality), and every importer enumerated in SOLVED.md still imports green. 2. Equivalence proven, not assumed: the copy's read and the organ's read compared on at least 9 documents (the belief instrument's own passages plus GUM narrative docs); mismatches counted and, for each, the hunk responsible named; the organ's answer is the one kept. 3. The belief instruments re-measured on the organ: the belief-at-t end-to-end cell and its witness, the ToM chain witness, any belief-fed board row -- before (copy) and after (organ), with the delta and CI where the instrument has one; a moved number is reported with its cause, never hidden. 4. No stand-in: the organ path has no spaCy/nltk/supervised model at inference (assert it in the witness the way test_no_nltk_on_the_live_path does: poisoned import, the read completes). 5. Nothing else changes: a digest of every non-belief field of the situation model on 6 GUM docs is byte-identical before/after (pri 137's E-check)."
result: "ONE ORGAN, and the drift cost exactly ONE number -- which was a spaCy number for a branch the product does not run. experiments/_belief_reader.py becomes a sys.modules ALIAS of hdlab.belief_reader (500 lines -> 44); `experiments._belief_reader is hdlab.belief_reader` under all four import spellings (plain import, package attribute, importlib.import_module, `from ... import drive`); 8 real importers (5 experiments, 3 verification) + 3 mention-only files enumerated, all green, all reaching the organ; 50 public module-level names checked, 0 lost. EQUIVALENCE on 28 documents (19 belief-instrument passages + 9 GUM narrative documents) x 6 extraction entry points: 0 mismatches at nlp=None (the live semantics -- hdlab.perceptual_access_ledger._nlp has been hardcoded None since CONT-28). THE MOVED NUMBER: W15 of verification/test_belief_at_t_end_to_end_organ.py asserted 'the promoted STATE_REGISTER organ recovers MORE than a stronger parser' on `status_register_recall = 0.600`; that call was `extract_reality_events(..., nlp=<spaCy>)` routed through the copy's `if nlp is not None` branch, which the 2026-09-09 promotion DELETED from the organ. Measured both ways in one process on the same 10 gold status events: COPY 0.600 -> ORGAN 0.000 (and 0.000 with nlp=None too -- the organ has one status path). W15 goes RED on the organ; 18 of the 19 checks are numerically IDENTICAL, and the belief-at-t end-to-end cell's FULL metrics dict is byte-identical before/after (sha256 9e7cdc067d30cb6f... both sides, 0 moved keys). E-CHECK: 6/6 GUM documents byte-identical over 78 non-belief situation-model fields, 0 flips. AND THE ROOT CAUSE OF THE 0.000, LOCATED AND PROTOTYPED PAST: `extract_status_events`'s in-substrate branch searches for the subject OF THE COPULA (`heads[k] == v`, v = the copular verb), but the reader's own parser is UD -- in 'The lamp was lit .' `was` is tagged AUX and attaches TO the predicate (heads = {1:2, 2:4, 3:4, 4:0}), so the subject attaches to the PREDICATE and NOTHING depends on the copula; `subj` is [] on every copular clause and the branch is structurally dead against the parse it is given. It was written for a copula-as-head analysis, which is what spaCy produces, and the removed spaCy branch had been masking it for a week. A UD-shaped re-read (predicate = head, copula = its `cop` dependent, subject = the predicate's dependent, same veridicality gate) scores 0.500 of 10 against the organ-as-shipped 0.000, with a shuffled-vocabulary twin at 0.100. NOT LANDED here (bar 5 is 'nothing else changes') -- handed over as a measured repair."
floor: "This problem has no accuracy gate; its floor is the CAN-FAIL structure of every claim, and each one was made to fail on purpose. (1) DEFECT-PRESENCE / DEFECT-ABSENCE (pri 137's control, in the witness): a stub through `experiments._belief_reader` must be a NO-OP on the organ BEFORE the patch and must BITE after; the witness DETECTS which tree it is on and asserts the matching state, so it fails in both directions and a tree in neither state fails outright. Measured: stub_bites=False pre-landing (the defect, reproduced first-hand), True post-landing. (2) The equivalence check is not vacuous: the SAME comparison driven with a real spaCy pipeline finds 14 mismatches across 7 of the 28 documents, confined to exactly the two entry points hunk H5 touches (`extract_reality_events`, `extract_status_events`) -- so the 0 mismatches at nlp=None is a measurement, not an incapacity to detect. (3) The poisoned-import check asserts the poison BITES (`import spacy` raises) before it asserts the read completes. (4) The hunk classifier computes the classification from a runtime re-diff of the pinned pre-collapse blob and asserts the dangerous class (copy-got-it-organ-did-not) is EMPTY and that nothing is UNCLASSIFIED -- it would go red if either were not so. (5) For the prototype, the STRONGEST real floor is the organ as shipped, 0.000 of 10 on the same population, and the info-free arm is the shuffled-vocabulary twin at 0.100 -- identical firing opportunities, no fact-specific content -- which LOSES to the prototype's 0.500 by 0.400."
controls: "(1) SHIM-EQUIVALENCE, 28 documents x 6 entry points, 0 mismatches at nlp=None -- excludes 'the alias silently changed an answer'. (2) H5-EXPOSURE arm (the same comparison with a real spaCy nlp): 14 mismatches / 7 documents, all in `extract_reality_events` + `extract_status_events` -- excludes 'the equivalence check cannot detect a difference', and ATTRIBUTES the divergence to H5 by where it lands, not by assertion. The nlp=None arm's 0 mismatches independently excludes H4 (the space-import repoint) as a contributor; the three helpers the belief path actually uses from it (`_frontend`, `_cluster_covering`, `_node_from_token`) were separately diffed byte-identical between experiments/_space_reader.py and hdlab/space_reader.py, and `build_backbone` -- the one that DID drift -- is imported but never called inside the belief reader. (3) DEFECT-PRESENCE/ABSENCE, described under floor -- excludes a witness that passes vacuously on either tree. (4) SURFACE control: the pre-collapse copy is loaded side by side as a private module and `set(dir(COPY)) - set(dir(ORGAN))` is empty over 50 public names -- excludes 'an importer loses a name'; the control also asserts the pre-collapse module is NOT the organ, so 'identity' is not trivially true of any two modules. (5) MONKEYPATCH control: assigning through the alias (`BR.extract_belief_assertions = stub`) is observed on the organ -- excludes the star-import failure mode pri 137 names. (6) E-CHECK: 6 GUM documents through the live SituationReader.read, sha256 of every non-belief situation-model field (78 per document), byte-identical on 6/6 with 0 flips -- excludes 'the alias perturbed the rest of the read via import-order side effects'. (7) POISONED IMPORT with spacy/nltk/transformers/sklearn/gensim made unimportable by a meta-path finder: the live read and the belief query both complete -- excludes a stand-in on the organ path. torch IS reachable from the read and is deliberately NOT poisoned: the chain is SituationReader.read -> hdlab/frontend.py:105 -> hdlab/attachment_arm.py:234 verbarg_arcs -> hdlab/incremental_parser.py:49 -> hdlab/grounded_similarity.py:83, and every use there is tensor arithmetic over the Lancaster/Brysbaert static norms (tensor/linalg/eigh; no nn.Module, no state_dict, no model load). Reported rather than suppressed so the judgement is on the record. (8) LANDED-STATE control: every number was produced BOTH by the in-process emulation of the alias AND on the tree with the diff actually applied, and they agree; the cell's hunk arm falls back to the pinned git blob so it keeps measuring the same two modules after the collapse lands."
files_changed: "experiments/exp_belief_one_organ_v1.py (NEW cell: arms A-G -- hunk classification from a runtime re-diff, identity+surface, equivalence on 28 documents, the instruments before/after, the E-check, the poisoned-import check, and the UD-copula prototype; --self-test, --arms, get_output_dir per Q115), verification/test_belief_reader_one_organ.py (NEW witness: 11 checks, defect-presence/defect-absence so it is can-fail on BOTH trees), notes/problems/<slug>/{SOLVED.md, belief_one_organ_patch.diff}. NO existing hdlab/, tools/ or tracked verification/experiments file was edited -- ONE proposed diff, `git apply --check` CLEAN at HEAD, covering 4 files: (1) experiments/_belief_reader.py -> a 44-line sys.modules alias (456 lines deleted); (2) hdlab/situation_reader.py, COMMENT LINES ONLY (:1210, :1216, :2949 -- the three places that still told the reader it imports experiments._belief_reader; 7 lines, no code); (3) experiments/exp_belief_extraction_drill_v1.py -- the STATE_REGISTER arm (which called the copy with a spaCy nlp) becomes ORGAN_STATUS on the organ's own status path, `status_register_recall` is retired in favour of `status_organ_recall` + `status_in_substrate_recall`, and a STRUCTURAL `measured_module_is_the_live_organ` field is emitted; (4) verification/test_belief_at_t_end_to_end_organ.py -- W15 repinned, the old claim withdrawn WITH its number, replaced by three can-fail claims (the location parser-recall gap; the drill measures the live module; ONE status path). Line endings preserved per file (the tree is mixed: situation_reader.py is CRLF with an 8-line LF island, the drill and the witness are LF)."
reverify: ".venv/Scripts/python.exe verification/test_belief_reader_one_organ.py    # green on BOTH trees and says which one it is on; then, with the diff applied: .venv/Scripts/python.exe verification/test_belief_at_t_end_to_end_organ.py (19/19) and .venv/Scripts/python.exe experiments/exp_belief_one_organ_v1.py --self-test"
---

# The belief reader: one organ, and the one number that was a phantom

**SOLVED.** The collapse is proven, and it found exactly what it was built to find: of the 51 drifted lines,
one hunk was load-bearing, and it had been holding up a witness claim for a week.

## 0. WHAT THE DISK SAYS (it outranks the brief)

1. **The brief's numbers reproduce exactly.** 51 whitespace-insensitive differing lines, 500 vs 493, five
   hunks. The importer list is 8 real importers (5 in `experiments/`, 3 in `verification/`) plus 3 files
   that only NAME the copy in prose (`hdlab/situation_reader.py` comments at :1210/:1216/:2949,
   `hdlab/entity_world_model_resolver.py:6`, and `verification/test_audit_live_standins.py:107-108`, which
   is a source-regex check, not an import). The brief said "4 verification"; it is 3 that import plus that
   one regex check.
2. 🔻 **The brief's INFERRED half was half right, and the wrong half is the whole finding.** It guessed "the
   51 lines are promotion-only plus the spaCy purge" (right) "and the belief numbers on record move little
   when pointed at the organ" (right for 18 of 19 checks, **wrong for the one that mattered**). The copy
   DID still carry a stand-in the organ dropped, and one witness was consuming it.
3. **`track_belief` defaults to `True`** (`hdlab/situation_reader.py:1003`), so the belief dimension is on
   the product path of every default read, not an opt-in. That raises the stake of the brief, not lowers it.
4. **pri 137's alias has NOT landed yet** (`experiments/_space_reader.py` is still the full 702-line copy).
   I read its diff for the mechanism as the brief instructs. The two landings are independent: my alias
   removes the belief reader's own `from experiments._space_reader import ...` line by making the organ the
   one object, and the three helpers it takes from there are byte-identical in both space modules anyway.

## 1. THE FIVE HUNKS, CLASSIFIED

Computed at run time by re-diffing the pinned pre-collapse blob (`cf4aff6f37c6`) against the organ, not
asserted in prose — so the classification itself can go red.

| hunk | what | class |
|---|---|---|
| **H1** | module docstring's own name `_belief_reader` -> `belief_reader` | promotion-only |
| **H2** | the organ-only PROMOTED provenance note (7 docstring lines) | a landing the organ got, the copy did not |
| **H3** | the organ-only `__bf_status__` / `__bf_verified__` / `__bf_note__` / `__bf_corrections__` block | a landing the organ got, the copy did not |
| **H4** | `from experiments._space_reader import ...` -> `from hdlab.space_reader import ...` | promotion-only |
| **H5** | **the spaCy STATUS branch removed from the organ** (`if nlp is not None` -> `experiments.state_register.extract_state_events`), replaced by a 7-line NOTE | a landing the organ got, the copy did not |

**The dangerous class — a change the COPY got and the organ did not — is EMPTY, and nothing is
unclassified.** That is the good news in this problem: nobody had been editing the copy. The damage came
from the copy standing still while the organ moved.

## 2. THE BAR, LINE BY LINE

### Bar 1 — ONE ORGAN ✅

`experiments/_belief_reader.py` becomes 44 lines ending in `sys.modules[__name__] = _organ`. Identity, not
equality, under **four** import spellings:

| spelling | used by | result |
|---|---|---|
| `import experiments._belief_reader as BR` | 6 importers | `is` the organ |
| `from experiments import _belief_reader as BR` | `_diagnose_tom_bottleneck.py`, `_tom_chain.py` | `is` the organ |
| `importlib.import_module("experiments._belief_reader")` | dynamic | `is` the organ |
| `from experiments._belief_reader import drive` | from-imports | the organ's own function object |

**Not a star-import**, for pri 137's reason: a star-import copies references, so `BR.f = stub` would rebind
a private name and the organ would keep running its own. The monkeypatch control confirms the difference —
assigning through the alias is observed on the organ (`True` after, `False` before).

**8 importers, all green, all reaching the organ; 50 public names checked, 0 lost.**

| file | line | statement |
|---|---|---|
| `experiments/exp_belief_at_t_end_to_end_v1.py` | 44 | `import experiments._belief_reader as BR` |
| `experiments/exp_belief_extraction_drill_v1.py` | 32 | `import experiments._belief_reader as BR` |
| `experiments/_belief_drive_scratch.py` | 11 | `import experiments._belief_reader as BR` |
| `experiments/_diagnose_tom_bottleneck.py` | 16 | `from experiments import _belief_reader as BR` |
| `experiments/_tom_chain.py` | 48 | `from experiments import _belief_reader as BR` |
| `verification/test_belief_at_t_end_to_end_organ.py` | 46 | `import experiments._belief_reader as BR` |
| `verification/test_tom_chain_landing.py` | 89 | `import experiments._belief_reader as BR` |
| `verification/test_track_belief_landing_organ.py` | 35 | `import experiments._belief_reader as BR` |

Mention-only (no import): `hdlab/situation_reader.py` :1210/:1216/:2949 (fixed by the diff),
`hdlab/entity_world_model_resolver.py:6` (a historical note in a docstring, left alone),
`verification/test_audit_live_standins.py:107-108` (asserts the reader's SOURCE contains no
`from experiments import _belief_reader` — still true, still green).

### Bar 2 — EQUIVALENCE PROVEN ✅ (28 documents, the brief asked for 9)

Population: the belief instrument's own 19 passages (`modern_items()` + `load_real()`) **plus 9 GUM
narrative documents** read through `parse_conll_sentences` the way the reader reads prose. Entry points
compared: `drive`, `extract_reality_events`, `extract_status_events`, `extract_location_events`,
`extract_belief_assertions`, `extract_inference_edges`.

* **`nlp=None` (the live semantics): 0 mismatches, 0 documents affected.** This is the product path —
  `hdlab.perceptual_access_ledger._nlp` has been hardcoded `None` since CONT-28, so every live call already
  had the organ's semantics.
* **`nlp=<spaCy en_core_web_sm>` (the H5 exposure arm): 14 mismatches across 7 of 28 documents**, and every
  one of them lands in `extract_reality_events` or `extract_status_events` — the two entry points H5
  touches, and no others. **That is what attributes the divergence to H5: where it lands, not my say-so.**
  It also proves the comparison is capable of detecting a difference, so the 0 above is a measurement.

**The organ's answer is the one kept, in every case.**

### Bar 3 — THE INSTRUMENTS RE-MEASURED ✅ (one number moved; it is reported, with its cause)

| instrument | before (copy) | after (organ) | delta |
|---|---|---|---|
| `verification/test_belief_at_t_end_to_end_organ.py` | 19/19 PASS | **18/19 PASS, W15 RED** | W15 only |
| the same witness's W2 / W3 / W6 / W9 / W11 / W19 headlines | oracle 1.000, live 0.758, floor 0.697, twin p95 0.630; real 0.857 vs 0.286; FANToM 0.893 vs 0.665 | **identical, to the digit** | 0 |
| `experiments/exp_belief_at_t_end_to_end_v1.py` full metrics dict | sha256 `9e7cdc067d30cb6f…` | sha256 `9e7cdc067d30cb6f…` | **byte-identical, 0 moved keys** |
| `verification/test_tom_chain_landing.py` | green | green (CHAIN 0.655, FB 0.669 vs floor 0.237) | 0 |
| `verification/test_track_belief_landing_organ.py` | green | green (3/3) | 0 |
| `verification/test_audit_live_standins.py` | green | green (3/3) | 0 |
| **the drill's `status_register_recall`** | **0.600** | **0.000** | **−0.600** |

**No belief-fed board row exists.** The board's rows are built in
`experiments/exp_board_rows_on_the_reader_v1.py`; nothing there reads `sm.believes` / `sm.knows`. So bar 3's
"any belief-fed board row" is answerable only as: there is none, and the belief dimension is computed on
every default read and never scored on the board. (Same shape as pri 137's finding for `sm.locations`.)

**No CI is quoted for the moved number** because it has none: the drill's recall is a raw
matched/total over 10 gold status events, not a bootstrapped estimator. `0.600 -> 0.000` is 6 of 10 events
recovered by the spaCy branch and 0 of 10 by the organ; I am not going to dress a count of 10 in a
confidence interval.

### Bar 4 — NO STAND-IN ✅

A meta-path finder makes `spacy`, `nltk`, `transformers`, `sklearn` and `gensim` raise on import. The check
asserts **the poison bites first** (`import spacy` raises with the poison's own message), then runs the
live `SituationReader().read()` on GUM documents and calls `sm.believes(...)`. Both complete.
`PerceptualAccessLedger()._nlp is None` is asserted on the same path.

🔻 **One thing I found and did not suppress: `torch` IS importable from the live read, and I deliberately
left it out of the poison set.** The chain is `SituationReader.read` -> `hdlab/frontend.py:105 parse` ->
`hdlab/attachment_arm.py:234 verbarg_arcs` -> `hdlab/incremental_parser.py:49` ->
`hdlab/grounded_similarity.py:83 import torch`. Every use of torch there is `torch.tensor` /
`linalg.vector_norm` / `dot` / `eigh` over the Lancaster sensorimotor + Brysbaert concreteness norms — a
vetted static offline FOUNDATION asset. **No `nn.Module`, no `state_dict`, no model load.** That is numpy
with another name, not an off-the-shelf model, so poisoning it would have measured the wrong thing. The
judgement is recorded in the metrics (`torch_reachable_from_the_read_but_admissible`) rather than hidden by
a quietly narrowed poison list. **If strategy disagrees with that call, the finding is already on the
record and the poison set is one list literal.**

I also had to separate **corpus preparation from inference**: the GUM scaffold (`experiments.gum_coref` ->
the name gazetteer) imports torch at module level, so the conll files are written BEFORE the poison goes in.
Everything after the poison is the read. Without that split the check was measuring the test harness.

### Bar 5 — NOTHING ELSE CHANGES ✅

**6 of 6 GUM documents byte-identical over 78 non-belief situation-model fields, 0 flips** — entities,
events, coref resolutions, timeline frames, causal links, entity states, pronoun abstentions, suppressed
predicates, the lot, each sha256'd, through the live `SituationReader().read`. `believes` / `knows` are
excluded only because they are per-read closures whose identity is not comparable.

## 3. THE FINDING: W15 WAS MEASURING A PHANTOM, AND UNDERNEATH IT IS A REAL GAP

**The claim as it stood:** *"status = the promoted STATE_REGISTER organ recovers MORE than a stronger
parser (not intrinsic)"*, on `status state_register 0.6 > parser 0.4`.

**What produced the 0.600:** `experiments/exp_belief_extraction_drill_v1.py:117` called
`BR.extract_reality_events(sents, by_sent, fact, nlp=<spaCy>)`. On the **copy**, a non-None `nlp` routed
the status path into `experiments.state_register.extract_state_events` — spaCy at inference. The
2026-09-09 promotion **deleted that branch from the organ** because the live reader always passes
`nlp=None`. So the number described a module the product does not run, and it said the opposite of the
truth: it said the status wall was closed by the right organ.

**On the organ: 0.000 of 10 gold status events** — with or without an `nlp` (the organ has one status path).

### Why the organ recovers nothing, traced to the line

Not "the extractor is weak". It **cannot fire at all**, and the reason is a hand-off mismatch one rung
upstream:

```
extract_status_events (in-substrate branch):
    subj = [k for k in range(1, len(toks)+1) if heads.get(k) == v]     # v = the COPULAR verb
```

It looks for the subject **of the copula**. The reader's own parser produces the **UD** analysis, in which
the copula is a DEPENDENT of the predicate:

```
The lamp was lit .        upos  The/DET lamp/NOUN was/AUX lit/VERB ./PUNCT
                          heads {1: 2, 2: 4, 3: 4, 4: 0, 5: 4}
                                 ^lamp -> lit    ^was -> lit    ^lit = ROOT
```

`lamp` attaches to `lit`, `was` attaches to `lit`, and **nothing attaches to `was`**. So `subj` is `[]` on
every copular clause the reader parses, on all 10 items. The extractor was written for a
**copula-as-head** analysis — which is exactly what spaCy produces (`was` heads `nsubj` + `acomp`) — and
hunk H5's spaCy branch had been masking the mismatch since the extractor was written.

### Prototyped past it, in the cell, with a twin

Read the copular clause the way UD encodes it — predicate = head, copula = its `cop` dependent, subject =
the predicate's other dependent — keeping the organ's own veridicality gate (a state inside a REPORTED
clause is the content of a report, not asserted reality; factive verbs are deliberately NOT report cues,
Kiparsky & Kiparsky 1970, which is why *"Nell knew the bridge was safe"* SHOULD fire):

| arm | recall (n = 10 gold status events) |
|---|---|
| the organ as shipped (the strongest real floor) | **0.000** |
| **the UD-copula prototype** | **0.500** |
| shuffled-vocabulary twin (same firing opportunities, no fact-specific content) | **0.100** — LOSES by 0.400 |
| *(for reference: the copy's retired spaCy number)* | *0.600* |

**It is NOT landed.** Bar 5 of this brief is "nothing else changes", and a status-extractor repair is a
different change with its own consumers. It is handed to strategy as a measured, located repair with the
mechanism written out, and the exact prototype is `_ud_copular_status_events` in
`experiments/exp_belief_one_organ_v1.py`.

### What I did to W15 instead

The brief says: *never keep the copy alive for that witness*. So the diff **retires the phantom arm** —
the drill's `STATE_REGISTER` arm becomes `ORGAN_STATUS` on the organ's own status path, and
`status_register_recall` is replaced by `status_organ_recall` + `status_in_substrate_recall` — and repins
W15 to three claims that can fail:

1. the location gap is **parser recall** (spaCy 0.917 > in-substrate 0.708) — unchanged, still routes to p2;
2. **STRUCTURAL: the module the drill measured IS the module the reader runs.** This is the check that did
   not exist and whose absence cost a week. It now fails loudly instead of passing vacuously;
3. **ONE STATUS PATH**: the dispatcher and the status extractor agree exactly, i.e. no second status
   implementation is hiding behind an `nlp` argument.

The organ's 0.000 is **REPORTED, not pinned as a number** (the README's rule that a witness pins claims),
with the located cause in the drill's own `verdict["status"]` string so anyone reading the metrics gets the
diagnosis, not just the zero.

## 4. THE OWNER'S PUSH SCRIPT, ANSWERED WITH NUMBERS

**(i) Is the organ's path brain-foundational at every rung it reads?** Three rungs, and one is not.

* **The ledger — YES.** `hdlab.perceptual_access_ledger._nlp` is `None` (CONT-28); the RULE0/RULE1/RULE2
  registration gate runs substrate-native. Asserted under the poisoned import.
* **Events — YES.** Reality events and belief assertions come from the organ's own extractors over the
  reader's own glass-box parse (`hdlab.pos_tagger` + `hdlab.arc_parser` +
  `hdlab.predicate_argument_frontend`). No external tool.
* 🔻 **Mentions — NO, and this is the second located defect.** `hdlab/situation_reader.py:2965` builds
  `by_sent = {i: [] for i in range(len(sents))}` and hands the organ an **EMPTY nominal-mention stream**.
  `by_sent` is what the organ's `_cluster_covering(noms, k-1)` reads to bind the tracked fact-entity by
  **coref cluster** instead of by literal surface form. With an empty stream that arm is dead on the live
  path and in all 11 other call sites (`grep -rn "by_sent = {i: \[\] for i"` — 12 hits, every one empty).
  **And the reader has the stream right there**: fifteen lines earlier, at `:4995`, the SPACE dimension
  receives `mentions=role_mentions` (pri 125's hand-off); at `:5012` BELIEF receives `(sm, sents)` and
  nothing else. `role_mentions` is in scope at the call site. **This is the same hand-off defect pri 137
  found for SPACE, on the belief dimension, and it is one parameter wide.**

**(ii) Any wall in the belief instruments now that they run the organ? Prototyped past it.** The only
number that moved is the status reality channel at 0.000, and it is not a wall: it is a parse-convention
mismatch, diagnosed to the line and prototyped to 0.500 with a losing twin (§3). The two remaining
shortfalls in the instrument were already routed before this brief and are unchanged by it: the location
channel's parser-recall gap (in-substrate 0.708 < spaCy 0.917 -> p2, the incremental parser) and the
perception channel's live 0.636 vs the dominant channels' 1.000.

**(iii) Is the wiring alone sufficient? What upstream gap remains, with its number?** The wiring is
sufficient for the bar — it makes the instruments measure the product — but it is **not** sufficient for the
belief dimension to work. Three named gaps, in the order I would take them:

1. **The UD copula hand-off** — status reality recall **0.000 -> 0.500** prototyped, twin 0.100 (§3).
2. **The empty mention stream** — the coref-binding arm of the fact-entity match is dead on the live path
   (§4.i). Unmeasured as a delta because measuring it requires the hand-off to exist; the SPACE precedent
   (pri 137) is that the same hand-off was worth **0.0426 -> 0.4043** there.
3. **The parser** — location extraction 0.708 in-substrate vs 0.917 with a stronger parse. This is the
   shared mega-cluster in `CROSS_SOLUTION_IMPROVEMENT_MAP.md`; I flag it as consumed-input, not as mine.

**(iv) Anything frozen on this path that needs an observe path?** Yes, and it is the whole cue layer.
`COPULAR` (18 verbs), `PLACE_TRANSFER` (34), `MENTAL_VERBS`, `HEAR_VERBS`, `TELL_VERBS`, `_REPORT_CUES`
(30) and `_TESTIMONY_VALUE` are **hand-written frozen lexicons** in the organ. The brain does not freeze
cue validities; it learns them from decoded outcomes over a lifetime. Nothing in the belief organ observes
or updates. That is a real fidelity gap, out of scope for a collapse brief, and it is the shape the
project already has machinery for (`hdlab/learner`). Naming it, not fixing it.

**(v) Prior work on disk — read, not recalled.** pri 137's `SOLVED.md` (50 KB) and its
`space_ground_lever_patch.diff`: I took the `sys.modules` mechanism verbatim, the star-import argument
verbatim, the equivalence-proof shape, the E-check shape, and the defect-presence/defect-absence control.
LOCATED item 15's repair is at `experiments/exp_belief_at_t_end_to_end_v1.py:121-135` — the `if _nlp is not
None` gate plus the in-substrate re-drive, with the honest `[spacy arm]` banner saying the arm is an
identical-source control and not a stronger parser. **I left it untouched and it stays green**; my drill
repair is the same defect one file over, and I copied its honesty (say what the arm actually is, in the
output).

**(vi) My own negatives, audited.**
* *Did I attribute the 14 H5 mismatches to H5 because it was convenient?* No — they land in exactly the two
  entry points H5 touches and nowhere else, and the `nlp=None` arm's 0 mismatches independently rules out
  H4. I also diffed the three space helpers the belief path actually uses and they are byte-identical.
* *Is "0.000" an artifact of my population?* No — the same 10 gold status events give the spaCy branch
  0.600 and a stronger parser 0.400, so the population is answerable; only the organ's branch is at zero.
* *Did I narrow the poison list to get a green?* I narrowed it once, from a set including torch, and the
  reason is written into the code and into §2 bar 4 with the import chain. The finding is reported, not
  deleted.
* *Is the prototype's 0.500 real or a two-item fluke?* n = 10 gold events over 9 items; 5 recovered. The
  twin at 0.100 says the content is doing the work, not the firing rate. I would not quote 0.500 as the
  organ's status recall — it is a prototype number, and it is labelled as one everywhere it appears.
* *A defect in my own witness, found and fixed:* the first version poisoned torch and measured the GUM
  scaffold rather than the read. It went red for the right reason and I fixed the check, not the claim.
* *A process slip I made and corrected:* my first patch normalised line endings and produced a 1,540-line
  diff with whole-file hunks that would have looked like a rewrite of two files. The tree is mixed (CRLF
  with an 8-line LF island in `situation_reader.py`; LF in the drill and the witness). Regenerated
  byte-faithfully: 728 lines, and the only whole-file hunk is the one that IS a whole-file replacement.

**(vii) Repeat (ii) until no wall is left untried.** Gap 1 is prototyped and measured. Gap 2 is located to
two line numbers with the precedent's number attached. Gap 3 is not mine and is already the fleet's
biggest open problem. **I am not claiming a wall anywhere in this problem.**

## 5. KEY REALIZATIONS

* **The equivalence proof that says "0 mismatches" is worthless unless the same comparison is shown to
  detect a real one.** Running the identical 28-document comparison with a spaCy `nlp` turned the zero from
  an absence of evidence into evidence of absence — and it handed me the attribution for free, because the
  mismatches landed only where the hunk lives. *A control that finds nothing has not been run; a control
  that finds the thing you deliberately put there has.*
* **Measure the retired arm directly, not through the instrument you are about to repair.** My first arm D
  ran the drill before and after and would have shown `0.000 -> 0.000` once the drill was fixed — the
  evidence for the whole finding would have vanished into my own repair. Re-deriving `0.600 -> 0.000` from
  `extract_reality_events(..., nlp=<spaCy>)` on the raw items keeps the phantom on the record permanently.
* **A witness for a defect should detect which tree it is on and assert the matching state.** pri 137's
  defect-presence/defect-absence control is the reason my witness is green and can-fail *before* the
  landing as well as after, instead of being a red file everyone else has to step around while strategy
  gets to it.
* **"The number moved" and "the number was always wrong" are different findings.** The belief headline did
  not move at all — it was organ-true all along, because `_nlp` was already `None`. What moved was a number
  produced by a code path nothing live could reach. *The phantom was not in the answer; it was in the
  diagnosis of why the answer was short — and a wrong diagnosis is worse than a wrong number, because it
  closes an investigation.* W15 was telling us the status wall had been solved by the right organ. It had
  not been solved at all, and the extractor supposed to solve it cannot fire.
* **When a promotion deletes a branch, the fallback it falls through to has never been tested.** H5 removed
  spaCy and left `nlp` in the signature "for caller compatibility (ignored)". That is a silent
  behaviour change for every caller that was passing one, and the in-substrate fallback underneath it had
  been dead code from the day it was written. *Deleting a branch is a landing; the thing underneath it
  needs its own number before you can call the deletion clean.*

## 6. ADJACENT COMPONENTS (candidate follow-on problems, in priority order)

1. **The UD copula hand-off in `hdlab/belief_reader.extract_status_events`.** Measured: 0.000 -> 0.500
   (n=10), twin 0.100. Prototype on disk in `exp_belief_one_organ_v1._ud_copular_status_events`. **Check
   `hdlab/state_register.py` and `hdlab/entity_states` for the same copula-as-head assumption before
   landing** — the same mismatch may be costing the copular is-a organ too, and that one IS on the board.
   *Brain status: the extractor is OUR-INVENTION; the UD re-read is a faithfulness repair to the parse the
   reader actually produces, not a new mechanism.*
2. **The empty mention stream into the belief dimension** (`hdlab/situation_reader.py:2965` vs `:4995`).
   One parameter. The SPACE precedent moved that dimension 0.0426 -> 0.4043.
3. **The belief dimension has no board row** although `track_belief` defaults ON and it is computed on
   every default read. Same finding pri 137 reported for `sm.locations`. **Two dimensions now compute on
   every read and are scored by nobody** — that is a pattern, not a coincidence, and it is worth one audit
   pass over all of `track_*`.
4. **The frozen cue lexicons** (§4.iv) — no observe path anywhere in the belief organ.
5. 🔻 **The remaining promoted-away copies.** This problem and pri 137 are two instances of one defect
   class. **A cheap standing check would be: for every `hdlab/X.py` with an `experiments/_X.py`, assert the
   two are one object.** `hdlab/entity_world_model_resolver.py:6` still names `_space_reader` /
   `_belief_reader` in its docstring, which is how I would look for the next one.

## 7. WHAT I WOULD WITHDRAW FIRST IF IT TURNED OUT TO BE WRONG

**The prototype's 0.500.** It is n=10 on the belief gold's own status items, it is not landed, and it has
not been run against a second population or checked for what it breaks on the location channel. Everything
else here is structural (identity, surface, byte-identical digests) or is a straight recount of the same 10
events through two code paths, and I would defend those. The 0.500 is the number most likely to shrink.

Second, **the "torch is admissible" call**. I am confident about the evidence (no `nn.Module`, no
`state_dict`, no model load — it is `eigh` over a CSV of norms) and less confident that the project wants
torch on the read path at all. That is a judgement for strategy, and I have put it where it can be
overruled rather than where it would be missed.

## 8. AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

* `hdlab/belief_reader.py` — `__bf_status__ = 'BF_SPIRIT'`, verified 2026-09-09, is **still accurate for
  the driver**, but the entry should record that **one of its extractors is dead against the reader's own
  parse**: `extract_status_events`'s in-substrate branch recovers 0.000 of 10 gold status events because it
  assumes a copula-as-head analysis the reader never produces. A driver that composes correctly onto a
  channel that cannot fire is not the same as a working channel.
* **New deviation to record on `hdlab/situation_reader.py`:** the belief dimension is handed an empty
  nominal-mention stream (`:2965`) while the space dimension beside it is handed the reader's own
  (`:4995`). The organ's coref-binding arm is therefore unreachable on the live path.
* **Correction to the audit's picture of the 2026-09-09 spaCy purge:** it is recorded as complete for
  `hdlab/`, and it was — but the *measurement* of the purged channel was still running through the
  promoted-away copy's spaCy branch for a week afterwards. The purge and the purge's *witness* are two
  different landings.

---

## SUBMISSION PROMPT

```
Problem: the_belief_reader_exists_twice_the_live_reader_runs_hdlab_belief_reader_while_every_belief_cell_and_witness_still_measures_the_drifted_experiments_copy_collapse_to_one_organ_with_an_alias  (pri 139)

SOLVED. experiments/_belief_reader.py becomes a sys.modules alias of hdlab.belief_reader (500 -> 44
lines): identity under all 4 import spellings, 8 importers green and reaching the organ, 50 public
names checked and 0 lost. Equivalence proven on 28 documents x 6 entry points: 0 mismatches at
nlp=None (the live semantics); the same comparison with a real spaCy nlp finds 14 mismatches in
exactly the 2 entry points hunk H5 touches, so the zero is a measurement, not a blind spot. E-check:
6/6 GUM docs byte-identical over 78 non-belief situation-model fields, 0 flips. Poisoned import
(spacy/nltk/transformers/sklearn/gensim): the live read and the belief query both complete.

ONE NUMBER MOVED, AND IT WAS A PHANTOM. W15 of test_belief_at_t_end_to_end_organ.py claimed "the
promoted STATE_REGISTER organ recovers MORE than a stronger parser" on status_register_recall 0.600.
That call passed a spaCy nlp into the COPY's `if nlp is not None` branch, which the 2026-09-09
promotion deleted from the organ. On the organ: 0.000 of 10 gold status events. 18 of 19 checks are
numerically identical and the belief end-to-end cell's full metrics are byte-identical (same sha256),
so the belief headline was organ-true all along -- what was wrong was the DIAGNOSIS of why it falls
short.

ROOT CAUSE, TRACED AND PROTOTYPED PAST: extract_status_events looks for the subject OF THE COPULA, but
the reader's own parser is UD -- "The lamp was lit" gives heads {1:2, 2:4, 3:4, 4:0}: the subject
attaches to the PREDICATE and nothing attaches to the copula, so subj is [] on every copular clause.
The extractor was written for a copula-as-head analysis (spaCy's), and the removed spaCy branch had
been masking it. A UD-shaped re-read scores 0.500 vs the organ's 0.000, shuffled-vocabulary twin
0.100. NOT LANDED (bar 5 is "nothing else changes") -- handed over as a measured repair.

SECOND DEFECT LOCATED, NOT FIXED: hdlab/situation_reader.py:2965 hands the belief organ an EMPTY
mention stream, so its coref-binding arm is dead on the live path -- fifteen lines earlier at :4995
the SPACE dimension receives mentions=role_mentions. Same hand-off defect pri 137 found for space,
one parameter wide.

Files: experiments/exp_belief_one_organ_v1.py (NEW cell, arms A-G, --self-test),
verification/test_belief_reader_one_organ.py (NEW witness, 11 checks, defect-presence/absence so it
is can-fail on both trees), notes/problems/<slug>/{SOLVED.md, belief_one_organ_patch.diff}.
No hdlab/ or tracked verification file was edited -- ONE diff, `git apply --check` CLEAN at HEAD,
4 files (the alias; situation_reader COMMENT LINES ONLY at :1210/:1216/:2949; the drill's phantom arm
retired; W15 repinned to three can-fail claims incl. a STRUCTURAL "the drill measures the module the
reader runs").

Reverify: .venv/Scripts/python.exe verification/test_belief_reader_one_organ.py
Then with the diff applied: verification/test_belief_at_t_end_to_end_organ.py (19/19).
```
