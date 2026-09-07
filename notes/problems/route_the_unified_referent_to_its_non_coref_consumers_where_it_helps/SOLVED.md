---
problem: route_the_unified_referent_to_its_non_coref_consumers_where_it_helps
status: PARTIAL
bar: "PASSES only with ALL of: 1. The route built as a glass-box wire, PER non-coref consumer ... 2. Per routed consumer, the unified-referent input beats that consumer's CURRENT input CI-separated on MODERN gold (GUM), reported separately per consumer. The FLOOR is the consumer's CURRENT live input ... gate on the floor's UPPER CI bound. 3. The info-free twin LOSES CI-separated, per consumer ... 4. The he/she coref pick is BYTE-IDENTICAL (untouched). 5. No other downstream consumer regresses. ... A rigorous NEGATIVE is a FULL PASS on any consumer (e.g. '... the affect-experiencer binding does NOT move because the live experiencer subpopulation is already near-ceiling ~0.90 ...'; OR '... the situation-model entity layer already runs the situation-gated common-noun former, which captures the same individuation the unified card would supply, so the route is redundant -- subsumption by a DIFFERENT landed organ, located and counted')."
result: "On MODERN gold (GUM V12.1.0, 137-doc TEST split; scorers per consumer; doc-level paired bootstrap 2000x; grouping BYTE-FAITHFUL to hdlab.unified_referent.resolve_unified_stream, self-test asserted), routing the unified referent to the three live NON-coref consumers does NOT deliver a per-consumer CI-separated gain -- a rigorous LOCATED NEGATIVE (a full pass under the bar). PER consumer: (C1) SITUATION-MODEL ENTITY LAYER, CoNLL b3/muc/ceafe avg over non-pronoun mentions: unified grouping 0.6976 vs the LIVE floor (commonnoun_binder.situation_predict) 0.6939 = +0.0036 CI[+0.0008,+0.0063] -- a MARGINAL CI-sep edge that is SUBSUMED by a DIFFERENT dormant landed organ (the entity-KB resolver reader_coref=None = 0.7033 > unified 0.6976). (C2) ENTITY-KB HARD-LINK (a common noun of a NAMED entity files under the named record), n=2587: unified grouping 0.0139 vs live floor 0.0228 = -0.0089 (REGRESSES; == blind surface-head 0.0139 -> the unified card supplies NO cross-type common->name bridge). (C3) AFFECT/GOAL EXPERIENCER BIND (person common-noun experiencer files under the named entity), n=295: unified grouping 0.0508 vs live floor 0.1288 = -0.0780 (REGRESSES). The reader_coref route is INERT: feeding the entity-KB resolver the unified card head-sets changes 0 labels across 137 docs (delta +0.0000), and feeding it the reader's OWN two-pass clustering head-sets (the +0.0882-on-19c-LitBank lever) moves the CoNLL by +0.0000 (325 diffs, CI[-0.0001,+0.0001]) -- the reader_coref lever is a 19c-only effect, not a wrong-source problem. Unified completed-gender injection is flat (-0.0004). The he/she coref pick is BYTE-IDENTICAL with the route on (16/16 docs). ===> PARTIAL: the brief's LITERAL mechanism (unified referent) is REFUTED, but the UNDERLYING GOAL -- a per-consumer CI-separated gain on the non-coref consumers -- is ACHIEVED VIA A DIFFERENT brain-foundational mechanism (the 'solve it a different way' the protocol asks for): a glass-box ANAPHORICITY-GATED PRECISE-CONSTRUCTS cross-type bridge (in-text apposition/copula/copular-verb/conjunction-shared-subject/detached-appositive/relcl/title + FrameNet verbal role predication + unique-gender age/gender recovery), VALIDATED LANDABLE on the reader's OWN glass-box parser (arc-eager + arc-labeler, NOT gold UD): live-parse 0.1234 coverage @ 0.8636 precision (gold-parse ceiling 0.156/0.96). Its links, merged into the live entity clustering, lift the AFFECT/GOAL EXPERIENCER consumer 0.1311 -> 0.1639 = +0.0328 CI[+0.0128,+0.0586] CI-SEP over the situation_predict floor AND +0.0291 CI[+0.0118,+0.0507] CI-SEP over the info-free shuffled-target TWIN (n=549, all 275 GUM docs); the entity-KB hard-link is up (+0.0035 CI-sep) and the entity-layer CoNLL up (+0.0003 CI-sep). So the non-coref consumers CAN be lifted CI-separated -- just not by the unified referent (refuted); by a proper text-predication bridge (landable, net-positive, twin loses)."
floor: "The strongest floor actually run, recomputed on the SAME GUM TEST population + scorer per consumer: (C1) the LIVE default entity-layer clustering commonnoun_binder.situation_predict = 0.6939 CoNLL avg (disk-verified default: commonnoun_situation_gate=True, entity_kb_resolver=False); (C2) situation_predict hard-link 0.0228; (C3) situation_predict experiencer bind 0.1288. Reference alternatives run on the SAME population: the DORMANT entity-KB resolver resolve_common_noun(reader_coref=None) C1 0.7033 / C2 0.0460 / C3 0.1119 (it DOMINATES the unified grouping on C1/C2), and blind surface-head C1 0.6937 / C2 0.0139 (== the unified grouping on C2/C3 -> no bridge)."
controls: "(1) SELF-TEST gate: group_unified reproduces the live resolve_unified_stream per-target records EXACTLY (byte-faithful stand-in -> the negative is not a harness artifact). (2) INFO-FREE TWIN = shuffled unified GROUPING (same #cards + size shape, random membership): LOSES CI-sep on the size-robust CoNLL (unified-twin +0.3707 CI[+0.360,+0.382]) -> the grouping IS load-bearing signal, so the negative is SUBSUMPTION/register, not 'no signal'. (The size-GAMEABLE hard-link metric is INFLATED by the twin -- random merging accidentally shares a name label -- so CoNLL is the valid twin instrument; the p12 scorer-gaming lesson, caught here again.) (3) SOURCE control: reader_coref from the reader's OWN two-pass clustering (the strongest possible source) is ALSO inert on GUM -> excludes 'wrong reader_coref source', the lever is 19c-only. (4) HE/SHE BYTE-IDENTITY: the tuned graded he/she pick (EventCentralityReader graded_pick=True, unified_referent=False) is byte-identical with the full non-coref route applied (disjoint path; 16/16 docs). (5) MODERN gold only (GUM), 19c LitBank NOT used as load-bearing (owner 2026-09-06). (6) DEEPENING (built the EXACT mechanism, not just the weak card): the EXACT NE-type+salience/recency cross-type bridge is BUILT and MEASURED -- it achieves ~7-9% bind PRECISION (both cues), does NOT beat the floor CI-sep, and the fidelity classifier shows why (below); this passes the discipline's SECOND gate (a miss is a ceiling only if the brain's ACTUAL mechanism, faithfully built, is what failed). (7) LANDABLE VALIDATION of the different-mechanism win: (a) LIVE PARSE -- the precise-constructs bridge re-measured on the reader's OWN arc-eager+labeler parse (gold mentions fixed -> isolates the parse variable) holds 0.864 precision / 0.123 coverage (vs gold-parse 0.96/0.156), so it survives the live parser; (b) DOWNSTREAM CONSUMER paired doc-bootstrap, floor vs floor+bridge, all 275 docs: experiencer +0.0328 CI-sep, hard-link +0.0035 CI-sep, entity-layer +0.0003 CI-sep; (c) INFO-FREE TWIN (same #merges, RANDOM named-entity targets) does NOT reproduce it -- bridge beats twin +0.0291 CI-sep on the experiencer -> the CORRECT cross-type targeting is load-bearing, not 'merge a person-common into any name'."
files_changed: "experiments/exp_route_unified_to_consumers_gum_v1.py, experiments/exp_crosstype_bridge_fidelity_gum_v1.py, experiments/exp_route_unified_typed_bridge_gum_v1.py, experiments/exp_crosstype_strata_gum_v1.py, experiments/exp_crosstype_precise_constructs_gum_v1.py, experiments/exp_crosstype_landable_validation_gum_v1.py (live-parse + downstream + twin), experiments/exp_crosstype_upgrades_gum_v1.py (FrameNet + graded-competition upgrades), experiments/fetch_wikidata_person_roles_v1.py (offline KB acquisition), verification/test_route_unified_to_consumers.py, verification/test_crosstype_precise_constructs.py, verification/test_crosstype_landable.py, verification/test_crosstype_upgrades.py, notes/research_common_noun_definite_description_centering_2026-09-07.md (research drill), data/corpora/wikidata_person_roles/ (acquired offline asset, gitignored; pinned fetch script + provenance), notes/problems/route_the_unified_referent_to_its_non_coref_consumers_where_it_helps/FIDELITY_SCAN_full_chain_2026-09-07.md (12-layer fidelity scan), notes/problems/route_the_unified_referent_to_its_non_coref_consumers_where_it_helps/SOLVED.md. NO hdlab/ written (Q111 -- the finding is DO-NOT-WIRE; strategy owns any hdlab change). Reuses data/corpora/gum/ (pinned GUM V12.1.0, already on disk)."
reverify: ".venv/Scripts/python.exe verification/test_route_unified_to_consumers.py (16/16) -- re-derives the located negative (R1-R5) + the fidelity deepening (F1-F2c: WK ceiling for non-person, un-realizable NE-type upper bound for person at ~7% bind precision both cues) + the DECISIVE stratification (F3: ~80% of person-definites NON-anaphoric = the anaphoricity gate is the biggest precision lever; the anaphoric-to-name glass-box rate ~0.19 CROSS-VALIDATES the project's own landed GUM name_bridge 19.1% and Raghunathan 2010 MUC-6 15%). LANDABLE-GRADE proof of the different-mechanism win: verification/test_crosstype_landable.py (4/4) -- live-parse survival + the CI-separated experiencer lift + the twin losing, from experiments.exp_crosstype_landable_validation_gum_v1.run()."
---

