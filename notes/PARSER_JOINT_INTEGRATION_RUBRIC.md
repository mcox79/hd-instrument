# PARSER JOINT-INTEGRATION RUBRIC — one parser optimized for ALL consumers, not a sum of piecemeal landings

**Why this exists (owner, 2026-09-05):** several of the in-flight submissions carry individual improvements / *replacements* to the parser. The parser is a shared, multi-consumer, load-bearing component whose fixes **do not transfer** (a change that helps one consumer has repeatedly regressed another). So parser changes are integrated as ONE jointly-optimized parser, not landed one at a time. This rubric is the scoring frame: the consumer matrix, the known transfer-conflicts, a slot per submission, and the joint-build protocol. It is the **parser tier** of the top-down integration pass (`notes/INTEGRATION_PASS_PLAN.md`).

**Workflow (do NOT front-run):** submissions arrive staggered; as each parser-touching one lands owner-DONE I reverify + grade + **stage** it into a Submission slot below (its change, claimed gain + instrument, per-consumer help/hurt). I **hold all live-parser wiring** until the last parser-relevant submission is staged, then run the JOINT-BUILD PROTOCOL once. Non-parser parts of each submission integrate independently.

---

## 1. The parser MODULES (disk-verified 2026-09-05)
| module | role | live status |
|---|---|---|
| `hdlab/arc_parser.py` | the shared frontend ARC-FACTORED parser (produces heads); vectorized + memoized fast path, byte-identical | LIVE default (`_cached_parse_heads` / `_frontend_parser`) |
| `hdlab/arceager_parser.py` | the opt-in improved parser (UD-EWT UAS 0.775→0.842 modern); `parse_with_conf` | LIVE behind `parser_arceager` DEFAULT-ON (routes the WIRED parse) |
| `hdlab/arc_labeler.py` | grammatical-relation LABELS (obj/nsubj:pass/obl…); has a graded readout (entropy AUC 0.93) | LIVE (lazy `ArcLabeler`); fast-path land-ready (OPEN) |
| `hdlab/incremental_parser.py` | left-corner incremental SUBJECT bind — one precision-weighted cue for agent ties | LIVE behind `cm_agent_struct` default-on (precision-only cue) |
| `verb_subcat.py` / `verb_subcat_frames.py` | VALENCY / complement-vs-adjunct subcat frames | LIVE (patient valency gate; goal bare-purpose) |
| `typed_rule_parser.py` / `semantic_parser.py` / `thematic_role_labeler.py` | typed/semantic parse + role labeler (islanded/partial) | mostly LATENT — candidates for the joint design |

## 2. The CONSUMER MATRIX — every live reader function that reads the parse (heads/labels/distribution)
The joint parser must **no-regress every row** (or route the conflict per-register/per-consumer). Each row's instrument is how we measure it off-vs-on.

| # | Consumer (need) | Reads | Live function | Current → ceiling | No-regress instrument |
|---|---|---|---|---|---|
| 1 | who-did-what **PATIENT** | heads + labels (obj/nsubj:pass) + voice + valency | `predicate_argument_frontend.structural_patient_pick` | 0.779–0.831 → 0.913 (clean UD) | `exp_board_patient_slot_v1` (built) / `exp_valency_labeled_patient_v1` |
| 2 | who-did-what **AGENT** | heads (subject) + incremental subject cue for ties | `graded_role_assigner.agent_competition_pick` + `incremental_parser` | board agent ~0.61–0.69; tie slice 0.67–0.71 | board `events` agent arm (`exp_situation_model_qa_v1`) |
| 3 | **world-state / relational** (who-has-what) | obl / PP-role attachment | `_read_world_state` / possessor binding | (PP-roles help here) | world-state QA arm |
| 4 | **SPACE / location** | obl / PP head attachment | `_space_reader` | 0.69 live → 1.0 gold | board `location` arm |
| 5 | copular **STATE** (is-a) | heads + labels (cop/nsubj) | `_read_entity_states` + `copular_binding` (re-parses via `_cached_parse_heads`+`ArcLabeler`) | 0.71 → 0.83 (robust_cop); arc-eager +0.032 modern | board `state` arm (UD-EWT gold) |
| 6 | **GOALS** (bare-purpose) | subcat frame + advcl-vs-xcomp attachment | `_read_goals` + `verb_subcat_frames` | parse-gated 0.33 vs oracle | board `goal` arm |
| 7 | the **GRADED organs** | the parse DISTRIBUTION / posterior, NOT the 1-best | arc-labeler graded readout; graded POS posterior | entropy flags errors AUC 0.93 (unwired) | per-organ (labeler entropy; CRF posterior) |
| 8 | **register robustness** | the whole parse on 19c vs modern | all of the above on 19c LitBank vs modern UD | arceager +modern / −19c | 19c-vs-modern split on every arm above |
| 9 | (cross-cut) **recall vs precision** | candidate SET width vs the cue-based streams | role binding is a separate cue stream (Frankland-Greene) | hard-restrict to incremental set HURTS | patient/agent arms with restricted vs open candidate set |

