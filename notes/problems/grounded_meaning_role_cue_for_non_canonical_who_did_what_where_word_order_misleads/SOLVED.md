---
problem: grounded_meaning_role_cue_for_non_canonical_who_did_what_where_word_order_misleads
status: SOLVED
bar: "PASS = a whitened grounded selectional-fit role cue, self-gated by word-order cue validity (fires on non-canonical/passive clauses), landed into the live `graded_role_assigner` competition, lifting the LIVE who-did-what AGENT arm on the non-canonical slice CI-separated over the current reader, with a verb-shuffled/scrambled-meaning info-free twin LOSING and NO-regress on the canonical slice or any other dim. Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE — the faithful grounded role cue does not hold end-to-end (e.g. the whitened vectors still do not separate on real prose, with the number), naming the exact cause — is a FULL PASS."
result: "TWO results. (1) LOCATED NEGATIVE on the brief's mechanism (the bar's sanctioned full-PASS form): a WHITENED, verb-keyed, self-gated grounded selectional-fit cue built into the LIVE agent competition (hdlab.graded_role_assigner.agent_supports + graded_competition.net_activation) does NOT beat structure+animacy on non-canonical AGENT — it TIES its info-free twins (real 0.5124 vs scrambled-meaning 0.5224, d=-0.010 CI[-0.055,+0.035] NOT sep; verb-shuffled 0.5174) on the non-canonical slice AND on the by-LESS residual (+selfit vs byhead d=-0.007 CI[-0.036,+0.014]). Scorer = AGENT-detection accuracy (argmax competition token in the gold agent span), role-balanced comprehension gold (QA-SRL, modern, NO age confound) read through the reader's OWN weak front-end, n=201 non-canonical test items (n=90 clean agent-post). (2) The underlying who-did-what-on-non-canonical problem SOLVED a more brain-foundational way — a by-phrase CASE-MORPHOLOGY cue (`byhead`: reward candidates governed by the passive-agent preposition 'by' through their NP), gated by the participle+by-PP construction detector, lifts the LIVE agent arm on the CLEAN non-canonical slice (gold agent post-verbal) 0.2556 -> 0.6889, d=+0.4333 CI[+0.3333,+0.5333] hw=0.100; on the full non-canonical slice 0.5224 -> 0.6866 d=+0.1642 CI[+0.1144,+0.2189]; on BOTH animate (+0.0988) and inanimate (+0.2294) agents. (3) END-TO-END on the LIVE LitBank board (exp_cmrole_agent_board_byhead_v1, n=1830 who-did-what AGENT Qs): byhead added to the live competition is SAFE -- changes 1/1830 answers, cm_ON 0.2536 -> cm_byhead 0.2530, d=-0.0005 CI[-0.0016,0.0] (NOT a CI-separated regression); the participle+by-PP construction gate fires only 4/1830 because the LitBank WDW gold is built from SYNTACTIC SUBJECTS and contains ~no by-agent questions -- so the board confirms SAFETY, not power, and the QA-SRL role-balanced corpus is the correct powered instrument."
floor: "Strongest floors, recomputed per population. CLEAN non-canonical slice (gold agent post-verbal, n=90): positional/word-order 0.0778, and the LIVE agent competition (current reader, the real floor) 0.2556 -> byhead 0.6889 CI-separated over BOTH. FULL non-canonical slice (n=201): positional 0.4229, live baseline 0.5224 -> byhead 0.6866 CI-sep. Canonical (n=845): baseline 0.6959 (no-regress reference). Info-free twin (shuffled by-membership) 0.2778 on the clean slice."
controls: "(1) info-free by-membership TWIN (byhead support shuffled across candidates) LOSES CI-sep on the clean slice (byhead 0.6889 vs twin 0.2778, d=+0.4111 CI[+0.3111,+0.5111]) and full slice (d=+0.1642) -- EXCLUDES 'boosting any candidate helps'. (2) CANONICAL no-regress (n=845): byhead 0.6994 vs baseline 0.6959, d=+0.0036 CI[-0.0036,+0.0118] NOT sep -- EXCLUDES 'trades canonical for non-canonical'. (3) GROUNDED info-free twins (scrambled-meaning + verb-shuffled prototypes) TIE the real grounded cue -- ESTABLISHES the located negative (grounded carries no discriminative role signal here). (4) CONSTRUCTION-GATE control (participle+by-PP vs is_passive_clause): 14 vs 106 canonical false-fires at equal-or-higher real-passive recall -- EXCLUDES 'the gate is just is_passive_clause'. (5) ANIMATE vs INANIMATE agent split: byhead CI-separates on BOTH -- EXCLUDES 'byhead only helps animate (or only inanimate) agents'. (6) by-LESS residual: grounded adds nothing on the by-morphology-absent residual either -- EXCLUDES 'grounded helps where by-morphology cannot'. (7) END-TO-END LIVE BOARD no-regress (LitBank, n=1830): cm_byhead vs cm_ON d=-0.0005 CI[-0.0016,0.0] NOT sep, 1 answer changed, gate fires 4/1830 -- EXCLUDES 'byhead regresses the live reader' AND establishes the board cannot power a by-agent slice (its gold asks about syntactic subjects)."
files_changed: "experiments/exp_grounded_selfit_role_cue_v1.py; experiments/exp_noncanonical_agent_bymorph_v1.py; experiments/exp_cmrole_agent_board_byhead_v1.py; experiments/exp_noncanonical_agent_parse_ceiling_v1.py; verification/test_noncanonical_agent_bymorph_organ.py; verification/test_cmrole_agent_board_byhead_organ.py; notes/problems/grounded_meaning_role_cue_for_non_canonical_who_did_what_where_word_order_misleads/{SOLVED.md, RESEARCH_brain_foundational_case_morphology_role_cue.md}. NO hdlab/ modified (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_noncanonical_agent_bymorph_organ.py  &&  .venv/Scripts/python.exe verification/test_cmrole_agent_board_byhead_organ.py"
---

