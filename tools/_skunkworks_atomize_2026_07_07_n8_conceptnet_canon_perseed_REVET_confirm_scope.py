"""
A5-gated atomize: LANDED-VET (AUDIT-ONLY, XHIGH) RE-VET of the N8 ConceptNet ingest CANONICAL run.

CELL: experiments/exp_n8_conceptnet_ingest_eval_v1.py
ANCHOR: n8_conceptnet_ingest_eval_v1 (canonical run n8_conceptnet_ingest_eval_canon_v1, commit 489032840, per-seed-tightened)
METRICS: data/exp_n8_conceptnet_ingest_eval_canon_v1/metrics.json (run_mode=full, seeds [7,17,23], elapsed 598.8s)
PREREG: notes/n8_conceptnet_ingest_pre_reg_2026-06-22.md
PARENT (already CG, cert585): math::T3/EXP_n8_conceptnet_ingest_eval_v1 (commit 8bbc11c4, atomized 2026-06-22)

CRITICAL DISPOSITION -- NO DOUBLE-COUNT:
  The canonical per-seed-tightened run reproduces the ORIGINAL n8 numbers essentially EXACTLY off-disk
  (2hop 0.415/0.425/0.4375, refuse OOD 1.0/0.9967/1.0 accept 0.9967/1.0/0.9933, setrecall 1.000 all M).
  n8 is ALREADY certified CG as cert585. This re-VET CONFIRMS cert585 under per-seed (worst-seed) gating
  and does NOT add a new cert. cert_increment_delta = 0 (avoids the July-1 rediscovery double-count pattern).

OFF-DISK INDEPENDENT RECOMPUTE (this session, python off canon metrics.json):
  setrecall@M100000 all=1.000 all 3 seeds; scale-curve pinned 1.0 except seed7 M50000=0.9997.
  CHANCE FLOOR: meanK = n_triples/n_keys = 100000/42154 = 2.372; n_ent = 80181;
    chance recall = meanK/n_ent = 2.96e-5 -> observed 1.000 is 33,799x above chance.
  refuse per-seed: ood [1.0,0.9967,1.0] min 0.9967; acc [0.9967,1.0,0.9933] min 0.9933; both >> 0.80 floor.
    inkb_conf/ood_conf ratio ~3.34-3.40 (held-split calibration; genuine separation).
  composition per-seed: 2hop [0.415,0.425,0.4375] mean 0.4258; 1hop [0,0,0]; enc [0.010,0.015,0.010]
    mean 0.01167; ratio mean 36.5x; per-seed ratios 41.5x/28.3x/43.75x all >= 2.0x. leak_skipped 1/6/10.

THE FOUR LOAD-BEARING AUDIT ANSWERS:

(1) SATURATION CHECK on setrecall=1.000 -> GENUINE, NOT vacuous, but SCALE-CURVE NON-DISCRIMINATING.
    set_recall_at_k (cell line 150-164) computes scores over ALL n_ent entities (80,181 at M100k) and
    takes top-K where K = true set size, then recall = |topk & objs|/K. So it competes against ~80k
    distractors; chance = K/n_ent = 2.96e-5. Observed 1.000 = 33,799x above chance -> the metric is
    GENUINELY DISCRIMINATING, NOT a by-construction ceiling (top-K is NOT restricted to the stored set).
    PROOF of non-triviality: seed7 M50000 = 0.9997 (one object missed) -- if it were trivially returning
    the stored set it would be EXACTLY 1.0 always; the lone sub-1.0 value proves the metric can and does
    deviate. HOWEVER: it is effectively SATURATED across the tested M-range (5k->100k): N=8192 Hebbian
    capacity is NOT exhausted at 100k triples, so the scale-CURVE does not locate a degradation cliff.
    Honest read: setrecall is a real CAPACITY PASS with UNTESTED HEADROOM, not a demonstrated
    scale-robustness with a measured degradation boundary. The pre-reg's own saturation-suspicion trigger
    fires -- resolution (per the U1 LANDED-VET lesson): multi-value setrecall is NOT by-construction, but
    here it simply was not stressed to a cliff. The setrecall gate is a NON-DISCRIMINATING (in-range) pass;
    the real signal rests on the refuse-gate + composition.

(2) REFUSE-GATE per-seed -> PASS on ALL 3 seeds independently (NOT mean-masked).
    ood min 0.9967 >= 0.80; acc min 0.9933 >= 0.80. Held-split calibration (cal on first half, eval on
    second half; cell line 177-188) -- no train/test leak. in-KB confidence ~3.4x higher than OOD; genuine
    separation. This is the GENUINELY-DISCRIMINATING dimension and is consistent with + reinforces the
    June-19 cross-arc finding that the substrate's certified KG VALUE is the fact-fabrication / refuse-gate.

(3) COMPOSITION FAIRNESS -> the RELATIVE claim is honest but must be SCOPED; two framing corrections:
    (3a) 1hop = 0.000 EXACTLY is BY CONSTRUCTION, NOT a firing can-fail control. The leak guard
         (cell line 229 `if (s,o) in direct: leak+=1; continue`) removes EVERY chain where o is 1-hop
         reachable from s under ANY relation. So the 1-hop baseline STRUCTURALLY cannot fire -- it is
         pinned at 0, not "firing correctly" as the original cert585 atom stated. It is not unfairly
         crippled (it accurately reflects "1-hop cannot reach a 2-hop-only answer"), but the
         "> 1hop + 0.02" gate is a WEAK/near-vacuous discriminator (only fails if 2hop itself collapses).
         The ONLY load-bearing composition discriminator is the frozen-encoder ratio.
    (3b) The frozen-encoder baseline (0.012) is a WEAK bar: MiniLM-L6 (~22M, not BGE), Hits@1 argmax
         nearest-neighbor to the SUBJECT name (cell line 243-250), no relation-conditioning. It fires for
         a real reason (0.012 nonzero: fires when a 2-hop target happens to be NN-by-name to the source),
         so it is a genuine uncrippled NON-COMPOSITIONAL baseline -- but it is NOT a strong completion
         encoder. substrate_2hop=0.426 is HONEST and if anything CONSERVATIVE (multi-valued intermediate
         nodes penalize the 2-hop argmax chain). The load-bearing claim is the RELATIVE one: composition
         beats the non-compositional similarity shortcut. The absolute 36.5x must NOT be read as
         "substrate composition beats a semantic encoder at KG completion."

(4) TIER + STRATEGIC VERDICT -> cert585 HOLDS as a CG INGEST+GOVERNANCE cert under per-seed tightening;
    the COMPOSITION dimension is scoped to MEASURED_MECHANISM. Honest scoped Stage-1 ingest claim:
    "The substrate INGESTS 100k real ConceptNet facts (N=8192 multi-value Hebbian) with setrecall ~1.000
    against ~80k distractors (genuine, 33,799x above chance; capacity headroom untested), GOVERNS them via
    a held-split refuse-gate (OOD-refuse/accept ~0.99 per-seed, the genuinely-discriminating dimension),
    and COMPOSES 2-hop chains at 0.426 -- beating a NON-COMPOSITIONAL subject-NN-by-name similarity
    shortcut by 36.5x. It does NOT establish superiority over a strong completion encoder: the June-19
    cross-arc result PROVED substrate multi-hop completion UNDERPERFORMS frozen-BGE single-hop
    (ConceptNet Hits@10 0.45 < BGE 0.50), and that result is NOT overturned here."

CROSS-ARC OVERLAP CHECK (substrate_query, mandatory):
  Top hits at cosine>0.30: 'B1 Auditable multi-hop reasoning / Hebbian knowledge graph' (0.337, note).
  At cosine 0.291: reference_inference_transfer_eval_design_closure_perfect_bge_is_the_bar_2026-06-19 --
  the LOAD-BEARING reconciliation: "substrate cf-RPE HDC multi-hop completion UNDERPERFORMS frozen-bge
  single-hop cosine (ConceptNet Hits@10 0.45 < bge 0.50 < exact-closure 1.0); substrate KG VALUE = the
  FACT-FABRICATION-BOUND/refuse-gate (AUROC 0.81 HARD_PASS), NOT positive completion." This RE-VET is a
  targeted confirmation + scope-correction of the EXISTING cert585 atom, not a rediscovery. The parent
  cert585 atom's over-claims (setrecall 'not saturation', 1hop 'fires correctly', 'beats semantic bar =
  genuine compositional inference') are SCOPED DOWN by this amendment; parent NOT superseded (its
  ingest+governance CG core stands, numbers reproduce).
"""
from __future__ import annotations
import json, os, time
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")
MATH_ATOMS = ROOT / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = ROOT / "data/substrate_index/meta/cert_ledger.jsonl"

