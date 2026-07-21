# Pre-reg: compositional generalization via native role-filler binding (Layer-1 component #1)

**Anchor:** `compgen_native_bind_role_filler_v1`
**Cell:** `experiments/exp_compgen_native_bind_role_filler_v1.py`
**Filed:** exp_dev, 2026-07-21. Design pointers: `notes/research_drill_compositional_generalization_role_binding_brain_mechanism_2026-07-21.md` + `notes/prior_art_scour_synthesis_focus_chaingrade_2026-07-18.md`.
**Status:** LOCAL-only (no push / no store mutation / no atom bank). Skunkworks VETs on land (CG candidate; VET hardest).

## Question
Does a LEARNED text->role encoder that outputs into a FIXED VSA (FHRR) binding space generalize to HELD-OUT (filler, role) combinations where a FAIR LEARNED-FLAT baseline (same capacity + supervision) FAILS -- with the LOCUS of the win being the LEARNED encoder, not the free binding algebra?

## Prior-work check (KB, cosine>0.30)
Top hits `preregs/2026-07-03_stage2 ARM (B)` (cos 0.50) + `preregs/2026-06-24_shotgun ARM 2` (cos 0.45) are FIXED-VSA held-out (role,filler) recovery with a RANDOM-UNBIND baseline = the free-algebra property (29399), NOT a learned encoder vs a fair learned-flat baseline. This cell is genuinely novel on the load-bearing axis: LEARNED-locus + fair learned-flat baseline + learning curve + tied-emb construction-check.

## Dataset + held-out-combination split protocol
- 24 noun concepts partitioned (deterministic sorted): both[0-7] (train agent+patient), agent_only[8-15] (train agent; test as PATIENT), patient_only[16-23] (train patient; test as AGENT). 12 verbs. FHRR N=1024 (phasor / complex64).
- Sentence = (agent_concept, patient_concept, verb). Role assignment structural (given identically to both arms). Learned locus = the noun->concept embedding (random init; learned from supervision; the learning curve = its convergence).
- TRAIN sampler never draws agent from patient_only nor patient from agent_only (split integrity by construction; asserted in self_test). Held-out test = NOVEL (concept, role): concept seen only as agent tested as patient (and vice versa). The ANSWER (concept in that role) never appears in training -> non-tautological (29423 bar).
- In-dist test = disjoint TRIPLES from train, same concept-role distribution (measures in-dist generalization, not memorization).

## Arms (one variable A vs B = readout: binding on/off; identical data+supervision)
- A `native_bind_shared`: FHRR binding readout, SHARED noun-emb across roles. [MECHANISM]
- B `flat`: per-role classifier heads over pooled features, handed the role-sorted structure + MORE params. NO binding. [FAIR BASELINE]
- C `native_bind_scramble`: LESION of trained A -- encode with correct roles, decode with RANDOM role keys. [MUST-FAIL: binding load-bearing]
- D `native_bind_tied`: binding readout but role-SPECIFIC emb tables. [LIVE-ALT / construction-check: binding alone insufficient]

## Pre-registered bands (primary discriminator = held-out compgen accuracy on the NOVEL role slot)
- HARD_PASS (all): native_heldout>=0.70 AND flat_heldout<=0.40 AND gap>=0.30 AND both in-dist>=0.80 AND learning-curve-rise(native heldout final-init)>=0.30 AND native_heldout_init<0.60 (not free-algebra) AND scramble_heldout<=0.10 (binding load-bearing) AND tied_heldout<=0.40 (shared-emb factorization load-bearing).
- HARD_FAIL: native_heldout<=0.40 OR gap<=0.10 OR flat_heldout>=0.70 (task not testing compgen; redesign) OR native_heldout_init>=0.60 (free-algebra) OR scramble_heldout>0.20 (binding not load-bearing).
- MIDDLE_BAND: otherwise.
- chance = 1/24 = 0.042.

## Two load-bearing risks + design-against
1. 29399 FREE-ALGEBRA TRAP: guarded by (a) learning curve (native heldout rises from chance = learned), (b) arm D tied-emb (binding + role-specific emb FAILS held-out -> the free algebra alone does NOT solve it; the LEARNED shared-embedding factorization is the locus), (c) scramble lesion -> chance.
2. CONSTRUCTION-DETERMINISM: flat is a FAIR strong baseline (handed role structure, MORE params) that ACES in-dist (genuinely trained, not a strawman) and fails held-out for a transparent reason (per-role heads share no filler identity across roles). Arm D is a live alternative where native-bind ALSO fails.

## Compute architecture
- Class (b) sequential-CPU with justification: torch-batched training, tiny (N=1024, 24 concepts), total wall < 2min for 3 seeds x 4 arms; no GPU speedup needed at this scale. device='cpu' default (runner passes no argv).
- Storage strategy: no_store_inmemory_codebook (learned-encoder cell; fixed codebook is an in-memory matrix, no atom store, no chained retrieval).

## Schema-vet fields
- arms_differ_verified: true (META_RULE_AF hash-test over 4 arms; 4 distinct digests).
- final_metrics_atomicity: tmp_replace (META_RULE_AH).
- except-ordering: SystemExit/KeyboardInterrupt raise before except Exception (no BaseException / no bare except).
- crlb_n/a: cleanup among 24 near-orthogonal FHRR at N=1024 is not the bottleneck (learning is); discriminator reachability confirmed at smoke.
- baseline_in_band: flat in-dist ~1.0 (proves capable/trained); flat held-out 0.0 is the intended CAN-FAIL result (not an AG regime problem -- the discriminator is held-out where flat fails, native rises).
- cardinality_ok: true (EXPECTED_N_UNITS = 3 seeds x 4 arms = 12).
- calibration_check: default_ok_for_this_regime (clean synthetic codebook; separation is the mechanism claim).
- deterministic_seeding: true (fixed int seeds + sorted() splits + np.random.default_rng(seed); no hash()-seeded RNG or list(set()) ordering).
- progress_logging: print_flush_true (timeout << 1800s; cell runs <2min).
- discriminator survives scale: full-N params used at smoke (single seed) -> discriminator fires identically.

## Self-test (non-tautological)
FHRR involution cos>0.99; scramble-fires (random decode key -> ~chance); SPLIT integrity (no held-out (concept,novel_role) in train; in-dist disjoint from train triples); learning-curve responds (native heldout <0.30 at init, rises >0.20 on a tiny run); arms-differ (4 distinct digests); native beats flat on held-out.

## Honest caveat (for VET)
Effect is SATURATED-clean (gap ~1.0) because the synthetic task has no lexical ambiguity/noise -- the result PROVES the mechanism (native binding delivers systematic role-filler generalization where flat fails, with a LEARNED locus) but the MAGNITUDE is construction-favorable. The non-construction-determined, load-bearing evidence is the three controls (learning curve rises; tied-emb fails; scramble collapses) + the fair flat baseline. Natural follow-up (quantify degradation): add lexical ambiguity / synonymy / noise and sweep to find where native's advantage erodes.
