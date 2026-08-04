# Pre-registration: exp_grounded_coherence_selector_v1

Date: 2026-08-04. Local-only cell (no queue, no remote, no push). Branch: dataprep/mcguffey-graded-corpus.
Run: `.venv/Scripts/python.exe experiments/exp_grounded_coherence_selector_v1.py [--self-test|--smoke|--full]`

## Motivation (disk-verified negative + component audit)
The sim-earned coherence SELECTOR (`exp_coherence_selector_novel_types_v3`, in-sim coherence_acc=0.8733)
FAILED to transfer to real text: `exp_coherence_selector_text_transfer_v1` -> CANNOT_BRIDGE_REPRESENTATION_GAP,
selector_text_acc=0.4286 (MEASURED@ data/exp_coherence_selector_text_transfer_v1/metrics.json), ~chance.
Component audit of that negative: its coherence was computed over (a) an ARBITRARY SIM PERMUTATION T
(M_backward learned to invert a synthetic coordinate geometry, NOT a grounded causal relation) and
(b) tested with a SURFACE char-trigram text encoding. Both non-brain-foundational.

The TELL: the GROUNDED APPRAISAL function DID transfer *given structure*
(`exp_grounded_appraisal_transfer_to_text_v1`: causal_arm_a[oracle structure]=1.0, but arm_b[extracted]=0.45
= EXTRACTION_BOTTLENECK, MEASURED@ data/exp_grounded_appraisal_transfer_to_text_v1/metrics.json). Its
representation was GROUNDED (appraisal dimensions), so it bridged when the structure was supplied.

=> FIX (this cell): re-earn causal-coherence SELECTION over a GROUNDED representation SHARED with how
text events are encoded, so the SELECTION itself (not just a supplied structure) bridges like appraisal did.

