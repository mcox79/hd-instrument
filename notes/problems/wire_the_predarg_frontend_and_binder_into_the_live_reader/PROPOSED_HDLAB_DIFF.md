# PROPOSED hdlab DIFF (strategy lands it, Q111) -- route the live reader's role path through a parse ->
# the event-semantic router (+ quotative inversion) -> the graded binder, with a good-enough positional fallback

Solver builds+validates in `experiments/` + `verification/`; **strategy is the sole writer of `hdlab/`.** This
file states EXACTLY what would change and why. THREE changes; all ADDITIVE / default byte-identical.

The measured effect (57 McGuffey passages, 178 target-role queries, the prior negative's inherited end-to-end
instrument): the wired role path lifts family-grain end-to-end role accuracy **0.517 -> 0.742 (+0.225 CI-sep
[+0.150,+0.303])**; exact-grain **0.483 -> 0.702**; info-free role twin loses CI-sep; regression 6/92 (6.5%).

---

## Change 1 -- `hdlab/predicate_argument_frontend.py`: add QUOTATIVE-INVERSION agent handling to the router

**Why (the biggest single lever, +0.253 CI-sep on real narrative):** the router's agent rule is
`agent_idx = before[-1]` (nearest nominal BEFORE the verb) with passive handling only. On narrative dialogue --
"said Fred", "exclaimed papa", "answered Joe" -- the speaker (the AGENT) is POSTVERBAL, so the rule brands the
speaker the OBJECT/theme. The router ALREADY computes the COMM VerbNet class (it uses it for recipient routing)
but does NOT use it to fix the AGENT. This is a real fidelity gap. Quotative inversion is the frame semantics of
communication verbs (FrameNet Statement; VerbNet say-37.7; Goldberg 1995 construction grammar) + animacy
proto-agent prominence (eADM, Bornkessel-Schlesewsky & Schlesewsky 2006, Psych Review 113:787, PMID 17014303) --
PINNED-in-principle (the exact positional mechanism is OUR-INVENTION-UNDER-TEST; no ERP isolates "said Mary").

```python
# in route_predicate_arguments(...), after computing `lemma`, `vclasses`, and before/around agent selection:
def _is_speech_verb(lemma):
    return ("COMM" in get_event_classes(lemma)) or (lemma in SPEECH_VERBS)   # VerbNet COMM OR curated set

# quotative inversion: for a speech/COMM verb, the AGENT is the nearest ANIMATE nominal OUTSIDE quotes,
# preferring POSTVERBAL ('said Fred') then preverbal; the quoted content is NOT a role filler.
if _is_speech_verb(lemma):
    sp = _quotative_speaker(tokens, upos, v)     # postverbal-first animate scan, quote-masked
    if sp is not None:
        agent_idx = sp
        theme_idx = None                          # drop the quote content as a spurious theme
```

`_quotative_speaker` + `_quote_mask` + `_is_animate_head` are validated in
`experiments/exp_wire_predarg_binder_live_reader_v1.py` (reusing the prior negative's speech-verb + animacy
pieces, and there is prior on-disk validation: `exp_quotative_speaker_attribution_stack_break050_v1` HARD_PASS).
`SPEECH_VERBS` is a small curated set covering archaic verbs VerbNet misses (exclaim/murmur/...); the COMM class
is the glass-box static-asset primary cue. NO external LLM.

## Change 2 -- `hdlab/situation_reader.py`: a `route="predarg"` option on the role path (a parse -> router -> binder)

**Why:** `_read_events` assigns roles via `_assign_roles` (positional agent/patient, NO parse). Add an OPTIONAL
role route that supplies a parse and routes through the landed router. Default `route="positional"` is
byte-identical to today.

