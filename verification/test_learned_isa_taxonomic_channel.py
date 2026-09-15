"""Scaffold-free witness for the_learned_is_a_taxonomic_identity_channel_is_the_dominant_unbuilt_meaning_lever.

Verifies the LOCATED NEGATIVE / REFUTATION on disk (landed metrics) + a few LIVE micro-checks of the
mechanism (so the negative is faithful, not a plumbing artifact). NO cell re-run in place (reads landed
metrics.json); the live checks build tiny in-memory objects only. 2 threads. ASCII-only.

Run: .venv/Scripts/python.exe verification/test_learned_isa_taxonomic_channel.py
"""
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
import json
import sys

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

CHECKS = []


def ck(name, cond, detail=""):
    CHECKS.append((name, bool(cond), detail))
    print(("PASS" if cond else "FAIL") + " | " + name + (("  -- " + detail) if detail else ""), flush=True)


def _load(sub):
    p = os.path.join(_REPO, "data", sub, "metrics.json")
    with open(p, encoding="ascii") as f:
        return json.load(f)["result"]


# ---------------------------------------------------------------- 1. the DIAGNOSTIC: premise vs strong baseline
D = _load("exp_meaning_fusion_isa_headroom_diag_v1")
sl = D["populations"]["SimLex_high_only"]; sla = sl["AUF_MRR"]
po = D["populations"]["SimLex+SimVerb_pooled"]; poa = po["AUF_MRR"]

ck("diag: grounded floor reproduces the brief's 0.188 (n=94)", abs(sla["GD"] - 0.188) < 0.02,
   "GD=%.3f" % sla["GD"])
ck("diag: grown-SEQ ALONE already >> grounded floor (SEQ banks the identity signal, Harris)",
   sla["SEQ"] > sla["GD"] + 0.15, "SEQ=%.3f vs GD=%.3f" % (sla["SEQ"], sla["GD"]))
ck("diag: STRONG baseline grounded+SEQ beats grounded floor CI-separated (the parent's landed lever)",
   sl["BASE_vs_GD"]["ci_sep"] and sla["BASE"] > 0.45, "BASE=%.3f BASE_vs_GD %s" % (sla["BASE"], sl["BASE_vs_GD"]["ci"]))
ck("diag: PREMISE REFUTED n=94 -- even CIRCULAR WordNet CM does NOT beat grounded+SEQ CI-separated",
   (not sl["CM_vs_BASE"]["ci_sep"]) and sl["CM_vs_BASE"]["diff@0.5"] < 0.30,
   "CM_vs_BASE %+.3f CI %s (brief claimed +0.488 vs the pre-SEQ floor)" % (sl["CM_vs_BASE"]["diff@0.5"], sl["CM_vs_BASE"]["ci"]))
ck("diag: PREMISE REFUTED pooled -- CM headroom over grounded+SEQ is tiny + not CI-sep",
   (not po["CM_vs_BASE"]["ci_sep"]) and po["CM_vs_BASE"]["diff@0.5"] < 0.12,
   "CM_vs_BASE %+.3f CI %s" % (po["CM_vs_BASE"]["diff@0.5"], po["CM_vs_BASE"]["ci"]))
ck("diag: oracle{grounded+SEQ} EXCEEDS the WordNet taxonomic ceiling (no missing REACHABLE coverage from CM alone)",
   sla["oracle_BASE"] > sla["CM_ceiling_CIRCULAR"], "oracle_BASE=%.3f > CM=%.3f" % (sla["oracle_BASE"], sla["CM_ceiling_CIRCULAR"]))
ck("diag: the residual is a READ-OUT/confidence gap (oracle_BASE >> realistic BASE), larger than the CM advantage",
   (sla["oracle_BASE"] - sla["BASE"]) > sl["CM_vs_BASE"]["diff@0.5"],
   "confidence gap 0.505->%.3f=+%.3f vs CM advantage +%.3f" % (sla["oracle_BASE"], sla["oracle_BASE"] - sla["BASE"], sl["CM_vs_BASE"]["diff@0.5"]))