## 3. The KNOWN TRANSFER-CONFLICTS — the constraints the joint parser must satisfy
These are measured, not hypothetical — they are exactly why joint > piecemeal.
- **C1 — PP/obl-role vs patient:** richer PP/obl-role attachment **helped world-state (3) but HURT patient (1) −0.051**. → the joint parser must route obl-role richness so it doesn't perturb the obj/nsubj:pass patient slot (per-role, not global).
- **C2 — arc-eager register split:** arc-eager is **+modern UAS/copular (+0.032) but −19c**; the reader eval includes 19c LitBank. → per-REGISTER routing (19c = the July/arc-factored tree, modern = arc-eager) unless a submission makes arc-eager register-safe.
- **C3 — store gate:** a knowledge/store gate **helped broken-parse items but hurt correct-parse items**. → gate on a parse-confidence signal, not globally.
- **C4 — 1-best vs distribution:** the graded organs (7) need the posterior; a 1-best-only improvement leaves them unfed even if UAS rises. → preserve/emit the distribution.
- **C5 — candidate-set width:** hard-restricting role candidates to the incremental parser's bounded set **HURTS** role binding (role binding is a separate cue-based stream). → the incremental parser stays a precision-weighted CUE, never a hard filter.
- **C6 — replacement vs improvement:** a submission that REPLACES the parser may subsume another's improvement OR require it ported on. → judge subsumption explicitly; port the orthogonal win onto the chosen base.

## 4. SUBMISSION SLOTS — fill as each parser-touching submission lands owner-DONE (staged, NOT wired)
For each: reverify first-hand, then record. `helps`/`hurts` = which consumer rows (§2) it moves, with the number + instrument.

| Submission (slug) | Change type | What it changes (module / decode / labels / REPLACEMENT) | Claimed gain + instrument | Helps (row:Δ) | Hurts (row:Δ) | Conflicts w/ | Disposition |
|---|---|---|---|---|---|---|---|
| `add_the_arc_labeler_fast_scoring_path` (arc-labeler LANDED; parser part D-O) | DIAGNOSIS + exploration (no replacement to wire) | arc-labeler fast path (LANDED, byte-identical); arc-eager analysis; self-sup DMV/online learner; whiten fix | arc-eager overall UAS +0.045 (0.79→0.84) / oracle-union 0.854; self-sup 0.38-0.45 (far below supervised 0.84); whiten flips grounding control +0.020 | long-range attach (parser +0.15/+0.18 dist 6-10/11+); left-headed +0.076; general-front-end flip → entity_states (row 5) | **obl:agent −0.147** (row 2 passive-agent), **det −0.019** (frequent), appos −0.035 | C2 (arc-eager 19c-neg), C1/C4 (obl:agent), C6 (self-sup vs supervised base) | **No wholesale replacement to wire.** Candidate: flip dormant arc-eager for the GENERAL front-end parser (+0.05 free, byte-safe, but LOW-leverage — only entity_states; who-did-what path already uses arc-eager) → confidence-gate/per-register in the joint build. Confidence-hybrid = **located negative** (no rule beats arc-eager). Self-sup parser = the north-star base (filed follow-on), not deployable now (regresses entity_states ~40% at 0.42 UAS). Ranked fixes for the joint parser: (1) feed DISTRIBUTED contextual reps into the parser (−0.083 SOTA gap, tractable, glass-box); (2) complete the DMV valence/lexicalization; (3) grounded meaning into ROLE competition (non-canonical, not the skeleton); (4) the arc-eager general-front-end flip. |
| _(slot 2 — pending)_ | | | | | | | |
| _(slot 3 — pending)_ | | | | | | | |
| _(slot 4 — pending)_ | | | | | | | |