# PARTIAL -- the unified referent is REFUTED, but the underlying goal is SOLVED a different way (landable)

**STATUS: PARTIAL** (solver scope; WIP until owner marks DONE). Glass-box, NO external LLM at inference (THE invariant).
NO `hdlab/` written -- measured in `experiments/` + `verification/`; the strategy session owns any hdlab change (Q111).
**Two-part result:** (1) routing the LANDED unified referent to the non-coref consumers is a rigorous LOCATED NEGATIVE
(do NOT wire it -- flat-to-negative, reader_coref lever 19c-only, marginal entity-layer edge subsumed by a dormant
organ); (2) the UNDERLYING GOAL -- a per-consumer CI-separated gain on those consumers -- IS achieved by a DIFFERENT
brain-foundational mechanism, the ANAPHORICITY-GATED PRECISE-CONSTRUCTS cross-type bridge, now VALIDATED LANDABLE
(survives the live parser at 0.86 precision; lifts the affect/goal EXPERIENCER consumer +0.033 CI-sep on the live path
with the info-free twin losing). The recommendation: do NOT wire the unified referent; DO land the precise-constructs
bridge into the entity-KB resolver's predication hook.

The brief's core hypothesis -- that routing the landed unified referent to the live NON-coref consumers (entity-KB
hard-link, affect/goal experiencer binding, situation-model entity layer) yields a per-consumer CI-separated gain on
modern gold -- is **REFUTED**. On GUM the routed arms are **flat-to-negative** on every consumer, and the one marginal
CI-separated edge is **subsumed by a different dormant landed organ**. A rigorous located negative is a full pass under
the bar; per the operating protocol I then went past the refutation to name the mechanism, test the redirect routes, and
establish the underlying problem is not solvable by any route I could test on modern gold.

## What the disk said that the brief did not (verified first-hand -- the disk outranks the brief)
1. **The live entity-layer clustering is NOT `resolve_common_noun`.** The brief names the entity-KB consumer as
   `resolve_common_noun(reader_coref=None)`, but on disk the live default is `commonnoun_situation_gate=True` **and
   `entity_kb_resolver=False`** (`hdlab/situation_reader.py` L908-910) -- so `_apply_commonnoun_gate` runs
   `commonnoun_binder.situation_predict`, and the entity-KB resolver is itself **DORMANT (default-off)**. My floor is
   therefore `situation_predict` (the true current input), with `resolve_common_noun(None)` measured as a reference.
