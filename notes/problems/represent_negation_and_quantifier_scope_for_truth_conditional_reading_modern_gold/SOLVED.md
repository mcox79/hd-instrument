---
problem: represent_negation_and_quantifier_scope_for_truth_conditional_reading_modern_gold
status: SOLVED
bar: "A glass-box polarity + quantity OPERATOR over the extracted proposition ... doing BOTH (a) POLARITY -- detect the negation operator and its SCOPE, mark the event/action proposition as NOT holding; and (b) QUANTITY/SCOPE -- read a quantifier's CARDINALITY over the argument set (some >= 1, all/every/each = whole set, none/no = 0, 'everyone but X' = set minus X). ... Answers a MODERN negation/quantifier gold, CI-separated over BOTH (a) a POLARITY-BLIND floor recomputed on the same population which MUST LOSE on the negated/quantified items; and (b) the info-free SHUFFLED-TOKEN twin ... report negation and quantifier SEPARATELY and aggregate ... A rigorous NEGATIVE is a FULL PASS."
result: "NEGATION reader-native (UD-EWT sm.events, n=131): net factuality 0.9313 vs polarity-blind 0.5038 (+0.4275 CI[0.3435,0.5115]); negated-recall 0.8769 vs blind 0.0000; over-negation 0.0000 clean / 0.0152 all -- BEATS the prior negation_factuality_gate MIDDLE_BAND (0.0303). NEGATION well-powered (MoNLI NMoNLI n=1202): operator 0.9965 vs blind 0.0035 (+0.9929 CI[0.9876,0.9973]); PMoNLI op==blind 1.0 (no positive regression); detection 1.0. QUANTIFIER reader-native (n=585, 210 passages, verb-extraction 1.0): 1.0000 vs quantity-blind 0.5385 (+0.4615 CI[0.4205,0.5026]); specific-exception 1.0 vs blind 0.0. QUANTIFIER well-powered (MED downward-monotone n=563): 0.8259 vs monotone-blind 0.1741 (+0.6519 CI[0.5879,0.7123])."
floor: "POLARITY/QUANTITY-BLIND floor (every extracted proposition stored positive+singular), recomputed per population: MoNLI-NMoNLI 0.0035 (inverts), EWT 0.5038, reader-native quantifier 0.5385, MED-downward 0.1741. Second floor: majority (MoNLI 0.5). All lose CI-separated on the negated/quantified subset."
controls: "(1) polarity/quantity-blind floor -- LOSES CI-sep on every negated/quantified population, and INVERTS on the monotonicity golds (MoNLI 0.0035, MED-down 0.1741) = the positive control (polarity-respecting answer OPPOSITE the blind one). (2) info-free shuffled-token twin (permute negation cues / determiners across items, matched shapes) -- LOSES CI-sep, beats null p95 on all four. (3) ADDITIVE isolation -- operator applied to sm.events leaves predicate/agent/patient/tense/pred_idx BYTE-IDENTICAL (no downstream regress). (4) ablation direct-only vs full scope -- the coordination/implicative/inversion machinery adds +0.053 net on EWT and drives over-negation 0.0303->0.0000."
files_changed: "experiments/_polarity_operator.py, experiments/fetch_negation_quantifier_gold_v1.py, experiments/exp_polarity_operator_monli_v1.py, experiments/exp_polarity_operator_ewt_v1.py, experiments/exp_quantifier_operator_v1.py, experiments/exp_quantifier_operator_med_v1.py, verification/test_polarity_operator_core.py, verification/test_polarity_operator_monli.py, verification/test_polarity_operator_ewt.py, verification/test_quantifier_operator.py, data/corpora/{monli,med}/ (fetched, gitignored), notes/problems/represent_negation_and_quantifier_scope_for_truth_conditional_reading_modern_gold/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_polarity_operator_ewt.py && .venv/Scripts/python.exe verification/test_quantifier_operator.py"
---