**INPUT to the joint build (from slot 1's D-O exploration, disk-measured):** the true-ideal parser is **register-general + graded-with-revision** (a retrain, out of a reuse-only scope) that fixes arc-eager's `obl:agent`/`det` pockets; a modern-trained SOTA parser LOSES on 19c (barred). The dominant chain leak is the PARSER (−21% heads even with gold tags; obl:agent LAS 0.0588). Meaning's locus is ROLE on non-canonical clauses (grounded 0.43 vs positional 0.00), NOT the attachment skeleton (4× confirmed grounded ties its scrambled control on UAS). These are the constraints the combined parser is optimized against.

**Disposition vocabulary:** `adopt-global` (net-positive on every consumer) · `per-register-route` (C2) · `per-role-route` (C1) · `confidence-gate` (C3) · `distribution-preserving` (C4) · `precision-cue-only` (C5) · `port-onto-replacement` (C6) · `reject` (a located negative / dominated by another submission).

## 5. JOINT-BUILD PROTOCOL (run once, when all parser submissions are staged)
1. **Reverify** each staged submission first-hand; fill its slot (§4) with the measured per-consumer help/hurt on each row's instrument (§2).
2. **Build the consumer × submission impact matrix** — for every (submission, consumer) cell, the measured Δ. This exposes subsumption (C6) and conflicts (C1–C5).
3. **Choose the base** — a replacement submission if it dominates; else the current arc/arc-eager stack. Port orthogonal wins onto the base.
4. **Resolve each conflict by ROUTING, not compromise** — per-register (C2), per-role (C1), confidence-gate (C3), distribution-preserving decode (C4), precision-cue (C5). Never accept a global change that regresses a consumer when routing can avoid it.
5. **Assemble ONE parser** and measure it against **every** consumer row (§2) on both registers (§2 row 8) — the acceptance bar is **no consumer regresses**, or a named, measured routing reason. Preserve byte-identity where a submission claimed it (speedups).
6. **Land as one unit** (Q111), one commit, then a **fresh full board** to confirm the net-positive aggregate. Fold an `AUDIT UPDATE` into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b describing the joint parser + its routing decisions. Update the INTEGRATION_LEDGER rows for each folded submission (claimed → realized).

## 6. MEASUREMENT HARNESS (ready now)
- Patient (row 1): `experiments/exp_board_patient_slot_v1.py` (built + witnessed) + `exp_valency_labeled_patient_v1` (the R0→R_final ladder + twins + gold ceiling, both parsers).
- Agent (row 2), world-state (3), location (4), state (5), goal (6): the board arms in `experiments/exp_situation_model_qa_v1.py` (run off-vs-on).
- UAS / attachment: the parser eval on UD-EWT (`ArcParser.eval_uas` / `arceager_parser`).
- Register (row 8): every arm split 19c LitBank vs modern UD-EWT.
- Graded (row 7): arc-labeler entropy AUC; CRF POS posterior (`crf_tagger`, latent).
- **The rule:** one instrument per consumer, run off-vs-on for each candidate parser combination; no number crosses consumers/populations.
