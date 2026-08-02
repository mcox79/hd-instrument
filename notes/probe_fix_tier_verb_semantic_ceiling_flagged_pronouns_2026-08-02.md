# PROBE: what knowledge would actually fix the flagged-pronoun errors? (2026-08-02)

Lightweight probe (not a scored experiment) answering: of the coref_flag_fix_loop_v1 cycle-1
NULL_FIX_MECHANISM (commit 82492af76, atom 29619), what fraction of the FLAGGED+WRONG pronoun
decisions would actually be resolved by verb-selectional-preference/animacy knowledge, vs
discourse-coherence, vs world-knowledge, vs genuine ambiguity? This is the ceiling estimate that
should gate whether we build a verb-semantic resource next.

Prior-work check: `tools/substrate_query.sh "verb selectional preference animacy pronoun
coreference fix"` -> top hits all cosine <=0.459, all generic concept nodes (coreference,
preference, WordNet Preference frame) or unrelated memory/prereg snippets -- NONE at cosine>0.30
is a prior EXPERIMENT CELL on this exact question. Novel probe.

## Method

Extracted every pronoun decision the powered coref eval (`gold_combined_pronoun_powered_v1.jsonl`,
36 passages / 76 pronoun decisions) marks FLAGGED (n_compatible >= 2, same threshold the loop cell
chose) AND strict_cb (our best coref, commit 5b266248f) gets link-WRONG
(`mention_link_wrong`, clean MUC-style local-decision label). This reproduces the loop cell's own
`strict_cb_errors_on_flagged = 17` count exactly (verified: extraction script printed
`n_flagged_wrong_cases=17`). For each case: pronoun surface + role, the clause it sits in, the
compatible-candidate antecedents (with each candidate's own last subject-role clause), the gold
answer, and the surrounding clauses for context. Script:
`C:\Users\marsh\AppData\Local\Temp\claude\d--AI\02e8b04e-1164-42ee-b96d-ac16726a826a\scratchpad\probe_flagged_wrong_extract.py`
(reads `exp_earn_coref_pronoun_strict_cb_v1` / `exp_earn_coref_match_or_allocate_v1` /
`exp_wire_coref_accumulate_situation_model_v1` verbatim, no mutation). Raw dump:
`data/probe_fix_tier_verb_semantic_ceiling_v1_cases.json` (17 cases, full clause context).

Each case classified by hand against the four buckets: (A) verb-selectional-preference/thematic
fit; (B) discourse-coherence (text-internal, cross-clause or same-clause structural); (C)
world/pragmatic knowledge; (D) genuinely ambiguous. B is further split into two very different
sub-mechanisms because they have very different build cost -- see below.

## Distribution (N=17 flagged-and-wrong pronoun decisions)

| Category | N | % |
|---|---|---|
| A -- verb-selectional-preference | 1 | 5.9% |
| B -- discourse-coherence (all forms) | 14 | 82.4% |
|   .. B1: cheap same-clause Principle-B (object pronoun != same-clause subject) | 5 | 29.4% |
|   .. B2: cross-clause / dialogue-turn topic-tracking or entity-identity bridging | 9 | 52.9% |
| C -- world/pragmatic knowledge | 2 | 11.8% |
| D -- genuinely ambiguous | 0 | 0.0% |

**%A = 5.9%. %A+B = 88.2% (dominated by B, not A). %C+D = 11.8%.**

## Verdict: REDIRECT (verb-semantics is not the lever)

Per the pre-registered honest bars: %A is SMALL (5.9%, far under the 40% BUILD bar), so a verb-
selectional-preference / animacy resource would move the needle on essentially none of these
errors -- **REDIRECT**, do not build a verb-semantic resource next.

The surprise is WHERE the mass actually is: not world-knowledge/genuine-ambiguity either (only
11.8%), but **discourse-coherence structure, and just over half of that (29.4% of ALL flagged
errors) is a genuinely CHEAP, purely-syntactic fix we are not yet doing**: our coref candidate
pool does not exclude an entity that already holds the **agent** role in the pronoun's OWN current
clause when the pronoun itself is a non-agent (patient/theme/recipient) role. That is Principle-B-
style disjoint reference ("the lad jerked **him** forward" cannot mean the lad jerked himself) --
zero external knowledge required, just a same-clause role-collision check on data we already
compute (`clause_role` is already tracked per entity per clause in `_EntityCb`). Cases 7 (Dick),
14 (dying-boy/schoolmaster), 15 (Joab/man) are clean single-clause instances of exactly this; case
1 (Sam/Harry) is the closely related Principle-C pattern (pronoun cannot corefer with a proper
name that IMMEDIATELY follows it as an object in the same clause).

The remaining ~53% (B2) is real cross-clause discourse work: reported-speech/dialogue-turn topic
tracking (who is being talked ABOUT inside a quote, not who is speaking -- cases 4/5/6/12/16),
protagonist-continuity across a scene (case 17, Rip), and definite-description-to-name identity
bridging ("the mercurial little Frenchman" = "Tonish", cases 10/11). This is harder and IS the
loop's real open frontier -- but it is a discourse/situation-model problem (who is the topic,
which descriptions co-refer), not a verb-plausibility problem.

