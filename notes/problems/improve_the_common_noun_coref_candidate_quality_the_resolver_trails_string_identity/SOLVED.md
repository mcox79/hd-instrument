---
problem: improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity
status: PARTIAL
bar: "It BEATS same-head string-identity CI-separated on MODERN GUM common-noun coref, floor recomputed on the SAME population (string-identity 0.5412 is the floor to beat; the live URG resolver 0.4879 is the incumbent it must also clear) ... The info-free twin LOSES CI-separated ... NO pronoun-dim regress + NO named-antecedent regress. A rigorous NEGATIVE is a FULL PASS (e.g. 'candidate generation reaches the gold antecedent X% but ranking cannot beat same-head because the residual is the different-head world-knowledge bridge, N of M, which routes to the entity-type KB not salience -- located and counted')."
result: "RIGOROUS LOCATED NEGATIVE that REFUTES the brief's premise (candidate/ranking quality, not knowledge, is the lever). On the board's OWN common_noun_coref instrument (URG unified resolver, MODERN GUM TEST=odd docs, n=2855 anaphoric common-noun mentions, metric = picked-referent.dominant_gold_eid == mention.eid), NO glass-box candidate-generation/ranking mechanism BEATS same-head string-identity (0.5412). The measured LADDER: incumbent URG 0.4879 -> pollution-ceiling 0.5310 (pronouns never write eids) -> string-identity 0.5412 -> gold-cluster oracle 0.5825. EVERY glass-box arm is <= string-identity CI-separated-or-below: weighted parallel constraint satisfaction (Ariel head cue + ACT-R recency + Centering role + soft agreement) 0.5138; recall-safe same-head 0.4862; +WordNet different-head bridge 0.4837; Nref confidence-gated writeback 0.4928; recency/modifier/ACT-R/combo SPLITTERS all below string-identity on BOTH the board metric AND field-standard CoNLL (string-identity CoNLL 0.7536 vs recency-gap 0.7434 / modifier 0.7507 / combo 0.7381). TWO located causes, counted: (1) the resolver trails string-identity because weak pronoun resolution (~47%) POLLUTES the shared DRT entity cards -- eliminating that pollution recovers +0.045 of the 0.053 gap (0.4879->0.5310) but STILL does not reach string-identity, and de-polluting is ANTAGONISTIC (it regresses the pronoun consumer, the shared-card tradeoff); (2) BEATING string-identity is WORLD-KNOWLEDGE-bound -- 33.7% of items (963/2855) are DIFFERENT-HEAD anaphors string-identity scores 0, and only ~15-18% of those are glass-box-reachable (WordNet synonym/2-hop-hypernym) at ~52-55% precision (pollution eats the +0.027 net); the remaining ~82% route to the SIBLING entity-type-KB brief (P31), NOT to salience. The gold-cluster oracle ceiling 0.5825 confirms the only thing above string-identity is world-knowledge-level clustering. The info-free twin does NOT lose (random-within-same-head ties the ranked pick) -> there is no glass-box RANKING headroom on this population; the signal is entirely the same-head CONTENT cue, which string-identity already captures."
floor: "Strongest floor actually run, recomputed on the SAME n=2855 GUM-TEST common-noun population + the SAME board scorer: same-head STRING-IDENTITY = 0.5412 (the floor to beat). Incumbent URG unified = 0.4879 (CI-below string-identity, delta -0.0532 CI[-0.0701,-0.0368]). Other floors on the same population: recency 0.0855; separate (per-type surface-head) 0.4872. Ceilings recomputed on the same population: pollution-ceiling (no pronoun writeback) 0.5310; gold-cluster oracle (no-LLM surface+gender pick) 0.5825; correct-pronoun-binding upstream ceiling 0.5124. Field-standard CoNLL (MUC/B3/CEAFe) on the same common-noun clustering: string-identity 0.7536, best splitter 0.7507."
controls: "(1) INFO-FREE TWIN = shuffle the candidate salience -> random compatible pick, same shape+counts: does NOT lose (delta ~0.0, CI incl 0) -> proves the ranking carries NO glass-box signal here (excludes 'better ranking would win'; the same-head content cue is the whole signal and string-identity has it). (2) POLLUTION CEILING = pronouns never write gold eids to cards (isolates cross-type pollution as the incumbent's deficit): recovers +0.045 but stays below string-identity -> excludes 'the deficit is bad common-noun candidate/ranking' (it is pollution) AND 'de-pollution beats the floor' (it does not). (3) GOLD-CLUSTER ORACLE (perfect clustering, no-LLM surface+gender pick) = 0.5825 -> excludes 'a better glass-box clusterer would clear it' (the headroom above string-identity is only 0.041 and it requires gold clusters = world knowledge). (4) METRIC AUDIT: the same splitters scored under field-standard CoNLL (penalizes over-merge) STILL lose to string-identity -> excludes 'the board's dominant-eid metric is the artifact / string-identity only wins by over-merge' (it wins on both metrics; modern-GUM same-head groups are mostly single-entity). (5) NO-REGRESS on the resolver's other consumers: de-pollution REGRESSES pronoun (-0.024 CI[-0.049,-0.008]) -> the shared card is antagonistic across consumers; name +0.008 (no regress). (6) BRIDGE PRECISION control: the different-head bridge is ~52-55% precise and pollutes; the dev weight-sweep of the weighted-CS resolver drove the synonym-bridge weight to 0. (7) UPSTREAM CEILING: correct (gold) pronoun binding recovers common to 0.5124 only -> better upstream pronoun resolution helps but cannot make common-noun BEAT string-identity."
files_changed: "experiments/exp_commonnoun_candidate_diagnostic_gum_v1.py, experiments/exp_commonnoun_lever_ceilings_gum_v1.py, experiments/exp_commonnoun_clustering_probe_gum_v1.py, experiments/exp_commonnoun_bridge_probe_gum_v1.py, experiments/exp_commonnoun_metric_audit_gum_v1.py, experiments/exp_commonnoun_weighted_cs_resolver_gum_v1.py, experiments/exp_commonnoun_recallsafe_bridge_resolver_gum_v1.py, experiments/exp_commonnoun_diffhead_anatomy_gum_v1.py, verification/test_commonnoun_candidate_diagnostic.py, verification/test_commonnoun_lever_ceilings.py, verification/test_commonnoun_metric_audit.py, verification/test_commonnoun_recallsafe_bridge_resolver.py, verification/test_commonnoun_diffhead_anatomy.py, data/exp_commonnoun_candidate_diagnostic_gum_v1/metrics.json, data/exp_commonnoun_lever_ceilings_gum_v1/metrics.json, data/exp_commonnoun_clustering_probe_gum_v1/metrics.json, data/exp_commonnoun_bridge_probe_gum_v1/metrics.json, data/exp_commonnoun_metric_audit_gum_v1/metrics.json, data/exp_commonnoun_weighted_cs_resolver_gum_v1/metrics.json, data/exp_commonnoun_recallsafe_bridge_resolver_gum_v1/metrics.json, data/exp_commonnoun_diffhead_anatomy_gum_v1/metrics.json, notes/problems/improve_the_common_noun_coref_candidate_quality_the_resolver_trails_string_identity/SOLVED.md. NO hdlab/ writes (Q111 -- proposed direction stated below). Reuses data/corpora/gum/ (pinned V12.1.0, already on disk)."
reverify: ".venv/Scripts/python.exe verification/test_commonnoun_candidate_diagnostic.py (4/4)  AND  test_commonnoun_lever_ceilings.py (3/3)  AND  test_commonnoun_metric_audit.py (3/3)  AND  test_commonnoun_recallsafe_bridge_resolver.py (6/6)  AND  test_commonnoun_diffhead_anatomy.py (3/3)"
---