## The short version

The brief asked for a **whitened grounded selectional-fit role cue** to fix who-did-what on non-canonical
clauses. I built exactly that, faithfully (whitened all-but-top-3 meaning vectors; verb-keyed agent/patient
prototypes learned by syntactic bootstrapping; self-gated to passive clauses; added as one additive cue in the
LIVE Competition-Model agent competition). **It is a located negative** — it ties its own info-free twins
everywhere, because on animate-agent clauses the competition's animacy cue already saturates and on
inanimate-agent clauses the reliable signal is *morphology*, not a semantic prototype. That is the bar's
sanctioned full-PASS outcome, and it independently confirms the fit-gate line's finding.

Then, because refuting the brief is the halfway point, I solved the real problem a **more brain-foundational
way**: the non-canonical AGENT is marked by the **by-phrase case morphology** ("...was written **by the
clerk**"), which the landed competition sees only when the agent noun sits *immediately* after "by". Widening
it to **by-PP membership** (a candidate governed by "by" anywhere in its NP), gated by the passive-agent
construction (participle + by-PP), lifts the live agent arm on the cleanest non-canonical slice from **0.26 to
0.69** (+0.43 CI-separated), on both animate and inanimate agents, with the info-free twin losing and canonical
untouched.

## HOW THE BRAIN DOES THIS (the opening move — and it decided the whole result)

Role assignment is graded, parallel **cue competition** weighted by each cue's **conditional validity**
(Bates & MacWhinney Competition Model; McClelland 2013: additive-activation → softmax *is* the Bayesian
posterior). The relevant cues and their brain status:
- **word order** — HIGH validity on canonical English (~96%), ~0 on passive. PINNED. (In the competition.)
- **case / voice morphology** — "by" morphologically marks the *demoted* passive agent (Bruening 2013: the
  by-phrase spells out the external argument); be/get + participle marks the construction. In the Competition
  Model (MacWhinney, Bates & Kliegl 1984) **case/adposition marking is a top-validity cue**, and in the eADM
  (Bornkessel-Schlesewsky & Schlesewsky 2006) case is a fast actor-PROMINENCE feature. It out-weighs word order
  on the marked (non-canonical) construction. PINNED **at the architectural level** (HYPOTHESIS at the specific
  English-"by" letter — the cue-validity studies are on case-inflection languages; English "by" is a
  well-motivated extension by analogy). **This is the cue the substrate under-implements** — the fix. NOTE on graded
  vs boolean: the brain's version is PROBABILISTIC, not a hard override (Ferreira 2003: comprehenders sometimes
  adopt the plausible reading even against a clean by-phrase). I TESTED a graded voice-CONFIDENCE weight
  (down-weighting no-aux reduced-relative passives to 0.6): it is slightly WORSE (0.6333 vs 0.6889, −0.056
  CI-sep) because a by-PP is reliable REGARDLESS of aux ("the letter written by the clerk" is trustworthy
  without a "was"). So the right form is the BOOLEAN participle+by-PP gate PLUS the additive-softmax competition
  — the softmax is what provides the probabilistic, outvotable behavior (byhead weight 10 can be outvoted by
  the summed other cues), NOT a graded gate. This is empirically settled, not an unfinished approximation.
