---
problem: reason_over_the_spatial_relational_model_containment_position_path_modern_gold
status: SOLVED
bar: "PASSES only with ALL of: (1) a glass-box RELATIONAL SPATIAL MODEL + reasoner (over sm.locations + the named-ground events; REUSE the LocationRegister + its region-containment primitive, EXTEND to a small updatable relational graph) answering THREE inference types no single location fact settles: (a) CONTAINMENT (multi-step/transitive), (b) RELATIVE POSITION (composed over the spatial framework), (c) PATH/TRANSFER (post-move location AND the vacate-Source 'no longer' inference); NO learned QA model, NO external LLM. (2) Answers CI-separated over BOTH controls on MODERN non-synthetic gold: (a) a most-recent/last-mention floor recomputed on the same population which MUST LOSE on the multi-fact items; (b) the info-free SHUFFLED-RELATION twin LOSES CI-separated on ALL THREE. (3) Isolates the REASONING from extraction (ablate to a single-fact readout). (4) One-screen summary. A rigorous NEGATIVE is a FULL PASS."
result: "Balanced yes/no, exact-match accuracy, paired bootstrap CI (half-width + null p95). ALL THREE inference types clear the bar CI-separated over BOTH controls on MODERN non-synthetic gold, with reasoning ISOLATED from extraction (gold relations supplied): CONTAINMENT (SpaceEval/ISO-Space gold, train n=1304): reasoner 1.000 vs last-mention 0.940, margin +0.060 CI[+0.047,+0.073], null p95 0.014; multi-fact subset (n=155) 1.000 vs 0.497 (last-mention at chance); shuffled-twin 0.508; two-level is_in_region ablation 0.896. RELATIVE POSITION (SpartQA-HUMAN gold SPRL, test n=1300): reasoner 1.000 vs last-mention 0.734, margin +0.266 CI[+0.242,+0.289]; multi-fact subset (n=828) 1.000 vs 0.582; shuffled-twin 0.143 (collapses). PATH/TRANSFER (SpaceEval gold MOVELINK, train n=32): reasoner 1.000 vs last-mention 0.500, margin +0.500 CI[+0.344,+0.656]; shuffled-twin 0.469; vacate-Source works. LOCATED NEGATIVE (end-to-end over the reader's OWN extraction, named with counts): the reader's parse+extractor recovers 22% of gold containment edges / 6% position / 2% moves on SpaceEval real prose (up from 13% after a net-positive brain-foundational extraction upgrade -- part-whole 'X of Y' + locative-verb constructions -- with NO end-to-end regression), and MULTI-HOP CONTAINMENT CHAIN SURVIVAL is 6/90 (6.7%, up from 1/90), so end-to-end >1-fact reasoning is still extraction-gated (the info-free twin still LOSES CI-separated, so the extracted relations are load-bearing; coverage, not the reasoner, is the cap)."
floor: "Most-recent/last-mention (strongest stateless), recomputed per population, per type: containment 0.940 (train) / 0.916 (trial); relative-position 0.734 (test) / 0.707 (train); path/transfer 0.500 (train). Each LOSES CI-separated to the reasoner, and each is at/near chance on its multi-fact subset (containment 0.497, position 0.582, path 0.500)."
controls: "(1) SHUFFLED-RELATION twin (edges permuted, node set + counts kept) LOSES CI-separated on all three types (containment 0.508, position 0.143, path 0.469 vs reasoner 1.000) -- the relation CONTENT is load-bearing. (2) SINGLE-FACT readout ablation (depth-1 reasoner) == the last-mention floor (composition is the lift). (3) IS_IN_REGION ablation (the LocationRegister's two-level INDOORS/OUTDOORS containment) scores 0.896 on containment -- it cannot answer arbitrary nested containment. (4) GOLD-vs-EXTRACTED (isolates reasoning from extraction): the reasoner is near-perfect on gold relations and coverage-limited end-to-end -> the wall is extraction recall, not the reasoning. (5) POSITIVE control: a >=2-fact item vs a matched single-fact item (single-fact subset reasoner==last-mention==1.000)."
files_changed: "experiments/fetch_spatial_relational_gold.py, experiments/spatial_relational_model.py, experiments/spatial_gold_loaders.py, experiments/spatial_relation_extractor.py, experiments/exp_spatial_reasoner_gold_relations_v1.py, experiments/exp_spatial_position_gold_v1.py, experiments/exp_spatial_position_qa_v1.py, experiments/exp_spatial_extraction_recall_v1.py, verification/test_spatial_relational_reasoning.py, notes/problems/reason_over_the_spatial_relational_model_containment_position_path_modern_gold/SOLVED.md (NO hdlab/ written -- Q111)"
reverify: ".venv/Scripts/python.exe verification/test_spatial_relational_reasoning.py"
---

