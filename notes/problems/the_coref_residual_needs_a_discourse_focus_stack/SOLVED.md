---
problem: the_coref_residual_needs_a_discourse_focus_stack
status: SOLVED
bar: "Resolves the anti-typical residual CI-separated over the salience/recency floor — the floor = the current recency/frequency-salience resolver (or `graded_coref_pick` as-is) recomputed on the SAME residual population; the info-free twin (shuffled focus transitions / randomized segment boundaries — so the focus signal is destroyed but the pool is unchanged) LOSES CI-separated. A can-fail ORACLE ceiling FIRST (if a perfect focus-oracle does NOT beat the floor, the mechanism is the wrong lever and that is a rigorous NEGATIVE worth reporting)."
result: "TWO results. (A) BAR-1 ORACLE CEILING = a RIGOROUS NEGATIVE for the focus-STACK: on the anti-typical residual (n=420 LitBank competitive pronouns, gold best on none of global recency/subject/freq), a focus stack given the STRONGEST oracle segmentation (gold quote spans + paragraph breaks + entity-topic-shift) diverges from finer TOKEN-locality in 1/420 cases and does NOT beat it (focus_best 0.481 vs token_recency 0.479, delta +0.0024 [+0.000,+0.008] NOT_SEP); the info-free quote-boundary-shuffle twin ties. The ~50-60% focus share (research-drill estimate, SPECULATIVE/by-elimination) is refuted; finer token-locality (0.479 vs sentence-recency 0.000) is the real ceiling. (B) The REAL causal brain-faithful lever = DISCOURSE-PARTICIPANT EXCLUSION: on the FULL anti-typical residual (n=420, all 3rd-person pronouns) it lifts the strongest token-recency floor 0.479 -> 0.557 (paired +0.079 [+0.050,+0.109] CI-sep, null_p95 0.041), recall 1.000; person-only (n=204) +0.083 [+0.046,+0.126] CI-sep; and it improves the FULL competitive population (n=9139) +0.036 [+0.022,+0.051] CI-sep, no regression. (C) It GENERALIZES as a brain principle, not a 19c-narrator artifact: helps MOST in 1st-person narration (+0.137 CI-sep), NEUTRAL in 3rd-person narration (+0.010 NOT_SEP), helps BOTH pronoun classes (person +0.083, neuter +0.074), NEVER hurts any genre split (recall 1.000 everywhere), and every exclusion threshold from 'any 1st/2nd mention' (+0.117) to '100% participant' (+0.050) beats the floor CI-sep (not a tuned knob). (D) It GENERALIZES ACROSS THE PHI-FEATURE FAMILY: participant exclusion is ONE case of hard phi-agreement hardening. ANIMACY agreement is a second clean recall-safe lever -- for person pronouns drop confirmed-INANIMATE candidates (lexical, no gold NER: +0.123 [+0.079,+0.169], recall 1.000; gold entity-type: +0.054), for it/its drop confirmed-ANIMATE (+0.125 [+0.056,+0.205]); person + animacy COMPOSE to +0.152 [+0.098,+0.205] (person 0.461 -> 0.613); the random-drop twin LOSES (-0.064, recall->0.64). Gender is the PRINCIPLED EXCEPTION (+0.010 NOT_SEP) -- person/animacy are established immediately by the pronoun form / head noun, a freshly-named character's gender often is not. (E) LANDING-VALIDATED through the ACTUAL landed resolver graded_antecedent_pick: a REFINED pure-participant rule (participant AND never narrated in 3rd person -- the true narrator, not a talkative character) lifts the FULL deployed workload (n=9139) 0.786 -> 0.841 (+0.054 CI-sep), recall 0.996, and GENERALIZES -- +0.147 in 1st-person docs, +0.006 ABOVE (no longer a regression) in 3rd-person docs, +0.162 on the residual; +animacy adds more (0.854). Turnkey diff in PROPOSED_HDLAB_DIFF.md."
floor: "Strongest floor actually run = TOKEN-recency over the permissive candidate pool = 0.479 on the full anti-typical residual (sentence-recency and the landed graded resolver score ~0.000/0.057 on this anti-salient-by-construction population; token-recency is the strongest and is the floor gated on). Landed keep_after_pool_cleanup floor = 0.502."
controls: "(1) info-free QUOTE-boundary-shuffle twin ties the focus arm (no segment info carried) -> focus-stack refuted. (2) info-free RANDOM-DROP twin (drop same #candidates as the participant filter, at random) LOSES to participant exclusion +0.086 [+0.049,+0.124] CI-sep and collapses recall 1.000->0.902 -> the win is the PARTICIPANT information, not pool-size. (3) participant exclusion is INCREMENTAL over the landed keep_after_pool_cleanup (+0.055 [+0.030,+0.083] CI-sep) -> catches NAMED narrators the pure-pronoun filter misses. (4) recall 1.000 (never drops gold; participant-is-gold ~ 1/200). (5) FULL-population regression control: +0.036 CI-sep, no regression. (6) causal GENDER-agreement NEGATIVE: gender-disagree exclusion +0.000 NOT_SEP, gender adds nothing over participant -0.007 NOT_SEP (the leaky 0.766 used FUTURE mentions). (7) positive control: on the 54 cases where a participant is the wrong token-pick, exclusion recovers 33 (0.61). (8) isolation: all arms differ ONLY in which candidates are dropped; identical recency pick over the kept pool."
files_changed: "experiments/exp_coref_focus_stack_oracle_ceiling_v1.py (new; bar-1 oracle ceiling + focus-stack + segment oracles + twins); experiments/exp_coref_residual_participant_pool_v1.py (new; the participant-exclusion mechanism + gender negative + regression + positive control); experiments/exp_coref_participant_generalization_v1.py (new; genre/pronoun-class generalization + threshold robustness); experiments/exp_coref_residual_phi_agreement_v1.py (new; the phi-agreement GENERALIZATION -- person + animacy hardening, lexical + gold, gender negative); experiments/exp_coref_phi_agreement_prefilter_v1.py (new; LANDING VALIDATION -- the pre-filter through the ACTUAL graded_antecedent_pick + genre generalization + the refined pure-participant rule); verification/test_coref_residual_focus_and_participant.py (new; 45/45 scaffold-free, recomputes every headline from source); data/exp_coref_focus_stack_oracle_ceiling_v1/metrics.json + data/exp_coref_residual_participant_pool_v1/metrics.json + data/exp_coref_participant_generalization_v1/metrics.json + data/exp_coref_residual_phi_agreement_v1/metrics.json + data/exp_coref_phi_agreement_prefilter_v1/metrics.json (new); notes/problems/the_coref_residual_needs_a_discourse_focus_stack/{research_deixis_participant_exclusion_brain_mechanism_2026-08-30.md (brain-mechanism drill), PROPOSED_HDLAB_DIFF.md (turnkey diff)}. hdlab/ UNTOUCHED (proposed diff, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_coref_residual_focus_and_participant.py"
---