## Brain structure named
Hippocampal/entorhinal RELATIONAL retrieval + reverse-replay: from an OUTCOME, retrieve the antecedent
CAUSE whose grounded consequence matches the outcome. Reused as a delta-rule scorer over a GROUNDED
appraisal/relational code (valence x effect-match x outcome-valence), NOT over arbitrary coordinate
geometry. Grounded code reuses the appraisal representation (valence/congruence dims via
`resolve_valence_blind`) + a situation-model relational effect-match (content-lemma overlap of the
candidate's consequence with the outcome, via `coreference_resolver.normalize_tokens`). FHRR binding organ
(`hdlab.binding.bind`/`hdlab.bundling.bundle`) reused verbatim from `exp_grounded_appraisal_sim_earned_v1`.
The simulation is a NAMED SUBSTITUTE for embodied experience; sim->text transfer is a TESTED claim, not asserted.

## Grounded feature space (shared sim<->text), per candidate given the outcome
- valence_c in {HARM, NEUTRAL, HELP}  (grounded appraisal dim; text via resolve_valence_blind)
- eff_bin_c in {0..K-1}  (quantized effect-match: does candidate's consequence match the outcome; text via
  content-lemma overlap of cand span vs outcome-description, quantized on FIXED thresholds)
- outcome_val in {NEG, POS}  (context; ALL 7 text items are blocked-goal = NEG)
- rec_c in {0,1}  (recency tag; decorrelated from truth in sim; text via line position)
- interaction bind(valence_c, outcome_val)  (conjunctive coding so "valence causes matching-sign outcome"
  is learnable, not an unlearnable XOR in additive features)
phi = to_real_feat(bundle([bind(R_VAL,val), bind(R_EFF,eff), bind(R_OUTVAL,oval), bind(R_REC,rec),
                           bind(R_VXO, bind(val, oval))]))  (reuses the sim's phi/to_real_feat idiom)

## Sim causal law the learner must EARN (not hardcoded; RANDOM must fail)
True cause = candidate that is BOTH valence-consistent with the outcome sign (HARM->NEG, HELP->POS) AND
highest effect-match. Distractors force the CONJUNCTION: one shares valence (consistent but low eff-match),
one shares eff-match (high eff-match but inconsistent valence). Neither valence-alone nor eff-alone suffices.
Recency tag assigned to a random slot, decorrelated from the true cause. Online epsilon-greedy delta-rule
bandit (reward +1 pick true cause, -0.5 wrong), reused from the appraisal sim's training idiom.

## Arms + floors
- FULL: all grounded dims.
- RANDOM: untrained theta (must ~chance = 1/N_CAND).
- NO_EFF: drop effect-match dim (must degrade below FULL; proves effect grounding load-bearing).
- NO_VAL: drop valence + interaction dims (must degrade below FULL; proves valence grounding load-bearing).
- SHUFFLED: train with candidate feature<->true-cause assignment shuffled (label decoupled -> must fail).
Eval baselines: RECENCY (pick rec=1), RANDOM-pick.

## IN-SIM bands (set before running; discriminator must fire at smoke)
- FULL_heldout_acc >= 0.80 and > each of {NO_EFF, NO_VAL, SHUFFLED, RECENCY, RANDOM} by >= 0.10.
- RANDOM_acc <= 1/N_CAND + 0.08 (must fail).
- SHUFFLED_acc <= 0.45 (must fail).
- NO_EFF and NO_VAL each in [0.40, 0.70] (partial: one grounded dim insufficient) and < FULL - 0.10.
If RANDOM or SHUFFLED do not fail, or NO_EFF/NO_VAL do not degrade -> CONSTRUCTION_DETERMINED / vacuous.

## TEXT TRANSFER (load-bearing arm; n=7 TINY -> DIRECTIONAL, not powered)
Same 7 Director-verified backward-causal items (grapp_mcca_001/003/004/005 from richer_v1 +
007/008/009 from crossspan_v2_DRAFT; 006 EXCLUDED). Oracle candidate SEGMENTATION (2 spans + outcome
given); the SELECTION among candidates is what is tested. Encode each into the SAME grounded feature space;
apply the learned FULL theta (mean pick over seeds); correct iff argmax == slot 0 (true_blocker).
Pre-registered outcomes:
- GROUNDED_BRIDGES: selector_text_acc > max(gold_recency=0.0, random=0.5) AND >= 4/7 AND > char-trigram 0.4286.
  => groundedness fixed the bridge (VET HARD, n=7).
- STILL_FAILS: selector_text_acc <= 0.5 (~char-trigram). => run the component brain-fidelity audit: is the
  grounded encoding actually grounding effect->outcome? did the causal model converge in-sim? is a
  similarity-proxy (content overlap) standing in where grounded reasoning should be? Report honestly.
- MIDDLE: between. Report inconclusive-leaning.
VET diagnostics (decompose the transfer, guard against a surface-overlap artifact): also report the
VALENCE-ONLY-grounded selector text acc (pure appraisal, zero content overlap) and the EFF-ONLY text acc.
Valence-only beating recency = the cleanest non-surface grounded result; eff-only carrying it all = flag
that effect-match may be a lexical-overlap proxy (a char-trigram cousin) and VET.

## Contamination guard (reused verbatim from exp_coherence_selector_text_transfer_v1)
mech sees ONLY: parenthetical goal-DESCRIPTION (leak-safe; item-007 goal_owner name-leak avoided),
query_span.text, candidate span texts, candidate/query line positions. MECH_FORBIDDEN_FIELDS
(true_blocker_agent, distractor_agent, recency_baseline_*, gold_verified, ...) NEVER read by the mechanism.
gold recency_baseline_correct read ONLY to report the 0/7 recency floor. Asserted at load.

## Guards
Glass-box; NO borrowed embedding/LLM/parser (char-trigram NOT used; FHRR + valence lexicon + lemma overlap
only). Deterministic: torch.Generator per seed, sorted(set()), OMP/OPENBLAS/MKL=1, no builtin hash()-seed.
Multi-seed (5). Resumable per-seed via tools/exp_checkpoint.py. Metrics atomic os.replace. Store write binary.

## Config
N_DIM=256 (matches appraisal sim), N_CAND=3 (sim) / 2 (text), K_EFF=4, SEEDS=[0,1,2,3,4],
FULL n_train=8000 n_eval=1500; SMOKE n_train=1200 n_eval=400.