# Spatial relational reasoning: the reasoner is sound and brain-faithful on all three types; the end-to-end wall is text->relation EXTRACTION, quantified

**Bottom line.** The reader tracked per-entity location but never REASONED over the arrangement (its only relational
move was a two-level INDOORS/OUTDOORS containment). I built the missing glass-box RELATIONAL SPATIAL MODEL + reasoner
-- transitive containment, spatial-framework relative position (with nested-frame inheritance), and Goal-over-Source
path/transfer with the vacate-Source "no longer" inference -- and validated it on MODERN non-synthetic gold. On
GOLD relations (reasoning isolated from extraction) all three types beat the last-mention floor CI-separated with the
shuffled-relation twin collapsing. End-to-end over the reader's OWN extraction the composition is coverage-limited,
and I traced that to its exact cause with counts: the parse+relation extractor recovers ~2-13% of the gold relations
and multi-hop chains almost never survive it (1/90). That located negative is corroborated by the SpaceEval
literature (best system F1 ~0.845 from gold elements vs ~0.573 from raw text) and is brain-consistent.

## 1. Opening move -- how the brain does this (PINNED; researched, notes/research below)
A reader represents a described scene as a small RELATIONAL model and reasons by INSPECTING it, not by applying formal
rules (Johnson-Laird 1983; Byrne & Johnson-Laird 1989 -- multiple-model problems are harder than one-model at matched
inference steps: model-based, PINNED). CONTAINMENT is region-nesting and TRANSITIVE (nested cognitive maps -- Wiener &
Mallot 2003; Peer & Epstein 2025; hippocampal transitive/relational inference -- Dusek & Eichenbaum 1997). RELATIVE
POSITION is read off a spatial FRAMEWORK of reference axes with an accessibility ordering above/below > front/back >
left/right and an INVERSE per relation (Franklin & Tversky 1990; Bryant, Tversky & Franklin 1992); position composes
ACROSS nested frames (an object inherits its container's coarse position -- Peer & Epstein 2025, an EFFORTFUL but real
competence). PATH/TRANSFER updates the model to the GOAL and vacates the Source (Talmy 1985; Goal-over-Source, Lakusta
& Landau 2005). Narrative space is categorical/topological (Rinck 1997). I replicated these COMPUTATIONS exactly and
SWEPT the free parameters (closure depth, axis granularity, abstention). PINNED vs OUR-INVENTION marked throughout.

## 2. What was built (glass-box, NO LLM; over the reused LocationRegister)
- `experiments/spatial_relational_model.py` -- `SpatialModel`: containment edges (transitive-closure BFS), position
  edges normalized to axis+sign with a per-axis transitive closure + converse + **nested-frame inheritance** (X in
  Cx, Y in Cy, Cx rel Cy => X rel Y), and moves folded into the promoted `hdlab.location_register.LocationRegister`
  for the path spine (`where_after`, `still_at` = the vacate-Source read). `shuffled_twin` = the info-free control.
- `experiments/spatial_relation_extractor.py` -- the model-CONSTRUCTION rule (OUR-INVENTION): text -> edges using the
  reader's OWN parse (`hdlab.pos_tagger` + `hdlab.arc_parser`, the same assets `_space_reader` uses) + linear
  backstops; coreference-lite entity resolution (head-noun + colour/size-conflict rejection).
- Gold loaders + a pinned reproducible fetch (`fetch_spatial_relational_gold.py`; data/ is gitignored, so a
  PROVENANCE.json records source URL/sha256/license/date for re-acquisition).

## 3. The result -- all three types, GOLD relations (reasoning isolated from extraction), MODERN non-synthetic gold

| type | gold | n | reasoner | last-mention floor | shuffled twin | margin (CI) | multi-fact subset (reasoner / last-mention) |
|---|---|---|---|---|---|---|---|
| CONTAINMENT | SpaceEval/ISO-Space | 1304 | **1.000** | 0.940 | 0.508 | +0.060 [+0.047,+0.073] | n=155: 1.000 / **0.497** |
| RELATIVE POSITION | SpartQA-HUMAN (gold SPRL) | 1300 | **1.000** | 0.734 | 0.143 | +0.266 [+0.242,+0.289] | n=828: 1.000 / **0.582** |
| PATH/TRANSFER | SpaceEval MOVELINK | 32 | **1.000** | 0.500 | 0.469 | +0.500 [+0.344,+0.656] | vacate-Source; twin 0.469 |