ck("diag: taxonomic IS complementary in principle (perfect router oracle_BASE_union_CM > oracle_BASE) -- but unrealizable",
   sla.get("oracle_BASE_union_CM", 0) > sla["oracle_BASE"] + 0.05,
   "oracle_union=%s > oracle_BASE=%.3f" % (sla.get("oracle_BASE_union_CM"), sla["oracle_BASE"]))

# ---------------------------------------------------------------- 2. SYMMETRIC shared-genus channel: located neg
K = _load("exp_meaning_fusion_isa_knowledge_v1")
ck("symmetric shared-genus (isa_knowledge) does NOT lift the live decision (<=0, not CI-sep)",
   (not K["OVERALL"]["genus_adds"]["ci_sep"]) and K["OVERALL"]["genus_adds"]["diff@0.5"] <= 0.005,
   "OVERALL genus_adds %+.4f CI %s" % (K["OVERALL"]["genus_adds"]["diff@0.5"], K["OVERALL"]["genus_adds"]["ci"]))
ck("symmetric shared-genus: knowledge-shuffled twin is NOT beaten (carries no identity signal)",
   K["OVERALL"]["twin_loses"] is False, "twin_loses=%s" % K["OVERALL"]["twin_loses"])

# ---------------------------------------------------------------- 3. DIRECTED is-a + capture: located neg
P = _load("exp_meaning_fusion_directed_isa_capture_v1")            # pooled, no backfill, sw_cap grow curve
pg = P["grow_curve"][-1]
ck("directed capture (pooled, read-edge coverage LIMITED): CAPTURE_vs_BASE ~ 0, not CI-sep",
   (not pg["OVERALL"]["CAPTURE_vs_BASE"]["ci_sep"]) and abs(pg["OVERALL"]["CAPTURE_vs_BASE"]["diff@0.5"]) < 0.01,
   "coverage=%.2f CAPTURE_vs_BASE %+.4f" % (pg["isa_query_coverage"], pg["OVERALL"]["CAPTURE_vs_BASE"]["diff@0.5"]))

B = _load("exp_meaning_fusion_directed_isa_capture_v1_simlex_bf")  # favorable pop + SEQ-backfill to 100% coverage
bg = B["grow_curve"][-1]
ck("directed capture STRONGEST (n=94 favorable pop + SEQ-backfill -> 100% is-a coverage): coverage really is ~1.0",
   bg["isa_query_coverage"] > 0.95, "isa_query_coverage=%.3f" % bg["isa_query_coverage"])
ck("directed capture STRONGEST: CAPTURE_vs_BASE ~ 0 even at 100% coverage (the learned is-a supplies nothing net)",
   (not bg["OVERALL"]["CAPTURE_vs_BASE"]["ci_sep"]) and abs(bg["OVERALL"]["CAPTURE_vs_BASE"]["diff@0.5"]) < 0.01,
   "CAPTURE_vs_BASE %+.4f CI %s" % (bg["OVERALL"]["CAPTURE_vs_BASE"]["diff@0.5"], bg["OVERALL"]["CAPTURE_vs_BASE"]["ci"]))
ck("directed capture STRONGEST: additive is-a FUSION HURTS the strong baseline (relatedness, not identity)",
   bg["OVERALL"]["FUSE_vs_BASE"]["diff@0.5"] < 0.0, "FUSE_vs_BASE %+.4f" % bg["OVERALL"]["FUSE_vs_BASE"]["diff@0.5"])
ck("directed capture STRONGEST: knowledge-shuffled twin NOT beaten (no real is-a identity signal captured)",
   bg["OVERALL"]["twin_loses"] is False, "twin_loses=%s" % bg["OVERALL"]["twin_loses"])

# ---------------------------------------------------------------- 3b. residual decomposition: read-out is NOT the sole lever
R = _load("exp_meaning_fusion_residual_decomposition_v1")
rs = R["populations"]["SimLex_high_only"]
gap_triage = rs["AUF_triage_oracle (perfect abstention, ranking FIXED)"] - rs["AUF_realistic (margin triage)"]
gap_sharpen = rs["AUF_ranksharpen_top3 (promote in-reach partner + perfect triage)"] - rs["AUF_triage_oracle (perfect abstention, ranking FIXED)"]
ck("residual: a substantial chunk is TRIAGE-recoverable-in-principle (read-out component exists)",
   gap_triage > 0.15, "triage-oracle gap +%.3f (realistic %.3f -> %.3f)" % (gap_triage, rs["AUF_realistic (margin triage)"], rs["AUF_triage_oracle (perfect abstention, ranking FIXED)"]))