# SOLVED by refute-and-replace. The coref residual does NOT need a discourse focus STACK (refuted by a direct perfect-segment oracle: it adds 1/420 over finer token-locality). It needs HARD PHI-AGREEMENT on the candidate set (person + animacy) — the substrate's permissive `_gn_compat` admits grammatically-impossible antecedents. The replacement mechanism is built, validated THROUGH THE ACTUAL landed resolver (+0.054 full population / +0.162 residual CI-sep, recall 0.996), generalized (genre, pronoun-class, phi-feature family, threshold, cross-linguistic-universal), brain-confirmed by a research drill, and landing-ready (turnkey diff). hdlab/ landing is the strategy session's (Q111); I did not and may not write it.

## What I built and measured

**Bar item 1 (the required can-fail oracle ceiling), measured FIRST — and it is a RIGOROUS NEGATIVE.**
I reconstructed the anti-typical residual on my own instrument (`exp_coref_graded_cue_retrieval_litbank_v1`): every competitive
LitBank pronoun (>=2 gn-compatible prior gold entities, gold among them) where the gold antecedent is the argmax on NONE of
{global recency, subjecthood, frequency} — the `gold_structurally_dominated` set, n=420, resolver-independent (NOT conditioned
on the resolver erring, so the floor is a genuine >0 baseline). I then built a **faithful Grosz-Sidner focus STACK**: narration
is a recurring matrix frame; each quoted-speech span PUSHES a nested frame that POPS at its close (so a narration pronoun's focus
space EXCLUDES quote mentions — focus can RETURN to a less-recent same-frame entity). I gave it the STRONGEST available oracle
segmentation — **gold quote spans** (LitBank `quotations/`), **paragraph breaks** (LitBank `original/`), and an
entity-topic-shift segmenter — i.e. a genuine perfect-segment oracle, not a surface detector.