ATOMIZED_BY = "skunkworks_atomize_2026_07_07_n8_conceptnet_canon_perseed_REVET_confirm_scope"
CELL_COMMIT = "489032840"
TS_ISO = "2026-07-07T22:45:49Z"
TS = 1783464349.0

PARENT_ID = "math::T3/EXP_n8_conceptnet_ingest_eval_v1"
JUNE19_REF = "reference_inference_transfer_eval_design_closure_perfect_bge_is_the_bar_2026-06-19"

atom_math = {
    "id": (
        "math::REVET_CONFIRM_n8_conceptnet_ingest_canon_perseed_tightened_CONFIRMS_cert585_ingest_plus_"
        "governance_CG_AND_SCOPES_DOWN_composition_to_MM_3seed_7_17_23_FULL_N8192_M100k_commit489032840_"
        "setrecall_1p000_GENUINE_vs_80181_distractors_chance_2p96e_minus5_33799x_above_but_scale_curve_"
        "NONDISCRIMINATING_capacity_headroom_untested_only_sub1_is_seed7_M50000_0p9997_proves_not_"
        "byconstruction_refuse_per_seed_ood_min_0p9967_acc_min_0p9933_heldsplit_genuine_3p4x_conf_sep_"
        "GENUINELY_DISCRIMINATING_dim_composition_2hop_0p4258_beats_ONLY_nonCompositional_subjectNNbyname_"
        "shortcut_enc_0p01167_ratio_36p5x_but_1hop_0p000_is_BYCONSTRUCTION_leakguard_NOT_firing_control_and_"
        "encoder_is_WEAK_MiniLML6_Hits1_NNtoSubject_NOT_strong_completion_JUNE19_arc_PROVED_substrate_"
        "multihop_UNDERPERFORMS_bge_ConceptNet_Hits10_0p45_lt_bge_0p50_NOT_overturned_cert_delta_ZERO_no_"
        "double_count_amends_cert585_over_claims_parent_NOT_superseded_2026-07-07"
    ),
    "name": (
        "MATH RE-VET: N8 ConceptNet ingest canonical (per-seed tightened, commit 489032840) CONFIRMS "
        "cert585 ingest+governance as CG and SCOPES DOWN the composition claim to MEASURED_MECHANISM "
        "(beats a non-compositional NN-by-name shortcut, NOT a strong completion encoder). cert_delta 0."
    ),
    "corpus": "math",
    "tier": "CHAIN_GRADE",
    "kind": "experiment_landed_vet",
    "cert_status": (
        "revet_confirms_cert585_ingest_governance_CG_under_per_seed_gating_scopes_composition_to_MM_"
        "no_new_cert_no_double_count"
    ),
    "cert_class": (
        "conceptnet_kb_ingest_at_scale_plus_held_split_refuse_governance_per_seed_confirmed_composition_"
        "beats_noncompositional_similarity_shortcut_only_scoped_down"
    ),
    "description": (
        "LANDED-VET (AUDIT-ONLY, XHIGH) of the N8 ConceptNet ingest CANONICAL run "
        "(exp_n8_conceptnet_ingest_eval_v1, canonical anchor n8_conceptnet_ingest_eval_canon_v1, commit "
        "489032840 per-seed-tightened; 3-seed [7,17,23] FULL, N=8192, M scale [5k,10k,25k,50k,100k], "
        "elapsed 598.8s). This is a RE-VET of the already-CG cell (parent cert585, commit 8bbc11c4, "
        "atomized 2026-06-22). The canonical per-seed-tightened run REPRODUCES the original numbers "
        "essentially exactly off-disk, so cert_increment_delta=0 (NO new cert; avoids double-count). "
        "OFF-DISK INDEPENDENT RECOMPUTE: setrecall@M100000 all=1.000 all 3 seeds (scale-curve pinned 1.0 "
        "except seed7 M50000=0.9997); refuse per-seed ood [1.0,0.9967,1.0] min 0.9967, acc "
        "[0.9967,1.0,0.9933] min 0.9933, both >> 0.80; composition per-seed 2hop [0.415,0.425,0.4375] mean "
        "0.4258, 1hop [0,0,0], enc [0.010,0.015,0.010] mean 0.01167, ratio 36.5x (per-seed 41.5x/28.3x/"
        "43.75x all >=2.0x), leak_skipped 1/6/10. FOUR LOAD-BEARING AUDIT FINDINGS: "
        "(1) SATURATION: setrecall=1.000 is GENUINE not vacuous -- top-K is scored over ALL 80,181 "
        "entities (NOT restricted to the stored set; cell line 150-164), chance floor = meanK/n_ent = "
        "2.372/80181 = 2.96e-5, so 1.000 is 33,799x above chance; the lone seed7 M50000=0.9997 PROVES the "
        "metric can deviate (not by-construction). BUT it is SATURATED across the tested M-range (N=8192 "
        "capacity not exhausted at 100k) -> the scale-CURVE is NON-DISCRIMINATING; a real CAPACITY PASS "
        "with UNTESTED HEADROOM, not a measured scale-degradation boundary. "
        "(2) REFUSE-GATE: PASS per-seed independently (ood min 0.9967, acc min 0.9933); held-split "
        "calibration, no leak; ~3.4x in-KB-vs-OOD confidence separation. This is the GENUINELY-"
        "DISCRIMINATING dimension and reinforces the June-19 finding that the substrate's certified KG "
        "value is the refuse-gate. "
        "(3) COMPOSITION FAIRNESS -- two framing corrections vs cert585: (3a) 1hop=0.000 is EXACTLY zero "
        "BY CONSTRUCTION (leak guard at cell line 229 removes every chain where o is 1-hop reachable), so "
        "it CANNOT fire -- the original atom's 'both control arms fire correctly' is WRONG for the 1-hop "
        "arm; the '>1hop+0.02' gate is near-vacuous. (3b) the frozen-encoder (0.012) is a WEAK bar: "
        "MiniLM-L6 Hits@1 NN-to-SUBJECT-name, no relation-conditioning (cell line 243-250) -- a genuine "
        "non-compositional shortcut baseline that fires for a real reason, but NOT a strong completion "
        "encoder. substrate_2hop=0.426 is honest and conservative (multi-valued intermediate nodes "
        "penalize the argmax chain). The load-bearing result is the RELATIVE claim (composition beats the "
        "similarity shortcut), NOT the absolute 36.5x. "
        "(4) TIER: cert585 HOLDS as a CG INGEST+GOVERNANCE cert under per-seed tightening; the COMPOSITION "
        "dimension is scoped to MEASURED_MECHANISM. CROSS-ARC RECONCILIATION (mandatory overlap check): the "
        "June-19 arc (" + JUNE19_REF + ") PROVED substrate multi-hop completion UNDERPERFORMS frozen-BGE "
        "single-hop (ConceptNet Hits@10 0.45 < BGE 0.50 < exact-closure 1.0) and that the substrate's KG "
        "value is the fact-fabrication/refuse-gate NOT positive completion -- that result is NOT overturned "
        "by N8's 36.5x (different, weaker baseline: MiniLM Hits@1 NN-to-subject vs BGE Hits@10 completion). "
        "Parent cert585 NOT superseded (its ingest+governance CG core reproduces); its three over-claims "
        "(setrecall 'not saturation', 1hop 'fires correctly', 'beats the semantic-similarity bar = genuine "
        "compositional inference') are SCOPED DOWN by this amendment."
    ),
    "provenance": {
        "cell": "experiments/exp_n8_conceptnet_ingest_eval_v1.py",
        "commit": CELL_COMMIT,
        "canonical_anchor": "n8_conceptnet_ingest_eval_canon_v1",
        "prereg": "notes/n8_conceptnet_ingest_pre_reg_2026-06-22.md",
        "metrics_path": "data/exp_n8_conceptnet_ingest_eval_canon_v1/metrics.json",
        "parent_cert585_atom": PARENT_ID,
        "parent_cell_commit": "8bbc11c4",
        "seeds": [7, 17, 23],
        "run_mode": "full",
        "elapsed_s": 598.8,
        "ts_iso": TS_ISO,
        "atomized_by": ATOMIZED_BY,
        "verified_off_data": True,
        "verified_off_data_note": (
            "Independent recompute off canon metrics.json: setrecall all=1.000 3 seeds (sub-1.0 only "
            "seed7 M50000=0.9997); chance floor meanK/n_ent = 2.372/80181 = 2.96e-5 (1.000 = 33,799x "
            "above); refuse ood min 0.9967 acc min 0.9933 held-split conf-ratio ~3.4x; 2hop mean 0.4258 "
            "1hop 0.0 enc 0.01167 ratio 36.5x per-seed all>=2.0x. Mechanism inspected: set_recall_at_k "
            "line 150-164 (top-K over full n_ent, not stored set); refuse_gate line 167-188 (held-split, "
            "no leak); inference_transfer line 207-254 (1hop pinned by leak guard line 229; encoder "
            "NN-to-subject line 243-250)."
        ),
    },
    "verified_numbers": {
        "setrecall_all_M100000_per_seed": [1.0, 1.0, 1.0],
        "setrecall_scale_curve_min_value": 0.9997,
        "setrecall_scale_curve_min_at": "seed7_M50000",
        "chance_floor_recall_M100000": 2.96e-5,
        "setrecall_x_above_chance": 33799,
        "n_ent_M100000": 80181,
        "n_keys_M100000": 42154,
        "mean_K": 2.372,
        "refuse_ood_per_seed": [1.0, 0.9966666666666667, 1.0],
        "refuse_acc_per_seed": [0.9966666666666667, 1.0, 0.9933333333333333],
        "refuse_ood_min": 0.9967,
        "refuse_acc_min": 0.9933,
        "inkb_ood_conf_ratio_per_seed": [3.40, 3.40, 3.34],
        "twohop_per_seed": [0.415, 0.425, 0.4375],
        "twohop_mean": 0.4258,
        "onehop_per_seed": [0.0, 0.0, 0.0],
        "encoder_per_seed": [0.010, 0.015, 0.010],
        "encoder_mean": 0.01167,
        "twohop_vs_encoder_ratio_mean": 36.5,
        "twohop_vs_encoder_ratio_per_seed": [41.5, 28.33, 43.75],
        "leak_skipped_per_seed": [1, 6, 10],
    },
    "saturation_verdict": (
        "GENUINE not vacuous (top-K over 80,181 distractors, chance 2.96e-5, 33,799x above; seed7 "
        "M50000=0.9997 proves non-by-construction) BUT SCALE-CURVE NON-DISCRIMINATING (N=8192 capacity "
        "unexhausted at 100k; real capacity pass with untested headroom, not a measured degradation cliff)"
    ),
    "refuse_verdict": (
        "PASS per-seed (ood min 0.9967, acc min 0.9933, both >> 0.80); held-split no-leak; ~3.4x conf "
        "separation; the GENUINELY-DISCRIMINATING dimension; reinforces June-19 refuse-gate-is-the-value"
    ),
    "composition_fairness_verdict": (
        "1hop=0.000 is BY CONSTRUCTION (leak guard), NOT a firing control -> '>1hop+0.02' gate near-"
        "vacuous. Encoder 0.012 is a genuine but WEAK non-compositional bar (MiniLM Hits@1 NN-to-subject, "
        "no relations). 2hop=0.426 honest+conservative. Load-bearing = RELATIVE claim (composition > "
        "similarity shortcut), NOT absolute 36.5x. Does NOT beat a strong completion encoder (June-19: "
        "substrate multi-hop < BGE, ConceptNet Hits@10 0.45<0.50, NOT overturned)."
    ),
    "honest_scoped_stage1_ingest_claim": (
        "Substrate INGESTS 100k real ConceptNet facts (N=8192 multi-value Hebbian) at setrecall ~1.000 vs "
        "~80k distractors (genuine, 33,799x above chance; capacity headroom untested), GOVERNS via "
        "held-split refuse-gate (OOD-refuse/accept ~0.99 per-seed; the genuinely-discriminating dim), and "
        "COMPOSES 2-hop at 0.426 beating a NON-compositional subject-NN-by-name shortcut 36.5x. Does NOT "
        "establish superiority over a strong completion encoder (June-19: substrate multi-hop < BGE, not "
        "overturned)."
    ),
    "framing_corrections_vs_parent_cert585": [
        "cert585 said setrecall discriminator is 'REAL not by-construction-saturation' -> CORRECT on "
        "non-vacuousness (33,799x above chance) but MISLEADING on the scale-curve: pinned-1.0 is a "
        "capacity pass with UNTESTED headroom, NOT a demonstrated scale-robustness with a measured cliff.",
        "cert585 said '1hop=0.000 ... mechanism-DEAD can-fail control ... both control arms fire "
        "correctly' -> the 1-hop arm CANNOT fire (pinned at 0 by the leak guard); it does not 'fire "
        "correctly', it is structurally pinned. Only the encoder ratio is a load-bearing discriminator.",
        "cert585 said 'substrate is doing genuine compositional inference ... beats the semantic-"
        "similarity bar' -> SCOPE DOWN: beats a WEAK non-compositional NN-by-name shortcut (MiniLM "
        "Hits@1), NOT a strong completion encoder. June-19 arc proved substrate multi-hop < frozen-BGE "
        "completion (ConceptNet Hits@10 0.45<0.50); NOT overturned. Composition dim = MEASURED_MECHANISM.",
    ],
    "composes": [PARENT_ID, "math::T3/EXP_u1_fb15k237_ingest_eval_v1"],
    "cross_arc_overlap_check": (
        "top hit cosine=0.337 (B1 Auditable multi-hop / Hebbian KG note); June-19 reconciliation at "
        "cosine=0.291 (" + JUNE19_REF + "): substrate multi-hop completion UNDERPERFORMS frozen-BGE "
        "single-hop, KG value = refuse-gate NOT completion -- NOT overturned by N8's weaker-baseline "
        "36.5x. This is a targeted re-VET + scope-correction of EXISTING cert585, NOT a rediscovery."
    ),
    "anchor": "n8_conceptnet_ingest_eval_v1",
    "cell_commit": CELL_COMMIT,
    "seeds": [7, 17, 23],
    "run_mode": "full",
    "cardinality_ok": True,
    "arms_differ_verified": True,
    "verified_off_data": True,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": "2026-07-07_n8_conceptnet_canon_perseed_revet",
    "ts": TS,
    "ts_iso": TS_ISO,
    "ts_added": TS_ISO,
    "aliases": [
        "N8 ConceptNet ingest canonical re-VET confirms cert585 ingest+governance CG scopes composition to MM",
        "setrecall 1.000 genuine 33799x above chance but scale-curve non-discriminating capacity headroom untested",
        "1hop=0 by-construction not firing control; frozen-encoder weak MiniLM Hits@1 NN-to-subject not strong completion",
        "substrate multi-hop underperforms BGE June-19 not overturned; N8 composition beats similarity shortcut only",
    ],
}
atom_math["added_atom_id"] = atom_math["id"]

