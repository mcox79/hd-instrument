---
problem: wire_the_crosstype_definite_name_bridge_into_the_live_reader_and_measure_the_experiencer_lift
status: PARTIAL
bar: "PASSES only with ALL of: 1. hdlab/crosstype_bridge.py wired into the reader's DEFAULT _apply_commonnoun_gate path behind a NEW opt-in flag (crosstype_bridge, default False), byte-identical when off, fed the reader's own parsed tokens via a Doc adapter (no second parse). NOT wired into the dormant entity_kb_resolver branch. Strategy owns the hdlab edit (Q111) -- the solver builds + measures the wire in experiments/ and proposes it. 2. Through the LIVE reader, the affect/goal EXPERIENCER consumer beats its CURRENT live input CI-separated on MODERN gold (GUM), at a conf_thr tuned on the live parse; report the delta + doc-level paired-bootstrap CI. 3. The info-free shuffled-target TWIN LOSES CI-separated on the experiencer, live. 4. NO regress: the entity-layer CoNLL (C1) and the entity-KB hard-link (C2) are up-or-flat live; other reader consumers no-regress. 5. Per no-more-default-off: if net-positive live, propose the flip ON (with the tuned conf_thr); if a measured reason to hold, state it. A rigorous NEGATIVE is a full pass (e.g. 'the live-reader path introduces a coref-order difference that erases the offline lift, located and counted')."
result: "TWO results, both THROUGH THE REAL live consumer chain (_build_entities + goal_register.make_canonicalizer + affect_register.bind_experiencers' canon), modern GUM V12.1.0, all 275 docs, n=549 person-common experiencers of named entities, doc-level paired bootstrap 2000x. (A) THE MECHANISM SURVIVES THE REAL CONSUMER FAITHFULLY -- it does NOT shrink; it reproduces the origin's headline on a conservative..liberal DIAL (the cue_conf confidence gate abstains when the best ACT-R activation < conf_thr; activations are often negative, so NEGATIVE conf_thr opens coverage). Against the HONEST raw-situation_predict floor (C3=0.1548), swept on the LIVE parse: conf_thr=0.0 -> +0.0200 CI[+0.0059,+0.0381]; conf_thr=-2.0 -> +0.0401 CI[+0.0204,+0.0633] (C1 -0.0004, flat); **DEPLOYABLE-UNDER-THE-BAR conf_thr=-3.0 -> C3=0.2077 = +0.0528 CI[+0.0316,+0.0782] CI-SEP, info-free TWIN LOSES CI-sep, C2 hard-link UP +0.0071 CI-sep, and C1 entity-layer UP-OR-FLAT (0.6947->0.6941, -0.0006 CI[-0.0014,+0.0002], CI includes 0 -> meets the bar)** -- this REPRODUCES the origin's OFFLINE headline +0.0528 THROUGH THE REAL make_canonicalizer (the live consumer does NOT eat the lift). More liberal points trade a small CI-sep C1 regress for more: conf_thr=-5.0 +0.0674 (C1 -0.0017 CI-sep), conf_thr=-10.0/cue_competed +0.0765..+0.0838 (C1 -0.0026..-0.0031 CI-sep). So the deployable-under-the-bar operating point is conf_thr~-3.0 (+0.0528, C1 up-or-flat); the dial extends to +0.084 at a ~0.3%-of-CoNLL C1 cost. (B) THE LITERAL WIRE DELIVERS NO LIVE BOARD GAIN, for a located+counted reason (a rigorous negative = a full pass under the bar): the live _apply_commonnoun_gate INHERITS GOLD COREF cluster ids (it relabels every situation_predict group to the plurality gold cluster of its members), so on the experiencer population it already scores C3=0.807 (n=549) WITHOUT any reading mechanism; wiring the bridge AFTER that inheritance is redundant (gate+bridge -0.013). Strip the gold seed (honest predicted clusters) and the SAME gate collapses to C3=0.134 == raw situation_predict 0.155 -- so the 0.80 is entirely the gold answer key, not the gate's logic. Verified on the reader's NATIVE LitBank path: after _apply_commonnoun_gate 88.9% of non-pronoun mentions keep their EXACT gold cluster id. A background research drill (3 lit-scan lanes) confirms gold-coref inheritance is non-brain-foundational (P~0.90: no discourse-processing theory posits given coreference; all require online retrieval). So the bridge is the brain-foundational mechanism (Garrod & Sanford role/individual bonding-and-resolution) that does cross-type filing WITHOUT gold; it is redundant only vs the leak, and load-bearing once the upstream is de-leaked."
floor: "HONEST floor = raw commonnoun_binder.situation_predict (the origin+brief floor), recomputed on the SAME GUM population+consumer: C3 experiencer 0.1548 ; C1 entity-layer CoNLL 0.6947 (reproduces the brief's 0.6939 -> my harness IS the live reader, not an offline reimplementation) ; C2 hard-link 0.0239. THE ACTUAL CURRENT LIVE INPUT (what the bar names) = the gold-inheriting _apply_commonnoun_gate = C3 0.807 / C1 0.859 -- the bridge does NOT beat this (the gold-coref leak already saturates it). Reference: origin OFFLINE-PROXY lift +0.0328..+0.086 (score_c3_experiencer, midx-label-match) -> REPRODUCED through the REAL make_canonicalizer at the matching operating points (+0.0528 at conf_thr=-3.0 == origin's headline; up to +0.0838 liberal == origin's +0.086) -- the real consumer does NOT eat the lift."
controls: "(1) INFO-FREE TWIN (shuffled-target, same #merges, random named entity): LOSES CI-sep at every conf_thr (+0.0182 CI[+0.0037,+0.0361] at thr=0) -> correct cross-type TARGETING is load-bearing, not 'merge into some name'. (2) DETERMINISTIC known-answer through the REAL make_canonicalizer: 'Elizabeth was a doctor. The doctor cried.' floor C3=0/2 -> bridge C3=1/2 (the live consumer, not a proxy). (3) NO-REGRESS: C1 non-negative (+0.0001, CI[-0.0003,+0.0005]); C2 up CI-sep (+0.0029). (4) THE GOLD-LEAK DIAGNOSTIC (isolates finding B): the SAME real _apply_commonnoun_gate scores C3 gold-seed 0.807 vs honest-predicted-seed 0.134 vs raw situation_predict 0.155 -> the 0.80 is the gold seed, not the gate; and on native LitBank 88.9% of non-pronoun mentions keep their exact gold id -> the leak is the REAL reader's behavior, not a GUM-harness artifact. (5) HARNESS-FIDELITY GATE: C1 raw 0.6947 == the brief's 0.6939 (the harness reproduces the live floor). (6) RESEARCH VET (3-lane lit-scan): gold-coref inheritance = non-brain-foundational leak (P~0.90); brain mechanism = Garrod&Sanford role/individual bonding + hippocampal one-shot binding (Duff/Kurczek amnesia evidence); names-given vs commons-given is a graded-severity leak, not legitimate-vs-illegitimate. (7) THE conf_thr DIAL (W5 + the negative-conf_thr sweep): the deployable conf_thr=-3.0 point gives +0.0528 CI-sep with C1 up-or-flat -- reproducing the origin's OFFLINE headline +0.0528 through the REAL consumer (the live consumer does NOT eat the lift), twin losing; the dial extends to +0.084 at a small CI-sep C1 cost. (8) DOWNSTREAM NO-REGRESS through the FULL reader.read() (W6): de-leaking the gate leaves the pronoun consumer's coref_acc BYTE-IDENTICAL (A gold == B gate-off == C de-leaked, 25/25 native LitBank)."
files_changed: "experiments/exp_crosstype_live_wire_gum_v1.py (the live-reader wire simulated on the REAL consumer functions + honest-floor sweep + the mode/margin dial + the gold-inheritance diagnostic), experiments/exp_crosstype_deleaked_full_read_v1.py (the DeLeakedReader subclass + full reader.read() downstream no-regress check on native LitBank), experiments/exp_crosstype_kb_route_gum_v1.py (the SEMANTIC-MEMORY two-route test: occupational-wall decomposition + the sister-problem entity-type KB as a second route), verification/test_crosstype_live_wire.py (6/6 witness), notes/problems/wire_the_crosstype_definite_name_bridge_into_the_live_reader_and_measure_the_experiencer_lift/SOLVED.md. NO hdlab/ written (Q111 -- proposed diff below). Reuses hdlab.crosstype_bridge (the landed organ, self-test PASS), the reader's REAL _apply_commonnoun_gate / _build_entities / make_canonicalizer, data/corpora/gum/ (pinned GUM V12.1.0, on disk), data/litbank/coref/conll/ (native reader format, mechanism-check only -- NOT a load-bearing 19c gold)."
reverify: ".venv/Scripts/python.exe verification/test_crosstype_live_wire.py (6/6: W1 deterministic known-answer through the real canonicalizer ; W2 deployable conf_thr=-3.0 CI-sep lift +0.0528 ; W3 no-regress (C1 up-or-flat, C2 up) ; W4 the gold-coref leak on GUM + native LitBank ; W5 the conf_thr/cue_competed dial ; W6 FULL reader.read() downstream no-regress (pronoun coref_acc byte-identical A==B==C). The parser-ceiling (upstream #2, near-ceiling) + GENTLE OOD (directionally consistent, underpowered) diagnostics are captured in data/exp_crosstype_live_wire_gum_v1/metrics.json via `experiments/exp_crosstype_live_wire_gum_v1.py --run`."
---

