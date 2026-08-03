"""
A5-gated atomization: coherence-margin-cannot-discriminate-satisfy-restate falsification
pilot (MEASURED_MECHANISM, honest negative). AUDIT-ONLY (hdi_skunkworks).

Independent recompute off data/exp_goal_state_satisfy_restate_falsification_pilot_v1/
metrics.json's raw result.per_case / coherence_margin_mechanism blocks (NOT off
verdict_msg/summary alone), plus a fresh independent run of the cell's own --self-test
mode to confirm mechanism determinism + candidate-blindness empirically (not merely
citing the file's own claim).

Writes ONE atom (seq 29642, math corpus) + 1 matching cert_ledger.jsonl entry,
atomically (tmp -> os.replace), then verify-loads both files and runs an integrity
check. LOCAL-ONLY: no origin push, no remote persist.
"""
import json
import os
import time
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATH_ATOMS_PATH = os.path.join(REPO, "data", "substrate_index", "math", "atoms.jsonl")
LEDGER_PATH = os.path.join(REPO, "data", "substrate_index", "meta", "cert_ledger.jsonl")

SEQ_COHERENCE_MARGIN_FALSIFICATION = 29642

ATOM_COHERENCE_MARGIN_FALSIFICATION = {
    "atom_id": (
        "math::goal_state_satisfy_restate_coherence_margin_falsification_pilot_v1_"
        "candidate_text_blind_by_construction_0of3_proven_not_measured_content_overlap_"
        "baseline_1of3_random_1of3_root_cause_accumulateregister_bindbundlecleanupargmax_"
        "sensitive_only_to_structural_collision_never_literal_content_idxvecs_rolevecs_"
        "content_agnostic_random_unit_phase_vectors_falsifies_earned_inference_design_"
        "section2_forka_minimal_transplant_NOT_the_deeper_kintsch_ci_idea_honest_fix_needs_"
        "margin_wired_to_real_relational_content_causallinkregister_atom29636_182links_"
        "de_risks_bigger_build_before_investment_8de52617f_MEASURED_MECHANISM_LOCAL_ONLY"
    ),
    "seq": SEQ_COHERENCE_MARGIN_FALSIFICATION,
    "op": "insert",
    "corpus": "math",
    "tier": "MEASURED_MECHANISM",
    "cert_status": "MEASURED_MECHANISM",
    "grade": "MM",
    "verdict": (
        "GENUINE MECHANISM-LEVEL NEGATIVE, CONFIRMED BY CONSTRUCTION AND INDEPENDENTLY "
        "RE-VERIFIED, NOT MERELY CITED FROM THE FILE'S OWN VERDICT. The design doc (notes/"
        "earned_semantic_relation_inference_design_2026-08-03.md, commit 4c8a26aed) Section 2 "
        "/ Fork (a) proposed reusing the validated situation-model coherence-margin "
        "(hdlab.self_improving_loop.decode_coherence_margins organ, atom 29609/HARD_PASS, "
        "AUC=0.917 in the coref-autonomy arc) as a SATISFY-vs-RESTATE discriminator for goal-"
        "state relation inference, via a counterfactual-write recipe: bind a candidate close-"
        "event under a NEW role (CLOSE, a genuine transition) vs bind it under the SAME role "
        "as the goal-open event (OPEN, a restatement), then compare the OPEN role's own decode "
        "margin. Independent re-run of the cell's own self-test mode this pass (.venv python "
        "experiments/exp_goal_state_satisfy_restate_falsification_pilot_v1.py --self-test) "
        "reproduces exactly: mech_a==mech_b bit-identical across two independent calls with the "
        "same seed, and confirms the mechanism function coherence_mechanism_score(case_seed) "
        "takes NO candidate-text argument at all -- it is architecturally incapable of reading "
        "which hypothesis's text is under test. Independent recompute of the raw metrics.json "
        "per_case block (3 real hand-verified gold cases: anne_goal_001/002/012 -> anne_"
        "causal_016/016/001) confirms each case's coherence_margin_mechanism.delta_close_minus_"
        "repeat is a SINGLE VALUE used for both the satisfy and restate candidate by "
        "construction (mech_outputs_identical_across_cases_sanity computed per-case, not "
        "assumed) -- the margin genuinely never receives candidate text. ROOT-CAUSE DERIVATION "
        "(verified, not merely asserted): AccumulateRegister's bind/bundle/cleanup-argmax "
        "primitives (hdlab/situation_model_accumulate.py) are sensitive ONLY to STRUCTURAL "
        "COLLISION PATTERNS (how many facts compete for the same bound key) -- idx_vecs and "
        "role_vecs are content-agnostic random unit-phase vectors, so the register cannot "
        "distinguish 'Mrs. Lynde agreed to add puffed sleeves' from any other candidate string; "
        "it only knows whether a write collided with a prior binding under the same role-key. "
        "This is the exact mechanism-class that worked for COREFERENCE (structural identity: "
        "which cluster/slot a mention binds to) and is provably the WRONG signal-class for "
        "relation-CONTENT inference (satisfy/thwart/cause requires discriminating what the "
        "candidate text SAYS, not which structural slot it occupies). RESULT: coherence_margin_"
        "discriminates_satisfy_over_restate=False, 0/3 by construction (not merely measured 0/3 "
        "-- the distinction matters: a construction-level impossibility, not a sampling miss). "
        "Content-overlap baseline (freshly recomputed on these exact 3 spans, not reused from "
        "atom 29634/29639's larger set) ranks satisfy>restate on 1/3 -- mixed, not a clean win "
        "for overlap either on this N=3 slice, so this pilot does not accidentally validate "
        "overlap as the alternative; it only falsifies the coherence-margin transplant."
    ),
    "anchor": "goal_state_satisfy_restate_falsification_pilot_v1",
    "anchor_name": "goal_state_satisfy_restate_falsification_pilot_v1_2026_08_03",
    "cell": (
        "experiments/exp_goal_state_satisfy_restate_falsification_pilot_v1.py; "
        "data/exp_goal_state_satisfy_restate_falsification_pilot_v1/metrics.json; "
        "commit 8de52617f; design doc notes/earned_semantic_relation_inference_design_"
        "2026-08-03.md, commit 4c8a26aed"
    ),
    "headline": (
        "N=3 falsification pilot (director-verified real gold: anne_goal_001/002/012 -> their "
        "true resolving events) on the cheapest fork of the earned-semantic-relation-inference "
        "design's most novel claim: FALSIFIED_FOR_THIS_OPERATIONALIZATION, 0/3 BY CONSTRUCTION. "
        "The validated coherence-margin organ (atom 29609, AUC=0.917 for coreference routing) "
        "never receives candidate text -- AccumulateRegister bind/bundle/cleanup-argmax is "
        "sensitive only to structural collision, never literal content (idx_vecs/role_vecs are "
        "content-agnostic random unit-phase vectors) -- so it architecturally cannot rank a "
        "true satisfy-event above a true restate-distractor. This is a mechanism-CLASS insight, "
        "not a tuning failure: coherence-margin = structural-identity signal (right for coref), "
        "wrong signal-class for relation-CONTENT inference (needs to discriminate what text "
        "SAYS). Falsifies the SPECIFIC minimal transplant (margin-toggle on an otherwise-empty "
        "register), NOT the deeper Kintsch-CI coherence/prediction-error idea (Section 1) -- "
        "the honest fix is wiring the margin to REAL relational content (e.g. the already-"
        "populated CausalLinkRegister, atom 29636, 182 real proposed links), which is a "
        "materially bigger build than this pilot, not a parameter tweak. De-risked a cheap-"
        "transplant investment before it was scaled."
    ),
    "key_metrics": {
        "n_cases": 3,
        "coherence_margin_discriminates_satisfy_over_restate": False,
        "n_correct_coherence_margin": 0,
        "coherence_margin_candidate_blind_by_construction": True,
        "n_overlap_ranks_satisfy_correct": 1,
        "n_agent_shift_ranks_correct": 1,
        "n_random_ranks_satisfy_correct": 1,
        "mech_outputs_identical_across_cases_sanity": False,
        "self_test_mechanism_deterministic": True,
        "self_test_mechanism_candidate_blind_confirmed": True,
        "arms_differ_verified": False,
        "arms_differ_exempted_reason": "mechanism takes no candidate-text argument by design",
    },
    "auditor": "hdi_skunkworks",
    "verified_off_data": True,
    "verified_off_data_note": (
        "Independent Python read of data/exp_goal_state_satisfy_restate_falsification_pilot_v1/"
        "metrics.json's raw result.per_case block (not verdict_msg/summary alone): all 3 cases' "
        "coherence_margin_mechanism.delta_close_minus_repeat values reproduce exactly against "
        "the file (0.5162235796451569, 0.5737628489732742, 0.5918500684201717); overlap_satisfy/"
        "overlap_restate per case reproduce exactly (n_overlap_ranks_satisfy_correct=1/3, case "
        "anne_goal_012_causal_001 only); n_agent_shift_ranks_correct=1/3 and "
        "n_random_ranks_satisfy_correct=1/3 both reproduce exactly. INDEPENDENTLY RE-RAN the "
        "cell's own --self-test mode this pass (.venv/Scripts/python.exe experiments/exp_goal_"
        "state_satisfy_restate_falsification_pilot_v1.py --self-test) rather than trusting the "
        "file's self_test_passed=True claim -- fresh run confirms self_test_mechanism_"
        "deterministic=True (mech_a==mech_b bit-identical across two independent calls with "
        "seed=20260803) and self_test_mechanism_candidate_blind_confirmed=True. Read the cell's "
        "source (experiments/exp_goal_state_satisfy_restate_falsification_pilot_v1.py, function "
        "coherence_mechanism_score) directly: confirmed its signature takes only case_seed, no "
        "candidate-text parameter -- the candidate-blindness is a verifiable property of the "
        "function's argument list, not an inference from output identity alone. Read hdlab/"
        "situation_model_accumulate.py's AccumulateRegister to confirm idx_vecs/role_vecs are "
        "generator-seeded random unit-phase vectors (content-agnostic), supporting the root-"
        "cause derivation rather than taking the cell's own docstring claim at face value. "
        "Cross-checked git log: commit 8de52617f (this cell) and 4c8a26aed (the design doc it "
        "falsifies a fork of) both confirmed present in repo history."
    ),
    "composes_seq": [29609, 29636, 29639, 29640],
    "corrects_seq": [],
    "amends_seq": [],
    "cert_delta": 0,
    "net_cert_delta": 0,
    "store_head_at_write": SEQ_COHERENCE_MARGIN_FALSIFICATION - 1,
    "honest_scope": (
        "N=3 hand-picked director-verified cases -- explicitly a falsification SMOKE, not a "
        "powered study; the file's own docstring and verdict_msg say this repeatedly and this "
        "atom does not upgrade that caveat. The 0/3 coherence-margin result is a CONSTRUCTION-"
        "level impossibility (proven via the function's own signature + bit-identical outputs), "
        "so N=3 is sufficient to falsify THIS SPECIFIC operationalization even though N=3 would "
        "be underpowered for a probabilistic claim -- the two claims (mechanism-class "
        "impossibility vs a numeric win-rate) require different N; this atom only banks the "
        "former. content-overlap baseline (1/3) and random floor (1/3) are NOT claimed as clean "
        "wins or clean losses on this N=3 slice -- reported as mixed/uninformative at this N, "
        "not as validating overlap as the fix. The scope explicitly does NOT extend to falsifying "
        "the deeper Kintsch-CI coherence/prediction-error idea (design doc Section 1) -- only "
        "the minimal margin-toggle-on-empty-register transplant (Section 2, fork a)."
    ),
    "framing_correction": (
        "None needed against the cell's own verdict_msg/summary -- independent recompute + a "
        "fresh self-test re-run both confirm the cell's claims exactly, including its own honest "
        "caveats (mixed overlap result, N=3 caution, scope limited to 'this operationalization'). "
        "One clarification added by this audit: the cell's summary describes the result as "
        "'0/3, proven not just measured' -- this atom explicitly separates that construction-"
        "level proof (verified independently via the function signature + generator-seeded "
        "bit-identical rerun, not merely restated) from the SEPARATE, genuinely-measured-not-"
        "provable numbers (overlap 1/3, agent-shift 1/3, random 1/3), which are ordinary small-N "
        "measurements and should not be read with the same certainty as the construction-level "
        "claim."
    ),
    "revival_criteria": (
        "Wire the coherence-margin computation to REAL relational content instead of an "
        "arbitrary per-candidate hypothesis-role toggle on an otherwise-empty register -- "
        "concretely, populate an AccumulateRegister-family organ (e.g. extend the existing "
        "CausalLinkRegister, atom 29636, already holding 182 real proposed causal links) so "
        "that a candidate event's actual extracted content (not just its assigned role) enters "
        "the bound key or the collision pattern, then re-test whether the resulting margin can "
        "rank true-satisfy above true-restate on the same 3 (or an expanded) gold set. This is "
        "materially bigger than a pilot -- a real content-population build, not a parameter "
        "retune -- and should itself go through a fresh design gate (can-fail discriminator, "
        "real baseline) before a full build, per the standing design-gate discipline."
    ),
    "primitive_assessment": (
        "No new primitive; this atom is a NEGATIVE mechanism-class finding about an EXISTING "
        "organ (AccumulateRegister, atom 29609). Reusable methodology worth banking generally: "
        "before transplanting a validated mechanism from one task to an adjacent one, check "
        "whether the mechanism's SIGNAL CLASS matches the new task's discrimination requirement "
        "-- a mechanism validated for STRUCTURAL-IDENTITY discrimination (which slot/cluster; "
        "coreference routing) is not automatically valid for CONTENT discrimination (what a "
        "candidate's text says; satisfy/thwart/cause relation typing), even when both live on "
        "the same organ and the same validated AUC number is cited. This generalizes beyond this "
        "specific cell: any bind/bundle/cleanup-argmax VSA organ built on content-agnostic random "
        "vectors is, by construction, blind to literal content unless content is explicitly "
        "encoded into what gets bound (not just which role it's bound under)."
    ),
    "hf_attribution": "n/a (MEASURED_MECHANISM tier: a proven mechanism-class boundary, not a HARD_FAIL test-design failure -- the positive-control-equivalent here is the self-test, which itself correctly demonstrates the candidate-blindness rather than failing to run).",
    "fairness_verdict": (
        "FAIR: every cited number reproduces exactly off the raw per_case block, and the "
        "construction-level claim (candidate-blindness) was independently re-verified via a "
        "fresh self-test rerun and direct source inspection, not merely cited from the file's "
        "own verdict. Symmetric anti-negativity: this is an honest downward-consistent negative "
        "(no inflation of the falsification into a stronger claim against the deeper Kintsch-CI "
        "idea than the evidence supports; no deflation either -- the mechanism-class insight is "
        "banked as a genuine, generalizable finding, not dismissed as 'just N=3 noise'). This "
        "negative is explicitly load-bearing: it de-risked further investment in the cheap fork "
        "(a) transplant before it was scaled to a larger build."
    ),
    "cross_arc_overlap": (
        "substrate_query.sh check ('coherence margin candidate content blind satisfy restate "
        "discrimination relation inference') returns top hits at cosine<=0.4023, all either the "
        "design doc's own chunk (notes/research_decisions_2026-07-14.md, generic cold-start/"
        "relational-inference framing, no specific overlap with this falsification), the "
        "gated_fusion_relation_inference capability-registry entry (a different, already-WIRED "
        "capability, no duplicate), or prior situation-model/coherence-gate design notes (07-21, "
        "generic architecture description predating this specific falsification test). No prior "
        "experiment-cell result duplicates this specific coherence-margin-vs-relation-content "
        "falsification. Composes directly with 29609 (the AccumulateRegister organ under test), "
        "29636 (the CausalLinkRegister/182-links organ named as the honest-fix revival path), "
        "and 29639/29640 (the goal-close-pairing arc + frontier synthesis that identified satisfy-"
        "vs-restate discrimination as the named residual this pilot then tested)."
    ),
    "needs_orchestrator_store_sync": True,
    "local_write_only_no_origin_push_no_remote_persist": True,
}