ck("residual: a comparable chunk needs the RANKING to change (rank2-3 in-reach; representation lever, NOT triage)",
   gap_sharpen > 0.08 and rs["rank_histogram"]["rank2_3"] > 0.15,
   "ranksharpen gap +%.3f; rank2-3 frac %.3f" % (gap_sharpen, rs["rank_histogram"]["rank2_3"]))
ck("residual: read-out is NOT PROVEN realizable -- margin only modestly discriminates correctness (parent Path-2 neg)",
   rs["AUC_margin_discriminates_correct"] < 0.75 and R["populations"]["SimLex+SimVerb_pooled"]["spearman_margin_vs_correct"] < 0.30,
   "AUC(margin->correct) n94=%.2f; spearman pooled=%.2f; conf-wrong n94=%.2f"
   % (rs["AUC_margin_discriminates_correct"], R["populations"]["SimLex+SimVerb_pooled"]["spearman_margin_vs_correct"], rs["confidently_wrong_fraction (margin>=median correct)"]))
ck("residual: a deep chunk (true partner rank>10) is coverage/knowledge-bound, neither read-out nor local rerank",
   rs["rank_histogram"]["rank_gt10"] > 0.25, "rank>10 frac n94=%.2f pooled=%.2f" % (rs["rank_histogram"]["rank_gt10"], R["populations"]["SimLex+SimVerb_pooled"]["rank_histogram"]["rank_gt10"]))

# ---------------------------------------------------------------- 3c. wall-prototype convergence (owner: do it all, iterate)
RR = _load("exp_meaning_fusion_relation_rerank_v1")
rr94 = RR["populations"]["SimLex_high_only"]
ck("wall#2: the brain's OWN competition (LATINHIB divnorm + lateral inhibition) does NOT resolve it (not CI-sep)",
   (not rr94["LATINHIB_vs_BASE"]["ci_sep"]) and abs(rr94["LATINHIB_vs_BASE"]["diff@0.5"]) < 0.02,
   "LATINHIB_vs_BASE %+.4f; DIVNORM %+.4f; CSLS %+.4f" % (rr94["LATINHIB_vs_BASE"]["diff@0.5"], rr94["DIVNORM_vs_BASE"]["diff@0.5"], rr94["CSLS_vs_BASE"]["diff@0.5"]))
ck("wall#2: competition null on the IN-REACH (rank 2-3) subset too -> signal must be ADDED, not routed",
   ("diff@0.5" in rr94.get("W2_inreach_LATINHIB", {})) and (not rr94["W2_inreach_LATINHIB"].get("ci_sep", False)),
   "in-reach LATINHIB %s" % rr94.get("W2_inreach_LATINHIB", {}).get("diff@0.5"))

NC = _load("exp_meaning_fusion_new_channels_v1")
nc94 = NC["populations"]["SimLex_high_only"]
ck("wall#2: symmetric-coordination (SYM) does NOT add over the strong grown base (hurts/null; redundant with SEQ)",
   nc94["SYM_vs_BASE"]["diff@0.5"] <= 0.005 and (not nc94["SYM_vs_BASE"]["ci_sep"]),
   "SYM_vs_BASE %+.4f (smoke over the WEAK base was +0.096 -- inverts over the strong base)" % nc94["SYM_vs_BASE"]["diff@0.5"])
ck("wall#2: mutual-inclusion (INCL) does NOT add (co-hyponyms share too many features)",
   nc94["INCL_vs_BASE"]["diff@0.5"] <= 0.005 and (not nc94["INCL_vs_BASE"]["ci_sep"]),
   "INCL_vs_BASE %+.4f" % nc94["INCL_vs_BASE"]["diff@0.5"])