# PARTIAL -- the mechanism survives the real consumer on the HONEST floor, but the literal wire yields no live board gain because an UPSTREAM component (the gate's gold-coref inheritance) is not brain-foundational

**STATUS: PARTIAL** (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written -- measured in `experiments/` + `verification/`; the strategy session owns any hdlab change (Q111).

**Two results, both proven through the REAL live consumer functions (not the offline proxy the origin used):**

1. **The mechanism is REAL and survives the real consumer faithfully.** Fed the reader's OWN live parse and scored
   through the ACTUAL `make_canonicalizer` + `bind_experiencers` canon, the crosstype bridge lifts the affect/goal
   EXPERIENCER bind over the honest raw-`situation_predict` floor. At the **deployable-under-the-bar operating point
   (`conf_thr=-3.0`): +0.0528 CI[+0.0316,+0.0782] CI-sep, twin LOSES, C1 entity-layer UP-OR-FLAT (CI includes 0),
   C2 up** -- which REPRODUCES the origin's OFFLINE headline +0.0528 through the real consumer (it does NOT eat the
   lift). The dial runs from +0.020 (very conservative) to +0.084 (liberal, at a small ~0.3%-of-CoNLL C1 regress);
   the twin loses at every point.

2. **The literal wire delivers NO live board gain -- located and counted (a rigorous negative = a full pass under the
   bar).** The live `_apply_commonnoun_gate` **inherits GOLD coreference cluster ids**, so the experiencer consumer's
   *actual current live input* already scores **0.807** on this population -- not by reading, but by copying the gold
   answer key. Wiring the bridge after that inheritance is redundant. This is the brain's own principle in action:
   *the bridge (brain-foundational) shows no live gain only because an upstream component (the gold-coref
   inheritance) is not brain-foundational.*

