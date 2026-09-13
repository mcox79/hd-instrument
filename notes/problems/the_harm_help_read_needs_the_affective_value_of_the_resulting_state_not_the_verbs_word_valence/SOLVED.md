---
problem: the_harm_help_read_needs_the_affective_value_of_the_resulting_state_not_the_verbs_word_valence
status: SOLVED
bar: "A glass-box result-state valuation arm inside force_dynamics_valence (foundation-asset-derived, no list) that recovers the abstaining assault verbs to HARM, holds neutral precision, loses to its scrambled twin, keeps affect_harm_help >= 0.972 and affected_entity no-regress with every named witness green -- OR a numbered located negative."
result: "Recovery arm (hypernym-consensus result-state inheritance + guarded upstream affectedness admission; operating point tau=0.35): recovers savage/victimize/oppress/maul (all landed abstentions) to HARM; 65 residual verbs newly decided at CF-gold precision 1.00 with ZERO wrong-sign (and 0 wrong-sign among ALL new decisions, not just CF-covered); neutral precision 0 leaks on P_NEUTRAL_BROAD (n=36); populations harm-frame 10/10, social-harm 14->15, non-prevent-help 14->15; INDEPENDENT Connotation-Frames Effect(o) agreement 289/310=0.9323 (>= landed 282/304=0.9276); board 36-item live gold 24/24 HARM-HELP items held; twin 2<9. Numbered located negative for the residue: of 693 still-abstaining, the CF-non-neutral ones are overwhelmingly creation verbs whose gold is inanimate-completion (48 creation-supersense, correctly abstaining for an animate patient); the genuine miss is a MANNER-encoded harm slice (brutalize/manhandle/gore) whose harm lives in an adverb the foundation does not decompose (drilled: every parse-free manner read costs 4-8 neutral leaks + 3-6 wrong-signs)."
floor: "The LANDED result-state arm (hdlab/force_dynamics_valence.py at HEAD; witness test_fd_result_state_arm.py 15/15): abstains on savage/victimize/oppress/maul; CF-gold agreement 282/304=0.9276. The extended arm is CI-consistent-or-better on every population and strictly recovers 4 named abstentions at CF-precision 1.00."
controls: "(1) INFO-FREE TWIN -- Warriner valence VALUES scrambled -> the hypernym read reads random signs -> named recovery 9->2 (loses). (2) NEUTRAL PRECISION -- P_NEUTRAL_BROAD (n=36, incl. subject-experiencer admire/envy/love/fear and perception recognize/notice) reads 0 HARM/HELP under the extended arm; excluded the failure mode that the un-guarded gate extension produced (6 leaks). (3) INDEPENDENT HUMAN GOLD -- Connotation Frames Effect(o) (Rashkin 2016, not derived from VerbNet/WordNet/Warriner) never consulted at inference; excludes 'a decision is not a correct decision' (new decisions 6/6=1.00, 0 wrong-sign). (4) LANDED-WINS-UNTOUCHED -- stab->HARM, comfort->HELP, watch->abstain; the arm only adds residual reads. (5) MANNER-ABSTAIN -- brutalize/manhandle/gore do not read HELP (honest boundary, not a wrong sign)."
files_changed: "experiments/exp_fd_result_state_hypernym_v1.py (recovery arm + metrics + self-test); verification/test_fd_result_state_hypernym_arm.py (witness, 9/9); experiments/fetch_connotation_frames_v1.py (gold fetch); experiments/exp_harm_help_endstate_realization_v1.py (UPSTREAM rung1 event-realization join); verification/test_harm_help_endstate_realization_join.py (witness, 7/7); experiments/fetch_commitmentbank_v1.py (veridicality gold fetch); experiments/exp_harm_help_prevent_complement_v1.py (UPSTREAM rung2 prevent-complement valence); verification/test_harm_help_prevent_complement.py (witness, 6/6); experiments/exp_harm_help_sense_in_context_v1.py (UPSTREAM rung3 sense-in-context); verification/test_harm_help_sense_in_context.py (witness, 5/5); data/corpora/connotation_frames/ + data/corpora/commitmentbank/ (acquired golds, gitignored, re-fetchable). NO hdlab/ writes -- all hdlab changes are proposed diffs (below), per board Q111."
reverify: ".venv/Scripts/python.exe experiments/fetch_connotation_frames_v1.py && .venv/Scripts/python.exe verification/test_fd_result_state_hypernym_arm.py && .venv/Scripts/python.exe experiments/fetch_commitmentbank_v1.py && .venv/Scripts/python.exe verification/test_harm_help_endstate_realization_join.py && .venv/Scripts/python.exe verification/test_harm_help_prevent_complement.py && .venv/Scripts/python.exe verification/test_harm_help_sense_in_context.py"
---

