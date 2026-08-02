"""A5-gated LOCAL-ONLY atomize of two independently-VET'd 2026-08-02 landings + one CERT-neutral
META synthesis. AUDIT-ONLY (hdi_skunkworks). Independent .venv recompute off raw metrics.json on
disk (NOT verdict_msg strings, NOT the Director/spawn-prompt summary). No experiment authored/
dispatched by auditor -- role separation preserved.

Cross-arc overlap check (substrate_query.sh):
  "Binding Principle B disjoint reference same-clause agent exclusion pronoun coreference"
    -> top hit cosine=0.3779 (generic concept node 'coreference'/'reference'), NONE >0.30 is a prior
       EXPERIMENT CELL on this exact mechanism. Novel.
  "verb selectional preference discourse coherence probe ceiling flagged pronoun errors"
    -> top hit cosine=0.3398 (FrameNet 'Preference' concept node + an UNRELATED HARD_FAIL/CELL_CRASHED
       selectional-preference cell from 07-17, different mechanism/arc). Novel.

THREE atoms, store head 29619 -> seqs 29620 (math, probe finding-1), 29621 (math, fix finding-2),
29622 (meta, CERT-neutral loop-engine synthesis).

RECOMPUTE PERFORMED:
  Finding-1 (probe): `.venv` load of data/probe_fix_tier_verb_semantic_ceiling_v1_cases.json (17
  raw cases, len() confirmed == 17), cross-checked against the note's own N=17/distribution table.
  This is a HAND-CLASSIFICATION over a small N -- no scored metrics.json exists for it (explicitly a
  diagnosis-only probe per its own text) -- so nothing beyond N and the raw-case-count is independently
  machine-verifiable; the category assignments themselves are judgment calls the note itself flags as
  such (B1 vs B2 boundary uncertain for case 7). Banked as MEASURED_MECHANISM with this scope stated
  explicitly, NOT as a powered/statistical result.

  Finding-2 (fix): independently RE-RAN the full cell (`.venv/Scripts/python.exe
  experiments/exp_coref_flag_fix_loop_principle_b_v1.py`, not just read metrics.json) -- fresh
  execution reproduced the verdict_msg and every headline number bit-for-bit (pronoun-B3 0.7029->
  0.7047, iddem 0.7193->0.7368, g5g6 0.72->0.76, corrected=1/broken=0/net=1, filter action counts
  identical). This is a genuine independent-recompute witness, not a report-read. Self-test
  (--self-test) also independently re-run and PASSed (positive fire + both guards).

DEFLATION CHECK: none needed -- both findings' own writeups already self-deflate correctly (probe:
small-N/hand-classified caveat explicit; fix: PARTIAL_COREF_ONLY not oversold as HARD_PASS, margin
below the pre-registered 0.02 bar stated plainly). No inflation found to correct.
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
assert STORE_HEAD == 29619, f"expected store head 29619, got {STORE_HEAD}"
assert any(iseq(o) == 29619 for o in pm), "parent 29619 (loop cycle1, math) missing"
assert any(iseq(o) == 29614 for o in pm), "parent 29614 (strict_cb, math) missing"
print(f"PRE-GATE OK: store head {STORE_HEAD}; parents 29614/29619 present; new seqs 29620/29621/29622.")

# =====================================================================================================
# OFF-DISK independent verify -- Finding 1: probe raw case count
# =====================================================================================================
cases = json.load(open("data/probe_fix_tier_verb_semantic_ceiling_v1_cases.json", encoding="utf-8"))
assert isinstance(cases, list) and len(cases) == 17
note_sha = sha16("notes/probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_2026-08-02.md")
cases_sha = sha16("data/probe_fix_tier_verb_semantic_ceiling_v1_cases.json")
# hand distribution from the note, cross-checked to sum to 17
dist = {"A_verb_selectional": 1, "B1_cheap_principle_b": 5, "B2_cross_clause": 9, "C_world_knowledge": 2, "D_ambiguous": 0}
assert sum(dist.values()) == 17
print(f"Finding-1 OFF-DISK OK: raw cases file confirmed len=17 (matches note's own n_flagged_wrong_cases=17). "
      f"Distribution A=1 B1=5 B2=9 C=2 D=0 sums to 17. cases_sha={cases_sha} note_sha={note_sha}")

# =====================================================================================================
# OFF-DISK independent recompute -- Finding 2: FRESH RE-RUN of the cell (not just metrics.json read)
# =====================================================================================================
import subprocess, sys
venv_py = os.path.join("d:\\AI\\hd-instrument", ".venv", "Scripts", "python.exe")
proc = subprocess.run([venv_py, "experiments/exp_coref_flag_fix_loop_principle_b_v1.py"],
                       capture_output=True, text=True, cwd="d:\\AI\\hd-instrument", timeout=300)
assert proc.returncode == 0, proc.stderr[-2000:]
assert "PARTIAL_COREF_ONLY" in proc.stdout
F = json.load(open("data/exp_coref_flag_fix_loop_principle_b_v1/metrics.json", encoding="utf-8"))
assert F["verdict"] == "PARTIAL_COREF_ONLY"
hc = F["headline_combined"]
assert abs(hc["pronoun_b3_f1"]["strict_cb"] - 0.7029326700972488) < 1e-9
assert abs(hc["pronoun_b3_f1"]["principle_b"] - 0.7047160370965815) < 1e-9
assert abs(hc["identity_demanding_query_acc"]["strict_cb"] - 0.7192982456140351) < 1e-9
assert abs(hc["identity_demanding_query_acc"]["principle_b"] - 0.7368421052631579) < 1e-9
assert abs(hc["identity_demanding_query_acc"]["oracle"] - 0.9298245614035088) < 1e-9
assert abs(hc["name_regression"] - 0.0007642648717568479) < 1e-6
assert abs(hc["overall_regression"] - 0.0002572426067406486) < 1e-6
cb = F["corrected_broken_combined"]
assert cb["corrected_all"] == 1 and cb["broken_all"] == 0 and cb["net_all"] == 1
assert cb["corrected_flagged"] == 1 and cb["broken_flagged"] == 0
ac = F["combined_powered"]["principle_b_action_counts"]
assert ac == {"abstain_no_same_clause_agent": 25, "abstain_agent_pronoun": 31,
              "abstain_multi_same_clause_agent": 3, "fired": 9, "allocate_new": 6,
              "abstain_no_compat": 1, "abstain_only_option": 1}
g = F["g5g6_only"]
gb3 = g["b3"]
assert abs(gb3["strict_cb"]["pronoun_only"]["f1"] - 0.7217667055293344) < 1e-9
assert abs(gb3["principle_b"]["pronoun_only"]["f1"] - 0.7235207666445213) < 1e-9
gq = g["query_metric"]
assert abs(gq["strict_cb"]["query_accuracy_identity_demanding"] - 0.72) < 1e-9
assert abs(gq["principle_b"]["query_accuracy_identity_demanding"] - 0.76) < 1e-9
assert F["combined_powered"]["n_passages"] == 36 and g["n_passages"] == 18
# self-test independently re-run
proc2 = subprocess.run([venv_py, "experiments/exp_coref_flag_fix_loop_principle_b_v1.py", "--self-test"],
                        capture_output=True, text=True, cwd="d:\\AI\\hd-instrument", timeout=120)
assert proc2.returncode == 0 and "PASS" in proc2.stdout, proc2.stdout + proc2.stderr
cell2_sha = sha16("experiments/exp_coref_flag_fix_loop_principle_b_v1.py")
metrics2_sha = sha16("data/exp_coref_flag_fix_loop_principle_b_v1/metrics.json")
print(f"Finding-2 OFF-DISK OK: FRESH re-execution (not report-read) reproduced verdict PARTIAL_COREF_ONLY "
      f"bit-for-bit: pronoun-B3 {hc['pronoun_b3_f1']['strict_cb']:.4f}->{hc['pronoun_b3_f1']['principle_b']:.4f}, "
      f"iddem {hc['identity_demanding_query_acc']['strict_cb']:.4f}->{hc['identity_demanding_query_acc']['principle_b']:.4f} "
      f"(oracle {hc['identity_demanding_query_acc']['oracle']:.4f}), g5g6 iddem "
      f"{gq['strict_cb']['query_accuracy_identity_demanding']:.2f}->{gq['principle_b']['query_accuracy_identity_demanding']:.2f}, "
      f"corrected={cb['corrected_all']} broken={cb['broken_all']} net={cb['net_all']}, "
      f"36-passage guard breakage=0 confirmed (broken_all==0). self-test independently re-run: PASS. "
      f"cell_sha={cell2_sha} metrics_sha={metrics2_sha}")

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
# ATOM 29620 -- MATH: probe-to-aim ceiling classification (Finding 1)
# =====================================================================================================
AID1 = ("math::probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_v1_N17_hand_classified_REDIRECT_"
    "verb_selectional_preference_5p9pct_1_of_17_far_under_40pct_build_bar_discourse_coherence_82p4pct_"
    "14_of_17_split_B1_cheap_same_clause_principle_b_29p4pct_5_of_17_B2_cross_clause_dialogue_identity_"
    "bridging_52p9pct_9_of_17_world_pragmatic_knowledge_11p8pct_2_of_17_genuinely_ambiguous_0pct_"
    "steered_the_next_build_AWAY_from_a_low_ceiling_verb_semantics_resource_TOWARD_the_cheap_principle_"
    "b_lever_probe_to_aim_methodology_not_a_powered_measurement_LOCAL_ONLY")
assert AID1 not in existing_ids
HEAD1 = ("MEASURED_MECHANISM (CERT +0; a probe-to-aim methodology/diagnosis atom, not a capability grant "
    "-- no cell was dispatched, no code changed). Hand-classifies all N=17 pronoun decisions the powered "
    "coref eval (36 passages/76 pronoun decisions) marks BOTH flagged (n_compatible>=2, atom 29619's own "
    "threshold) AND link-wrong under strict_cb (atom 29614), by what knowledge/mechanism would actually "
    "resolve each: A=verb-selectional-preference/thematic-fit 5.9% (1/17); B=discourse-coherence 82.4% "
    "(14/17), split B1=cheap same-clause Binding-Principle-B exclusion 29.4% (5/17) vs B2=cross-clause "
    "dialogue-turn/identity-bridging 52.9% (9/17); C=world/pragmatic knowledge 11.8% (2/17); D=genuinely "
    "ambiguous 0%. VERDICT: REDIRECT away from building a verb-semantic/richer-animacy resource (5.9% is "
    "far under the pre-registered 40% BUILD bar, and the sole A-case is not even resolved by the existing "
    "animacy_lexicon -- both entities are animate). Correctly identified the actually-cheap lever (B1, "
    "zero new knowledge, same-clause role-collision exclusion) BEFORE it was built, and correctly scoped "
    "the real open frontier (B2, ~53%, cross-clause discourse/identity tracking) as harder future work.")
atom1 = {
    "atom_id": AID1, "seq": 29620, "op": "atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "grade": "MM_probe_to_aim_diagnosis_redirect_verb_semantics_low_ceiling_identifies_principle_b_lever",
    "verdict": "REDIRECT", "anchor": "probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_v1",
    "anchor_name": "probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_v1",
    "cell": "n/a (diagnosis-only probe, no experiment cell)",
    "cell_commit": "b839a317601fdf3ae23ec47d9c2e39dd960f8c26",
    "note_path": "notes/probe_fix_tier_verb_semantic_ceiling_flagged_pronouns_2026-08-02.md",
    "note_sha256_16": note_sha,
    "raw_cases_path": "data/probe_fix_tier_verb_semantic_ceiling_v1_cases.json",
    "raw_cases_sha256_16": cases_sha,
    "headline": HEAD1,
    "key_metrics": {
        "n_cases": 17, "pct_A_verb_selectional": 0.059, "pct_B_discourse_total": 0.824,
        "pct_B1_cheap_principle_b": 0.294, "pct_B2_cross_clause": 0.529,
        "pct_C_world_knowledge": 0.118, "pct_D_ambiguous": 0.0,
        "build_bar_used": 0.40, "cheap_animacy_resolvable_subset_of_A": 0.0,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv load of the raw 17-case JSON file (not a scored "
        "metrics.json -- this is a hand-classification probe, explicitly diagnosis-only per its own "
        "text) confirmed len()==17, matching the note's cited n_flagged_wrong_cases=17. The category "
        "distribution itself (A/B1/B2/C/D counts) is NOT independently machine-recomputed here -- it is "
        "a judgment-call classification the note's own author flags as such (e.g. case 7's B1-vs-B2 "
        "boundary called out as uncertain). This atom is scoped accordingly: banked as a small-N, "
        "hand-classified AIM-PROBE, not a powered/statistical measurement. Distribution sums verified "
        "to exactly 17/17."),
    "composes_seq": [29619], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("Verdict-bearing for: the REDIRECT decision (verb-semantics not worth building, "
        "ceiling ~6%) and for correctly flagging B1 (cheap Principle-B) as the actual next lever BEFORE "
        "atom 29621 built and confirmed it. NOT verdict-bearing as a precise/statistical percentage "
        "breakdown -- N=17 is small and hand-classified; category boundaries (esp B1/B2 and B/C) required "
        "judgment. Treat the specific percentages as directional, not a powered estimate."),
    "framing_correction": ("None needed -- the note itself already states these caveats plainly (small N, "
        "hand classification, uncertain category boundaries flagged inline per-case). No inflation found "
        "in the Director's framing to correct."),
    "revival_criteria": ("If a genuinely richer verb-selectional-preference resource becomes cheaply "
        "available (e.g. a supplied FACT table, not a bolt-on parser) it could still be probed against a "
        "LARGER flagged-error sample (more McGuffey mining) to check whether 5.9% holds at scale before "
        "fully abandoning the direction -- current N=17 is not powered enough to rule it out at scale, "
        "only to deprioritize it now."),
    "primitive_assessment": ("No experimental primitive; validates a reusable METHODOLOGY -- probe-to-aim "
        "(cheap hand-classification of a small error sample against candidate fix mechanisms BEFORE "
        "committing build effort) correctly steered investment toward the cheap lever and away from the "
        "low-ceiling one; atom 29621 (below) confirms the redirect was correct in direction."),
    "hf_attribution": "n/a (methodology/diagnosis atom, not a HF).",
    "fairness_verdict": ("FAIR as a probe: reused the SAME flagged+wrong case set the loop cell (29619) "
        "already defined (n_flagged_wrong_cases=17 reproduced exactly, not cherry-picked), read verbatim "
        "from the strict_cb/match_or_allocate/situation_model source without mutation."),
    "cross_arc_overlap": ("substrate_query.sh 'verb selectional preference discourse coherence probe "
        "ceiling flagged pronoun errors' -> top cosine=0.3398 (FrameNet 'Preference' concept node + an "
        "unrelated 07-17 selectional-preference HARD_FAIL/CELL_CRASHED cell, different mechanism/arc); "
        "none >0.30 is a duplicate of this specific classification. Novel."),
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom1))

# =====================================================================================================
# ATOM 29621 -- MATH: Binding Principle B fix -- PARTIAL_COREF_ONLY, net-positive, guard-safe (Finding 2)
# =====================================================================================================
AID2 = ("math::coref_flag_fix_loop_principle_b_v1_PARTIAL_COREF_ONLY_binding_principle_b_same_clause_"
    "agent_exclusion_pronoun_B3_0p7029_to_0p7047_lift_0p0018_below_0p02_hard_pass_margin_identity_"
    "demanding_query_0p7193_to_0p7368_lift_0p0175_toward_oracle_0p9298_g5g6_0p72_to_0p76_lift_0p04_"
    "name_overall_flat_no_regression_filter_fired_9_of_76_corrected_1_broke_0_net_1_participial_and_"
    "multi_agent_guards_zero_breakage_across_36_passages_glass_box_zero_supplied_knowledge_opt_in_"
    "strict_cb_never_mutated_LOCAL_ONLY")
assert AID2 not in existing_ids
HEAD2 = ("MEASURED_MECHANISM (CERT +0; the fix is real/net-positive/guard-safe grammatical competence but "
    "does not clear the pre-registered HARD_PASS bar, so it is banked as a proven-bound partial gain, not "
    "a full capability grant). Implements + measures Binding Principle B (disjoint reference: a non-agent "
    "pronoun's candidate pool excludes the entity holding the AGENT role in the pronoun's OWN clause) as "
    "an opt-in candidate-pool filter layered before strict_cb's (atom 29614) selection -- glass-box, zero "
    "supplied knowledge, zero borrowed embeddings, strict_cb itself never mutated. FRESH RE-EXECUTION of "
    "the cell independently reproduced every headline number bit-for-bit: pronoun-B3 F1 0.7029->0.7047 "
    "(lift=+0.0018, below the pre-registered 0.02 HARD_PASS margin -> not HARD_PASS on this metric); "
    "identity-demanding situation-model query accuracy 0.7193->0.7368 (lift=+0.0175, toward oracle 0.9298); "
    "g5g6-only identity-demanding query 0.72->0.76 (lift=+0.04, toward oracle 0.96); name-path (0.8369-> "
    "0.8361) and overall (0.8078->0.8075) B3-F1 flat, both within the 0.01 regression tolerance -> zero "
    "regression. DIRECT: filter fired on 9/76 pronoun decisions, changed 2 final picks, corrected 1 "
    "(probe case 14, 'the schoolmaster took a seat beside him' -> him=boy not schoolmaster) and broke 0; "
    "net +1, entirely inside the flagged subset. Guard mechanism verified in the fresh run: 25 abstentions "
    "via abstain_no_same_clause_agent (covers participials/continued-subject where the agent is tagged at "
    "a PRIOR clause), 3 via abstain_multi_same_clause_agent (multi-verb/relative clauses with >=2 same-"
    "clause agents), 0 breakage across all 36 passages -- confirms the conservative firing conditions do "
    "their job. Honest read: right fix flavor, small realized coverage; the ~53% cross-clause discourse "
    "frontier (B2 from atom 29620) remains open.")
atom2 = {
    "atom_id": AID2, "seq": 29621, "op": "atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "grade": "MM_binding_principle_b_net_positive_guard_safe_below_hard_pass_margin_partial_coref_only",
    "verdict": "PARTIAL_COREF_ONLY", "anchor": "coref_flag_fix_loop_principle_b_v1",
    "anchor_name": "coref_flag_fix_loop_principle_b_v1",
    "cell": "experiments/exp_coref_flag_fix_loop_principle_b_v1.py",
    "cell_commit": "4cc041fcd356ae20e1694afeba813316ae177fc2", "cell_content_sha256_16": cell2_sha,
    "metrics_path": "data/exp_coref_flag_fix_loop_principle_b_v1/metrics.json",
    "metrics_sha256_16": metrics2_sha,
    "headline": HEAD2,
    "key_metrics": {
        "cell_verdict": "PARTIAL_COREF_ONLY", "auditor_tier": "MEASURED_MECHANISM", "cert_delta": 0,
        "pronoun_b3_strict_cb": 0.7029326700972488, "pronoun_b3_principle_b": 0.7047160370965815,
        "pronoun_b3_lift": 0.0017833669993326806, "pronoun_b3_hard_pass_margin": 0.02,
        "iddem_query_strict_cb": 0.7192982456140351, "iddem_query_principle_b": 0.7368421052631579,
        "iddem_query_oracle": 0.9298245614035088, "iddem_query_lift": 0.01754385964912275,
        "g5g6_iddem_strict_cb": 0.72, "g5g6_iddem_principle_b": 0.76, "g5g6_iddem_oracle": 0.96,
        "name_regression": 0.0007642648717568479, "overall_regression": 0.0002572426067406486,
        "regression_tol": 0.01,
        "n_pronoun_decisions": 76, "n_filter_fired": 9, "n_decisions_changed": 2,
        "corrected": 1, "broken": 0, "net": 1,
        "guard_abstain_no_same_clause_agent": 25, "guard_abstain_multi_same_clause_agent": 3,
        "n_passages": 36, "breakage_across_all_passages": 0,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv FRESH RE-EXECUTION of the cell (subprocess re-run, not "
        "a metrics.json read) reproduced every headline number bit-for-bit against the pre-existing "
        "banked metrics.json: pronoun-B3, name/overall regression, identity-demanding query (combined + "
        "g5g6-only), corrected/broken/net counts, and the full principle_b_action_counts dict (fired=9, "
        "abstain_no_same_clause_agent=25, abstain_multi_same_clause_agent=3, plus the remaining abstain/"
        "allocate categories) all matched exactly. --self-test independently re-run and PASSed (positive "
        "co-argument fire + participial guard abstain + multi-agent guard abstain, all exercised on the "
        "real query-metric code path). This is a genuine independent recompute, not a report-read."),
    "composes_seq": [29614, 29619, 29620], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("Verdict-bearing for: (a) Binding Principle B is a real, glass-box, brain-faithful, "
        "guard-safe grammatical mechanism that produces a genuine net-positive correction (1 corrected, 0 "
        "broken) with zero regression and zero breakage across all 36 passages; (b) it moves the identity-"
        "demanding situation-model query metric meaningfully (+0.0175 combined, +0.04 on g5g6) toward "
        "oracle. NOT verdict-bearing as a HARD_PASS or as closing the pronoun-coreference gap -- the "
        "pronoun-B3 lift (+0.0018) is well below the pre-registered 0.02 margin, and realized coverage (1 "
        "correction out of 9 fires, out of 76 total pronoun decisions) is small. Coverage was intentionally "
        "traded for safety via the conservative same-clause-agent + single-candidate guards; a looser "
        "filter would likely fire more but risks the exact participial/multi-agent breakage those guards "
        "prevent (untested here -- this cell only measured the conservative variant)."),
    "framing_correction": ("None needed -- the spawn prompt's framing (PARTIAL, below-margin pronoun-B3, "
        "clear iddem/g5g6 lift, zero breakage) matches the fresh-recompute numbers exactly; no inflation or "
        "deflation found."),
    "revival_criteria": ("To promote toward HARD_PASS: either (a) loosen the same-clause-agent guard "
        "(e.g. allow multi-agent clauses when a secondary disambiguator like animacy or recency can break "
        "the tie) and re-measure breakage risk, or (b) combine with a B2 cross-clause discourse fix (atom "
        "29620's real open frontier, ~53% of flagged errors) so the two fixes' corrections compound rather "
        "than B1 alone bearing the whole margin. Current guard-conservative design is the right FIRST cut "
        "(prioritizes zero regression) but is not yet the ceiling of what Principle-B-style constraints "
        "could contribute if loosened carefully."),
    "primitive_assessment": ("Validates a reusable, glass-box, brain-faithful grammatical-competence "
        "primitive (same-clause role-collision exclusion via clause_role, already-tracked per-entity-per-"
        "clause data, zero new knowledge/resource) as a safe, composable candidate-pool filter layered "
        "before an existing coref mechanism. This is the first concrete confirmation that the self-"
        "improving-loop's probe-to-aim step (atom 29620) correctly identified a real, buildable lever."),
    "hf_attribution": "n/a (net-positive, not a HF; PARTIAL not NULL).",
    "fairness_verdict": ("FAIR: one-variable comparison (principle_b filter layered on strict_cb vs "
        "strict_cb alone, same streams/event-slots, same gold, same 36-passage/76-decision powered eval); "
        "pre-registered can-fail bars (0.02 pronoun-B3 margin, 0.03 iddem margin, 0.01 regression tol) "
        "stated BEFORE the run per the cell's own docstring; guard-driven abstentions reported in full "
        "(not just the fired count) so the coverage/safety tradeoff is fully visible, not summarized away. "
        "Regression tolerance was NOT cleared for iddem lift bar (0.0175 < 0.03 IDDEM_QUERY_MARGIN) -- "
        "flagged here explicitly since the cell's own verdict_msg does not restate this second sub-bar "
        "miss; PARTIAL_COREF_ONLY correctly reflects missing BOTH the pronoun-B3 margin AND the iddem "
        "margin, not just the former."),
    "cross_arc_overlap": ("Composes atom 29614 (strict_cb, the imported-verbatim baseline mechanism), "
        "atom 29619 (loop cycle 1, defines the flag threshold n_compatible>=2 and the 76-decision powered "
        "eval this cell reuses), and atom 29620 (the probe that identified this exact lever). "
        "substrate_query.sh 'Binding Principle B disjoint reference same-clause agent exclusion pronoun "
        "coreference' -> top cosine=0.3779 (generic 'coreference'/'reference' concept nodes); none >0.30 "
        "is a prior experiment cell on this mechanism. Novel."),
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom2))

# =====================================================================================================
# ATOM 29622 -- META (CERT-neutral): self-improving-loop engine pattern, cycles 1-2
# =====================================================================================================
AID3 = ("meta::self_improving_reader_loop_engine_flag_probe_to_aim_fix_discriminates_good_from_bad_"
    "fixes_on_its_own_signal_cycle1_topic_continuity_REJECTED_null_fix_mechanism_cycle2_principle_b_"
    "ACCEPTED_net_positive_guard_safe_glass_box_brain_faithful_zero_supplied_knowledge_zero_borrowed_"
    "embeddings_MM_TENTATIVE_SYNTHESIS_only_2_cycles_composed_needs_a_3rd_before_CG_LOCAL_ONLY")
assert AID3 not in existing_ids
HEAD3 = ("MM_TENTATIVE_SYNTHESIS (CERT-neutral methodology atom; composes atoms 29619, 29620, 29621 -- "
    "no new experimental grant, characterizes the PATTERN across them). The self-improving-reader loop "
    "(flag earned-error-prone decisions via n_compatible -> probe-to-aim classifies what mechanism would "
    "fix them -> implement the redirected fix -> measure honestly) has now run TWO full cycles with "
    "opposite outcomes, and the loop's own can-fail measurement correctly discriminated between them "
    "without needing outside judgment: Cycle 1 (topic-continuity/Centering-Continue, atom 29619) was "
    "REJECTED by its own measurement -- pronoun-B3 and identity-demanding-query both regressed, 0 "
    "corrected/3 broken on the divergent flagged decisions, robust across a decay sweep -- a clean, "
    "trustworthy NULL. The probe (atom 29620) then re-diagnosed the flagged-error population and "
    "correctly redirected effort toward a different, cheaper mechanism. Cycle 2 (Binding Principle B, "
    "atom 29621) was ACCEPTED by the same measurement discipline -- net-positive (1 corrected, 0 broken), "
    "zero regression, zero breakage across all 36 passages, real lift on the situation-model-relevant "
    "identity-demanding query metric -- though it stayed below the pre-registered HARD_PASS margin, so "
    "it is a guard-safe partial win, not a closed capability. Every step in both cycles is glass-box "
    "(no bolt-on parser/reader, no borrowed embeddings, no LLM-at-inference) and brain-faithful (Binding "
    "Principle B is a genuine grammatical universal, not a task-specific heuristic).")
atom3 = {
    "atom_id": AID3, "seq": 29622, "op": "atomize", "corpus": "meta",
    "tier": "MM_TENTATIVE_SYNTHESIS", "cert_status": "n/a (CERT-neutral methodology synthesis)",
    "grade": "MM_TENTATIVE_synthesis_loop_engine_discriminates_good_bad_fixes_on_own_signal_2_cycles",
    "verdict": "PATTERN_HOLDS_2_CYCLES", "anchor": "self_improving_reader_loop_engine_synthesis",
    "anchor_name": "self_improving_reader_loop_engine_synthesis",
    "cell": "n/a (synthesis atom composing 29619/29620/29621)",
    "headline": HEAD3,
    "key_metrics": {
        "n_cycles_composed": 2, "cycle1_verdict": "NULL_FIX_MECHANISM (REJECTED)",
        "cycle2_verdict": "PARTIAL_COREF_ONLY (ACCEPTED, net-positive, below HARD_PASS margin)",
        "cycle1_corrected": 0, "cycle1_broken": 3, "cycle2_corrected": 1, "cycle2_broken": 0,
        "glass_box": True, "brain_faithful": True, "zero_supplied_knowledge": True,
        "zero_borrowed_embeddings": True,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("Composed strictly from atoms 29619 (cycle 1, independently VET'd this "
        "session's predecessor batch) and 29620/29621 (probe + cycle 2, independently recomputed above in "
        "THIS script). No new off-disk numbers introduced; this atom characterizes the CROSS-CYCLE pattern "
        "only. Explicitly NOT overclaimed as a general-purpose self-improvement guarantee -- N=2 cycles is "
        "too small to certify the loop as reliably self-correcting; it is banked as a tentative, promising "
        "pattern that composing atoms already support, not a new capability grant."),
    "composes_seq": [29619, 29620, 29621], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("Verdict-bearing for: the loop's measurement discipline (pre-registered can-fail "
        "bars, honest corrected/broken accounting, guard-safety checks) correctly separated a genuinely bad "
        "fix (cycle 1) from a genuinely good-but-partial one (cycle 2) using ONLY its own signal, no "
        "external adjudication needed. NOT verdict-bearing as 'the loop reliably self-improves' or 'the "
        "loop will keep finding good fixes' -- 2 data points (1 reject, 1 accept) is not enough to certify "
        "a general self-improvement capability; expansion criterion below."),
    "framing_correction": ("This atom exists specifically to avoid over-certifying the loop pattern from "
        "only 2 cycles -- banked as MM_TENTATIVE_SYNTHESIS, CERT-neutral, not MM_STANDARD or CG, per "
        "instruction to only bank if it holds up as reusable and not cheerleading."),
    "revival_criteria": ("Expansion criterion (MM_TENTATIVE -> MM_STANDARD): a 3rd independent cycle "
        "(ideally targeting the B2 cross-clause discourse frontier atom 29620 identified as the real open "
        "work) that the loop's own measurement again correctly accepts or rejects, without director/auditor "
        "steering the classification. A 3rd cycle landing cleanly on either side would materially "
        "strengthen the claim that this is a durable engine property, not a 2-sample coincidence."),
    "primitive_assessment": ("No experimental primitive; a reusable METHODOLOGY pattern for any future "
        "flag -> probe-to-aim -> fix -> measure cycle in this program (situation-model, self-monitoring/"
        "calibration, or other construction-competency work): pre-register can-fail bars, measure honestly "
        "on the loop's own held signal, let probe-to-aim redirect after a rejection rather than iterating "
        "blindly on the same failed mechanism."),
    "hf_attribution": "n/a (CERT-neutral synthesis, not a HF).",
    "fairness_verdict": ("FAIR: composes only atoms already independently VET'd (29619 by a prior batch, "
        "29620/29621 by this script), does not introduce new unverified claims, and explicitly bounds its "
        "own confidence by N=2 cycles rather than generalizing prematurely."),
    "cross_arc_overlap": ("Directly composes 29619/29620/29621 (this arc). No separate substrate_query.sh "
        "check needed beyond the two already run for 29620/29621 -- this atom introduces no new mechanism "
        "claim, only a cross-cycle characterization."),
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom3))

# =====================================================================================================
# WRITE: 29620/29621 -> math; 29622 -> meta. Then 3 ledger entries.
# =====================================================================================================
math_after1 = A5_write(ATOMS_MATH, math_lines, atom1, "MEASURED_MECHANISM")
math_after2 = A5_write(ATOMS_MATH, [json.dumps(o, ensure_ascii=False) for o in math_after1], atom2, "MEASURED_MECHANISM")
assert math_after2[-1]["seq"] == 29621 and math_after2[-2]["seq"] == 29620
print(f"MATH ATOMS OK: {len(math_lines)} -> {len(math_after2)}; seqs 29620 (probe) & 29621 (fix).")

meta_after1 = A5_write(ATOMS_META, meta_lines, atom3, "MM_TENTATIVE_SYNTHESIS")
assert meta_after1[-1]["seq"] == 29622
print(f"META ATOMS OK: {len(meta_lines)} -> {len(meta_after1)}; seq 29622 (loop-engine synthesis, CERT-neutral).")

# ---- LEDGER (3 entries) ----
ledger_now = ledger_lines
for atom, decision in [
    (atom1, "MEASURED_MECHANISM CERT +0 (probe/diagnosis, composes 29619). Recompute confirms raw case "
             "count (17/17) matches the loop cell's own flagged-and-wrong count exactly. Distribution "
             "(A=5.9%/B1=29.4%/B2=52.9%/C=11.8%/D=0%) is a small-N hand classification, banked as such -- "
             "not a powered statistic. REDIRECT verdict correctly steered away from verb-semantics (low "
             "ceiling) toward the cheap Principle-B lever, subsequently confirmed real by atom 29621."),
    (atom2, "MEASURED_MECHANISM CERT +0 (PARTIAL_COREF_ONLY, composes 29614/29619/29620). FRESH cell "
             "re-execution (not a report-read) reproduced every headline number bit-for-bit: pronoun-B3 "
             "+0.0018 (below 0.02 margin), iddem +0.0175/g5g6 +0.04 (below the 0.03 iddem margin -- both "
             "sub-bars missed, correctly reflected in PARTIAL_COREF_ONLY not a HARD_PASS mislabel), "
             "name/overall flat, corrected=1/broken=0/net=1, 0 breakage across 36 passages via guards. "
             "Real, brain-faithful, glass-box grammatical competence; small realized coverage; the ~53% "
             "cross-clause B2 frontier remains open."),
    (atom3, "MM_TENTATIVE_SYNTHESIS CERT-neutral (composes 29619/29620/29621, no new grant). The self-"
             "improving loop's own measurement discipline correctly discriminated a rejected fix (cycle 1) "
             "from an accepted net-positive fix (cycle 2) without external adjudication. Explicitly scoped "
             "as tentative -- N=2 cycles, expansion criterion (a 3rd independently-adjudicated cycle) "
             "stated for promotion to MM_STANDARD. Not cheerleading: banked only because it composes "
             "already-VET'd evidence and states its own confidence bound."),
]:
    led = dict(atom)
    led["decision"] = decision
    led["note"] = ("AUDIT-ONLY (hdi_skunkworks) independent .venv recompute -- Finding 1 verified via raw "
                   "case-file load, Finding 2 verified via FRESH cell re-execution (subprocess, not a "
                   "metrics.json read), Finding 3 is a bounded cross-cycle synthesis. NOT from verdict_msg "
                   "or spawn-prompt summary. 2026-08-02 batch (3 atoms, store head 29619). LOCAL-ONLY; no "
                   "origin push; no remote persist.")
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
assert len(vl) == len(ledger_lines) + 3
assert [iseq(x) for x in vl[-3:]] == [29620, 29621, 29622]
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seqs 29620/29621/29622.")
print("DONE. net_cert_delta = +0 for all three (probe diagnosis + guard-safe partial fix + CERT-neutral "
      "synthesis, no new full capability grant). LOCAL-ONLY; no origin push; no remote persist.")
