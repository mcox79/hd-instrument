"""A5-gated LOCAL-ONLY atomize of two independently-VET'd 2026-08-02 landings.
AUDIT-ONLY (hdi_skunkworks). Independent .venv recompute off raw metrics.json (per_entity_records /
per_arm per_entity, NOT verdict_msg strings, NOT the Director summary). No experiment authored/dispatched
by auditor.

TWO atoms, store head 29608 -> seqs 29609/29610:
  29609 math : situation-model register is ARCHITECTURALLY accumulate (FHRR bundle), not pure-overwrite --
               construction-proof MEASURED_MECHANISM (proven-bound), cert_delta +1. Composes/upgrades
               situation_model_event_bundle_focus_v1 (PARTIAL, cosine=0.3721 nearest KB hit, confirmed
               build-on not rediscovery).
  29610 math : end-to-end wire (validated extraction -> validated accumulate WM) HARD_FAILs because
               EXTRACTION does not generalize off its quotative/by-agent training distribution to
               canonical-active multiclause narrative (REAL=0.231 vs ORACLE=1.000 vs FLOOR=0.192).
               Honest negative, cert_delta 0. AMENDS 29606/29608 (construction-scope narrowing, does
               NOT retract their cert -- those atoms' own quotative/by-agent claims are unaffected).

DISK-VERIFY performed before this script banks (see scratchpad recompute
C:/Users/marsh/AppData/Local/Temp/claude/d--AI/02e8b04e-1164-42ee-b96d-ac16726a826a/scratchpad/
skunkworks_vet_20260802.py, executed via .venv, output captured below):

#1 data/exp_situation_model_accumulate_vs_overwrite_v1/metrics.json (per_entity_records, N=15 entities,
   13 multi-event): recomputed multi_event_agg EXACTLY matches reported for all 3 arms (overwrite
   0.461538, accumulate 1.000000, floor 0.205128); single-event positive control both arms =1.0, floor=0.0
   (control holds); analytic overwrite formula (1+(n-1)*chance)/n recomputes to 0.497863, matching
   measured overwrite within the pre-registered 0.08 tolerance (can-fail formula confirmed, not just
   trusted); accumulate_by_n_events breakdown recomputes 1.0 at both n=2 (5 entities) and n=3 (8 entities)
   -- i.e. the 100% accumulate result is a CEILING at chain-length 2-3, capacity NOT stress-tested beyond
   that (construction-proof scope, not a capacity/scale win, exactly as the spawn prompt flagged). Gap
   recomputes to 0.5385 >= 0.30 bar. arms_differ_verified True (3 distinct sha256 hashes).

#2 data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1/metrics.json (per_arm/per_entity, N=15
   entities, 13 multi-event): recomputed multi_event_recall EXACTLY matches reported for all 3 arms
   (oracle 1.000000 -- reproduces atom 29609/36ab29a93 bit-for-bit within tol; real 0.230769; floor
   0.192308). floor reg_digest (b1b9f97c7a...832312) is IDENTICAL across this cell and the accumulate
   cell (same seed+999 construction) -- independent cross-check that the floor arm is genuinely the
   same non-vacuous construction in both cells, not silently redefined. role_census recomputes exactly:
   agent=21 patient=7 recipient=3 theme=4 addressee=1, total=36, unreachable(theme+recipient+addressee)=8,
   unreachable_fraction=0.2222 (matches the binary is-agent-or-not extractor's structural ceiling).

MECHANISM-LEVEL recompute beyond the metrics.json aggregate (spawn-prompt's "root cause off the
per-entity dump, not the verdict string" requirement): tabulated true-role vs pred-role for every one of
the 36 role-events in per_entity_dump. Among the 21 events where true_role=='agent', STAGE-1 predicts
'patient' 17/21 times (81.0%) and 'agent' correctly only 4/21 times (19.0%) -- CONFIRMS the extraction
does NOT merely fail to help on canonical actives, it is actively WRONG on canonical actives most of the
time. HOWEVER, a more precise mechanism characterization than the spawn prompt's framing ("predict
surface-subject=patient"): inspecting clause_dump.argmax_token for the mispredicted cases shows STAGE-1's
argmax frequently lands on a NON-SUBJECT, often clause-final/oblique mention (e.g. mary_dash_doll clause0
argmax="time", not "Mary"; edgar_thomas_boat clause2 argmax="hand", not "Edgar"/"Thomas") -- i.e. this is
ARGMAX-MISLOCALIZATION (the model's is-agent score peaks on the wrong candidate entirely), not a clean
"true-subject gets the patient label" inversion rule. The true agent then defaults to 'patient' as the
UNCLAIMED fallback, which produces the same net effect (true-agent -> pred-patient) but the underlying
cause is that STAGE-1's learned features (follows_by, in_passive_ctx, after_close, position-after-verb)
are overfit to postposed-quotative-speaker and by-agent-passive positional patterns and provide NO
reliable positive signal for a plain preverbal SVO subject. Correspondingly, of the 4 events where
STAGE-1 correctly predicted agent for a true-agent event, 3 of 4 are exactly quotative-postposed-speaker
constructions matching its training distribution (susie_hears_1 clause2 "'...' Susie asked", harry_
carriage clause2 "'...' said Harry to his mother", edgar_thomas_boat clause0 "'...' said the boatman")
-- direct confirmation that STAGE-1 generalizes within its trained construction types and fails outside
them, exactly the spawn prompt's hypothesis, with this one refinement on the precise failure mode.
Among the 8 structurally-unreachable role-events (theme/recipient/addressee), 7/8 were forced to
'patient' and 1/8 coincidentally landed on 'agent' (the argmax happened to fall on that mention) --
consistent with a fallback mechanism, not a crash, and consistent with "structurally unreachable
regardless of extraction quality" (a binary is-agent classifier cannot emit a 3rd/4th/5th label).

cross_arc_overlap check (bash tools/substrate_query.sh, per the substrate-KB concept-overlap discipline):
  #1 query "situation model accumulate bundle FHRR entity tracking multi-event register" -> top hit
     situation_model_event_bundle_focus_v1 cosine=0.3721 (PARTIAL verdict) -- CONFIRMS this is a genuine
     build-on/decisive-resolution of that prior PARTIAL finding, not a rediscovery.
  #2 query "extraction generalization failure canonical active voice agent role wrong argmax
     non-canonical training" -> no relevant prior-arc atom at cosine>0.30 (top hits were generic
     wordnet/gene-ontology noise on the word "canonical") -- NOVEL finding, no dedup concern.

Commits verified present: 36ab29a93 (accumulate cell), 8b57859cf (wire cell), 041ee195e (WHERE doc).
HEAD before this batch = 29608 (confirmed: math/meta/ledger all report max seq 29608).
"""
import json, os, time, tempfile, datetime, hashlib