def atomic_append_jsonl(path, record):
    line = json.dumps(record, ensure_ascii=True) + "\n"
    dir_ = os.path.dirname(path)
    with open(path, "rb") as f:
        existing = f.read()
    fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as tmp:
            tmp.write(existing)
            tmp.write(line.encode("utf-8"))
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def verify_load(path, expect_seq=None, expect_atom_id=None):
    found = False
    count = 0
    with open(path, "rb") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            count += 1
            d = json.loads(raw.decode("utf-8"))
            if expect_seq is not None and d.get("seq") == expect_seq:
                found = True
            if expect_atom_id is not None and d.get("atom_id") == expect_atom_id:
                found = True
    return found, count


def make_ledger_entry(seq, atom, corpus, decision, note):
    now = time.time()
    return {
        "seq": seq,
        "atom_id": atom["atom_id"],
        "corpus": corpus,
        "decision": decision,
        "note": note,
        "needs_orchestrator_store_sync": True,
        "local_write_only_no_origin_push_no_remote_persist": True,
        "ts": now,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now)),
        "ts_day": time.strftime("%Y-%m-%d", time.gmtime(now)),
    }


def main():
    now = time.time()
    ts_iso = time.strftime("%Y-%m-%dT%H:%M:%S.000000+00:00", time.gmtime(now))
    ts_day = time.strftime("%Y-%m-%d", time.gmtime(now))

    ATOM_COHERENCE_MARGIN_FALSIFICATION["ts"] = now
    ATOM_COHERENCE_MARGIN_FALSIFICATION["ts_iso"] = ts_iso
    ATOM_COHERENCE_MARGIN_FALSIFICATION["ts_day"] = ts_day

    ledger_entry = make_ledger_entry(
        SEQ_COHERENCE_MARGIN_FALSIFICATION, ATOM_COHERENCE_MARGIN_FALSIFICATION, "math",
        "MEASURED_MECHANISM CERT +0 (coherence-margin-cannot-discriminate-satisfy-restate "
        "falsification pilot). Independent recompute off raw result.per_case block reproduces "
        "exactly (0/3 by construction, overlap 1/3, agent-shift 1/3, random 1/3); INDEPENDENTLY "
        "RE-RAN the cell's --self-test mode this pass (fresh, not cited from file) confirming "
        "mechanism determinism + candidate-blindness; confirmed via direct source read that "
        "coherence_mechanism_score() takes no candidate-text argument. Genuine mechanism-class "
        "negative: coherence-margin (structural-identity signal, right for coreference) is the "
        "WRONG signal-class for relation-CONTENT inference (satisfy/thwart/cause). Falsifies the "
        "SPECIFIC minimal transplant (fork a, Section 2 of the design doc), NOT the deeper "
        "Kintsch-CI idea (Section 1). De-risked the cheap-transplant investment before scaling.",
        "AUDIT-ONLY (hdi_skunkworks) independent recompute off data/exp_goal_state_satisfy_"
        "restate_falsification_pilot_v1/metrics.json, NOT off verdict_msg alone; plus a fresh "
        "independent self-test rerun and direct source inspection of coherence_mechanism_score() "
        "and AccumulateRegister. Commit 8de52617f (cell), 4c8a26aed (design doc). LOCAL-ONLY.",
    )

    atomic_append_jsonl(MATH_ATOMS_PATH, ATOM_COHERENCE_MARGIN_FALSIFICATION)
    atomic_append_jsonl(LEDGER_PATH, ledger_entry)

    found, count = verify_load(
        MATH_ATOMS_PATH,
        expect_seq=SEQ_COHERENCE_MARGIN_FALSIFICATION,
        expect_atom_id=ATOM_COHERENCE_MARGIN_FALSIFICATION["atom_id"],
    )
    assert found, f"FAIL: atom seq={SEQ_COHERENCE_MARGIN_FALSIFICATION} not found in {MATH_ATOMS_PATH} after write"

    found_ledger, ledger_count = verify_load(LEDGER_PATH, expect_seq=SEQ_COHERENCE_MARGIN_FALSIFICATION)
    assert found_ledger, f"FAIL: ledger entry seq={SEQ_COHERENCE_MARGIN_FALSIFICATION} not found in {LEDGER_PATH} after write"

    print(f"OK: atom seq={SEQ_COHERENCE_MARGIN_FALSIFICATION} written to {MATH_ATOMS_PATH} ({count} total lines)")
    print(f"OK: ledger entry written to {LEDGER_PATH} ({ledger_count} total lines)")
    print("atom_id:")
    print(f"  seq={ATOM_COHERENCE_MARGIN_FALSIFICATION['seq']} corpus={ATOM_COHERENCE_MARGIN_FALSIFICATION['corpus']} -> {ATOM_COHERENCE_MARGIN_FALSIFICATION['atom_id'][:120]}...")


if __name__ == "__main__":
    main()