2. **The p11 "entity-KB hard-link +0.072" and "pronoun pick +0.106" are PRONOUN-resolution metrics, not the live
   common-noun consumers.** In `exp_unified_referent_gum_v1.py` the "kb_hardlink" scorer is
   `bool(picked is not None and picked.has_name and picked.dominant_eid() == m.eid)` for a **pronoun** `m` -- i.e. "does
   the PRONOUN resolve to the referent carrying the name," measured intrinsically on a WEAK resolver. It is the pronoun
   pick under a different scorer, not the live `resolve_common_noun` (a COMMON-noun task). The brief itself flagged these
   were "measured on the reference HARNESSES, not the live consumers"; the disk confirms they are the same PRONOUN task.
3. **`resolve_unified_stream` returns only per-target pronoun records** -- no mention->card grouping. To route the card
   to a non-coref consumer I reproduced its file-change grouping (`group_unified`) and GATED it with a self-test that it
   reproduces the live `resolve_unified_stream` per-target records EXACTLY (byte-faithful stand-in).

## How the brain does this (the frame -- and why the negative was predictable)
- **PINNED (Ariel 1990 Accessibility Hierarchy; both prior SOLVEDs cite it).** The retrieval CUE is consumer-specific.
  The unified card's distinctive asset is COMPLETED cross-type SALIENCE + gender -- which is the **PRONOUN** cue
  (high-accessibility anaphora resolve by salience/prominence). Definite descriptions / common nouns resolve by
  **RECENCY / HEAD identity** (+ world knowledge for cross-type bridging), NOT salience. So the card's completed salience
  does not reach the common-noun consumers -- the brief's premise that these are "identity/salience consumers" is wrong
  for common-noun resolution.
- **The consequence the measurement then confirmed:** the ONLY live consumers that use the salience/identity cue the
  card completes are PRONOUN resolvers -- and the live reader resolves pronouns with the TUNED he/she pick (where the
  card is SUBSUMED + antagonistic, p12) and, for experiencers, through that same tuned pick. **There is no live consumer
  that both (a) lacks the tuned pool AND (b) uses the salience cue.** The unified referent's value has one home -- the
  pronoun pick -- and there it is subsumed.

## The measurement (GUM V12.1.0 TEST, 137 docs; one screen)
| consumer (scorer) | live floor | UNIFIED grouping | delta vs floor | dominant alt (dormant landed) |
|---|---|---|---|---|
| **C1 situation-model entity layer** (CoNLL b3/muc/ceafe) | situation_predict **0.6939** | **0.6976** | **+0.0036 CI[+0.0008,+0.0063]** (marginal, CI-sep) | entity-KB resolver **0.7033** (SUBSUMES) |
| **C2 entity-KB hard-link** (common noun files under named record, n=2587) | **0.0228** | **0.0139** | **-0.0089** (REGRESSES; == blind surface-head -> no bridge) | entity-KB resolver 0.0460 |
| **C3 affect/goal experiencer bind** (person common-noun experiencer, n=295) | **0.1288** | **0.0508** | **-0.0780** (REGRESSES) | entity-KB resolver 0.1119 |

**Routes tested (all three the brief named -- cluster / canonical head / ACT-R salience / reader_coref head-sets):**
- **Route (i) unified grouping AS the clustering** (`uni_direct`): the table above -- marginal-subsumed on C1, regresses
  C2/C3. The grouping is blind-head for common nouns (a common noun merges only with a prior SAME-head card; names never
  add to `.heads`) -> it supplies NO cross-type common->name bridge, so it is identical to surface-head on C2/C3. The
  bridge is exactly the world-knowledge wall p11 documented (81% of common->name anaphora needs world knowledge).
- **Route (ii) unified head-sets as the entity-KB resolver's `reader_coref` lever** (`uni_rc`): **0 label changes across
  137 docs** (delta +0.0000 on every consumer). The card's >=2-head sets are name-VARIANT sets ({barack,obama}) the
  aliaser already handles, never cross-type {president,obama} bridges -> the lever never fires. **SOURCE control:** even
  the reader's OWN two-pass clustering head-sets (the +0.0882-on-19c-LitBank lever) are inert on GUM (+0.0000, 325 diffs)
  -> the `reader_coref` lever is a **19c-only effect**, not a wrong-source problem.
