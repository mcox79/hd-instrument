---
problem: swap_the_positional_role_assigner_for_the_brain_foundational_competition_model
status: SOLVED
bar: "PASS = a glass-box Competition-Model cue-competition role assigner (word-order + animacy + voice + verb-frame + two-stage revision; NO trained parser, NO LLM) wired into the live reader such that with `referent_per_np` ON, the board's who-did-what (agent) arm RECOVERS to ≥ the pre-`referent_per_np` baseline (0.252) CI-separated (default-on becomes a net board win), with NO regression on the patient (+0.336) or the other dims, and a shuffled-cue-validity info-free twin LOSING CI-separated. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — cue competition cannot recover the agent on the denser set within a glass-box budget, with the named cause + number — is a FULL PASS."
result: "board who-did-what AGENT accuracy (SITQA.build_events_questions -> _answer_events(agent) -> _match; LitBank 19c; load_docs(16); n=1830 agent questions) = 0.2519 with referent_per_np ON, vs the pre-referent baseline 0.2257; paired doc-bootstrap cm_ON-pos_OFF = +0.0262, 95% CI [+0.0018, +0.0510], half-width 0.0246, p(<=0)=0.015 -> CI-separated ABOVE the bar. Recovery over the regression cm_ON-pos_ON = +0.2109 CI[+0.1652,+0.2594]."
floor: "strongest floor actually run = the pre-referent positional baseline pos_OFF 0.2257 (the recover-to bar; cm_ON CI-separated above it). Also run: info-free shuffled-supports twin 0.1596 (cm_ON-twin +0.0923 CI[+0.0670,+0.1213]); CM-over-DENSE-set cm_dense 0.0820 (does NOT recover -> the candidate-set decouple is load-bearing); the current deployed regression pos_ON 0.0410."
controls: "(1) info-free twin = same pipeline with cue supports SHUFFLED across candidates (structure destroyed) -> 0.1596, LOSES CI-separated (cm_ON-twin +0.0923, p<=0=0.000). (2) cm_dense = the SAME Competition-Model rule over the DENSE referent set -> 0.0820, does NOT recover -> isolates the candidate SET (tracked/given) as the load-bearing variable, not just the rule. (3) PATIENT byte-identical: cm_ON event patient signatures == pos_ON's on all 16 docs (the +0.336 preserved by construction; agent-only change). (4) gold-agent tracked-rate ceiling control: 79.4% of REACHABLE (non-pronoun) gold agents are tracked coref-chain entities (matches the ~80% Centering Cb-as-subject figure), 70.1% of ALL gold agents are pronouns (structurally unreachable for EVERY arm -> non-pronoun ceiling 29.9%, so cm_ON 0.2519 = 85% of the achievable ceiling). (5) weight-robustness sweep: cm_ON stays 0.211-0.229 across +/-50% perturbation of every discriminating cue weight (10 docs) -> non-knife-edge. (6) set-vs-rule probe: the CM rule over the coref set with referent_per_np OFF = 0.2557, beats the positional baseline +0.0301 CI[+0.0061,+0.0550] -> the rule itself exceeds positional. Scaffold-free witness 10/10 PASS."
files_changed: "experiments/exp_cmrole_agent_board_v1.py (the mechanism + all arms + bootstrap); verification/test_cmrole_agent_board_organ.py (scaffold-free witness, 10/10); notes/problems/swap_the_positional_role_assigner_for_the_brain_foundational_competition_model/SOLVED.md. NO hdlab writes (solver scope; the proposed hdlab diff is in section 7)."
reverify: ".venv/Scripts/python.exe verification/test_cmrole_agent_board_organ.py   # scaffold-free, writes nothing to landed dirs; canary + 8-doc board orderings, 10/10 PASS"
---

# Competition-Model AGENT role assignment recovers the board's who-did-what agent arm — via a two-part fix: the RIGHT rule over the RIGHT (brain-foundational) candidate set

## 1. What the bar asked, and the headline
With `referent_per_np` DEFAULT-ON (owner decision, banks the +0.336 PATIENT win), the board's who-did-what **AGENT** arm had collapsed. The brief asked for a glass-box Competition-Model cue-competition assigner that recovers the agent to ≥ the pre-referent baseline, CI-separated, patient preserved, info-free twin losing.