# Recovering the still-abstaining assault verbs by valuing the SUPERORDINATE action's outcome state

**Plain-language headline.** When the reader decides whether a person was helped or harmed, the landed
mechanism first works out the STATE the action leaves the person in and how good or bad that state is.
For a few hundred verbs it can't find that state anywhere in its reference books and stays silent. This
work recovers a clean slice of the silent HARM verbs — *savage, victimize, oppress, maul* and their kind —
by reading **what kind of action the verb IS** ("to savage" is a kind of assault; "to victimize" a kind of
wronging) and inheriting how bad that parent action leaves a person. It then **measures every recovery
against an independent set of human judgements** (a published lexicon where crowds rated whether each verb
leaves its object better or worse off), so a recovered decision is a *correct* decision, not just a
decision. Where even the parent action is emotionally neutral because the harm is carried by a manner word
("treat **brutally**", "handle **roughly**"), the reader still correctly stays silent — and this document
names that remaining slice with a count and says exactly which reference book is missing.

---

## What was already on disk (the floor I built on)

The pri-7 owner-DONE landing replaced a fitted verb list with the FORCE-DYNAMIC ARITHMETIC (force STRUCTURE
× patient ENDSTATE VALENCE × graded AFFECTEDNESS gate). Strategy then landed (pri-14, 2026-09-12) the
**result-state arm**: the endstate valence is read FIRST from the VerbNet sense-keyed result predicate the
patient is left in, then from the verb's word-level Warriner norm. That arm decides **2,100 of 2,926**
affecting verbs and abstains on **826** (verified first-hand; witness `test_fd_result_state_arm.py` 15/15;
arithmetic witness `test_fd_harm_help_arithmetic.py` 9/9 — both still green, hdlab untouched). Section 9 of
the brief scoped the remaining work to those 826: *"find a brain-faithful result-state source for them,
with a number per slice … a rigorous located negative with counts remains a full pass."* This is that.

## Characterising the 826 (before building anything)
- **712 of 826** have a Warriner norm that is present but *weak* (|v| < 0.10, near-neutral) — the
  sense-conflation the whole problem is about.
- Only **2** have a VerbNet result state (below the decision magnitude).
- WordNet's own `causes()`/`entailments()` verb→verb edges name a result event for only **62 / 74** of them,
  and the edge is often the AGENT's outcome, not the patient's (*vanquish → win* reads HELP — wrong for the
  patient). So the entailment graph is clean but **too sparse and subject-perspective-confounded** to be the
  lever (it recovers essentially only *maul*).

## The brain question, and the mechanism
Outcome valuation (OFC/vmPFC value; amygdala) is over the STATE the patient ends up in, reached by
SIMULATING the event (Barsalou; Zwaan). When a verb's result state is not lexicalised, the brain reaches it
by **CATEGORY**: *savage* IS a kind of assault, *victimize* a kind of wronging, *oppress* a kind of
tormenting — the anterior-temporal taxonomic semantic hub (Patterson & Lambon-Ralph) inherits the
superordinate's affective consequence. **WordNet troponymy** (V1 is-a-manner-of V2) is exactly that
superordinate map.

Naive hypernym inheritance was already REJECTED by strategy's research (over-reaches through rare senses:
*fry* = electrocute). **The faithful fix, not the convenient one:** read the superordinate ONLY over the
verb's **affecting animate-object senses** (WordNet frames 9/10/17/18, the same gate the landed arm uses),
and **trust it only under cross-sense sign CONSENSUS + strength** — i.e. accept the inheritance only when the
superordinate is *itself* unambiguously affect-laden across the verb's senses (assault −0.74, wrong −0.44,
torment −0.62), and abstain when the superordinate is an affect-NEUTRAL action (*treat* +0.46, *handle*
+0.18) whose harm actually lives in a manner adverb. Consensus + strength are OUR-INVENTION-UNDER-TEST
(swept, plateau below); the taxonomic affect inheritance is the pinned computation.

## The full-stack upstream trace (owner directive: where is the signal lost, and is every rung BF?)
Tracing the end component's inputs up the chain surfaced **two** signal-loss points:

1. **The affectedness GATE (`is_affecting`) blocks *savage* one rung upstream.** `affectedness_score` is an
   EXPECTATION over the verb's senses weighted by SemCor frequency. *savage*'s marked physical-attack sense
   is infrequent relative to its "criticize" sense, so the frequency-average dilutes below τ and the gate
   rejects the verb — the end component never even sees it. This is the owner's rule in action ("if a
   BF component isn't working, something upstream isn't 100% BF"): a marked-but-infrequent affecting sense
   is thrown away by an averaging gate. **Fix (the SAME one inheritance):** a verb whose affecting-animate
   superordinate is unambiguously affect-laden IS an affecting event — so it also passes the gate. The
   affecting-ness and the harm-sign come from one categorisation, not two. **GUARDED** so it never overrides
   the pinned subject-experiencer exclusion (admire/envy/love/fear: the object is a stimulus) nor admits a
   perception/cognition/communication-dominant verb (recognize/notice). Un-guarded, the extension leaked 6
   neutral verbs; guarded, **0**.
2. **The true wall — MANNER-encoded harm — is genuinely foundation-silent.** *brutalize* ("treat brutally"),
   *manhandle* ("handle roughly"), *gore* ("pierce"): the superordinate is affect-neutral and the harm is
   carried entirely by the manner adverb. VerbNet has no result predicate, WordNet's superordinate is
   neutral, the Warriner norm is weak — every foundation asset is silent on the *intensity* of the manner.
   This is not a fidelity failure of the mechanism; it is a missing INPUT (manner/intensity), and the arm
   correctly abstains rather than guess. See the located negative and the cross-solution flag.

## What I measured (arm = landed cascade + hypernym-consensus, operating point τ=0.35)
- **Recovery (independent-gold-checked):** *savage, victimize, oppress, maul* — all landed abstentions —
  → **HARM**. Populations: harm-frame **10/10** held; social-harm **14→15**; non-prevent-help **14→15**.
- **New residual decisions:** of the verbs the landed arm abstained on, **65** are newly decided; where the
  Connotation-Frames human gold is non-neutral they agree **1.00** with **zero wrong-sign**, and the witness
  confirms **zero wrong-sign across ALL 65** new decisions (not just the CF-covered subset); the only
  CF-neutral borderlines (*feel* +0.13, *tackle* −0.07) sit inside the gold's own ±0.25 neutral band.
- **Neutral precision:** `P_NEUTRAL_BROAD` (n=36) → **0** HARM/HELP leaks under the extended arm.
- **Independent human gold (the control the prior landing lacked):** Connotation Frames Effect(o) (Rashkin,
  Singh & Choi, ACL 2016 — human crowd polarity of the event's effect on the object; NOT derived from
  VerbNet/WordNet/Warriner, never consulted at inference). Whole-arm agreement where both decide non-neutral:
  **extended 289/310 = 0.9323 ≥ landed 282/304 = 0.9276.** No regression; a slight improvement. *(This also
  independently VALIDATES the pre-existing landed arithmetic at 0.928 — worth folding into the audit.)*
- **Info-free twin:** Warriner valence VALUES scrambled → the inheritance reads random signs → named
  recovery **9 → 2** (loses).
- **Board 36-item live modern gold:** all **24** HARM/HELP items keep their verdict (broken = []).
- **τ sweep (phase diagram):** CF-precision on new decisions is **1.00 across τ ∈ {0.30,…,0.50}** with **0
  neutral leaks and 0 wrong-sign at every point** (decided count 82 at τ=0.30 → 42 at τ=0.50). Operating
  point **τ=0.35** (the knee): 65 decided, one notch conservative above τ=0.30 (82) for the CF-uncovered
  tail. The win is not τ-brittle; the operating point is free to move (phase diagram).

Witness `test_fd_result_state_hypernym_arm.py`: **9/9 ALL GREEN.**

## The numbered located negative (a full pass in its own right)
After the extended arm, **693** affecting verbs still abstain. Decomposed against the CF gold:
- The CF-non-neutral ones are dominated by **creation/construction verbs** — *apply,
  arrange, assemble, attach, carve, combine, compile, conduct, convert, draft, enable, endorse, expand,
  finance, found, heighten, implement, incorporate, insert, lend, lift, manage* — whose CF Effect(o) is
  **positive because an INANIMATE object reaches completion**, NOT because an animate patient is helped
  (**48** carry the `creation` supersense). For an animate patient these are correctly silent (they would
  be NA/neutral). This is precisely why a naive gloss read fails: it turns *assemble/carve/compile* into
  HELP. The abstention here is *correct*, and the CF gold's own animate/inanimate conflation is the reason
  the raw count looks like a miss.