ATOMS_MATH = "data/substrate_index/math/atoms.jsonl"
ATOMS_META = "data/substrate_index/meta/atoms.jsonl"
LEDGER = "data/substrate_index/meta/cert_ledger.jsonl"
CAPREG = "data/capability_registry.jsonl"


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
capreg_lines = load(CAPREG)
pm = [json.loads(l) for l in math_lines]
pe = [json.loads(l) for l in meta_lines]
pl = [json.loads(l) for l in ledger_lines]
existing_ids = {o.get("atom_id") for o in (pm + pe) if o.get("atom_id")}
assert not any("\r" in l for l in (math_lines[-5:] + meta_lines[-5:]))


def maxseq(objs):
    m = -1
    for o in objs:
        s = o.get("seq")
        try:
            s = int(s)
        except Exception:
            continue
        if s > m:
            m = s
    return m


STORE_HEAD = max(maxseq(pm), maxseq(pe), maxseq(pl))
assert STORE_HEAD == 29608, f"expected store head 29608, got {STORE_HEAD}"
assert not any("situation_model_accumulate_vs_overwrite_v1" in o.get("anchor_name", "") for o in pm)
assert not any("wire_extraction_accumulate_wm_oracle_vs_real_v1" in o.get("anchor_name", "") for o in pm)
assert any(iseq(o) == 29606 for o in pm), "parent 29606 missing (needed for amends_seq)"
assert any(iseq(o) == 29608 for o in pm), "parent 29608 missing (needed for amends_seq)"
print(f"PRE-GATE OK: store head {STORE_HEAD}; parents 29606/29608 present; new seqs 29609/29610.")

# =====================================================================================================
# OFF-DISK independent recompute (bare python, re-derives every headline number from raw per-entity
# arrays in metrics.json, NOT from verdict_msg/summary strings)
# =====================================================================================================
import statistics
from collections import defaultdict

# ---- #1 accumulate vs overwrite ----
M1 = json.load(open("data/exp_situation_model_accumulate_vs_overwrite_v1/metrics.json", encoding="utf-8"))
recs = M1["per_entity_records"]
multi = [r for r in recs if r["multi_event"]]
single = [r for r in recs if not r["multi_event"]]
recompute = {}
for arm in ("overwrite", "accumulate", "floor"):
    recompute[arm] = statistics.mean([r["recall_per_arm"][arm] for r in multi])
assert abs(recompute["overwrite"] - 0.46153846153846145) < 1e-9
assert abs(recompute["accumulate"] - 1.0) < 1e-9
assert abs(recompute["floor"] - 0.20512820512820512) < 1e-9
chance = 1.0 / 6
analytic = statistics.mean([(1.0 + (r["n_events"] - 1) * chance) / r["n_events"] for r in multi])
assert abs(analytic - M1["analytic_overwrite_multi_predicted"]) < 1e-9
gap1 = recompute["accumulate"] - recompute["overwrite"]
assert abs(gap1 - 0.5384615384615385) < 1e-9
byn = defaultdict(list)
for r in multi:
    byn[r["n_events"]].append(r["recall_per_arm"]["accumulate"])
for k, v in byn.items():
    assert abs(statistics.mean(v) - 1.0) < 1e-9
single_ctrl_ok = (statistics.mean([r["recall_per_arm"]["overwrite"] for r in single]) >= 0.95
                  and statistics.mean([r["recall_per_arm"]["accumulate"] for r in single]) >= 0.95)
assert single_ctrl_ok
assert M1["gates"]["canfail_ok"] is True and M1["gates"]["gate_mechanism_hard_pass"] is True
assert M1["arms_differ_verified"] is True
m1_sha = sha16("data/exp_situation_model_accumulate_vs_overwrite_v1/metrics.json")
cell1_sha = sha16("experiments/exp_situation_model_accumulate_vs_overwrite_v1.py")
print(f"#1 OFF-DISK OK: overwrite={recompute['overwrite']:.4f} accumulate={recompute['accumulate']:.4f} "
      f"floor={recompute['floor']:.4f} gap={gap1:.4f} (>=0.30 bar); analytic-overwrite recompute "
      f"{analytic:.4f} matches reported (can-fail formula independently confirmed); accumulate=1.0 at "
      f"BOTH n_events=2 (5 ent) and n_events=3 (8 ent) -- ceiling at this short chain length, capacity "
      f"beyond 3 events NOT tested (construction-proof scope). metrics_sha={m1_sha}")

# ---- #2 wire extraction (oracle/real/floor) ----
M2 = json.load(open("data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1/metrics.json", encoding="utf-8"))
for arm, expect in (("oracle", 1.0), ("real", 0.23076923076923073), ("floor", 0.19230769230769232)):
    ents = M2["per_arm"][arm]["per_entity"]
    v = statistics.mean([e["recall"] for e in ents if e["multi_event"]])
    assert abs(v - expect) < 1e-9, (arm, v, expect)