ledger_math = {
    "ts": TS,
    "ts_iso": TS_ISO,
    "atom_id": atom_math["id"],
    "corpus": "math",
    "tier": "CHAIN_GRADE",
    "disposition": "revet_confirm_cert585_ingest_governance_CG_scope_composition_MM_no_new_cert",
    "cert_status": (
        "revet_confirms_cert585_under_per_seed_gating_no_double_count_composition_scoped_to_MM"
    ),
    "cert_class": (
        "conceptnet_kb_ingest_at_scale_plus_refuse_governance_per_seed_confirmed_composition_beats_"
        "noncompositional_shortcut_only"
    ),
    "cert_increment_delta": 0,
    "cert_delta": {"CG": 0, "MM": 0, "HF": 0},
    "cert_delta_note": (
        "cert_delta ZERO: n8 already counts as cert585 (chain-grade, commit 8bbc11c4, 2026-06-22). This "
        "canonical per-seed-tightened run REPRODUCES the numbers off-disk exactly, so it CONFIRMS cert585 "
        "under worst-seed gating (no new cert; no double-count -- avoids the July-1 rediscovery pattern). "
        "Ingest (setrecall genuine 33,799x above chance) + governance (refuse per-seed ood 0.9967/acc "
        "0.9933) HOLD as CG. Composition dim SCOPED to MEASURED_MECHANISM: 2hop 0.426 beats a WEAK "
        "non-compositional NN-by-name shortcut (36.5x) but 1hop=0 is by-construction (leak guard, not a "
        "firing control) and the encoder is MiniLM Hits@1 not a strong completion encoder -- June-19 arc "
        "(substrate multi-hop < BGE, ConceptNet Hits@10 0.45<0.50) NOT overturned. Parent cert585 NOT "
        "superseded; its three over-claims scoped down by this amendment."
    ),
    "verified_off_data": True,
    "anchor": "n8_conceptnet_ingest_eval_v1",
    "cell_commit": CELL_COMMIT,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks",
    "landed_VET_session": "2026-07-07_n8_conceptnet_canon_perseed_revet",
    "composes": [PARENT_ID],
    "amends_parent": PARENT_ID,
}


