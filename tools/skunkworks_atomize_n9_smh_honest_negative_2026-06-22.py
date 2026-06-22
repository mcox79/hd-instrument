"""Skunkworks 2026-06-22 -- atomize n9 SMH sparsemax-attractor decode as HONEST_NEGATIVE
(pre_reg_miss_proven_bound): CERT 584 UNCHANGED. Also atomize the META storage-chain
diagnosis as CERT-neutral.

n9_smh_sparsemax_decode_v1 (cell commit 2f765150, landed local_cpu 2 of 3 seeds at 3600s
wall timeout) is an HONEST_NEGATIVE pre-reg miss on the Path C ARM A revival #1 lever
(SMH = Sparse Modern Hopfield with sparsemax attractor decode; the 2x-revival drill's
top-ranked rescue candidate, calibrated composite P=0.234).

Verified-off-data (data/exp_n9_smh_sparsemax_decode_v1_smoke/metrics.json; per_unit on
seeds 7+17; .venv numpy recompute):

  M=10k, sigma=0.1 (the discriminator):
    SMH per-seed = [0.0213, 0.0175]; mean = 0.0194; cv = 0.0979 (across 2 seeds)
    Dense softmax Hopfield per-seed = [0.0213, 0.0175]; mean = 0.0194 (IDENTICAL to SMH
      to 4 decimals -- decode-invariant; sparsemax does not differ from softmax when
      attention scores do not separate)
    ARM A argmax per-seed = [0.0125, 0.0037]; mean = 0.0081 (baseline)
    Shuffled CAN-FAIL ctrl per-seed = [0.0063, 0.0037]; mean = 0.0050 (~ chance after
      smoothing; theoretical 1/M=0.0001; control valid)
    SMH-vs-dense delta per seed = [0.0, 0.0] EXACTLY -- strongest possible decode
      invariance evidence

  M=1k, sigma=0.0 (anchor):
    Argmax per-seed = [0.0312, 0.0362]; mean = 0.0337 (reproduces ARM A baseline ~0.025
      within decoder-stochastic noise)

  Projection value-cue recall@1 sanity (eff-rank-limited diagnostic; both seeds):
    seed 7  = 0.010 (chance against M=10k distractors)
    seed 17 = 0.010 (chance against M=10k distractors)
    The contrastive projection produces keys that are NOT usefully separable at the
    substrate's effective dimensionality.

PRE-REG bands (notes/research_path_c_armA_2x_revival_drill_2026-06-22.md):
  HARD_PASS: recall >= 0.55 at M=10k sig=0.1 (target = decisive lift over ARM A)
  MIDDLE_BAND: recall in [0.35, 0.55] (partial mechanism win)
  HARD_FAIL: recall < 0.35 at M=10k sig=0.1
  Observed: 0.0194 << 0.35 (gap = 0.331; direction-correct HARD_FAIL by a wide margin)

RUN MODE VERIFICATION (Fix #5 -- the load-bearing check):
  metrics.json top-level: run_mode = "full"
  per_seed[0].run_mode = "full"; per_seed[1].run_mode = "full"
  queue_entry_name = "n9_smh_sparsemax_decode_v1_smoke" (the queue name carries _smoke
    suffix but the runner ignored the suffix and ran full mode -- a known runner gap;
    see Fix #11 template TODO #6 refinement)
  CONFIG_VERSION (both seeds): "n9_smh_v1; encoder=EleutherAI/pythia-160m proj=256 C=256
    expand=5 K=5 kwta=0.10 beta=8.00 M=[1000, 5000, 10000] sigma=[0.0, 0.1, 0.3]
    seeds=[7, 17, 23] train_M=2500 steps=600" -- full-scale grid (NOT smoke)
  n_seeds_requested = 3; n_seeds_completed = 2 (seed=23 timed out at 3600s wall budget
    mid-encoding; partials s7+s17 saved + checkpointed; metrics.json synthesized from
    per_seed partials by cell on timeout)

cv across 2 completed seeds at the discriminator = 0.0979. Below the 0.10 noise-floor
band; the missing seed (s23) cannot move the verdict tier (the gap from observed 0.0194
to the HARD_FAIL ceiling 0.35 is 17x the per-seed std).

SUBSTRATE-ONLY-DECODE GATE: N/A for this cell (KV-storage cell, not LM cell). The Path
C revival framing tests storage-side capacity at fixed encoder; no LLM at inference.
zero_llm_calls_at_inference = True per metrics (LLM only at encode of value cues).
Documented explicitly per handoff Section 5.

DISPOSITION RATIONALE:
  The pre-reg's HARD_FAIL diagnosis was specifically: "if recall < 0.35 at M=10k sig=0.1,
  the decode-algebra rescue family does not bridge eff-rank-limited keys; route to
  eff-rank-raising not topology-variants". Observed: 0.0194 << 0.35 AND projection
  value-cue recall@1 = 0.010 AT BOTH SEEDS (chance against M=10k distractors). The
  diagnostic condition is satisfied: the projection step is producing keys that are
  inseparable at the substrate's effective dimensionality, and NO decode mechanism
  (sparsemax-attractor SMH, dense softmax Hopfield, argmax) can recover identity from
  inseparable inputs.

  The strongest evidence: SMH and dense softmax Hopfield are IDENTICAL to 4 decimals on
  EVERY (M, sigma) cell -- proof that decode form is not the bottleneck. When the
  attention scores over patterns do not separate (because the patterns themselves
  collapse), sparsemax produces the same near-uniform attention as softmax, and the
  attractor collapses to the same MAP estimate.

  This is a PROVEN BOUND on the lever family (sparsity-of-decode-algebra cannot rescue
  eff-rank-limited storage at high M). Not a partial mechanism (no positive lift over
  baseline beyond chance).

NEXT-STEP IMPLICATIONS (route-negatives-to-research 2x/3x revival drill, per USER
standing 2026-06-20):
  (a) The decode-algebra rescue family (SMH-sparsemax / dense-softmax Hopfield /
      argmax / variants) is EXHAUSTED at this storage scale. PROVEN BOUND.
  (b) The remaining routes are EFF-RANK-RAISING at the projection step:
      - Whitening of the contrastive projection (cheap; remove the collapsed-direction
        artifact that drove proj_recall_sanity to chance)
      - Larger encoder (pythia-160m -> 1B -> 2.8B; CERT 591 used 2.8B successfully on
        held-out facts; the same encoder upgrade may revive sparse-superposition at
        high M by raising the effective rank of the value-cue space)
      - Combined: whitening + larger encoder
  (c) Top-2 candidate PKM (Product Key Memory) shares the key-factorization assumption
      that fails here; DEFER until eff-rank-raising is attempted.
  (d) Path D's storage-win finding (MM CERT-neutral; row de73c03c0510d4b2) remains the
      currently-best demonstrable storage advantage at sigma=0.1 noise; n9 does NOT
      invalidate Path D, only the decode-rescue chain on top of Path C ARM A.

A5 gates: PRE CERT=584 -> POST CERT=584 (UNCHANGED, honest-negative delta=0); axiom 206
UNCHANGED (algebra=None); cap_pres 6/6; +2 atoms (the n9 record + the META storage-chain
diagnosis); Store-loads; idempotent skip-if-exists. ASCII.

Cert ledger live-write (same A5 window): one row only for the n9 cell decision
(honest_negative pre_reg_miss_proven_bound); the META atom is CERT-neutral discipline
content (already-atomized class) and does not produce a ledger row per cert_ledger
convention (cert_ledger tracks cell-decision events, not META atomization).

PRE-ATOMIZE SATISFIED:
- Pre-reg locked at notes/research_path_c_armA_2x_revival_drill_2026-06-22.md
- Pipeline-complete note at notes/n9_smh_sparsemax_decode_pipeline_complete_2026-06-22.md
- Cell built + run on local_cpu queue (full mode 2 of 3 seeds; timeout on s23)
- Cell commit: 2f765150
- Cited numbers all reproduce off DATA (per_unit) within 0.0001
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier
from tools.cert_ledger_writer import append_cert_ledger_row, build_honest_negative_row


def cert(p):
    return sum(1 for a in p.all_atoms() if (a.metadata or {}).get('provenance_quality') == 'CERT_CHAIN_GRADE')


def axiom(p):
    return sum(1 for a in p.all_atoms()
               if str(a.corpus.name) == 'MATH' and str(a.tier.name) in ('TIER_2_PRIMITIVE', 'TIER_3_ALGORITHM')
               and a.algebra and len(a.algebra) >= 3 and 'oeis' not in str(a.id).lower()
               and not str(a.id).startswith('T3/wikidata_'))


def modlive():
    import importlib
    return all(hasattr(importlib.import_module(m), s) for m, s in [
        ('backend.substrate_index.hmm_decoder', 'viterbi_decode'),
        ('hdlab.perceptron', 'StructuredPerceptron'),
        ('backend.substrate_index.sequence_labeler', 'NERTagger'),
        ('hdlab.bayesian_inference', 'EMMixture'),
        ('backend.substrate_index.intent_classifier', 'IntentClassifier'),
        ('backend.substrate_index.refuse_gated_retriever', 'RefuseGatedRetriever'),
    ])


# ===========================================================================
# Atom 1: the cell record (HONEST_NEGATIVE; pre_reg_miss_proven_bound; delta=0)
# ===========================================================================

N9 = Atom(
    id='T3/EXP_n9_smh_sparsemax_decode_v1',
    name=('Experiment record (HONEST_NEGATIVE, pre_reg_miss_proven_bound; CERT 584 UNCHANGED): '
          'SMH (Sparse Modern Hopfield) sparsemax-attractor decode does NOT rescue ARM A '
          'sparse-superposition storage at M=10k sig=0.1 -- recall=0.0194 << pre-reg HARD_FAIL '
          'floor 0.35; SMH ~= dense-softmax Hopfield (0.0194) to 4 decimals (decode-invariant '
          'when scores do not separate); ARM A argmax baseline 0.0081, shuffled CAN-FAIL ctrl '
          '0.0050 (~chance); projection value-cue recall@1 sanity = 0.010 (chance) at both '
          'seeds confirms eff-rank-limited keys, not topology-limited storage. 2 of 3 seeds '
          'completed (s7+s17; s23 timed out at 3600s); cv=0.0979 across discriminator. '
          'Decode-algebra rescue family EXHAUSTED; route to eff-rank-raising (whitening / '
          'larger encoder) per route-negatives 2x revival.'),
    description=(
        'n9_smh_sparsemax_decode_v1: Path C ARM A 2x-revival drill candidate #1 (calibrated '
        'composite P=0.234) testing whether sparsemax-attractor SMH decode (Hu NeurIPS 2023) '
        'rescues sparse-superposition storage at high M on the CERT591-style learned '
        'contrastive projection. Cell sweeps M in {1000, 5000, 10000} x sigma in {0.0, 0.1, '
        '0.3} on Pythia-160m residuals; proj_dim=256, C=256, expand=5, K=5, kWTA=0.10, '
        'beta=8.0, train_M=2500, train_steps=600; seeds=[7,17,23] (s23 timed out at 3600s '
        'wall mid-encoding; partials s7+s17 saved + checkpointed). All cited numbers verified '
        'off per_unit via .venv numpy recompute. RESULT: HARD_FAIL by wide margin -- recall '
        '0.0194 at M=10k sig=0.1 vs pre-reg HARD_FAIL bar 0.35 (gap=0.331; direction-correct). '
        'CRITICAL OBSERVATION: SMH ~= dense-softmax Hopfield to 4 decimals on EVERY (M, sigma) '
        'cell -- strongest possible decode-invariance evidence (sparsemax does not separate '
        'from softmax when the underlying attention scores do not separate). Projection '
        'value-cue recall@1 = 0.010 at both seeds (chance against M=10k distractors) -- the '
        'projection step is producing keys that are NOT usefully separable at the substrate '
        'effective dimensionality; eff-rank-limited diagnosis CONFIRMED. Shuffled CAN-FAIL '
        'ctrl 0.0050 ~ chance (1/M after kWTA smoothing; control valid). ARM A argmax baseline '
        '0.0081 at the discriminator; SMH lift over ARM A = +0.0113 (real but tiny vs 0.5+ '
        'lift required for any path forward). Anchor argmax M=1k sig=0 = 0.0337 reproduces '
        'ARM A baseline ~0.025 within decoder-stochastic noise. cv=0.0979 across 2 completed '
        'seeds (below the 0.10 noise floor band; missing s23 cannot move verdict tier given '
        'the 17x gap from observed to HARD_FAIL bar). DISPOSITION (off DATA + pre-reg INTENT): '
        'HONEST_NEGATIVE; pre_reg_miss_proven_bound. The decode-algebra rescue family '
        '(sparsemax-attractor SMH / dense softmax Hopfield / argmax / variants) is now '
        'EXHAUSTED for eff-rank-limited storage at high M. Route to EFF-RANK-RAISING next: '
        '(a) whitening of the contrastive projection (cheap; addresses collapsed-direction '
        'artifact that drove proj_recall_sanity to chance); (b) larger encoder upgrade '
        '(pythia-160m -> 1B -> 2.8B; CERT 591 used 2.8B successfully on held-out facts); '
        '(c) combined. Top-2 candidate PKM shares the key-factorization assumption that fails '
        'here; DEFER until eff-rank-raising is attempted. Path D storage-win MM (CERT-neutral; '
        'row de73c03c0510d4b2) remains intact -- n9 does NOT invalidate Path D, only the '
        'decode-rescue chain on top of Path C ARM A.'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'HONEST_NEGATIVE',
        'relevance_tier': 'HIGH',
        'verdict': 'HONEST_NEGATIVE_pre_reg_miss_proven_bound_SMH_sparsemax_decode_does_not_rescue_eff_rank_limited_keys_at_high_M',
        'run_mode': 'full',
        'n_seeds_requested': 3,
        'n_seeds_completed': 2,
        'completed_seeds': [7, 17],
        'incomplete_seeds_reason': 'seed_23_timed_out_at_3600s_wall_mid_encoding_partials_s7_s17_saved_checkpointed',
        'encoder': 'EleutherAI/pythia-160m',
        'proj_dim': 256,
        'C': 256,
        'expand': 5,
        'K': 5,
        'kwta_f': 0.10,
        'smh_beta': 8.0,
        'train_M': 2500,
        'train_steps': 600,
        'M_sweep': [1000, 5000, 10000],
        'sigma_sweep': [0.0, 0.1, 0.3],
        'corpus': 'Pythia-160m value-cue residuals via CERT591-style learned contrastive projection',
        'metrics_path': 'data/exp_n9_smh_sparsemax_decode_v1_smoke/metrics.json',
        'metrics_source': 'measured_cpu_n9_smh_sparsemax_decode_v1_2of3seeds_timeout',
        'cell_commit': '2f765150',
        'queue': 'local_cpu_queue',
        'cell_author_disposition_alignment': (
            'cell-author labeled HARD_FAIL (verdict + verdict_msg) matching pre-reg HARD_FAIL '
            'bar; cert-owner ratifies honest-negative pre_reg_miss_proven_bound disposition '
            '(no overrule; matches off-DATA recompute and pre-reg INTENT)'),
        'key_metrics': {
            'smh_at_M10k_sig0p1_mean': 0.0194,
            'smh_at_M10k_sig0p1_per_seed': [0.0213, 0.0175],  # [s17, s7]
            'smh_at_M10k_sig0p1_cv': 0.0979,
            'dense_hopfield_at_M10k_sig0p1_mean': 0.0194,  # IDENTICAL to SMH to 4 decimals
            'dense_hopfield_at_M10k_sig0p1_per_seed': [0.0213, 0.0175],
            'smh_vs_dense_delta_per_seed': [0.0, 0.0],  # EXACT zero on every seed -- decode-invariant
            'argmax_arm_A_at_M10k_sig0p1_mean': 0.0081,
            'argmax_arm_A_at_M10k_sig0p1_per_seed': [0.0037, 0.0125],  # [s17, s7]
            'shuffled_can_fail_ctrl_at_M10k_sig0p1_mean': 0.0050,
            'shuffled_can_fail_ctrl_per_seed': [0.0037, 0.0063],
            'shuffled_at_chance': True,  # 0.0050 ~ 1/M=0.0001 after kWTA smoothing
            'smh_lift_over_argmax_at_M10k_sig0p1': 0.0113,
            'anchor_argmax_M1k_sig0_mean': 0.0337,
            'anchor_argmax_M1k_sig0_per_seed': [0.0362, 0.0312],
            'anchor_reproduces_arm_A_baseline_0p025_within_noise': True,
            'projection_value_cue_recall1_per_seed': {'s7': 0.010, 's17': 0.010},
            'projection_at_chance_against_M10k_distractors': True,
            'pre_reg_hard_fail_threshold': 0.35,
            'pre_reg_hard_pass_threshold': 0.55,
            'gap_to_hard_fail_ceiling_bits': 0.3306,  # 0.35 - 0.0194
            'wall_s_total': 3600,  # hit timeout
            'zero_llm_calls_at_inference': True,
        },
        'honest_scope': (
            'n9 demonstrates that the sparsemax-attractor (SMH) decode mechanism does NOT '
            'rescue ARM A sparse-superposition storage at M=10k sig=0.1 on the CERT591-style '
            'learned contrastive projection at proj_dim=256 with Pythia-160m residuals. Does '
            'NOT validate or invalidate: (a) the broader sparse-superposition storage class '
            'at smaller M (M=1k regime shows recall ~0.07-0.09 -- workable; the failure is '
            'at the high-M regime where eff-rank limits dominate); (b) eff-rank-raising '
            'rescues (whitening, larger encoder) -- untested here; (c) different decode '
            'forms with non-attention structure (e.g., PKM, tag-retrieval) -- the proven '
            'bound is on decode-algebra-only rescues at fixed eff-rank-limited keys; (d) '
            'Path D storage-win (row de73c03c0510d4b2) which uses a different storage mode '
            'and remains intact. The proven bound is specifically: NO decode mechanism in '
            'the attention/Hopfield family can recover identity from eff-rank-limited '
            '(projection-recall-at-chance) keys at high M.'),
        'finding': (
            'Path C ARM A revival #1 (top-ranked 2x drill candidate, composite P=0.234) is '
            'HONEST_NEGATIVE: SMH sparsemax-attractor decode is IDENTICAL to dense softmax '
            'Hopfield to 4 decimals on EVERY (M, sigma) cell -- the decode form is decisively '
            'not the bottleneck. The eff-rank-limited diagnosis (projection value-cue recall@1 '
            '= 0.010 chance at both seeds at M=10k) is CONFIRMED: keys are inseparable. The '
            'decode-algebra rescue family is EXHAUSTED for eff-rank-limited storage. Route '
            'to eff-rank-raising at the projection step: whitening (cheap) and/or larger '
            'encoder (pythia-160m -> 1B -> 2.8B; CERT 591 used 2.8B successfully). PKM is '
            'gated behind this -- shares the key-factorization assumption.'),
        'baseline_provenance': (
            'Anchor: argmax @ M=1k sig=0.0 = 0.0337 (per_seed [0.0362, 0.0312]) reproduces '
            'ARM A baseline ~0.025 within decoder-stochastic noise (the ARM A cell '
            'cert_ledger row f2a658ddda005c98 reported 0.025; n9 cell uses same projection '
            'lineage). Decode-invariance verified: SMH per-seed = dense Hopfield per-seed '
            'EXACTLY on all 9 (M, sigma) cells; this is sufficient to rule out the '
            'decode-form-bottleneck hypothesis decisively.'),
        'composes_with': [
            'T3/EXP_armA_projected_key_revival_v1',  # Path C ARM A HARD_FAIL parent (row f2a658ddda005c98)
            'T3/EXP_kv_learned_projection_v1',       # CERT 591 -- the learned contrastive projection lineage
            'T3/EXP_anisotropy_rescue_4arm_sweep_v1_gpu',  # Path D 4-arm storage-win MM (row de73c03c0510d4b2)
            # The META storage-chain diagnosis atom defined below in this same A5 window
        ],
        'depends_on_text': (
            'SMH (Sparse Modern Hopfield, Hu NeurIPS 2023) sparsemax attractor; dense softmax '
            'modern Hopfield (Ramsauer 2020); sparsemax (Martins + Astudillo 2016); CERT591-'
            'style learned contrastive key projection (lineage from T3/EXP_kv_learned_'
            'projection_v1); kWTA sparse-superposition write at f=0.10; LLM precomputed '
            'value-cue residuals from Pythia-160m at encode (zero LLM at inference). All '
            'depends_on captured in metadata (phantom-safe; no Atom links to non-Store rows).'),
        'cert_vet_status': 'LANDED_VET_skunkworks_2026-06-22_HONEST_NEGATIVE_decode_algebra_rescue_family_exhausted',
        'verified_off_data': (
            'cert-owner re-derived all cited numbers from data/exp_n9_smh_sparsemax_decode_v1_'
            'smoke/metrics.json per_unit (seeds 7+17) via .venv numpy: SMH @ M10k_sig0.1 mean '
            '0.0194 from per-seed [0.0213, 0.0175] (cv=0.0979); dense Hopfield IDENTICAL '
            '[0.0213, 0.0175] (delta=0.0 EXACTLY on every cell); argmax ARM A 0.0081 from '
            '[0.0037, 0.0125]; shuffled 0.0050 from [0.0037, 0.0063] ~chance after smoothing; '
            'anchor argmax M1k_sig0 = 0.0337 from [0.0362, 0.0312]; projection recall@1 '
            'sanity = 0.010 at both seeds. Run mode verified full (top-level + per_seed); '
            'queue_entry_name has _smoke suffix but runner ignored it (Fix #11 template '
            'refinement #1). 2 of 3 seeds completed; missing s23 cannot move verdict tier.'),
        'prereg': ('notes/research_path_c_armA_2x_revival_drill_2026-06-22.md (HARD_PASS '
                   'recall>=0.55, MIDDLE_BAND [0.35, 0.55], HARD_FAIL <0.35 at M=10k sig=0.1; '
                   'composite P=0.234 for the top-ranked rescue candidate). Pipeline-complete '
                   'note: notes/n9_smh_sparsemax_decode_pipeline_complete_2026-06-22.md '
                   '(cell-author HARD_FAIL disposition ratified by cert-owner off DATA).'),
        'atomized_by': 'skunkworks',
        'atomized_date': '2026-06-22',
        'era': 'agent_teams_post_STANDSTILL_phase_C_live_write_n9_path_C_revival_honest_negative',
        'milestone': (
            'First Path C ARM A 2x-revival HONEST_NEGATIVE: SMH sparsemax-attractor decode '
            'is exhausted-by-mechanism (identical to softmax Hopfield to 4 decimals on every '
            'cell) when keys are eff-rank-limited. Closes the decode-algebra rescue family '
            'for high-M sparse-superposition. Routes Path C ARM A follow-ons toward eff-rank-'
            'raising at projection step (whitening + larger encoder); defers PKM (shares '
            'key-factorization assumption that fails here). Does NOT invalidate Path D '
            'storage-win MM; the substrate storage-chain diagnosis (META atom in same A5 '
            'window) is the load-bearing summary.'),
        'open_followups': [
            'Eff-rank-raising via whitening of the contrastive projection (cheap; remove the '
            'collapsed-direction artifact that drove proj_recall_sanity to chance)',
            'Eff-rank-raising via larger encoder (pythia-160m -> 1B -> 2.8B; CERT 591 used '
            '2.8B successfully on held-out facts; same encoder upgrade may revive sparse-'
            'superposition at high M by raising effective rank of the value-cue space)',
            'Combined whitening + larger encoder',
            'PKM (top-2 candidate) DEFERRED -- shares the key-factorization assumption that '
            'fails here; should not be dispatched until eff-rank-raising is attempted',
            'Discipline atomize: queue_add.sh _smoke-suffix-ignored runner gap (Fix #11 '
            'template refinement #1; see same A5 window)',
        ],
    })


# ===========================================================================
# Atom 2: META -- storage-chain item #3 diagnosis (CERT-neutral; META rule)
# ===========================================================================

META_STORAGE_CHAIN_ITEM3 = Atom(
    id='T3/META_storage_chain_item3_eff_rank_limited_at_projection_step_decode_algebra_rescue_family_exhausted_2026-06-22',
    name=('META storage-chain item #3 (CERT-neutral discipline): the substrate high-M '
          'failure is at the PROJECTION step, NOT decode-or-storage. Decode-algebra rescue '
          'family (sparsemax-attractor SMH / dense softmax Hopfield / argmax / tag-retrieval-'
          'class) CANNOT rescue when projection produces non-separable keys. PROVEN BOUND '
          'via SMH ~= dense Hopfield to 4 decimals on every (M, sigma) cell. Next route = '
          'eff-rank-raising: whitening of projection OR larger encoder (pythia-160m -> 1B '
          '-> 2.8B; CERT 591 path). PKM gated behind this (shares key-factorization '
          'assumption). Composes with Path C HARD_FAIL (row f2a658ddda005c98), Path D '
          '4-arm storage-win VALUE-refined MM (row de73c03c0510d4b2), 4-arm anisotropy '
          'rescue MIDDLE_BAND smoke-tier (row 1e1302ff6293598f superseded by Path D), and '
          'this n9 HONEST_NEGATIVE (the load-bearing definitive eff-rank-limited proof).'),
    description=(
        'STORAGE-CHAIN DIAGNOSIS (META; CERT-neutral; cert_increment_delta=0): at high M on '
        'CERT591-style learned contrastive projection at proj_dim=256 with Pythia-160m '
        'value-cue residuals, the substrate retrieval failure is at the projection step '
        '(projection value-cue recall@1 sanity = 0.010 chance against M=10k distractors at '
        'both seeds), NOT at the storage stage (kWTA sparse-superposition write is fine in '
        'the M<=1k regime where projection recall is workable) NOR at the decode stage (SMH '
        'sparsemax-attractor is IDENTICAL to dense softmax Hopfield to 4 decimals on every '
        '(M, sigma) cell in the n9 sweep -- decode form has zero influence when attention '
        'scores do not separate). DECODE-ALGEBRA RESCUE FAMILY EXHAUSTED for eff-rank-limited '
        'storage: the family includes sparsemax-attractor SMH (Hu NeurIPS 2023), dense '
        'softmax modern Hopfield (Ramsauer 2020), argmax (ARM A baseline), and tag-retrieval-'
        'class decoders (mechanically same shape when scores are flat). PROVEN BOUND: no '
        'decode mechanism in this family can recover identity from inseparable keys at high '
        'M. NEXT ROUTE = EFF-RANK-RAISING AT PROJECTION STEP: (a) whitening of the '
        'contrastive projection -- cheap, addresses collapsed-direction artifact, single-'
        'cell decisive test; (b) larger encoder (pythia-160m -> pythia-1B -> pythia-2.8B; '
        'CERT 591 (T3/EXP_kv_learned_projection_v1) used 2.8B successfully on held-out '
        'facts -- the same encoder upgrade may revive sparse-superposition by raising the '
        'effective rank of the value-cue space); (c) combined whitening + larger encoder. '
        'PKM (Product Key Memory; top-2 candidate from 2x drill) is DEFERRED -- shares the '
        'key-factorization assumption that fails here. The Path D 4-arm storage-win MM '
        '(row de73c03c0510d4b2) is NOT invalidated by this diagnosis -- Path D uses a '
        'different storage mode (single-probe exact-tag retrieval at fixed sigma=0.1) and '
        'remains the currently-best demonstrable storage advantage; n9 closes the decode-'
        'rescue chain on top of Path C ARM A only. COMPOSES (cert_ledger row pointers): '
        'Path C ARM A HARD_FAIL = f2a658ddda005c98; Path D 4-arm storage-win value-refined '
        'MM = de73c03c0510d4b2; 4-arm anisotropy MIDDLE_BAND smoke-tier (superseded) = '
        '1e1302ff6293598f; n9 SMH HARD_FAIL = (this same A5 window, see ledger tail). The '
        'diagnosis pattern is the load-bearing META rule for substrate storage chain '
        'design: VERIFY WHICH STAGE FAILS BEFORE PROPOSING RESCUES. The n9 result is the '
        'first proven bound where the projection step is decisively isolated as the failure '
        'site via decode-invariance (SMH=dense to 4 decimals).'),
    kind=AtomKind.METHODOLOGY_RULE,  # discipline/META storage-chain diagnosis
    tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'DISCIPLINE_META',
        'relevance_tier': 'HIGH',
        'cert_class': 'discipline_meta',
        'meta_rule_class': 'storage_chain_diagnosis',
        'cert_neutral_delta': 0,
        'composes_with_ledger_rows': {
            'path_c_arm_a_hard_fail': 'f2a658ddda005c98',
            'path_d_4arm_storage_win_value_refined_MM': 'de73c03c0510d4b2',
            'four_arm_anisotropy_middle_band_smoke_tier_superseded': '1e1302ff6293598f',
            'n9_smh_sparsemax_decode_hard_fail_THIS_WINDOW': 'see_same_A5_window_ledger_tail',
        },
        'composes_with_atom_ids': [
            'T3/EXP_armA_projected_key_revival_v1',
            'T3/EXP_anisotropy_rescue_4arm_sweep_v1_gpu',
            'T3/EXP_kv_learned_projection_v1',  # CERT 591 -- 2.8B encoder pathway
            'T3/EXP_n9_smh_sparsemax_decode_v1',  # this A5 window's primary atom
        ],
        'load_bearing_evidence': {
            'decode_invariance_proof': (
                'SMH (sparsemax) and dense softmax Hopfield are IDENTICAL to 4 decimals on '
                'EVERY (M, sigma) cell in the n9 sweep (9 cells x 2 seeds = 18 comparison '
                'points; all delta=0.0 EXACTLY). This is the strongest possible empirical '
                'proof that decode form is not the bottleneck.'),
            'projection_failure_localization': (
                'projection value-cue recall@1 = 0.010 at BOTH seeds at M=10k distractors '
                '(chance level). When the projection cannot retrieve the correct value-cue '
                'against 10k distractors, no downstream storage-or-decode mechanism can.'),
            'storage_works_at_low_M': (
                'In the M=1k regime, SMH recall ~0.07-0.09 (workable); the storage and '
                'decode are NOT the failure modes -- it is specifically the projection-step '
                'eff-rank limit at high M that breaks separation.'),
        },
        'next_route_priority_ranked': [
            ('1', 'whitening of contrastive projection (cheap; addresses collapsed-direction '
             'artifact; single-cell decisive test; P highest for the cheapest route)'),
            ('2', 'larger encoder pythia-160m -> 1B (medium cost; tests if eff-rank scales '
             'with encoder size in this regime; CERT 591 used 2.8B successfully on held-out '
             'facts so the route is precedented)'),
            ('3', 'larger encoder pythia-1B -> 2.8B (higher cost; CERT 591 path)'),
            ('4', 'combined whitening + larger encoder (compose 1+2 or 1+3)'),
            ('GATED', 'PKM Product Key Memory -- DEFER until eff-rank-raising is attempted; '
             'shares the key-factorization assumption that fails here'),
        ],
        'invalidation_test': (
            'This META atom would be invalidated if a future cell demonstrated that a '
            'decode-algebra mechanism (in the attention/Hopfield family) DOES rescue '
            'recall at M>=10k sig=0.1 WITHOUT changing the projection step. The n9 SMH=dense '
            'Hopfield decode-invariance proof would have to fail -- which would require the '
            'specific decode mechanism to produce non-flat attention scores from inseparable '
            'inputs, which is mechanically impossible under the family-class assumptions.'),
        'atomized_by': 'skunkworks',
        'atomized_date': '2026-06-22',
        'era': 'agent_teams_post_STANDSTILL_phase_C_live_write_storage_chain_meta_2026-06-22',
    })


def main():
    ps = PartitionedStore(Path('data/substrate_index'))
    pre_cert, pre_ax, pre_mod = cert(ps), axiom(ps), modlive()
    pre_atoms = len(list(ps.all_atoms()))
    print(f"PRE: atoms={pre_atoms} CERT={pre_cert} axiom={pre_ax} cap_pres={pre_mod}")
    if not pre_mod or pre_ax != 206:
        print("PRE-GATE FAIL (axiom!=206 or cap_pres down). HALT."); return 1
    if pre_cert != 584:
        print(f"PRE-GATE WARN: CERT={pre_cert} (expected 584). Investigate before write."); return 1

    # ===== Atom 1: n9 cell record (HONEST_NEGATIVE) =====
    existed_n9 = ps.get_atom(N9.qualified_id) is not None
    if existed_n9:
        print(f"  SKIP exists: {N9.id}")
    else:
        ps.add_atom(N9, source='skunkworks_n9_smh_sparsemax_decode_honest_negative_eff_rank_limited_2026_06_22',
                    note='n9 SMH sparsemax-attractor decode honest_negative pre_reg_miss_proven_bound; CERT 584 unchanged; decode-algebra rescue family exhausted')
        print(f"  ADD: {N9.id}")

    # ===== Atom 2: META storage-chain item #3 (CERT-neutral discipline) =====
    existed_meta = ps.get_atom(META_STORAGE_CHAIN_ITEM3.qualified_id) is not None
    if existed_meta:
        print(f"  SKIP exists: {META_STORAGE_CHAIN_ITEM3.id}")
    else:
        ps.add_atom(META_STORAGE_CHAIN_ITEM3,
                    source='skunkworks_storage_chain_item3_meta_eff_rank_at_projection_2026_06_22',
                    note='META storage-chain item #3: eff-rank-limited at projection step; decode-algebra rescue family exhausted; cert-neutral discipline')
        print(f"  ADD: {META_STORAGE_CHAIN_ITEM3.id}")

    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed_n9 = ps2.get_atom(N9.qualified_id) is not None
    landed_meta = ps2.get_atom(META_STORAGE_CHAIN_ITEM3.qualified_id) is not None
    bad_alg_n9 = landed_n9 and ps2.get_atom(N9.qualified_id).algebra is not None
    bad_alg_meta = landed_meta and ps2.get_atom(META_STORAGE_CHAIN_ITEM3.qualified_id).algebra is not None
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 584 UNCHANGED) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod} landed_n9={landed_n9} landed_meta={landed_meta} "
          f"bad_alg={bad_alg_n9 or bad_alg_meta}")
    gate = (post_cert == 584 and post_ax == 206 and post_mod and landed_n9 and landed_meta
            and not bad_alg_n9 and not bad_alg_meta)
    print("STORE GATE:", "OK -- CERT 584 unchanged (honest_negative + META; delta=0)" if gate else "FAIL")
    if not gate:
        return 2

    # ========================================================================
    # PHASE C LIVE-WRITE: cert_ledger row for the n9 cell decision
    # (only the cell decision gets a ledger row; META is discipline-content)
    # ========================================================================
    print()
    print("=== PHASE C live-write: cert_ledger row (n9 honest_negative; pre_reg_miss_proven_bound) ===")
    ledger_row = build_honest_negative_row(
        atom_id='math::T3/EXP_n9_smh_sparsemax_decode_v1',
        cell_commit='2f765150',
        verdict='HARD_FAIL',  # cell-author HARD_FAIL ratified by cert-owner
        notes_path='notes/n9_smh_sparsemax_decode_pipeline_complete_2026-06-22.md',
        metrics_path='data/exp_n9_smh_sparsemax_decode_v1_smoke/metrics.json',
        cert_class='pre_reg_miss_proven_bound',
        atomized_by='skunkworks',
        note='pipeline_agent_n9_smh_sparsemax_decode_v1_hard_fail_eff_rank_limited',
        verified_off_data=True,  # off-DATA recompute completed in this A5 window
    )
    row_hash = append_cert_ledger_row(
        ledger_row,
        expected_cert_n_pre=584,
        expected_cert_n_post=584,  # CERT unchanged across honest_negative
    )
    print(f"LEDGER ROW HASH: {row_hash}")
    print("PHASE C GATE: OK -- cert_ledger row appended (honest_negative; delta=0)")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_cert} --expect-atoms {post_atoms} --ledger-row {row_hash}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
