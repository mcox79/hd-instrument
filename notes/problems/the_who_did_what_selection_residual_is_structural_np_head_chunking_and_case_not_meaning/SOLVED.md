---
problem: the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning
status: SOLVED
bar: "PASS = an NP-head chunker (compound + genitive) + a morphological case cue in the reader's role assignment (glass-box, NO LLM) that lifts clean 19c who-did-what patient selection CI-separated over the nearest-post-verbal position floor (target ~0.98) on held-out cleaned 19c direct-object gold, with an info-free twin (shuffled chunk boundaries / shuffled case) LOSING CI-separated, and NO modern regression. Report CI half-width + null p95; recompute the floor on the same population. A rigorous located NEGATIVE -- the chunker/case cue cannot be built glass-box above the position floor, with the reason -- is a FULL PASS. If wired: a live 19c who-did-what lift through the reader."
result: "SOLVED on the CHUNKER half (a HIGH-VALUE downstream fix, not ceiling polish); brain-faithful LOCATED NEGATIVE on the CASE half. On the cleaned 19c direct-object gold (n=669, position floor recomputed 0.9178, matching the parent) a glass-box NP-HEAD chunker (compound Right-hand-Head-Rule + genitive DP-head) lifts patient selection to 0.9806 -- +0.0628 CI[+0.0419,+0.0837], CI half-width 0.0209, null_p95 0.0209 (CI-separated AND above its permutation null). The info-free CHUNK-SHUFFLE twin (drop a random same-size candidate subset) ties the floor (-0.0015 ns) and the chunker beats it +0.0643 CI-sep; the lift holds on BOTH held-out doc halves (A +0.050, B +0.076 CI-sep); NO modern regression (qasrl n=1261: +0.1277 CI[+0.109,+0.147], the lift is LARGER on modern). DOWNSTREAM (WIRE-DON'T-ISLAND, verified FIRST-HAND): the LANDED role assigners the live reader actually uses score only 0.6831 on this gold (they grab compound modifiers / genitive possessors), and 204/212 (96%) of their misses are exactly this NP-head error; the NP-head wire, dropped into EACH consumer's candidate set, lifts every one +0.20 CI-sep first-hand -- resolve_patient 0.683->0.888, hybrid_role_patient 0.683->0.888, competition_pick 0.671->0.873, route_predicate_arguments(theme, run end-to-end) 0.683->0.888 -- with every info-free twin failing to recover; the full combined stack (content-noun NP-heads + graded competition) is 0.9806 = +0.2975 CI-sep over the landed consumer. The recorded live reader (wired_pick) abstains on 22% and scores 0.807 on its picks, of whose misses 99/101 (98%) are the same NP-head error. So the wire is not a 0.98->ceiling polish; it repairs the DOMINANT who-did-what error mode of the live reader. Fed into the ACTUAL graded Competition-Model organ over the NP-heads the pick is order-dominant at 0.9806 (exactly the Competition Model) and the shuffled-cue-validity twin collapses to 0.6084 (d=+0.372 CI-sep). The morphological CASE cue is a faithfully-built, REAL cue (position-neutralized 2AFC: CASE 1.00 vs info-free shuffle 0.51, d=+0.49 CI-sep) with ZERO availability on the canonical-active DO gold (0/669 orthogonal value -- objects are full nouns, not case-marked pronouns; decisive fronted-object regime = 59/120000 sentences = 0.05%) -- a located negative that is the Competition Model's/eADM's OWN prediction (case = high-reliability, near-zero-availability outside pronouns), not an implementation failure. Structural ceiling = 0.9836 gold-corrected (2 residual misses are gold-annotation errors where the chunker picks the PropBank-correct patient). An aggressive X-bar rule does NOT beat the simple chunker (-0.0075 ns); a FULL modern parser (spaCy) scores 0.9297 < ours (it is itself degraded on 19c) -- we are at/above the 19c parse ceiling."
floor: "Strongest floor = nearest post-verbal grounded candidate (position) = 0.9178 on the cleaned direct-object 19c gold (n=669), recomputed in-population (matches the parent's 0.9178). SECOND, stronger floor run: a FULL modern dependency parser (spaCy en_core_web_sm dobj head, reference-only oracle) = 0.9297 -- BELOW our glass-box chunker, because the modern parser is itself degraded on 19c prose. NP-head chunker 0.9806 beats both CI-separated. Also run: aggressive X-bar chunk 0.9731 (does not help); shuffled-cue-validity graded-competition twin 0.6084."
controls: "CHUNK-SHUFFLE twin (drop a RANDOM same-size subset of post-verbal candidates instead of the real NP-heads) -- ties the floor (-0.0015 ns) and loses to the chunker +0.0643 CI-sep => head IDENTIFICATION carries the signal, not merely dropping candidates. Null p95 (sign-flip permutation) = 0.0209 < the +0.0628 lift => above chance. Held-out doc split (by sentence hash) -- both halves CI-sep => not overfit. Modern no-regression (qasrl n=1261) -- +0.1277 CI-sep => generalizes, no modern harm. Shuffled-cue-validity twin on the graded competition (0.6084) -- the learned Competition-Model validities carry real signal. CASE-SHUFFLE twin (random member) on the position-neutralized probe (0.51 chance) -- the case cue's role information is real (CASE 1.00). spaCy ORACLE-POS (0.9342<ours) and ORACLE full-parse dobj (0.9297<ours) -- a modern tagger/parser does NOT beat ours on 19c => POS/parse are not the lever. Each control excludes a specific alternative: chunk-shuffle kills 'any candidate-drop helps'; null_p95 kills 'small-sample'; held-out kills 'overfit'; modern kills '19c-specific artifact/regression'; shuffled-validity kills 'the competition is inert'; case-shuffle kills 'case is built wrong'; the spaCy oracles kill 'a real parser would do better'."
files_changed: "experiments/exp_whodidwhat_nphead_case_v1.py (NP-head chunker + CHUNK-SHUFFLE twin + held-out + modern no-regression + case availability/orthogonal-value + position-neutralized case probe + fronted-object regime count), experiments/exp_whodidwhat_ideal_structural_v1.py (the ideal STAGE-A->STAGE-B stack reusing hdlab.graded_role_assigner + shuffled-validity twin + X-bar ceiling control + residual taxonomy + gold-frame-error audit), experiments/exp_whodidwhat_signal_loss_ledger_v1.py (end-to-end stage-by-stage signal-loss audit vs a spaCy reference-only competent-parser oracle), experiments/exp_whodidwhat_downstream_live_reader_v1.py (WIRE-DON'T-ISLAND: the landed role assigners run first-hand on the gold + the NP-head-fixable share of their misses + the recorded live-reader wired_pick coverage/acc), experiments/exp_whodidwhat_improved_consumer_v1.py (the improved consumer = landed resolver + NP-head reduce, +info-free twin +combined full stack), experiments/exp_whodidwhat_per_consumer_wire_v1.py (the wire proven FIRST-HAND on EACH consumer: resolve_patient/hybrid_role_patient/competition_pick/route_predicate_arguments run end-to-end), experiments/exp_whodidwhat_full_fix_v1.py (THE FULL FIX as one drop-in role_patient_full_fix function: coverage + parser-free NP-head candidates + graded competition + dormant case cue; 0.629->0.981 effective end-to-end, info-free twin 0.547), experiments/exp_whodidwhat_mention_path_fix_v1.py (the SECOND-PASS follow-on: the mention-level NP-head fix proven on the LANDED situation_reader._assign_roles run unchanged), verification/test_whodidwhat_nphead_case.py (scaffold-free witness, 45/45), data/{exp_whodidwhat_nphead_case_v1,exp_whodidwhat_ideal_structural_v1,exp_whodidwhat_signal_loss_ledger_v1,exp_whodidwhat_downstream_live_reader_v1,exp_whodidwhat_improved_consumer_v1,exp_whodidwhat_per_consumer_wire_v1}/metrics.json, notes/problems/the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning/BRAIN_FIDELITY_AND_SIGNAL_LOSS.md. REUSED (not modified): hdlab.graded_role_assigner (competition_pick/hybrid_role_patient/DEFAULT_VALIDITIES), hdlab.relcl_resolver (resolve_patient/_cands), hdlab.predicate_argument_frontend (route_predicate_arguments -- run, monkeypatched _cands at RUNTIME only), hdlab.pos_tagger, hdlab.closed_class_lexicon (case pronoun set), experiments.exp_19c_composed_cleaned_gold_v1 (is_clean_do/grounded_cands -- the cleaner), experiments.exp_verbrole_exemplar_which_arg_v1 (load_pop)."
reverify: ".venv/Scripts/python.exe verification/test_whodidwhat_nphead_case.py"
---

