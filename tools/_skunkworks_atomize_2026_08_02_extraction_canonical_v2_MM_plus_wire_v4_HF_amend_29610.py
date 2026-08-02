"""A5-gated LOCAL-ONLY atomize of two independently-VET'd 2026-08-02 landings (commit 9abc82cd2).
AUDIT-ONLY (hdi_skunkworks). Independent .venv recompute off raw metrics.json on disk (NOT verdict_msg
strings, NOT the Director summary, NOT the WHERE-banner commit-message framing). No experiment authored
or dispatched by the auditor.

TWO atoms, store head 29610 -> seqs 29611/29612:
  29611 math: extraction_commit_then_revise_v2 -- MEASURED_MECHANISM (proven-bound, NOT chain-grade/HARD_PASS).
              Deflates the Director spawn prompt's "general-purpose agent/patient extraction achieved,
              29610 wall broken at mechanism level" framing. The isolated-benchmark improvement (canonical
              role_acc 0.658 > position floor 0.536, quotative/byagent preserved, gate FP dropped) is real
              and internally consistent, BUT full independent per-prediction recompute was not possible
              (metrics.json ships only per-arm/per-kind AGGREGATES, no per-mention prediction dump) --
              verification here is aggregate-consistency + calibration-sanity, not bit-for-bit recompute,
              which caps the tier below chain-grade on its own. More importantly, the cell's OWN very next
              sibling cell (v4, same commit, 3 minutes later, wiring this exact model end-to-end onto real
              diverse McGuffey gold) shows the improvement does NOT propagate and slightly REGRESSES vs the
              simpler v1 lever (0.4208 < 0.4333) -- see atom 29612. AMENDS 29610 (refines: canonical-KIND
              classification improved in an isolated pooled discriminator task; the true end-to-end
              generalization wall from 29610 is NOT resolved, it is reinforced by 29612).
  29612 math: wire_extraction_accumulate_wm_oracle_vs_real_v4 -- HARD_FAIL (honest negative, cert_delta 0).
              Independent recompute (re-deriving multi_event_recall by hand from per_entity_dump) confirms
              the two-lever STAGE-1 extractor from 29611, wired end-to-end onto the SAME diverse real
              per-entity gold used to test v1/v2/v3 STAGE-1 variants, does NOT beat the one-lever v1/v3
              baseline (real=0.4208 vs v3=0.4333, delta -0.0125, misses V3_MUST_BEAT_MARGIN=0.03) and
              remains well below REAL_HARD_PASS_MIN=0.5. Confirms 29610's wall (extraction generalization
              to canonical/diverse constructions + 22-29% role-inventory coverage gap) STANDS despite a
              genuine, targeted repair attempt. Oracle reproduces 1.0000 (WM organ still validated given
              correct roles); floor at chance -- can-fail gates hold, so this is a trusted negative.

Both cells were committed HONESTLY (commit 9abc82cd2 message itself states "did not propagate to a
measurable end-to-end lift... honestly reported as a negative/flat result rather than claimed as a win"),
so this atomization is a scope/tier correction of the WHERE-banner ("wall broken at mechanism level"),
not a correction of the cell author's own claims.

DISK-VERIFY performed before this script banks:
  #1 data/exp_extraction_commit_then_revise_v2/metrics.json: canonical role_acc V2=0.6576 (role_n=330,
     consistent across all 5 arms) > POSITION floor=0.5364 (CANONICAL_MIN band=0.5064, cleared);
     quotative=0.7541 (QUOTATIVE_MIN=0.75, cleared by 0.004 -- thin margin); byagent=0.7872
     (BYAGENT_MIN=0.68, cleared); v1_gate_fp=0.2124 -> v2_gate_fp=0.1416 (dropped); RANDOM arm canonical
     =0.2697 approx 1/4 chance for 4-way vocab (agent/patient/addressee/none) -- calibration sanity check
     passes; POSITION arm quotative=0.0820 < RANDOM quotative=0.2623 -- the classic marked-construction
     INVERSION signature (linear-order heuristic actively worse than chance on marked constructions,
     confirming the 29599 signature reproduces in the no-revise/position-only ablation). CLAUSE_POSITION
     (clause-level lever ALONE, no gate lever) canonical=0.6727, HIGHER than the combined two-lever
     COMMIT_REVISE_V2=0.6576 -- the gate/revise lever trades a small amount of isolated canonical accuracy
     for large marked-construction preservation (CLAUSE_POSITION byagent=0.1489, near floor, vs
     COMMIT_REVISE_V2 byagent=0.7872): a genuine, honest tradeoff, not a strict Pareto win. NO raw
     per-prediction dump exists in this metrics.json (only per_arm_per_kind aggregates + grid_summary) --
     independent verification here is aggregate-consistency (matching role_n/full_n across all arms,
     calibration-sanity on RANDOM, ablation-signature reproduction), NOT a bit-for-bit per-item recompute.
  #2 data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v4/metrics.json: independently RE-DERIVED
     real_multi_event_recall by hand-averaging the 20 multi_event=true entities' "real" arm per-entity
     recalls from per_entity_dump (excluding the 3 single-event entities, matching real_n_entities=20) --
     got 8.4167/20=0.420833..., MATCHES summary's real_multi_event_recall=0.4208333333333333 EXACTLY.
     Same recompute for real_commit_revise_v1 arm: got 8.6667/20=0.433333..., MATCHES
     real_commit_revise_v1_multi_event_recall=0.4333333333333333 EXACTLY. role_census: agent=32+patient=9
     =41 reachable / 58 total events -> unreachable=17/58=0.293103..., MATCHES unreachable_fraction
     =0.29310344827586204 EXACTLY. oracle_multi_event_recall=1.0 (all 20 multi-event per_entity oracle
     recalls =1.0, confirmed by inspection). floor=0.1833 (well below REAL_HARD_PASS_MIN discriminator,
     can-fail-consistent). Confirmed via metrics.json "bands": V3_MUST_BEAT_MARGIN=0.03, v4 misses it
     (v4_minus_commit_revise_v1_reproduced_here=-0.0125). Confirmed cell-commit both files land under the
     SAME commit 9abc82cd2 (git show), with v4 landing ts_iso 15:55:24Z, 3m4s after v2's 15:52:20Z --
     i.e. v4 IS the direct, immediate end-to-end follow-up test of the v2 STAGE-1 model, not an unrelated
     or stale comparison.

cross_arc_overlap check (both atoms): bash tools/substrate_query.sh "clause-level agent subject margin
gated graceful degrade canonical role extraction commit revise" -> top hit cosine=0.2871 (a distinct
clause-seg/composition atom, no overlap at cosine>0.30). NOVEL, no dedup concern.

Commits verified present: 9abc82cd296ffb664db1996ac35e464dc2fb0146 (both cells, single commit).
Store head before this batch = 29610 (math atoms tail; meta atoms max 29604; ledger max 29610).
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS_MATH = "data/substrate_index/math/atoms.jsonl"
ATOMS_META = "data/substrate_index/meta/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"


def iseq(o):
    try:
        return int(o.get("seq"))
    except Exception:
        return -1


def load(p):
    return [l for l in open(p, encoding="utf-8").read().splitlines() if l.strip()]


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


# ---- PRE-GATE ----
math_lines = load(ATOMS_MATH)
meta_lines = load(ATOMS_META)
ledger_lines = load(LEDGER)
pm = [json.loads(l) for l in math_lines]
pe = [json.loads(l) for l in meta_lines]
pl = [json.loads(l) for l in ledger_lines]
existing_ids = {o.get("atom_id") for o in (pm + pe) if o.get("atom_id")}
assert not any("\r" in l for l in (math_lines[-5:] + meta_lines[-5:]))
STORE_HEAD = max(max(iseq(o) for o in pm), max(iseq(o) for o in pe), max(iseq(o) for o in pl))
assert STORE_HEAD == 29610, f"expected store head 29610, got {STORE_HEAD}"
assert not any("extraction_commit_then_revise_v2" in o.get("anchor_name", "") for o in pm)
assert not any("wire_extraction_accumulate_wm_oracle_vs_real_v4" in o.get("anchor_name", "") for o in pm)
assert any(iseq(o) == 29610 for o in pm), "parent 29610 missing (needed for amends_seq)"
print(f"PRE-GATE OK: store head {STORE_HEAD}; parent 29610 present; seqs 29611/29612.")

# =====================================================================================================
# OFF-DISK independent recompute
# =====================================================================================================
# ---- #1 extraction_commit_then_revise_v2 ----
V2 = json.load(open("data/exp_extraction_commit_then_revise_v2/metrics.json", encoding="utf-8"))
s2 = V2["summary"]
assert V2["verdict"] == "HARD_PASS_BOTH_LEVERS_BEAT_POSITION_FLOOR_PRESERVE_MARKED"
assert abs(s2["commit_revise_v2_canonical_role_acc"] - 0.6575757575757576) < 1e-12
assert abs(s2["position_canonical_role_acc"] - 0.5363636363636364) < 1e-12
assert abs(s2["commit_revise_v2_quotative_role_acc"] - 0.7540983606557377) < 1e-12
assert abs(s2["commit_revise_v2_byagent_role_acc"] - 0.7872340425531915) < 1e-12
assert abs(s2["v1_canonical_gate_fp_rate"] - 0.2124) < 1e-3
assert abs(s2["v2_canonical_gate_fp_rate"] - 0.1415929203539823) < 1e-12
assert s2["canonical_beats_position_floor"] is True
assert s2["quotative_preserved"] is True and s2["byagent_preserved"] is True
assert s2["no_revise_reproduces_inversion_quotative"] is True and s2["no_revise_reproduces_inversion_byagent"] is True
bands2 = V2["bands"]
assert abs(bands2["QUOTATIVE_MIN"] - 0.75) < 1e-9
quot_margin = s2["commit_revise_v2_quotative_role_acc"] - bands2["QUOTATIVE_MIN"]
assert 0 < quot_margin < 0.01  # thin margin, confirmed
pak2 = s2["per_arm_per_kind"]
role_ns = {k: pak2[k]["canonical"]["role_n"] for k in pak2}
assert len(set(role_ns.values())) == 1 and list(role_ns.values())[0] == 330  # consistent test set across all arms
full_ns = {k: pak2[k]["canonical"]["full_n"] for k in pak2}
assert len(set(full_ns.values())) == 1 and list(full_ns.values())[0] == 771
# calibration sanity: RANDOM canonical near 1/4 chance (4-way: agent/patient/addressee/none)
assert abs(pak2["RANDOM"]["canonical"]["role_acc"] - 0.25) < 0.03
# marked-construction inversion signature: POSITION quotative BELOW RANDOM quotative (worse than chance)
assert pak2["POSITION"]["quotative"]["role_acc"] < pak2["RANDOM"]["quotative"]["role_acc"]
# clause-level-alone lever (CLAUSE_POSITION) beats the combined two-lever on canonical in isolation,
# but loses badly on byagent -- the honest tradeoff, not a strict Pareto win
assert pak2["CLAUSE_POSITION"]["canonical"]["role_acc"] > s2["commit_revise_v2_canonical_role_acc"]
assert pak2["CLAUSE_POSITION"]["passive_byagent"]["role_acc"] < 0.20
assert "per_prediction" not in json.dumps(V2)[:50000]  # sanity: confirming no raw per-item dump ships in this file
v2_sha = sha16("data/exp_extraction_commit_then_revise_v2/metrics.json")
cellv2_sha = sha16("experiments/exp_extraction_commit_then_revise_v2.py")
print(f"#1 OFF-DISK OK: canonical V2={s2['commit_revise_v2_canonical_role_acc']:.4f} > "
      f"POSITION={s2['position_canonical_role_acc']:.4f}; quot={s2['commit_revise_v2_quotative_role_acc']:.4f} "
      f"(margin over QUOTATIVE_MIN={quot_margin:.4f}, thin); byagent={s2['commit_revise_v2_byagent_role_acc']:.4f}; "
      f"gate_fp {s2['v1_canonical_gate_fp_rate']:.4f}->{s2['v2_canonical_gate_fp_rate']:.4f}; "
      f"calibration sanity + inversion-signature + role_n/full_n consistency all confirmed; "
      f"CLAUSE_POSITION-alone canonical={pak2['CLAUSE_POSITION']['canonical']['role_acc']:.4f} beats "
      f"the two-lever combo in isolation but byagent collapses to "
      f"{pak2['CLAUSE_POSITION']['passive_byagent']['role_acc']:.4f} (honest tradeoff). "
      f"metrics_sha={v2_sha}")

# ---- #2 wire_extraction_accumulate_wm_oracle_vs_real_v4 ----
V4 = json.load(open("data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v4/metrics.json", encoding="utf-8"))
s4 = V4["summary"]
assert V4["verdict"] == "HARD_FAIL_V4_DID_NOT_BEAT_V3_SAME_GOLD"
assert abs(s4["oracle_multi_event_recall"] - 1.0) < 1e-9
assert abs(s4["real_multi_event_recall"] - 0.4208333333333333) < 1e-12
assert abs(s4["floor_multi_event_recall"] - 0.18333333333333332) < 1e-12
assert abs(s4["real_v1_multirole_multi_event_recall"] - 0.4333333333333333) < 1e-12
assert abs(s4["real_commit_revise_v1_multi_event_recall"] - 0.4333333333333333) < 1e-12
assert s4["beats_v2_same_gold_anchor"] is False
assert abs(s4["v4_minus_v2_anchor"] - (-0.012466666666666737)) < 1e-9
assert s4["beats_commit_revise_v1_reproduced_here"] is False
assert abs(s4["v4_minus_commit_revise_v1_reproduced_here"] - (-0.012500000000000011)) < 1e-9
rc = s4["role_census"]
assert rc["counts"]["agent"] + rc["counts"]["patient"] == rc["reachable_agent_patient_events"] == 41
assert rc["total_events"] - rc["reachable_agent_patient_events"] == rc["unreachable_events"] == 17
assert abs(rc["unreachable_fraction"] - 0.29310344827586204) < 1e-12
bands4 = V4["bands"]
assert abs(bands4["V3_MUST_BEAT_MARGIN"] - 0.03) < 1e-9
assert abs(bands4["REAL_HARD_PASS_MIN"] - 0.5) < 1e-9
assert s4["real_multi_event_recall"] < bands4["REAL_HARD_PASS_MIN"]

# independent by-hand re-derivation of real_multi_event_recall from per_entity_dump (not trusting summary)
dump = V4["per_entity_dump"]
real_multi = [e["real_recall"] for e in dump if e["multi_event"]]
commit_v1_multi = [e["real_commit_revise_v1_recall"] for e in dump if e["multi_event"]]
oracle_multi = [e["oracle_recall"] for e in dump if e["multi_event"]]
assert len(real_multi) == 20 == len(commit_v1_multi) == len(oracle_multi)
recomputed_real = sum(real_multi) / len(real_multi)
recomputed_commit_v1 = sum(commit_v1_multi) / len(commit_v1_multi)
recomputed_oracle = sum(oracle_multi) / len(oracle_multi)
assert abs(recomputed_real - s4["real_multi_event_recall"]) < 1e-9
assert abs(recomputed_commit_v1 - s4["real_commit_revise_v1_multi_event_recall"]) < 1e-9
assert abs(recomputed_oracle - s4["oracle_multi_event_recall"]) < 1e-9
v4_sha = sha16("data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v4/metrics.json")
cellv4_sha = sha16("experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v4.py")
print(f"#2 OFF-DISK OK: independently RE-DERIVED (not trusted from summary) real_multi_event_recall="
      f"{recomputed_real:.6f} (n=20, matches reported {s4['real_multi_event_recall']:.6f} EXACTLY), "
      f"commit_revise_v1={recomputed_commit_v1:.6f} (matches {s4['real_commit_revise_v1_multi_event_recall']:.6f}), "
      f"oracle={recomputed_oracle:.6f} (matches 1.0). v4 misses V3_MUST_BEAT_MARGIN by "
      f"{s4['v4_minus_commit_revise_v1_reproduced_here']:.4f}. role_census unreachable="
      f"{rc['unreachable_events']}/{rc['total_events']}={rc['unreachable_fraction']:.4f}. metrics_sha={v4_sha}")

# chronology + shared-commit check
import subprocess
commit_hash = "9abc82cd296ffb664db1996ac35e464dc2fb0146"
show = subprocess.run(["git", "show", "--stat", commit_hash], cwd=".", capture_output=True, text=True).stdout
assert "exp_extraction_commit_then_revise_v2.py" in show and "exp_wire_extraction_accumulate_wm_oracle_vs_real_v4.py" in show
print(f"CHRONOLOGY OK: both cells land under single commit {commit_hash[:9]}; "
      f"v2 ts_iso={V2['ts_iso']}, v4 ts_iso={V4['ts_iso']} (v4 is the immediate end-to-end follow-up).")

ts = time.time()
ts_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
ts_day = "2026-08-02"


def A5_write(path, lines, new_atom, tier_expect):
    line = json.dumps(new_atom, ensure_ascii=False)
    assert "\r" not in line and "\n" not in line
    new_text = "\n".join(lines + [line]) + "\n"
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp"); os.close(fd)
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(new_text); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, path)
    raw = open(path, "rb").read()
    assert b"\r\n" not in raw, f"CRLF doubling in {path}"
    v = [json.loads(l) for l in open(path, encoding="utf-8").read().splitlines() if l.strip()]
    assert len(v) == len(lines) + 1
    assert v[-1]["atom_id"] == new_atom["atom_id"] and v[-1].get("tier") == tier_expect
    return v


# =====================================================================================================
# ATOM 29611 -- MATH: extraction_commit_then_revise_v2 -- MEASURED_MECHANISM (proven-bound). cert_delta 0.
# =====================================================================================================
AID1 = ("math::extraction_commit_then_revise_v2_MEASURED_MECHANISM_AUDITOR_DEFLATED_from_cell_HARD_PASS_"
    "clause_level_agent_equals_subject_plus_margin_gated_graceful_degrade_beats_position_only_floor_on_"
    "an_ISOLATED_pooled_canonical_quotative_byagent_passive_4way_discriminator_task_canonical_0p658_gt_"
    "position_0p536_quotative_0p754_thin_margin_over_0p75_bar_byagent_0p787_preserved_gate_fp_dropped_"
    "0p212_to_0p142_no_revise_ablation_reproduces_29599_marked_construction_inversion_signature_BUT_no_"
    "raw_per_prediction_dump_ships_in_metrics_json_only_aggregates_so_verification_here_is_aggregate_"
    "consistency_plus_calibration_sanity_NOT_bit_for_bit_recompute_capping_the_tier_below_chain_grade_"
    "MORE_IMPORTANTLY_the_very_next_sibling_cell_v4_same_commit_3min_later_wires_this_EXACT_model_end_"
    "to_end_onto_real_diverse_McGuffey_gold_and_it_does_NOT_propagate_slightly_REGRESSES_vs_the_simpler_"
    "v1_lever_see_seq_29612_AMENDS_29610_refines_does_NOT_resolve_the_extraction_generalization_wall_"
    "LOCAL_ONLY")
assert AID1 not in existing_ids
HEAD1 = ("MEASURED_MECHANISM (proven-bound, CERT +0; DEFLATED from the cell's own verdict string "
    "HARD_PASS_BOTH_LEVERS_BEAT_POSITION_FLOOR_PRESERVE_MARKED and from the Director's WHERE-banner "
    "framing 'wall broken at mechanism level'). The two-lever fix (margin-gated graceful-degrade revise + "
    "clause-level agent=first-non-quoted-mention-per-clause) IS a real, internally-consistent improvement "
    "on an ISOLATED pooled 4-way discriminator task (canonical/quotative/byagent/passive sentence kinds, "
    "binary-ish agent/patient/addressee/none role vocab): canonical role_acc 0.658 beats the position-only "
    "floor 0.536 (v1 commit-then-revise was 0.479, a prior MIDDLE_BAND miss), quotative 0.754 and byagent "
    "0.787 preserved above their floors (quotative margin over its 0.75 bar is thin, 0.004), canonical gate "
    "false-positive rate dropped 0.212->0.142, and the no-revise/position-only ablation still reproduces "
    "the 29599 marked-construction-inversion signature (POSITION arm scores BELOW its own RANDOM baseline "
    "on quotative -- a genuine positive control). AUDITOR CAP ON TIER: this metrics.json ships only "
    "per-arm/per-kind AGGREGATES (role_acc/role_n/full_acc/full_n per kind), no raw per-mention prediction "
    "dump -- so independent verification here is limited to aggregate-consistency (role_n/full_n identical "
    "across all 5 arms => same held-out test set), calibration-sanity (RANDOM arm ~=1/4 chance), and "
    "ablation-signature reproduction, NOT a bit-for-bit per-item recompute. That alone would cap this below "
    "chain-grade. THE MORE LOAD-BEARING FINDING, however, is atom 29612: the cell author's OWN immediate "
    "next cell (v4, same commit 9abc82cd2, landing 3m4s later) wires this EXACT STAGE-1 model end-to-end "
    "onto the real diverse multiclause McGuffey gold used to test all STAGE-1 variants, and there the "
    "improvement does NOT propagate -- it slightly REGRESSES vs the simpler one-lever v1 (real=0.4208 vs "
    "v1/v3=0.4333). ALSO WORTH NOTING: the clause-level lever ALONE (CLAUSE_POSITION arm, no gate/revise "
    "lever) actually scores HIGHER on canonical in isolation (0.673) than the combined two-lever config "
    "(0.658) -- the gate/revise lever's real contribution is preserving byagent (0.787 vs CLAUSE_POSITION's "
    "0.149, near-floor) at a small cost to isolated canonical accuracy, a genuine and honest tradeoff, not "
    "a strict improvement across the board.")
atom1 = {
    "atom_id": AID1, "seq": 29611, "op": "atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "grade": "MM_isolated_pooled_discriminator_task_win_deflated_from_cell_HARD_PASS_no_endtoend_propagation_see_29612",
    "verdict": "HARD_PASS_BOTH_LEVERS_BEAT_POSITION_FLOOR_PRESERVE_MARKED_auditor_scoped_MEASURED_MECHANISM",
    "anchor": "extraction_commit_then_revise_v2", "anchor_name": "extraction_commit_then_revise_v2",
    "cell": "experiments/exp_extraction_commit_then_revise_v2.py",
    "cell_commit": "9abc82cd2", "cell_content_sha256_16": cellv2_sha,
    "metrics_path": "data/exp_extraction_commit_then_revise_v2/metrics.json", "metrics_sha256_16": v2_sha,
    "headline": HEAD1,
    "key_metrics": {
        "cell_verdict": "HARD_PASS_BOTH_LEVERS_BEAT_POSITION_FLOOR_PRESERVE_MARKED",
        "auditor_tier": "MEASURED_MECHANISM", "cert_delta": 0,
        "canonical_v2": 0.6575757575757576, "canonical_position_floor": 0.5363636363636364,
        "canonical_v1": 0.47878787878787876, "canonical_clause_position_alone": 0.6727272727272727,
        "quotative_v2": 0.7540983606557377, "quotative_min_band": 0.75, "quotative_margin": quot_margin,
        "byagent_v2": 0.7872340425531915, "byagent_min_band": 0.68,
        "byagent_clause_position_alone": 0.14893617021276595,
        "gate_fp_v1": 0.2124, "gate_fp_v2": 0.1415929203539823,
        "no_revise_reproduces_inversion": True,
        "role_n_consistent_across_arms": 330, "full_n_consistent_across_arms": 771,
        "raw_per_prediction_dump_available": False,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv recompute off metrics.json summary/bands/per_arm_per_kind "
        "(NOT verdict_msg): all cited numbers reproduced exactly. Independent checks performed beyond what "
        "the cell reports: (1) role_n=330/full_n=771 identical across all 5 arms confirming a single "
        "consistent held-out test set, not per-arm cherry-picked subsets; (2) RANDOM arm canonical role_acc "
        "0.270 approx 1/4 chance for the 4-way vocab, a calibration-sanity check on the harness; (3) POSITION "
        "arm quotative (0.082) scores BELOW its own RANDOM baseline (0.262) -- the specific below-chance "
        "inversion signature that makes the no-revise ablation a genuine positive control, not merely a "
        "restated claim; (4) CLAUSE_POSITION-alone vs COMMIT_REVISE_V2 comparison independently confirms the "
        "tradeoff framing (clause-lever-alone wins canonical, loses byagent badly). NO raw per-prediction "
        "dump exists in this file -- full bit-for-bit recompute of the underlying 330 canonical predictions "
        "was not possible; this caps the verification below a chain-grade bar even though every aggregate "
        "check passed."),
    "composes_seq": [], "corrects_seq": [], "amends_seq": [29610],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("Real, reproducible-on-its-own-aggregates improvement on an ISOLATED pooled 4-way "
        "discriminator task (canonical/quotative/byagent/passive sentence-kind classification with a small "
        "role vocab), achieved via a well-designed tradeoff (clause-level agent assignment + margin-gated "
        "graceful degrade) that preserves marked-construction wins while lifting canonical accuracy above "
        "the position-only floor. NOT general-purpose semantic-role extraction, NOT proof the 29610 wall is "
        "broken -- see atom 29612, the direct end-to-end test of this exact model, which shows no "
        "propagation and a slight regression vs the simpler v1 lever. Do not cite this atom alone as "
        "'extraction generalization solved'; cite it paired with 29612's honest end-to-end result."),
    "framing_correction": ("The cell's own verdict string (HARD_PASS_BOTH_LEVERS_BEAT_POSITION_FLOOR_"
        "PRESERVE_MARKED) is narrowly and accurately scoped to the isolated task and IS supported by the "
        "aggregate data available. The Director spawn prompt's broader framing ('GENERAL-PURPOSE agent/"
        "patient extraction across canonical + marked constructions is now achieved', 'the wall from atom "
        "29610 broken at the mechanism level for agent/patient') and the git WHERE-banner ('Wall broken at "
        "mechanism level... End-to-end flat = role-INVENTORY coverage ceiling') UNDERSTATE how much the wall "
        "persists: it is not merely a coverage-ceiling issue (22-29% unreachable roles) layered on top of a "
        "solved extraction problem -- the extraction-generalization component of the wall (canonical/diverse "
        "constructions) is ALSO not solved end-to-end, per atom 29612's direct measurement. This is a "
        "downward scope correction of the Director's framing, not a disagreement with the cell author's own "
        "(correctly narrow) verdict, and not a retraction of 29610's original characterization -- if "
        "anything this REINFORCES 29610."),
    "revival_criteria": ("Per 29610's own revival_criteria (construction-conditional multi-role extraction, "
        "not a binary is-agent classifier; extend beyond binary agent/patient to the 22-29% unreachable "
        "roles): this cell's two-lever fix is a partial, isolated-task-only step in that direction. Next "
        "test: repower this exact isolated 4-way task's canonical slice with a HELD-OUT split disjoint from "
        "whatever tuned the margin/gate thresholds (thresh=0.6, margin_thresh=0.3 were grid-selected on this "
        "same 330-item canonical pool per grid_summary -- check for threshold-selection leakage before "
        "citing the 0.658 number as out-of-sample); if that holds, the natural next step is adding canonical-"
        "active-voice gold to STAGE-1's TRAINING distribution (not just re-tuning inference-time gates) so "
        "the end-to-end wire test (29612's successor) has a chance to actually move."),
    "primitive_assessment": ("Confirms a real, narrow construction-competency refinement (clause-scoped "
        "agent assignment + confidence-gated graceful degrade) that measurably shifts an isolated "
        "canonical-kind benchmark without breaking marked-construction performance. Does not constitute a "
        "new general-purpose extraction primitive; the underlying STAGE-1 classifier architecture is "
        "unchanged from 29606/29608, only its clause-segmentation and gate-thresholding logic is refined."),
    "hf_attribution": "n/a (not a negative in isolation; paired with 29612's negative for the end-to-end claim).",
    "fairness_verdict": ("PARTIALLY VERIFIABLE: arms share a consistent held-out test set (role_n/full_n "
        "identical across arms) and the RANDOM/POSITION controls behave as expected (calibration sanity + "
        "inversion signature), so the isolated-task comparison is fair on its face. However, the grid_summary "
        "shows thresh/margin_thresh were SELECTED via a grid search over this same 330-canonical-item pool -- "
        "the auditor could not confirm from this metrics.json alone whether the reported 0.658 canonical "
        "number is measured on a split disjoint from the grid-selection split or the same pool (possible "
        "mild threshold-selection optimism); flagged in revival_criteria, not treated as disqualifying."),
    "cross_arc_overlap": ("bash tools/substrate_query.sh 'clause-level agent subject margin gated graceful "
        "degrade canonical role extraction commit revise' -> top hit cosine=0.2871 (a distinct clause-seg/"
        "composition atom, subject-recovery not role-extraction-gate). NOVEL, no dedup concern. AMENDS 29610 "
        "(does not compose/build-on; refines its characterization)."),
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom1))

# =====================================================================================================
# ATOM 29612 -- MATH: wire_extraction_accumulate_wm_oracle_vs_real_v4 -- HARD_FAIL. cert_delta 0.
# =====================================================================================================
AID2 = ("math::wire_extraction_accumulate_wm_oracle_vs_real_v4_HARD_FAIL_the_two_lever_extraction_fix_"
    "from_29611_wired_end_to_end_onto_the_SAME_diverse_real_McGuffey_per_entity_gold_used_for_v1_v2_v3_"
    "does_NOT_beat_the_simpler_one_lever_v1_v3_baseline_real_0p4208_vs_0p4333_delta_minus_0p0125_misses_"
    "V3_MUST_BEAT_MARGIN_0p03_remains_well_below_REAL_HARD_PASS_MIN_0p5_oracle_reproduces_1p000_WM_organ_"
    "still_validated_given_correct_roles_floor_at_chance_0p183_can_fail_gates_hold_so_this_is_a_trusted_"
    "negative_CONFIRMS_29610s_extraction_generalization_wall_STANDS_despite_a_genuine_targeted_repair_"
    "attempt_independently_RE_DERIVED_by_hand_averaging_per_entity_dump_not_trusted_from_summary_LOCAL_ONLY")
assert AID2 not in existing_ids
HEAD2 = ("HARD_FAIL (honest negative, CERT +0; the cell's OWN verdict is already correctly framed as a "
    "negative -- HARD_FAIL_V4_DID_NOT_BEAT_V3_SAME_GOLD -- this atom independently confirms it, not merely "
    "restates it). This is the direct end-to-end follow-up test of the exact STAGE-1 extraction model "
    "atomized in 29611: wiring it into the validated accumulate-register WM organ (atom 29609) and running "
    "against the SAME diverse real multiclause McGuffey per-entity gold used to test the v1/v2/v3 STAGE-1 "
    "variants. RESULT: real_multi_event_recall=0.4208 does NOT beat the simpler one-lever v1/v3 baseline "
    "(0.4333, delta -0.0125), missing the pre-registered V3_MUST_BEAT_MARGIN=0.03 and remaining well below "
    "REAL_HARD_PASS_MIN=0.5. Oracle (gold roles fed to WM) reproduces 1.0000 exactly (WM organ remains "
    "validated given correct input) and the floor sits at chance (0.183), so the can-fail gates hold and "
    "this negative is trustworthy, not a broken harness. THE LOAD-BEARING TAKEAWAY: a genuine, targeted "
    "repair attempt at the extraction-generalization component of 29610's wall (clause-level agent + "
    "confidence-gated graceful degrade, atom 29611) does NOT propagate to end-to-end improvement and "
    "slightly regresses -- 29610's wall STANDS, reinforced rather than resolved. Role-inventory coverage "
    "gap independently reconfirmed at 29.3% (17/58 role-events unreachable by a binary agent/patient "
    "extractor), consistent with 29610's 22.2% on a smaller gold set (both wall components -- "
    "generalization AND coverage -- remain open).")
atom2 = {
    "atom_id": AID2, "seq": 29612, "op": "atomize", "corpus": "math",
    "tier": "HARD_FAIL", "cert_status": "honest-negative",
    "grade": "HF_extraction_repair_attempt_does_not_propagate_end_to_end_reinforces_29610_wall",
    "verdict": "HARD_FAIL_V4_DID_NOT_BEAT_V3_SAME_GOLD",
    "anchor": "wire_extraction_accumulate_wm_oracle_vs_real_v4",
    "anchor_name": "wire_extraction_accumulate_wm_oracle_vs_real_v4",
    "cell": "experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v4.py",
    "cell_commit": "9abc82cd2", "cell_content_sha256_16": cellv4_sha,
    "metrics_path": "data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v4/metrics.json",
    "metrics_sha256_16": v4_sha,
    "headline": HEAD2,
    "key_metrics": {
        "cell_verdict": "HARD_FAIL_V4_DID_NOT_BEAT_V3_SAME_GOLD", "auditor_tier": "HARD_FAIL", "cert_delta": 0,
        "oracle_multi": 1.0, "real_multi_v4": 0.4208333333333333, "real_multi_v1_v3": 0.4333333333333333,
        "floor_multi": 0.18333333333333332, "delta_v4_minus_v1": -0.012500000000000011,
        "v3_must_beat_margin": 0.03, "real_hard_pass_min": 0.5,
        "unreachable_events": 17, "total_events": 58, "unreachable_fraction": 0.29310344827586204,
        "recomputed_by_hand_real_multi": recomputed_real, "recomputed_by_hand_commit_v1_multi": recomputed_commit_v1,
        "recomputed_by_hand_oracle_multi": recomputed_oracle,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv recompute off metrics.json per_entity_dump (NOT verdict_msg "
        "or summary alone): independently RE-DERIVED real_multi_event_recall by hand-averaging the 20 "
        "multi_event=true entities' 'real' per-entity recalls from raw per_entity_dump rows (excluding the 3 "
        "single-event entities), obtaining 0.420833... which matches the reported summary value to 9 decimal "
        "places. Same by-hand recompute for the real_commit_revise_v1 arm (0.433333...) and oracle arm "
        "(1.000000), both matching exactly. role_census cross-checked: agent(32)+patient(9)=41 reachable of "
        "58 total events, unreachable=17/58=0.2931, matching the reported unreachable_fraction exactly. "
        "Confirmed both this cell and 29611's cell land under the SAME git commit (9abc82cd296ffb664db1996"
        "ac35e464dc2fb0146, verified via git show --stat) with this cell's ts_iso (15:55:24Z) 3m4s after "
        "29611's cell (15:52:20Z) -- confirming this is the immediate, intentional end-to-end follow-up "
        "test of the exact 29611 model, not a stale or unrelated comparison."),
    "composes_seq": [29609], "corrects_seq": [], "amends_seq": [29610, 29611],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("Genuine structural negative, not a test-design failure: oracle reproduces its own bar "
        "(1.0000) confirming the WM organ and harness wiring are correct; floor sits at chance; the "
        "comparison arms (v1/v2/v3/v4 STAGE-1 variants) are all evaluated on the identical gold set (per-"
        "entity dump reg_digest matches across the v1-family arms). HF_STRUCTURAL_BOUND: the specific "
        "extraction-generalization repair attempt genuinely does not transfer to this harder, more diverse "
        "end-to-end evaluation; this is not a bug in the wire cell."),
    "framing_correction": ("The cell's own verdict (HARD_FAIL_V4_DID_NOT_BEAT_V3_SAME_GOLD) and the commit "
        "message (\"the extraction-layer HARD_PASS did not propagate to a measurable end-to-end lift... "
        "honestly reported as a negative/flat result rather than claimed as a win\") are ALREADY correctly "
        "and honestly scoped -- no correction needed to the cell author's own framing. The correction this "
        "atom applies is to the LEDGER-LEVEL narrative: this result, taken together with 29611, means the "
        "Director's WHERE-banner claim that the 29610 wall is 'broken at the mechanism level' for agent/"
        "patient extraction is not supported by the immediately-following end-to-end measurement, and should "
        "be read as 'a targeted repair attempt did not resolve the wall' rather than 'wall resolved, only "
        "coverage remains.'"),
    "revival_criteria": ("Same as 29610's original revival_criteria (construction-conditional multi-role "
        "extraction trained on canonical-active gold alongside quotative/by-agent, not just inference-time "
        "gate re-tuning; extend beyond binary agent/patient to cover theme/recipient/possessor/experiencer). "
        "This atom adds one refinement: inference-time-only fixes (clause segmentation + confidence gating, "
        "as attempted in 29611) are now empirically shown NOT sufficient on their own -- the fix needs to "
        "touch STAGE-1's TRAINING distribution, not just its decision rule, before re-testing this exact "
        "wire cell."),
    "primitive_assessment": ("No new primitive; this is a diagnostic wire-up re-confirming 29609's WM organ "
        "(oracle=1.0000, composes_seq=[29609]) while re-localizing the bottleneck to extraction "
        "generalization -- now with direct evidence that a specific, reasonable repair attempt (29611) does "
        "not resolve it."),
    "hf_attribution": "HF_STRUCTURAL_BOUND (oracle positive control cleared its own bar; floor at chance; "
        "not a broken test).",
    "fairness_verdict": ("FAIR: all STAGE-1 variants (v1/v2/v3/v4) evaluated against the identical real gold "
        "set in this same cell run (same per_entity keys, same n_events per entity across arms), oracle and "
        "floor controls both behave as expected, and the V3_MUST_BEAT_MARGIN=0.03 discriminator was "
        "presumably pre-registered as a real bar rather than tuned post-hoc to force a negative (consistent "
        "with the honest commit-message framing)."),
    "cross_arc_overlap": ("Direct end-to-end follow-up of 29611/29610/29609; no unrelated prior-arc overlap "
        "(same substrate_query check as 29611 covers this construction). Composes atom 29609 (WM organ, "
        "oracle reproduction) via composes_seq; amends atoms 29610 (wall characterization, reinforced) and "
        "29611 (scopes its isolated-task win as non-propagating) via amends_seq."),
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom2))

# =====================================================================================================
# WRITE: both atoms -> math (in seq order). Then 2 ledger entries.
# =====================================================================================================
math_after1 = A5_write(ATOMS_MATH, math_lines, atom1, "MEASURED_MECHANISM")
math_after2 = A5_write(ATOMS_MATH, [json.dumps(o, ensure_ascii=False) for o in math_after1], atom2, "HARD_FAIL")
assert math_after2[-1]["seq"] == 29612 and math_after2[-2]["seq"] == 29611
print(f"MATH ATOMS OK: {len(math_lines)} -> {len(math_after2)}; seqs 29611 (MM, amends 29610, +0) & "
      f"29612 (HARD_FAIL, amends 29610/29611, +0).")

# ---- LEDGER (2 entries) ----
ledger_now = ledger_lines
for atom, decision in [
    (atom1, "MEASURED_MECHANISM CERT +0 (DEFLATED from cell HARD_PASS; amends 29610, does not retract). "
             "Recompute off metrics.json confirms EXACTLY: canonical V2=0.658 > POSITION floor=0.536; "
             "quotative=0.754 (thin margin over 0.75 bar); byagent=0.787; gate_fp 0.212->0.142; no-revise "
             "ablation reproduces marked-construction inversion. Aggregate-consistency + calibration-sanity "
             "verified (no raw per-prediction dump exists to fully bit-for-bit recompute, capping tier below "
             "chain-grade). CLAUSE_POSITION-alone beats the combo on canonical in isolation (0.673 vs 0.658) "
             "but collapses on byagent (0.149) -- honest tradeoff, not a strict Pareto win. Real load-bearing "
             "correction: this is an isolated-pooled-task win, NOT proof the 29610 wall is broken -- see "
             "29612, the direct end-to-end test of this exact model, which shows no propagation."),
    (atom2, "HARD_FAIL CERT +0 (honest negative, confirms cell's own correctly-framed verdict). Recompute "
             "off per_entity_dump: independently RE-DERIVED (not trusted from summary) real_multi_event_"
             "recall=0.4208 (n=20 by-hand average matches exactly), oracle=1.0000, commit_revise_v1=0.4333. "
             "v4 (the 29611 two-lever model wired end-to-end) does NOT beat v1/v3 (delta -0.0125, misses "
             "V3_MUST_BEAT_MARGIN=0.03), remains well below REAL_HARD_PASS_MIN=0.5. Confirmed both cells "
             "land under the same commit 9abc82cd2, v4 landing 3m4s after v2 (direct intentional follow-up, "
             "not stale). CONFIRMS 29610's extraction-generalization wall STANDS despite a genuine repair "
             "attempt; reinforces rather than resolves it. HF_STRUCTURAL_BOUND (oracle + floor controls "
             "clean, not a broken test)."),
]:
    led = dict(atom)
    led["decision"] = decision
    led["note"] = ("AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off metrics.json per_arm/"
                   "per_entity_dump/summary/bands, NOT verdict_msg or Director/spawn-prompt summary. "
                   "2026-08-02 batch (2 atoms, store head 29610). LOCAL-ONLY; no origin push; no remote "
                   "persist.")
    json.loads(json.dumps(led))
    line = json.dumps(led, ensure_ascii=False)
    assert "\r" not in line and "\n" not in line
    ledger_now = ledger_now + [line]

new_led = "\n".join(ledger_now) + "\n"
dl = os.path.dirname(os.path.abspath(LEDGER))
fd2, tmp2 = tempfile.mkstemp(dir=dl, suffix=".tmp"); os.close(fd2)
with open(tmp2, "w", encoding="utf-8", newline="") as f:
    f.write(new_led); f.flush(); os.fsync(f.fileno())
os.replace(tmp2, LEDGER)
assert b"\r\n" not in open(LEDGER, "rb").read(), "CRLF doubling in ledger"
vl = [json.loads(l) for l in open(LEDGER, encoding="utf-8").read().splitlines() if l.strip()]
assert len(vl) == len(ledger_lines) + 2
assert [iseq(x) for x in vl[-2:]] == [29611, 29612]
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seqs 29611/29612.")
print("DONE. net_cert_delta = +0 (both amend prior atoms; no new/lost cert -- isolated-task win paired "
      "honestly with its own end-to-end non-propagation). LOCAL-ONLY; no origin push; no remote persist.")
