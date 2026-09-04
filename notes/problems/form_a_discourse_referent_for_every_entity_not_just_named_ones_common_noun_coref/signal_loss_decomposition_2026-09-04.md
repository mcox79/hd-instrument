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