# The clean-19c who-did-what selection residual IS structural NP-head chunking (a real CI-separated lift), and the case cue is a real-but-structurally-unavailable brain cue -- with the whole pipeline already at the 19c parse ceiling

**Bottom line: the NP-head chunker is a genuine, twin-controlled, held-out, modern-safe structural PASS (0.918 ->
0.981, +0.063 CI-sep and above its null); the morphological case cue is a faithfully-built, provably-real cue that
has ZERO availability on the canonical-active gold -- a located negative that is the Competition Model's own
prediction. Fed into the actual graded-role-assignment organ the system is order-dominant at 0.981 exactly as the
brain does English, and an end-to-end signal-loss audit shows we are AT/ABOVE what a full modern parser achieves on
19c prose. The remaining ~1.6% is verb subcategorization + archaic-POS brittleness + gold noise -- not more
chunking and not a meaning store.**

## WHAT I BUILT (all glass-box, NO LLM, parser-free -- dodges the 19c parser wall)
1. **The NP-head chunker (STAGE A).** The PINNED head operation: from the post-verbal grounded candidates, keep
   only NP-HEADS -- drop a candidate immediately followed by another noun (compound modifier, Right-hand Head Rule,
   Williams 1981) or a possessive marker (genitive possessor -> the possessed noun is the DP-head, Abney 1987). So
   "drove a trade delivery VAN" -> van (not trade), "the undertaker's SHOP" -> shop. `exp_whodidwhat_nphead_case_v1`.