# SOLVED (PARTIAL) -- common-noun coref candidate quality: a rigorous located negative that refutes the brief's premise

**STATUS: PARTIAL** (solver scope; WIP until the owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written -- everything is proved in `experiments/` + `verification/`; the proposed DIRECTION is stated below and
STRATEGY lands any hdlab change (Q111). This is the rigorous LOCATED NEGATIVE the bar names as a FULL PASS -- and it is
the bar's own worked example: *"candidate generation reaches the gold antecedent X% but ranking cannot beat same-head
because the residual is the different-head world-knowledge bridge ... which routes to the entity-type KB not salience."*

## The one-screen result (the ladder)
On the board's OWN `common_noun_coref` instrument (URG unified resolver; modern GUM TEST; n=2855 anaphoric common-noun
mentions; metric = picked referent's dominant gold eid == mention eid), recomputed floors on this exact population:

| arm (common-noun dim) | acc | what it isolates |
|---|---|---|
| recency floor | 0.0855 | trivial lower bound |
| **incumbent URG unified** | **0.4879** | the live board pick (CI-below the floor it should beat) |
| separate (per-type surface head) | 0.4872 | no cross-type merge |
| weighted parallel constraint satisfaction (Ariel+ACT-R+Centering+soft agr) | 0.5138 | the brain's cue-based retrieval, faithfully built |
| recall-safe same-head | 0.4862 | soft (not hard) agreement |
| + WordNet different-head bridge | 0.4837 | accessibility-shaped candidate generation |
| Nref confidence-gated pronoun writeback | 0.4928 | hold-under-ambiguity |
| **pollution ceiling** (pronouns never write eids) | **0.5310** | isolates the incumbent's real deficit |
| **same-head STRING-IDENTITY (the floor to beat)** | **0.5412** | the trivial baseline |
| correct (gold) pronoun binding | 0.5124 | the upstream (pronoun) ceiling |
| **gold-cluster ORACLE** (no-LLM surface+gender pick) | **0.5825** | the world-knowledge ceiling |

**No glass-box candidate/ranking arm beats string-identity. The only thing that does is gold-cluster-level clustering
(0.5825) -- i.e. world knowledge.** The info-free twin does NOT lose (random-within-same-head ties the ranked pick), so
there is no glass-box RANKING headroom on this population.

## 0. How the brain does this (the opening move) and what is PINNED vs OUR-INVENTION
- **PINNED (the computation).** Coreference is incremental content-addressable cue-based retrieval (Lewis & Vasishth 2005;
  McElree): the anaphor is a retrieval cue, all discourse referents are matched in PARALLEL by a weighted sum of cue
  overlaps, argmax retrieves. For a DEFINITE common noun the dominant cue is descriptive CONTENT (the head-type), not
  recency (Ariel 1990 Accessibility: a full definite NP marks a LESS-accessible antecedent than a pronoun). Grammatical
  salience ranks by Centering (subject>object>other; Grosz-Joshi-Weinstein 1995). Agreement is a SOFT graded cue
  (Carminati 2002). **This corrects the brief:** the substrate store (E3, `substrate_map --organ E3`) states the brain
  does NOT filter-then-rank -- it does weighted parallel constraint satisfaction with the cue ORDERING
  agreement>role>recency. The brief's "Lappin-Leass HARD-filter-then-rank" is not the brain's mechanism; I built the
  weighted-CS version (the store outranks the brief).
- **PINNED (the wall).** Competitive resolution among 2+ same-type antecedents ("which of two doctors is 'the doctor'")
  is resolved by the SITUATION MODEL / world knowledge (Zwaan-Radvansky; Sanford-Garrod bonding->resolution). E3
  states this "has NEVER been tested at scale"; the sibling SOLVED `form_a_discourse_referent...` measured that 82% of
  competitive common-noun links need exactly this. It is world-knowledge, and the no-LLM-at-inference invariant bars it.
- **OUR-INVENTION-UNDER-TEST (swept, not adopted):** cue weights, discourse-new threshold, ACT-R decay, recency-split
  window, modifier-conflict penalty, bridge weight. Swept on DEV; none clears string-identity on TEST.

## 1. The enumeration (an absence claim requires an enumeration, not a search) -- `exp_commonnoun_candidate_diagnostic`
Reproduces the board defect EXACTLY (URG 0.4879 vs string-identity 0.5412, delta -0.0532 CI[-0.0701,-0.0368], n=2855)
and decomposes every anaphoric common-noun mention by reachability:
- **66.3% (1892) reachable by head** (a prior same-head mention of the same entity exists). On this slice string-identity
  scores **0.8166** and the incumbent only **0.7363** -- **the incumbent LOSES 214 same-head items string-identity gets.**
  It is not candidate-STARVED there; it is SELF-INFLICTED (its hard gn-filter fragments the chain + cross-type merge
  pollutes the dominant).
- **33.7% (963) different-head only.** BOTH string-identity and the incumbent's common path score these **0** -- both are
  head-gated. This is the slice where the only possible gain lives, and it is where the world-knowledge bridge lives.
- **0% unreachable** (every anaphoric mention has a prior antecedent -- the population is clean).

## 2. Why candidate/ranking cannot beat string-identity (every lever, measured)
- **SPLITTING the over-merge is net-negative** (`exp_commonnoun_clustering_probe`, `exp_commonnoun_metric_audit`).
  string-identity lumps all same-head mentions into one cluster (347 over-merge losses), but on modern GUM same-head
  groups are mostly single-entity, so every splitter (recency-gap W20/40/80, modifier-split, ACT-R-split, combo) breaks
  MORE correct merges than it fixes -- losing on BOTH the board's dominant-eid metric AND field-standard CoNLL
  (string-identity CoNLL 0.7536 vs best splitter 0.7507). **This refutes the "audit the ruler" hypothesis:**
  string-identity's strength is NOT a dominant-eid-metric artifact; it is genuinely strong because the over-merge it
  commits is small (E3: competitive same-type is world-knowledge-bound and rare on modern text).
- **DIFFERENT-HEAD bridging is glass-box-capped, and the residual is world-knowledge -- now OPENED and counted**
  (`exp_commonnoun_lever_ceilings`, `exp_commonnoun_bridge_probe`, `exp_commonnoun_diffhead_anatomy`). The different-head
  anatomy (n=772) breaks down as: **appos/copula text-stated is-a 5.0% | name-containment 0.7% | WordNet-type 10.0% |
  RESIDUAL WORLD-KNOWLEDGE / abstract-anaphora 84.3%.** The residual examples are exactly world knowledge ("the country"
  <- "Argentina"; "the college" <- "American College of Pediatricians") and abstract/event anaphora ("this trend", "these
  cases", "that need") -- neither is glass-box in-text resolvable; the entity-type cases route to the SIBLING
  `acquire_wikidata_p31_entity_type_kb...` asset (P31), the abstract-anaphora cases are a different phenomenon. Only 15.7%
  is glass-box-reachable, and EVERY glass-box bridge nets ~0 once card-pollution is included: WordNet net +0.027 mention-
  level collapses in the resolver (dev sweep drove its weight to 0), and even the HIGHEST-precision, genuinely in-text cue
  -- apposition/copula is-a ("Google is a company", learned from the text, not world knowledge) -- nets **-0.0007 over the
  no-pollute base** (CI[-0.0085,+0.0070], not sep): the 5% reach times imperfect precision, minus the pollution it adds to
  the shared cards, cancels exactly. So the different-head slice is DEFINITIVELY world-knowledge-bound at inference.
- **RECALL-SAFE (soft) agreement barely matters** here: recall-safe 0.4862 vs hard-filter 0.4879 -- gender is ~6%-sparse on
  common nouns (sibling compose SOLVED), so the hard filter rarely fires wrongly on common nouns.
- **The info-free twin does NOT lose** on any arm (random-within-same-head ties the ranked pick) -- decisive evidence that
  the glass-box RANKING has no headroom: the same-head CONTENT cue is the entire signal, and string-identity already has it.

## 3. The resolver's real deficit is cross-type PRONOUN POLLUTION (located + counted), and it is ANTAGONISTIC to fix
`exp_commonnoun_recallsafe_bridge_resolver` isolates the cause. String-identity keeps pronouns in their own surface-lemma
buckets (it does not resolve them to entities), so common-noun clusters stay pure. The URG unified resolver RESOLVES
pronouns into the shared DRT cards -- and pronoun resolution is only ~47% accurate, so wrong pronoun bindings write wrong
gold eids into common-noun cards and flip their dominant. **Turning off pronoun writeback entirely (the pollution ceiling)
recovers +0.045 (0.4879 -> 0.5310) -- but it STILL does not reach string-identity, and it REGRESSES the pronoun consumer
(-0.024 CI[-0.049,-0.008]).** The shared entity card is antagonistic across consumers (the same finding the sibling compose
SOLVED reached from the pronoun side; here it appears on the common side). Even a Nref confidence-gate (hold-under-ambiguity,
the brain-faithful partial fix) only reaches 0.4928 and trades off pronoun. **Correct (gold) pronoun binding -- the upstream
ceiling -- reaches only 0.5124**, so even a perfect upstream pronoun resolver cannot make common-noun BEAT string-identity.

## 4. Performance vs the brain (the mechanism-diff), and the full-stack upstream
- Where we lose signal vs a competent reader: the reader resolves competitive same-type ("two doctors") and different-head
  ("the artist"->"Zurbaran") reference by the SITUATION MODEL / world knowledge. We have the retrieval op (ACT-R,
  content-addressable), Centering salience, Ariel accessibility, and soft agreement -- all faithfully built. We LACK the
  world-knowledge/situation-model cue that resolves the 33.7% different-head slice and the competitive same-head slice.
  The gold-cluster oracle (0.5825) is the ceiling that cue would unlock; string-identity (0.5412) is already 93% of it.
- **UPSTREAM (the owner's full-stack directive), prototyped:** the upstream of common-noun coref is (a) the mention
  detector/NP-head chunker (here GOLD mentions -- the competent-reader reference, NOT the bottleneck), (b) the agreement
  features (gender ~6%-sparse -> recall-safe vs hard barely matters), and (c) PRONOUN resolution -- the pollution source.
  Better pronoun resolution is the real upstream lever: the sibling compose SOLVED already EXCEEDS on he/she pronoun coref
  (+0.082 CI-sep on modern GUM). That upstream win reduces the pollution that caps common-noun -- but the measured upstream
  ceiling (0.5124 at correct binding) shows it recovers common toward parity, NOT past string-identity. **Every component
  we built is brain-foundational; the one that beats the wall (the world-knowledge/situation-model cue) is the sibling
  P31-KB asset, out of scope here.** No other downstream consumer is helped by changing the common-noun candidate path
  (de-pollution regresses pronoun; name is byte-stable +0.008).

## 5. Proposed DIRECTION (Q111 -- strategy owns any hdlab landing; solver does not write hdlab/)
1. **Do NOT change the URG resolver's common-noun candidate/ranking.** Recall-safe agreement, splitting, different-head
   bridging, and Nref-gating all FAIL to beat string-identity on this population, and de-polluting regresses the pronoun
   consumer. There is no glass-box candidate/ranking win to land. Keep the common-noun path as-is.
2. **The board's `common_noun_coref` instrument scores a POLLUTED view.** The incumbent's 0.4879 is dragged below
   string-identity by pronoun pollution of the shared cards; the un-polluted common-noun clustering is ~0.5310 (~parity).
   Consider reporting the common-noun dim on the common+name view of the cards (or adding string-identity 0.5412 as the
   acknowledged glass-box ceiling), so the dim measures common-noun clustering quality rather than pronoun-pollution
   collateral. This is a board-instrument fix analogous to the ledger's "landed != live / board under-measures" pattern.
3. **The real lever to BEAT string-identity is upstream + world-knowledge, both already-filed elsewhere:** (a) land the
   sibling compose SOLVED's pronoun stack (+0.082) to shrink the pollution; (b) the SIBLING
   `acquire_wikidata_p31_entity_type_kb_for_name_bridge_coref` asset for the 33.7% different-head slice (a static offline
   asset, invariant-safe). Neither is this brief's candidate-quality lever.

## 6. AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md` sec 2b, E3 coreference / common-noun)
- **NEW finding to fold in:** on modern GUM common-noun coref, the URG unified resolver (the board's `common_noun_coref`
  instrument) trails same-head string-identity (0.4879 vs 0.5412) primarily because weak pronoun resolution (~47%)
  POLLUTES the shared DRT entity cards -- eliminating that pollution recovers +0.045 (to 0.5310) but does not reach
  string-identity, and de-polluting is ANTAGONISTIC (regresses the pronoun consumer). The shared-card antagonism the
  2026-09-06 E3 entry noted for `unified_referent` (pronoun side) is now confirmed on the COMMON-NOUN side.
- **CONFIRMS E3's brain-math correction:** the brain does weighted parallel constraint satisfaction, not filter-then-rank;
  a faithful weighted-CS common-noun resolver (Ariel head cue + ACT-R + Centering + soft agreement) reaches 0.5138 and does
  not beat string-identity -- the ranking has no glass-box headroom (info-free twin ties). The residual is the situation
  model / world knowledge (gold-cluster oracle 0.5825), i.e. the different-head bridge routes to the entity-type KB, not to
  salience. This makes the brief's "candidate quality, not knowledge" premise INACCURATE on disk: it is a knowledge wall.

## 7. Adjacent components (evaluated for brain-fidelity + optimization -> next problems)
- **PRONOUN resolution (`event_centrality_coref` / URG pronoun pick):** the pollution source. Brain-faithful op (ACT-R),
  but ~47% accurate -> pollutes shared cards. The sibling compose SOLVED's +0.082 stack (phi person-feature exclusion,
  agreement-narrow on `him`, soften generic-suppress) is the landable upstream fix that shrinks the pollution. High-value.
- **The shared DRT entity card (unification):** antagonistic across consumers (pronoun vs common-noun) when the writers are
  weak. Brain-faithful in principle (one card per entity), but our weak writers make it net-negative on any single
  consumer's metric. The fidelity fix is BETTER WRITERS (accurate pronoun binding), not un-unifying.
- **The entity-type-KB / situation model (the 33.7% different-head slice):** the genuine route past the wall; a static
  offline asset (P31 / scenario-role KB), invariant-safe, already the SIBLING brief. This is where the leverage is.
- **The board `common_noun_coref` instrument:** measures a pronoun-pollution-collateral view; a candidate for a
  measurement upgrade (common+name view, or acknowledge string-identity as the glass-box ceiling).

## KEY REALIZATIONS (the enabling moves)
- **Ask whether it could succeed first, and enumerate.** The diagnostic (66% same-head, 34% different-head, 214
  self-inflicted, slice-B scored 0) predicted the whole result before any resolver was tuned: string-identity already
  captures the only glass-box signal (the same-head content cue), and the rest is world-knowledge.
- **The info-free twin not losing is the tell.** When shuffling the candidate ranking does NOT hurt, the ranking is not
  where the signal is -- so no amount of salience/Centering/ACT-R tuning can win. The content cue (head match) is the whole
  game, and the trivial baseline has it.
- **Audit the ruler -- and accept the audit's answer.** I hypothesized the board's dominant-eid metric under-penalizes
  over-merge (so a splitter would win on CoNLL). It does not: string-identity wins on CoNLL too, because modern-GUM
  same-head groups are mostly single-entity. The disk refuted my own reframe, which made the negative trustworthy.
- **The trivial baseline was strong for a reason we mislabeled.** The resolver trails string-identity not because its
  common-noun candidate/ranking is bad, but because it RESOLVES PRONOUNS into the shared cards and pronoun resolution is
  weak -- string-identity wins by NOT doing the harder job. The defect is cross-type pollution, not candidate quality;
  and fixing it is antagonistic, so the honest route is upstream pronoun accuracy + the world-knowledge asset.

## What I did NOT establish / would withdraw first
- I did NOT beat string-identity (the bar's headline) -- this is a located negative, and if a reviewer requires the beat,
  it is a clean REFUTED on that clause. The FIRST thing I would flag.
- The different-head bridge net (+0.027 upper bound) is measured at the MENTION level with a most-recent-related pick; the
  resolver-level net is lower once card-pollution is included (the dev sweep zeroed the bridge weight). I would withdraw
  any bridge number quoted as a live gain first.
- The upstream ceiling (0.5124 at correct pronoun binding) uses a gold-eid write to isolate the direction; the realistic
  upstream lever is the compose SOLVED's +0.082, whose exact common-noun pollution-reduction on THIS metric I argue from
  the ceiling, not measured end-to-end (a clean follow-on: land the compose stack, re-measure common-noun).
- GUM only (modern, TEST=odd docs). No OOD (GENTLE/reddit) arm; the world-knowledge ceiling is argued from the oracle, not
  from a second corpus.

## TLDR (plain English)
The reader was said to be worse at re-recognising repeated common-noun mentions (a second "the doctor") than a dumb
same-word rule, and the brief guessed the fix was a smarter short-list-and-ranking. I built the brain's actual method for
this (match by description, rank by how recently/prominently each candidate was mentioned, rule out mismatches gently) and
measured every version. None beats the dumb same-word rule -- and crucially, a scrambled-ranking version does JUST as well,
which proves the ranking isn't where the signal is: matching the same word is the whole game, and the dumb rule already
does that. Two real findings came out of it. First, the reader looks worse than the dumb rule mainly because it also tries
to resolve pronouns ("he", "she") into the same character records, and it only gets those right about half the time, so the
wrong guesses contaminate the records -- the dumb rule wins by simply not attempting that harder job. Turning off that
contamination recovers most of the gap but still doesn't beat the dumb rule, and it makes pronoun-tracking worse (you can't
have it both ways with one shared record). Second, the only way to actually beat the dumb rule is world knowledge -- linking
"the artist" to "Zurbaran", or telling two same-type characters apart -- which our no-outside-AI rule forbids at read time
and which is exactly what a separately-planned offline fact store is for. So the brief's premise is wrong on the evidence:
this is a knowledge problem, not a short-list-quality problem, and the honest fixes are (a) better pronoun-tracking upstream
and (b) the planned offline fact store -- not a cleverer common-noun ranking.

## QUESTIONS
None blocking. One judgement call for the owner: the board's common-noun-coref score (0.4879) reflects pronoun-contamination
collateral, not common-noun clustering quality (which is ~0.5310, near the dumb-rule 0.5412). If you want the dim to measure
common-noun clustering rather than pronoun-contamination, that is a small board-instrument change strategy can make; I did
not touch it (out of solver scope).

## NEXT STEPS (priority-ordered; strategy owns any hdlab/board change, Q111)
1. **Do NOT ship a common-noun candidate/ranking change** -- every glass-box lever fails to beat string-identity and
   de-polluting regresses pronouns. Keep the URG common-noun path as-is.
2. **Land the sibling compose SOLVED's pronoun stack (+0.082)** to shrink the pollution that caps common-noun; then
   re-measure the common-noun dim (predicted to rise toward ~0.53 parity, not past string-identity).
3. **Pursue the SIBLING `acquire_wikidata_p31_entity_type_kb...` asset** for the 33.7% different-head slice -- the genuine,
   invariant-safe route to BEAT string-identity (a static offline KB, not inference-time knowledge).
4. **Board-instrument option:** report `common_noun_coref` on the common+name view of the cards (or record string-identity
   0.5412 as the acknowledged glass-box ceiling), so the dim measures clustering quality, not pronoun-pollution collateral.
5. **DO NOT REDO (measured-capped):** same-head splitting (net-negative on both dominant-eid AND CoNLL); different-head
   WordNet bridging (15-18% reach, 52-55% precision, pollutes -> net 0); different-head APPOS/COPULA in-text is-a bridge
   (5% reach, high precision, but nets -0.0007 after pollution -- even the best glass-box cue is exhausted); recall-safe vs
   hard agreement on common nouns (gender ~6%-sparse); Nref-gate / no-pollute de-pollution (antagonistic with pronoun);
   weighted parallel constraint satisfaction (0.5138 < string-identity, info-free twin ties -> no ranking headroom). All on
   disk with their capping reason. The different-head residual is 84.3% world-knowledge / abstract-anaphora (measured).
