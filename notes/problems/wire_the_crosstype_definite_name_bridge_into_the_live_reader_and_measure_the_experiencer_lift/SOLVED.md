---
problem: wire_the_crosstype_definite_name_bridge_into_the_live_reader_and_measure_the_experiencer_lift
status: PARTIAL
bar: "PASSES only with ALL of: 1. hdlab/crosstype_bridge.py wired into the reader's DEFAULT _apply_commonnoun_gate path behind a NEW opt-in flag (crosstype_bridge, default False), byte-identical when off, fed the reader's own parsed tokens via a Doc adapter (no second parse). NOT wired into the dormant entity_kb_resolver branch. Strategy owns the hdlab edit (Q111) -- the solver builds + measures the wire in experiments/ and proposes it. 2. Through the LIVE reader, the affect/goal EXPERIENCER consumer beats its CURRENT live input CI-separated on MODERN gold (GUM), at a conf_thr tuned on the live parse; report the delta + doc-level paired-bootstrap CI. 3. The info-free shuffled-target TWIN LOSES CI-separated on the experiencer, live. 4. NO regress: the entity-layer CoNLL (C1) and the entity-KB hard-link (C2) are up-or-flat live; other reader consumers no-regress. 5. Per no-more-default-off: if net-positive live, propose the flip ON (with the tuned conf_thr); if a measured reason to hold, state it. A rigorous NEGATIVE is a full pass (e.g. 'the live-reader path introduces a coref-order difference that erases the offline lift, located and counted')."
result: "TWO results, both THROUGH THE REAL live consumer chain (_build_entities + goal_register.make_canonicalizer + affect_register.bind_experiencers' canon), modern GUM V12.1.0, all 275 docs, n=549 person-common experiencers of named entities, doc-level paired bootstrap 2000x. (A) THE MECHANISM SURVIVES THE REAL CONSUMER FAITHFULLY -- it does NOT shrink; it reproduces the origin's arms, on a conservative..liberal DIAL. Against the HONEST raw-situation_predict floor (C3=0.1548): the STRONGEST arm cue_competed (full-referent competition, liberal margin=0.0) -> C3=0.2386 = +0.0838 CI[+0.0536,+0.1167] CI-SEP (== the origin's OFFLINE +0.086 -> the real surface-keyed make_canonicalizer does NOT eat the lift), info-free TWIN LOSES CI-sep (+0.0729), C2 hard-link UP +0.0102 CI-sep -- BUT a small CI-sep C1 entity-layer regress (0.6947->0.6917, -0.0031 CI[-0.0043,-0.0019]), so it FAILS the bar's up-or-flat C1. The C1-SAFE arm cue_conf -> C3=0.1749 = +0.0200 CI[+0.0059,+0.0381] CI-sep, twin loses (+0.0200), C2 +0.0029 CI-sep, C1 +0.0001 (SAFE -- meets the bar). So the deployable-under-the-bar operating point is cue_conf (+0.020, C1-safe); cue_competed trades a ~0.3%-of-CoNLL C1 regress for 4x the experiencer + hard-link gain (the exact conservative..liberal dial the brief anticipated). (B) THE LITERAL WIRE DELIVERS NO LIVE BOARD GAIN, for a located+counted reason (a rigorous negative = a full pass under the bar): the live _apply_commonnoun_gate INHERITS GOLD COREF cluster ids (it relabels every situation_predict group to the plurality gold cluster of its members), so on the experiencer population it already scores C3=0.807 (n=549) WITHOUT any reading mechanism; wiring the bridge AFTER that inheritance is redundant (gate+bridge -0.013). Strip the gold seed (honest predicted clusters) and the SAME gate collapses to C3=0.134 == raw situation_predict 0.155 -- so the 0.80 is entirely the gold answer key, not the gate's logic. Verified on the reader's NATIVE LitBank path: after _apply_commonnoun_gate 88.9% of non-pronoun mentions keep their EXACT gold cluster id. A background research drill (3 lit-scan lanes) confirms gold-coref inheritance is non-brain-foundational (P~0.90: no discourse-processing theory posits given coreference; all require online retrieval). So the bridge is the brain-foundational mechanism (Garrod & Sanford role/individual bonding-and-resolution) that does cross-type filing WITHOUT gold; it is redundant only vs the leak, and load-bearing once the upstream is de-leaked."
floor: "HONEST floor = raw commonnoun_binder.situation_predict (the origin+brief floor), recomputed on the SAME GUM population+consumer: C3 experiencer 0.1548 ; C1 entity-layer CoNLL 0.6947 (reproduces the brief's 0.6939 -> my harness IS the live reader, not an offline reimplementation) ; C2 hard-link 0.0239. THE ACTUAL CURRENT LIVE INPUT (what the bar names) = the gold-inheriting _apply_commonnoun_gate = C3 0.807 / C1 0.859 -- the bridge does NOT beat this (the gold-coref leak already saturates it). Reference: origin OFFLINE-PROXY lift +0.0328..+0.086 (score_c3_experiencer, midx-label-match) -> +0.0164..+0.0200 through the REAL make_canonicalizer."
controls: "(1) INFO-FREE TWIN (shuffled-target, same #merges, random named entity): LOSES CI-sep at every conf_thr (+0.0182 CI[+0.0037,+0.0361] at thr=0) -> correct cross-type TARGETING is load-bearing, not 'merge into some name'. (2) DETERMINISTIC known-answer through the REAL make_canonicalizer: 'Elizabeth was a doctor. The doctor cried.' floor C3=0/2 -> bridge C3=1/2 (the live consumer, not a proxy). (3) NO-REGRESS: C1 non-negative (+0.0001, CI[-0.0003,+0.0005]); C2 up CI-sep (+0.0029). (4) THE GOLD-LEAK DIAGNOSTIC (isolates finding B): the SAME real _apply_commonnoun_gate scores C3 gold-seed 0.807 vs honest-predicted-seed 0.134 vs raw situation_predict 0.155 -> the 0.80 is the gold seed, not the gate; and on native LitBank 88.9% of non-pronoun mentions keep their exact gold id -> the leak is the REAL reader's behavior, not a GUM-harness artifact. (5) HARNESS-FIDELITY GATE: C1 raw 0.6947 == the brief's 0.6939 (the harness reproduces the live floor). (6) RESEARCH VET (3-lane lit-scan): gold-coref inheritance = non-brain-foundational leak (P~0.90); brain mechanism = Garrod&Sanford role/individual bonding + hippocampal one-shot binding (Duff/Kurczek amnesia evidence); names-given vs commons-given is a graded-severity leak, not legitimate-vs-illegitimate. (7) THE DIAL (W5): the STRONG arm cue_competed reproduces the origin's OFFLINE +0.086 through the REAL consumer (+0.0838 CI-sep) with the twin losing -> the live consumer does NOT eat the lift; cue_conf is the C1-safe conservative point (+0.020)."
files_changed: "experiments/exp_crosstype_live_wire_gum_v1.py (the live-reader wire simulated on the REAL consumer functions + honest-floor sweep + the gold-inheritance diagnostic), verification/test_crosstype_live_wire.py (4/4 witness), notes/problems/wire_the_crosstype_definite_name_bridge_into_the_live_reader_and_measure_the_experiencer_lift/SOLVED.md. NO hdlab/ written (Q111 -- proposed diff below). Reuses hdlab.crosstype_bridge (the landed organ, self-test PASS), the reader's REAL _apply_commonnoun_gate / _build_entities / make_canonicalizer, data/corpora/gum/ (pinned GUM V12.1.0, on disk), data/litbank/coref/conll/ (native reader format, mechanism-check only -- NOT a load-bearing 19c gold)."
reverify: ".venv/Scripts/python.exe verification/test_crosstype_live_wire.py (5/5: deterministic known-answer through the real canonicalizer + honest-floor CI-sep lift + twin loses + no-regress + the gold-coref leak on GUM and native LitBank + the cue_competed/cue_conf conservative..liberal dial)."
---

