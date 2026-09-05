# Where exactly is the common-noun coref signal lost, and how the brain does it -- the drill

Owner (2026-09-04): "research and drill that result aggressively. Where are we losing signal, and how
does the brain do it exactly? Where do we differ from the 100% brain-foundational approach, precisely?"

Instrument: `experiments/exp_commonnoun_linktype_decomposition_v1.py` (100 LitBank docs). For every GOLD
PERSON common-noun coreference link (a common-noun non-pronoun mention m with a nearest prior same-cluster
non-pronoun antecedent), categorize by the KNOWLEDGE the link requires, and measure whether pure
ACCESSIBILITY (most-recent gender/number-compatible person referent) recovers it and how many COMPETING
compatible person referents intervene (the ambiguity = the situation-model dependency).

## The decomposition (1,936 person common-noun links)

| category | n | frac | accessibility recovers | mean competing referents when missed |
|---|---|---|---|---|
| head_identical ("the man" ... "the man") | 555 | 0.287 | 0.222 | 3.03 |
| name_antecedent ("Elizabeth" ... "the girl") | 363 | 0.188 | 0.215 | 2.63 |
| wordnet_bridge ("the fellow" -> "the man") | 152 | 0.078 | 0.230 | 2.21 |
| kinship_role ("her father", "the servant") | 423 | 0.219 | 0.135 | 2.86 |
| residual (deep world knowledge) | 443 | 0.229 | 0.126 | 3.02 |

## The two precise findings

**1. Static lexical assets can tag almost none of the gap.** The non-head-match links are 71.3% of the
total. A buildable STATIC lexical-taxonomy asset (WordNet person hypernymy, best-sense, generous oracle)
tags only **7.8%** of links (wordnet_bridge). The dominant non-head-match slices -- name_antecedent
(18.8%), kinship_role (21.9%), residual (22.9%) = **63.5%** -- are NOT lexical-taxonomy problems. "Her
father" is not a WordNet neighbour of the man's name; "the Squire" is not a synonym of anything; the girl
called "Elizabeth" three sentences ago shares no word with "the girl." So the +0.43 headroom is NOT behind
a missing lexicon -- adding WordNet moves ~8% of links at best (and my CoNLL measure already showed the
bridge arm is a wash, because tagging 8% while over-merging elsewhere nets zero).

**2. The loss is a SITUATION-MODEL dependency, quantified.** Pure accessibility (bind the description to
the most-recent gender/number-compatible active person) recovers only 0.13-0.23 of links in EVERY
category, because on average **2.2-3.0 OTHER compatible person referents are more recent than the true
antecedent.** Summed across categories, only **349 / 1,936 = 18% of person common-noun links occur with a
SINGLE unambiguous compatible active referent**; the other **82% occur in multi-person contexts** where 2-3
same-gender persons are simultaneously active and NO recency/lexical/gender cue picks the right one. This
is exactly the content-identical over-merge from the diagnostic (91%), now localized: it is not a tagging
failure, it is that the correct referent is determined by WHICH entity the current scene is ABOUT.

## How the brain does it EXACTLY, and where we differ (the precise mechanism-diff)

- The brain maintains an ONLINE SITUATION MODEL (Zwaan-Radvansky event-indexing; Sanford-Garrod
  scenario-mapping; Kintsch construction-integration): a representation of WHICH entities are PRESENT and
  FOREGROUNDED in the current scene, continuously updated by the EVENT structure (who did what to whom).
  A definite description ("the man", "her father", "the girl") is resolved by binding it to the
  currently-foregrounded entity of that description-TYPE -- a content-addressable retrieval whose dominant
  CUE is scenario/situation membership, gated by role-relational and lexical-type compatibility. The
  reference is fixed by the SCENE, not by the words or their recency.
- WE HAVE: the retrieval OP (ACT-R activation, `graded_coref_pick`, PINNED) and lexical typing (WordNet,
  gender). WE LACK: the online situation model of who-is-active, so when 2-3 compatible persons are
  foregrounded (82% of links) we retrieve by recency/frequency/role and pick wrong as often as right --
  the measured wash. The `event_centrality_coref` organ is the closest existing piece (event-bundle memory
  that disambiguates same-gender pronoun ties) but it is (a) wired for pronouns only and (b) still cannot
  supply the role-relational knowledge ("whose father?") the kinship slice needs.
