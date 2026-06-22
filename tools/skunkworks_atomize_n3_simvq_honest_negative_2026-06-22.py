"""Skunkworks 2026-06-22 -- atomize n3 SimVQ-MVP as HONEST_NEGATIVE (proven_bound): CERT 584 UNCHANGED.

n3_vq_alignment_simvq_v1 (cell commit f5a0685a, landed FULL on remote_cpu 3 seeds 7/17/23) is an
HONEST_NEGATIVE pre-reg miss on the PRIMARY decode-side ceiling lever (SimVQ-MVP at PROJ_DIM=64,32
INCREASES ceiling_bpc vs identity instead of LOWERing it).

Verified-off-data (data/exp_n3_vq_alignment_simvq_v1/metrics.json; all 3 seeds via per_unit; .venv
numpy recompute):

  PROJ_DIM=768 (IDENTITY anchor; control):
    ceiling_bpc mean=2.0491 (matches N2 V_C=1024/N=16384/K=1 anchor 2.0491 EXACTLY -- same seeds
    same residuals same alg; anchor diff=0.0000 <<< pre-reg gate 0.05; PASSES anchor-OK)
    substrate_bpc mean=4.9743 (N2 anchor 4.9591; 0.0151 bits drift -- within decoder-stochastic noise)
    concept_top1=0.5423, ceiling_top1=0.7305, util=0.936, alpha=0.503 (NOT saturated)
    per seed ceilings=[2.069, 1.994, 2.084] cv=0.019

  PROJ_DIM=64 (PRIMARY SimVQ-MVP arm; the pre-reg HARD_PASS candidate):
    ceiling_bpc mean=2.2805 (HIGHER than identity by +0.231 bits -- ceiling got WORSE, not better)
    substrate_bpc mean=5.0298 (HIGHER than identity by +0.056 bits)
    concept_top1=0.5050 (DROPPED from 0.542; -0.037 -- coarser concepts at PD=64)
    util=0.956 (UP from 0.936 -- mechanically expected from low-d k-means)
    per seed ceilings=[2.327, 2.249, 2.265] cv=0.015 alpha=0.535

  PROJ_DIM=32 (more aggressive SimVQ-MVP arm):
    ceiling_bpc mean=2.4746 (HIGHER than identity by +0.426 bits -- ceiling WORSE, monotonic in
    the wrong direction; lower-d projection HURTS more)
    substrate_bpc mean=5.0691 (HIGHER by +0.095 bits)
    concept_top1=0.4776 (DROPPED 0.064 from identity)
    util=0.960, alpha=0.553 per seed ceilings=[2.502, 2.470, 2.452] cv=0.009

PRE-REG bands (notes/exp_dev_n3_simvq_pre_reg_2026-06-22.md):
  HARD_PASS: some PD has ceiling<=1.75 AND substrate<=4.75 AND cv<=0.05 AND not saturated -- FAILED
    (best non-identity ceiling=2.281, far from 1.75; substrate=5.030, far from 4.75)
  MIDDLE_BAND: ceiling drops 0.10-0.30 bits vs identity (intent: PARTIAL improvement) -- NOT MET
    (deltas are NEGATIVE: -0.231 at PD=64, -0.426 at PD=32 -- SimVQ-MVP made it WORSE)
  HARD_FAIL: ceiling change < 0.05 (no measurable difference) -- not strictly satisfied by abs()
    (abs deltas 0.231 and 0.426 are large) but the directional intent (improvement) is REVERSED

DISPOSITION RATIONAL: per the pre-reg INTENT (ceiling_delta = identity - simvq, +ve means SimVQ
helps), every non-identity arm produced a LARGE NEGATIVE delta -- SimVQ-MVP is anti-helpful in
this regime. This is a PROVEN BOUND on the lever, not a partial mechanism. The pre-reg's HARD_PASS
HYPOTHESIS (PCA-init projection separates token-heterogeneous residuals) is FALSIFIED at
V_C=1024/N=16384 (the calibrated P=0.40-0.45 was a coin-flip; came out the other way).

The cell-author labeled MIDDLE_BAND via the fallback at experiments/exp_n3_vq_alignment_simvq_v1.py
line 1151 ("small-effect ceiling_delta=%.3f (<0.10)"). That branch triggers for any
abs(delta)>=0.05 not meeting HARD_PASS or improvement-MIDDLE_BAND -- but in the negative-direction
case, the pre-reg INTENT was an HONEST_NEGATIVE proven bound, not a "partial mechanism". The
verdict_msg's MIDDLE_BAND label inflates the result. Cert-owner overrules the cell-author
disposition off DATA + off PRE-REG INTENT.

SUBSTRATE-ONLY-DECODE GATE: PASSED. zero_llm_calls_at_inference=True on all per_seed entries;
total_llm_forward_calls_observed=0; module-level counter assertion fires at selftest; no
model()/forward()/generate()/AutoModel/transformers in the cell (verified by grep + read).
At inference the cell uses only numpy + sklearn.cluster.MiniBatchKMeans.predict; Pythia residuals
were precomputed at ingest into data/exp_phase05_v1_.../residuals_per_token.npz.

TRAIN/TEST DISCIPLINE: PCA fit on L2-normalized train residuals only (fit_pca_projection line 272-297
on train_res_n derived from train_docs); MiniBatchKMeans fit on train_proj only (line 760);
km.predict applied to test_proj (no train-test leak). Codebook does NOT see heldout. CLEAN.

INTERPRETATION (load-bearing for next-step routing): the unsupervised PCA-init projection
DESTROYS variance directions that carry token-discriminating signal at V_C=1024. The high-variance
principal directions of Pythia residuals are not aligned with token-conditional structure (which is
consistent with the residual isotropy work in the substrate -- the residual stream's high-variance
axes are dominated by sentence-level / topic / register variation, NOT next-token contrast). MVP
SimVQ (frozen PCA basis) is the wrong form; only FULL SimVQ (W learned jointly with VQ assignment,
end-to-end gradient through a token-prediction objective) would have any chance of recovering the
ceiling.

Decode-side mechanism characterization (across PROJ_DIM):
  - Lower PROJ_DIM monotonically HURTS ceiling (768 -> 64 -> 32: 2.05 -> 2.28 -> 2.47).
  - substrate_bpc tracks ceiling_bpc but more weakly (768 -> 64 -> 32: 4.97 -> 5.03 -> 5.07).
  - The decode-side bottleneck hypothesis is INTACT (substrate-vs-ceiling gap is ~2.9 bits at
    every PD; the gap is concept-prediction-limited, not VQ-floor-limited at V_C=1024). But the
    SPECIFIC LEVER (PCA-init linear projection before MBK) goes the wrong way.
  - codebook_utilization mechanically tracks PROJ_DIM (lower d -> higher util by isotropy of
    low-d Voronoi; 0.936 -> 0.956 -> 0.960). Utilization gain comes at a ceiling cost.

NEXT-STEP IMPLICATIONS (for Director / Research, route as routing-not-author):
  (a) MKN drop-in (Research drill #2 lever, P(>=0.10 BPC gain)=0.55) is now the HIGHEST-PROBABILITY
      Path B lever. Pure smoothing replacement, no architecture change, composable with anything.
  (b) FULL SimVQ (learned W jointly with VQ via straight-through estimator or contrastive loss)
      is the natural revival per the pre-reg's deferred follow-on (notes/exp_dev_n3 line 33-34).
      P deflated from the MVP's 0.40-0.45 because the MVP empirically negative.
  (c) Path A (V_C=4096 x N=32768+) remains evidence-warranted per the pre-reg's Prediction 2
      ("if SimVQ HARD-FAILs, the substrate's decode floor is codebook-granularity-limited, and
      Path A becomes the only evidence-based next step"). The empirical landed deltas (negative
      monotonic with lower PD) BOLSTER this -- coarser projections worsen ceiling; finer codebook
      (more concepts) should help.
  (d) FSQ with PCA-aligned projection (Research alt lever, P=0.35-0.40) is at HIGH risk of the
      same PCA-misalignment failure; deflate to ~0.20 post-empirical.

A5 gates: PRE CERT=584 -> POST CERT=584 (UNCHANGED, honest-negative cert_increment_delta=0);
axiom 206 UNCHANGED (algebra=None); cap_pres 6/6; +1 atom; Store-loads; idempotent skip-if-exists. ASCII.

Cert ledger live-write: same A5 window via tools.cert_ledger_writer.build_honest_negative_row +
append_cert_ledger_row. Expected ledger 632 -> 633 (cert_ruling op).

PRE-ATOMIZE SATISFIED:
- SCHEMA-VET pre-reg locked at notes/exp_dev_n3_simvq_pre_reg_2026-06-22.md
- Research drill routing at notes/research_decode_side_lm_improvements_substrate_native_2026-06-22.md
- Cell built + run on remote_cpu full mode 3 seeds; metrics.json complete + per_unit populated
- Cell commit: f5a0685a
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


N3 = Atom(
    id='T3/EXP_n3_vq_alignment_simvq_v1',
    name=('Experiment record (HONEST_NEGATIVE, proven bound; CERT 584 UNCHANGED): SimVQ-MVP '
          '(PCA-init linear projection before MiniBatchKMeans) at PROJ_DIM in {32, 64} INCREASES '
          'ceiling_bpc vs identity (+0.231 at PD=64, +0.426 at PD=32) at V_C=1024 / N_DIM=16384 / '
          'K=1 / f=0.006 -- pre-reg HARD_PASS (ceiling<=1.75) and pre-reg MIDDLE_BAND-improvement '
          '(ceiling_delta>=+0.10) both FAILED; the unsupervised PCA-init lever is anti-helpful in '
          'this regime; substrate-only-decode gate PASSED (zero LLM calls at inference); anchor '
          'PD=768 reproduces N2 ceiling 2.0491 EXACTLY; 3 seeds cv<=0.02; first Path B HONEST_NEGATIVE.'),
    description=(
        'n3_vq_alignment_simvq_v1: Path B (decode-side improvement) MVP test of SimVQ-style linear '
        'projection BEFORE MiniBatchKMeans VQ, vs the N2 identity baseline. PCA-init projection W '
        '(residual_dim, proj_dim) fit on L2-normalized train residuals only; train+test residuals '
        'projected through W + L2-renormalized in projected space; MBK fit on train_proj then '
        'km.predict on test_proj (clean train/test discipline; no leak). Sweep PROJ_DIM in '
        '{768 [identity anchor], 64, 32}; 3 seeds (7, 17, 23); MAX_DOCS=100k Pythia-160m residuals '
        '(same corpus as N2). HYPOTHESIS (research drill 2026-06-22, calibrated P(>=0.30 BPC gain)'
        '=0.40-0.45): PCA projection separates residuals with heterogeneous token distributions '
        'into different Voronoi cells, reducing within-concept token entropy. RESULT: FALSIFIED. '
        'Every non-identity arm INCREASED ceiling_bpc monotonically in lower-d (PD=768: 2.049 -> '
        'PD=64: 2.281 -> PD=32: 2.475); substrate_bpc also INCREASED weakly (4.974 -> 5.030 -> 5.069); '
        'concept_top1 DROPPED (0.542 -> 0.505 -> 0.478) showing coarser projections degrade '
        'concept-prediction too. Pre-reg HARD_PASS bar (ceiling<=1.75) unattained by >0.5 bits. '
        'Pre-reg MIDDLE_BAND-improvement bar (ceiling_delta>=+0.10) FAILED in opposite direction '
        '(deltas NEGATIVE: -0.231, -0.426). Anchor PASSED: identity PD=768 ceiling_bpc=2.0491 '
        'reproduces N2 V_C=1024/N=16384/K=1 ceiling=2.0491 EXACTLY (same seeds, residuals, alg). '
        'Substrate-only-decode gate PASSED: zero_llm_calls_at_inference=True on every per_unit; '
        '_LLM_CALL_COUNTER assertion enforced at selftest + at metrics-write; module-level '
        'audit confirms zero model()/forward()/generate()/AutoModel/transformers at inference '
        '(Pythia residuals precomputed at ingest). Cross-seed cv=[ceiling: 0.009-0.019; '
        'substrate: 0.002-0.006] all <=0.05. Cell-author labeled MIDDLE_BAND via verdict() '
        'fallback (line 1151) -- a verdict-logic gap: the fallback treats large abs(delta) as '
        'MIDDLE_BAND regardless of direction, but pre-reg INTENT was MIDDLE_BAND=partial '
        'IMPROVEMENT (delta>=+0.10). Cert-owner overrules off DATA + pre-reg INTENT: every '
        'non-identity arm went the wrong way by a magnitude that constitutes a PROVEN BOUND, not '
        'a partial mechanism. INTERPRETATION: the high-variance PCA directions of Pythia residuals '
        'are dominated by sentence-level / topic / register variation, not next-token contrast; '
        'an unsupervised PCA-init projection is the wrong form. FULL SimVQ (W learned jointly with '
        'VQ via straight-through estimator or contrastive token-prediction loss) is the natural '
        'revival per the pre-reg deferred follow-on; the MVP empirical negative deflates its '
        'calibrated P. CERT-NEUTRAL (delta=0) but a genuine proven bound on PCA-init linear '
        'projection as a Path B lever.'),
    kind=AtomKind.EXPERIMENT_RECORD, tier=Tier.TIER_3_ALGORITHM, corpus=Corpus.MATH, algebra=None,
    metadata={
        'provenance_quality': 'HONEST_NEGATIVE',
        'relevance_tier': 'HIGH',
        'verdict': 'HONEST_NEGATIVE_pre_reg_miss_proven_bound_PCA_init_linear_projection_VQ_lever_anti_helpful',
        'run_mode': 'full',
        'n_seeds': 3,
        'seeds': [7, 17, 23],
        'V_C': 1024,
        'N_DIM': 16384,
        'K': 1,
        'f_sparse': 0.006,
        'proj_dim_grid': [768, 64, 32],
        'MAX_DOCS': 100000,
        'corpus': 'Pythia-160m residuals (residuals_per_token.npz, ~34.5MB) -- same as N2 lineage',
        'metrics_path': 'data/exp_n3_vq_alignment_simvq_v1/metrics.json',
        'metrics_source': 'substrate_native_LM_VQ_alignment_SimVQ_MVP_PCA_init_projection_sweep',
        'cell_commit': 'f5a0685a',
        'cell_author_verdict_disagreement': (
            'cell-author wrote MIDDLE_BAND via verdict() fallback at line 1151 ("small-effect '
            'ceiling_delta=-0.231"); cert-owner overrules to HONEST_NEGATIVE off pre-reg INTENT '
            '(MIDDLE_BAND requires delta>=+0.10 = IMPROVEMENT, not abs(delta)>=0.05 in either '
            'direction). The verdict-logic gap is a discipline-atomize candidate.'),
        'key_metrics': {
            'identity_PD768_ceiling_bpc_mean': 2.0491,
            'identity_PD768_ceiling_bpc_cv': 0.0193,
            'identity_PD768_ceiling_bpc_per_seed': [2.0692, 1.9940, 2.0843],
            'identity_PD768_substrate_bpc_mean': 4.9743,
            'identity_PD768_substrate_bpc_cv': 0.0064,
            'identity_PD768_concept_top1_mean': 0.5423,
            'identity_PD768_ceiling_top1_mean': 0.7305,
            'identity_PD768_codebook_util_mean': 0.9362,
            'identity_PD768_alpha_mean': 0.5034,
            'simvq_PD64_ceiling_bpc_mean': 2.2805,
            'simvq_PD64_ceiling_bpc_cv': 0.0147,
            'simvq_PD64_ceiling_bpc_per_seed': [2.327, 2.249, 2.265],
            'simvq_PD64_substrate_bpc_mean': 5.0298,
            'simvq_PD64_substrate_bpc_cv': 0.0023,
            'simvq_PD64_concept_top1_mean': 0.5050,
            'simvq_PD64_codebook_util_mean': 0.9564,
            'simvq_PD64_ceiling_delta_vs_identity_bits': -0.2314,  # NEGATIVE -- SimVQ HURTS
            'simvq_PD64_substrate_delta_vs_identity_bits': -0.0555,
            'simvq_PD32_ceiling_bpc_mean': 2.4746,
            'simvq_PD32_ceiling_bpc_cv': 0.0085,
            'simvq_PD32_ceiling_bpc_per_seed': [2.502, 2.470, 2.452],
            'simvq_PD32_substrate_bpc_mean': 5.0691,
            'simvq_PD32_substrate_bpc_cv': 0.0059,
            'simvq_PD32_concept_top1_mean': 0.4776,
            'simvq_PD32_codebook_util_mean': 0.9596,
            'simvq_PD32_ceiling_delta_vs_identity_bits': -0.4255,  # MORE NEGATIVE at lower d
            'simvq_PD32_substrate_delta_vs_identity_bits': -0.0948,
            'anchor_diff_vs_N2_ceiling_bits': 0.0000,  # identity arm reproduces N2 EXACTLY (same seeds)
            'anchor_diff_vs_N2_substrate_bits': 0.0151,
            'bigram_bpc_mean': 3.8442,  # global; unchanged by VQ alignment
            'unigram_bpc_mean': 6.3261,
            'pre_reg_hard_pass_ceiling_threshold': 1.75,
            'pre_reg_hard_pass_substrate_threshold': 4.75,
            'pre_reg_middle_band_ceiling_delta_threshold_bits': 0.10,
            'pre_reg_hard_fail_ceiling_delta_threshold_bits': 0.05,
            'zero_llm_calls_at_inference': True,
            'total_llm_forward_calls_observed': 0,
            'wall_s_total': 1262.66,
        },
        'honest_scope': (
            'n3 demonstrates that SimVQ-MVP (PCA-init linear projection W frozen at PCA basis '
            'before MiniBatchKMeans VQ) is anti-helpful as a Path B decode-side lever at V_C=1024, '
            'N_DIM=16384, K=1, MAX_DOCS=100k on Pythia-160m residuals. Does NOT validate: '
            '(a) the full Path B class (decode-side improvement is dead) -- MKN smoothing (drill #2) '
            'and full-learned-SimVQ (deferred follow-on) remain untested; (b) the broader Path B vs '
            'Path A direction -- this is ONE lever (PCA-init projection) within Path B sub-area (a) '
            'and only at the MVP form; (c) the substrate-native LM concept (the substrate-only-decode '
            'gate passed cleanly; the bottleneck is decode-floor, not the decode mechanism). Does NOT '
            'invalidate the decode-bottleneck hypothesis from N2 (the 2.9-bit substrate-vs-ceiling gap '
            'is intact at every PD; the LEVER is wrong, not the diagnosis). Single PROJ_DIM sweep; '
            'pythia-160m residual corpus only; N=16384 only.'),
        'finding': (
            'First Path B HONEST_NEGATIVE post-STANDSTILL. The unsupervised PCA-init linear-projection-'
            'before-VQ lever does NOT lower ceiling_bpc; it raises it monotonically with lower '
            'projection dimension. The high-variance PCA directions of Pythia-160m residuals are not '
            'aligned with token-conditional structure (consistent with residual-stream isotropy audits '
            'in the substrate -- the dominant variance axes are sentence/topic/register, not '
            'next-token contrast). The decode-side bottleneck hypothesis (substrate_bpc minus '
            'ceiling_bpc ~2.9 bits at V_C=1024) is intact; this rules out PCA-init projection as a '
            'fix while keeping the broader decode-side direction alive. PROVEN BOUND: PCA-init '
            'projection before VQ does not reduce ceiling at this scale; revival angles are FULL '
            'SimVQ (learned W jointly with VQ) or MKN-only smoothing.'),
        'baseline_provenance': (
            'Anchor: PROJ_DIM=768 (identity, no projection) reproduces N2 V_C=1024/N=16384/K=1 '
            'ceiling_bpc=2.0491 EXACTLY across all 3 seeds (same residual corpus, same seeds, same '
            'sparse codebook construction, identical algorithm modulo the no-op projection); anchor '
            'diff = 0.0000 bits, well within pre-reg gate 0.05. substrate_bpc anchor diff = 0.0151 '
            'bits (within decoder stochastic noise). N2 itself is from exp_n2_capacity_scaling_v1 '
            '(LANDED_VET MIDDLE_BAND 2026-06-22).'),
        'composes_with': [
            'T3/EXP_n2_capacity_scaling_v1',  # the baseline N2 lineage this anchors against
            'T3/EXP_n1_concept_lm_substrate_native_token_decode_v3_1',  # N1 substrate-only-decode parent
        ],
        'depends_on_text': (
            'PCA via SVD on L2-normalized train residual covariance (numpy linalg.eigh on symmetric); '
            'MiniBatchKMeans VQ assignment (sklearn.cluster); count-proportional decode with '
            'Jelinek-Mercer interpolation (substrate-native); sparse Willshaw codebook (f=0.006); '
            'pre-computed Pythia-160m residual stream at ingest (no LLM at inference). Recorded in '
            'metadata (phantom-safe; residual corpus is a data reference).'),
        'cert_vet_status': 'LANDED_VET_skunkworks_2026-06-22_HONEST_NEGATIVE_first_Path_B_proven_bound',
        'verified_off_data': (
            'cert-owner re-derived all cited numbers from data/exp_n3_vq_alignment_simvq_v1/'
            'metrics.json per_seed (seeds 7/17/23) via .venv numpy: identity ceiling=2.0491 (per-seed '
            '2.0692/1.9940/2.0843; matches N2 anchor exactly), PD=64 ceiling=2.2805 (per-seed '
            '2.327/2.249/2.265; delta=-0.231 vs identity), PD=32 ceiling=2.4746 (per-seed '
            '2.502/2.470/2.452; delta=-0.426 vs identity). All cv<=0.02. zero_llm_calls confirmed '
            'on every per_unit + module-counter + grep source audit. Train/test split discipline: '
            'PCA fit on train_res_n only (line 740), MBK fit on train_proj only (line 760), '
            'km.predict applied to test_proj. Cell-author MIDDLE_BAND label overruled to '
            'HONEST_NEGATIVE off pre-reg INTENT (MIDDLE_BAND requires +0.10 IMPROVEMENT, not '
            'abs-delta in either direction).'),
        'prereg': ('notes/exp_dev_n3_simvq_pre_reg_2026-06-22.md (HARD_PASS ceiling<=1.75 + '
                   'substrate<=4.75 + cv<=0.05; MIDDLE_BAND ceiling_delta in [0.10, 0.30] IMPROVEMENT; '
                   'HARD_FAIL ceiling change <0.05 OR anchor mismatch OR LLM-violation). '
                   'Research routing: notes/research_decode_side_lm_improvements_substrate_native_'
                   '2026-06-22.md (calibrated P(>=0.30 BPC gain)=0.40-0.45).'),
        'atomized_by': 'skunkworks',
        'atomized_date': '2026-06-22',
        'era': 'agent_teams_post_STANDSTILL_phase_C_live_write_first_HONEST_NEGATIVE',
        'milestone': (
            'First Path B HONEST_NEGATIVE post-STANDSTILL. Establishes proven bound: PCA-init linear '
            'projection before MBK VQ does NOT lower ceiling_bpc at V_C=1024/N=16384. Routes Path B '
            'sub-area (a) follow-ons toward FULL SimVQ (learned W) and pivots Path B effort toward '
            'sub-area (b) MKN smoothing (untested, P=0.55, composable). Does NOT close Path B '
            'wholesale; does NOT preempt Path A (V_C=4096 x N=32768+ remains evidence-warranted per '
            'pre-reg Prediction 2).'),
        'open_followups': [
            'Path B (b): MKN drop-in cell (Research drill #2 lever, P>=0.10 BPC gain ~0.55; pure '
            'smoothing replacement, no architecture change, composable with identity VQ + with '
            'eventual Path A)',
            'Path B (a) full-SimVQ revival: W learned jointly with VQ via straight-through estimator '
            'or contrastive token-prediction loss (the MVP empirical negative deflates calibrated P; '
            'still worth a single-cell decisive test)',
            'Path A: V_C=4096 x N=32768+ (evidence-warranted per pre-reg Prediction 2; the monotonic '
            'PD-vs-ceiling trend in n3 BOLSTERS the case -- coarser concepts hurt ceiling, finer '
            'should help)',
            'Discipline atomize: verdict() fallback gap (large-abs-delta-wrong-direction misclassified '
            'as MIDDLE_BAND; should be HONEST_NEGATIVE when pre-reg INTENT was directional)',
        ],
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
    existed = ps.get_atom(N3.qualified_id) is not None
    if existed:
        print(f"  SKIP exists: {N3.id}")
    else:
        ps.add_atom(N3, source='skunkworks_n3_simvq_honest_negative_proven_bound_2026_06_22',
                    note='n3 first Path B HONEST_NEGATIVE: PCA-init linear projection before VQ raises ceiling_bpc; pre-reg miss proven bound (CERT 584 unchanged)')
        print(f"  ADD: {N3.id}")
    ps2 = PartitionedStore(Path('data/substrate_index'))
    post_cert, post_ax, post_mod = cert(ps2), axiom(ps2), modlive()
    post_atoms = len(list(ps2.all_atoms()))
    landed = ps2.get_atom(N3.qualified_id) is not None
    bad_alg = landed and ps2.get_atom(N3.qualified_id).algebra is not None
    print(f"POST: atoms={post_atoms} (+{post_atoms-pre_atoms}) CERT={post_cert} (expect 584 UNCHANGED) "
          f"axiom={post_ax} (expect 206) cap_pres={post_mod} landed={landed} algebra!=None={bad_alg}")
    gate = (post_cert == 584 and post_ax == 206 and post_mod and landed and not bad_alg)
    print("STORE GATE:", "OK -- CERT 584 unchanged (honest_negative; delta=0)" if gate else "FAIL")
    if not gate:
        return 2

    # ========================================================================
    # PHASE C LIVE-WRITE: cert_ledger row in the SAME A5 window
    # ========================================================================
    print()
    print("=== PHASE C live-write: cert_ledger row (honest_negative; pre_reg_miss_proven_bound) ===")
    ledger_row = build_honest_negative_row(
        atom_id='math::T3/EXP_n3_vq_alignment_simvq_v1',
        cell_commit='f5a0685a',
        verdict='HONEST_NEGATIVE',  # cert-owner ruling; overrides cell-author MIDDLE_BAND label
        notes_path='notes/skunkworks_to_research_cc_all_LANDED_VET_n3_simvq_HONEST_NEGATIVE_2026-06-22.md',
        metrics_path='data/exp_n3_vq_alignment_simvq_v1/metrics.json',
        cert_class='pre_reg_miss_proven_bound',
        note='n3_simvq_first_Path_B_honest_negative_PCA_init_projection_anti_helpful_proven_bound',
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