assert M1["arm_hashes"]["floor"] == M2["per_arm"]["floor"]["reg_digest"], "floor construction diverged across cells"
dump = M2["per_entity_dump"]
census = defaultdict(int)
for e in dump:
    for r in e["true_roles"]:
        census[r] += 1
total = sum(census.values())
reachable = census.get("agent", 0) + census.get("patient", 0)
assert dict(census) == {"agent": 21, "patient": 7, "recipient": 3, "theme": 4, "addressee": 1}
assert total == 36 and reachable == 28 and (total - reachable) / total == M2["summary"]["role_census"]["unreachable_fraction"]

# mechanism-level: true-agent events, predicted-label breakdown
agent_pred = defaultdict(int)
n_agent = 0
for e in dump:
    for t, p in zip(e["true_roles"], e["pred_roles"]):
        if t == "agent":
            n_agent += 1
            agent_pred[p] += 1
assert n_agent == 21
frac_wrong_as_patient = agent_pred["patient"] / n_agent
assert abs(frac_wrong_as_patient - (17.0 / 21.0)) < 1e-9
assert agent_pred["agent"] == 4

# spot-check argmax-mislocalization on canonical actives (not clean subject->patient inversion, but
# argmax landing on an unrelated/oblique token, per clause_dump)
clause_by_key = {(c["passage_id"], c["clause_idx"]): c for c in M2["clause_dump"]}
mary_clause0 = clause_by_key[("mary_dash_doll", 0)]
edgar_clause2 = clause_by_key[("edgar_thomas_boat", 2)]
assert mary_clause0["argmax_token"] == "time" and "Mary" not in (mary_clause0["argmax_token"] or "")
assert edgar_clause2["argmax_token"] == "hand"
# quotative-postposed-speaker correct-agent spot check (susie_hears_1 clause2, harry_carriage clause2,
# edgar_thomas_boat clause0 -- all quotative, all argmax correctly lands on the true speaker/agent)
assert clause_by_key[("susie_hears_1", 2)]["argmax_token"] == "Susie"
assert clause_by_key[("harry_carriage", 2)]["argmax_token"] == "Harry"
assert clause_by_key[("edgar_thomas_boat", 0)]["argmax_token"] == "boatman"

assert M2["verdict"] == "HARD_FAIL_REAL_EXTRACTION_NO_BETTER_THAN_FLOOR"
oracle_to_real_drop = M2["summary"]["oracle_to_real_drop"]
assert abs(oracle_to_real_drop - 0.7692307692307693) < 1e-9
real_to_floor_gap = M2["summary"]["real_multi_event_recall"] - M2["summary"]["floor_multi_event_recall"]
assert real_to_floor_gap < 0.05  # real barely clears floor -- can-fail-consistent HARD_FAIL, not a bug
m2_sha = sha16("data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1/metrics.json")
cell2_sha = sha16("experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1.py")
print(f"#2 OFF-DISK OK: oracle=1.0000 (reproduces atom 29609/36ab29a93) real=0.2308 floor=0.1923 "
      f"(real-floor gap={real_to_floor_gap:.4f}, barely above floor); role_census confirmed "
      f"unreachable_fraction=0.2222; true-agent-events mispredicted-as-patient={frac_wrong_as_patient:.4f} "
      f"(17/21); argmax-mislocalization confirmed on canonical actives (Mary clause argmax='time', "
      f"Edgar/Thomas clause argmax='hand') vs correct agent-argmax on 3/3 spot-checked quotative-"
      f"postposed-speaker clauses. metrics_sha={m2_sha}")

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
# ATOM 29609 -- MATH: situation-model register is ARCHITECTURALLY accumulate (bundle), not pure-overwrite.
# Construction-proof, MEASURED_MECHANISM (proven-bound). cert_delta +1.
# =====================================================================================================
AID1 = ("math::situation_model_accumulate_vs_overwrite_v1_MEASURED_MECHANISM_situation_model_register_"
    "is_ARCHITECTURALLY_an_ACCUMULATE_FHRR_bundle_organ_NOT_a_pure_OVERWRITE_organ_on_real_McGuffey_"
    "multiclause_entity_track_gold_overwrite_0p4615_matches_analytic_1_over_n_events_0p4979_exactly_"
    "accumulate_1p000_floor_0p2051_at_chance_gap_0p5385_ge_0p30_bar_single_event_positive_control_"
    "both_arms_1p000_holds_arms_differ_verified_HONEST_SCOPE_construction_proof_NOT_a_capacity_scale_"
    "win_accumulate_hits_ceiling_1p000_at_BOTH_n_events_2_and_3_only_chain_lengths_present_in_this_"
    "gold_bundling_capacity_beyond_3_events_UNTESTED_composes_and_upgrades_situation_model_event_"
    "bundle_focus_v1_PARTIAL_cosine_0p3721_confirmed_build_on_not_rediscovery_LOCAL_ONLY")