# PARTIAL -- the mechanism survives the real consumer on the HONEST floor, but the literal wire yields no live board gain because an UPSTREAM component (the gate's gold-coref inheritance) is not brain-foundational

**STATUS: PARTIAL** (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written -- measured in `experiments/` + `verification/`; the strategy session owns any hdlab change (Q111).

**Two results, both proven through the REAL live consumer functions (not the offline proxy the origin used):**

1. **The mechanism is REAL and survives the real consumer faithfully.** Fed the reader's OWN live parse and scored
   through the ACTUAL `make_canonicalizer` + `bind_experiencers` canon, the crosstype bridge lifts the affect/goal
   EXPERIENCER bind over the honest raw-`situation_predict` floor on a conservative..liberal DIAL: **+0.020 CI-sep
   (cue_conf, C1-safe) up to +0.0838 CI-sep (cue_competed, liberal)**, the info-free twin LOSES CI-sep at every point.
   The strong arm reproduces the origin's OFFLINE +0.086 -- the real consumer does NOT eat the lift (my first pass
   under-read it by sweeping only the conservative arm). cue_conf keeps C1/C2 up-or-flat; cue_competed trades a small
   CI-sep C1 regress (-0.003) for 4x the gain.

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

## The measurement (GUM V12.1.0, all 275 docs, n=549; through the REAL consumer) -- the conservative..liberal DIAL
| arm | merges | C3 floor -> bridge (twin) | delta vs floor (CI) | vs twin | C1 entity-layer | C2 hard-link |
|---|---|---|---|---|---|---|
| **cue_conf** (conservative, C1-safe) | 37 | 0.1548 -> 0.1749 | **+0.0200 [+0.0059,+0.0381]** sep | +0.0200 sep | +0.0001 (SAFE) | +0.0029 sep |
| **cue_competed** margin 0.5 | 310 | 0.1548 -> 0.2313 | **+0.0765 [+0.0478,+0.1083]** sep | +0.0656 sep | -0.0026 [-0.0037,-0.0015] | +0.0092 sep |
| **cue_competed** margin 0.0 (liberal) | 351 | 0.1548 -> 0.2386 | **+0.0838 [+0.0536,+0.1167]** sep | +0.0729 sep | -0.0031 [-0.0043,-0.0019] | +0.0102 sep |