2. **The morphological case cue (a Competition-Model/eADM cue).** Nominative {he,she,they,we,i,who,thou,ye} vs
   accusative {him,her,them,us,me,whom,thee} (register-matched; reuses `hdlab.closed_class_lexicon`). Measured for
   availability + orthogonal value on the gold, and given a FAIR position-neutralized mechanism test.
3. **The ideal integrated stack (STAGE A -> STAGE B).** NP-head candidates fed into the ACTUAL
   `hdlab.graded_role_assigner.competition_pick` (the landed graded Competition-Model organ). This is the proposed
   WIRE, proven end-to-end. `exp_whodidwhat_ideal_structural_v1`.
4. **The signal-loss ledger.** Every pipeline stage isolated against a spaCy reference-only competent-parser oracle
   to locate exactly where signal is lost vs the brain. `exp_whodidwhat_signal_loss_ledger_v1`.

## THE THREE RESULTS

### 1. NP-head chunking is the live structural lever -- a clean PASS
| arm | acc (n=669) |
|---|---|
| **NP-head chunker (compound + genitive)** | **0.9806** |
| nearest post-verbal token (position floor) | 0.9178 |
| CHUNK-SHUFFLE twin (random same-size drop) | 0.9163 |
| aggressive X-bar chunk (drop all ADJ/DET) | 0.9731 |
| full modern parser (spaCy dobj, oracle) | 0.9297 |

`NP-head vs floor = +0.0628 CI[+0.0419,+0.0837]`, half-width 0.0209, null_p95 0.0209 (CI-sep AND above null). The
info-free CHUNK-SHUFFLE twin ties the floor; the chunker beats it +0.0643 CI-sep -- so *head identification*, not
candidate-dropping, is the signal. Held-out on both doc halves (A +0.050, B +0.076 CI-sep). NO modern regression:
on modern qasrl the lift is LARGER (+0.1277 CI-sep), because modern prose has more compounds/genitives.

### 2. The case cue is real but structurally unavailable (brain-faithful located negative)
- **0/669 orthogonal value** on the gold: case NEVER changes the pick (objects are full nouns; 0 items even have a
  nominative pronoun between verb and gold). Not redundant -- *structurally absent* on canonical-active full-NP DOs.
- **The cue mechanism is real and correctly built**: position-neutralized 2AFC, CASE 1.00 vs info-free shuffle 0.51
  (d=+0.49 CI-sep) -- with word order removed, case alone recovers the role, and its shuffle is at chance.