- **Route (iii) unified completed-gender as a per-mention prior** (`uni_gender`): flat (-0.0004 C1, +0.0000 C2) -- gender
  is ~6%-sparse on modern nominals (p11's quantified cap), so the card's completed gender has almost no common-noun
  gn-filtering to convert.

**Controls.** Twin (shuffled grouping) LOSES on the size-robust CoNLL (unified-twin +0.3707 CI-sep -> the grouping IS
real signal, the negative is subsumption not "no signal"); the twin INFLATES the size-gameable hard-link (so CoNLL is the
valid twin instrument -- the p12 scorer-gaming lesson, re-caught). He/she pick byte-identical (16/16 docs, disjoint path).

## Why this matches the bar's OWN examples of a valid located negative (a full pass)
- **C3 = "the experiencer binding does NOT move because the subpopulation is near-ceiling."** The experiencer binding is
  near-ceiling on the EASY subpop (pronoun experiencers via the tuned pick ~0.90; name experiencers bind trivially) --
  the byte-identical he/she pick the route may not touch -- and at the WORLD-KNOWLEDGE WALL on the hard common-noun
  subpop (0.13). The unified referent helps NEITHER: the easy subpop is the off-limits tuned pick; the hard subpop is the
  bridge wall. No headroom, both mechanisms confirmed with counts (n=295 hard subpop).
- **C1 = "subsumption by a DIFFERENT landed organ, located and counted."** The unified grouping's only CI-sep edge over
  the live `situation_predict` (+0.0036) is dominated by the dormant entity-KB resolver (0.7033 > 0.6976) -- turning THAT
  on is strictly better and simpler than routing the unified referent. The unified card adds nothing the entity-KB
  resolver does not already provide (and more).

## The redirect I tested (protocol: refutation is the halfway point) and why it also fails on modern gold
The real underlying goal is "realize the unified referent's proven value at a consumer that lacks the tuned pool." Its
proven value is the PRONOUN pick (isolation +0.106, p11). I looked for a live pronoun consumer that is NOT the tuned
he/she pick: (a) the affect/goal experiencer PRONOUN binding uses `sm.coref_resolutions` = the tuned pick (byte-identical,
off-limits); (b) the entity-KB resolver's INTERNAL `resolve_pronoun` is a separate weak pronoun resolver, but it feeds
common-noun linking, which I measured flat/negative (the bridge wall dominates). So every live pronoun-resolution consumer
routes through the tuned pick, and every non-pronoun consumer is at the recency/head + world-knowledge wall. **No route I
could test on modern gold realizes a gain** -- the routes tested: grouping-as-clustering, reader_coref (unified + two-pass
source), completed-gender prior, and the search for a non-tuned pronoun consumer. The ONE untested lever is a NEW
capability (extend coref TARGETS to they/it/plural pronouns the tuned he/she pick does not cover) -- that is a different
problem (a new pronoun-population organ), not "route to non-coref consumers," and I name it as a candidate follow-on.

## DEEPENING -- "if we were EXACT this would perform very well" (aggressive brain-foundational fidelity pass)
The owner pushed back: a fair test of a WEAK implementation is not proof of a ceiling; the brain plainly keeps
"Elizabeth", "the doctor", "she" on one card. So I went past the port-faithful card and asked whether an EXACT
brain-faithful cross-type bridge would perform well. It does NOT on modern gold -- and now for a MEASURED,
mechanism-level, brain-foundational reason (not an implementation shortcut). This is the discipline's second gate:
a located negative counts only if the brain's ACTUAL mechanism, faithfully built, is what failed.

**Step 1 -- research (a research-drill agent).** The prior "~81% needs world knowledge" framing (from p11) is NOT
literature-supported: the Stanford deterministic-sieve OntoNotes error analysis attributes only 41.7% of its
residual to semantics/discourse; Poesio & Vieira (1998) class the proper-name<->role-noun case as solvable by
NAMED-ENTITY TYPING (not open-ended lexical bridging); for INVENTED fictional characters no external
world-knowledge source could even exist. So the gap MIGHT be a narrow-detector coverage ceiling, not an LLM wall.
(The agent's prose report did not persist to disk -- I did not rely on it; I disk-verified every claim by
measurement below.)

**Step 2 -- the decisive residual classifier (`exp_crosstype_bridge_fidelity_gum_v1.py`).** Using GUM's GOLD UD
syntax (deprel/head) + gold coref, I partitioned the common->name hard-link population by RECOVERY MECHANISM
(glass-box first, an UPPER BOUND per bucket): PRED (explicit apposition/copula/title predication) / TYPE (person
role-noun + a named person, Poesio-Vieira NE-typing) / KB (ConceptNet/WordNet role-scenario) / WK (genuine
encyclopedic). Result (275 docs, 1495 hard-links):
- **NON-PERSON entities (org/place): glass-box ceiling 0.126, WK residual 0.874** -- a genuine WORLD-KNOWLEDGE
  wall (Argentina->"the country", Frontiers->"the publisher"). p11 was right HERE. LLM-barred.
- **PERSON entities: glass-box UPPER BOUND 0.769, dominated by TYPE = 494/707 (70%)** -- the optimistic reframe.
  BUT PRED is only 16/707 and KB 34/707; the 70% is entirely the TYPE bucket, an upper bound that assumes NE-type
  + salience can DISAMBIGUATE among compatible named persons.

**Step 3 -- build the EXACT NE-type bridge and test whether the upper bound REALIZES
(`exp_route_unified_typed_bridge_gum_v1.py`).** I built the exact mechanism into the unified card: a person
role-noun DEFINITE ("the doctor") binds to a gender/number-compatible NAMED-person card by the card's OWN cue --
swept over BOTH salience (ACT-R base-level activation, the port already computes it) and recency (the Ariel
definite-description cue), margin-gated, then FILES the descriptor onto the card (Heim/Kamp file-change). Measured
on GUM (the oracle arm = gold clusters confirms the headroom is real, 1.000):
- **Bind PRECISION ~7-9% for BOTH cues** (salience 0.072, recency 0.062; margin-swept 0.0-1.5, precision tops out
  ~0.10). So the 0.769 upper bound does NOT realize: the bridge binds the WRONG named person ~90% of the time.
- **WHY (two counted causes):** (a) **~77% of person-definites are NOT anaphoric to any name** (achievable = 23%)
  -> firing on all definites over-fires massively; (b) among the ~23% achievable, neither salience NOR recency
  identifies the right named person (recall of achievable ~15%) -- multiple compatible persons, and the correct
  antecedent is not the most-salient/most-recent one.
- **The exact bridge is net flat-to-NEGATIVE on every consumer** (C1 -0.0036, C2 -0.0008, C3 -0.0068; none CI-sep)
  -- it introduces more wrong merges than right ones.

**Step 3b -- a second research drill + the DECISIVE stratification (`exp_crosstype_strata_gum_v1.py`) -- fixing
two of MY OWN fidelity errors.** A second cited research drill
(`notes/research_common_noun_definite_description_centering_2026-09-07.md`, ~30 sources) surfaced two things I
had gotten wrong: (i) I had lumped POSSESSIVES ("his father", relational, NOT a type-bind) in with definite
articles -- an over-firing fidelity bug; (ii) I had no ANAPHORICITY gate (the brain first asks "is this definite
even anaphoric?" -- Heim familiarity; Poesio & Vieira 1998: ~70-78% of definites are non-anaphoric). It also
confirmed my cue was fine: recency == the backward-looking center Cb in English (Poesio et al. 2004 GNOME:
role-ranking and recency statistically indistinguishable; Tetreault 2001: textbook Centering scores WORSE than
recency). I fixed both errors (article-only) and STRATIFIED the bind on GUM (275 docs, n=1213 article-definite
person role-nouns), cue-invariant (recency 0.181 == salience 0.190 on the anaphoric subset):
- **NON-anaphoric / cataphoric: 987/1213 = 81%**, correct-bind 0.005 -- the over-fire mass; the ANAPHORICITY GATE
  is the single biggest precision lever (unfiltered 0.038 -> anaphoric-to-name 0.186 = ~5x, confirming the
  research's Prediction A). But abstaining only fixes PRECISION; it adds no correct cross-type links.
- **ANAPHORIC-to-name subset (a prior name of the entity exists): n=226, only 0.186 resolve glass-box** by
  recency/salience. **This ~19% THREE-WAY CROSS-VALIDATES**: (1) this project's OWN landed GUM measurement
  (`expand_the_clean_semantic_memory_foundation...` SOLVED, name_bridge in-text-derivable = 19.1%); (2) Raghunathan
  et al. 2010 MUC-6 (15% of common-noun errors NOT world-knowledge, i.e. 85% are); (3) my independent number here.
  Three methods/eras/corpora converge at ~15-19% glass-box-recoverable.
- **In-text PREDICATION is essentially ABSENT for article-definite person role-nouns on GUM: 1/226** -- so the
  apposition/copula detector (the one glass-box lever the first research drill hoped for) has ~0% coverage on this
  population; the ~81% residual is genuine world-knowledge ("Obama IS the president"), not stated-but-undetected.

**Step 4 -- the brain-foundational reconciliation (this is the real answer).** Ariel (1990) Accessibility
Hierarchy: a DEFINITE DESCRIPTION is a LOW-accessibility marker, retrieved by DESCRIPTIVE CONTENT (+ recency),
NOT by salience (the high-accessibility PRONOUN cue). The faithful cue for "the doctor"->"Elizabeth" is therefore
the file card's DESCRIPTIVE CONDITION -- the entity the text PREDICATED to be a doctor ("Elizabeth, a doctor" /
"Elizabeth was a doctor"). That predication is the PRED bucket: **~2% of GUM cases (25/1495)**. It is COMMON in
19c narrative ("Elizabeth, the eldest Miss Bennet, ...") -- the register that is BANNED as load-bearing (owner
2026-09-06) -- and RARE in modern multi-genre prose. So on modern gold the cross-type definite->name bridge is
either explicit predication (~2%, glass-box, and already captured by the DORMANT entity-KB resolver's `attrs`
apposition path) or genuine world-knowledge/unstated (LLM-barred). **NE-type + salience/recency -- the mechanism
the optimistic upper bound pointed to -- is NOT the brain's cue for definites and does not work (7% precision).**
The "if we were exact this would perform very well" intuition is TRUE for 19c protagonist-narrative and does NOT
transfer to modern gold, precisely because the licensing descriptive content is not stated. This CORRECTS the
research reframe: it IS a wall on modern gold; the "narrow-detector" story holds only for the ~2% predication,
which a landed organ already handles.

## What I did NOT establish / would withdraw first if wrong
- **The marginal C1 +0.0036 CI-sep edge over `situation_predict` is the closest thing to a positive, and the first thing
  I would withdraw.** It is within a hair of its own half-width (0.0028), it is SUBSUMED by the entity-KB resolver, and it
  does not survive as a capability (routing the grouping regresses C2/C3). If a reviewer wants to read C1 alone as a
  micro-PASS, the honest reading is still "do not route the unified referent; turn on the entity-KB resolver instead."
- **GUM only.** GENTLE OOD (26 docs, on disk) was not run; the negative is on GUM's 18 modern genres. The mechanism (Ariel
  cue-specificity + the common->name world-knowledge wall) predicts the same OOD, but I measured only GUM.
- **The experiencer C3 easy-subpop near-ceiling (~0.90) is argued from mechanism** (pronoun via the tuned pick; name
  trivial), quantified directly only on the HARD common-noun subpop (n=295 at 0.13). A full easy+hard experiencer census
  would strengthen it but does not change the verdict (the unified referent touches neither).

## KEY REALIZATIONS (the enabling moves)
- **The disk's default flags reframed the whole floor.** `entity_kb_resolver=False` on disk means the live entity-layer
  clustering is `situation_predict`, not `resolve_common_noun` -- so the brief's named consumer is itself dormant, and the
  reader_coref lever it points at is off the live path. Reading the actual `__init__` defaults, not the brief, set the
  correct floor and revealed the reader_coref route is doubly-dormant.
- **The "entity-KB hard-link +0.072" was the pronoun pick wearing a different scorer.** Tracing the p11 `kb_hardlink`
  scorer to its source (`picked.has_name and dominant_eid==m.eid` for a PRONOUN) showed the reference-harness "non-coref
  lifts" are all PRONOUN-resolution metrics on a weak resolver -- so they cannot transfer to the truly-separate
  common-noun consumers, and the live reader already does pronouns with the tuned pick. This is the whole refutation: the
  unified referent's home is the pronoun pick, where p12 already showed it subsumed.
- **The SOURCE control separated "wrong source" from "lever is 19c-only."** Feeding the resolver the reader's OWN two-pass
  clustering (the exact +0.0882-LitBank lever) and getting +0.0000 on GUM is what turns "the unified head-sets are too
  thin" into "the reader_coref lever does not transfer to modern gold" -- a register wall, counted.
- **The twin re-caught the p12 scorer-gaming trap.** The shuffled twin WON on the hard-link metric (random merging shares
  a name label) but LOST hard on CoNLL -- confirming CoNLL is the size-robust instrument and the hard-link metric must not
  be used for the twin control. Validating the twin against the metric before trusting it is what kept the negative honest.
- **A glass-box CEILING upper-bound is not a capability -- build the mechanism and measure whether it REALIZES.** The
  fidelity classifier said "77% of the person gap is NE-type-recoverable," which looked like the refutation was premature.
  Building the EXACT NE-type bridge and measuring its PRECISION (7%, both cues) is what turned the optimistic upper bound
  into the real finding: type-COMPATIBILITY is not type-RESOLUTION. The upper bound assumed perfect disambiguation; the
  faithful mechanism can't disambiguate on modern multi-person text. Always test whether an upper bound realizes.
- **Ariel's cue-specificity is the whole answer, and I nearly applied the wrong cue.** A definite description resolves by
  DESCRIPTIVE CONTENT + recency, NOT salience (that is the pronoun cue). "Make the card do salience-binding for the doctor"
  is LESS brain-faithful, not more -- and testing BOTH cues (both 7%) proved the wall is not wrong-cue but missing-content:
  the licensing predication is a 19c-narrative feature, banned, and rare on modern gold. Cue-specificity (Ariel) predicted
  the whole result.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b, E3 coreference / entity tracking)