# Represent negation + quantifier scope for truth-conditional reading — SOLVED

A glass-box, no-LLM truth-conditional **polarity + quantity operator** attached to the reader's already-extracted
`sm.events` / argument set. It **clears the bar on all counts** — negation and quantifier, reader-native headline
and well-powered naturalistic companion, CI-separated over a polarity/quantity-blind floor that MUST lose (and
*inverts*) and an info-free shuffled-token twin — and it **exceeds the prior attempt** (`negation_factuality_gate`
topped out at MIDDLE_BAND, blocked by parse conj/complement edge-typing; this reaches 0.0000 clean over-negation).

## The opening move: how does the brain do this? (PINNED vs OUR-INVENTION)

- **PINNED — negation is an OPERATOR that TOGGLES a represented proposition's truth value** (Kaup & Zwaan 2005
  two-step: represent the to-be-negated state, then the ACTUAL state; comprehension ends on the actual state).
  A polarity-blind extractor performs only step one (keeps the embedded positive content) — exactly the bug.
  Neuroscience: negating an action sentence SUPPRESSES the negated content (Tettamanti 2008; Tomasino 2010).
- **PINNED — quantification is CARDINALITY over the model's token set** (Johnson-Laird mental models): some≥1,
  all/every/each = every token, **none/no = ZERO tokens = ¬∃** (negation and "none" UNIFY — one representation
  of the actual state), "everyone but X" = every token except X.
- **PINNED — scope is the operator's clause-local c-command domain**: negation toggles its own finite clause's
  predicate + coordinated predicates at the same level, and does NOT cross into an embedded COMPLEMENT clause;
  a complement's factuality comes from the matrix verb's IMPLICATIVE/FACTIVE signature (Karttunen 1971;
  Kiparsky & Kiparsky 1970 factive gerunds; de Marneffe 2012).
- **OUR-INVENTION-UNDER-TEST (swept):** the cue lexicon (incl. informal no-apostrophe web contractions), the
  transparent-adverb/auxiliary skip window, the coordinator/comma sharing rule, the implicative/factive lexicon,
  the quantifier→cardinality table, the "but/except X" exception construction, interrogative-inversion and
  post-verbal neg-quant-object routes. **The operator↔representation composition is OUR-SYNTHESIS.**

## What I built (`experiments/_polarity_operator.py`, 23/23 self-test)

A pure-symbolic operator that CONSUMES a proposition (predicate token index + sentence tokens + argument set)
and returns polarity ∈ {+1 holds, −1 does-not-hold, 0 undetermined} and a quantifier cardinality readout. It
**REUSES `hdlab/state_register.py` verbatim** — the polarity primitive (`StateSpan.polarity`), the
antonym/contradiction guards (`incompatible`, `_contradictory_pair`), and the ATL-hub WordNet entailment matcher
(`state_match` / `_wn_hypernym_entails`, with the privative / open-vs-closed-scale / typed-antonymy guards). It
is the copular-state polarity primitive **EXTENDED onto EVENT/action propositions + a quantifier layer** — it
does not re-extract, re-type, or re-parse.

Negation scope (the brain-foundational upstream fix for the prior gate's wall): (1) clause-local do-support /
modal / adverbial negator scan skipping transparent adverbs AND auxiliaries; (2) negative-existential subject
("no one / none / nobody"); (3) coordination CHAIN sharing (comma/and/or/nor, blocked by contrastive "but" and
by complementizers); (4) an IMPLICATIVE/FACTIVE complement gate that **replaces** negation propagation into
complements — "did not remember [George telling]" → telling TRUE (factive gerund), "did not want to leave" →
UNKNOWN (attitude), "did not manage to escape" → escape FALSE (implicative); (5) interrogative subject-aux
inversion ("can't you see"); (6) post-verbal negative-quantifier object ("has no money", Klima neg-incorporation).
Quantifier layer: read the determiner over the argument set → ALL/SOME/ZERO/EXC(all-but-X)/FEW, answer who /
how-many / did-anyone from the cardinality — robust to the reader's noisy binding (it reads the DETERMINER, not
the garbled agent bind the probe exposed for "everyone but Mary agreed").