Result: the focus stack diverges from finer **token-locality** in **1 case out of 420**, and does not beat it
(`focus_best` 0.481 vs `token_recency` 0.479; paired +0.0024 [+0.000,+0.008] **NOT_SEP**). The info-free quote-boundary-shuffle
twin ties. **A perfect focus-oracle does not clear the token-locality floor** — so, by the bar's own words, "the mechanism is
the wrong lever and that is a rigorous NEGATIVE." The research-drill estimate that focus carries ~50-60% of this residual was
explicitly flagged SPECULATIVE / by-elimination; measured directly, it is **refuted**. What actually recovers ~48% is finer
**token/clause-grain recency** (sentence-bucket recency scores 0.000 by construction; token-distance recency scores 0.479) —
the research note's "finer-locality" channel, which is the real ceiling here, not focus.

**Why (I read the cases, per the standing directive to understand a wall before declaring it).** The anti-typical residual is
NOT topic-shift. The candidate pool is huge (**mean ~45**), and the gold looks anti-salient only because the pool is FLOODED
with non-referents that the permissive agreement filter admits — above all the **discourse PARTICIPANTS**: the narrator/speaker
"I"/"we" and the addressee "you". Their gender is unknown (their pronouns aren't gendered), so `_gn_compat(f/m, sg, None, None)
= True` admits them for every "he"/"she"; and being the most frequent + most recent entity, salience grabs them. Concrete
verbatim misses: Dracula "she" -> gold *lady* but token-recency picks *I* (narrator); Adrift "he" -> gold *boy* but picks *I*
(the speaker); Vanity Fair "her" -> gold *Sedley* but picks *we*.

**The real mechanism (bar items 3-4), built and validated: DISCOURSE-PARTICIPANT EXCLUSION.** A candidate cluster whose PRIOR
mentions are >=50% 1st/2nd-person forms is a discourse participant (speaker/hearer) and is excluded from a 3rd-person pronoun's
candidate pool. On the FULL anti-typical residual (n=420, all 3rd-person pronouns) this lifts the strongest (token-recency)
floor **0.479 -> 0.557** (paired **+0.079 [+0.050,+0.109]** CI-sep, null_p95 0.041); person-only (n=204) **+0.083** CI-sep,
and it GENERALIZES to the neuter/plural residual (they/them referring to groups, polluted by "we"): **+0.074** CI-sep. On the
FULL competitive population (n=9139) **0.679-class -> +0.036 CI-sep** — it HELPS the typical cases too, no regression. Controls:
recall **1.000** (never drops gold); the info-free random-drop twin LOSES (**+0.086** CI-sep, and it collapses recall to 0.902
— so the win is the participant INFORMATION, not the pool-size reduction); **incremental over the landed**
`keep_after_pool_cleanup` (**+0.055** CI-sep — the landed pure-pronoun filter misses NAMED narrators like Jonathan-in-Dracula);
positive control recovers 33/54 of the participant-is-wrong-pick cases. It has no tuned parameters worth the name (a 0.5
majority threshold), so there is no DEV/TEST overfitting to report.

This is a discourse-attentional mechanism — the PARTICIPANT / deixis layer of Grosz-Sidner attentional state (I/you are
conversational participants, categorically distinct from the 3rd-person focus-space referents; person-feature agreement is an
obligatory morphosyntactic constraint — she != I, they != we) — just NOT the segment push/pop stack the brief proposed.

**It GENERALIZES as a principle, not a corpus trick (the owner's "this needs to generalize too", tested directly).** The risk
was that this only works because 19c novels have a chatty 1st-person NARRATOR. Decomposing by genre kills that worry: the lift
is **+0.137 CI-sep in 1st-person-narrated docs** (where the narrator "I" floods the pool), **NEUTRAL (+0.010 NOT_SEP) in
3rd-person-narrated docs** (no narrator to remove), positive in both dialogue-density halves, positive for BOTH person and
neuter/plural pronouns, and it **HURTS NOWHERE** (recall 1.000 in every split). That is the exact signature of a grammatical
principle whose BENEFIT scales with how much a text violates it — helps where participant pollution exists, inert where it
doesn't, harmful never. And it is not a tuned knob: every exclusion threshold from "any 1st/2nd mention" (+0.117) to "100%
participant" (+0.050) beats the floor CI-separated (recall trades off cleanly; 0.5 is the recall-safe point).

**Brain-fidelity confirmed by a research drill (`research_deixis_participant_exclusion_brain_mechanism_2026-08-30.md`), and
PINNED vs OUR-INVENTION labelled honestly.** The adversarial question I set the drill — "is person-agreement actually NOT a
hard/early constraint?" (which would have reframed the result) — FAILED, in the direction that strengthens it:
- **PINNED — person is the sturdiest phi-feature and a participant is an IMPOSSIBLE (not just unlikely) antecedent.** Benveniste
  1966 (1st/2nd = the speech-act "persons", 3rd = the "non-person" — disjoint in reference by definition); Mancini et al. 2011
  (person violations give an N400 tied specifically to the speaker/hearer discourse-participant representation); Van Dyke /
  Parker & Van Dyke 2019 (person is the feature most RESISTANT to retrieval intrusion). Cross-linguistically UNIVERSAL (Cysouw
  2003; Silverstein 1976) — so the lever transfers (surface pronoun forms are per-language; the participant/non-participant
  split is not). The narrator "I" as the single most-accessible entity that any salience ranker grabs unless person is enforced
  first (Ariel/Gundel/Centering) is a clean theory-match to the +0.137-vs-neutral split.
- **The drill's one honest correction:** "categorically never" is exactly right at the COMPETENCE (grammar) level but slightly
  strong at the PROCESSING level (retrieval is graded best-match). The upshot VALIDATES the design: a HARD exclusion on the
  candidate SET (what I built) is MORE faithful than a graded down-weight, because it mirrors competence-level eligibility — and
  my recall 1.000 confirms the corpus almost never actually violates it. **OUR-INVENTION (swept, not pinned):** the ">=50% of
  prior mentions are 1st/2nd-person" proxy for "this entity is a participant"; the drill confirms the GLOBAL person-TYPE proxy
  is defensible and robust, while per-utterance speaker ATTRIBUTION is genuinely hard (matching the landed WorkingOverlay
  result). I do NOT claim person > gender as a single ordering (SPECULATIVE — different effect kinds).

**It generalizes ACROSS THE PHI-FEATURE FAMILY (the owner's "generalize in all aspects") -- participant exclusion is
ONE case of a general principle.** The root cause is not "narrators" specifically; it is that the substrate's candidate
filter `_gn_compat` is PERMISSIVE (unknown person/gender/number passes), so it admits candidates that VIOLATE hard
phi-agreement. Hardening the IMMEDIATELY-ESTABLISHED features cleans the pool:
- **PERSON (participant):** +0.083 CI-sep (validated above).
- **ANIMACY:** a second clean, recall-safe, CI-sep lever. For person pronouns (he/she/him/her) the antecedent must be
  ANIMATE -> drop confirmed-INANIMATE candidates (a lexical animacy heuristic with NO gold NER: **+0.123** [+0.079,
  +0.169], recall **1.000**; the gold LitBank entity-type version: +0.054). For it/its the antecedent must be INANIMATE
  -> drop confirmed-ANIMATE persons (**+0.125** [+0.056,+0.205], recall 1.000). Person + animacy COMPOSE to **+0.152**
  [+0.098,+0.205] (person residual 0.461 -> 0.613); the info-free random-drop twin LOSES (-0.064, recall collapses to
  0.64). That the LEXICAL animacy (a noun list + name gazetteer, no gold annotations) works EVEN BETTER than gold
  entity-type is the cute-trick guard passing: the win is not an artifact of gold NER labels.
- **GENDER is the PRINCIPLED EXCEPTION (+0.010 NOT_SEP), and the exception PROVES the rule:** person and animacy are
  established IMMEDIATELY (the pronoun form is 1st/2nd-person; the head noun "city"/"man" carries animacy), so they are
  causally available at the pronoun; a freshly-NAMED character's gender often is not yet established by any prior cue, so
  gender agreement cannot fire causally. The generalization is to the immediately-established phi-features, not to every
  feature blindly -- exactly what a faithful account predicts. This also PARTLY closes the neuter-residual gap the
  earlier draft routed as a separate problem: animacy is the lever there too.

**Prior work credited (not re-derived).** `exp_read_deixis_participant_tracking_third_reader_v1` (2026-07-18,
SCOPE_LIMITED_OR_WEAK) and `hdlab.state_of_mind.WorkingOverlay` (`note_turn/resolve_deixis/speaker/addressee`) already model the
COMPLEMENTARY, HARDER direction — resolving what "I"/"you" inside quotes REFER TO (bind I->speaker). That attribution was
scope-limited; my EXCLUSION direction is easier (needs only person-TYPE, not attribution) and is validated CI-sep. The two
compose: exclude participants from 3rd-person pools (this result) + attribute the 1st/2nd-person indexicals to speaker/addressee
(WorkingOverlay).

## KEY REALIZATIONS (the moves that made the result)

1. **Measure the oracle with the BRAIN'S actual operation, or you measure your own bug.** My first focus-stack implementation
   keyed on `(segment_id, token_position)` — but segment id is monotonic in token position, so the segment tie-break could never
   override recency and the arm mathematically REDUCED to token-recency. Catching that (focus == token-recency to 3 decimals)
   forced the faithful push/pop STACK, where a closed quote frame is popped and its mentions leave the focus space. Only the
   faithful version is a real test — and it still refuted the mechanism (1/420).
2. **Read the hard cases before theorizing.** Fifteen minutes reading verbatim misses overturned the brief's whole model: the
   residual is candidate-SET pollution, not topic-shift. No aggregate number would have shown that "I" (the narrator) is the
   dominant wrong antecedent for "she".
3. **The leak that flattered gender.** Requiring positive gender agreement scored 0.766 — but only because it read the cluster's
   FUTURE gendered pronouns. Recomputing gender from PRIOR mentions only (plus a gendered-noun lexicon and an NLTK name
   gazetteer) collapsed recall to 0.53 and the "win" to -0.042 (NOT_SEP): causally, when "she" first refers to a freshly-named
   character no prior pronoun has established her gender, so prioritizing confirmed-gender candidates promotes DISTRACTORS.
   The lever is the PARTICIPANT feature, not gender. (Reported as an explicit negative.)
4. **The right floor is the strongest one actually run.** The landed graded resolver scores 0.057 on the anti-typical population
   (its salience weights anti-correlate with anti-salient gold); token-recency scores 0.461. Gating over token-recency (the
   strongest) rather than the trivially-weak graded floor is what keeps the participant win honest.

## What I did NOT establish / would withdraw first

- **The focus STACK is not shown to help at all** on this residual (1/420). If wrong, I'd withdraw the strength of the negative
  first — but it survives the strongest oracle segmentation available and an info-free twin, and the divergence count is 1.
- **Participant exclusion is a PARTIAL fix, not the whole residual.** After it, ~46% of the anti-typical person residual still
  errs. Reading those, the remainder is **finer within-sentence syntactic binding** (Black Beauty "him" -> the object/patient
  *horse* not the subject *farrier*; Main Street "his" -> the possessor *lawyer*) plus a small genuine **QUD/semantic** core
  (Vanity Fair: the dialogue is *about* Sedley's departure). Both need clause structure or meaning — see NEXT STEPS.
- **The NEUTER residual (it/its/they, ~215 of 420) is PARTLY but not fully addressed.** Participant exclusion generalizes to
  it (+0.074 CI-sep — "they/them" for a group is polluted by "we"), which is why the headline is on the full n=420. But its
  RESIDUAL pollution is ANIMACY/semantic-type (a "downtown" belongs to a *city*, not an *ocean*), a different lever I did NOT
  build — named as an adjacent gap (NEXT STEPS #3), not silently dropped.
- **Gender via a fuller name/description gazetteer** might recover more than the closed lexicon I used; I did not build the
  complete gazetteer, so the gender negative is bounded by my gender coverage (though the FAILURE MODE — promoting confirmed
  distractors over unknown gold — is structural, not a coverage artifact).

## PROPOSED hdlab CHANGE (strategy lands, Q111 — I did not touch hdlab/)

Extend `hdlab/graded_coref_pick.py` with a **participant-exclusion pre-filter**, applied to the candidate pool BEFORE
`graded_antecedent_pick` (a stronger sibling of the existing `keep_after_pool_cleanup`):

```python
# a cluster whose PRIOR mentions are >=50% 1st/2nd-person forms is a discourse PARTICIPANT (speaker/hearer),
# categorically ineligible as a 3rd-person antecedent (deixis vs anaphora; person-feature agreement). Unlike
# is_first_second_person_artifact (pure-pronoun only), this also excludes NAMED narrators/speakers.
FIRST_SECOND_PERSON_EXT = FIRST_SECOND_PERSON | frozenset("thou thee thy thine mine ours yours".split())

def is_discourse_participant(prior_mention_heads):  # heads of this cluster's mentions BEFORE the pronoun
    heads = [h.lower() for h in prior_mention_heads]
    if not heads:
        return False
    return sum(h in FIRST_SECOND_PERSON_EXT for h in heads) / len(heads) >= 0.5

def keep_after_participant_filter(candidate_prior_heads):  # per-candidate PRIOR-mention head lists
    return [i for i, heads in enumerate(candidate_prior_heads) if not is_discourse_participant(heads)]
```

Wiring: the caller applies `keep_after_participant_filter` to its candidate pool for a 3rd-person pronoun (it composes with
`keep_after_pool_cleanup`). Measured effect on LitBank: full competitive person accuracy +0.036 CI-sep, anti-typical residual
+0.083 CI-sep, recall 1.000, no regression. **Do NOT** add the focus stack (refuted) or a positive gender-agreement cue (a
leak / causal negative). ⚠️ COORDINATE with the assembly reader-wiring (Changes 2-3) which also touch the coref path.

**The general form (harden phi-agreement, not just the person feature).** The deeper fix is that `_gn_compat` is PERMISSIVE
(unknown passes). Add a recall-safe ANIMACY constraint alongside person: for a PERSON pronoun (he/she/him/her) drop candidates
whose entity is CONFIRMED-INANIMATE (a place/object -- from the reader's NER/lexical animacy, NOT gold); for it/its drop
CONFIRMED-ANIMATE (person) candidates. Measured: lexical animacy +0.123 (person, recall 1.000), it/its +0.125; person +
animacy compose to +0.152. Keep it CONFIRMED-incompatible-only (recall-safe); do NOT require POSITIVE gender (causal
non-lever). This is a small, glass-box, KB-free extension of the agreement pre-filter the pool already runs.

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

- **COREFERENCE organ:** the flat Centering Cb was flagged as an OUR-INVENTION simplification of the Grosz-Sidner attentional
  STACK. MEASURED verdict now: on the anti-typical residual the segment STACK is NOT the missing fidelity (a perfect-segment
  oracle adds 1/420 over finer token-locality). The residual is candidate-SET-quality bound. NEW deviations to record: (i) the
  candidate pool VIOLATES HARD PHI-AGREEMENT because `_gn_compat` is PERMISSIVE (unknown person/animacy/number/gender all pass);
  the brain enforces phi-agreement as an obligatory filter. Two immediately-established features are buildable, recall-safe,
  CI-separated levers: PERSON/participant (1st/2nd-person entities wrongly admitted as 3rd-person antecedents; +0.083 residual /
  +0.036 full) and ANIMACY (inanimate entities admitted for he/she, animate for it/its; +0.123 lexical / +0.125 it-its; person +
  animacy compose +0.152). GENDER is the principled EXCEPTION (causally unavailable for freshly-named entities; +0.010 NOT_SEP).
  (ii) the retrieval recency metric is SENTENCE-grain where the brain uses clause/token-grain (finer-locality recovers 0.479 vs
  0.000 on the residual, but is "ungateable globally" per the prior note — an open gating problem). The PARTICIPANT gap should be filed
  as PINNED-BY-EVIDENCE (person-feature agreement is grammar, validated cross-literature) with a HARD-exclusion fix; the fine
  speaker-ATTRIBUTION half stays OUR-INVENTION/hard (matching `WorkingOverlay`'s SCOPE_LIMITED result). Citations to add:
  Benveniste 1966 (person = the speech-act persons; 3rd = non-person); Mancini et al. 2011 (person-violation N400 tied to the
  discourse-participant representation); Cysouw 2003 / Silverstein 1976 (participant/non-participant is a language universal);
  Ariel/Gundel accessibility + Centering (the self "I" is the most-accessible entity a salience ranker grabs); Parker & Van
  Dyke 2019 (person most resistant to retrieval intrusion); Grosz & Sidner 1986 (participants vs focus space); McRae &
  Ferretti / animacy in thematic-fit + the entity model (animacy as an obligatory selectional constraint on he/she vs it). One measured soft
  spot to record: a quoted "I" belongs to a CHARACTER, not the narrator — layer per-utterance participant tracking INSIDE
  detected quotes only; do NOT make the exclusion lever depend on attribution.

## TLDR (plain language)

Our reader mis-links pronouns in old novels, and the brief guessed the fix was a "who are we talking about right now" tracker
that follows the story scene to scene. I built that tracker with the best possible scene information (the book's own quotation
marks and paragraph breaks) and measured it honestly: it fixes essentially none of the hard cases (one in four hundred) beyond
what you already get by just looking at which name is physically closest to the pronoun. So the brief's idea is the wrong fix,
and I can prove it. Reading the actual mistakes showed the real problem: the reader is choosing the antecedent from a list of
about forty candidates, most of which are junk — and the single biggest junk entry is the NARRATOR themselves ("I"), which the
reader keeps grabbing for "he"/"she". Telling the reader that the person telling the story ("I", "we", "you") is never who
"he"/"she" refers to fixes a clean, measurable slice of the errors — it makes the reader right about 8 more pronouns in every
hundred hard cases, and about 4 more in every hundred cases overall, without ever making anything worse. That is a real,
brain-faithful improvement (people never confuse the narrator with a third character — this is basic grammar, confirmed against
the brain-science literature, and it is a universal across languages, not a quirk of old English novels). It behaves exactly
like a real rule should: it helps a LOT in stories told in the first person, does nothing (and no harm) in stories told in the
third person, and never once makes any kind of book worse. That "helps where the problem is, harmless everywhere else" pattern
is how we know it is a genuine principle and not a trick tuned to this one set of books. It is the piece worth wiring in.

## QUESTIONS

None — the oracle result is decisive (the focus stack is refuted with the strongest available segmentation) and the participant
lever is CI-separated, twin-controlled, and regression-checked. The remaining residual is characterized and routed below.

## NEXT STEPS

1. **Land the participant-exclusion pre-filter** in `hdlab/graded_coref_pick.py` (diff above), sequenced with the assembly
   reader-wiring — strategy owns it (Q111). It is a PINNED grammatical constraint (person-feature agreement), research-drill
   confirmed, generalization-tested, hurts nowhere. Compose it with the landed `hdlab.state_of_mind.WorkingOverlay` (which
   already tracks speaker/addressee for the COMPLEMENTARY attribution direction). Fidelity refinement for later: inside detected
   quotes, a 1st-person "I" is the CHARACTER speaking, not the narrator — add per-utterance participant tracking there only.
2. **New problem — finer-locality gating (the biggest remaining lever):** token/clause-grain recency recovers 0.479 of the
   anti-typical residual but the prior note found it "ungateable globally" (regresses structure-decisive cases 1.000->0.814).
   A confidence/entropy-GATED intra-sentential retrieval is the research note's ranked-#2 build and is the real headroom here.
3. **The NEUTER (it/its) ANIMACY lever is now DEMONSTRATED (+0.125 CI-sep, recall 1.000) and folds into the same
   phi-agreement pre-filter** — land it with the animacy constraint. What REMAINS unsolved: "they/them" is
   animacy-UNCONSTRAINED (a group can be animate or inanimate), and the residual AFTER animacy is finer inanimate-type
   disambiguation (which "it" of several inanimate things) — that last slice is the genuinely semantic one (a static
   commonsense KB was measured dead ~2-3%); scope only that remainder separately.
4. **Fold the AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (participant/deixis gap; sentence-vs-clause recency grain;
   focus-stack-not-the-lever).

---

## INTEGRATED_BY_STRATEGY — 2026-08-30 (grade: EXCELLENT; SOLVED owner-DONE)

Integrated by strategy. Reverified FIRST-HAND: `verification/test_coref_residual_focus_and_participant.py` **45/45 PASS** (scaffold-free — recomputes every headline from source, INCLUDING the landing validation through the real `hdlab.graded_coref_pick.graded_antecedent_pick`, W38-W45). Argument adversarially audited and sound: (1) the brief's named FOCUS-STACK is REFUTED with a direct perfect-segmentation oracle (diverges from finer token-locality 1/420, 0.481 vs 0.479 NOT_SEP, twin ties) — a rigorous negative = a full pass; the discipline lesson (measure the oracle with the BRAIN's operation: the first stack keyed on (segment, token-position), monotone, silently reduced to token-recency). (2) The real fix = HARD PHI-AGREEMENT on the candidate set (the permissive `_gn_compat` admits the discourse participant "I" for he/she + animacy-mismatched entities): PERSON +0.083 CI-sep residual (recall 1.000); ANIMACY +0.123 lexical no-gold-NER; person+animacy compose +0.152; GENDER the principled exception (+0.010 NOT_SEP). (3) Validated through the ACTUAL landed resolver: refined pure-participant lifts n=9139 0.786->0.841 (+0.054 CI-sep, recall 0.996); residual 0.057->0.219. (4) Generalizes every aspect (1st-person +0.147, 3rd-person +0.006 no-regression, person+neuter, threshold-robust, cross-linguistic universals, no-gold-NER beats gold = anti-cute-trick); info-free random-drop twin loses. Brain-faithful PINNED (person+animacy obligatory universal anaphora constraints; hard exclusion > graded down-weight, recall 1.000). Exemplary honesty (withdraws the focus stack, the gender leak, the open residual).

**hdlab landing DONE (Q111, additive/opt-in):** appended `FIRST_SECOND_PERSON_EXT` + `is_discourse_participant(prior_mention_heads)` + `phi_agreement_keep(pronoun_low, candidate_prior_heads, candidate_animacy)` to `hdlab/graded_coref_pick.py` (verbatim from PROPOSED_HDLAB_DIFF.md, resolving `FIRST_SECOND_PERSON`/`THIRD_PERSON_PRON` already in the module). They COMPOSE with the existing `keep_after_pool_cleanup`; existing callers are BYTE-UNCHANGED (the pre-filter is inert until a caller opts in). Witness `verification/test_phi_agreement_prefilter_organ.py` recomputes from source. **The reader-WIRING** (apply `phi_agreement_keep` to the live coref pool before `graded_antecedent_pick`, + build `candidate_animacy` from the reader's NER) is COUPLED with the assembly (Changes 2-3) — recorded in the wire-don't-island debt. Do NOT add the focus stack / a positive gender cue / the global (non-refined) participant rule.

**Audit §2b folded** (COREFERENCE: the flat Centering Cb / focus-stack is NOT the residual's fidelity gap — a perfect-segment oracle adds 1/420; the pool VIOLATES hard phi-agreement; PERSON/participant + ANIMACY are recall-safe CI-separated levers, GENDER the principled exception. Citations: Benveniste 1966; Mancini 2011; Cysouw 2003; Silverstein 1976; Parker & Van Dyke 2019; Grosz & Sidner 1986). Review (EXCELLENT) + `> ## ✅ SOLVER REVIEW` block in PROBLEM.md; `priority:` cleared.

**Follow-ons:** they/them animacy-unconstrained resolution; confidence-gated finer clause-locality (the biggest remaining slice); the ~2-3% genuinely-semantic core.
