---
problem: the_common_noun_binder_is_string_identity_not_the_brains_content_addressable_typed_coref
status: SOLVED
bar: "Route the LIVE C2 definite-common-noun binding through the typed content-addressable competition (typed_coref) replacing the string-identity heuristic, and SHOW it beats the string-identity floor CI-separated on the honest de-leaked C2 slice (info-free twin LOSING) with no downstream board regress (coref / common_noun_coref / who_did_what dims) -- OR a rigorous LOCATED NEGATIVE naming exactly why typed binding cannot beat string identity on the reader's own metric (with a number; the brain's actual mechanism faithfully built). INVARIANT: the recall path + non-C2 consumers byte-identical off the changed decision; no external tool/LLM at inference."
result: "The typed content-addressable binding, re-keyed on a brain-foundational lexical-CONCEPT lemma (WordNet morphy -- the substrate's standing wordform->lemma-concept tool, used by 6+ organs), scores per-mention common-noun RESOLUTION accuracy 0.5580 on GUM modern TEST (n=2855 anaphoric common-noun mentions; metric = resolved-referent nominal-dominant gold eid == mention eid, the URG board instrument), and BEATS the honest DE-LEAKED string-identity floor 0.5254 by +0.0326 CI[+0.0205,+0.0450] CI-sep; info-free twin LOSES +0.0322 CI[+0.0233,+0.0416] CI-sep; a strict gain over the current live wire (crude key, 0.5482). The brief's premise ('typed binding only ties the floor') was an artifact of a LEAKY floor: the raw gold-lemma floor 0.5412 keys redacted 'the ____' mentions on the annotator-supplied REAL word (redaction see-through), annotation raw text cannot access -- removing ONLY that see-through drops the floor to 0.5254, and EVEN THE CURRENT crude-key wire beats 0.5254 CI-sep (+0.0228). Vs the raw LEAKY 0.5412 the concept-key binding is +0.0168 (CI[-0.0003,+0.0327] includes 0 -- honest parity-plus; the residual is exactly the irreducible redaction). GOLD-FREE; the fix is a one-line KEY swap inside the additive resolution consumer -> clustering/coref/who_did_what byte-identical (no-regress by construction)."
floor: "Strongest floor computable from raw text: HONEST DE-LEAKED gold-lemma string-identity = 0.5254 (n=2855; the raw gold-lemma floor 0.5412 with ONLY the redaction see-through removed -- redacted/non-alpha heads keyed on their raw surface, gold lemma kept on every visible word). Also run on the identical population: fair same-regime morphy string-identity 0.5261; crude head_lemma string-identity 0.5156; raw LEAKY gold-lemma string-identity 0.5412 (reported, not beaten CI-sep -- +0.0168 CI incl 0; the +0.0158 gap 0.5254->0.5412 is pure redaction annotation)."
controls: "(1) FAITHFULNESS: the crude-key arm is BYTE-IDENTICAL to the deployed live wire (hdlab.situation_reader-served _reader_commonnoun_resolution) on 20 GUM docs -> the measured delta is the fix, nothing else. (2) INFO-FREE TWIN (bridge -> random gn-compatible prior) LOSES CI-sep (+0.0322) -> the type signal is load-bearing, not 'any reach'. (3) FAIR same-regime floor (morphy string-identity 0.5261) BEATEN CI-sep (+0.0319) -> the binding adds over string-identity IN THE SAME key regime, not merely via the better key. (4) DE-LEAK: removing the raw gold floor's redaction see-through (0.5412->0.5254) exposes the leak; the binding beats the de-leaked floor CI-sep. (5) LOCATED SUB-NEGATIVE: the loose WordNet-synonymy 'concept' identity gate (0.5464) is BELOW the lemma arm (0.5580) -> the WRITING identity gate must be lemma-TIGHT; type-compatibility belongs in the NON-writing bridge (consistent with the prior is-a-WRITE negative). (6) NO-REGRESS by construction: the fix is a KEY swap inside the read-only additive resolution consumer (writes only sm.commonnoun_resolution). (7) ADJACENT no-regress measured: re-keying the OTHER live head_lemma consumer (online_entity_cluster, sm.entities) on the concept lemma moves entity-layer CoNLL 0.6975->0.6974 (delta -0.0001) -- flat (the key defect is invisible to cluster-F1, which is dominated by big clusters). (8) GOLD-FREE (inherited): no gold field touches a resolution decision (prior W5)."
files_changed: "experiments/exp_cn_headkey_decomposition_v1.py, experiments/exp_cn_conceptkey_binding_v1.py, experiments/exp_cn_conceptkey_clustering_adjacent_v1.py, experiments/exp_cn_conceptkey_ood_v1.py, experiments/exp_cn_readerhead_endtoend_v1.py, experiments/exp_cn_bf_rolecue_v1.py, verification/test_cn_conceptkey_binding.py, notes/problems/the_common_noun_binder_is_string_identity_not_the_brains_content_addressable_typed_coref/SOLVED.md, notes/problems/the_common_noun_binder_is_string_identity_not_the_brains_content_addressable_typed_coref/UPSTREAM_BF_AUDIT_2026-09-10.md. NO hdlab/ writes (Q111 -- the proposed diff is in section 6). Reuses data/corpora/gum/ (pinned V12.1.0, on disk) + hdlab.{typed_coref,typed_spokes,commonnoun_binder,salience_binder,coref,situation_reader,online_entity_cluster} + experiments.{exp_situation_model_qa_modern_v1,exp_commonnoun_binder_live_report_v1,exp_unified_referent_gum_v1,exp_online_cue_cluster_gum_v1} + nltk-WordNet morphy (static offline lexical foundation)."
reverify: ".venv/Scripts/python.exe verification/test_cn_conceptkey_binding.py   # 7/7; recomputes every headline from source on the full GUM modern TEST (n=2855)"
---