ck("wall#2 CONVERGENCE: six first-order-co-occurrence mechanisms all null/neg over the strong base (theorem-explained)",
   all(x <= 0.007 for x in [rr94["LATINHIB_vs_BASE"]["diff@0.5"], rr94["DIVNORM_vs_BASE"]["diff@0.5"],
                            rr94["CSLS_vs_BASE"]["diff@0.5"], rr94["MP_vs_BASE"]["diff@0.5"],
                            nc94["SYM_vs_BASE"]["diff@0.5"], nc94["INCL_vs_BASE"]["diff@0.5"]]),
   "is-a/competition/divnorm/CSLS/MP/inclusion/SYM all <= +0.007 over BASE")

# ---------------------------------------------------------------- 3d. the PIVOT: referential-equivalence channel
EQ = _load("exp_meaning_fusion_equivalence_channel_v1")
eq94 = EQ["populations"]["SimLex_high_only"]
ck("pivot: diffuse referential-equivalence channel does NOT overcome the wall (hurts, twin not beaten)",
   eq94["EQUIV_vs_BASE"]["diff@0.5"] <= 0.005 and (eq94["AUF"]["+EQUIV"] <= eq94["AUF"]["TWIN"] + 1e-9),
   "+EQUIV %+.4f; twin not beaten" % eq94["EQUIV_vs_BASE"]["diff@0.5"])
ck("pivot: precision-GATED equivalence binding fires on ~0 eval queries (renaming targets entities, not common-word synonyms)",
   eq94["gate_fires_on_n_queries"] <= 1 and eq94["gate_boosts_the_GOLD_partner_on_n_queries"] == 0,
   "gate fires on %d queries; boosts gold partner on %d (of %d)" % (eq94["gate_fires_on_n_queries"], eq94["gate_boosts_the_GOLD_partner_on_n_queries"], eq94["n"]))

# ---------------------------------------------------------------- 3e. research-driven probes (contrast + confusion taxonomy)
CP = _load("exp_meaning_fusion_contrast_probe_v1")
a = CP["AUC_syn_over_cohyp"]
ck("probe: cosine DOES weakly separate syn vs co-hyp (AUC>0.6) -- the wall is overlap+ranking, not zero signal",
   a["cos"] > 0.6, "cosine AUC syn>cohyp = %.3f" % a["cos"])
ck("probe: the CONTRAST lever does NOT add over cosine on our corpus (coverage-starved: apposition ~0, contrast ~0)",
   CP["CONTRAST_CORRECTED_best_vs_cos"]["auc"] <= a["cos"] + 0.01 and CP["coverage_frac_pairs_with_signal"]["appos"]["syn"] < 0.05,
   "corrected AUC %.3f vs cos %.3f; appos coverage %.2f; contrast AUC %.3f" % (
       CP["CONTRAST_CORRECTED_best_vs_cos"]["auc"], a["cos"], CP["coverage_frac_pairs_with_signal"]["appos"]["syn"], a["contrast"]))
CT = _load("exp_meaning_fusion_confusion_taxonomy_v1")
ir = CT["populations"]["SimLex_high_only"]["IN_REACH_2_3_confusions"]
taxonomic = ir.get("CO_HYPONYM", 0) + ir.get("CO_TAXON_loose", 0) + ir.get("HYPER_HYPO", 0)
ck("probe: the in-reach residual confusions are dominated by TAXONOMIC relatives (co-hyponym/hyper-hypo) + antonyms",
   taxonomic >= 0.4, "in-reach taxonomic frac=%.2f; antonym=%.2f; alt-synonym(not-really-wrong)=%.2f"
   % (taxonomic, ir.get("ANTONYM", 0), ir.get("SYNONYM_alt", 0)))
ck("probe: ~half of wrong top-1 picks are higher-FREQUENCY hub words than the true partner",
   CT["populations"]["SimLex_high_only"]["hub_wrong_frac (wrong top1 more frequent than gold)"] > 0.3,
   "hub_wrong_frac=%.2f" % CT["populations"]["SimLex_high_only"]["hub_wrong_frac (wrong top1 more frequent than gold)"])

