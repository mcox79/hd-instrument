# PROPOSED hdlab DIFF — phi-agreement candidate pre-filter (Q111, strategy lands)

**Status:** validated end-to-end through the ACTUAL landed resolver `hdlab.graded_coref_pick.graded_antecedent_pick`
(cell `experiments/exp_coref_phi_agreement_prefilter_v1.py`; witness `verification/test_coref_residual_focus_and_participant.py`).
I (solver) may not write `hdlab/` — this is the exact change for the strategy session to apply.

## What it is

A recall-safe candidate-pool **pre-filter** that enforces hard, immediately-established PHI-AGREEMENT (person, animacy)
before `graded_antecedent_pick` — fixing that the substrate's agreement check is PERMISSIVE (unknown passes), which
admits grammatically-impossible antecedents (the narrator "I" for "she"; a place for "he"). Brain-foundational
(person = the speech-act "persons" vs the 3rd-person "non-person", Benveniste 1966; a language universal, Cysouw 2003;
animacy is an obligatory selectional constraint). Glass-box, KB-free, NO external LLM.

## Measured effect (through the landed graded_antecedent_pick, LitBank 100 docs)

| population | as-is | TIER1 pure-participant | TIER2 +animacy |
|---|---|---|---|
| FULL competitive (n=9139, the deployed workload) | 0.786 | **0.841 (+0.054 CI-sep)** recall 0.996 | 0.854 (+0.068) recall 0.989 |
| anti-typical residual (n=420) | 0.057 | 0.219 (+0.162 CI-sep) recall 1.000 | 0.288 (+0.231) recall 0.981 |
| 1st-person-narrated docs (n=3118) | 0.663 | **0.810 (+0.147 CI-sep)** recall 0.994 | 0.823 (+0.160) recall 0.988 |
| 3rd-person-narrated docs (n=6021) | 0.851 | 0.857 (+0.006 ABOVE) recall 0.997 | 0.870 (+0.019) recall 0.989 |

Info-free random-drop twin LOSES (residual +0.176 CI-sep, recall collapses). Generalizes: ABOVE on every split, no
regression anywhere. **Recommend landing TIER1 first (recall-safe 0.996); TIER2 animacy is additive but wants the
reader's own NER/lexical animacy (the +animacy recall dip to 0.989 is from an incomplete lexical noun-list — the live
reader's NER would recover it).**

## The exact diff for `hdlab/graded_coref_pick.py`

Append these (they compose with the existing `keep_after_pool_cleanup`; that stays):

```python
# ── Hard PHI-AGREEMENT pre-filter (person + animacy). Landed 2026-08-30 from the integrated problem
# `the_coref_residual_needs_a_discourse_focus_stack` (focus-STACK REFUTED; the residual is a candidate-SET-quality /
# hard-phi-agreement-violation problem). Person-feature agreement + animacy are OBLIGATORY constraints on anaphora
# (Benveniste 1966; Mancini et al. 2011; Cysouw 2003; McRae/Ferretti animacy). `_gn_compat` is PERMISSIVE (unknown
# passes) so it admits grammatically-impossible antecedents: the discourse PARTICIPANT ("I"/"we"/"you", the most
# salient entity, grabbed for every he/she) and animacy-mismatched entities (a place for "he"). Confirmed-incompatible
# ONLY -> recall-safe. Gender is deliberately NOT enforced (a causal non-lever: a freshly-named entity's gender is not
# yet established). spaCy-free. Additive / opt-in: a pre-filter the caller applies to its pool BEFORE
# graded_antecedent_pick; existing callers are byte-unchanged.

FIRST_SECOND_PERSON_EXT = FIRST_SECOND_PERSON | frozenset("thou thee thy thine mine ours yours".split())

def is_discourse_participant(prior_mention_heads):
    """REFINED (deployment-faithful) participant test: a cluster is the narrator/speaker -- ineligible as a
    3rd-person antecedent -- iff its PRIOR mention heads are >=50% 1st/2nd-person AND it has NO 3rd-person-pronoun
    mention. The 'no 3rd-person mention' clause is load-bearing: a talkative CHARACTER says 'I' in quotes but IS
    narrated in 3rd person ('he') -> keep; the true narrator is never a 3rd-person referent -> exclude. (Restores
    full-population recall 0.979->0.996 and removes a small 3rd-person-narration regression.)"""
    hs = [h.lower() for h in prior_mention_heads]
    if not hs:
        return False
    fs = sum(h in FIRST_SECOND_PERSON_EXT for h in hs)
    third = sum(h in THIRD_PERSON_PRON for h in hs)   # THIRD_PERSON_PRON already defined in this module
    return fs / len(hs) >= 0.5 and third == 0

def phi_agreement_keep(pronoun_low, candidate_prior_heads, candidate_animacy):
    """Indices to KEEP after the hard phi-agreement pre-filter, for a 3rd-person `pronoun_low`.
    candidate_prior_heads[i] = cluster i's PRIOR mention-head list; candidate_animacy[i] in
    {'animate','inanimate',None} from the reader's NER/lexical animacy (None = unknown -> kept, recall-safe).
    Drops: discourse participants (person feature); + confirmed-INANIMATE for he/she/him/her; + confirmed-ANIMATE
    for it/its. TIER1 = pass candidate_animacy all-None to get participant-only (recall-safe 0.996)."""
    person = pronoun_low in {"he", "she", "him", "her", "his", "himself", "herself"}
    itpro  = pronoun_low in {"it", "its", "itself"}
    keep = []
    for i, heads in enumerate(candidate_prior_heads):
        if is_discourse_participant(heads):
            continue
        a = candidate_animacy[i] if candidate_animacy else None
        if person and a == "inanimate":
            continue
        if itpro and a == "animate":
            continue
        keep.append(i)
    return keep or list(range(len(candidate_prior_heads)))   # never empty (recall floor)
```

## Wiring (in the coref caller that builds the pool for `graded_antecedent_pick`)

1. Build `candidate_prior_heads` (each candidate cluster's mention heads seen SO FAR) and `candidate_animacy` from the
   reader's entity model / NER (PER -> 'animate'; FAC/LOC/GPE/VEH/ORG or an inanimate common-noun head -> 'inanimate';
   else None). For TIER1 only, pass `candidate_animacy=None`.
2. `keep = phi_agreement_keep(pronoun_low, candidate_prior_heads, candidate_animacy)` (after `keep_after_pool_cleanup`).
3. Restrict `candidate_priors` to `keep`, call `graded_antecedent_pick`, map the returned index back through `keep`.

## Do NOT

- Do NOT add the focus STACK (REFUTED: a perfect-segment oracle adds 1/420 over finer token-locality).
- Do NOT add a POSITIVE gender-agreement cue (causal non-lever / leak; +0.010 NOT_SEP).
- Do NOT use the GLOBAL participant rule (>=50% with no 3rd-person clause) — it conflates a chatty character with the
  narrator and slightly regresses 3rd-person narration; use the refined `is_discourse_participant` above.

## Coordinate

Sequenced with the assembly reader-wiring (Changes 2-3) which also touch the coref path. Compose with the landed
`hdlab.state_of_mind.WorkingOverlay` (speaker/addressee attribution — the complementary direction).
Reverify: `.venv/Scripts/python.exe verification/test_coref_residual_focus_and_participant.py`.