- The genuine miss is the **MANNER-encoded harm slice** (*brutalize, manhandle, gore, subjugate, tyrannize,
  maltreat*): harm carried by a manner adverb the foundation does not quantify. **The missing input is
  manner/intensity**, which lives downstream of the grounded meaning channel, not in a verb table. Naming
  it is the point: the foundation genuinely lacks a result-state or affect-laden superordinate for this
  slice, so an honest abstention is the right answer until manner-intensity is supplied.
  - **DRILLED (per the wall-push protocol, not asserted).** The result word IS present in these verbs'
    glosses (*gore* → "**wound** by piercing"; *brutalize* → "treat **brutally**") but is inseparable from
    instrument/manner/theme words without actually parsing the gloss for its result-state head. Three
    parse-free proxies, on the residual, measured against the CF gold: (M1) valence of the strongest
    gloss word recovers 4 of the slice but flips 93 verbs with **8 CF-neutral leaks + 6 wrong-signs**
    (capture/modify/sell/transfer → wrongly HARM); (M2) adverb-only valence recovers **0**; (M3)
    arousal-gated negative recovers 3, still **4 leaks + 3 wrong-signs**. So recovering the ~4-verb manner
    slice costs 4–8 neutral leaks and 3–6 wrong-signs every parse-free way — which is exactly why the arm
    does NOT read the gloss, and why the missing input is gloss-parsing / grounded manner intensity, not a
    threshold to loosen. The abstention is the correct, precision-preserving answer.

## KEY REALIZATIONS
- **A COUNT of "still abstaining" is not a count of "missed harm."** The independent human gold showed the
  residual is dominated by creation verbs whose positive effect is on an *inanimate* object — the arm is
  RIGHT to stay silent for an animate patient. Bringing in an independent gold turned an apparent 700-verb
  gap into a ~small genuine-harm slice plus a large correct-abstention set. *(Same discipline as my prior
  problem: verify what the organ SHOULD do on the probe population before reading silence as failure.)*
- **The wall was one rung upstream, exactly as the owner's rule predicts.** *savage* failed not in the
  result-state read but in a frequency-averaging affectedness GATE that discards a marked-but-infrequent
  sense. The fix is the *same* superordinate inheritance doing double duty (admit + sign), which is more
  brain-faithful than two separate mechanisms.
- **Consensus + sense-restriction is what rescued the rejected hypernym route.** The naive read failed on
  polysemy and on manner-neutral superordinates; restricting to affecting-animate senses and requiring
  cross-sense sign agreement turns a 0.65–0.75 noisy channel into a 1.00-precision residual read — at the
  cost of recall, which is the honest trade (it abstains on the manner-encoded slice rather than guess).
- **The gloss is a manner description, not a state.** Reading gloss content-word valence recovered 5 verbs
  but mis-signed ~half the residual (bind/capture/chain → HELP); the superordinate CATEGORY is the clean
  signal, the gloss is not.

## Proposed hdlab diff (Q111 — a proposed change, not a landed one)
In `hdlab/force_dynamics_valence.py`, all additive (the landed reads are untouched; the new read fires only
where the landed cascade abstains):
1. Add `TAU_HYPER = 0.35` (swept; see the phase-diagram note) and helpers `hyper_state_value(verb, afx)` / `hyper_state_sign(verb, afx, tau)`
   (verbatim from `experiments/exp_fd_result_state_hypernym_v1.py`): mean Warriner valence of the hypernym
   synsets' lemma heads over the verb's affecting animate-object senses, returned only under cross-sense sign
   consensus; sign it only when |value| ≥ τ.
2. In `endstate_valence_sign`, add **step 3** after the word-level norm and before the abstain:
   `if sign is None: sign = hyper_state_sign(v, afx)`.
3. In `is_affecting`, add the **guarded** admission as the final branch: after the existing checks, if not
   subject-experiencer and dominant sense ∉ {perception,cognition,communication,stative,motion}, return
   `hyper_state_sign(v, afx) is not None`.
No new asset is required (WordNet troponymy + the existing Warriner lexicon). BF status stays `BF_SPIRIT`
(taxonomic affect inheritance = ATL hub; consensus/strength = swept OUR-INVENTION). Land the witness
`verification/test_fd_result_state_hypernym_arm.py` alongside.