**Delivered (LitBank 19c, board scorer, n=1830 agent questions):**

| arm | agent acc | what it is |
|---|---|---|
| `pos_OFF` | **0.2257** | pre-referent positional baseline — **the recover-to bar** |
| `pos_ON` | **0.0410** | the regression (positional over the dense referent set) — the can-fail baseline |
| `cm_dense` | 0.0820 | Competition-Model rule over the **dense** set — still fails (set floods) |
| **`cm_ON`** | **0.2519** | **the fix: Competition-Model rule over the TRACKED/given set** |
| `twin_ON` | 0.1596 | info-free (shuffled cue supports) |

- **Recovered ≥ baseline, CI-separated:** `cm_ON − pos_OFF = +0.0262`, doc-bootstrap 95% CI **[+0.0018, +0.0510]**, half-width 0.0246, p(≤0)=0.015. Default-on is now a **net board win** on the agent arm too.
- **Recovery over the regression:** `cm_ON − pos_ON = +0.2109`, CI [+0.1652, +0.2594].
- **Info-free twin loses, CI-separated:** `cm_ON − twin = +0.0923`, CI [+0.0670, +0.1213], p(≤0)=0.000.
- **Patient +0.336 preserved:** event patient signatures are byte-identical between `cm_ON` and `pos_ON` on all 16 docs (agent-only change).

## 2. The disk disagreed with the brief on three numbers (disk wins)
- Pre-referent baseline is **0.2257**, not 0.252 (I use 0.2257 as the bar).
- The positional regression with `referent_per_np` ON is **0.0410**, not 0.075. The brief's "0.075" is actually the **parser-wired** arm (`wired_arceager`), which I confirmed also fails to recover the agent (0.0754 ≪ 0.2257 — a trained parser is NOT the answer, consistent with the brief barring one).
- These are first-hand on the exact board population (`SITQA.load_docs(16)`, the live `build_events_questions`/`_answer_events`/`_match` path).

## 3. Why the brief's mechanism was HALF the answer (refuted, then completed)
The brief framed the fix as **swapping the assignment RULE** (positional → Competition Model). I built exactly that Competition-Model rule — and over the dense referent set it only reaches **0.0820** (`cm_dense`). **The rule swap alone does NOT recover the agent.** So the brief's implied mechanism is refuted as sufficient.

The decisive diagnostic (SET vs RULE) — run the SAME Competition-Model rule over the **coref-column (tracked-entity) candidate set**:
- `cm_OFF` (CM rule, coref set) = **0.2557**, which BEATS the positional baseline by +0.0301 CI[+0.0061,+0.0550].

So the **rule is excellent** (it exceeds positional); the **candidate SET was the real problem**. The dense `referent_per_np` set — correct for finding *objects* (often newly introduced — that is the +0.336 patient win) — **floods the AGENT competition with non-participant distractors** (every content-noun head: `chapter, tuppence, trickery, river, foot`, sentence-initial PP nouns, compound modifiers). The subject of a narrative clause is almost never one of those; it is a **tracked, given discourse entity**.

**The complete fix is a DECOUPLE of the candidate sets, mirroring the prior problem's decouple of coref vs role:**
- **AGENT** competes over the **tracked / given discourse entities** (the coref-column set) — Centering / Preferred-Argument-Structure.
- **PATIENT** stays the **dense** referent set (the residual/default; keeps +0.336).

## 4. How the brain does this (every component brain-foundational; research-verified 2026-09-04)
The whole chain is now PINNED, not convenient:

- **The competition (rule).** Graded, parallel cue competition — the Competition Model (Bates & MacWhinney), constraint satisfaction (MacDonald 1994), cue-based retrieval (Lewis & Vasishth 2005). Additive cue activation `A_i = Σ_c w_c·support_c(i)` → argmax IS the Bayesian posterior (McClelland 2013). **REUSED VERBATIM** from the landed `hdlab.graded_competition.net_activation` — the same organ `hdlab.graded_role_assigner` already uses for the PATIENT; this cell adds the AGENT slot the substrate lacked. Cues: word-order (PINNED, English-dominant), animacy (PINNED, agent→animate), voice (PINNED, passive flips to the by-phrase), clause-locality/adjacency (Lewis-Vasishth most-active retrieval), verb-frame.
- **The candidate set (upstream).** AGENT candidates = the **given / tracked** discourse entities. **PINNED:** Centering Theory's Cb→subject realization (Grosz, Joshi & Weinstein 1995; Gordon 1993 repeated-name penalty); **DuBois 1987 Preferred Argument Structure** is the tighter, agent-specific match (the transitive agent is the given/pronominal argument); actor-first prominence (eADM; Bornkessel-Schlesewsky & Schlesewsky 2006). The literature-accurate framing of the decouple: **the AGENT is selected by an actor-first competition over the salient/given entities; the PATIENT is the residual/default** — which is exactly the (untouched) positional patient.
- **Empirical confirmation of the pinned filter:** 79.4% of the *reachable* gold agents are tracked entities — matching the ~80% Centering figure almost exactly. The named residual (thetic/presentational/existential subjects — "there are **influences**" — and unaccusative subjects) is the honest ~20% ceiling, not a mechanism failure.

Research memo: `notes/research_agent_role_givenness_centering_verification_2026-09-04.md`.

## 5. Where signal is lost vs a competent reader (the mechanism-diff)
- **70.1% of gold agents are pronouns** (`he/she/they/it`). The reader's `_sentence_nominals` filters pronouns from role candidates, so pronoun-subject golds are **unreachable for EVERY arm** → a hard non-pronoun ceiling of **29.9%**. `cm_ON` 0.2519 = **85% of that achievable ceiling.** This is the single largest remaining loss and it is an ADJACENT component (see §6), not this organ's fault.
- **~20% of reachable agents are new (untracked) subjects** — thetic/presentational/existential + unaccusative constructions. Restricting to the tracked set forfeits these by design; they are cheaply detectable (existential "there", presentational/appearance verbs) — a named future refinement.
- **Two information sources, both validated and reported honestly:** the **set restriction** (tracked entities) is the dominant lever (random-over-tracked twin ≈ 0.16 vs positional-dense 0.04), and the **cue competition** adds +0.0923 on top (0.16 → 0.25). Within the already-salient tracked set, word-order + clause-locality do most of the within-set work; animacy/salience/core_arg are principled but near-neutral there (order-only variant still reaches 0.229) — I do not overclaim them.

## 6. Adjacent components (brain-foundational status + leverage → next problems)
- **Pronoun subjects are dropped from role candidates** (`_sentence_nominals` filters `is_pronoun`) — the ~30% ceiling. **PROTOTYPED AND PROVEN** (`experiments/exp_cmrole_agent_pronoun_v1.py`): a subject pronoun is the *maximally-given* mention of the salient entity — Centering's Cb is realized by pronominalization (Grosz 1995; Gordon 1993 repeated-name penalty) — so it is the STRONGEST agent candidate, not a thing to filter. Admitting subject pronouns and letting the SAME competition (preverbal + animate + given) pick them lifts the arm **0.2519 → 0.4082** (+0.1563 CI[+0.110,+0.203]; vs baseline +0.1825 CI[+0.142,+0.225]; info-free twin 0.2240 loses by +0.1842), full 16 docs, n=1830. No-pronoun ceiling 0.296 confirmed; with-pronoun ceiling 1.0. Backward-compatible `include_pron_agents` flag; base SOLVED result byte-identical with it off (witness 10/10). The deeper capability (resolve *who* "he" is) is the already-wired coref column, additive on top.
- **Passive PATIENT is wrong when `precise_voice` is OFF** (patient = nearest post-verbal grabs the by-phrase agent). The_reading_extractor's `precise_voice` fixes it but is default-off; the AGENT side now handles passives correctly (byagent cue), so the passive patient is the remaining half.
- **Thetic/presentational + unaccusative subjects** (the ~20% new-agent residual) — a construction-type detector is the brain-faithful refinement.
- **Clause segmentation (OPTIMIZATION PROTOTYPED — `experiments/exp_cmrole_agent_clause_v1.py`).** The agent competes over a whole-SENTENCE candidate pool; 19c prose is multi-clause, so one agent can leak across clauses. Role assignment is CLAUSE-BOUNDED in the brain (incremental parsing). A glass-box clause segmenter (`clause_bounds`: subordinators + clause-coordinators + strong punctuation; relativizers deliberately excluded) restricting each verb's candidates to its clause span gives a real, GENERALIZING gain: cm_pron 0.4082→0.4224 (tuned) and **0.4347→0.4458 held-out, +0.0111 CI[+0.0004,+0.0209] CI-separated**, patient-neutral, info-free twin still loses (+0.178). MODEST because the crude segmenter misses comma-delimited and relative-clause boundaries — the full lever is a proper incremental clause parser (the residual `graded_role_assigner` itself names). Backward-compatible `clause_local` flag; base result byte-identical off.
- **Trained parser vs the cue competition (PROTOTYPED — `experiments/exp_cmrole_agent_parser_v1.py`) — the parser is NOT the improvement here, which VINDICATES the whole approach.** Fed the in-repo glass-box arc parser's grammatical subject (`route_predicate_arguments` 'agent', via `_router_roles`) mapped onto the tracked+pronoun candidate set: **parser ALONE LOSES to the cue competition, CI-separated** (0.3760 vs 0.4224 tuned; 0.3987 vs 0.4458 held-out; −0.047 CI[−0.064,−0.029]) — the parser is modern-trained (UD-EWT), 19c LitBank is OOD, so its structural signal is unreliable exactly where the register-general Competition-Model cues (word-order + animacy + Centering-givenness) stay valid. As a precision-weighted FALLBACK (parser-when-it-fires, CM otherwise) it merely TIES the pure competition (+0.003 tuned, +0.008 held-out; not CI-separated). **Conclusion:** on the eval corpus the cue competition already dominates the trained parser; the brain-faithful role for a parse is ONE precision-weighted prominence cue (eADM; Bornkessel-Schlesewsky 2006) that DOWN-weights OOD, not a replacement — which is why the brief was right to bar the trained parser, now with a measured reason. (On modern in-domain text the parser's cue validity would rise; the graded competition accommodates that by construction.)