assert AID1 not in existing_ids
HEAD1 = ("MEASURED_MECHANISM (CERT +1, proven-bound, construction-proof). On real McGuffey multiclause "
    "entity-track gold (15 entities, 13 multi-event, 36 role-events), the situation-model register is "
    "ARCHITECTURALLY an accumulate (FHRR-bundle-of-all-event-bindings) organ, not a pure-overwrite "
    "(last-write-wins) organ: accumulate recovers 100% of multi-event entities' role-history "
    "(recall=1.0000) vs overwrite's 0.4615, which matches the CLOSED-FORM structural prediction "
    "[1+(n-1)*chance]/n = 0.4979 almost exactly (the can-fail check the pre-reg required), while an "
    "independent random-register floor sits at 0.2051 (~chance=0.1667). Gap=0.5385 clears the "
    "pre-registered 0.30 HARD_PASS bar; single-event positive control holds (both arms=1.0, floor=0.0). "
    "All 3 arm registers verified bit-distinct (arms_differ_verified). AUDITOR SCOPE CORRECTION vs the "
    "cell's raw HARD_PASS verdict (per spawn-prompt instruction to VET the construction-proof scope): "
    "this is a CONSTRUCTION-PROOF of the register's FORM (bundle beats overwrite), not a capacity/scale "
    "win -- accumulate_by_n_events shows the 100% ceiling holds identically at n_events=2 (5 entities) "
    "and n_events=3 (8 entities), the ONLY chain lengths present in this gold; the register's bundling "
    "CAPACITY (how many events it can hold before crosstalk degrades recall) is genuinely untested "
    "beyond 3. Tiered MEASURED_MECHANISM/proven-bound rather than a raw chain-grade capacity claim, "
    "matching the auditor convention used for atom 29606 (also cell-HARD_PASS, auditor-scoped MM).")
atom1 = {
    "atom_id": AID1, "seq": 29609, "op": "atomize", "corpus": "math",
    "tier": "MEASURED_MECHANISM", "cert_status": "proven-bound",
    "grade": "MM_situation_model_register_architecturally_accumulate_not_overwrite_construction_proof_scope_bounded_to_2to3_event_chains",
    "verdict": "HARD_PASS_auditor_scoped_MEASURED_MECHANISM_construction_proof",
    "anchor": "situation_model_accumulate_vs_overwrite_v1", "anchor_name": "situation_model_accumulate_vs_overwrite_v1",
    "cell": "experiments/exp_situation_model_accumulate_vs_overwrite_v1.py",
    "cell_commit": "36ab29a93", "cell_content_sha256_16": cell1_sha,
    "metrics_path": "data/exp_situation_model_accumulate_vs_overwrite_v1/metrics.json", "metrics_sha256_16": m1_sha,
    "headline": HEAD1,
    "key_metrics": {
        "cell_verdict": "HARD_PASS", "auditor_tier": "MEASURED_MECHANISM", "cert_delta": 1,
        "overwrite_multi": 0.46153846153846145, "accumulate_multi": 1.0, "floor_multi": 0.20512820512820512,
        "analytic_overwrite_predicted": 0.49786324786324787, "gap": 0.5384615384615385,
        "chance": 0.16666666666666666, "n_entities_total": 15, "n_multi_event_entities": 13,
        "single_event_overwrite": 1.0, "single_event_accumulate": 1.0, "single_event_floor": 0.0,
        "accumulate_by_n2": 1.0, "accumulate_by_n2_n_entities": 5,
        "accumulate_by_n3": 1.0, "accumulate_by_n3_n_entities": 8,
        "canfail_ok": True, "gate_mechanism_hard_pass": True, "arms_differ_verified": True,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv recompute off per_entity_records (NOT verdict_msg/summary): "
        "independently recomputed multi_event_agg for all 3 arms from the raw recall_per_arm arrays -- exact "
        "match to reported (overwrite 0.461538, accumulate 1.000000, floor 0.205128). Independently re-derived "
        "the analytic-overwrite closed-form prediction (0.497863) rather than trusting the stored value -- "
        "matches. Independently recomputed the accumulate_by_n_events breakdown (n=2: 1.0/5 entities; n=3: "
        "1.0/8 entities) confirming the ceiling-at-short-chains scope claim directly from raw data, not from "
        "the cell's own honest-scope framing."),
    "composes_seq": [], "corrects_seq": [], "amends_seq": [],
    "cert_delta": 1, "net_cert_delta": 1, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("Construction-proof of ARCHITECTURE (accumulate vs overwrite), not a capacity/scale "
        "result. The gold's max multi-event chain length is 3; the accumulate arm is a clean CEILING (1.0) "
        "at both observed lengths (2 and 3), meaning bundling-capacity degradation (which FHRR bundles are "
        "known to eventually exhibit as more items are superposed) has NOT been stress-tested here. A future "
        "cell extending chain length to 5-10+ events per entity would be the natural capacity-boundary test."),
    "framing_correction": ("Confirms the Director's HARD_PASS framing on the core claim (accumulate "
        "architecturally beats overwrite) but downgrades the SCOPE framing exactly as the spawn prompt "
        "flagged: 'construction proof of register-form, not a capacity/scale win' is independently verified "
        "true from the accumulate_by_n_events breakdown, not merely asserted."),
    "revival_criteria": ("n/a (not a negative). Natural extension: re-run with entity chains of length "
        "5, 8, and near MAX_EVENT_SLOTS=8 to find where FHRR bundle crosstalk starts degrading accumulate "
        "recall below 1.0 -- this would convert the construction-proof into a genuine capacity-boundary "
        "chain-grade result."),
    "primitive_assessment": ("Validates a reusable primitive: FHRR bind-per-event + bundle-across-events + "
        "unbind-by-slot-index-key IS the correct situation-model register organ (accumulate), superseding "
        "pure-overwrite as the WM update rule for entity-event history, at least at short (2-3 event) chain "
        "lengths. See capability_registry.jsonl gate decision (WIRE) below for reuse status."),
    "hf_attribution": "n/a (positive finding).",
    "fairness_verdict": ("FAIR: overwrite arm matches its OWN closed-form structural prediction almost "
        "exactly (0.4615 vs analytic 0.4979, within the pre-registered 0.08 tolerance), meaning the harness "
        "is trustworthy and overwrite is not being sandbagged by a bug -- it is genuinely structurally "
        "limited to the last-written slot plus chance-level guessing elsewhere. Floor at chance, single-event "
        "positive control holds, arms verified bit-distinct. No leak, no artifact found."),
    "cross_arc_overlap": ("bash tools/substrate_query.sh 'situation model accumulate bundle FHRR entity "
        "tracking multi-event register' -> top hit situation_model_event_bundle_focus_v1 (cosine=0.3721, "
        "prior verdict PARTIAL). CONFIRMED genuine build-on/decisive-resolution of that prior PARTIAL "
        "finding (this cell resolves the overwrite-vs-accumulate architectural question that finding left "
        "open), NOT a rediscovery. No other prior-arc atom at cosine>0.30."),
    "capability_registry_decision": "WIRE (see data/capability_registry.jsonl id="
        "'situation_model_accumulate_register_organ' for full gate record; auditor decision, not exp_dev/"
        "testbed promotion -- hdlab/ module creation is NOT done by this atom, flagged as the next-step "
        "for a wiring role).",
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom1))