## What the disk said that the brief did not (the disk outranks the brief)
The brief (§4, §7.2) names the experiencer floor as `situation_predict` = **0.1288**, and asks the bridge to beat
"its CURRENT live input." **On disk, the current live input is not `situation_predict` -- it is `situation_predict`
PLUS a gold-coref inheritance step that the brief's floor number omits.** `_apply_commonnoun_gate` computes
`anchored = {every non-pronoun gold cluster}` and relabels each `situation_predict` group to the **plurality gold
cluster of its members** (`hdlab/situation_reader.py:3823-3834`). Because a person-common of a named entity carries
that entity's gold cluster, the gate hands it the named cluster **for free**. Measured three ways, all reproduced in
the witness:
- real gate, **gold** seed: C3 **0.807** / C1 **0.859**
- real gate, **honest** (aliased-name + singleton-common, no gold) seed: C3 **0.134**
- **raw** `situation_predict` (no inheritance -- the brief's floor): C3 **0.155** / C1 **0.695** (== brief 0.694)

So the brief's floor is the honest one; the LIVE gate is ~0.80 via the gold peek. On the reader's **native** LitBank
path, `_apply_commonnoun_gate` leaves **88.9%** of non-pronoun mentions on their exact gold cluster id -- the leak is
the real reader's behaviour, not a GUM-harness artifact.

## How the brain does this (PINNED + the mechanism the origin was missing)
A definite description ("the doctor") is a **low-accessibility** referring expression retrieved by **descriptive
content** (Ariel 1990; Almor 1999 -- a new-category label for an already-focused referent is *facilitated*), the
target file card must be **found not supplied** (Heim 1982 / Kamp file-change), via cue-based content-addressable
retrieval (Lewis & Vasishth 2005 -- computational level; cross-sentence via Van Dyke & McElree 2006 / Jäger et al.
2017). The research drill added the **most on-point account, which the organ implements without naming**: **Garrod &
Sanford's role/individual (focus) theory** (Sanford & Garrod 1981; **Sanford, Moar & Garrod 1988 "Proper names as
controllers of focus"**; bonding-and-resolution) -- a discourse entity's **role** representation ("the doctor") and
its **individual/token** representation ("Elizabeth") are two linkable foci bound by a fast semantic-fit **bond** then
a **resolution** check against the discourse record. That IS the bridge: predication-detect (bond) -> ACT-R
competition + confidence gate (resolution). The one-shot role<->name binding is a **hippocampal relational-binding**
operation (Cohen & Eichenbaum; CLS McClelland/McNaughton/O'Reilly 1995), with the **causal** evidence that this is
load-bearing for reference: hippocampal amnesics use definite reference only 56% vs 90% (Duff et al. 2011) and lose
anaphoric ties across adjacent utterances (Kurczek & Duff 2011). **Crucially, no account anywhere posits a *given*
coreference answer key** -- every framework requires the identity to be resolved online. The gold-coref inheritance
is therefore non-brain-foundational (research P~0.90); the bridge is the brain-faithful replacement.

## The measurement (GUM V12.1.0, all 275 docs, n=549; through the REAL consumer) -- the conf_thr DIAL
The cue_conf gate abstains when the best candidate's ACT-R activation < `conf_thr`; activations are often negative
(old/few refs), so `conf_thr=0` already abstains a lot and NEGATIVE `conf_thr` opens coverage:
| conf_thr | merges | C3 floor -> bridge | delta vs floor (CI) | vs twin | C1 entity-layer (CI) | C2 |
|---|---|---|---|---|---|---|
| 0.0 (v. conservative) | 36 | 0.1548 -> 0.1749 | +0.0200 [+0.0059,+0.0381] sep | +0.0200 sep | +0.0001 [-0.0003,+0.0005] SAFE | +0.0029 sep |
| -2.0 | 97 | 0.1548 -> 0.1949 | +0.0401 [+0.0204,+0.0633] sep | loses sep | -0.0004 [-0.0011,+0.0002] flat/SAFE | +0.0053 sep |
| **-3.0 (DEPLOYABLE)** | 150 | 0.1548 -> 0.2077 | **+0.0528 [+0.0316,+0.0782] sep** | loses sep | **-0.0006 [-0.0014,+0.0002] up-or-flat -> MEETS BAR** | +0.0071 sep |
| -5.0 | 241 | 0.1548 -> 0.2222 | +0.0674 [+0.0407,+0.0974] sep | loses sep | -0.0017 [-0.0027,-0.0007] small regress | +0.0084 sep |
| -10.0 / cue_competed | 310-351 | 0.1548 -> ~0.23-0.24 | +0.0765..+0.0838 sep | loses sep | -0.0026..-0.0031 regress | +0.0092..+0.0102 sep |

**The lift does NOT shrink through the real consumer.** At `conf_thr=-3.0` the bridge lifts the experiencer
**+0.0528 CI-sep with C1 up-or-flat (CI includes 0) and the twin losing** -- reproducing the origin's OFFLINE
headline +0.0528 THROUGH the real surface-keyed `make_canonicalizer` (it is faithful; my first pass only looked
smaller because I swept the extra-conservative `conf_thr=0`). So the **deployable-under-the-bar operating point is
conf_thr~-3.0 (+0.0528, C1 up-or-flat)**; the dial extends to +0.084 at a ~0.3%-of-CoNLL C1 cost. The **binding
limiter is COVERAGE** (36-351 fires over a 787 person-definite population), bounded by the origin's ~19%
stated-in-text ceiling; the other ~81% of cross-type links are world-knowledge (LLM-barred).

## FULL-STACK-UPSTREAM: the two upstream components, and which one blocks the live gain
The owner's directive: prototype THIS component AND its upstream to excel/exceed, confirm no downstream regress,
research the upstream is brain-foundational.

- **UPSTREAM #1 (the blocker) -- the entity-layer clustering's GOLD-COREF INHERITANCE.** *Not* brain-foundational
  (research P~0.90). This is why the bridge shows no live gain: the gate already gold-links the commons. **The
  brain-foundational upstream is the HONEST clustering** (names given via the aliaser -- a smaller, string-match-
  redundant "leak" per the graded view -- commons resolved by `situation_predict` + the bridge, NO gold common-noun
  inheritance). Prototyped: on the honest (de-leaked) layer the bridge is exactly the +0.0528 (conf_thr=-3.0,
  C1 up-or-flat, deployable) .. +0.0838 (liberal) CI-sep win above. **The system cannot "exceed" the leaked 0.80
  brain-foundationally** -- 0.80 is the gold answer key, and the
  honest ceiling is floor + the ~19% stated-predication fraction; the rest is the world-knowledge wall. That is the
  honest performance-vs-brain statement, not a defeat.
- **UPSTREAM #2 (measured NEAR-CEILING -- not the lever) -- the live PARSER/labeler.** The bridge reads the
  reader's arc-eager + arc-labeler deprels. Quantified through the REAL consumer at the deployable conf_thr=-3.0:
  GOLD-parse (oracle UD) lift **+0.0601 CI[+0.0356,+0.0886]** (161 fires) vs LIVE-parse **+0.0528 CI[+0.0316,+0.0782]**
  (150 fires) -- **overlapping CIs, a ~0.007 / ~11-fire gap**: the live parser is essentially AT the gold-parse
  ceiling for this task, so improving it recovers almost nothing here. The parser is a reader-wide OUR-INVENTION
  proxy for the brain's incremental predictive parse (a filed reader-wide gap), but it is NOT this chain's limiter.
- **Downstream-regress check -- now EMPIRICAL through the whole `reader.read()`
  (`exp_crosstype_deleaked_full_read_v1.py`).** I prototyped the surgical de-leak as a `DeLeakedReader` subclass
  (keeps NAME/pronoun anchoring, drops COMMON-noun gold inheritance) and ran the ACTUAL `reader.read()` on 25 native
  LitBank docs (2083 pronoun targets) in three configs: A baseline (gold-inherit), B gate-off, C de-leaked. **Pronoun
  `coref_acc = 0.6116` is BYTE-IDENTICAL across all three (A==B 25/25, A==C 25/25)** -- the entity gate, and hence
  de-leaking its gold inheritance, does NOT move the pronoun consumer at all (it reads its own coref-column stream;
  this also confirms the gate's own "coref byte-identical" docstring). So de-leaking upstream #1 is downstream-safe for
  the pronoun consumer. The only consumer it changes is the one we WANT to change -- the entity-layer / experiencer
  canonicalizer -- and there the drop (0.86->0.70, 0.80->0.15) is removing a gold inflation, not regressing a real
  capability. (LitBank is 19c -- used here ONLY as the reader's native-format MECHANISM check, no capability number
  claimed from it; the load-bearing numbers are the modern-GUM ones above.)

## THE OCCUPATIONAL WALL, DECOMPOSED -- and the brain's SEMANTIC-MEMORY route tested (owner deep-dive 2026-09-08, `exp_crosstype_kb_route_gum_v1.py`)
Decomposing the missed anaphoric-to-name person-definite population (n=154) by descriptor kind: **OCCUPATIONAL
("the doctor/author/director") = 116 (75%)** at recall 0.241 ; age_gender 33 (21%) at 0.273 ; relational 5 (3%). The
occupational bulk is where we lose the most, and the origin established these roles are almost never STATED near the
name (PRED ~1/226). So the miss is not a detector gap -- it is **SEMANTIC MEMORY**: the brain KNOWS "Byron is a
poet" (Bruce-Young person-identity nodes / ATL), and that fact is never written in the text. That is the single
biggest reason we do not match a competent reader here.
- **The brain's route, tested (the two-route CLS -- consolidated KB UNION episodic in-text).** I added the
  sister-problem entity-type KB (DBpedia InstanceOf, on disk) as a second licensing route feeding the SAME cue
  competition. It **~DOUBLES occupational REACH** (in-text reaches gold in 14/116, KB in 19, UNION 30; **16 are
  KB-only -> the routes are near-disjoint**, exactly the CLS pattern). So the wall is NOT a pure ceiling -- the
  famous-entity occupational cases the text never states ARE recoverable from stored knowledge.
- **But the incremental WIN is small and coverage-bounded (the honest part).** Through the real consumer at
  conf_thr=-3.0: in-text +0.0528 -> two-route **+0.0583** (NOT CI-separated from in-text; shuffled-KB twin +0.0510
  is close). The KB reaches ~2x but the competition converts only ~3 extra to correct unique binds, because GUM's
  named persons are largely **LOCAL / fictional (absent from DBpedia)** -- the KB's famous-entity slice is a small
  part of the population. This REPRODUCES the sister problem's lesson: the two-route architecture is the right
  brain-foundational shape; the binding lever is **encyclopedic COVERAGE** (a foundation-acquisition problem), not a
  new mechanism. **So the honest answer to "why aren't we showing the brain's results": our semantic memory has
  bounded coverage (famous entities), while the brain has full encyclopedic + learned knowledge AND resolves
  local/fictional persons' roles from accumulated discourse context -- which needs the general situation-model
  comprehension, not a lookup.**

## PROPOSED hdlab DIFF (Q111 -- strategy lands it), in two independent parts
1. **The opt-in bridge wire** in `SituationReader._apply_commonnoun_gate`, behind a NEW flag `crosstype_bridge`
   (default False -> byte-identical off): after the situation former assigns clusters, build a Doc adapter from the
   reader's OWN `_read_parse_cache` (pos + `parse_with_conf` heads + `_frontend_labeler` deprels -- NO second parse)
   + `role_mentions`, call `hdlab.crosstype_bridge.crosstype_bridge_links(doc, self.gaz, conf_thr=-3.0)` (the tuned
   C1-up-or-flat operating point; conservative..liberal is a swept dial the owner picks at flip), and set
   each bound role mention's cluster to the named entity's cluster. Wire alongside the `entity_kb_resolver`/
   `unified_referent` block; NOT inside the dormant `entity_kb_resolver` branch.
2. **The load-bearing part -- de-leak the upstream** so the wire is not redundant: in `_apply_commonnoun_gate`'s
   `lab_to_cluster` step, restrict gold-cluster inheritance to NAME/PRONOUN-anchored groups and give COMMON-only
   groups a fresh `CN:` id (drop the common-noun gold-coref inheritance). Then the bridge supplies the cross-type
   common->name link that the gold peek currently fakes. **Part 2 is the actual fix; Part 1 without Part 2 changes no
   board number.** Both are strategy's to land and to re-measure with the full `reader.read()` (incl. the pronoun
   consumers) before any flip.

## What I did NOT establish / would withdraw first if wrong
- **The full `reader.read()` on MODERN gold under the de-leak+bridge.** The pronoun-consumer no-regress is now
  established empirically through the whole `reader.read()` (25/25 byte-identical `coref_acc`, above) -- but on
  NATIVE LitBank (19c, mechanism-check only). The de-leaked-gate + bridge EXPERIENCER lift through the full `read()`
  was proven on modern GUM via the real consumer FUNCTIONS (not the whole `read()` -- GUM is not the reader's native
  CoNLL). Converting GUM to the reader's CoNLL format and running the entire `read()` end-to-end on modern gold is
  the remaining integration step; I would withdraw the magnitude first if that end-to-end run on modern gold differs
  from the consumer-function measurement.
- **Whether the owner/strategy classes gold-coref inheritance as a leak or a legitimate given.** My strong, research-
  backed read is *leak* (no theory posits given coref; the project treats common-noun coref as a hard prediction task
  everywhere else; the brief's own floors are the honest raw numbers). If strategy rules it a legitimate given, then
  finding (B) stands as a clean located negative ("the bridge is redundant with the gold-anchored live input") and
  part 2 of the diff is moot -- but so is any board gain from the bridge.
- **OOD is directionally consistent but UNDERPOWERED, not CI-separated.** Ran GENTLE (26 OOD docs, on disk) at the
  deployable conf_thr=-3.0 through the real consumer: C3 0.0952 -> 0.1429 = **+0.0476 CI[+0.0000,+0.1042]** -- the
  SAME direction and magnitude as GUM (+0.0528), but n=42 (only 9 merges) so the CI touches 0 and the twin is not
  CI-sep either. So the mechanism GENERALIZES in point-estimate OOD, but GENTLE is too small to establish
  CI-separation; I would not claim a CI-sep OOD win, only a consistent one.

## KEY REALIZATIONS (the enabling moves)
- **Score through the REAL consumer -- and sweep the ARM, or you will under-read your own mechanism.** The origin's
  `score_c3_experiencer` is a midx-label-match; the live `make_canonicalizer` is surface-head-keyed. My first pass
  (the conservative `cue_conf` arm) read +0.020 and I nearly wrote "the real consumer eats a third." Sweeping the
  origin's STRONGEST arm (`cue_competed`) showed +0.0838 -- the real consumer is FAITHFUL, it reproduces the offline
  +0.086; the apparent haircut was the wrong operating point, not the consumer. *Score through the actual consumer
  AND sweep the deployable arms before concluding a live path costs signal.*
- **The floor the whole line of work quotes is not the reader's live output.** Reproducing the brief's C1=0.694 by
  raw `situation_predict`, then finding the REAL `_apply_commonnoun_gate` outputs 0.859, is what surfaced the gold
  leak. *When a floor and the live code disagree, run the live code.*
- **A near-ceiling live number can be a gold ARTIFACT, not a capability -- test it by stripping the gold seed.**
  Feeding the same gate honest (predicted, no-gold) seeds and watching 0.807 collapse to 0.134 is the single
  measurement that proved the reader was faking cross-type filing with the answer key. The 88.9%-gold-kept on native
  LitBank made it undeniable.
- **The owner's principle located the real problem.** "A brain-foundational component that shows no gain means
  something upstream is not brain-foundational" -- following that literally led from "the bridge is redundant live"
  to "the upstream gate gold-inherits," which is the actual thing to fix.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md, E3 coreference / entity tracking)
- **NEW, load-bearing deviation:** `hdlab/situation_reader.py::_apply_commonnoun_gate` inherits GOLD coreference
  cluster ids (relabels each `situation_predict` group to the plurality gold cluster of its members; 88.9% of
  non-pronoun mentions keep their exact gold id on native LitBank). This gold-coref inheritance is
  **non-brain-foundational** (3-lane research drill, P~0.90: no discourse-processing theory posits given coreference;
  ACT-R / DRT file-change / situation-model all require online resolution). It inflates the entity-layer CoNLL
  (0.695 honest -> 0.859) and the experiencer bind (0.155 -> 0.807), and it MASKS any downstream cross-type
  mechanism (the crosstype bridge is redundant against it). Recommend the audit flag the entity-layer clustering's
  fidelity as **gold-anchored (leak)**, and that the honest numbers (C1 ~0.69, C3 ~0.15) are the real capability.
- **The crosstype bridge is brain-foundational and its computation now has its precise reference:** Garrod & Sanford
  role/individual bonding-and-resolution + hippocampal one-shot relational binding (add to the organ's cite list;
  Bruce-Young PINs and the ATL category hub were over-extended -- PINs model *familiar-identity retrieval*, the ATL
  hub models *category* semantics, neither is the one-shot role<->name binding this organ does).

## Adjacent components (seeds for the next problems -- evaluated for brain-foundational fidelity)
- **The entity-layer clustering (`commonnoun_binder.situation_predict` + the gate's gold inheritance) is the highest-
  value follow-on.** Its brain-status: `situation_predict` (head-match + window + event-centrality) is an
  OUR-INVENTION heuristic; the gold-coref inheritance is a LEAK. A brain-foundational entity layer (online cue-based
  clustering, no gold) is a filed-worthy problem in its own right, and it is the precondition for THIS bridge (and the
  `entity_kb_resolver`, and any cross-type consumer) to show a real gain.
- **The world-knowledge common->name bridge (~81% of the population).** Text-stated links (~19%) are the bridge's
  reach; the rest need encyclopedic/discourse knowledge (the origin's located Wikidata-occupation negative + the
  Phase-1 identifiability wall). Brain-foundational and filed; the honest performance-vs-brain gap lives here.
- **The live parser/labeler** (bridge precision 0.42-0.61 live vs 0.86-0.96 gold): a reader-wide precision lever,
  second-order for this coverage-bound task.

---

**TLDR (plain English):** We had a tool that works out "the doctor" is "Elizabeth" from the grammar. I plugged it
into the real reader and found two things. First, run through the reader's *actual* naming step (not the lab-bench
stand-in), the tool still helps -- and by as much as it did on the lab bench (the real reader does NOT eat the
benefit, once you use the right setting): about **5 more experiencers in 100** bound to the right character at the
recommended setting *with no cost to any other score*, up to ~8 more in 100 if you push it (which costs a hair on the
entity-grouping score), and a scrambled version can't fake it. Second, and bigger:
the reader is currently *faking* this skill by copying the human answer key -- it quietly reuses the gold
coreference labels, which is why it looks like it already scores ~80 in 100. Strip the answer key and it drops to
~15 in 100, and the tool is what lifts it back. So plugging the tool in "as is" changes no score, because the answer
key already did the job -- but the answer key isn't reading, it's peeking, and the brain has no answer key. The real
fix is to stop the reader peeking; then the tool becomes the genuine, brain-faithful way to do it. Research confirms
no theory of reading gives the brain a coreference answer key -- it always has to work it out.

**QUESTIONS:** one real judgement call for the owner/strategy (you own the substrate): **is feeding the reader the
gold coreference labels a legitimate "given" (like gold mention spans), or a leak to remove?** My research-backed
read is *leak* for common nouns (names are a smaller, partly-redundant case). If you rule it legitimate, the tool is
simply redundant live (a clean located negative); if you rule it a leak, the two-part diff below turns the tool into
a real board gain.

**NEXT STEPS:** (1) Strategy: decide the leak question. (2) If leak: land the two-part hdlab diff (opt-in bridge wire
+ de-leak common-noun gold inheritance) and re-measure with the FULL `reader.read()` including the pronoun
consumers (the one downstream I could not run). (3) File the "brain-foundational entity-layer clustering (no gold
coref)" follow-on -- it is the precondition for this bridge and every cross-type consumer. (4) Optionally sweep the
live parser on the licensing constructions (a smaller, precision-only lever).