- **The decisive regime is sparse**: true fronted-object (order-conflict) clauses = 59 in 120,000 sentences
  (0.05%). So the ~0 pooled case effect on 19c is an AVAILABILITY fact -- the Competition Model's/eADM's own
  prediction (English case = high-reliability, near-zero-availability outside pronouns), confirmed, not a failure.

### 3. The ideal stack is order-dominant at the ceiling; the residual is verb subcategorization
Feeding the NP-heads into the actual graded competition gives 0.9806 -- IDENTICAL to nearest-head, because word
order is the dominant valid cue on canonical DOs (the Competition Model showing through). The shuffled-cue-validity
twin collapses to 0.6084 (the learned validities are real). The aggressive X-bar rule does NOT help (-0.0075 ns) --
we are at the structural ceiling. The 13 residual misses are verb SUBCATEGORIZATION (naming/object-complement,
ditransitive, clause-boundary), of which **2 are gold-annotation errors** where the chunker already picks the
PropBank-correct patient ("call the bungalow a PLACE": deep patient = bungalow ARG1-PPT, place = ARG2-PRD attribute)
-> gold-corrected ceiling 0.9836. Glass-box supply exists (PropBank ARG2-PRD/GOL, static, no LLM) but its value is
~0.5% here and its real home is the non-canonical regime.

### 4. THE WIRE FIXES EVERY DOWNSTREAM CONSUMER (WIRE-DON'T-ISLAND -- verified first-hand)
The chunker gain is NOT an isolation artifact. The who-did-what consumers all route the patient through
`resolve_patient` or `hybrid_role_patient(cands)` (`route_predicate_arguments` delegates its theme to
`hybrid_role_patient(_cands(upos))`, line 427; `situation_reader._router_roles` calls `resolve_patient`, line 1228).
Run FIRST-HAND on the clean 19c DO gold, the LANDED consumers score **0.6831** -- they grab the compound modifier /
genitive possessor ("drove **trade**" not van, "entered **officers**" not hospital), and **204/212 (96%) of their
misses are exactly this NP-head error**. Dropping the NP-head reduction into each consumer's candidate set lifts
every one +0.20 CI-sep, first-hand:

| consumer | landed | +NP-head wire | info-free twin |
|---|---|---|---|
| `resolve_patient` (situation_reader path) | 0.6831 | **0.8879** (+0.2048 CI-sep) | 0.6667 (no recover) |
| `hybrid_role_patient` | 0.6831 | **0.8879** (+0.2048 CI-sep) | 0.6667 |
| `competition_pick` (graded) | 0.6712 | **0.8729** (+0.2018 CI-sep) | 0.6577 |
| `route_predicate_arguments['theme']` (end-to-end) | 0.6831 | **0.8879** (+0.2048 CI-sep) | 0.6562 |
| **combined full stack** (content-noun heads + competition) | 0.6831 | **0.9806** (+0.2975 CI-sep) | -- |

The recorded live reader (`wired_pick`) abstains on 22% and scores 0.807 on its picks, of whose misses 99/101 (98%)
are the same error. **So this wire is not a 0.98->ceiling polish -- it repairs the DOMINANT who-did-what error mode
of the live reader** (one wire, all consumers, because they share the candidate mechanism).

**The full ideal recovers COVERAGE too.** The live reader abstains on 22% of clean who-did-what events -- 20 to a
spaCy event/pred gate that does not recognise archaic verbs (round/befall/overshadow...), and 127 to the
parse-dependent mention/candidate builder silently dropping answerable clauses (the 19c parse wall again). Those
abstained items are ANSWERABLE: the NP-head chunker gets **0.9592** on exactly them. So EFFECTIVE end-to-end
(abstention counted as wrong): the LIVE reader = **0.6293**, the IDEAL parser-free NP-head-chunked stack = **0.9806**,
**+0.3513 CI[+0.3154,+0.3886]**. The ideal recovers BOTH the accuracy (NP-head) AND the coverage (attempt every finite
verb -- Davidsonian; the parser-free path sidesteps the 19c parse degradation that costs the live reader both).