# =====================================================================================================
# ATOM 29610 -- MATH: end-to-end wire HARD_FAIL -- extraction does not generalize off its training
# construction types. Honest negative, cert_delta 0. AMENDS 29606 and 29608 (scope-narrowing, no
# retraction of their cert).
# =====================================================================================================
AID2 = ("math::wire_extraction_accumulate_wm_oracle_vs_real_v1_HARD_FAIL_end_to_end_extraction_to_"
    "accumulate_WM_pipeline_FAILS_because_STAGE1_EXTRACTION_does_not_generalize_off_its_quotative_"
    "by_agent_training_construction_types_to_canonical_active_multiclause_narrative_ORACLE_gold_"
    "roles_1p000_reproduces_29609_36ab29a93_bit_for_bit_REAL_extraction_predicted_roles_0p2308_"
    "FLOOR_0p1923_real_barely_clears_floor_oracle_to_real_drop_0p7692_true_agent_events_"
    "mispredicted_as_patient_17_of_21_0p810_MECHANISM_argmax_mislocalization_not_a_clean_subject_"
    "inversion_STAGE1_argmax_lands_on_an_unrelated_oblique_clause_final_mention_mary_clause_argmax_"
    "time_not_Mary_edgar_thomas_clause_argmax_hand_correct_agent_predictions_concentrate_on_"
    "quotative_postposed_speaker_constructions_matching_training_distribution_3_of_4_spot_checked_"
    "22pct_of_roles_theme_recipient_addressee_structurally_UNREACHABLE_by_a_binary_is_agent_"
    "extractor_regardless_of_quality_the_WM_accumulate_organ_is_VALIDATED_end_to_end_GIVEN_correct_"
    "roles_the_wall_to_real_comprehension_is_EXTRACTION_GENERALIZATION_not_the_WM_AMENDS_29606_and_"
    "29608_construction_scope_narrowing_does_NOT_retract_their_quotative_by_agent_cert_LOCAL_ONLY")
assert AID2 not in existing_ids
HEAD2 = ("HARD_FAIL (honest negative, CERT +0, load-bearing as hard as a positive per contract). Wiring "
    "the two validated organs end-to-end (STAGE-1: frozen production interactive top-down extraction "
    "model from atom 29606/29608, applied out-of-domain; STAGE-2: the accumulate register validated in "
    "atom 29609) onto real McGuffey multiclause entity-tracking gold shows the pipeline FAILS: "
    "ORACLE(gold roles fed to WM)=1.0000 (reproduces atom 29609 bit-for-bit -- confirms the WM organ is "
    "correctly wired and works given correct input), but REAL(STAGE-1-predicted roles fed to WM)=0.2308, "
    "barely above FLOOR=0.1923 (real-floor gap=0.038, can-fail-consistent: extraction adds almost no "
    "signal over noise once end-to-end). ROOT CAUSE, verified off the per-entity_dump (not the verdict "
    "string): among the 21 true-agent role-events, STAGE-1 predicts 'patient' 17 times (81.0%) and "
    "'agent' correctly only 4 times (19.0%). AUDITOR REFINEMENT of the spawn prompt's proposed mechanism: "
    "this is not a clean 'surface-subject gets mislabeled patient' inversion rule -- inspecting "
    "clause_dump.argmax_token shows STAGE-1's argmax often lands on an unrelated, non-subject, "
    "often clause-final/oblique mention entirely (mary_dash_doll clause0 argmax='time', not 'Mary'; "
    "edgar_thomas_boat clause2 argmax='hand', not 'Edgar'/'Thomas'), so the true agent defaults to the "
    "'patient' fallback because it was simply never claimed by anything, not because it was actively "
    "recognized-and-relabeled. The mechanism is ARGMAX-MISLOCALIZATION driven by features (follows_by, "
    "in_passive_ctx, after_close, verb-adjacency) that were fit to postposed-quotative-speaker and "
    "by-agent-passive constructions and provide no reliable positive signal on plain preverbal SVO "
    "subjects. Correspondingly 3 of the 4 correct true-agent predictions are exactly quotative-postposed-"
    "speaker clauses matching STAGE-1's training distribution -- direct within-distribution-generalizes, "
    "out-of-distribution-fails confirmation. SEPARATELY, 22.2% of all role-events (theme/recipient/"
    "addressee, 8/36) are STRUCTURALLY unreachable by a binary is-agent-or-not extractor regardless of "
    "how well it generalizes -- a coverage-gap ceiling independent of the generalization failure. THE "
    "LOAD-BEARING TAKEAWAY: the extraction milestone (atoms 29606/29608) is a CONSTRUCTION-SPECIFIC "
    "competency (quotative-speaker-selection, by-agent-passive-agent-selection), NOT a general-purpose "
    "semantic-role extractor; the wall to real McGuffey comprehension is EXTRACTION GENERALIZATION to "
    "canonical active-voice constructions, while the accumulate WM organ (atom 29609) is fully validated "
    "given correct roles and is NOT the bottleneck.")