- THE PRECISE DIVERGENCE FROM 100% BRAIN-FOUNDATIONAL: not a missing static lexicon and not a weaker
  retrieval formula -- it is the absence of the ONLINE SITUATION MODEL (scene-foregrounding + event
  structure + role-relational binding) that supplies the DOMINANT retrieval cue for definite descriptions.
  That is the Phase-1 meaning-channel / world-model boundary the affect and WSD located negatives also hit.
  It is a fidelity gap to BUILD across (a situation-model-gated referent binder over the event structure),
  NOT a ceiling -- but it is a substantial capability, not a coref heuristic, and it is gated on the
  reader having a working event/scene model to query.

## Is 0.605 near the real ceiling? (the owner's "glass-box, we should do much better")
The mean-ambiguity 2.2-3.0 says: even a competent human, at "the man said..." in a 3-man scene, resolves
by the SCENE, not the sentence. So the glass-box ceiling WITHOUT a situation model is low by construction
-- our 0.605 (character clusters) / surface-head grouping is near the ceiling of what recency+lexical cues
can reach. The "much better" the owner expects is real but it lives BEHIND the situation model, not behind
a better coref rule.

LITERATURE CROSS-CHECK (research drill, verified primary sources -- Bamman et al. 2020 LREC LitBank;
Toshniwal et al. 2021):
- SOTA NEURAL coref on LitBank = 79.3 CoNLL F1 with gold mentions / 68.1 with predicted (Bamman 2020;
  Toshniwal 2021 also 79.3). But this OVERALL number is DOMINATED by pronouns (LitBank is 54.3% pronoun,
  33.5% common-noun/NOM, 12.2% proper), and is achieved WITH a large pretrained LM (SpanBERT-class) whose
  embeddings encode implicit WORLD KNOWLEDGE -- exactly the resource our NO-external-LLM invariant bars.
- Human IAA (ceiling) = MUC 95.5 (3 trained annotators), but inflated (LitBank restricts to characters /
  6 ACE types) and MUC is the most link-lenient metric.
- NO paper reports a per-type (pronoun vs proper vs NOMINAL) F1 breakdown on LitBank -- so this
  decomposition is a novel localization. The INDIRECT literature evidence CONVERGES on our finding:
  common nouns sit a MEDIAN of 5-6 entities from their antecedent (vs 2 for pronouns; Bamman 2020) -- an
  independent corroboration of our "2-3 competing compatible referents / 82% multi-person" measurement;
  multi-genre error analysis finds "the majority of errors involved definite nominals" and some nominal
  links "require world knowledge" (Toshniwal 2021).