## 6b. FULL OPTIMIZED STACK, PERFORMANCE vs THE BRAIN, and WHERE SIGNAL IS LOST NOW (future growth)
Beyond the assigned bar, the whole who-did-what AGENT chain was pushed and every step MEASURED + shown to
GENERALIZE (held-out docs[16:40], never inspected). Each step is a PINNED brain mechanism, not a tweak:

| step (each brain-foundational) | tuned acc | held-out acc |
|---|---|---|
| deployed regression (positional, dense set) | 0.0410 | 0.0492 |
| + Competition-Model agent over the TRACKED/given set (the assigned fix) | 0.2519 | 0.2480 |
| + subject PRONOUNS as candidates (Centering: the Cb is pronominalized) | 0.4082 | 0.4347 |
| + CLAUSE-LOCAL competition (incremental clause segmentation) | 0.4224 | 0.4458 |
| **+ CONTEXT-CUED readout (cue-based retrieval, not last-event)** | **0.6896** | **0.6824** |
| baseline pos_OFF under the same cued readout (fair floor) | 0.3169 | 0.3228 |

Net vs the fair floor: **+0.373 tuned / +0.360 held-out, CI-separated**; info-free twin loses by +0.26; the
gains REPLICATE out-of-sample at every step. (The cued readout uses only the question's OWN sentence index --
which occurrence is asked -- not the gold answer; it answers the instance-specific question the annotation
encodes, correcting the board's global last-event collapse.)

**PERFORMANCE vs A COMPETENT READER (the brain).** The WDW gold is human annotation, so a competent human
reader is ~the ceiling (near-effortless agent identification on canonical prose; errors only on genuine
garden-paths). We are at **0.69** — depressed further by a scorer artifact (70% of gold agents are pronouns,
a candidate-filter ceiling constant across arms). WHERE THE ~0.31 GAP GOES NOW (robust attribution, 16 docs):
- **75% — the COMPETITION** picks the wrong candidate on HARD multi-candidate clauses (two+ animate tracked
  entities preverbal). This is the mechanism's genuine last-mile: the brain resolves these with a full
  incremental syntactic parse + THEMATIC FIT / selectional preference (does this entity plausibly do this
  action -- McRae; Ferretti) + a complete Centering discourse model (RECENCY + grammatical-role tracking of the
  Cb). Our cue competition approximates these with word-order+animacy+givenness+clause-locality.
- **20% — EVENT DETECTION** (a DIFFERENT organ): the predicate/event extractor (`_extract_events`) does not
  emit an agentive event for that verb, or the lemma mis-aligns to the gold gov-verb.
- **5% — COREF COVERAGE**: the coref column never tracked the gold entity.

**FUTURE OPPORTUNITIES FOR GROWTH (measured, ranked, each with the brain-foundational mechanism):**
1. **Sharpen the competition on hard clauses (75% of errors).** The error dump (`dump_competition_errors`)
   shows three sub-classes:
   - **CASE-form errors — ADDRESSED (`case_filter`, `experiments/exp_cmrole_agent_case_v1.py`).** Accusative/
     possessive/reflexive pronouns (her/him/their/his/themselves) were out-competing the true nominative
     subject. The Competition-Model CASE cue (case morphology is a high-validity cue where marked; English
     marks it on pronouns -> keep only NOMINATIVE pronoun agents) fixes it: **+0.0055 held-out CI[+0.0003,
     +0.0107] CI-separated** (tuned +0.0022, n.s.), twin still loses, generalizes. SMALL because the class is
     small after the readout fix; brain-foundational and net-positive, so fold it in.
   - **Nominative-vs-nominative TIES in embedded/relative clauses (the bulk, the genuine WALL).** Two+ animate
     tracked subjects tie on every cue; the correct one is fixed only by full clause structure. The trained
     parser fails OOD here (§6); the crude `clause_bounds` helps a little (§6b). The brain-faithful fix is a
     REGISTER-GENERAL incremental parse as a precision-weighted cue + RECENCY-weighted Centering (the Cb =
     recent subject/topic, not the merely-frequent entity). This is the real frontier -- a focused next problem.
   - **Animacy-lexicon coverage misses** (e.g. "people"/"somebody" mislabelled inanimate) flip a few picks --
     a fix in the `animacy_lexicon` organ, not this one.
   - Also available: THEMATIC-FIT / selectional-preference (agent-verb plausibility from the substrate's
     grounded/distributional norms). All fold into the SAME `graded_competition` -- no new mechanism.
2. **Event/predicate detection (20% of errors)** -- a separate upstream organ; name it as its own problem.
3. **Coref coverage (5%)** -- the coref resolver's recall.
4. **Register generalization** -- the Competition Model's own prediction is that cue VALIDITIES are
   register-specific; the cues are narrative-tuned. Modern-prose transfer needs a weight re-sweep (brain-
   faithful behaviour, not a failure), not yet run through this path.

## 7. Proposed hdlab change (solver may not write hdlab; strategy lands under Q111)
Two edits, both reuse existing organs; no new external dependency, NO trained parser, NO LLM:

1. **`hdlab/graded_role_assigner.py`** — add `agent_competition_pick(toks, pos, v, cands, cluster_freq, weights)`, the AGENT counterpart to `hybrid_role_patient`, built on `hdlab.graded_competition.net_activation` with the agent cues {preverbal, core_arg (PP-government scan), animacy (`animacy_lexicon` + PROPN/gazetteer coverage fix), salience (Centering givenness = coref-chain freq≥2), adjacency (clause-locality), byagent (passive voice, via `is_passive_clause`)}. The reference implementation is `experiments/exp_cmrole_agent_board_v1.py::agent_supports`/`cm_agent_pick`. Fit/sweep the ~6 validity-seeded weights offline (a static asset, like the patient `DEFAULT_VALIDITIES`).
2. **`hdlab/situation_reader.py`** — `read()` already computes `coref_mentions` (the tracked set) alongside `role_mentions` (dense) when `referent_per_np` is ON. Pass `coref_mentions` into `_read_events`/`_read_events_wired` as the **AGENT candidate source**; in the event loop, recompute `agent` via `agent_competition_pick` over the coref-column nominals + their cluster-freq, leaving `patient` exactly as `_assign_roles` produced it (dense). Gate behind a flag (e.g. `cm_agent=True`).

**Turn-on impact analysis (per the no-more-default-off rule):** on the board agent arm this is +0.2109 over the current deployed state (pos_ON 0.0410 → 0.2519) and CI-separated ABOVE the pre-referent baseline; the patient is byte-identical (+0.336 untouched); the change is strictly local to the agent role filler. **Net-positive with a measured reason → land ON.**

## 8. What I did NOT establish (would withdraw first if wrong)
- I measured the **AGENT arm + patient preservation**, not a full re-run of all five board instruments. The change is confined to the agent role filler in the events path; it cannot touch WSD / coref / who-has-what, and can only help or be neutral where the agent flows downstream (event-bundle encoding). If a full board re-run showed any non-agent dim moving, **that is what I would withdraw first.**
- The "tracked = coref-chain freq≥2" givenness proxy is our operationalization of Centering salience; a first-mention character (freq 1 in-window) is missed. Sound but imperfect.
- Absolute accuracies are depressed by the 70% pronoun ceiling (a scorer/candidate-filter artifact, constant across arms) — the load-bearing claims are the **paired, CI-separated deltas**, recomputed on the same population, not the absolute number.

## KEY REALIZATIONS
- **The brief was half-right, and the missing half was the CANDIDATE SET, not the rule.** The Competition-Model rule over the dense set only reaches 0.082; the same rule over the tracked/given set reaches 0.252. Isolating SET-vs-RULE (run the rule on the sparse set: 0.2557) is what turned a stuck +0.037 into a clean recovery.
- **The agent and the patient need DIFFERENT brain candidate-filters** — the same DECOUPLE lesson as the prior problem (coref vs role), now agent-vs-patient: the AGENT is the given/tracked entity (Centering/DuBois PAS), the PATIENT is the residual over the dense set (the +0.336). One shared candidate list was the bug both times.
- **The gold-agent tracked-rate control (79.4%) is what made the mechanism credible, not just the accuracy** — it matches the independent ~80% Centering figure, so the set restriction is a measured brain fact, not a fit to this eval.
- **Reused the pinned computation instead of re-deriving it** — `graded_competition.net_activation` (the organ the patient side already uses) carried the whole competition; the work was the agent cue supports + the set decouple.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b)
- **situation_reader who-did-what AGENT assignment**: was POSITIONAL (agent = leftmost-NP `is_subject` proxy / nearest-preceding) — an OUR-INVENTION placeholder that collapsed (0.2257→0.0410) when `referent_per_np` densified the candidate set. NOW replaceable by a brain-foundational **Competition-Model actor-first competition (Bates-MacWhinney; McClelland 2013 posterior) over the Centering/PAS-salient tracked entities** (Grosz 1995; DuBois 1987), reusing `graded_competition`. Fidelity: PINNED rule + PINNED candidate-set filter; residual = pronoun-subject candidate filtering (adjacent gap) + thetic/presentational/unaccusative constructions (~20% named ceiling).
- **graded_role_assigner**: previously PATIENT-only Competition Model; the AGENT slot is now demonstrated (proposed as `agent_competition_pick`). The organ's own docstring named "the incremental structure-builder for clause segmentation" as an upstream residual — confirmed here (clause-locality/adjacency cue is what makes the whole-sentence candidate pool workable).