## What I measured (four layers, all CI-separated, modern gold)

| layer | gold | operator | polarity/quantity-blind floor | twin | margin |
|---|---|---|---|---|---|
| **Negation — reader-native HEADLINE** | UD-EWT `sm.events`, n=131 | net **0.9313**; neg-recall **0.8769**; over-neg **0.0000** clean | 0.5038; neg-recall 0.0000 | 0.5496 | +0.4275 CI[0.344,0.512]; twin +0.382 > null 0.083 |
| **Negation — well-powered companion** | MoNLI NMoNLI, n=1202 | **0.9965** | **0.0035 (inverts)** | 0.4548 | +0.9929 CI[0.988,0.997]; detection 1.0 |
| **Quantifier — reader-native HEADLINE** | constructed modern QA, n=585 | **1.0000**; exception 1.0 | 0.5385; exception **0.0** | 0.5671 | +0.4615 CI[0.421,0.503]; twin +0.433 > null 0.040 |
| **Quantifier — well-powered companion** | MED downward-monotone, n=563 | **0.8259** | **0.1741 (inverts)** | — | +0.6519 CI[0.588,0.712]; cover 0.490 |

PMoNLI (positive, n=1476): operator == blind == 1.0 — **zero regression on positive items** (the operator only
fires where polarity/quantity bites). Witnesses: `verification/test_polarity_operator_{core,monli,ewt}.py` +
`test_quantifier_operator.py` = **14/14 checks**. Heavy runs stayed local (short sentences, <90 s each).

## The wall, fully researched (owner: research every wall)

The prior `negation_factuality_gate` reached MIDDLE_BAND because it PROPAGATED negation through a learned
arc-labeler's `conj` edges, which mislabels complement clauses → over-negation 0.0303. I built ACROSS it two
ways: (a) **surface coordination + implicative signatures** instead of a learned label (more brain-faithful:
categorial parallelism + Karttunen implicatives), and (b) a **complement gate** that never propagates into a
complement. Result: over-negation **0.0000 on clean affirmatives**.

Drilling the residual 8/65 EWT misses to their mechanism (not tuning): **~5–6 are GOLD NOISE** — the gold's own
auto-`conj_propagated` construction over-propagated negation across contrastive **"but"** (the exact v1 bug),
labelling linguistically-AFFIRMATIVE second clauses NEGATED: "can't help **but** trot it out" (= trot DOES
happen), "not done a test **but** have done a panel" (= panel WAS done), "not in how much she likes X **but** how
much they like her". One over-negation (AFD_081 "know **nothing** about courtesy") is Klima neg-incorporation my
operator reads correctly as negated while the gold labels it realized. **My brain-faithful operator is arguably
more correct than the gold on these ~6 items**; scored against a noise-cleaned gold, negated-recall is ≈0.95.
Two are genuinely hard (relative-clause-interrupted coordination "get treats that he loves and give"; both need
a labelled parse — the same upstream parse-quality lever the audit already tracks). I report the RAW numbers as
the headline (they clear the bar) and name the noise items rather than quietly excluding them.

## What I did NOT establish / would withdraw first

- The **reader-native quantifier headline is a constructed template set** (modern vocabulary, 585 items) — 1.0000
  is a construction-faithfulness proof, not free-narrative robustness. The MED companion (naturalistic,
  CI-sep +0.65 on the downward subset) is the honest well-powered check; **withdraw the 1.0000 headline first**
  if pressed, and stand on MED + the EWT negation headline.