**THE FULL FIX, as one drop-in function** (`exp_whodidwhat_full_fix_v1.role_patient_full_fix`): attempt every finite
verb -> parser-free grounded content-noun candidates -> NP-head reduction (compound + genitive) -> the landed graded
Competition-Model competition (order-dominant + a DORMANT early case cue). Measured end-to-end on the gold: LIVE
reader effective **0.6293** (78% coverage) -> FULL FIX effective **0.9806** (100% coverage), **+0.3513 CI[+0.315,
+0.389]**; the info-free twin (shuffled chunk boundaries + shuffled cue validities) collapses to 0.547 (full fix
beats it +0.434 CI-sep). This function is the exact prototype of the proposed hdlab wire.

### 5. DOES THE FIX PROPAGATE TO EVERY CONSUMER? -- yes to the core, with named FOLLOW-ON (traced on disk)
Every who-did-what path funnels the patient through ONE of two primitives, and BOTH are covered by the wire:
`route_predicate_arguments` (parse route, situation_reader line 956) takes its theme from `hybrid_role_patient(_cands)`
(line 427); `situation_reader._router_roles` also falls back to `resolve_patient` (line 1228). So the +0.20 fix on
`resolve_patient`/`hybrid_role_patient` propagates to the router theme automatically.

**But the trace surfaces TWO separate mechanisms the `_cands` wire does NOT reach, plus the automatic-but-stale
tail -- this is the FOLLOW-ON WORK, and it is real:**

| consumer | path | wire reaches it? | follow-on |
|---|---|---|---|
| `resolve_patient`, `hybrid_role_patient`, `competition_pick`, `route_predicate_arguments['theme']` | `_cands` primitive | **YES (measured +0.20 each)** | land the wire |
| `situation_reader` STOCK positional path `_assign_roles`/`_pick_role_mentions` (line 1010) | `patient = nearest post-predicate MENTION head` | **NO** -- separate mechanism, not `_cands` | **FIXED + PROVEN** (2nd-pass wire): the SAME NP-head reduction at the mention level lifts the LANDED `_assign_roles` (run unchanged) 0.7728 -> **0.9477, +0.1749 CI[+0.144,+0.206]**, info-free twin 0.719 (fails). `exp_whodidwhat_mention_path_fix_v1` |
| `situation_reader` mention-head resolution `_nom_head_at` (line 1028) | maps the theme INDEX to the covering mention's `head` | PARTIAL -- it half-corrects (why the live reader is 0.807 not 0.888) | make the mention `head` NP-head-consistent (the mention-level filter above supersedes this once landed) |
| ~20 role-OUTPUT organs (`EventRecord`/`SituationModel` -> `bound_event_backbone`, `event_bundle`, `causation_typing`, `possession_operators`, `hd_fact_store`, `reasoner`, `situation_model_accumulate/multibank`, `world_state_register`, `goal_typing`, ...) | consume the assigned patient head string | **YES, automatically** (no code change) | RE-RUN anything that cached patient outputs; RE-VALIDATE anything tuned on the old (wrong) outputs; they still lose the 22% coverage until problem 1b |

**Both accuracy wires are now PROTOTYPED + PROVEN** (nothing landed -- strategy lands hdlab, Q111): (1) the `_cands`
primitive wire fixes resolve_patient / hybrid_role_patient / competition_pick / route_predicate_arguments (+0.20
each); (2) the mention-level wire fixes the stock positional `_assign_roles` path (+0.175, on the landed function
run unchanged). They are the SAME NP-head rule at two sites. The full live reader (`wired_pick` 0.807, 98% of misses
NP-head) is the empirical proof both sites carry the error. Recommendation: land BOTH passes (one shared
`np_head_reduce` helper, called on `_cands` in the primitive AND on `sent_noms` in `_pick_role_mentions`); the ~20
output organs then need re-validation, not re-coding; the 22% coverage is problem 1b.

## WHERE, EXACTLY, WE LOSE SIGNAL vs THE BRAIN (the signal-loss ledger; full table in BRAIN_FIDELITY_AND_SIGNAL_LOSS.md)
- **S2 POS-tag**: ~6/13 residual touch an archaic-form tag disagreement -- but NO available modern tagger fixes it
  (spaCy POS 0.9342 < ours 0.9806). A 19c-adapted tagger is the (bounded, parent-refuted-as-lever) fix.
- **S3 candidates**: 0 who-did-what signal lost to pronoun (STOP) filtering on this gold (0 true-dobj pronouns) --
  but it's the structural cap that zeroes case availability.