def append_jsonl_a5(path: Path, new_row: dict, label: str) -> int:
    pre_lines = []
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            pre_lines = f.read().splitlines()
    pre_count = len(pre_lines)
    print(f"[A5] {label}: pre_count={pre_count}")

    for i, ln in enumerate(pre_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail line {i+1}: {e}")

    new_line = json.dumps(new_row, ensure_ascii=True)
    parsed_back = json.loads(new_line)
    if "id" in new_row:
        assert parsed_back.get("id") == new_row.get("id")
    if "atom_id" in new_row:
        assert parsed_back.get("atom_id") == new_row.get("atom_id")

    out_text = "\n".join(pre_lines + [new_line]) + "\n"
    tmp_path = path.with_suffix(path.suffix + ".tmp_a5")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    import time as _time
    for _attempt in range(10):
        try:
            os.replace(str(tmp_path), str(path))
            break
        except PermissionError:
            if _attempt == 9:
                raise
            _time.sleep(0.1 * (2 ** _attempt))

    with open(path, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    print(f"[A5] {label}: post_count={post_count}")
    assert post_count == pre_count + 1

    tail = json.loads(post_lines[-1])
    if "id" in new_row:
        assert tail["id"] == new_row["id"]
    if "atom_id" in new_row:
        assert tail["atom_id"] == new_row["atom_id"]

    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail line {i+1}: {e}")

    print(f"[A5] {label}: OK")
    return post_count


def main():
    print(f"[A5] atomize START {ATOMIZED_BY} ts={time.time():.3f}")
    append_jsonl_a5(MATH_ATOMS, atom_math, "math/atoms (N8 ConceptNet canon RE-VET confirm+scope)")
    append_jsonl_a5(CERT_LEDGER, ledger_math, "cert_ledger (N8 re-VET, cert_delta 0)")
    print(f"[A5] DONE OK")
    print(f"[A5] n8_conceptnet canon -> CONFIRMS cert585 (CG ingest+governance) + SCOPES composition to MM; cert_delta 0")


if __name__ == "__main__":
    main()