# SOLVED -- the typed content-addressable binding beats the HONEST de-leaked string-identity floor CI-sep; the residual wall was a NON-brain-foundational upstream KEY, and fixing it (crude regex -> lexical-concept lemma) strengthens the win

**STATUS: SOLVED** (solver scope; WIP until the owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written -- the mechanism + the fix are proved in `experiments/` + `verification/`; the Q111 wire is proposed in
section 6. The disk outranks the brief, and it disagreed with the brief in two load-bearing ways (both documented below).

## The one-paragraph result
The prior owner-DONE problem already routed the reader's live per-mention common-noun RESOLUTION through the typed
content-addressable binding (`sm.commonnoun_resolution`); it beat the FAIR floor CI-sep but only reached PARITY with the
"string-identity 0.5412" floor, and located the residual as the reader's HEAD-LEMMA KEY. This problem finishes it. **(1)**
That 0.5412 floor is partly a LEAK: it keys redacted `the ____` mentions on the annotator-supplied real word ("____"->"show").
Removing ONLY that see-through -- keeping gold lemma quality on every visible word -- drops the honest floor to **0.5254**,
and the typed binding beats **0.5254 CI-sep even with the current crude key** (+0.0228). **(2)** The head-key itself is a
non-brain-foundational OUR-INVENTION: `commonnoun_binder.head_lemma` is a hand-rolled regex that (a) maps every non-alpha
head to `""` so all 176 redacted/digit heads FALSE-MERGE into one blob, and (b) over-strips singular `-us/-es` nouns
("corpus"->"corpu", "cases"->"cas"). Re-keying the binding on the brain-faithful lexical-CONCEPT lemma (WordNet morphy --
the substrate's own standing lemma tool, used by `causation_typing`/`event_type`/`generalized_event_knowledge`/
`goal_achievement`) lifts the binding **0.5482 -> 0.5580**, beating the honest de-leaked floor **+0.0326 CI[+0.0205,+0.0450]
CI-sep**, the fair same-regime morphy floor **+0.0319 CI-sep**, and the info-free twin **+0.0322 CI-sep**.

## 0. How the brain does this (PINNED vs OUR-INVENTION) -- and the exact deviation this problem fixes
- **PINNED (Ariel 1990 accessibility; Lambon-Ralph ATL hub; Lewis-Vasishth ACT-R retrieval).** A definite common noun is a
  CONTENT-ADDRESSABLE retrieval cue. The wordform is first mapped to a lexical-semantic CONCEPT in the anterior-temporal
  hub -- morphological variants ("dog"/"dogs", "man"/"men", "corpus"/"corpus") CONVERGE on one concept -- and the antecedent
  is retrieved by concept/type compatibility x salience (recency x frequency x role prominence), settled softly. The brain
  does NOT gate reference on surface-string identity; it gates on the CONCEPT.
- **OUR-INVENTION (the deviation).** The live binding keys its same-referent gate on `commonnoun_binder.head_lemma(head)`
  -- a surface-string regex. That is the non-brain-foundational step: it operates on the wordform SURFACE, not the lexical
  concept, so it both (a) collapses concept-DISTINCT redacted/numeric heads together (empty-string merge) and (b) splits
  concept-IDENTICAL forms apart ("corpus"->"corpu" != "corpus"). Replacing it with the concept lemma (morphy) makes the gate
  operate on the concept, as the brain does -- the exact-replication move the owner's checklist asks for.
- **PINNED division of labour, validated here.** The WRITING identity gate must be TIGHT (lexical-concept identity: same
  lemma), while superordinate TYPE compatibility ("the animal"->"a dog") stays a NON-writing bridge (Nieuwland hold). The
  loose-synonymy gate (arm `concept`, WordNet synset overlap) was tested and LOST (-0.0116 vs the lemma arm) -- over-merging
  polysemous words corrupts the same-head chain, exactly the failure the prior is-a-WRITE negative predicted. So the
  brain-faithful design is lemma-tight identity + soft type bridge, and the evidence confirms it.

## 1. What I built (experiments/)
- **`exp_cn_headkey_decomposition_v1.py`** -- decomposes the -0.0214 head-key gap on the SAME gold head-surface (isolating
  LEMMATISATION from parse/mention detection). Classifies every crude!=gold key disagreement and re-verifies the morphy
  floor first-hand.
- **`exp_cn_conceptkey_binding_v1.py`** -- a faithfulness-asserting PARAMETERIZED re-implementation of the live wire
  (`_reader_commonnoun_resolution`) with the head-KEY (`lemma_fn`) and the same-referent gate (`same_gate`) as variables.
  With `(head_lemma, "string")` it reproduces the deployed wire BYTE-IDENTICALLY (asserted on 20 docs). Arms: `crude`
  (deployed), `lemma` (concept-key fix), `concept` (loose-synonymy gate, the located sub-negative). Scores vs the crude / morphy
  / de-leaked-gold / raw-gold floors + the info-free twin, doc-paired bootstrap CI (URG `_paired_boot`).
- **`exp_cn_conceptkey_clustering_adjacent_v1.py`** -- the full-stack check: re-keys the OTHER live head_lemma consumer
  (`online_entity_cluster`, sm.entities) on the concept lemma and measures entity-layer CoNLL (does the shared upstream fix
  help/hurt the second consumer?).
- **`verification/test_cn_conceptkey_binding.py`** -- scaffold-free witness (7/7), recomputes every headline from source.

## 2. What I measured (GUM modern TEST, n=2855 anaphoric common-noun mentions)

### 2a. The head-key decomposition (why the crude regex loses signal)
| floor | acc | note |
|---|---|---|
| crude `head_lemma` string-identity | 0.5156 | the current FAIR floor |
| **morphy** string-identity | **0.5261** | **+0.0105 over crude -- a real lemmatiser recovers it (the prior board note "+0.0004" is WRONG; re-verified first-hand)** |
| gold `lemma_head` string-identity | 0.5412 | the "brief bar" -- but see the leak below |

243 crude!=gold key disagreements: **176 REDACTION** (`"____"->"show"`; crude maps all to `""` -> false-merge blob),
**36 CASE_PUNCT** (`census->censu`, `corpus->corpu` -- the regex strips singular `-us`), **21 MORPHOLOGY** (`cases->cas` --
the `-ses`->[:-2] rule over-fires), **10 MWE_COPULA**. Of the 86 scored crude-wrong->gold-right flips, morphy recovers 36
from raw text; the ~50 residual are redaction see-through (annotation raw text cannot access).

### 2b. The fix (re-key the typed binding on the concept lemma)
| arm | resolution acc | vs DE-LEAKED floor 0.5254 | vs raw LEAKY gold 0.5412 | vs fair morphy 0.5261 |
|---|---|---|---|---|
| crude (the deployed live wire) | 0.5482 | +0.0228 CI[+0.0079,+0.0372] **CI-sep** | +0.0070 (CI incl 0) | +0.0221 CI-sep |
| **lemma (concept-key FIX)** | **0.5580** | **+0.0326 CI[+0.0205,+0.0450] CI-sep** | +0.0168 (CI[-0.0003,+0.0327] incl 0) | +0.0319 CI-sep |
| concept (loose-synonymy gate) | 0.5464 | +0.0210 CI-sep | +0.0053 (incl 0) | +0.0203 CI-sep |
| info-free TWIN | 0.5257 | -- (lemma beats twin +0.0322 CI-sep) | | |

### 2c. The de-leak (the crux -- the brief's floor is partly a leak)
The raw gold-lemma floor 0.5412 keys redacted `the ____` mentions on the GUM-annotated REAL lemma. A raw-text reader sees
`"____"` and cannot know it is "show"/"dish"/"platter". Removing ONLY that see-through (redacted/non-alpha heads keyed on
their raw surface; gold lemma kept on every visible word) drops the floor to **0.5254** -- the strongest floor computable
from raw text. The +0.0158 difference is pure redaction annotation. The brief says "MEASURE ON THE HONEST DE-LEAKED FLOOR";
0.5254 is it, and the binding beats it CI-sep.

## 3. Performance vs the brain + FULL-STACK UPSTREAM (owner's directive)
- **Where we lose signal, itemized (this problem's slice):** a competent reader maps "corpus"/"cases"/"the ____" to the
  right lexical concept before any binding. The reader lost that signal at ONE non-brain-foundational upstream step -- the
  crude `head_lemma` regex -- not in the binding (the binding is the correct typed content-addressable organ). Fixing the
  KEY closes it; the binding then beats the honest floor.
- **THE UPSTREAM IS SHARED (full-stack finding).** `commonnoun_binder.head_lemma` is imported by BOTH live consumers: the
  resolution consumer (`situation_reader._resolve_commonnouns`) AND the live entity clustering
  (`hdlab.online_entity_cluster`, `:40/:111/:116`). So the crude regex is one shared non-BF upstream defect feeding two
  organs. Re-keying it is safe for BOTH: on the CLUSTERING consumer the concept key moves entity-layer CoNLL 0.6975->0.6974
  (-0.0001) -- FLAT (the key defect is invisible to cluster-F1, dominated by big person clusters, but it moves per-mention
  RESOLUTION, where every mention is a decision). So the concept-key's VALUE is specific to resolution; its RISK to
  clustering is nil. No other downstream consumer regresses.
- **The full chain, itemized (deepening cron) -- every stage traced, both upstream fixes PROTOTYPED:** raw text ->
  [span-head SELECTION: parse-based -0.049 CI-sep; FIXED by the BF `boundary_nphead`+`np_head_reduce` rule -> -0.015] ->
  [LEMMA/concept key: crude regex NOT_BF -> concept lemma, +0.0098] -> [typed content-addressable binding: BF, correct organ]
  -> [non-writing type bridge: BF]. The binding beats string-identity CI-sep at EVERY head-quality level (gold-head +0.0326;
  parse-head +0.0308; boundary-head +0.0277), so the mechanism is robust; the two reader-controlled upstream inputs (span-head
  selection, then lemma) were where signal was lost, and both now have prototyped brain-foundational fixes that make the chain
  EXCEED (raw-text binding 0.5426 beats the gold-head de-leaked floor 0.5254 CI-sep). Nothing on this chain is a ceiling.
- **Remaining headroom above this fix is WORLD KNOWLEDGE, and it is a SEPARATE problem.** The prior work's oracle type
  comparator ceiling (0.7492) is dominated by the encyclopedic/schema KB (handed off to
  `world_knowledge_common_noun_to_name_bridge...`) + generative situation-model inference -- NOT the head key. This problem
  closes the head-key wall; that problem owns the KB wall.

## 4. What I did NOT establish / would withdraw first
- **I did NOT beat the RAW leaky 0.5412 floor CI-sep** (+0.0168, CI lower bound -0.0003). That is the honest headline's one
  soft edge, and the first thing to state plainly: the binding reaches parity-plus with the raw floor and clears the
  HONEST de-leaked version of it. I deliberately did NOT chase the leaky number -- beating it would require reproducing
  gold's redaction see-through, which raw text cannot, and the owner's bar is the honest de-leaked floor. If a reviewer
  insists the literal 0.5412 must fall CI-sep, that clause is unmet by design (it is a leak), and the de-leaked 0.5254 is
  the floor that should stand.
- **The +0.0098 crude->concept GAIN is GUM-genre-specific; the FLOOR win generalizes.** OOD (GENTLE, n=275, 26 docs,
  `exp_cn_conceptkey_ood_v1.py`): the concept-key fix is **no-regress** (fix == crude == 0.5782) but adds nothing there,
  because GENTLE has NO redactions (raw gold == de-leaked, leak +0.0000 -- the redaction see-through is a GUM_reddit
  artifact) and few `-us/-es` over-strip heads, so the crude regex's bugs simply do not bite. What DOES replicate OOD is the
  headline direction "typed binding beats the honest de-leaked floor" (+0.0073 GENTLE vs +0.0326 GUM, underpowered). So the
  brain-foundational CORRECTNESS of the concept key holds universally (the crude regex is wrong; morphy is the right key; it
  is harmless where the surface is clean), but the measured accuracy GAIN is concentrated where the crude regex actually
  fails -- GUM's redaction-heavy genre. Honest headline: on the BOARD instrument (GUM) the fix is a CI-sep win over the honest
  floor AND a strict gain over crude; OOD it is a no-regress neutral.
- **The DEEPER upstream is measured AND its fix is PROTOTYPED (deepening cron) -- "all the way upstream", excel + exceed.**
  The board feeds GOLD head surfaces; when the reader picks its OWN mention heads from its arc parse
  (`exp_cn_readerhead_endtoend_v1.py`), the parse-based rule (`external_noun`) mis-heads ~7% of anaphoric-common mentions
  (post-modified NPs: "the environments identified by Quilis" -> the parser attaches the modifier) and costs the binding
  **-0.0490 CI[-0.0597,-0.0392]** -- ~5x the lemma fix, because a wrong head poisons the whole referent chain. NOT a ceiling:
  a BRAIN-FOUNDATIONAL span-head rule (`boundary_nphead`: the head is the nominal BEFORE post-modification -- take the initial
  nominal run to the first post-modifier boundary [ADP/VERB/rel-PRON/PUNCT], apply the substrate's `np_head_reduce`
  Right-Hand-Head-Rule for compounds -- REUSES the landed organ, zero fitted params) RECOVERS most of the wall: reader-head
  binding **0.5089 -> 0.5426**, cost **-0.0490 -> -0.0154** (recovers +0.0337), and the raw-text-path binding now BEATS even
  the GOLD-head de-leaked floor CI-sep (+0.0172 CI[+0.0039,+0.0313]). KEY INSIGHT: coref needs a CONSISTENT head (same NP
  structure -> same head token), NOT the exact gold head -- the deterministic POS-pattern rule is MORE self-consistent than
  the noisy arc root (its surface-fidelity is even higher, 94.7% vs 93.1%). So BOTH upstream inputs are now prototyped
  brain-foundationally (lemma key + span-head selection), and **the typed binding beats string-identity CI-sep at EVERY
  head-quality level** -- gold-head +0.0326, parse-head +0.0308, boundary-head +0.0277 (all CI-sep). The binding is robust;
  the upstream fixes lift the whole chain with the binding staying ahead. (Live-path note: the deployed reader uses GOLD
  mention heads on CoNLL corpora, so the span-head fix is a RAW-TEXT-path win -- it matters when reading un-annotated text.)
- **TESTED the UNFROZEN parser for head selection (owner question 2026-09-10) -- WORSE, as the disk predicted; the binding is
  robust even to it.** The never-frozen `OnlinePredictiveParser` (online, prediction-error-driven; Naseem prior + Friston
  PE-gated Hebbian; `exp_online_predictive_structure_learner_v1`, trained online on UD-EWT) has raw UAS ~0.44 (POS-only);
  using ITS arc heads for coref span-head gives head-pick fidelity 78.7% and coref 0.4438 -- WORSE than the frozen arc_parser
  (93.1%, 0.5089) and far below the parser-free `boundary_nphead` rule (94.7%, 0.5426). Head-quality ladder (reader-head +
  concept-key, n=2855): gold 0.5580 > boundary_nphead 0.5426 > frozen 0.5089 > unfrozen 0.4438. This CONFIRMS the substrate's
  own owner-DONE ruling ("UAS ~0.44 ... do NOT swap it"): the unfrozen parser's brain-faithful value is register-adaptive
  RELIABILITY/CONFIDENCE (OOD-robust where every frozen-parser confidence collapses to chance), NOT head accuracy -- a
  DIFFERENT lever, owned by `the_parser_is_a_frozen_supervised_hard_decode...`. Load-bearing positive: the typed binding
  beats string-identity CI-sep at EVERY head-quality level INCLUDING the weak unfrozen heads (+0.0263 CI[+0.0157,+0.0379]) --
  the mechanism does not depend on parse quality. And the WINNER for this sub-task uses NO full parser (`boundary_nphead`):
  coref head-selection is a shallow CONSISTENCY task, not a parser-accuracy task. (Arm: `exp_cn_readerhead_endtoend_v1.py
  --unfrozen` / `--compare`.)
- **The concept (loose-synonymy) gate is REFUTED as an identity gate** (0.5464 < 0.5580) -- a located sub-negative, not a
  caveat: content-addressable IDENTITY wants the lemma-tight concept; synonymy/is-a stay in the non-writing bridge.

## 5. Controls (all clean; witness 7/7)
FAITHFULNESS (crude arm == deployed wire, 20 docs) -> the delta is the fix. TWIN loses CI-sep -> type signal load-bearing.
FAIR morphy floor beaten CI-sep -> the binding adds over same-regime string-identity. DE-LEAK -> the honest floor. Located
sub-negative (loose synonymy < lemma). NO-REGRESS by construction (KEY swap in the read-only additive consumer) + measured
flat on the clustering consumer. GOLD-FREE inherited.

## 6. Proposed hdlab WIRE (Q111 -- strategy lands; solver does not write hdlab/)
1. **Add a brain-foundational `concept_lemma(surf)` helper** (next to `head_lemma` in `hdlab/commonnoun_binder.py`, so both
   consumers can import it): WordNet-morphy NOUN lemma of the head surface; NON-ALPHA heads (redaction `"____"`, digits) kept
   as their lowered surface -- NEVER collapsed to `""`. This is the substrate's standing lemma convention (already used by
   `causation_typing`/`event_type`/`generalized_event_knowledge`/`goal_achievement`); it is a static offline lexical
   foundation (nltk-WordNet), invariant-safe. Drop-in reference: `exp_cn_conceptkey_binding_v1.concept_lemma`.
2. **Re-key the RESOLUTION consumer only.** In `hdlab/situation_reader.py._resolve_commonnouns` replace
   `hl = head_lemma(m["head"])` (:4173) with `hl = concept_lemma(m["head"])`; re-key its private
   `_commonnoun_appos_map` is-a seed (:4064/:4073) to `concept_lemma` for consistency (it is consumed ONLY by
   `_resolve_commonnouns`). Sync the board copy `exp_situation_model_qa_modern_v1._reader_commonnoun_resolution` (:1699) +
   `board_commonnoun_resolution_dimension` (the two must stay in step, per the prior integration note). Leave
   `commonnoun_binder.head_lemma` itself unchanged -> the CLUSTERING consumer + `sm.entities` are byte-identical.
3. **Update the board floor to the honest DE-LEAKED gold floor (0.5254).** The current arm's "strongest floor" is already
   the FAIR same-lemmatizer floor (correct); ADD the de-leaked gold floor as the reference the headline beats CI-sep, and
   demote the raw leaky 0.5412 to a transparency line (the +0.0158 redaction leak documented). This is a measurement-honesty
   fix independent of the wire.
4. **Per no-more-default-off:** the resolution stream is ADDITIVE (writes only `sm.commonnoun_resolution`, reads
   role_mentions read-only), so it stays ON by default; the KEY swap does not touch coref / sm.entities / who_did_what.
   OPTIONAL (adjacent): re-key `online_entity_cluster` on `concept_lemma` too (measured no-regress, -0.0001 CoNLL) if a
   future consumer wants the concept key everywhere -- not required by this problem.

## 7. AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, E3 coreference / common-noun)
- **The residual non-brain-foundational component on the C2 chain was the HEAD-LEMMA KEY, not the binding.** The typed
  content-addressable binding (`typed_coref`) is the correct BF resolution organ; it was under-performing because its KEY --
  `commonnoun_binder.head_lemma`, a surface-string regex -- is an OUR-INVENTION that violates the brain's wordform->concept
  mapping (empty-collapse of non-alpha heads; over-strip of `-us/-es`). Mark `commonnoun_binder.head_lemma` NOT_BF and note
  the BF replacement is the lexical-concept lemma (`concept_lemma`, morphy). This is a shared upstream: `online_entity_cluster`
  imports the same crude key.
- **The `commonnoun_binder` NOT_BF entry is now precisely located.** Its resolution deficit is (i) its LitBank-clustering
  binding (person-gate + modifier-split + event-centrality -- already superseded for resolution by `typed_coref` and for
  clustering by `online_entity_cluster`) AND (ii) the crude head-key it still exports. The binder is increasingly vestigial
  for both live consumers; the residual live dependency worth retiring is its `head_lemma`.
- **Measurement-honesty deviation found:** the board's `common_noun` "string-identity 0.5412" floor embeds a redaction
  see-through LEAK worth +0.0158 (0.5254 de-leaked). Any claim measured against 0.5412 as "the honest floor" is inflated;
  the de-leaked 0.5254 is the raw-text-honest floor.

## 8. Adjacent components (seeds for the next problems; BF-fidelity + optimisation potential)
- **The span-head SELECTION organ (raw-text upstream) -- MEASURED + PROTOTYPED here; ready to promote.** Parse-based
  head-picking mis-heads ~7% of anaphoric-common mentions (post-modified NPs) at a -0.049 CI-sep coref cost. The prototyped
  `boundary_nphead` rule (initial nominal run to the first post-modifier boundary + `np_head_reduce` Right-Hand-Head-Rule)
  recovers it to -0.015 (raw-text binding 0.5426, beats the gold-head de-leaked floor CI-sep). BF status: brain-foundational
  (the UD/linguistic NP-head definition; zero fitted params; reuses the landed `np_head_reduce`). Promote it as the coref
  mention-head selector on the raw-text path -- a small, landable organ that de-risks the parser mega-cluster for coref
  WITHOUT waiting on a better arc_parser. Note: `np_head_reduce` alone handles compounds but NOT post-modification -- the
  boundary rule is the missing piece and could extend that organ.
- **The type comparator's KNOWLEDGE (encyclopedic C8 / schema).** Already a filed problem
  (`world_knowledge_common_noun_to_name_bridge...`); oracle headroom +0.18, dominated by KB + situation-model inference.
- **`online_entity_cluster` keys on the same crude `head_lemma`.** Re-keyed no-regress here (-0.0001 CoNLL); a candidate to
  fold the concept key into when its instrument is next revisited (its value there is nil on cluster-F1, so low priority).
- **`concept_lemma` as a shared organ.** morphy is used ad-hoc across 6+ organs; promoting one canonical `concept_lemma`
  helper would remove the divergent hand-rolled `head_lemma` regex from the coref path (and is a small consolidation win).

## KEY REALIZATIONS (the enabling moves)
- **Re-verify the disk's own decomposition -- it was wrong.** The board note claimed "WordNet morphy recovers +0.0004", which
  read as "the head-key gap is unfixable annotation". Re-measuring morphy as a same-key floor first-hand showed +0.0105 --
  more than half the gap -- which flipped the whole problem from a located-negative into a fixable brain-foundational upstream.
- **Classify the key disagreements, do not just count the gap.** Splitting crude!=gold into REDACTION / CASE / MORPHOLOGY /
  MWE exposed that the crude regex FALSE-MERGES all non-alpha heads to `""` -- a bug distinct from "can't resolve redactions",
  and one a raw-text-honest key fixes.
- **The floor was leaking, so I de-leaked the FLOOR, not just the model.** Realising the 0.5412 floor keys redacted heads on
  the gold real word made the "parity" honest-to-explain: the model was already beating the HONEST floor; the tie was against
  a floor that cheats. Removing only the see-through (0.5412->0.5254) is the measurement that turned parity into a CI-sep win.
- **Content-addressable IDENTITY is lemma-tight; type-compat is the soft bridge.** Trying the loose-synonymy gate and watching
  it LOSE confirmed the brain-faithful split -- and matched the prior is-a-WRITE negative, so it is a mechanism finding, not a
  tuning artifact.
- **Faithfulness by a byte-identity assert makes the delta trustworthy AND no-regress free.** Because the crude arm reproduces
  the deployed wire exactly, the +0.0098 is attributable to the key alone, and the additive/read-only structure makes the
  no-regress a construction fact, not a fragile separate measurement.

## TLDR (plain English)
When the reader meets a plain-noun phrase like "the corpus" and has to decide which thing it means, it first boils the word
down to a base form to compare it with earlier mentions. That boiling-down step was a hand-written spelling rule with two
bugs: it turned blanked-out words (privacy redactions written as "____") all into the SAME empty string -- so it wrongly
merged unrelated blanks -- and it chopped the end off ordinary singular words ("corpus" became "corpu"). Swapping that
hand-rule for the standard dictionary-based word-normaliser the rest of the system already uses (the brain's own
"map-the-word-to-its-concept" step) fixes both, and the reader now recognises 56 plain-noun mentions correctly per 100 vs
the honest dumb-rule baseline's ~53 -- a clean, statistically separated win, with an information-scrambled version losing as
it should. Two footnotes for honesty: (1) the "54.1" baseline everyone had been comparing to was inflated -- it secretly
used the answer key to see through the redactions, and once you take that cheat away it drops to ~52.5, which our method
clearly beats; (2) this same word-boiling step is ALSO used by the entity-grouping part of the reader, and swapping it there
changes nothing (safe), because that part is graded by big groups where a few rare words don't matter. The deeper remaining
gap is world knowledge ("the artist" = an earlier painter's name), which is a different, already-filed job.

## QUESTIONS
None blocking. One judgement call for the owner/strategy at integration: the headline is stated against the HONEST DE-LEAKED
floor (0.5254), because the literal 0.5412 in the brief embeds a redaction-annotation leak. If you would rather the headline
quote the raw 0.5412, the result there is honest parity-plus (+0.0168, CI includes 0), and the located reason is the
irreducible redaction. I recommend the de-leaked floor as the honest bar (it is what the brief's own "measure on the honest
de-leaked floor" instruction asks for).

## NEXT STEPS (priority-ordered; strategy owns any hdlab landing, Q111)
1. **HIGH -- land the concept-key wire (section 6.1/6.2):** add `concept_lemma`, re-key `_resolve_commonnouns` +
   its appos seed, sync the board copy. One-line KEY swap; additive; no-regress by construction + measured.
2. **HIGH -- fix the board floor honesty (section 6.3):** add the de-leaked gold floor (0.5254) as the reference the
   `common_noun` headline beats CI-sep; demote the raw 0.5412 to a documented transparency line (the +0.0158 redaction leak).
3. **MEDIUM/HIGH -- promote the PROTOTYPED span-head selector (raw-text path):** the `boundary_nphead` rule
   (`exp_cn_readerhead_endtoend_v1.py`, mode=boundary_nphead) recovers the parser head-selection wall from -0.049 to -0.015
   CI-sep and makes the raw-text binding (0.5426) beat the gold-head de-leaked floor CI-sep. Landable as the coref
   mention-head selector on un-annotated text (reuses `np_head_reduce`; zero fitted params). Inert on the current GUM board
   (gold heads), so it does not affect the headline; it de-risks reading real text. Consider folding the boundary rule into
   `np_head_reduce` (extends it from compounds to post-modification).
4. **LOW/OPTIONAL -- fold `concept_lemma` into `online_entity_cluster`** when its instrument is next revisited (no-regress,
   nil cluster-F1 value -- do it for consistency, not for a gain).

## SUBSTRATE INCORPORATION MANIFEST (owner 2026-09-09 -- distilled load-bearing knowledge to incorporate on DONE)
- **INCORPORATE:** the `concept_lemma` (morphy, non-alpha-safe) head-key for the common-noun RESOLUTION consumer (section 6);
  the de-leaked-gold-floor measurement (0.5254) as the honest `common_noun` floor.
- **INCORPORATE-AS-DURABLE-NEGATIVE:** the raw gold-lemma 0.5412 floor embeds a +0.0158 redaction see-through LEAK (record in
  BRAIN_FOUNDATIONAL_AUDIT E3 + `reference_retired_claims`); the loose-synonymy identity gate LOSES (identity must be
  lemma-tight; type-compat is the non-writing bridge); the prior board "morphy +0.0004" note is WRONG (it is +0.0105).
- **INCORPORATE (raw-text path, prototyped): the `boundary_nphead` span-head selector for coref mention heads** -- initial
  nominal run to the first post-modifier boundary + `np_head_reduce` (Right-Hand-Head-Rule). Recovers the parser head-selection
  wall from -0.049 to -0.015 CI-sep; makes the raw-text binding beat the gold-head de-leaked floor CI-sep; zero fitted params;
  reuses the landed organ. Inert on gold-head corpora. Candidate to extend `np_head_reduce` from compounds to post-modification.
- **INCORPORATE-AS-DURABLE-FINDING (full-stack upstream):** the parser's span-head selection is the dominant raw-text upstream
  wall for coref (~7% mis-heads, -0.049 CI-sep via chain-poisoning); the typed binding beats string-identity CI-sep at EVERY
  head-quality level (gold +0.0326, parse +0.0308, boundary +0.0277); coref needs a CONSISTENT head, not the exact gold head.
  Record in CROSS_SOLUTION_IMPROVEMENT_MAP as this solution's consumed input (mention head surface) + the prototyped fix.
- **DO-NOT-INCORPORATE:** the crude `commonnoun_binder.head_lemma` regex on the resolution path (retire it there); the
  `concept` loose-synonymy arm (refuted).