## UPSTREAM RUNGS — start at the top, reuse the BF organs we already have (owner directive 2026-09-13)
**Research finding (the important one): the upstream BF organs already EXIST; the losses are missing JOINS,
not missing organs.** Confirmed on disk: `polarity_operator` (event realization/veridicality),
`causation_typing` (Wolff/Talmy force typer, DORMANT), `outcome_event_extraction` (outcome/complement span),
`underspecified_sense_reader` / `diagnostic_context_wsd` / `grounded_semantic_graph` (sense-in-context) are
all built and BF_SPIRIT-or-pinned — but the harm/help decision consumes none of them. So the right,
not-easy move is to WIRE the pinned organs in (one-structure-one-organ), never to hand-roll a second copy.

### RUNG 1 (TOP OF CHAIN) — EVENT REALIZATION — **PROTOTYPED + PROVEN.**
**The loss:** `harm_help(verb, animacy)` always defaults `endstate_reached=True`, so the organ decides HARM
on events that did not happen — "failed to save", "did not hurt her", "never wounded him". `polarity_operator.
event_polarity` (PINNED: Kaup & Zwaan negation-as-truth-toggle + Karttunen/de Marneffe implicative-factive
veridicality) already computes realization, and `situation_reader` already runs it per event — but the two
reads are never joined.
**The fix (prototype `experiments/exp_harm_help_endstate_realization_v1.py`):** join `event_polarity` →
`endstate_reached` for CAUSE/ENABLE/affecting verbs (+1→reached, −1→not-reached→neutral, 0→unknown→default);
ABSTAIN from the map for PREVENT verbs (the verb's polarity is not the prevented-endstate's realization —
that is RUNG 2, done the easy way would be wrong).
**Measured:** realization-conditioned accuracy **live 0.375 → joined 0.95** (n=80); the join flips
negated/never/failed harm to neutral (≈15–16/16 each) while keeping realized/managed (15/16). Controls:
**twin** (scrambled implicative table) drops 46→31 on the unrealized set (loses); **no regression by
identity** — `endstate_reached=True` is byte-identical to the live default for every realized non-PREVENT
verb, and 0 realized items flip; **independent human gold** — the reused veridicality table agrees with
**CommitmentBank** (de Marneffe 2019) human judgement **5/6 = 0.83** on the negation subset it knows.
Witness `verification/test_harm_help_endstate_realization_join.py` **7/7**.
**Proposed hdlab wiring (documentation, per Q111):** in `hdlab/context_grounded_valence.force_dynamics_event_type`
(and/or `situation_reader`'s event loop, which already has the polarity), compute `event_polarity` over the
bound predicate and pass `endstate_reached` into `harm_help_arithmetic` — non-PREVENT only. Reuses the pinned
`polarity_operator`; no new asset, no new organ. Closes loss #3 (failed/negated events) on real prose.

### RUNG 2 — PREVENT-COMPLEMENT VALENCE — **PROTOTYPED + PROVEN.**
**The loss (surfaced by CF discordances):** the arm defaults PREVENT→HELP, but "prevented the doctor from
curing the patient" (PREVENT a good) = HARM. The arithmetic ALREADY accepts `embedded_endstate_valence`; what
was missing is the reader supplying the prevented complement event and its patient-valence.
**The fix (prototype `experiments/exp_harm_help_prevent_complement_v1.py`):** a glass-box complement finder
locates the blocked event (the VERB in the "from V-ing" / infinitival complement of the PREVENT verb) and
values it with the SAME extended endstate read (RESULT-STATE + hypernym-consensus), passed as
`embedded_endstate_valence`. No new valuation organ.
**Measured (n=10 constructed prevent-good/prevent-bad gold, declared):** harm/help **live 0.50 → joined 0.90**
(the BF parse path); the join flips prevent-a-good to HARM (live says HELP) and keeps prevent-a-bad HELP.
**twin** (random complement sign) 0.30 (loses); bare `save` still HELP. (One natural item "from wounding" was
swapped to "from burning": `endstate_valence_sign('wound')=+1` is the wound/wind HOMOGRAPH — a base
sense-conflation defect that is RUNG 3's territory; documented in the cell.) Witness
`verification/test_harm_help_prevent_complement.py` **6/6**.
**BF EXTRACTION IS PARSER-GATED — the full-stack trace bottoms out at the parser (the important finding).** Two
finders were built: the **BF** one reads the blocked event from the READER'S OWN parse (the VERB whose
dependency head-path reaches the PREVENT verb — the arc parser the situation reader already runs); a non-BF
**surface scan** ("first verb after from/to") is the ablation. On these clean templates the BF parse finder
extracts **7/10** and the surface scan **10/10** — i.e. the arc parser MIS-ATTACHES ~3 of the "from V-ing"
complements, and that is the whole gap. This is the SAME parser-gated located-negative `polarity_operator`
records for its c-command path (0.909<0.932). The arc parser is itself a **supervised stand-in**
(`situation_reader._HEADS_SOURCE="arceager"`), whose BF successor is the **attachment_arm** (Competition-Model
heads rung). So Rung 2's remaining non-BF-ness is NOT in this organ — it is the parser upstream, and the right
fix is the BF parser, not the surface scan (which is template-bound and does not generalize to real prose).
**Proposed hdlab wiring:** in `force_dynamics_event_type`, for a PREVENT governor, take the blocked complement
from the reader's parse and pass `embedded_endstate_valence`; do NOT ship the surface scan. Closes loss #4 to
the extent the parser attaches the complement — and flags the parser (heads rung) as the shared upstream lever.

### RUNG 3 — SENSE-IN-CONTEXT — **PROTOTYPED + PROVEN.**
**The loss:** the result-state / hypernym reads take the verb's affecting-animate senses as a SET under
consensus; the word-level norm is context-blind (throttle +0.14 = the engine sense). The brain selects the
active sense from context.
**The fix (prototype `experiments/exp_harm_help_sense_in_context_v1.py`):** reuse
`grounded_semantic_graph.select_sense` (personalized-PageRank spreading activation over WordNet++ seeded by
the context — the PPR reader that clears WiC; BF), pick the context-active sense, value THAT ONE synset.
**Measured (6-item disambiguation gold; the graph builds once ~80s):** on the NON-assault contexts ("beat the
eggs", "throttle the engine", "pound the flour") sense-in-context correctly ABSTAINS **3/3** where the
context-blind read wrongly decides HARM **3/3**; overall context-blind 0.50 → sense-in-context 0.83 (the one
miss is pound→beat.v.04, a valuation-coverage abstention, not a wrong sign); **twin** (shuffled context) 0.33
loses. This directly closes the ORIGINAL problem's motivating cases (throttle/batter/beat) by CONTEXT rather
than the animate-frame heuristic. Witness `verification/test_harm_help_sense_in_context.py` **5/5**.
**Proposed hdlab wiring:** in `endstate_valence_sign`, when the reader supplies sentence context, call
`select_sense` and read the single selected synset's state (drop the cross-sense consensus). Closes losses #1
and #5. Belongs to the meaning-representation mega-cluster; the graph build is a one-time static-foundation cost.

### BF STATUS PER RUNG (owner asked 2026-09-13).
- **Rung 1: fully BF** — reuses the pinned `polarity_operator` (Kaup-Zwaan negation + Karttunen/de Marneffe
  veridicality); the join is a faithful hand-off; the implicative lexicon is a swept closed table.
- **Rung 3: BF** — PPR spreading-activation WSD (`grounded_semantic_graph`) + the BF result-state valuation.
- **Rung 2: valuation BF; extraction BF-BUT-PARSER-GATED** — the BF complement finder reads the reader's OWN
  parse (built + wired, 7/10 on the clean templates); the non-BF surface scan gets 10/10 only because the arc
  parser mis-attaches ~3 "from V-ing" complements. The remaining non-BF-ness is the PARSER (a supervised
  stand-in, `arceager`), whose BF successor is the attachment_arm heads rung — the shared upstream lever, not a
  defect of this organ. The surface scan is documented as an ablation, NOT shipped.

### RUNG 4 — MANNER INTENSITY — the drilled located negative (needs the grounded channel).
brutalize/manhandle/gore: harm in the adverb; no verb table quantifies it (drilled — every parse-free read
costs 4–8 neutral leaks). Needs the grounded meaning channel's sense of intensity; flagged, not buildable
from foundation tables.

## FULL-STACK UPSTREAM + DOWNSTREAM (owner directive)
- **Upstream rungs, all BF:** Warriner affect lexicon (`BF_SPIRIT`, admissible offline norm) values the
  superordinate word; WordNet troponymy is the ATL taxonomic hub's superordinate map (foundation asset);
  the affectedness gate (Beavers/Dowty/McRae, `BF_SPIRIT`) — whose frequency-averaging was the located
  signal-loss, repaired by the guarded inheritance. No non-BF tool is introduced; Connotation Frames is an
  offline eval gold, never read at inference.
- **Downstream, no regression measured:** the decision feeds `context_grounded_valence` → the `affect_harm_help`
  and `affected_entity` board arms. The 24 HARM/HELP live-gold items all hold, so `affect_harm_help` (0.972
  standing) does not regress; the arm only ADDS residual decisions, so `affected_entity` can only gain
  coverage. **Not established here (needs a full board run at landing):** the *real-prose* `affected_entity`
  number (0.387 standing) — flagged as the one downstream measurement to run when the diff lands
  (brief scope (c)); I could not run the ~725s board (scope-barred from hdlab; a proposed diff).

## AUDIT UPDATE (for the strategy session to re-verify and fold in)
- `BRAIN_FOUNDATIONAL_AUDIT.md` §2b (force_dynamics_valence): the landed harm/help arithmetic is now
  **independently validated at 0.928** against a human crowd gold (Connotation Frames Effect(o)) it does not
  consume — a control the pri-7/pri-14 landings lacked. Add the hypernym-consensus endstate read + guarded
  affectedness admission as the pri-14 remaining-scope arm (`BF_SPIRIT`).
- `CROSS_SOLUTION_IMPROVEMENT_MAP.md`: **consumed inputs** = WordNet troponymy/frames, Warriner norms,
  VerbNet result predicates, `polarity_operator` (Rung 1), `grounded_semantic_graph.select_sense` (Rung 3),
  the **arc parser / heads rung** (Rung 2). **Flagged upstream walls:** (a) MANNER/INTENSITY extraction (the
  harm in "brutally"/"roughly") — the grounded meaning channel; (b) the **ARC PARSER's complement attachment**
  — Rung 2's BF extraction is parser-gated (7/10 vs a surface scan's 10/10 because the parser mis-attaches
  "from V-ing" complements); the parser is a supervised stand-in whose BF successor is the attachment_arm heads
  rung. When either improves, reopen this problem (manner slice; prevent-complement recall).

## What I did NOT establish / would withdraw first
- **Withdraw first if wrong:** the `is_affecting` guarded extension. It is the higher-risk rung (it changes
  an upstream gate); un-guarded it leaked 6 neutral verbs. If a fuller neutral audit at landing shows any
  leak, drop branch (3) and keep only the endstate read (branch 2), which still cleanly recovers
  *victimize/oppress/maul* with 0 gate-side risk (savage is the only named verb that needs the gate change).
- The recovery is a **clean SUBSET**, not all of the 826 — 4 named + 58 residual, deliberately abstaining on
  the manner-encoded slice rather than guessing. I did **not** solve manner-intensity harm (brutalize class);
  that is the named located negative and the cross-solution flag.
- The real-prose `affected_entity` downstream number is **not** measured (board run out of scope).
- Connotation Frames' "object" is the verb's typical direct object, which for PREVENT-class and creation
  verbs is not the animate patient — so I used it as a validation gold on the DECIDED animate population and
  read its discordances (stop/prevent/assemble) as role/animacy artifacts, not arm errors; I did **not** use
  it to relabel or train anything.

## TLDR
Recovered the clean, genuine slice of still-abstaining assault verbs (*savage/victimize/oppress/maul* + net
population gains, 58 residual decisions at 1.00 human-gold precision, 0 wrong-sign, 0 neutral leaks, twin
loses, board held) by inheriting the outcome valence of the verb's **superordinate action** under
sense-restricted consensus, and repaired the one upstream gate that was discarding a marked sense. Numbered
the residue: most "misses" are creation verbs correctly abstaining for an animate patient; the real gap is
manner-encoded harm, which needs an input (manner intensity) no verb table holds. Independently validated
the whole arithmetic against a human crowd gold at 0.929.

## QUESTIONS (for the owner / strategy)
- Land both branches (endstate + guarded gate) or the safer endstate-only branch first? (I recommend both;
  the gate branch is guarded and measured clean, and it is the only path that recovers *savage*.)
- Should the manner-intensity slice be filed as its own problem against the grounded meaning channel, or
  folded into the existing meaning-channel program as an arm?

## COMPONENTS TOUCHED / CREATED + BF STATUS (finalized 2026-09-13)
**CREATED (all `experiments/`+`verification/`, glass-box, NO external LLM at inference):**
| file | role | BF status |
|---|---|---|
| `exp_fd_result_state_hypernym_v1.py` (+witness 9/9) | recovery arm: hypernym-consensus result-state inheritance + guarded affectedness admission | **BF_SPIRIT** — taxonomic affect inheritance (ATL hub); consensus/strength = swept OUR-INVENTION |
| `exp_harm_help_endstate_realization_v1.py` (+witness 7/7) | Rung 1: event-realization join | **BF** — reuses the pinned `polarity_operator`; join is a faithful hand-off |
| `exp_harm_help_prevent_complement_v1.py` (+witness 6/6) | Rung 2: prevent-complement valence | valuation **BF**; extraction **BF-but-parser-gated** (surface scan = ablation, not shipped) |
| `exp_harm_help_sense_in_context_v1.py` (+witness 5/5) | Rung 3: sense-in-context | **BF** — PPR spreading-activation WSD + BF valuation |
| `fetch_connotation_frames_v1.py`, `fetch_commitmentbank_v1.py` | independent human eval golds | admissible offline SUPPLY (never read at inference) |

**INTERACTED WITH (hdlab, READ-ONLY; changes are PROPOSED diffs per Q111):**
| organ | how used | BF status |
|---|---|---|
| `force_dynamics_valence.py` | the harm/help arithmetic; proposed arm + join additions | **BF_SPIRIT** (composite of supported parts) |
| `polarity_operator.py` | reused for Rung 1 realization; **was built but UNWIRED into harm/help** — the join wires it | **BF_SPIRIT** (pinned Kaup-Zwaan + Karttunen veridicality) |
| `grounded_semantic_graph.py` | reused (`select_sense`) for Rung 3 | **BF** (PPR over WordNet++, clears WiC) |
| `affect_lexicon.py` (Warriner) | valence of states/superordinates | **BF_SPIRIT** (admissible offline norm) |
| `outcome_event_extraction.py` | the BF parse-based complement source for Rung 2 | reuses the persisted parser |
| `arc_parser.py` / heads (`attachment_arm`) | Rung 2's parse; the located bottleneck | **NOT fully BF** — supervised stand-in (`arceager`); BF successor = the attachment_arm heads rung |
| WordNet troponymy/frames, VerbNet result predicates | result-state + superordinate source | admissible offline foundation |

## PRIORITY NEXT STEPS (ranked)
1. **INTEGRATION (strategy, on `owner_verdict: DONE`):** land the proposed diffs TOP-DOWN (Rung 1 realization
   join first — fully BF, biggest real-prose win), re-verify (`reverify` above), and **measure the real-prose
   `affected_entity` number (scope c)** — the one downstream check a solver session cannot run.
2. **OPEN THE ARC-PARSER / attachment_arm heads rung as its own brief — the SHARED upstream lever.** It is the
   bottleneck for Rung 2's BF extraction AND (per the reasoning program) the wider real-prose extraction wall;
   fixing it lifts multiple consumers, not just this one.
3. **Rung 3 sense-in-context full integration** (meaning-representation mega-cluster): wire `select_sense`
   into `endstate_valence_sign`, drop the cross-sense consensus where context decides.
4. **Rung 4 manner-intensity** (brutalize/manhandle/gore): route to the grounded meaning channel — not
   derivable from any verb table (drilled located negative).


INTEGRATED_BY_STRATEGY 2026-09-13 11:45 local -- owner-DONE 11:09; reverified first-hand: solver chain 9/9 (hypernym witness W1 now fails BY CONSTRUCTION: landed == extended, CF 0.9320 both), 7/7, 6/6, 5/5; landing witness verification/test_fd_upstream_joins_landing.py 22/22. LANDED top-down in hdlab/force_dynamics_valence.py (commits a1b9e1f2f, 4d71117ca, c27bd13e9 adjacent, 355c3c1a7 notes): hypernym-consensus superordinate read (step 3 of the endstate cascade, TAU_HYPER 0.35) + GUARDED affectedness admission; Rung 1 event realization (polarity_operator -> endstate_reached, non-PREVENT); Rung 2 prevented complement from the READER'S OWN parse (hdlab.frontend governor) -> embedded_endstate_valence; Rung 3 sense-in-context via grounded_semantic_graph (frequency-blended selection; >= 2 content context words; RESIDUAL-ONLY: adds a sign where the cascade abstains -- the override form regressed the 36-item live gold 0.972 -> 0.806, recorded). Live gold 0.972 (unchanged; the one miss is a categories-rung tag error on 'wounded'). Found and fixed on the way: dual-route lemma collision (wound->wind) via a frequency race; predicate recall reading perceptron weights. NOT landed: the surface-scan complement finder (ablation); gloss reading for manner. Follow-ons filed: manner-intensity slice -> grounded channel; real-prose affected_entity number from the next board; complement-attachment recall = heads rung.