# ---------------------------------------------------------------- 3f. the in-context probe VALIDATES the pivot
IC = _load("exp_meaning_fusion_incontext_probe_v1")
type_auc = IC["by_alpha"]["alpha=1.0"]["AUC_same_gt_diff"]
ctx_auc = IC["by_alpha"]["alpha=0.0"]["AUC_same_gt_diff"]
ck("in-context: TYPE-level representation is ~chance on WiC by construction (same word -> identical vector)",
   abs(type_auc - 0.5) < 0.03, "type-level AUC = %.3f" % type_auc)
ck("in-context: CONTEXT-conditioning LIFTS discrimination over type-level (the pivot, validated)",
   ctx_auc > type_auc + 0.05, "context AUC %.3f vs type-level %.3f (WiC n_used=%d, tgt_cov=%.2f)"
   % (ctx_auc, type_auc, IC["n_used"], IC["target_coverage"]))
ck("in-context: the lift is MONOTONE in context weight (alpha 1.0->0.0), not an artifact",
   (IC["by_alpha"]["alpha=1.0"]["AUC_same_gt_diff"] <= IC["by_alpha"]["alpha=0.5"]["AUC_same_gt_diff"]
    <= IC["by_alpha"]["alpha=0.0"]["AUC_same_gt_diff"]),
   "AUC by alpha 1.0/0.5/0.0 = %.3f/%.3f/%.3f" % (IC["by_alpha"]["alpha=1.0"]["AUC_same_gt_diff"],
    IC["by_alpha"]["alpha=0.5"]["AUC_same_gt_diff"], IC["by_alpha"]["alpha=0.0"]["AUC_same_gt_diff"]))

# ---------------------------------------------------------------- 4. LIVE micro-checks of the mechanism (faithful build)
from experiments.exp_meaning_fusion_isa_knowledge_v1 import _hearst_edges
from experiments.exp_meaning_fusion_directed_isa_capture_v1 import build_isa_dense, genus_overlap_matrix, harvest_isa_edges
from experiments.exp_learned_structured_meaning_v1 import dep_ppmi_matrix

edges = {(h, g) for (h, g, w) in _hearst_edges("A robin is a kind of bird. Birds such as robins migrate. A hound is a dog.")}
ck("live: parser-free/WordNet-free Hearst extractor reads directed is-a edges",
   ("robin", "bird") in edges and ("hound", "dog") in edges, "%r" % sorted(edges))

words = ["robin", "bird", "hound", "dog", "sofa", "couch", "furniture"]
hypo_of = {"robin": {("HYP", "bird"): 3.0}, "hound": {("HYP", "dog"): 2.0},
           "sofa": {("HYP", "furniture"): 2.0}, "couch": {("HYP", "furniture"): 2.0}}
has_hypo = {"bird": {("HYPO", "robin"): 3.0}, "dog": {("HYPO", "hound"): 2.0},
            "furniture": {("HYPO", "sofa"): 2.0, ("HYPO", "couch"): 2.0}}
ISA, mask, ne = build_isa_dense(words, hypo_of, has_hypo, rank=4)
ck("live: Roller SVD densification returns unit-norm rows for edge-bearing words",
   ISA.shape[0] == len(words) and abs(np.linalg.norm(ISA[words.index("robin")]) - 1.0) < 1e-6,
   "ISA=%r n_edge=%d" % (ISA.shape, ne))
raw = {"sofa": {"furniture": 2.0}, "couch": {"furniture": 2.0}, "robin": {"bird": 3.0}}
GEN, gmask = genus_overlap_matrix(words, raw)
gs = np.asarray((GEN[[words.index("couch")]] @ GEN[words.index("sofa")].T).todense()).ravel()[0]
ck("live: genus-overlap is HIGH for co-hyponyms sharing a genus (the symmetric same-kind factor)",
   gs > 0.9, "genus_overlap(sofa,couch)=%.3f" % gs)

# ---------------------------------------------------------------- summary
npass = sum(1 for _n, ok, _d in CHECKS if ok)
print("\nWITNESS %s: %d checks / %d pass" % ("PASS" if npass == len(CHECKS) else "FAIL", npass, len(CHECKS)), flush=True)
if __name__ == "__main__":
    sys.exit(0 if npass == len(CHECKS) else 1)


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_file_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(__file__)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