- **S4 head-find**: we are AT/ABOVE the ceiling -- a FULL modern parser scores 0.9297 < ours; the modern parser is
  itself degraded on 19c prose (the parent's parser wall, quantified end-to-end). Head-finding is NOT where we lose.
- **S5 role-assign**: ~5/13 -- verb subcategorization (the one clean, addressable, but low-value-here gap).
- **S6 clause / metric**: ~1 embedded-clause + exact-match vs graded proto-role + the 2 gold-frame-errors.

**So: on canonical-active 19c direct-object selection there is almost no room left -- above the available full
parse, chunking exhausted, POS not modern-improvable, meaning refuted at power. The real room is in the regime this
gold cannot test (non-canonical: passive/fronting/wh, where case[built,dormant] + verb-frame projection + full
parsing are decisive and our order-only pipeline would collapse) and in the measurement (graded metric, gold
cleanup) -- both different, named problems.**

## WHAT I DID NOT ESTABLISH
- **No live lift through the reader.** The wire (STAGE A into `graded_role_assigner`) is proven in experiments/ over
  the same organ, but NOT landed (solver scope; strategy lands hdlab, Q111). The proposed diff is below.
- **The case cue is untested where it matters** (non-canonical order): the 19c gold has 0 such items and building
  one is blocked (the parent's A3 parser wall). The mechanism proof is on mined canonical clauses (position gives
  the gold; case is the tested cue), not a non-canonical gold.
- **The verb-frame gap is sized, not filled.** ~0.5% recoverable here; not built (would overfit 3-5 items).

## WHAT I WOULD WITHDRAW FIRST IF WRONG
The whole PASS rests on **nearest-post-verbal being the fair position floor** (0.9178, recomputed, matches parent).
If the intended task is the non-canonical subset, position is not 0.918 -- but that subset is 0% of this gold. Second:
the chunker's `np_heads` rule is a shallow 2-rule head-finder; on a corpus with heavier coordination/apposition it
would need extension -- but the aggressive X-bar variant already shows more-aggressive rules HURT here, and a full
modern parser does WORSE, so the simple rule is defensibly at the 19c ceiling.

## KEY REALIZATIONS (the enabling moves)
- **The info-free twin for a CHUNKER is "drop a RANDOM same-size subset", not "drop nothing."** That isolates head
  IDENTIFICATION from candidate-count reduction -- the twin ties the floor while the real chunker separates, proving
  it's the head choice that carries signal.
- **A near-zero pooled cue effect can be the theory's PREDICTION, not a failure.** The Competition Model says
  English case is near-zero-availability on full-NP objects; measuring 0/669 orthogonal value CONFIRMS the model.
  The move that made this rigorous (not just "case didn't help") was giving the cue a FAIR position-neutralized
  mechanism test -- proving it's built right -- then reporting availability separately. Same discipline the parent
  used for composition (real mechanism, wrong instrument).
- **A modern full parser is a WORSE oracle than a 2-rule heuristic on 19c prose.** Using spaCy as a diagnostic
  upper bound BACKFIRED into the strongest result: we are above the available full-parse ceiling, so "just parse it
  properly" is not a lever on archaic text. The signal-loss ledger only located the real gaps because the oracle
  turned out to be below us.
- **Inspecting the residual against PropBank flipped 2 "misses" into gold ERRORS.** The chunker picks the deep
  patient (ARG1-PPT); the gold labelled the naming complement (ARG2-PRD). The error taxonomy, checked against the
  argument-structure standard, raised the true ceiling and shrank the "capability gap."

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec.2b)
- **`hdlab.graded_role_assigner` is MISSING STAGE A (constituent-head identification).** It treats every nominal
  TOKEN as a candidate (`_cands`) and the `order` cue points at the nearest TOKEN, so it grabs compound modifiers /
  genitive possessors. Adding a glass-box NP-head reduction (compound RHR + genitive DP-head) BEFORE the competition
  lifts clean 19c who-did-what selection +0.063 CI-sep to 0.9806 (info-free twin ties floor; held-out; no modern
  regression). PINNED operation (Williams 1981; Abney 1987; Nelson 2017 bracket-closure). This is the proposed wire.