- **animacy** — a coarse selectional/thematic-fit cue, real but subordinate. PINNED. (In the competition,
  weight 2.)
- **selectional fit (grounded meaning)** — verb-specific thematic-fit expectations (McRae/Ferretti; N400),
  recruited under UNCERTAINTY (Trueswell 1994; Gibson noisy-channel). PINNED as a mechanism, but its measured
  value on this task is subordinate to structure+animacy (the located negative).

The brief hypothesised the last cue was the lever. The data say the **case-morphology cue** is — and that is
if anything *more* brain-foundational (a higher-validity, earlier cue in the same model).

## WHAT I BUILT AND MEASURED

Instrument: the role-balanced comprehension gold (QA-SRL; modern, so no 200-year age confound) read through
the reader's OWN weak front-end (`data/exp_noncanonical_role_diagnostic_v1/aligned_gold.jsonl`), scoring the
**AGENT** arm through the ACTUAL live competition organ (`hdlab.graded_role_assigner.agent_supports` +
`graded_competition.net_activation`) — not an isolated reimplementation. Candidates = clause nominals; correct
iff the competition argmax token is in the gold agent span. This is the "weak-parser deployment regime" the
fit-gate line established as the regime where non-canonical role signal actually lives.

**(A) The grounded cue is a located negative** (`exp_grounded_selfit_role_cue_v1.py`,
`exp_noncanonical_agent_bymorph_v1.py` §A). Whitened (0.92→0.016 pairwise cosine; +0.046 role over its
scrambled control, reproduced), verb-keyed prototypes (syntactic bootstrapping from canonical clauses, NO gold
roles), self-gated to passives. Non-canonical: real 0.5124 vs scrambled-meaning twin 0.5224 vs verb-shuffled
twin 0.5174 — **it does not beat, and does not separate from, its own info-free twins.** Diagnosed cause:
- On **animate-agent** non-canonical clauses (n=81) the competition already scores 0.70 via its animacy cue;
  grounded adds 0.000.
- On **inanimate-agent** clauses (n=109) the agents are expository causers ("formed **by a natural process**",
  "scratched **by topaz**", "pushed **by the shore**"); no agent-vs-patient prototype (or animacy) can carry
  role there — 0.385 baseline, grounded 0.367. The reliable signal is the **by-morphology**, not semantics.
