# Pre-reg: compgen_native_bind_real_text_v1

REAL-TEXT compositional-generalization test for native role-filler binding.
Follow-up to `compgen_native_bind_role_filler_v1` (HARD_PASS, synthetic near-orthogonal codes)
and `compgen_native_bind_desaturation_sweep_v1` (robust across synthetic difficulty). Removes the
only remaining bound: those used ABSTRACT random codes; this uses REAL fillers with REAL WordNet
lexical geometry from REAL McGuffey text.

## Question
Does the LEARNED text->role encoder (into a fixed FHRR binding space) generalize to HELD-OUT
(concept, role) combinations on REAL fillers where a FAIR LEARNED-FLAT baseline FAILS, or does
real lexical structure (polysemy / frequency / non-orthogonality) erode native's edge?

## Real fillers (the de-saturation)
- Vocab + role structure: McGuffey gold argument-structure golds (`data/gold_mcguffey_lccp_argstruct_v1.json`
  + `data/gold_mcguffey_castle_building_svo_v1.json`), frozen to `data/real_fillers_mcguffey_wordnet_v1.json`.
- Embeddings: each noun's fixed FHRR code = idf-weighted WordNet hypernym-closure feature vector ->
  phasor angle. Similar nouns get NON-orthogonal codes (off|cos| 0.045 vs random 0.031; castle~castles=1.0,
  kitten~animals, father~papa). Real geometry caps clean cleanup at ~0.94 (NOT the synthetic 1.0).
- Role groups: attested corpus roles -> both(5) / agent_only(21) / patient_only(51). 77 nouns, 59 verbs,
  69 real gold tuples. Held-out uses the real agent/patient asymmetry (animate=>agent, object=>patient).

## Gold-role confound control (load-bearing)
Roles fed to the encoder are GOLD by construction (no parser in the loop) -> a held-out failure is
genuinely "no compositional generalization", not "parser missed the patient". Predicted-role arm
DEFERRED (no parser integrated); the clean test is gold-role. Held-out (noun, novel-role) combos
never appear in training in that role (non-tautological; asserted in self_test split-integrity).

## Arms (one variable A/B = readout binding-vs-flat; BOTH consume the same real fillers)
- A `native_bind_shared`  : FHRR binding readout, SHARED noun-emb, real WordNet codebook  [MECHANISM]
- B `flat`                : per-role heads over a frozen REAL-FEATURE projection            [FAIR BASELINE]
- C `native_bind_scramble`: A lesion (decode with random role keys)                        [MUST-FAIL]
- D `native_bind_tied`    : binding readout, role-SPECIFIC emb tables                       [FREE-ALGEBRA LOCUS]

Difficulty knob: additive complex-Gaussian noise on the composed vector (sigma grid), the erosion
axis (N is not a de-sat knob here; WordNet geometry is angle-only so cleanup is dimension-flat).

## Compute architecture
Class (b) sequential-CPU. Justified: tiny complex matmuls (B x 77 codebook at N=1024); FULL wall
~90s; reuses the proven CPU base/sweep cells. No GPU batching benefit. Storage: no_storage (learned
readout, no item store). deterministic_seeding: fixed int seeds + sorted() splits + index-derived
noise gen (NO hash()-seeded RNG). final_metrics_atomicity: tmp_replace. progress_logging:
line_buffered_stdout. seeds: [7,13,19] (>=3).

## Pre-registered bands (envelope-fail)
HARD-PASS = CG_ROBUST_REAL_TEXT (all of): native heldout >= 0.65; flat heldout <= 0.40; gap
(native-flat) >= 0.30; native in-dist >= 0.85; flat in-dist >= 0.85 (baseline aces => fair +
learnable); learning-curve rise >= 0.30; native heldout init < 0.55 (not free-algebra); scramble
heldout <= 0.10 (binding load-bearing); tied heldout <= 0.45 (shared-emb factorization load-bearing);
native in-dist <= 0.98 (real geometry de-saturated); native heldout tracks in-dist on the noise
sweep (where in-dist >= 0.60, heldout >= 0.85*in-dist - 0.05).

HARD-FAIL = native heldout <= 0.40 OR gap <= 0.10 OR flat heldout >= 0.60 OR scramble > 0.20 OR
native in-dist < 0.60 (real task too hard for native) OR flat in-dist < 0.70 (baseline broken).

MIDDLE_BAND (GRACEFUL_EROSION) otherwise.

## CG-supporting vs MM criterion (pre-registered)
- CG-SUPPORTING (real-text systematicity SURVIVES): native robustly generalizes on real fillers where
  flat structurally fails (gap >= 0.30), held-out tracks in-dist under erosion (never collapses first),
  tied fails held-out, scramble collapses.
- MM / honest bound (ERODES = synthetic-only): native's edge collapses toward flat (gap < 0.15) OR
  held-out collapses well before in-dist under mild noise (real structure specifically breaks
  generalization) OR native in-dist too low (real task too hard for both).

## Design-gate self-verify
Real baseline = flat on gold-role real tuples (aces in-dist). Can-fail: native's edge could collapse
to ~flat on real fillers (honest bound) OR native fails in-dist. Difficulty-on: real non-orthogonal
ambiguous fillers, held-out combos disjoint. One-variable: binding readout on/off. Discriminator
survives scale: smoke at FULL N=1024. LOCAL-ONLY: no push, no store mutation, no atom bank.