- **`graded_role_assigner`'s cue set is missing morphological CASE, but it is DORMANT on canonical DOs** (0/669
  availability; decisive regime 0.05% of sentences). Case is a faithfully-buildable early soft cue (proven real:
  +0.49 CI-sep position-neutralized) whose value is in the non-canonical regime the organ targets -- wire it as a
  soft cue, expect ~0 on canonical who-did-what. This CONFIRMS (does not overturn) the parent's "case is the
  cheapest cue" note, but re-scopes it: cheap to build, ~0 yield on the available 19c gold.
- **Who-did-what SELECTION on canonical-active 19c DOs is at the 19c parse ceiling.** A full modern parser (spaCy)
  scores 0.9297 < our 0.9806; a modern tagger 0.9342 < ours. The parent's "19c parser degradation" wall now has an
  end-to-end number: full parsing HURTS on 19c. The residual is verb subcategorization (PropBank-suppliable, ~0.5%
  here) + archaic-POS brittleness (no free fix) + gold noise, NOT chunking and NOT meaning.
- **The 19c who-did-what gold has verb-frame annotation errors.** >=2/669 clean-DO items label the ARG2-PRD naming
  complement or ARG2-GOL recipient as the patient (PropBank/VerbNet: the deep patient is the direct object / theme).
  Flag the gold as canonical-active-only AND verb-frame-noisy for any who-did-what selection claim.

## PROPOSED hdlab DIFF (strategy lands, Q111 -- default-off, witnessed)
In `hdlab/graded_role_assigner.py`, add a glass-box STAGE-A head-reduction pre-pass + a dormant case cue:
1. **`np_head_reduce(toks, pos, cands) -> cands'`**: drop any candidate index whose next token is a NOUN/PROPN
   (compound modifier, RHR) or a possessive marker (genitive possessor). Call it at the top of `hybrid_role_patient`
   / `competition_pick` so the `order`/`adjacency` cues compete over PHRASE HEADS, not raw tokens. On canonical DOs
   this reduces to nearest-head (measured 0.9806); it changes NO confident discrete route (default-safe island).
1b. **SECOND SITE (same helper): the mention path.** In `situation_reader._pick_role_mentions`, filter `sent_noms`
   with the SAME rule (drop a mention whose head token is a compound modifier / genitive possessor) before the
   nearest-post-predicate pick. Measured on the LANDED `_assign_roles` run unchanged: 0.7728 -> 0.9477 (+0.1749
   CI-sep), info-free twin fails. Without this, the stock positional path keeps the NP-head error even after diff #1.
2. **Add `"case"` to `CUES`** with a support in `cue_supports`: +1 for an accusative-pronoun candidate, -1 for a
   nominative-pronoun candidate (lexicon = `hdlab.closed_class_lexicon` case sets). Learn its validity offline (it
   will be near-0 on canonical data, high on non-canonical) -- an early soft cue, dormant on full-NP DOs.
3. Measure on the LIVE reader (`role_balanced_comprehension_gold` + the 19c who-did-what slice) before any claim;
   info-free twins (shuffled chunk boundaries / shuffled case) must lose. Do NOT flat-replace the cascade.
**Reference implementation:** `experiments/exp_whodidwhat_full_fix_v1.role_patient_full_fix` is the exact drop-in
(steps 1+2 packaged); it takes the clause's nominal candidate pairs and returns the patient head, byte-identical to
`resolve_patient` on confident routes. The abstention/coverage half (attempt every finite verb; parser-free
candidate fallback) is the ADJACENT problem 1b, not this diff.