**The lift does NOT shrink through the real consumer.** cue_competed reproduces the origin's OFFLINE +0.086 almost
exactly (+0.0838) -- the surface-keyed `make_canonicalizer` is faithful; my first pass only looked smaller because I
swept the *conservative* `cue_conf` arm. The dial: **cue_conf is C1-safe (+0.020, meets the bar's up-or-flat C1);
cue_competed trades a ~0.3%-of-CoNLL CI-sep C1 regress for 4x the experiencer + hard-link gain** (== the origin's
offline cue_competed C1 -0.0026). Under the bar's strict "up-or-flat C1", the deployable point is **cue_conf**. The
**binding limiter is COVERAGE** (37-351 fires over a 787 person-definite population), bounded by the origin's ~19%
stated-in-text ceiling; the other ~81% of cross-type links are world-knowledge (LLM-barred).

## FULL-STACK-UPSTREAM: the two upstream components, and which one blocks the live gain
The owner's directive: prototype THIS component AND its upstream to excel/exceed, confirm no downstream regress,
research the upstream is brain-foundational.

- **UPSTREAM #1 (the blocker) -- the entity-layer clustering's GOLD-COREF INHERITANCE.** *Not* brain-foundational
  (research P~0.90). This is why the bridge shows no live gain: the gate already gold-links the commons. **The
  brain-foundational upstream is the HONEST clustering** (names given via the aliaser -- a smaller, string-match-
  redundant "leak" per the graded view -- commons resolved by `situation_predict` + the bridge, NO gold common-noun
  inheritance). Prototyped: on the honest (de-leaked) layer the bridge is exactly the +0.020 (cue_conf, C1-safe) ..
  +0.0838 (cue_competed, liberal) CI-sep win above. **The system cannot "exceed" the leaked 0.80
  brain-foundationally** -- 0.80 is the gold answer key, and the
  honest ceiling is floor + the ~19% stated-predication fraction; the rest is the world-knowledge wall. That is the
  honest performance-vs-brain statement, not a defeat.
- **UPSTREAM #2 (secondary) -- the live PARSER/labeler.** The bridge reads the reader's arc-eager + arc-labeler
  deprels; live-parse precision is 0.61 (conservative) / 0.42 (liberal) vs the gold-parse ceiling ~0.86-0.96 (origin).
  A better parse of the licensing constructions (appos/copula/nsubj) would raise *precision*, but coverage (the 3-5%)
  is bounded by how often the link is *stated*, so the parser is a real but second-order lever here.
- **Downstream-regress check:** de-leaking upstream #1 would DROP the reader's *reported* C1/C3 (0.86->0.70, 0.80->
  0.15) -- but that is removing an inflation, not regressing a real capability. The one genuine coupling to protect:
  `_apply_commonnoun_gate` inherits gold cluster ids so that **pronoun resolutions (keyed on the gold coref cluster)
  stay tied to the named entity**. The surgical de-leak keeps NAME/PRONOUN anchoring and drops only the COMMON-noun
  cross-type inheritance (let the bridge supply it). The pronoun he/she pick reads `sm.coref_resolutions`, a separate
  stream -- untouched by the common-noun gate -- so the tuned pick is byte-identical either way (as the origin's p12
  established). Full pronoun-consumer re-measure needs the whole `reader.read()` and is named as the one unverified
  downstream (below).