Every type: reasoner beats the last-mention floor CI-separated (the floor is at/near chance on its multi-fact
subset -- it MUST lose exactly where >=2 facts must be composed), the shuffled-relation twin LOSES CI-separated (the
relation content is load-bearing), and the single-fact subset shows reasoner == last-mention == 1.000 (the positive
control -- they agree when one fact suffices). The two-level `is_in_region` ablation scores 0.896 on containment: the
existing register CANNOT answer arbitrary nested containment, which is exactly the gap this problem targets.

SpaceEval TEST is unannotated (0 gold relations -- it is the SemEval prediction input); the gold-relation eval is
train+trial, reported per split (trial reproduces: containment +0.084 CI[+0.056,+0.114]).

## 4. The wall, RESEARCHED FULLY: end-to-end it is EXTRACTION, not the reasoning (the located negative, with counts)
Running the reasoner over the reader's OWN extraction (`exp_spatial_extraction_recall_v1`, SpaceEval real prose,
train): the parse+extractor recovers **containment 0.223 (140/628), position 0.058 (7/120), moves 0.024 (7/291)**, and
**multi-hop containment CHAIN survival is 6/90 = 0.067** (trial 0/33). So end-to-end >1-fact reasoning is still
severely limited on that prose -- not because the reasoner fails, but because the chains rarely survive extraction.
(These are AFTER the extraction upgrade in Sec 4b; before it, recall was 0.129 and chain survival 1/90.) On
SpartQA-HUMAN end-to-end QA (`exp_spatial_position_qa_v1`, n=127) the info-free twin still LOSES CI-separated
(reasoner 0.158 vs twin 0.071, margin-vs-twin CI[+0.024,+0.150]) -- so the extracted relations ARE load-bearing --
but the reasoner does NOT beat last-mention CI-separated end-to-end (coverage 0.213; margin CI touches 0). On ReSQ
(real-world captions, n=610) 83% of items are entity-unresolved: the captions state relations implicitly and ~17% are
explicitly commonsense (not derivable from stated relations).

**Diagnosis of the SpartQA end-to-end losses (fully-stated scenes, so UNK = a fixable extraction gap, not missing
info):** REL_UNDETERMINED 45% (mostly missing-edge composition gaps + wrong resolution), ENTITY_UNRESOLVED 20%,
NOPARSE 17%, ANSWERED 19% at 0.75 accuracy. I moved the operating point (the phase-diagram knob) by DENSIFYING the
extraction: colour/size-conflict rejection in resolution, possession-containment ("A has X"), and -- a "go deeper"
FIX, not a patch -- **nested-frame position inheritance** in the reasoner (SpartQA transitivity is largely
cross-block: object-in-L, L-left-R, object-in-R => object left-of object). Each raised coverage/margin; the residual
is parse quality (arc_parser UAS ~0.79) + relation-binding, i.e. an UPSTREAM organ.