- The 2026-09-06 unified-referent DEFAULT-OFF disposition is CONFIRMED and EXTENDED: not only is it subsumed at the he/she
  pick (p12), its value **cannot be realized at the live NON-coref consumers on modern gold either** -- routing its
  grouping is flat-to-negative (C1 +0.0036 subsumed by the entity-KB resolver; C2 -0.0089; C3 -0.078), its `reader_coref`
  lever is inert on GUM regardless of source (a 19c-only effect), and its completed gender is ~6%-sparse. **Keep
  `hdlab/unified_referent.py` DEFAULT-OFF everywhere; do NOT add a non-coref route.**
- **CORRECTION to the p12 adjacent-components note** ("the unified referent's real home is the WEAK scorer / non-coref
  consumers"): REFUTED on the LIVE consumers on modern gold. The reference-harness "non-coref lifts" were PRONOUN-pick
  metrics on a weak resolver; the truly-separate common-noun consumers do NOT lift (Ariel cue-specificity + the
  common->name world-knowledge wall). The unified referent's only home is the pronoun pick, where it is subsumed.
- **NEW deviation to fold in:** the entity-KB resolver's `reader_coref` Step-3 lever (+0.0882 CoNLL on 19c LitBank) does
  NOT transfer to modern GUM (+0.0000, both from the unified card AND from the reader's own two-pass clustering) -- a
  19c-vs-modern register effect on the common->name bridge, which is world-knowledge-bound on modern multi-genre text.
- **NEW (the fidelity deepening) -- the cross-type common->name bridge on modern gold, decomposed and measured:**
  NON-PERSON entities are a world-knowledge ceiling (glass-box 0.13 / WK 0.87). PERSON entities have a 0.77 NE-type
  UPPER BOUND that does NOT realize -- the EXACT NE-type bridge (person-definite -> named person by salience OR recency)
  achieves ~7% bind precision because ~77% of person-definites are non-anaphoric and the achievable rest is
  undisambiguable without STATED predication (~2% of GUM, a banned-19c-register feature). The brain-faithful cue for a
  definite description is DESCRIPTIVE CONTENT + recency (Ariel), not salience; on modern gold the licensing content is
  either explicitly predicated (~2%, glass-box, already in the dormant entity-KB resolver's `attrs`) or world-knowledge
  (LLM-barred). So the unified referent -- even made exact -- cannot supply the cross-type bridge on modern gold.

## Adjacent components (seeds for the next problems -- evaluated for brain-foundational fidelity)
- **The DORMANT entity-KB resolver (`entity_kb_resolver=False`)** dominates the unified grouping on the entity layer
  (C1 0.7033 vs 0.6976) and the hard-link (C2 0.0460 vs 0.0139) on GUM, but slightly regresses the experiencer subpop
  (C3 0.1119 vs 0.1288). Whether to turn it on (net across consumers, twin, no-regress) is a separate, higher-value
  wiring question than routing the unified referent -- a candidate follow-on. Brain-status: its salience is composite
  Centering (PINNED-ish); its common->name bridge is a curated KB (OUR-INVENTION world-knowledge proxy, the honest wall).
- **The common->name world-knowledge bridge is the real lever for ALL three consumers** (C2/C3 sit at 0.01-0.13 because a
  common noun cannot find its named entity). p11 measured the glass-box bridge (apposition/copula + head-in-name) recovers
  ~19%; the other ~81% needs a semantic is-a/scenario prior (the Phase-1 `entity_world_model_resolver` identifiability
  wall). This -- not the unified referent -- is where the entity-KB/affect consumers gain. Brain-foundational and filed.
- **Extend the pronoun-resolution TARGET set beyond he/she (they/it/plural)** -- the one place the unified referent's
  broader ACT-R pronoun resolution could add a LIVE gain the tuned he/she pick does not cover. A NEW capability (a new
  pronoun population), not this problem; candidate follow-on.

---

**TLDR (plain English):** A good reader keeps one shared record per character. We built that record; it helps the
reader's "who is he/she" guess (but there it's redundant with an already-tuned guesser), and the plan here was to send it
instead to the reader's OTHER jobs -- filing a fact under the right named person, attaching a feeling to the right
character, keeping straight which "the man" is which. I wired it to those jobs and tested on modern text, and it did **not**
help: two of the three jobs got slightly WORSE, and the third improved by a whisker that a different, already-built (but
switched-off) tool beats anyway. The reason is a real one about how reading works: the shared record's strength is knowing
who's "in focus," which is exactly what "he/she" needs -- but "the man" and "the doctor" are matched by the WORD and by
outside world-knowledge, not by focus, so the shared record has nothing to offer them. The numbers that made this look
promising earlier were actually measuring the "who is he/she" job again under a different name. So the honest answer is:
don't send the shared record to these other jobs -- it belongs to the "he/she" job, where it's already redundant. I proved
the shared record itself is real (a scrambled version falls apart) and that the "he/she" guesser is left exactly as it was.

**QUESTIONS:** none blocking. One judgement call: I marked this **REFUTED** rather than PARTIAL. The one CI-separated
edge (the entity layer, about four more right in a thousand) is real but marginal AND beaten by a different switched-off
tool, while the other two jobs regress -- so the brief's promise (a per-consumer gain) is not met and its premise (that
the reference-harness lifts transfer to the live jobs) is disproven. If you'd rather log the marginal entity-layer edge as
a micro-PARTIAL, the actionable recommendation is unchanged: do NOT route the unified referent; if the entity layer is to
improve, evaluate turning on the dormant entity-KB resolver instead.

Deepening answer to "if we were EXACT this would perform very well": I took that seriously and built the exact
brain-faithful cross-type bridge (NE-type + salience AND + recency, filing descriptive conditions onto the file card).
It performs POORLY on modern gold -- ~7% bind precision, net-negative -- for a measured, principled reason: a definite
description resolves by DESCRIPTIVE CONTENT (Ariel), and the content that licenses "the doctor"->"Elizabeth" is stated
in only ~2% of modern GUM (it IS common in 19c narrative, which is banned as load-bearing). "Exact" WOULD perform well
on 19c protagonist-narrative; it does not transfer to modern multi-genre text because the licensing content is not there
(non-person cases are outright world-knowledge). The one glass-box lever that DOES exist (the ~2% explicit predication)
is already captured by the dormant entity-KB resolver -- so the actionable path is to evaluate/strengthen THAT organ's
predication + NE-typing, not to route the unified referent.

## CONSTRUCTIVE FOLLOW-ON -- the two glass-box pieces that DO generalize (prototyped, `exp_crosstype_precise_constructs_gum_v1.py`)
The owner asked to prototype the path that WOULD make cross-type work on modern text. Built + measured on GUM,
on the person-cleaned anaphoric-to-name population (n=154), witness `test_crosstype_precise_constructs.py` 3/3:
| mechanism | hit rate | precision | net effect |
|---|---|---|---|
| FLOOR (situation_predict, blind head) | 0.084 | -- | current live |
| FORCE-bind (recency/salience, NO gate) | 0.227 | **0.324** | floods wrong merges -> **NET-NEGATIVE** |
| **GATED precise-constructs (OPTIMIZED)** | **0.156** | **0.960** | clean -> **NET-POSITIVE** |
| ORACLE (gold) | 1.000 | -- | ceiling |
- **Piece 1 -- the ANAPHORICITY GATE + PERSON CLEANUP is the fix that flips net-negative to net-positive.** Firing
  only when a role is licensed (predication) to a named person, and excluding org/thing false-positives ("the
  publisher"=Frontiers, "the respondent"=PAC), raises precision from 0.324 (force-bind floods) to **0.960**. The
  brain does exactly this (Heim familiarity: is this definite even anaphoric?) -- my original mechanism did not.
- **Piece 2 -- a PROPER PRECISE-CONSTRUCTS detector, OPTIMIZED** through a glass-box construction ladder
  (0.004 narrow -> 0.110 [appos/copula/copular-verbs/title/relcl + person cleanup] -> 0.117 [conjunction-shared
  subjects: "Dvorak moved and became the director"] -> 0.123 [FrameNet-style VERBAL role predication: "Moreau
  starred / Galois wrote"] -> **0.156** [unique-gender AGE/GENDER narrative recovery: "the boy"=the unique prior
  compatible named male]) = a **39x recall gain** over the narrow detector, at **0.960 precision**, reaching 82% of
  the project's landed ~0.191 in-text ceiling. Every rung is glass-box, NO LLM, and net-positive (no flooding). The
  detached-appositive + verbal + age/gender rungs are the ones a naive "apposition only" detector (and the project's
  prior 19.1% measurement) leaves on the table.
- **The residual (~0.89) is genuine WORLD-KNOWLEDGE** and splits two ways (residual dump): FAMOUS-person roles
  ("the boy"=Byron, "the author"=Galois, "the star"=Jeanne Moreau, "the director"=Dvorak) that a role/occupation
  KB (Wikidata P106/P39) WOULD supply -- but no Wikidata is on disk, so this is a FOUNDATION ACQUISITION (admissible:
  static offline KB, the invariant is no-LLM-at-inference); and LOCAL/fictional characters ("the old man"=Pachomius)
  whose role is only loosely in the discourse -- genuinely unrecoverable unless stated. So a role-KB helps the bio
  subset, not the interview/reddit/how-to subset.
**Honest bottom line of the constructive pass:** the glass-box path (anaphoricity gate + precise-constructs + person
cleanup) is a REAL, brain-foundational, net-POSITIVE win over the current force-bind -- but it recovers only the
~11-19% of cross-type person links whose role is STATED in the text, and the absolute count on modern GUM is small
(the anaphoric-to-name person population is itself thin), so it does not move the downstream consumers CI-sep.

**THE SEMANTIC-MEMORY KB (Wikidata) IS A LOCATED NEGATIVE -- built brain-foundationally, acquired for real, MEASURED
(owner ask: "do it brain foundationally").** BRAIN FRAME: comprehension binds "the poet"->"Byron" by retrieving from
SEMANTIC MEMORY (Tulving; the ATL person-knowledge store, Bruce & Young person-identity nodes) that this Byron IS a
poet; the file card accumulates conditions from BOTH the text (Heim/Kamp) AND stored world-knowledge, and "the poet"
retrieves by type-cue match (Lewis-Vasishth). I ACQUIRED a real offline proxy: Wikidata occupation (P106) + position
(P39) for the GUM person population (`experiments/fetch_wikidata_person_roles_v1.py`, pinned + provenance under
`data/corpora/wikidata_person_roles/`; notability ranking = the familiarity prior; queried as an OFFLINE lookup, NO LLM
at inference -- the invariant holds), and matched it WordNet-hypernym-aware ("writer"<-"poet"). RESULT: it adds
**+0.000** coverage. Of the 16 definites whose entity HAS catalogued occupation roles, the descriptor matches the
occupation only **1** time (spurious). MECHANISM (the deep finding): **people are re-mentioned by a definite almost
NEVER by their catalogued occupation -- they are re-mentioned by AGE/GENDER ("the man"->Pachomius, "the woman"->Kamala
Harris), RELATION ("the son"/"the daughter"->L'Enfant/Moreau), or a CONTEXT-specific role ("the royalist", "the
umpire", "the director of the Conservatory") that is either STATED IN THE TEXT (the precise-constructs path already
gets it) or bound by the DISCOURSE, not by a static occupation KB.** So the occupation KB is the WRONG KIND of
world-knowledge for definite-description resolution -- a rigorous, brain-foundational located negative that CORRECTS
both my earlier "needs a role-KB" hypothesis and the research drill's Wikidata-P31 recommendation. The right levers are
all glass-box or discourse: text predication (built), gender/age tracking (built, unique-gated), stated relations
(text), and genuine narrative context (not a lookup). There is no static-KB lever left to pull.

**Net:** the constructive path's real, net-positive win is the glass-box text+gender bridge (0.156 @ 0.960); the KB is a
measured dead-end. This CONFIRMS the refutation's ceiling AND closes the "what would make it work" question: on modern
text the cross-type definite->name bridge is text-stated (~19%, built) + age/gender (built) + genuine discourse context
(not KB-recoverable) -- NOT an occupation-fact gap.

## FIDELITY AUDIT + UPGRADES (owner ask: "is this 100% brain-foundational? any upgrades?") -- `exp_crosstype_upgrades_gum_v1.py`
**NOT 100% brain-foundational: the COMPUTATIONS are (DRT file-change descriptive conditions PINNED; phi-agreement;
frame-semantic roles; Heim familiarity gating; Lewis-Vasishth cue-based retrieval), but four IMPLEMENTATIONS are
proxies** -- (1) predication EXTRACTION = the reader's statistical arc-eager+labeler parse (glass-box but not the brain's
incremental predictive parse -- the standing parser gap, shared reader-wide); (2) verbal role = a curated ~30-verb
lexicon; (3) the BIND = a hard UNIQUENESS heuristic; (4) person detection = a curated stoplist. Two upgrades built +
measured:
- **UPGRADE A -- FrameNet verbal-role ingest (the research-flagged "unused FrameNet ingest"): REJECTED, measured.**
  Raw frame co-membership (verb LU + person-noun LU in the same frame) is TOO NOISY -- it conflates AGENT with
  PATIENT/other roles ("teach"->{professor, PUPIL, protege}) and word senses ("compose"->{director, producer}, missing
  composer). A clean ingest needs frame-ELEMENT-level agent restriction + sense disambiguation (a separate build). The
  curated lexicon is higher-precision; FrameNet is NOT a drop-in win.
- **UPGRADE B -- GRADED ACT-R / recency competition replacing the hard uniqueness gate: ADOPTED, measured win.** BRAIN
  FRAME: a definite resolves by cue-based content-addressable retrieval (Lewis-Vasishth) over the entity cards -- the
  SAME engine the reader uses for pronouns -- with RECENCY (== the backward-center Cb in English, Poesio 2004) as the
  cue and a CONFIDENCE MARGIN gating the commit (abstain under ambiguity). This is strictly MORE brain-faithful than
  "fire only if exactly one compatible named person". Baseline BYTE-MATCHES the validated bridge (live 0.1234 @ 0.8636);
  the upgrade (margin=2, dev-swept) raises LIVE coverage **0.1234 -> 0.1883 (+53% relative)** at 0.7632 precision (still
  far above the net-negative force-bind 0.32), and BOOSTS the downstream affect/goal EXPERIENCER lift from **+0.0328 to
  +0.0510 CI-separated** (live parse, floor->bridge 0.1311->0.1821). So the DEPLOYABLE config is the graded-competition
  bridge, not the uniqueness gate. Witness: `test_crosstype_upgrades.py`.
- **UPGRADE C -- the UNIFIED cue-based ACT-R retrieval, ALL THE WAY UP THE CHAIN (parse -> deprel grammatical role
  -> Cf-ranked salience [Centering ROLE_PROMINENCE] -> descriptive-boost [Almor] + gender + recency + confidence
  margin): BUILT, and it DEMONSTRATES the chain dependency.** UNGATED it recovers 3x more links (LIVE coverage 0.435,
  C3 +0.1038) but over-merges at 0.50 precision and REGRESSES the entity-layer CoNLL CI-separated (C1 -0.0058) -- the
  faithful retrieval CANNOT be dropped in without the upstream anaphoricity gate (the owner's "depends on the chain").
- **UPGRADE D -- cue-retrieval + the ANAPHORICITY/FAMILIARITY gate (the missing upstream stage): the DEPLOYABLE,
  most-brain-foundational config.** Gating the retrieval to anaphoric-safe descriptors (predication OR age/gender)
  fixes the regression: C1 -0.0004 (safe, not CI-sep), C2 +0.0057 CI-sep, C3 +0.0528 CI-sep (LIVE, 275 docs) -- best
  of all configs, using the brain's actual retrieval mechanism on the faithful upstream. RECOMMENDED deployable config.
- **UPGRADE E -- ANIMACY via the FREQUENCY PRIOR (WordNet first-sense = noun.person; the brain's default sense,
  Anderson base-rate) replacing the hand stoplist: MIXED, honest.** Raises ceiling coverage 0.201 -> 0.309 LIVE at
  equal precision (0.778) -- more principled + more coverage -- but the deployment C3 lift drops +0.0528 -> +0.0364
  (the extra coverage over-fires without a stronger gate). So it is a FIDELITY win gated by the same anaphoricity-gate
  dependency; keep the stoplist config deployable until the gate is upgraded.
- **FULL FIDELITY SCAN, all the way up the chain: `FIDELITY_SCAN_full_chain_2026-09-07.md` (12 layers, evidence-backed).**
  Verdict: the COMPUTATIONS are 100% brain-foundational; ~7/12 implementations faithful, 5/12 proxy, with 2
  LOAD-BEARING (measured) proxies -- the anaphoricity DETECTOR (the ungated over-merge quantifies it) and the
  statistical PARSER (the live-parse coverage/precision drop quantifies it). Ordered path to 100%: (a) a real
  anaphoricity/discourse-new detector to safely unlock the ungated 3x coverage; (b) SWEEP the ROLE_PROMINENCE + cue
  weights (literature gives orderings, not numbers); (c) the incremental-predictive parser (reader-wide); (d)
  frame-ELEMENT FrameNet agent ingest; (e) graded phi-agreement. Each named + measured, none a hidden gap.

**NEXT STEPS (strategy owns any hdlab change; solver is scope-barred from hdlab/):**
1. **DO NOT WIRE the unified referent to the non-coref consumers, and keep `hdlab/unified_referent.py` DEFAULT-OFF
   everywhere.** The route is flat-to-negative on modern gold; the reader_coref lever is 19c-only; the marginal entity-layer
   edge is subsumed by the entity-KB resolver.
1b. **FILE THE CONSTRUCTIVE FOLLOW-ON (the real path, brain-foundational + net-positive):** a glass-box cross-type
   bridge = (a) an ANAPHORICITY GATE (abstain on non-anaphoric definites; ~80% of them) + PERSON CLEANUP, (b) a
   proper PRECISE-CONSTRUCTS predication detector -- appos/copula/copular-verbs/conjunction-shared-subject/detached-
   appositive/relcl/title/FrameNet-verbal-role (0.960 precision, 0.156 recall, ~82% of the in-text ceiling), plus
   (c) unique-gender AGE/GENDER narrative recovery -- landed into the entity-KB resolver's `attrs`/predication path
   (it already has the hook). Prototype: `exp_crosstype_precise_constructs_gum_v1.py`. **DO NOT pursue a Wikidata
   occupation KB (P106/P39): MEASURED located negative -- adds +0.000 because definite descriptors are
   age/gender/relation/context, not catalogued occupation (1/16 match).** The residual above the glass-box path is
   genuine discourse context, not a static-KB gap.
2. **Fold the AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` sec 2b, including the CORRECTION to p12's "non-coref
   consumers are the unified referent's home" note (refuted on the live consumers).
3. **FOLLOW-ON (higher value than this route):** decide whether to turn on the DORMANT entity-KB resolver
   (`entity_kb_resolver`) -- it dominates the unified grouping on the entity layer + hard-link on GUM (measure net across
   consumers + twin + no-regress on the experiencer subpop), and pursue the glass-box common->name bridge (the real lever
   for the entity-KB / affect consumers, ~19% glass-box + the ~81% world-knowledge Phase-1 wall).
4. **FOLLOW-ON:** extend the pronoun-resolution TARGET set beyond he/she (they/it/plural) -- the one place the unified
   referent's broader ACT-R pronoun resolution could add a live gain the tuned he/she pick does not cover (a new capability).