atom2 = {
    "atom_id": AID2, "seq": 29610, "op": "atomize", "corpus": "math",
    "tier": "HARD_FAIL", "cert_status": "honest-negative",
    "grade": "HF_extraction_generalization_wall_argmax_mislocalization_outside_trained_construction_types_wm_organ_validated_given_correct_roles",
    "verdict": "HARD_FAIL_REAL_EXTRACTION_NO_BETTER_THAN_FLOOR",
    "anchor": "wire_extraction_accumulate_wm_oracle_vs_real_v1", "anchor_name": "wire_extraction_accumulate_wm_oracle_vs_real_v1",
    "cell": "experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1.py",
    "cell_commit": "8b57859cf", "cell_content_sha256_16": cell2_sha,
    "metrics_path": "data/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1/metrics.json", "metrics_sha256_16": m2_sha,
    "headline": HEAD2,
    "key_metrics": {
        "cell_verdict": "HARD_FAIL_REAL_EXTRACTION_NO_BETTER_THAN_FLOOR", "auditor_tier": "HARD_FAIL", "cert_delta": 0,
        "oracle_multi": 1.0, "real_multi": 0.23076923076923073, "floor_multi": 0.19230769230769232,
        "oracle_to_real_drop": 0.7692307692307693, "real_to_floor_gap": 0.038461538461538464,
        "true_agent_events_n": 21, "true_agent_mispred_as_patient_n": 17, "true_agent_mispred_as_patient_frac": 0.8095238095238095,
        "true_agent_correct_n": 4, "unreachable_role_events_n": 8, "unreachable_role_events_total": 36,
        "unreachable_fraction": 0.2222222222222222,
        "quotative_spotcheck_correct_agent_of_correct_predictions": "3_of_4",
        "floor_digest_cross_experiment_match": True,
    },
    "auditor": "hdi_skunkworks", "verified_off_data": True,
    "verified_off_data_note": ("AUDIT-ONLY .venv recompute off per_arm/per_entity + per_entity_dump + "
        "clause_dump (NOT verdict_msg/summary): oracle/real/floor multi_event_recall all independently "
        "recomputed and match exactly. Floor reg_digest cross-checked bit-identical between this cell and "
        "atom 29609's cell (same seed+999 construction, confirming the floor was not silently redefined). "
        "Role census independently recomputed from true_roles arrays, matches reported unreachable_fraction "
        "exactly. THE MECHANISM CLAIM (argmax-mislocalization, not clean subject-inversion) was derived "
        "directly from clause_dump.argmax_token spot-checks on the specific mispredicted canonical-active "
        "entities (Mary, Edgar, Thomas) and the specific correctly-predicted quotative entities (Susie, "
        "Harry, boatman) -- this is a genuine off-disk mechanism audit, not a restatement of the cell's own "
        "prose."),
    "composes_seq": [29609], "corrects_seq": [], "amends_seq": [29606, 29608],
    "cert_delta": 0, "net_cert_delta": 0, "store_head_at_write": STORE_HEAD,
    "honest_scope": ("Genuine structural negative, not a test-design failure: can-fail gates held (oracle "
        "reproduces atom 29609 within tolerance, floor at chance, arms hash-differ), so the harness is "
        "trustworthy and the HARD_FAIL is trusted. STAGE-1 was correctly used as a FROZEN production model "
        "(refit on 100% of ITS OWN validated gold, then applied out-of-domain) -- this is a fair test of "
        "generalization, not an unfair or miscalibrated one. HF_STRUCTURAL_BOUND: the extraction "
        "construction-competency genuinely does not extend to canonical actives; this is not a bug."),
    "framing_correction": ("Confirms the Director's core framing (extraction generalization is the wall, WM "
        "organ validated given correct roles) but SHARPENS the mechanism claim: the spawn prompt hypothesized "
        "the extraction 'inverts on canonical active-voice clauses (predict surface-subject=patient)'. The "
        "off-disk clause_dump audit shows this is not quite a clean inversion rule -- the argmax more often "
        "lands on an entirely unrelated/oblique mention (not the true agent AND not necessarily the true "
        "patient either), so the true agent defaults to 'patient' as the unclaimed fallback rather than being "
        "actively recognized-and-mislabeled. Net observable effect on the true-agent class is the same "
        "(81% mispredicted as patient), but the causal story is ARGMAX-MISLOCALIZATION on out-of-distribution "
        "features, not surface-subject-specific inversion. This is a precision correction, not a disagreement "
        "with the Director's overall verdict or root-cause direction."),
    "revival_criteria": ("Per the spawn prompt's own framing and Bornkessel eADM reference: the fix is "
        "CONSTRUCTION-CONDITIONAL multi-role extraction, not a single global binary is-agent classifier. "
        "(1) Add canonical-active-voice gold (preverbal-subject=agent, no quote, no by-phrase, no passive "
        "morphology) to STAGE-1's training distribution alongside quotative/by-agent, so the model learns a "
        "construction-conditional feature interaction rather than overfitting to postposed/passive-context "
        "features; (2) extend the label space beyond binary agent/patient to cover the 22.2% structurally-"
        "unreachable theme/recipient/addressee roles (a genuinely different architecture: multiclass role "
        "assignment per mention, not a single argmax-picks-the-agent scheme); (3) re-run this exact wire "
        "cell after either fix to check whether REAL climbs meaningfully above FLOOR (target: clearing the "
        "pre-registered REAL_MIDDLE_MIN=0.30, ideally REAL_HARD_PASS_MIN=0.50)."),
    "primitive_assessment": ("No new working primitive from THIS cell in isolation (it is an integration/"
        "diagnostic wire-up, not a novel mechanism); its value is CONFIRMING atom 29609's WM organ works "
        "end-to-end given correct input (oracle=1.0, composes_seq=[29609]) and LOCALIZING the actual "
        "comprehension bottleneck precisely to extraction generalization rather than the WM, which the prior "
        "atoms (29606/29608) had left ambiguous by testing extraction and WM in isolation from each other."),
    "hf_attribution": "HF_STRUCTURAL_BOUND (genuine generalization failure of a construction-specific "
        "classifier applied out-of-domain; positive control -- oracle reproduction -- cleared its own bar, "
        "so this is not a broken harness).",
    "fairness_verdict": ("FAIR: STAGE-1 was refit as a frozen production model on 100% of its own already-"
        "validated gold (no peeking at the new multiclause evaluation gold during fitting), then applied "
        "out-of-domain -- a genuine generalization test, not a rigged one. Oracle/real/floor three-arm design "
        "isolates extraction error from WM error cleanly (composes_seq=[29609] documents the WM organ's own "
        "independent validation). Coverage-gap (22.2% unreachable roles) was pre-registered and read off disk "
        "BEFORE running, per the cell's own docstring -- not a post-hoc excuse."),
    "cross_arc_overlap": ("bash tools/substrate_query.sh 'extraction generalization failure canonical active "
        "voice agent role wrong argmax non-canonical training' -> no relevant prior-arc atom at cosine>0.30 "
        "(only generic wordnet/gene-ontology noise on the word 'canonical'). NOVEL finding, no dedup concern. "
        "Composes atom 29609 (WM organ) via composes_seq; amends atoms 29606/29608 (extraction construction-"
        "scope) via amends_seq -- see those atoms' honest_scope fields, which already flagged 'small N, "
        "construction-specific, not full comprehension'; this atom concretizes that caveat with a specific, "
        "measured out-of-domain failure mode rather than retracting either atom's in-domain cert."),
    "wm_organ_validated_end_to_end_given_correct_roles": True,
    "needs_orchestrator_store_sync": True, "local_write_only_no_origin_push_no_remote_persist": True,
    "ts": ts, "ts_iso": ts_iso, "ts_day": ts_day,
}
json.loads(json.dumps(atom2))