- INTERPRETATION: the ~79 SOTA reachable ceiling is (a) pronoun-dominated and (b) built on pretrained-LM
  world knowledge. The common-noun-nominal residual -- the population THIS problem targets -- is the hard,
  world-knowledge-dependent part, unreported as a standalone number precisely because it is where systems
  struggle. Our glass-box no-LLM tie at 0.605 is near the ceiling reachable WITHOUT importing that world
  knowledge; crossing it means building the situation model (or, disallowed, importing an LLM's implicit one).

## ATTACK THE REAL CAPABILITY: the ceiling of every BUILDABLE glass-box lever (measured, GOLD oracle)
Owner: "let's attack the real capability." I measured the CEILING of each buildable brain-foundational lever
BEFORE building, using GOLD referents (so it measures the SIGNAL, not our clustering).

**(1) Event-centrality situation gate -- BUILT.** Reused `event_centrality_coref` for definite descriptions:
+0.013 CoNLL over surface_head (CI-sep), no-regress. A small real landable win; recovers the which-active
slice, not the relational/residual.

**(2) Presence / locality model -- CAPPED, measured fairly** (`exp_commonnoun_scene_presence_ceiling_v1.py`).
FIRST caveat found + fixed: `scene_segment.detect_scene_boundaries` yields only ~1.6 scenes on an ~86-sentence
LitBank excerpt (median 1) -- too coarse; "in scene" == "in doc". So I swept a tight PRESENCE WINDOW Wp
instead. Ceiling over all 1,936 person common-noun links (GOLD referents):

| Wp (on-stage last Wp sents) | recall (ante in window) | unique&correct | presence+recency correct | mean candidates |
|---|---|---|---|---|
| 1 | 0.231 | 0.088 | 0.149 | 1.14 |
| 3 | 0.410 | 0.090 | 0.219 | 2.24 |
| 5 | 0.518 | 0.076 | 0.245 | 3.16 |
| 8 | 0.612 | 0.053 | 0.259 | 4.31 |
| 15 | 0.686 | 0.031 | 0.265 | 6.51 |

A locality/presence model faces a BRUTAL recall/precision tradeoff: tight window -> ~1 candidate but the
antecedent is rarely in it (recall 0.23); wide window -> antecedent present but ~6 candidates. **Best
presence+recency = ~0.26; unique-AND-correct tops out at ~0.09.** Even a PERFECT gold-referent presence
oracle CANNOT fix the referent -- the scenes hold ~3-6 co-present compatible same-gender persons and presence
does not narrow them. By category at Wp=5: head_identical 0.297, name_antecedent 0.333 (surface cue helps),
but **kinship_role 0.194, residual 0.135** -- presence is weakest exactly on the slices that need
relational/world knowledge. So the situation model AT PRESENCE/LOCALITY GRANULARITY is NOT the crossing lever.

**(3) Relational / kinship binder -- PROTOTYPED, works, negligible recovery (confirms the ceiling).**
Structure: of the 423 kinship_role links, 46.8% are possessive-headed ("her father", "his wife") -- a
relational target -- but 52.2% are BARE roles ("the servant", "the Squire") with NO explicit structure
(world-knowledge-bound), and the possessive cases need the relation ESTABLISHED in-text. I BUILT the
mechanism (`situation_predict(relational=True)`): the brain's SAME-RELATION+SAME-RELATUM rule -- resolve the
possessive-pronoun possessor to a discourse referent, key the role-referent by (role_lemma, possessor_ref),
so "her father" ... "her father" (same 'her') co-refer. MEASURED (100 docs): kinship-slice link recall
0.357 -> 0.366 (+4 of 423 links); overall character-cluster CoNLL BEST+RELATIONAL - BEST = +0.0006
CI[+0.0001,+0.0012] (CI-separated but NEGLIGIBLE), BEST+RELATIONAL - surface_head +0.0134 CI-sep, twin loses,
no-regress on named. So the relational situation model is a CORRECT, buildable, brain-foundational mechanism
-- and prototyping it CONFIRMS the world-knowledge boundary rather than crossing it: real recovery is ~1% of
the kinship slice, because most role-relational reference needs the relation established by world knowledge
(bare roles) or a possessor resolution + relation recurrence that the narrative rarely makes explicit.

## SIGNAL-LOSS TRACE of all 3 prototypes (`exp_commonnoun_prototype_signal_trace_v1.py`) -- weak impl vs true wall
Owner discipline: a fair test of a WEAK impl proves THAT setup failed, not the capability. Traced each lever.

- **LEVER 3 (relational) -- CONFIRMED true wall, my apposition hypothesis REFUTED.** Structure across 561
  role-description links: possessive_pronoun 53.7%, BARE 43.7%, apposition_name 1.6%, genitive/of 1.1%. I had
  suspected the weakness was missing APPOSITION ("Mr. Bennet, her father") + role->NAME binding -- but
  apposition is only 1.6% of links, so the relation `father-of(Elizabeth)=Bennet` is ALMOST NEVER stated
  explicitly; it is world/narrative knowledge the reader accumulates. My prototype DID target the dominant
  structure (possessive, 54%); its low recovery is because (a) 44% are bare roles ("the master") needing world
  knowledge, and (b) the possessive relations rarely RECUR with a consistently-resolvable possessor. Not a
  missing-apposition weak impl -- a genuine world-knowledge fact.
- **LEVER 2 (presence) -- CONFIRMED true wall.** Entrance-based spatial presence (present until a gap>6 sents)
  gives 5.19 candidates vs the recency-window's 6.36, but LOWER antecedent retention (0.676 vs 0.749) -- the
  same recall/precision tradeoff. ~5-6 compatible persons are co-present regardless of the presence
  definition. Not a weak window -- genuine scene crowding.
- **LEVER 1 (event gate) -- narrow by design + a real fidelity gap.** It only ranks head-match ties, and its
  event extraction is POSITIONAL (first-subject = agent), NOT true SRL.

**WHERE WE ARE NOT BRAIN-FOUNDATIONAL (named, from the trace):** (i) event extraction is positional, not the
verb-frame SRL the brain uses (Hagoort MUC) -- the situation model is fed noisy roles; (ii) the relational
binder resolved the possessor by most-recent-compatible, not the LANDED graded_coref_pick (ACT-R) resolver;
(iii) there is NO persistent ENTITY WORLD-MODEL (a file card per entity carrying role, relations, location,
recent actions) that reference resolution queries -- we resolve from surface cues, the brain resolves against
an accumulated situation/world model. (i)-(ii) are cheap fidelity fixes the trace predicts yield little (the
structure is not there for most links); (iii) is the real capability = the Phase-1 world model.

## THE PROPER IMPLEMENTATION BUILT: entity world-model query -- mechanism crosses, deployment hits a bootstrap wall
Research (`research` drill, 19 verified sources -- Kintsch CI; Zwaan event-indexing; Sanford-Garrod
bonding->resolution; Morrow-Bower/Glenberg foregrounding; Heim FCS/Kamp DRT; EntNet/EntityNLM/Referential
Reader) PINNED the proper mechanism: the reader resolves "the man"/"her father"/"the master" by QUERYING an
accumulated ENTITY WORLD-MODEL (one file card per entity: types, social ROLE, RELATIONS accumulated across
the text, recent-EVENT participation, presence, salience), restricted to the FOREGROUNDED set (bonding),
scored by descriptive match (resolution) -- NOT by weighting surface cues. WHERE WE WERE NOT
BRAIN-FOUNDATIONAL: no persistent entity model; recency/gender/head are surface cues not entity records;
no role/relation/presence tracking; ACT-R ranks surface mentions not model records.

BUILT it (`exp_commonnoun_entity_world_model_v1.py`) and measured the AMBIGUOUS-LINK resolution accuracy the
research targets (0.26->0.5-0.65):
| arm (1716 ambiguous person common-noun links, GOLD referents) | resolution accuracy |
|---|---|
| recency (surface baseline) | 0.255 |
| event-agent (situation cue alone) | 0.287 |
| **ENTITY WORLD-MODEL query** | **0.540** |
| union-oracle (any single cue uniquely correct) | 0.615 |

**The mechanism CROSSES: 0.255 -> 0.540, more than double, in the research's predicted band.** The union
oracle 0.615 confirms the disambiguating facts ARE in the narrative. My earlier "capped" conclusion was
premature AT THE MECHANISM LEVEL -- it was capped for a SURFACE-CUE resolver, not for the entity-world-model
query. Per-category: head_identical 0.202->0.723, kinship_role 0.294->0.548, residual 0.279->0.418.

**BUT the DEPLOYABLE former hits a BOOTSTRAPPING / IDENTIFIABILITY wall.** The 0.540 uses records built from
the GOLD clustering (the answer). Building records from the reader's OWN clustering (`world_model_predict`)
and re-scoring: character-cluster CoNLL 0.6046 -> 0.6097 (+0.0051, CI includes 0), CEAFe 0.469 -> 0.501
(+0.032 -- genuinely better ENTITY boundaries) but MUC -0.010 -> net wash. TWO-PASS CONSOLIDATION (accumulate
full-document records, then re-resolve -- the brain's "build the situation model, then resolve") does NOT
cross it either: 0.6091 (+0.0045), no gain over single-pass (-0.0006). Reason: self-built records are ~60%
pure (our clustering is ~0.60), so the descriptive/role/relation records are noisy, and consolidation
REINFORCES pass-1 errors rather than fixing them. You cannot build correct-enough entity records without
already resolving the reference -- a genuine chicken-and-egg the brain breaks with PRIOR WORLD KNOWLEDGE
(it knows a priori who "the master" is, who Elizabeth's father is), the external prior the no-LLM invariant
bars. So the residual is now PRECISELY characterized: not a missing mechanism (built, ceiling 0.540) but an
identifiability wall broken only by external world knowledge -- exactly what SOTA imports from a pretrained
LM and the human brings as world knowledge.

## VERDICT (attack the real capability): the crossing capability is NOT a buildable coref/presence heuristic
Every buildable glass-box lever is measured -- and PROTOTYPED where it had a ceiling -- and all are CAPPED:
event-centrality situation gate +0.013 (built, landable); presence/locality ~0.26 ceiling even with a gold
oracle; relational situation model +0.0006 (built, works, negligible -- confirms the ceiling). Combined
BEST+RELATIONAL = +0.0134 over surface_head, far from the +0.43 headroom. The crossing
requires (a) fine-grained discourse FOCUS beyond recency (partly captured, small headroom), (b) a RELATIONAL
world-model (who is whose father / whose servant -- built from the narrative), and (c) genuine WORLD KNOWLEDGE
for the bare-role + deep-residual ~45%. That triad IS the Phase-1 meaning channel / situation-model-plus-world-
knowledge capability -- exactly what SOTA imports from a pretrained LM (barred here) and what the human brings.
It is a fidelity gap to BUILD ACROSS as a Phase-1 program (a relational situation model over the event
structure), NOT a coref build -- and building more coref/presence heuristics here would be the "shared wall
across variations" the owner warns is NOT convergence. The brain's actual mechanism is identified (situation
model + relational + world knowledge) and each buildable approximation is shown capped with a SPECIFIC measured
reason -- the legitimate stopping point for THIS problem, and the precise brief for the next.