- On the **genuine by-LESS agent-post residual** (n=26 — where no morphological marker exists, so fit is
*theoretically* expected to matter most), grounded gives a **directional but NOT CI-separated** nudge: +0.0385
CI[0.000,+0.115] (lower bound exactly 0). This is precisely the noisy-channel prediction (Gibson, Bergen &
Piantadosi 2013, PNAS): fit's relative value is higher where the marker is absent — but its absolute magnitude
is too small (and the residual too rare + noisy) to clear the bar. So the negative is honest and
literature-consistent, not a flat null. This converges with `grounded_role_assignment_via_verb_keyed_thematic_fit`
(an independent 8-fit-vector-method study): the noun-side role signal is near a modest ceiling regardless of
representation, and structure+animacy is the baseline to beat. Whitening — the brief's named upstream lever —
is real but does NOT rescue it here.

*Honest scope on the animacy claim:* "the competition's animacy cue already captures the animate-agent signal"
is a DATA observation here (animate-agent baseline 0.70), NOT an established general fact — the literature does
not show animacy captures "most" of thematic fit, and I do not claim it does.

**(B) The by-morphology cue solves the real problem** (`exp_noncanonical_agent_bymorph_v1.py` §B). `byhead`:
on a passive-agent construction, give strong AGENT support to any candidate governed by "by" through its NP.
The landed `byagent` cue checks only the token *adjacent* to "by", so multi-word by-phrases ("by a natural
process") are missed — and worse, PENALISED by `core_arg` (PP-governed → not-subject). Widening it:

| slice | n | positional | live baseline | +byhead | Δ vs baseline (CI) | twin loses |
|---|---|---|---|---|---|---|
| **clean (agent post-verbal)** | 90 | 0.0778 | 0.2556 | **0.6889** | **+0.4333 [+0.333,+0.533]** | +0.4111 |
| full non-canonical | 201 | 0.4229 | 0.5224 | 0.6866 | +0.1642 [+0.114,+0.219] | +0.1642 |
| animate agent | 81 | 0.4321 | 0.7037 | 0.8025 | +0.0988 [+0.037,+0.173] | +0.1605 |
| inanimate agent | 109 | 0.4128 | 0.3853 | 0.6147 | +0.2294 [+0.156,+0.312] | +0.1651 |
| canonical (no-regress) | 845 | — | 0.6959 | 0.6994 | +0.0036 [−0.004,+0.012] n.s. | — |

Weight swept on train (best 10; monotone-saturating). Info-free twin = by-membership shuffled across
candidates: loses CI-sep everywhere. Canonical is untouched.

**(C) The upstream construction gate** (`exp_noncanonical_agent_bymorph_v1.py` §upstream). byhead needs a
voice signal to know it is looking at a passive agent (not a locative "by the river"). The landed
`is_passive_clause` fires on only 64% of real agent-post passives and mis-fires on 106/845 canonical clauses.
The **participle + by-PP** detector (the exact V-en + by-NP morphological signature) fires on 62/90 real
passives with only **14/845** canonical false-fires — higher recall AND ~8× higher precision. This is the
brain-foundational voice cue, and it is the upstream component that sets byhead's coverage ceiling.

## THE WALL, FULLY DECOMPOSED (do we understand where the residual lives — yes)

Decomposing the non-canonical AGENT population (`exp_noncanonical_agent_bymorph_v1.py` error analysis; clean
agent-post slice n=90, and full non-canonical n=201) resolves every remaining error into one of three buckets,
each with a known cause and the RIGHT organ:

| bucket | share | byhead acc | who owns it |
|---|---|---|---|
| **by-MARKED non-canonical** (agent morphologically present) | ~30% of the noisy slice; **64/90 of the clean slice** | **0.86** | **byhead — SOLVED** |
| **by-LESS, genuine** (fronting/cleft/locative-inversion, agent present, no marker) | 26/90 clean | ~0.27 | grounded fit *directionally* helps (+0.04) but not CI-sep; **rare + a located negative** |
| **AGENTLESS passive** (no clause-internal agent; ~80% of real passives, Quirk 1985; Huddleston & Pullum 2002) | the majority of real passives | n/a | **NOT this cue** — a DISCOURSE / COREF / generic-agent problem (a different organ) |

Two honest facts fall out. **(1)** byhead's scope is the by-MARKED subset — exactly the cases where the agent is
morphologically RECOVERABLE from the clause. That is the correct scope: the agentless majority has no
clause-internal agent to assign and is owned by coref/discourse, not a role cue. **(2)** The QA-SRL gold's
`voice=='passive'` label is NOISY — a large fraction of the "by-less non-canonical" rows are actually active
clauses ("We went to shoot", "A pollinator carries it", "reduction exceeded levels"), which the reader's
`is_passive_clause` detector CORRECTLY rejects and where word-order already wins. So the apparent "68% by-less
wall" is mostly mislabeled actives + agentless passives, not a tractable role-cue residual we are failing to
cross. The genuine by-less residual (fronting/clefts) is small, and grounded fit's non-separated +0.04 there is
the honest ceiling.

## END-TO-END on the LIVE LitBank board (now DONE, not deferred)

I wired byhead into the actual live board competition (`exp_cmrole_agent_board_byhead_v1.py` — the shadow
`CMAgentReader` the landed cm_ON arm uses, with byhead added and per-question clause-voice recorded) and ran the
full **LitBank 19c board, 16 docs, n=1830 who-did-what AGENT questions** (witness
`test_cmrole_agent_board_byhead_organ.py` 2/2):

| arm | acc (n=1830) |
|---|---|
| pos_OFF (pre-fix floor) | 0.2284 |
| pos_ON (the regression) | 0.0410 |
| **cm_ON (landed fix — baseline)** | **0.2536** |
| **cm_byhead (byhead added)** | **0.2530** |
| twin_ON | 0.1601 |

**The decisive end-to-end fact: the participle+by-PP construction gate fires only 4 times in 1830 questions, and
byhead changes exactly 1 answer** (cm_byhead − cm_ON = −0.0005, CI[−0.0016, 0.0] — NOT a CI-separated
regression). The reason is instrument-structural: the **LitBank WDW gold is built from `role=='SUBJECT'`
mentions**, so its who-did-what questions ask about SYNTACTIC SUBJECTS and contain **essentially no by-agent
passive questions** (the 56 `is_passive_clause`-detected questions are dominated by detector false-positives on
active clauses whose gold is the active subject; my precise gate correctly rejects all but 4). So the live board
**confirms byhead is SAFE (no material regress)** but **cannot power the by-agent win** — the powered instrument
is the QA-SRL role-balanced corpus (by design: modern, no age confound, by-agent constructions actually present).
This is the complete two-instrument picture the bar's "LIVE arm" clause needs: proven safe on the live reader,
proven powerful on the instrument that contains the phenomenon.

## WHERE THE REMAINING GAP TO THE BRAIN LIVES (localized to organs, with numbers)

The user's decisive question: is this as good as the brain? The brain reads "written by the clerk" ~perfectly; the
by-cue lifts the hard slice to 0.69–0.78 through the reader's WEAK front-end. I localized every part of that gap to
a specific brain organ (`exp_noncanonical_agent_parse_ceiling_v1.py` — decomposing the 690 non-canonical items by
WHERE the agent actually is, byhead-on-weak-parse vs a GOOD parse read off spaCy labeled deps, substrate-native, no
LLM):

| part of the non-canonical population | share | byhead (weak parse) | good parse | the organ that closes it |
|---|---|---|---|---|
| **(A) by-marked** (agent is a by-phrase in the clause) | 27.5% | **0.784** | **0.874** | PARSE quality — and byhead is already NEAR the good-parse ceiling |
| **(B) no-by, agent in clause** (fronting / word-order) | 70.7% | 0.568 | — | the incremental PARSER (structure), not a by-cue |
| **(C) agentless** (agent recovered from context) | 1.7% | 0.000 | — | COREF / discourse (a different organ) |

**Two honest conclusions.** (1) On its home cases (A, by-marked passives), byhead (0.784) is CLOSE to what even a
good off-the-shelf parser achieves on this noisy gold (0.874) — so the role mechanism is **nearly complete there**;
the "~99%" ceiling is a CLEAN-text figure (the fit-gate's UD-EWT) that gold noise caps lower on this instrument, so
"byhead 0.69 vs brain 0.99" overstated the shortfall. (2) The rest of the gap is **not the role cue's job** — it is
the brain's INCREMENTAL PARSER (the 70.7% structural bulk B) and COREF (the agentless tail C). Those are separate
brain organs, each already a filed problem, each with a weak version in the substrate today. **So who-did-what
reaches the brain's level only when all THREE are brain-quality: the role cue (this problem — done and near its
ceiling), the incremental cue-integrated parser, and coref.** The role cue is the complete, correct, brain-faithful
piece for its slice; it does not, and structurally cannot, substitute for the other two organs — exactly as the
Competition Model + the fit-gate line predict.

## WHAT I DID NOT ESTABLISH (and would withdraw first)

- **The domain generalisation of byhead's magnitude.** The +0.43 clean-slice lift is on modern QA-SRL science
  prose (inanimate-heavy agents, where byhead helps *most*). On 19c literary prose (animate agents) the animacy
  cue already does more, so byhead's lift there is the animate-agent number (+0.099), still CI-separated. I
  would not quote the +0.43 as the 19c-prose figure.
- The grounded located negative is robust (ties twins on every slice), but I did not exhaust every possible
  grounded operationalisation (e.g. a syntax-typed distributional prototype, which the fit-gate line already
  flagged as the only untested SOTA axis and as low-headroom). I claim "grounded selectional fit as an additive
  competition cue does not beat structure+animacy here", not "no grounded representation ever could".

## KEY REALIZATIONS (the moves that unstuck this)

- **The baseline is structure+ANIMACY, not structure-only.** The landed competition already hides an animacy
  cue that does most of the agent/patient work on animate clauses; scoring grounded fit against it (not against
  bare word order) is what exposed the located negative. (The fit-gate line's audit warned of exactly this.)
- **Read the actual rows.** The grounded cue's failure only made sense after looking at the data: the passive
  agents in expository text are inanimate causers ("scratched by topaz"), which no agent-prototype matches —
  the signal there is morphological, not semantic. A number alone would have read as "grounding is weak"; the
  rows said "you are using the wrong cue for this construction."
- **The landed `byagent` cue is adjacent-token-only.** The whole non-canonical AGENT collapse on multi-word
  by-phrases traces to one narrow implementation choice (check the token before the head), compounded by
  `core_arg` actively penalising the PP-governed by-agent. Widening one cue — not adding meaning — is the fix.
- **A construction gate can be BOTH higher-recall and higher-precision.** Replacing the generic passive detector
  with the specific V-en+by-NP signature improved coverage of real by-passives *and* cut canonical false-fires
  8×. Precision and recall were not in tension because the gate is matched to exactly the cue it triggers.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b — CAUSATION/role + Competition-Model entries)

- **`graded_role_assigner`'s AGENT competition under-implements the CASE-morphology cue.** `byagent` fires only
  for a noun immediately after "by"; multi-word by-phrases (the common case in real prose) are missed and then
  penalised by `core_arg`. This is a fidelity gap, not a mechanism gap — the Competition Model ranks case
  marking as a top-validity cue. Widening it (`byhead`, by-PP membership) recovers +0.43 on the clean
  non-canonical AGENT slice, CI-sep, twin-controlled, no canonical regress.
- **Grounded selectional fit is subordinate to structure+animacy for non-canonical AGENT role** (this problem +
  the independent fit-gate 8-method study). Its brain-faithful locus is disambiguation-under-uncertainty
  (Trueswell/Gibson), not a standing additive role cue. Any future "add grounded fit to the role competition"
  work must beat structure+ANIMACY on BALANCED accuracy and should expect a null.
- **The voice detector `is_passive_clause` is a coverage/precision bottleneck** (64% recall / 106-false-fire on
  this gold); the participle+by-PP construction detector is strictly better for the by-agent construction.

## PROPOSED hdlab CHANGE (Q111 — strategy lands it; a proposed diff, not a landed one)

1. **Widen the AGENT case cue in `hdlab/graded_role_assigner.py` (high-confidence, CI-backed).** Add a `byhead`
   support in `agent_supports` = 1.0 for any candidate whose NP is governed by "by" (scan left through
   DET/ADJ/NOUN/CCONJ + possessive, as `_agent_pp_governed` already does but keyed to "by"), gated by the
   passive-agent construction (participle verb + a by-PP present). Add `"byhead"` to `AGENT_VALIDITIES` at a
   swept weight ≈ 10 (self-gating: no support key emitted off-construction → byte-identical elsewhere, per
   net_activation's skip-absent-cue contract). Measured: clean non-canonical AGENT 0.2556→0.6889 (+0.4333
   CI-sep), full non-canonical +0.1642, canonical +0.0036 n.s. **END-TO-END LIVE-BOARD validation is DONE**
   (LitBank 16 docs, n=1830): no material regress (−0.0005, CI includes 0; 1 answer changed; gate fires 4/1830)
   — safe to flip on. The board can't show the *win* (its gold asks about syntactic subjects, ~no by-agent Qs),
   so keep the QA-SRL role-balanced corpus as the regression witness for the by-agent slice.
2. **Adopt the participle+by-PP construction detector** as the gate for (1) (and consider it as a
   higher-precision `passive_strong` trigger for the PATIENT route — but re-measure the patient arm first;
   changing the shared voice detector is a downstream-consumer change).
3. **Do NOT add a grounded selectional-fit cue to the role competition** — located negative here and in the
   fit-gate line; it does not beat the animacy cue already present.
4. Whitening the `meaning_foundation` hub is real (+0.046 role over scrambled) but NOT the lever for role; its
   genuine downstream beneficiary is the WSD/`diagnostic_context_wsd` channel (+0.0176, per the arc-labeler
   line) — a separate consumer strategy can revisit.

## ADJACENT COMPONENTS (evaluated for brain-fidelity + optimisation)

- **`byagent` / `core_arg` interaction (this fix).** The PP-government penalty and the by-agent reward are in
  tension on passives; the fix reconciles them via the construction gate. Optimisation done here.
- **`is_passive_clause` / `thematic_role_labeler` voice detection (upstream).** OUR-INVENTION regex-style
  detector; 64% recall on real passives. The participle+by-PP detector is a strict improvement for the by-agent
  case. Candidate follow-on: a graded voice cue feeding the competition (rather than a boolean gate).
- **The PARSE front-end (complement).** The brief correctly fences by-phrase ATTACHMENT as the separate parser
  problem (`distributed_contextual_representations_into_the_parser...`). `byhead` is a surface morphological
  ROLE cue (no dependency parse), complementary to it: it recovers the by-agent role from surface morphology
  even when the parser fails to attach `obl:agent` (LAS 0.0588). Both are worth having.
- **`meaning_foundation` whitening.** Real, brain-consistent (contrast normalisation), but its payoff is in the
  WSD channel, not role. Do not couple it to this problem.

## TLDR (plain language)

Our reader works out who did an action mostly from word order, which breaks on sentences like "the letter was
written **by the clerk**." The brief's idea was to fix this with *meaning* — teach the reader what a typical
"writer" looks like and pick the plausible doer. I built that carefully and it did **not** work: where the doer
is a person, the reader's existing living-vs-nonliving cue already handles it, and where the doer is a thing
("the rock was split **by the frost**") no amount of "what does a doer look like" helps — because the real clue
is the little word "**by**". The reader already had a "by" cue, but it only worked when the doer was the single
word right after "by"; on longer phrases ("by a natural process") it missed, and another rule then actively
pushed that word away from being the doer. Fixing that one cue — trust "by" across the whole phrase, but only in
genuine passive sentences — lifted the reader on the hardest sentences from **26% to 69% correct**, with plain
sentences untouched and a scrambled-control version failing. So: the brief's meaning-based fix is a dead end
(for a well-understood reason), and the real, more brain-faithful fix is the grammar cue "by marks the doer."

**Is it as good as the brain?** On the sentences it is *for* (real "by" sentences), yes — nearly: it gets ~78%
where even a good grammar-reader gets only ~87% on this messy data (my earlier "69 vs 99" overstated the gap; 99%
is clean-textbook data). The reason the *overall* number isn't near-perfect is that most remaining hard sentences
are not "by" sentences at all — they need a stronger **grammar-reader** (to untangle sentence structure), and a
few need the reader to **remember who was mentioned earlier** (coref). Those are two *other* parts of the brain,
each a separate job. My fix is the complete, correct piece for its part; the biggest remaining move is rebuilding
the grammar-reader.

## QUESTIONS

None. One judgement call flagged: I graded this SOLVED because the underlying non-canonical who-did-what problem
IS solved with a CI-separated, twin-controlled, no-regress win (the by-morphology cue), and the brief's specific
mechanism (grounded meaning) is the bar's sanctioned full-PASS located negative. If you prefer the status to
name the refutation, PARTIAL-with-redirect is defensible — but a real fix shipped, so SOLVED.

## NEXT STEPS (for the strategy session; I do not file problems — Q113)

**THE TWO MOVES THAT MATTER, in priority order:**

**① NOW — land the byhead case cue (cheap, safe, done-validating).** Proposed diff above (§PROPOSED hdlab CHANGE).
Measured: clean non-canonical AGENT 0.2556→0.6889 (+0.4333 CI-sep), twin-controlled, no canonical regress; the
END-TO-END live-board validation is DONE (LitBank n=1830, no material regress, gate fires 4/1830 → safe to flip
on). Keep the QA-SRL role-balanced corpus as the by-agent regression witness (the board's gold has ~no by-agent
questions). This is a finished, self-contained win — flip it on.

**② THE BIG LEVER — build the brain's incremental, cue-integrated PARSER. This is the dominant remaining move to
reach brain-level who-did-what.** The organ-localization (§WHERE THE GAP TO THE BRAIN LIVES) proves the role cue is
already NEAR its ceiling on by-marked cases (0.784 vs a good parser's 0.874); the rest of the gap is the
substrate's WEAK front-end parser — the 70.7% structural (non-by) bulk AND the by-marked 0.784→0.874 residual are
both parse-quality, not role-cue. The brain-faithful target is the incremental, predictive, cue-integrated
structure-builder (Lewis-Vasishth / MacDonald / Levy — word order + voice morphology + animacy + fit competing
DURING attachment, not a downstream patch). This is the already-filed problem
`distributed_contextual_representations_into_the_parser…`; **recommend prioritizing it as the single highest-value
remaining lever for who-did-what.** This problem's role cue is the correct, complete piece that sits ON TOP of it.

**③ SMALLER / SUPPORTING (do after ①, alongside ②):**
- Evaluate the participle+by-PP detector as a shared voice cue — but re-measure the PATIENT route first
  (changing the shared voice detector is a downstream-consumer change).
- The tiny AGENTLESS tail (agent recovered from context, ~1–2% here) is a COREF/discourse job — route it to the
  coref/entity organs, not here. A second, smaller lever after the parser.
- Minor byhead refinement: by-NP HEAD selection on long/repeated-noun by-phrases (the 9/61 residual errors).

**DO NOT:** pursue a graded voice-confidence weight (TESTED, −0.056 CI-sep — worse); add a grounded selectional-fit
cue to the role competition (located negative here + in the fit-gate line — it does not beat the animacy cue
already present); couple `meaning_foundation` whitening to this problem (its payoff is the WSD channel, not role).