## TLDR (plain English)
The job was to fix the last mistakes in "who did what" on old prose by grouping words into the right noun-phrase
and by using old-fashioned word-endings. The noun-phrase grouping works and is a real, clean win: teaching the
reader that in "the undertaker's shop" the thing acted on is "shop" (not "undertaker") and in "a trade delivery van"
it's "van" (not "trade") raises accuracy from 92% to 98%, it holds on held-out text, it doesn't hurt modern text
(it helps more), and a scrambled version of the same trick does nothing -- so the grouping is really doing the
work. The word-ending idea (he/him, who/whom) is a genuinely real cue -- when we hide word order, it alone can tell
who did what -- but it only appears on pronouns, and the answer key here is all full nouns, so it never actually
gets a chance to help (0 out of 669). That's not a bug; it's exactly what the textbook theory of English predicts
(English mostly uses word order; endings only matter in unusual sentences like "him she loved", which are
0.05% of the text). Then, to see if we're missing anything, I ran the whole thing against a full modern grammar
parser -- and our simple method actually BEATS it on old prose, because modern parsers get confused by old English.
So we're essentially as good as it gets on ordinary old sentences. The handful of remaining mistakes are about verbs
like "call X a Y" and "gave the man a gift" (which need a dictionary of verb patterns, and two of them are actually
mistakes in the answer key, not ours). The honest verdict: on ordinary sentences there's very little room left; the
real headroom is in unusual word-order sentences (which aren't in this old-prose test and can't be reliably built
from it) and in using a fairer, graded scoring method -- both separate jobs.
**And it matters in practice, not just on paper:** the reader's CURRENT "who did what" is right only about 63% of
the time on these clean sentences -- it grabs the wrong word inside a phrase on a third of them and silently gives
no answer on a fifth (both because the modern grammar tool it leans on chokes on old prose). The full fix -- one
drop-in routine that (a) always tries, (b) picks the phrase head, (c) uses the same brain-style cue competition we
already have -- takes that from 63% to 98%, and a scrambled version of it drops to 55%, proving the fix is real.

## QUESTIONS
None blocking. One routing note (with recommendation):
- The case cue and the verb-frame (PropBank) cue are BUILT/specified but ~0-yield on canonical 19c who-did-what;
  their value is the NON-CANONICAL regime. **Recommendation:** land the NP-head STAGE-A reduction into
  `graded_role_assigner` now (measured +0.063, default-off, the clean win); hold the case + verb-frame cues for a
  future non-canonical/modern role-assignment problem where they can be exercised (do NOT expect them to move 19c
  who-did-what).

## NEXT STEPS FOR STRATEGY (ordered)
1. **Land the NP-head STAGE-A reduction** (the proposed diff #1) into `resolve_patient` / `hybrid_role_patient`
   (reduce `cands` before the pick), default-off, witnessed on the live reader. This is now a HIGH-VALUE wire, not
   ceiling polish: it lifts EVERY downstream consumer +0.20 CI-sep first-hand (resolve_patient / hybrid_role_patient
   / competition_pick / route_predicate_arguments all 0.683 -> 0.888) and the full stack +0.35 EFFECTIVE end-to-end
   (0.629 -> 0.981), fixing 96% of the live reader's dominant who-did-what error mode. Info-free twins all fail.
1b. **The 22% ABSTENTION is a separate COVERAGE gap worth its own problem** (adjacent, measured): 20/669 to a
   spaCy event/pred gate that mis-rejects archaic verbs (not brain-faithful -- every finite verb projects an event,
   Davidsonian), 127/669 to the parse-dependent mention/candidate builder dropping answerable 19c clauses. The
   chunker gets 0.96 on the abstained items -- pure lost coverage. File as `the_live_reader_abstains_on_a_fifth_of
   _answerable_who_did_what_events` (parser-free candidate fallback + a Davidsonian event gate).
2. **Wire the case cue as a dormant early soft cue** (diff #2) -- cheap, brain-faithful, ~0 yield on canonical DOs
   by design; it earns its keep only on the non-canonical regime the organ targets. Do NOT expect a 19c number.
3. **File verb subcategorization (PropBank ARG2-PRD/GOL frames) as a supply for the graded_role_assigner's
   NON-canonical residual**, not this task -- ~0.5% here, high-value on reduced-relatives/object-complements. The
   organ's own docstring already flags "verb-subcat SUPPLY".
4. **Correct the gold**: >=2 clean-DO items mislabel the ARG2-PRD complement / ARG2-GOL recipient as the patient;
   the true structural ceiling is >=0.9836. Flag the 19c who-did-what gold as canonical-active-only + verb-frame-noisy.
5. **The real room is elsewhere** (not this task): a position-ambiguous 19c gold (the parent's blocked A3) to exercise
   case/frames, and a graded proto-role metric (the parent's C1). DO NOT re-open chunking (X-bar hurts), a modern
   parser/tagger (both lose on 19c), or a meaning store for SELECTION (parent-refuted at power).
