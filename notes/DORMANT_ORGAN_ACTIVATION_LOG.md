# DORMANT-ORGAN ACTIVATION LOG

> **Owner directive 2026-09-03:** apply the flag-flip treatment to every dormant/"vestigial" organ — DEEP-DIVE
> (what it does in the BRAIN + who its consumers/would-be-consumers are) → REFURBISH to the current substrate →
> WIRE default-off → EVALUATE downstream on the RIGHT instrument → keep net-positives / name located-negatives.
> "Vestigial" = dormant-unwired, NOT dead. An older organ may be built against an outdated reader/parser and a
> consumer may never have considered its importance. Method: `feedback_dormant_organ_activation...` memory +
> the DORMANT-ORGAN ACTIVATION CYCLE. Enumerate islands via `tools/wiring_debt.py` (~116 island-only organs).

---

## #1 — `verb_role_exemplar_selector` (VerbRoleExemplarSelector) — ✅ ACTIVATION NET-POSITIVE (wire owed)

**Deep dive.** BRAIN: verb-specific SELECTIONAL PREFERENCE / thematic fit stored as an EXEMPLAR (instance)
distribution, NOT a centroid (McRae et al. 1998; Elman 2009; the eADM) — "which candidate is the right patient
*for this verb*," read out by NEAREST grounded exemplar (k-NN=1 / Chamfer max over the verb's attested OBJ fillers;
store `data/selectional_preferences_v1/selectional_slots_v1.pkl`, 14.7MB offline UD-parsed asset; grounded via the
wired `hdlab.grounded_similarity`). CONSUMERS: the reader's patient-selection tie-break — and the key point (owner's
"may not have considered its importance"): the live reader's patient pick (`route_predicate_arguments` /
`graded_role_assigner.competition_pick`/`hybrid_role_patient`) does NOT use verb-specific thematic fit for
SELECTION at all — only `predict_surprisal` uses a coarse grounded centroid *post-hoc* as an N400 error flag. So
this organ is a genuinely NEW selection signal the consumer under-uses.

**Reverify (functions):** eat→apple, read→book, drive→car, drink→water (not the distractors). Works.

**Evaluate downstream** (`exp_verbrole_exemplar_integrated_v1`, construction-conditional cue weighting — Competition
Model/Bates & MacWhinney: `score(c)=beta_pos(construction)·log_softmax(position)+beta_sel·log_softmax(exemplar_fit)`,
word-order weight COLLAPSES on non-canonical/archaic constructions; GOLD-BLIND canonicity from the parse):

| population | live reader WIRED | INTEGRATED | vs WIRED | verb-shuffled twin |
|---|---|---|---|---|
| **Modern QA-SRL** | 0.4808 | **0.5046** | **+0.0237 CI[+0.0040,+0.0431]** ✓ | +0.0164 (twin LOSES ✓) |
| **19c LitBank** | 0.1852 | **0.4029** | **+0.2177 CI[+0.2050,+0.2302]** ✓ | −0.0030 (twin TIES) |

**Honest read (two distinct wins):**
1. **Modern** — the verb-specific exemplar store does REAL work (beats WIRED +0.024 CI-sep AND beats its own
   verb-shuffled twin). The dormant organ delivers on its right corpus.
2. **19c** — a HUGE +0.22 over the live reader, but the twin TIES → on old prose the gain is NOT the verb store, it
   is the CONSTRUCTION-CONDITIONAL INTEGRATION mechanism itself. STRUCTURAL FINDING (a consumer blind spot surfaced
   by the activation): **the live reader's patient pick over-trusts WORD ORDER** (WIRED only 0.185 on 19c);
   down-weighting order on non-canonical/archaic constructions lifts it to 0.403. The register-native verb store is
   its own (already-filed) problem.

**WIRE OWED (default-off, Q111):** promote the construction-conditional integration (position × exemplar with
canonicity-gated beta) to hdlab + a default-off flag on the reader's patient path, byte-faithful to the validated
INTEGRATED arm; lazy-load the store + grounded space when on. Delivers: modern (verb store) + 19c (order-weighting).
Witness: default-off byte-identical + flag-on == INTEGRATED byte-for-byte + twin loses (modern). NOT the register-
native 19c store (separate problem). This is the FIRST proof the dormant-organ activation method yields a measured
downstream gain + a structural insight — exactly the owner's thesis.