```python
class SituationReader:
    def __init__(self, *, role_route="positional", frontend=None, ...):   # NEW: role_route + a parse frontend
        # role_route in {"positional" (default, byte-identical), "predarg" (parse -> router -> binder),
        #                "hybrid" (predarg where the parser gives structure, positional fallback else)}
        self.role_route = role_route
        # frontend = hdlab.candidate_generator.CandidateGenerator.load(POS_ASSET, ARC_ASSET) -- the SAME
        # persisted UPOS tagger + hashed arc parser the router was validated on (data/frontend_assets/).
        self.frontend = frontend

    # in _read_events, per clause, when role_route != "positional":
    #   cand = self.frontend.generate(clause_text)          # tokens, upos, heads (a real parse)
    #   for each matrix verb: roles = route_predicate_arguments(cand.tokens, cand.pos, cand.heads, v)
    #       -> emit (head, thematic_role) for agent/theme/goal/recipient/... (richer than agent/patient)
    #   resolve pronoun heads via the graded binder (Change 3); named heads by the existing coref backbone
    #   HYBRID: if a clause yields no router binding for an entity (copula/AUX-only, no-verb), fall back to
    #           the positional _assign_roles for that clause (Ferreira good-enough dual-route -- PINNED).
```

**Notes for the lander (measured):**
- The **HYBRID route is the recommended default when the option is turned on**: it keeps the full +0.225 lift
  AND halves the regression (12->6 of 92) by using the positional rule only where the parser leaves a clause
  structureless. This is the brain-faithful good-enough fallback (Ferreira 2003 Cog Psych 47:164; Ferreira &
  Patson 2007; noisy-channel Levy 2008 / Gibson 2013 PNAS 110:8051), and PROBLEM.md sec.3 pins it.
- The richer inventory is real per-role: GOAL 0.00->1.00, RECIPIENT 0.00->0.50, and (with the already-wired
  frame labeler) EXPERIENCER 0.00->0.38 -- roles the positional agent/patient front-end structurally cannot emit.
- **Parse source = the persisted `data/frontend_assets/{pos_tagger_ud_ewt_upos.json, arc_parser_hashed_ud_ewt.npz}`**
  (CandidateGenerator). CITED modern ceiling UAS 0.7868 (exp_depparse_hashed_cpu_v1). McGuffey g2-g6 parses
  confidently (mean arc margin 14.2, 6.9% low-confidence, 2.1% no-verb clauses); the archaic-prose parse-quality
  lift is the sibling p8 (`role_assignment_is_untested_on_archaic_literary_prose`), NOT this wiring.
- SWEEP (OUR-INVENTION, do not adopt): the parse source and the abstain/fallback policy (the hybrid gate).

## Change 3 -- wire the graded binder for pronoun -> entity resolution (who-did-what)

**Why:** on a pronoun head with >1 gender-compatible antecedent, resolve via
`hdlab.graded_coref_pick.graded_antecedent_pick` over the causally-accumulated (clause, gram-role) histories
(Lewis & Vasishth 2005 ACT-R cue retrieval; Centering Cb) -- replacing the recency/positional pick.

```python
# for a pronoun head with candidate antecedents (gn-compatible, already-introduced):
res = graded_antecedent_pick([ent_hist[c] for c in cands_with_history], clause_idx, pron_role=gram_role)
pick = cands_with_history[res["pick"]]      # bind the pronoun to the graded winner
```

**HONEST measurement-population caveat (do NOT claim a McGuffey who-did-what lift):** the binder is genuinely
EXERCISED on McGuffey (147 items, 70% of ambiguous), but it does NOT move the McGuffey ROLE-accuracy number
(random-BIND twin TIES the graded binder, +0.000 NOT_SEP). Reason: the role label is PARSE-derived, and the
metric's majority-agent fallback masks binding errors -- so this instrument cannot see binding quality. The
binder's who-did-what value is established on its OWN population, LitBank: **+0.083 live / +0.136 re-instrumented,
CI-separated, random twin loses** (the landed `pronoun_to_event_binding_caps_who_did_what`, do not re-derive).
So: WIRE the binder (it is the right mechanism and composes cleanly) but MEASURE its who-did-what lift on
LitBank, not on the McGuffey role instrument.

**No change to `hdlab/graded_coref_pick.py` or `hdlab/candidate_generator.py`** (composed as-is).