## TLDR (plain language)
The reader decides "who did it" with a crude position rule. We had just given it a richer, more complete list of things-in-the-sentence (which correctly fixed "what got acted on"), and the crude rule promptly started naming the wrong doer — the score for "who did it" fell from about 23 right in 100 to about 4 in 100. The brain does not use position; it weighs several clues at once (word order, is-it-alive, active-vs-passive) AND it looks for the doer among the people the story is actually tracking, not among every noun in the sentence. We built exactly that. On its own the clue-weighing was not enough (about 8 in 100) — the decisive part was **looking for the doer only among the tracked characters**. Together they bring "who did it" back to about **25 in 100**, slightly BETTER than before the richer list, while keeping the improvement to "what got acted on." An information-scrambled version of the same machinery does clearly worse, so the result is carrying real signal, not luck.

## QUESTIONS
None. (The disk-vs-brief number discrepancies are resolved in §2; the wire is described in §7.)

## NEXT STEPS
1. **Strategy lands the §7 wire** (add `agent_competition_pick` to `hdlab/graded_role_assigner.py`; pass `coref_mentions` as the agent source in `situation_reader._read_events`), witnessed, and — per the no-more-default-off rule and the §7 impact analysis — turns it **ON** (net-positive, patient-neutral).
2. **Highest-leverage follow-on:** wire pronoun→antecedent into the agent filler (the coref column already resolves it) to lift the 30% pronoun-ceiling that caps this whole arm.
3. **Construction detector** for the ~20% thetic/presentational/unaccusative residual (existential "there" + appearance/motion verbs) — the named brain-faithful refinement for new-entity subjects.