## PROPOSED hdlab DIFF (Q111 -- strategy lands it), in two independent parts
1. **The opt-in bridge wire** in `SituationReader._apply_commonnoun_gate`, behind a NEW flag `crosstype_bridge`
   (default False -> byte-identical off): after the situation former assigns clusters, build a Doc adapter from the
   reader's OWN `_read_parse_cache` (pos + `parse_with_conf` heads + `_frontend_labeler` deprels -- NO second parse)
   + `role_mentions`, call `hdlab.crosstype_bridge.crosstype_bridge_links(doc, self.gaz, conf_thr=<tuned>)`, and set
   each bound role mention's cluster to the named entity's cluster. Wire alongside the `entity_kb_resolver`/
   `unified_referent` block; NOT inside the dormant `entity_kb_resolver` branch.
2. **The load-bearing part -- de-leak the upstream** so the wire is not redundant: in `_apply_commonnoun_gate`'s
   `lab_to_cluster` step, restrict gold-cluster inheritance to NAME/PRONOUN-anchored groups and give COMMON-only
   groups a fresh `CN:` id (drop the common-noun gold-coref inheritance). Then the bridge supplies the cross-type
   common->name link that the gold peek currently fakes. **Part 2 is the actual fix; Part 1 without Part 2 changes no
   board number.** Both are strategy's to land and to re-measure with the full `reader.read()` (incl. the pronoun
   consumers) before any flip.

## What I did NOT establish / would withdraw first if wrong
- **The full `reader.read()` pronoun-consumer re-measure under the de-leak.** I proved the bridge + honest floor
  through the real `make_canonicalizer`/`bind_experiencers`, driven on GUM mentions; I did NOT run the entire
  `read()` (GUM is not the reader's native CoNLL). The claim that de-leaking common-noun inheritance leaves the
  pronoun pick byte-identical rests on the separate-stream architecture + the origin's p12 result, not a fresh live
  run. **This is the first thing to verify at integration**, and the first thing I would withdraw if the pronoun
  consumers turn out to depend on the common-noun gold ids.
- **Whether the owner/strategy classes gold-coref inheritance as a leak or a legitimate given.** My strong, research-
  backed read is *leak* (no theory posits given coref; the project treats common-noun coref as a hard prediction task
  everywhere else; the brief's own floors are the honest raw numbers). If strategy rules it a legitimate given, then
  finding (B) stands as a clean located negative ("the bridge is redundant with the gold-anchored live input") and
  part 2 of the diff is moot -- but so is any board gain from the bridge.
- **GUM only.** GENTLE OOD (26 docs, on disk) not run. The mechanism (Ariel cue-specificity + the world-knowledge
  coverage wall) predicts the same OOD; measured only GUM.

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
benefit, once you use the right setting): about 2 more experiencers in 100 on the safe setting, up to ~8 more in 100
on the aggressive setting (which costs a hair on a different score), and a scrambled version can't fake it. Second,
and bigger:
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