## Cheap-animacy-subset check (category A)

Of the single category-A case (case 3, Frisk-the-dog vs Harry-the-boy), our existing
`hdlab/animacy_lexicon.py` does NOT resolve it: both Harry (person) and Frisk (animal) are
ANIMATE, so a simple animate/inanimate split gives no signal; even the lexicon's finer "person"
vs "animal" category tag does not by itself tell you which is *plausible as agent of "fetch,
carry, pick up a ball of cotton"* -- that needs a verb-specific selectional association ("fetch"
skews toward dog-agents in this genre), which we do not have. **Cheap-animacy-resolvable subset =
0/17 (0%).** Category A's one case needs a genuinely richer resource than what we already hold, and
it is only 1 case -- not worth building for.

## Examples (representative, full context in the raw JSON)

**A (1 case) -- case 3, Frisk/Harry:** "*He* could fetch or carry either by land or water, and
would pick up a ball of cotton if little Annie should happen to drop it, or take Harry's dinner to
school for him." gold=Frisk (the dog). Both Frisk and Harry are animate; fetch/carry/pick-up-in-
mouth are dog-behaviors, but this needs verb-specific world knowledge about trained dogs, not a
lexicon category.

**B1 -- cheap syntactic, cases 7/14/15 (representative: case 14):** "and his eyes were very
bright. **The schoolmaster** took a seat beside **him**." gold=boy (the dying child), predicted=
schoolmaster. The schoolmaster is the AGENT of "took a seat" in the SAME clause as the patient
pronoun "him" -- cannot corefer without reflexive "himself". A same-clause role-collision
exclusion resolves this with zero new knowledge.

**B2 -- dialogue-turn tracking, case 6 (Philip/Stephen/Robinson):** "'All this is true,' replied
Philip, 'but **he** has broken my cane, and I will be revenged.'" gold=Robinson_son (the
antagonist established several turns earlier as "farmer Robinson's son"), predicted=Stephen (the
addressee, most recent subject). Requires tracking that Philip's grievance is against the
absent third party across the whole dialogue, not the person he's currently talking to.

**B2 -- entity-identity bridging, case 10 (Tonish/colt):** "The mercurial little Frenchman was
beside himself with exultation. It was amusing to see **him** with his prize." gold=Tonish.
Requires recognizing "the mercurial little Frenchman" (a description) IS Tonish (a name),
introduced pages earlier -- itself a coreference-bridging problem, not a verb-fit problem.

**C -- world/pragmatic, case 13 (Duke/porter):** "'Is the Duke at home?' the porter replied 'but
has left particular orders that... you are to go up to **him** directly.'" gold=Duke,
predicted=porter. Resolving requires household-visiting-protocol knowledge (you are conducted UP
to see the master of the house, not the porter who already answered the door) -- genuine world
knowledge, not text-internal.

**C -- narrative causal inference, case 8 (Sherman/student):** "...to pour the reflected rays of
the sun directly in Mr. Sherman's face. **He** moved his chair, and the thing was repeated." gold=
Sherman, predicted=the ungentlemanly student. Requires the pragmatic inference that moving one's
chair is a REACTION performed by the annoyed victim, not the prankster -- common-sense causal
reasoning about the narrative, not verb-argument selectional preference (both "moved his chair"
subjects are plausible agents of that verb).

## Recommendation

Two-part REDIRECT:
1. Do NOT build a verb-selectional-preference / richer animacy resource next -- ceiling is ~6% of
   the flagged-error population and the one case it would help is not even covered by our existing
   animacy lexicon.
2. DO ship the cheap, zero-knowledge same-clause Principle-B exclusion (candidate holding `agent`
   role in the pronoun's own current clause is excluded when the pronoun's own role is non-agent)
   as a near-free win covering ~29% of the flagged-error population, BEFORE investing in anything
   discourse-heavier. This is a mechanism fix (candidate filtering), not a knowledge resource, and
   is cheap to smoke-test in isolation from the topic-continuity fix that already failed.
3. The REAL open frontier after that (~53% of flagged errors) is discourse-level: reported-speech/
   dialogue-turn topic tracking + definite-description-to-name identity bridging. That is a
   situation-model / entity-tracking problem, consistent with the MEMORY north-star reframe that
   the loop's real cross-clause job is coreference/identity-tracking, not local candidate re-
   ranking -- worth aiming the NEXT real build at THAT, not verb semantics.

## Caveats

- N=17 is small; category boundaries (esp. B1 vs B2, and B vs C) required judgment calls -- flagged
  transparently with quoted context above so the Director can sanity-check.
- The B1 same-clause fix is proposed from READING the cases, not yet implemented or smoke-tested;
  its true yield depends on whether `clause_role` reliably tags the local subject for participial/
  continued-subject clauses (case 7's "catching Dick..., jerked him forward" is a weaker instance
  of this than the single-clause cases 14/15 -- flagged as uncertain in the writeup above).
- This is diagnosis only. No cell was dispatched; no code changed in any banked experiment file.