**Literature corroboration (this is a KNOWN, named bottleneck, not our artifact):** the best SpaceEval-2015 Task 8
system (D'Souza & Ng) reaches F1 ~0.845 extracting relations from GOLD spatial elements but only ~0.573 from raw
text -- a ~27-point collapse -- and MOVELINK (source/goal binding) is the hardest link type. That is the exact
reasoning-sound / extraction-weak split I measured. SpartQA/SpaRTUN report the same human-vs-machine gap localized to
relation-representation construction, not compositional inference.

## 4b. Extraction upgrade IMPLEMENTED (the phase-diagram knob, moved and measured -- net-positive, no regression)
Decomposing WHY gold containment edges are missed (per missed edge, on SpaceEval train): 40% NEITHER endpoint
extracted, 34% ONE endpoint, 13% recovered, **10% BOTH endpoints extracted but not linked** (attachment/pattern),
3% endpoint-not-in-text. So the loss is dominated by ENTITY RECOGNITION + CONSTRUCTION COVERAGE (74%), NOT
PP-attachment (10%) -- and a large share of the 74% is proper-noun place names, part-whole ("heart of Shitamachi"),
and event/inferential gold ("stay in home"). I added two brain-foundational constructions to the extractor:
**part-whole "X of Y"** (region-nesting, place-gated so it never fires on "number of people") and **locative
predication** ("X is located/situated/lies in Y", the Basic Locative Construction). Measured effect: SpaceEval
containment recall **0.129 -> 0.223** and multi-hop chain survival **1/90 -> 6/90**, with the end-to-end position QA
UNCHANGED on SpartQA/ReSQ (those grid/caption scenes use explicit "X is above Y", not part-whole/locative-verb -- so
the upgrade is neutral there, not a regression; the info-free twin stays collapsed). This proves the wall is MOVABLE
and quantifies the lever; the remaining recall gap is proper-noun/multiword place recognition + event-participant
location grounding + inferential gold, i.e. the extraction organ (below), not the reasoner.

## 5. Why this clears the bar (and where I deflate)
Bar (1) three-type glass-box reasoner: MET. (2) CI-separated over BOTH controls on modern non-synthetic gold, floor
loses on multi-fact, twin loses on all three: MET on the gold-relation condition for all three types. (3) isolate
reasoning from extraction: MET (gold-vs-extracted + single-fact + is_in_region ablations). (4) one-screen summary:
Sec 3. And a rigorous located NEGATIVE (the extraction wall, named with counts) -- which the bar calls a FULL PASS --
is ALSO delivered. **Deflation:** the CI-separated wins supply the relations (gold); end-to-end over the reader's own
noisy extraction is coverage-limited (the located negative). I would WITHDRAW FIRST any claim that the reader reasons
over real narrative prose end-to-end today -- it cannot, until the extraction organ improves; what is proven is that
the REASONER is the correct, brain-faithful mechanism and that extraction is the sole remaining lever.

## 6. Isolation vs capability -- the honest line (the trap this project keeps hitting)
A gold-relation win is, by itself, a construction proof. It becomes a capability claim only in the exact scope proven:
the REASONING COMPUTATION is sound, brain-faithful, and necessary (last-mention and the shuffled twin both fail). The
END-TO-END capability over the reader's extraction is NOT established (it is the located negative). Both are reported
side by side; neither number crosses into the other's territory.

## 7. PROPOSED hdlab DIFF (Q111 -- strategy lands it; NOTHING landed by me)
1. Promote `SpatialModel` (containment transitive closure + spatial-framework position with converse + nested-frame
   inheritance + `still_at` vacate-Source) as a new `hdlab/spatial_relational_model.py` REASONING organ that composes
   `sm.locations` (the LocationRegister) -- default-OFF read-time query API (`contains_path`/`relative`/`still_at`),
   no change to the tracking core. It is additive (a read-time reasoner; emits no events), so no other consumer moves.
2. Do NOT land the text->relation extractor as a capability wire yet: its recall (2-13%) makes it coverage-limited on
   real prose. It belongs behind the parent SPACE line's next problem (Ground-aware PP-attachment / relation binding).
3. The reasoner's answers are only as good as the relations fed in -- wire it to consume BETTER relations as the
   extraction organ improves (the gold-vs-extracted gap IS the expected gain curve).

## KEY REALIZATIONS
- **Isolate the reasoner from extraction and the picture inverts.** Over-the-extraction numbers looked like a weak
  reasoner; feeding GOLD relations showed the reasoner is near-perfect (1.000, all three types, CI-separated) and the
  cap is extraction recall. The gold-vs-extracted split is the single most clarifying control.
- **Chain SURVIVAL, not edge recall, is the right wall metric.** 13% edge recall sounds recoverable; but multi-hop
  reasoning needs EVERY edge of a chain, so 13% edge recall -> 1% chain survival. The exponent is why end-to-end
  multi-fact reasoning collapses while single-fact reading survives.
- **The transitivity in real spatial QA is CROSS-FRAME, not same-axis.** SpartQA transitivity is object-in-block +
  block-position, not A-above-B-above-C. Adding nested-frame inheritance (an object inherits its container's position)
  -- a PINNED brain competence -- was the "go deeper" fix that the shared-wall demanded, not more extraction tuning.
- **Colour-conflict rejection is a reasoning bug in disguise.** "the red circle" silently resolving to "blue circle"
  (only-circle-in-scene) turned correct compositions into REL_UNDETERMINED. Entity resolution is part of the reasoning
  chain, not preprocessing.
- **Determinism bug: set iteration is hash-seed-randomized.** Resolving among candidate entities via a Python set
  made results drift across processes (the reverify would not reproduce). Sorting the candidate set + a total-order
  tie-break fixed it. A witness that passes in one process is not reproducible until it passes in a fresh one.
- **"Sparse" here was in my EXTRACTION, not the data.** SpartQA scenes state every relation; the sparsity was my
  lossy extractor under-recovering a dense text. The phase-diagram knob I could move was extraction completeness --
  and moving it (resolution + inheritance + possession) raised coverage, confirming the wall is extraction, not data.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, SPACE entry)
- NEW reasoning layer over the LOCATION REGISTER: a glass-box relational reasoner (transitive containment; spatial-
  framework relative position with converse + nested-frame inheritance; Goal-over-Source path with vacate-Source) is
  demonstrated brain-faithful and CI-separated on all three types on GOLD relations. The register's only prior
  relational move (two-level INDOORS/OUTDOORS `is_in_region`) is confirmed insufficient (0.896 on nested containment).
- The SPACE cap is now doubly located: (parent) named-ground BINDING at extraction, and (here) relation EXTRACTION
  RECALL for multi-fact reasoning (chain survival 1/90). Reasoning is NOT the bottleneck.
- CORRECTION to inherit: two SPACE audit phrasings are OVERSTATED per the literature. (a) "metric coords RULED OUT
  for narrative space" should read "categorical/topological BY DEFAULT, metric recruitable on demand" (Rinck 1997
  Exp 3). (b) the vacate-Source "no longer" inference: the Goal-over-Source SALIENCE asymmetry is PINNED (Lakusta &
  Landau 2005), but its AUTOMATICITY during comprehension is CONTESTED/under-tested -- model it as available, not
  obligatory. Nested-frame position inheritance is PINNED but EFFORTFUL (Peer & Epstein 2025).