- MED coverage is **0.490** (the operator decides clean subset-diff / single-lex-replacement edits; conjunctions,
  conditionals, NPIs, multi-word edits are out of the glass-box operator's scope — stated, not hidden). On the
  UPWARD subset operator == blind (0.4258) — the operator adds nothing where the quantifier is trivial; its value
  is concentrated on the DOWNWARD subset, which is the point.
- The operator depends on the reader recovering the predicate (EWT align_fail 1/132; quantifier verb-extraction
  1.0) and, for the hardest coordination/relative-clause cases, on a labelled parse — the upstream lever below.

## KEY REALIZATIONS (the enabling moves)

1. **"None" IS negation.** Unifying the negative quantifier ("no one / none / nobody") with sentential negation
   (cardinality 0 == ¬∃) is what let ONE operator answer both the negation and the quantifier golds — and it is
   the Johnson-Laird representation, not a hack.
2. **Read the determiner, not the binding.** The reader mis-binds quantified arguments ("everyone but Mary
   agreed" → agent=Mary, the very person who did NOT agree). Reading truth off the CUE/DETERMINER tokens makes
   the operator robust to the noisy extraction — the reason the reader-native quantifier headline works at all.
3. **The complement gate, not propagation, is the brain's mechanism** — and it is what beats the prior wall.
   Complement-clause factuality comes from the matrix verb's implicative/factive signature; propagating negation
   into the complement (what v1/v2 and the gold-construction script did) is the bug, not the fix.
4. **The polarity-blind floor doesn't just lose — it INVERTS** (MoNLI 0.0035, MED-down 0.1741). Ignoring one
   "not" or one "no" flips the truth value, which is the strongest possible statement of why this matters.
5. **The gold embodied the bug.** The EWT gold's auto-propagation over-negates across "but"; a brain-faithful
   operator is measurably more correct than its own evaluation gold on ~6 items — a reminder that the disk can
   be wrong and to drill misses to mechanism before accepting them.

## AUDIT UPDATE (`notes/BRAIN_FOUNDATIONAL_AUDIT.md` — event-stream / state-register entries)

- **NEW DEVIATION, now measured:** `EventRecord` carries no truth-POLARITY or QUANTITY field — every event is
  stored POSITIVE + SINGULAR (verified by enumeration; the fields are predicate/agent/patient/tense/subj_role/
  obj_role/affect/patient_surprisal/patient_conf — none truth-conditional). This is now demonstrated CI-sep on
  modern gold: reading a proposition polarity-blind is not just lossy, it **inverts** the truth value under
  negation/downward-monotone quantifiers (MoNLI 0.0035, MED-down 0.1741).
- **FRAGMENTATION found:** truth-conditional negation is scattered across ≥5 clause-local scanners
  (`goal_typing._verb_negated_before`, `definitional_predicate_v61.negation_in_scope`, `goal_register._negated_before`,
  `result_type_induction._neg_present`, `goal_achievement.desiderative_negation_channel`) and per-slot polarity
  in `state_register` / `situation_model_accumulate.add_causal_link`. There is NO unified event-proposition
  operator. This operator is the consolidation point; `state_register`'s copular polarity is the primitive it
  extends. (Distinct from affective VALENCE — `wordnet_polarity_propagation` — which is orthogonal.)

## Adjacent components — brain-fidelity + revisit opportunities (seeds the next problems)

- **`state_register` (copular polarity) — REVISIT to REUSE this operator.** It carries polarity only for copular
  states; the event stream now has the same primitive. Unifying them under one polarity representation is the
  brain-faithful move (one truth-conditional layer over copular AND event propositions).
- **The parser / arc-labeler (upstream of upstream) — the residual lever.** The 2 genuinely-hard EWT misses and
  MED's uncovered conjunction/conditional cases need a labelled parse (conj vs relcl vs ccomp). This is the SAME
  parse-quality lever the precision-weighting audit entry already tracks — a candidate follow-on, not a bolt-on.
- **The QA capstone + coref + goal/causal registers** consume these propositions polarity-blind today; they are
  the DOWNSTREAM that will answer negated/quantified questions correctly once the field is wired (no regress —
  the field is additive; extraction byte-identical).

## PROPOSED hdlab change (Q111 — I prototype, strategy lands + witnesses)

Additive, default-off, byte-identical fallback — exactly the pattern of the existing `affect` / `patient_surprisal`
/ `patient_conf` fields on `EventRecord`:
1. Add default-`None` fields `polarity: Optional[int]` and `quantity: Optional[str]` (+ `quantity_exception`) to
   `EventRecord`, and a `polarity_provenance: Optional[str]` for glass-box provenance.
2. Add a default-off `read_polarity` capability flag on `SituationReader`: an additive post-read pass that runs
   `_polarity_operator.event_polarity` over each event (tokens + pred_idx) and `read_quantifier` over the
   coref-resolved subject NP, setting ONLY the new fields (following the `_read_state` / `predict_surprisal`
   wiring template). Promote `experiments/_polarity_operator.py` as `hdlab/polarity_operator.py` (glass-box,
   reuses `hdlab/state_register`). Default OFF → the current reader is byte-identical; flip-on when a downstream
   consumer (QA / causal / state) reads the field, per the no-more-default-off / flip-on-find-the-break rule.
3. `state_register` REUSE: route event-proposition polarity through the same `state_match` primitive so copular
   and event polarity share one representation.
Do NOT: rebuild the state register / event extractor / coref (all live); use an LLM or learned NLI (the invariant);
conflate with affective valence.

---

**TLDR (plain English):** Our reader used to file every fact a story states as true and about one thing — even
"she didn't take the key" (filed as she took it) or "none of the guards moved" (filed as someone moved) or
"everyone but Mary agreed" (filed Mary as agreeing, when she's the one who didn't). I built the small reasoning
step that carries the little words — not, no, never, none, some, all, each, "everyone but" — through to the stored
fact, marking a denied fact as not-true and a quantified one as covering the right people and count, reusing the
machinery the reader already had for "she is / is not ill". On modern test data it gets these right where a reader
ignoring those words gets them **exactly backwards**: on a standard negation set it scores 99.6% where the
word-ignoring baseline scores 0.4% (ignoring one "not" doesn't just miss — it flips the answer); reading real
web sentences it correctly flags 88% of the negations the old reader flagged none of, while never wrongly denying
a plain positive statement; on quantifiers it is perfect where the old reading is a coin-flip. It also beats an
earlier in-house attempt that got stuck, because I used the brain's actual rule for tricky cases ("she didn't
remember him leaving" still means he left) instead of the shortcut that attempt used. It is a transparent add-on
that changes none of the reader's existing output.

**QUESTIONS:** none blocking. One judgement call for the owner: the reader-native quantifier headline is a
constructed (templated) modern set — I lead with it per the brief's "reader-native narrative as HEADLINE" and
back it with the naturalistic MED companion; if you prefer, treat MED + the EWT negation headline as the
load-bearing numbers and the constructed set as illustrative.

**NEXT STEPS (priority-ordered):**
- **P1 (strategy-owned, ready now):** land the additive default-off `read_polarity` field + promote
  `hdlab/polarity_operator.py` (the Q111 diff above); wire the QA capstone to answer polarity/quantity-sensitive
  questions off it — the downstream that makes the gain board-visible.
- **P2 (this operator, next build):** unify `state_register` copular polarity and event polarity under one
  representation (revisit the adjacent component to REUSE this operator) — one truth-conditional layer.
- **P3 (upstream lever):** the 2 hard EWT misses + MED's uncovered conjunction/conditional cases need a labelled
  parse (conj vs relcl vs ccomp) — the same parse-quality lever the precision-weighting entry tracks; a candidate
  follow-on problem, itemized with counts.
- **P4 (adjacent):** consolidate the ≥5 scattered clause-local negation scanners in hdlab under this operator
  (fragmentation named in the AUDIT UPDATE) — removes duplicated, divergent negation logic.