# =====================================================================================================
# WRITE: both atoms -> math (in seq order). Then 2 ledger entries.
# =====================================================================================================
math_after1 = A5_write(ATOMS_MATH, math_lines, atom1, "MEASURED_MECHANISM")
math_after2 = A5_write(ATOMS_MATH, [json.dumps(o, ensure_ascii=False) for o in math_after1], atom2, "HARD_FAIL")
assert math_after2[-1]["seq"] == 29610 and math_after2[-2]["seq"] == 29609
print(f"MATH ATOMS OK: {len(math_lines)} -> {len(math_after2)}; seqs 29609 (MM, +1) & 29610 (HARD_FAIL, +0, amends 29606/29608).")

# ---- LEDGER (2 entries) ----
ledger_now = ledger_lines
for atom, decision in [
    (atom1, "MEASURED_MECHANISM CERT +1 (proven-bound, construction-proof). Recompute off "
             "per_entity_records confirms EXACTLY: overwrite=0.4615 matches its own closed-form analytic "
             "prediction 0.4979 (can-fail confirmed independently, not trusted), accumulate=1.0000, "
             "floor=0.2051, gap=0.5385 clears the 0.30 bar, single-event positive control holds. Auditor "
             "scopes DOWN from the cell's raw HARD_PASS to MEASURED_MECHANISM because accumulate_by_n_events "
             "shows the 100% result is a ceiling at chain-length 2-3 only (untested capacity beyond that) -- "
             "construction-proof of architecture, not a capacity/scale win, matching the spawn prompt's "
             "explicit instruction to VET this scope. cross_arc_overlap query confirms genuine build-on of "
             "situation_model_event_bundle_focus_v1 (cosine=0.3721, prior PARTIAL), not a rediscovery."),
    (atom2, "HARD_FAIL CERT +0 (honest negative, VET'd as hard as a positive per contract). Recompute off "
             "per_arm/per_entity confirms EXACTLY: oracle=1.0000 (reproduces atom 29609), real=0.2308, "
             "floor=0.1923 (real barely clears floor, can-fail-consistent). Off-disk mechanism audit of "
             "per_entity_dump + clause_dump confirms 17/21 (81.0%) true-agent events mispredicted as "
             "'patient', REFINES the spawn prompt's proposed mechanism from a clean 'subject->patient "
             "inversion' to ARGMAX-MISLOCALIZATION (argmax lands on an unrelated oblique mention entirely, "
             "e.g. 'time'/'hand' instead of the true agent), with correct predictions concentrated 3/4 in "
             "quotative-postposed-speaker constructions matching STAGE-1's training distribution. Confirms "
             "22.2% of roles are structurally unreachable by a binary is-agent extractor. Localizes the "
             "comprehension wall to EXTRACTION GENERALIZATION, not the WM (which reproduces its own prior "
             "cert=1.0 given correct roles). AMENDS atoms 29606/29608 (construction-scope narrowing) without "
             "retracting their quotative/by-agent cert grants."),
]:
    led = dict(atom)
    led["decision"] = decision
    led["note"] = ("AUDIT-ONLY (hdi_skunkworks) independent .venv recompute off metrics.json per_entity_"
                   "records / per_arm / per_entity_dump / clause_dump, NOT verdict_msg or Director summary. "
                   "2026-08-02 batch (2 atoms, store head 29608). LOCAL-ONLY; no origin push; no remote "
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
assert [iseq(x) for x in vl[-2:]] == [29609, 29610]
print(f"LEDGER OK: {len(ledger_lines)} -> {len(vl)}; seqs 29609/29610.")

# =====================================================================================================
# CAPABILITY REGISTRY: WIRE decision for the accumulate register organ (auditor decision + record;
# actual hdlab/ module-promotion code-writing is explicitly OUT OF SCOPE for hdi_skunkworks -- flagged
# as the next step for a wiring role, per role-separation).
# =====================================================================================================
cap_ids = set()
for l in capreg_lines:
    try:
        cap_ids.add(json.loads(l).get("id"))
    except Exception:
        pass
CAP_ID = "situation_model_accumulate_register_organ"
assert CAP_ID not in cap_ids, "capability registry row already exists -- would duplicate"
cap_row = {
    "id": CAP_ID,
    "name": "FHRR bind-per-event + bundle-across-events situation-model register (VET-CONFIRMED "
            "construction-proof: accumulate beats pure-overwrite for multi-event entity role history)",
    "kind": "exp-cell+mechanism",
    "path": [
        "experiments/exp_situation_model_accumulate_vs_overwrite_v1.py",
        "experiments/exp_wire_extraction_accumulate_wm_oracle_vs_real_v1.py",
    ],
    "status": "vet_confirmed_measured_mechanism_construction_proof_2026-08-02",
    "gate_decision": "WIRE",
    "gate_decision_target": (
        "promote the accumulate-register organ (bind role_vec to idx_vec per event, FHRR-bundle across "
        "all of an entity's events, unbind-by-slot-key + cleanup-argmax to read back) to a formal reusable "
        "hdlab/ module (e.g. hdlab/situation_model_register.py exposing build_register/score_entity or "
        "equivalent), since it is now validated in TWO independent cells (atom math seq 29609 direct test; "
        "atom math seq 29610 end-to-end reproduction given correct roles, oracle=1.0). Currently the organ "
        "is duplicated bit-for-bit as bare-numpy code in both experiment cells, not yet a single importable "
        "module -- that promotion is explicitly OUT OF SCOPE for hdi_skunkworks (audit-only role separation; "
        "code-authoring/wiring belongs to hdi_exp_dev or hdi_testbed) and is flagged here as the concrete "
        "next step for whichever role picks this up."
    ),
    "integration_status": "ISLAND",
    "used_by": [],
    "revival_criteria": (
        "n/a for the organ itself (validated, not shelved). BLOCKING caveat for practical end-to-end use: "
        "atom math seq 29610 (HARD_FAIL) shows the organ is fully validated GIVEN CORRECT ROLES but the "
        "only available real-text role extractor (atoms 29606/29608) does not generalize to canonical "
        "active-voice constructions (real=0.231 vs oracle=1.000 vs floor=0.192) -- so a hdlab/ promotion of "
        "this organ now would have no correctly-functioning real-text consumer yet. Promote as a WIRED, "
        "discoverable, oracle-validated asset regardless (per the 'wire don't island' + 'promote at land-"
        "time' discipline), but the natural DOWNSTREAM step (a working end-to-end comprehension pipeline) "
        "is gated on fixing extraction generalization (see atom 29610's revival_criteria: construction-"
        "conditional multi-role extraction, not a binary is-agent classifier), not on this organ."
    ),
    "supersedes": None, "superseded_by": None,
    "current_best_for": (
        "reusable situation-model WM register asset: any harness needing multi-event entity-role history "
        "over an FHRR substrate should use bind(role,idx)+bundle-across-events+unbind, NOT last-write-wins "
        "overwrite. VET math seq 29609 CONFIRMED (construction-proof, scope-bounded to chain-length 2-3, "
        "capacity beyond that untested) + VET math seq 29610 (independent end-to-end reproduction of the "
        "SAME organ given correct roles, oracle=1.0000, confirms the organ, not just the isolated cell, "
        "generalizes across a second independent implementation/harness)."
    ),
    "provenance": (
        "cell 36ab29a93 (direct test) + cell 8b57859cf (end-to-end wire, reimplemented bit-for-bit for the "
        "oracle arm). VET math seq 29609 (hdi_skunkworks) = CONFIRMED MEASURED_MECHANISM/proven-bound, "
        "construction-proof scope. VET math seq 29610 (hdi_skunkworks) = independent oracle-arm reproduction "
        "(1.0000, bit-for-bit) confirms cross-cell robustness; the real-arm HARD_FAIL in that same atom is "
        "attributed entirely to STAGE-1 extraction, not this organ. Composes situation_model_event_bundle_"
        "focus_v1 (prior PARTIAL, cosine=0.3721 nearest KB hit, confirmed genuine build-on not rediscovery "
        "via substrate_query.sh)."
    ),
    "last_audit_utc": ts_iso,
    "last_decision_utc": ts_iso,
}
json.loads(json.dumps(cap_row))
cap_line = json.dumps(cap_row, ensure_ascii=False)
assert "\r" not in cap_line and "\n" not in cap_line
capreg_new = capreg_lines + [cap_line]
new_cap_text = "\n".join(capreg_new) + "\n"
dcap = os.path.dirname(os.path.abspath(CAPREG))
fd3, tmp3 = tempfile.mkstemp(dir=dcap, suffix=".tmp"); os.close(fd3)
with open(tmp3, "w", encoding="utf-8", newline="") as f:
    f.write(new_cap_text); f.flush(); os.fsync(f.fileno())
os.replace(tmp3, CAPREG)
assert b"\r\n" not in open(CAPREG, "rb").read(), "CRLF doubling in capability registry"
vc = [json.loads(l) for l in open(CAPREG, encoding="utf-8").read().splitlines() if l.strip()]
assert len(vc) == len(capreg_lines) + 1
assert vc[-1]["id"] == CAP_ID and vc[-1]["gate_decision"] == "WIRE"
print(f"CAPABILITY REGISTRY OK: {len(capreg_lines)} -> {len(vc)}; WIRE decision recorded for {CAP_ID}.")

print("DONE. net_cert_delta = +1 (atom 29609 MEASURED_MECHANISM proven-bound construction-proof) "
      "+ 0 (atom 29610 HARD_FAIL honest negative, amends 29606/29608 scope without retracting their cert). "
      "Capability registry: WIRE decision recorded for the accumulate register organ (hdlab/ module-"
      "promotion code itself left to a wiring role, per audit-only separation). LOCAL-ONLY; no origin push; "
      "no remote persist.")