## 8. ADJACENT COMPONENTS (seeds the next problems)
- **The text->spatial-relation EXTRACTOR (the owned bottleneck):** parse UAS ~0.79 + PP-attachment + motion
  source/goal binding. This is the parent SPACE line's queued "Ground-aware attachment" problem; it now has a
  DOWNSTREAM CONSUMER (this reasoner) and a target curve (the gold-vs-extracted gap). Highest-leverage follow-on.
- **A gap-filling SIMULATOR for under-specified text:** the brain fills unstated relations by perceptual simulation +
  commonsense (Barsalou) and correctly ABSTAINS on genuinely indeterminate text -- our abstention is brain-consistent;
  the missing faculty is a simulator, NOT a stronger reasoner. Candidate follow-on (must preserve correct abstention).
- **`grounded_semantic_graph` (ConceptNet AtLocation):** a functional-locus containment-typing source the extractor
  could use to type more grounds -- brain-foundational, untested here.

## TLDR (plain English)
Our reader knew where each character was but could not reason about how things sit in space. I built the missing
reasoning: it keeps a little map of what is inside what, what is left/above/near what, and where someone ends up (and
no longer is) after moving, and it chains facts the story never states outright ("key in box" + "box in drawer" ->
"key in drawer"). When I hand it clean relationships, it answers all three kinds of question essentially perfectly and
far better than a reader that just reads off the single latest fact, and a scrambled-map control fails -- proving the
reasoning is real and matches how the brain does it. The one wall is the earlier step: reading a passage and correctly
pulling out those relationships. Our reader recovers only a small fraction of them from real text, and multi-step
chains almost never survive, so end-to-end it is limited by that reading step -- exactly the wall the published
systems hit (best results get relationships ~85% right from clean building blocks but only ~57% from raw text). So the
reasoning part is solved and brain-faithful; the remaining work is the relationship-extraction part, which is a
separate, already-known component.

## QUESTIONS
None. (One judgement call for the owner: I marked this SOLVED because the reasoner clears the full positive bar on all
three types on modern gold AND a rigorous located negative is delivered -- the bar treats either as a pass. A stricter
reading that requires the CI-separation to hold end-to-end over the reader's OWN extraction would make it PARTIAL;
the end-to-end is coverage-limited, by design of the extraction wall. Content is identical either way.)

## NEXT STEPS
1. Land the `SpatialModel` reasoning organ default-OFF over `sm.locations` (Sec 7.1); it is additive, no consumer
   regresses.
2. File the follow-on: improve the text->spatial-relation extractor (PP-attachment + motion source/goal binding) --
   it now has a downstream consumer and a measured target (gold-vs-extracted gap); coordinate with the parent SPACE
   line's Ground-aware attachment problem, do not duplicate.
3. Fold the AUDIT UPDATE (new reasoning layer; the two overstated SPACE phrasings; chain-survival as the wall metric)
   into BRAIN_FOUNDATIONAL_AUDIT.md.
4. Do NOT re-file: denser dataset (the sparsity is extraction, not data), metric coordinates (categorical by default),
   or a third bridging variant (out of scope).
