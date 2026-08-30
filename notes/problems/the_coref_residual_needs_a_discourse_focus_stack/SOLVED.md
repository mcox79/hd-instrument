---
problem: the_coref_residual_needs_a_discourse_focus_stack
status: PARTIAL
bar: "Resolves the anti-typical residual CI-separated over the salience/recency floor — the floor = the current recency/frequency-salience resolver (or `graded_coref_pick` as-is) recomputed on the SAME residual population; the info-free twin (shuffled focus transitions / randomized segment boundaries — so the focus signal is destroyed but the pool is unchanged) LOSES CI-separated. A can-fail ORACLE ceiling FIRST (if a perfect focus-oracle does NOT beat the floor, the mechanism is the wrong lever and that is a rigorous NEGATIVE worth reporting)."
result: "TWO results. (A) BAR-1 ORACLE CEILING = a RIGOROUS NEGATIVE for the focus-STACK: on the anti-typical residual (n=420 LitBank competitive pronouns, gold best on none of global recency/subject/freq), a focus stack given the STRONGEST oracle segmentation (gold quote spans + paragraph breaks + entity-topic-shift) diverges from finer TOKEN-locality in 1/420 cases and does NOT beat it (focus_best 0.481 vs token_recency 0.479, delta +0.0024 [+0.000,+0.008] NOT_SEP); the info-free quote-boundary-shuffle twin ties. The ~50-60% focus share (research-drill estimate, SPECULATIVE/by-elimination) is refuted; finer token-locality (0.479 vs sentence-recency 0.000) is the real ceiling. (B) The REAL causal brain-faithful lever = DISCOURSE-PARTICIPANT EXCLUSION: on the FULL anti-typical residual (n=420, all 3rd-person pronouns) it lifts the strongest token-recency floor 0.479 -> 0.557 (paired +0.079 [+0.050,+0.109] CI-sep, null_p95 0.041), recall 1.000; person-only (n=204) +0.083 [+0.046,+0.126] CI-sep; and it improves the FULL competitive population (n=9139) +0.036 [+0.022,+0.051] CI-sep, no regression."
floor: "Strongest floor actually run = TOKEN-recency over the permissive candidate pool = 0.479 on the full anti-typical residual (sentence-recency and the landed graded resolver score ~0.000/0.057 on this anti-salient-by-construction population; token-recency is the strongest and is the floor gated on). Landed keep_after_pool_cleanup floor = 0.502."
controls: "(1) info-free QUOTE-boundary-shuffle twin ties the focus arm (no segment info carried) -> focus-stack refuted. (2) info-free RANDOM-DROP twin (drop same #candidates as the participant filter, at random) LOSES to participant exclusion +0.086 [+0.049,+0.124] CI-sep and collapses recall 1.000->0.902 -> the win is the PARTICIPANT information, not pool-size. (3) participant exclusion is INCREMENTAL over the landed keep_after_pool_cleanup (+0.055 [+0.030,+0.083] CI-sep) -> catches NAMED narrators the pure-pronoun filter misses. (4) recall 1.000 (never drops gold; participant-is-gold ~ 1/200). (5) FULL-population regression control: +0.036 CI-sep, no regression. (6) causal GENDER-agreement NEGATIVE: gender-disagree exclusion +0.000 NOT_SEP, gender adds nothing over participant -0.007 NOT_SEP (the leaky 0.766 used FUTURE mentions). (7) positive control: on the 54 cases where a participant is the wrong token-pick, exclusion recovers 33 (0.61). (8) isolation: all arms differ ONLY in which candidates are dropped; identical recency pick over the kept pool."
files_changed: "experiments/exp_coref_focus_stack_oracle_ceiling_v1.py (new; bar-1 oracle ceiling + focus-stack + segment oracles + twins); experiments/exp_coref_residual_participant_pool_v1.py (new; the participant-exclusion mechanism + gender negative + regression + positive control); verification/test_coref_residual_focus_and_participant.py (new; 21/21 scaffold-free, recomputes both headlines from source); data/exp_coref_focus_stack_oracle_ceiling_v1/metrics.json + data/exp_coref_residual_participant_pool_v1/metrics.json (new). hdlab/ UNTOUCHED (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_coref_residual_focus_and_participant.py"
---

# The coref residual does NOT need a discourse focus STACK — it needs a cleaner candidate SET (participant exclusion). The brief's mechanism is refuted by a direct oracle; a different, more brain-faithful lever is built and validated.

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

## AUDIT UPDATE (for `notes/BRAIN_FOUNDATIONAL_AUDIT.md`)

- **COREFERENCE organ:** the flat Centering Cb was flagged as an OUR-INVENTION simplification of the Grosz-Sidner attentional
  STACK. MEASURED verdict now: on the anti-typical residual the segment STACK is NOT the missing fidelity (a perfect-segment
  oracle adds 1/420 over finer token-locality). The residual is candidate-SET-quality bound. NEW deviations to record: (i) the
  candidate pool omits the PARTICIPANT/deixis constraint (1st/2nd-person entities are wrongly admitted as 3rd-person
  antecedents) — a real, pinned morphosyntactic gap, buildable (+0.036 full CI-sep); (ii) the retrieval recency metric is
  SENTENCE-grain where the brain uses clause/token-grain (finer-locality recovers 0.479 vs 0.000 on the residual, but is
  "ungateable globally" per the prior note — an open gating problem); (iii) permissive gender agreement (`_gn_compat` admits
  unknown gender) — but POSITIVE gender is a causal non-lever here (gold is freshly-named). Citations to add: Grosz & Sidner
  1986 (participants vs focus space); Levinson 1983 / Buhler (deixis vs anaphora); Kush/Parker (item-level finer locality).

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
brain-faithful improvement (people never confuse the narrator with a third character), and it is the piece worth wiring in.

## QUESTIONS

None — the oracle result is decisive (the focus stack is refuted with the strongest available segmentation) and the participant
lever is CI-separated, twin-controlled, and regression-checked. The remaining residual is characterized and routed below.

## NEXT STEPS

1. **Land the participant-exclusion pre-filter** in `hdlab/graded_coref_pick.py` (diff above), sequenced with the assembly
   reader-wiring — strategy owns it (Q111).
2. **New problem — finer-locality gating (the biggest remaining lever):** token/clause-grain recency recovers 0.479 of the
   anti-typical residual but the prior note found it "ungateable globally" (regresses structure-decisive cases 1.000->0.814).
   A confidence/entropy-GATED intra-sentential retrieval is the research note's ranked-#2 build and is the real headroom here.
3. **New problem — the NEUTER (it/its/they) pool is ANIMACY/type-bound:** the neuter residual (~215 cases) needs semantic-type
   candidate filtering (a "downtown" has an inanimate possessor), a different lever than participant exclusion; scope it
   separately (and mind that a static commonsense KB was already measured dead ~2-3% on the person residual — this is TYPE
   filtering, not selectional plausibility).
4. **Fold the AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (participant/deixis gap; sentence-vs-clause recency grain;
   focus-stack-not-the-lever).
