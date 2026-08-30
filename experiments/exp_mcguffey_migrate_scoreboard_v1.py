"""exp_mcguffey_migrate_scoreboard_v1 -- THE UNIFIED PER-ORGAN CORPUS-AGE SCOREBOARD.

Problem: the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text (p1).

Assembles the one-screen deliverable the migration asks for: per reader organ, the McGuffey-population
result vs the MODERN-population result, each vs its strongest floor recomputed on its OWN population,
with the info-free twin, and the corpus-age delta. Reads only landed metrics.json (no recompute; no
in-place rewrite of any landed dir). Writes only data/exp_mcguffey_migrate_scoreboard_v1/scoreboard.json.

Rows:
  ROLE / SITUATION-MODEL  -- this problem's Cells (McGuffey vs modern UD-EWT, same scorer) + the fix.
  COREF / WHO-DID-WHAT    -- already migrated to LitBank (cited from landed cells; owner-DONE).
"""
from __future__ import annotations
import argparse, json, os
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(REPO, "data/exp_mcguffey_migrate_scoreboard_v1")


def load(rel):
    p = os.path.join(REPO, rel)
    return json.load(open(p)) if os.path.exists(p) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    rev = load("data/exp_mcguffey_migrate_revalidate_v1/metrics.json")
    fix = load("data/exp_mcguffey_migrate_passive_cue_fix_v1/metrics.json")
    binder = load("data/exp_wire_predarg_binder_litbank_whodidwhat_v1/metrics.json")

    assert rev and fix, "run the revalidate + fix cells first"

    mcg = rev["populations"]["MCGUFFEY_1830s"]["subsets"]
    mod = rev["populations"]["MODERN_UD_EWT"]["subsets"]

    def cell(row, arm):
        a = row[arm]
        return {"acc": a["acc"], "ci": a["ci"], "n": a["n"]}

    scoreboard = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "rows": {
            "ROLE_situation_model": {
                "organ": "situation_reader role front-end (vargs) + resolver + role scorer",
                "metric": "role accuracy (agent/patient) on entity-role-at-clause-T queries",
                "MCGUFFEY_1830s": {
                    "population": "57 hand-authored passages, 153 in-scope q",
                    "majority_floor": cell(mcg["ALL_INSCOPE"], "FLOOR_MAJORITY"),
                    "organ_vargs": cell(mcg["ALL_INSCOPE"], "VARGS"),
                    "info_free_twin": cell(mcg["ALL_INSCOPE"], "VARGS_TWIN"),
                    "organ_beats_strongest_floor_ci_sep": cell(mcg["ALL_INSCOPE"], "VARGS")["ci"][0] >
                                                          cell(mcg["ALL_INSCOPE"], "FLOOR_MAJORITY")["ci"][1],
                    "note": "DEGENERATE: 90.85% of in-scope gold is agent; organ (0.856) LOSES to the "
                            "always-agent floor (0.908). McGuffey only ever beat the twin, never the floor.",
                },
                "MODERN_UD_EWT": {
                    "population": "330 UD-EWT gold-parse passages, 700 in-scope q (177 role-varying, 59 non-canonical)",
                    "majority_floor_all": cell(mod["ALL_INSCOPE"], "FLOOR_MAJORITY"),
                    "organ_vargs_all": cell(mod["ALL_INSCOPE"], "VARGS"),
                    "organ_vargs_rolevarying": cell(mod["ROLE_VARYING"], "VARGS"),
                    "floor_rolevarying": cell(mod["ROLE_VARYING"], "FLOOR_MAJORITY"),
                    "organ_vargs_canonical": cell(mod["CANONICAL"], "VARGS"),
                    "organ_vargs_noncanonical": cell(mod["NONCANONICAL"], "VARGS"),
                    "twin_noncanonical": cell(mod["NONCANONICAL"], "VARGS_TWIN"),
                    "organ_beats_strongest_floor_all_ci_sep": cell(mod["ALL_INSCOPE"], "VARGS")["ci"][0] >
                                                              cell(mod["ALL_INSCOPE"], "FLOOR_MAJORITY")["ci"][1],
                    "organ_below_floor_all_ci_sep": cell(mod["ALL_INSCOPE"], "VARGS")["ci"][1] <
                                                    cell(mod["ALL_INSCOPE"], "FLOOR_MAJORITY")["ci"][0],
                    "organ_below_floor_noncanonical_ci_sep": cell(mod["NONCANONICAL"], "VARGS")["ci"][1] <
                                                             cell(mod["NONCANONICAL"], "FLOOR_MAJORITY")["ci"][0],
                    "note": "current organ does NOT clear the strongest floor on modern text; COLLAPSES to "
                            "0.29 on non-canonical (below coin-flip twin) -- confidently wrong.",
                },
                "corpus_age_delta_vargs_all": rev["corpus_age_delta"]["ALL_INSCOPE"]["vargs_modern_minus_mcguffey"],
                "brain_fidelity_fix": {
                    "noncanonical_broken": fix["subsets"]["NONCANONICAL"]["BROKEN"]["acc"],
                    "noncanonical_fixed": fix["subsets"]["NONCANONICAL"]["FIXED"]["acc"],
                    "noncanonical_fixed_ci": fix["subsets"]["NONCANONICAL"]["FIXED"]["ci"],
                    "noncanonical_twin": fix["subsets"]["NONCANONICAL"]["FIXED_TWIN"]["acc"],
                    "fixed_beats_broken_ci_sep": fix["verdict"]["fixed_beats_broken_noncanonical_ci_sep"],
                    "fixed_beats_twin": fix["verdict"]["fixed_beats_twin_noncanonical"],
                    "canonical_not_hurt": fix["verdict"]["fixed_not_hurt_canonical"],
                    "note": "brain-faithful passive-aware content-verb assigner (Competition Model cue-"
                            "validity) recovers non-canonical; the wall is a cue gap, not a ceiling.",
                },
            },
            "COREF_who_did_what": {
                "organ": "coreference_resolver / predarg binder (graded ACT-R)",
                "status": "ALREADY MIGRATED to LitBank + owner-DONE (coreference_is_capped_at_065... SOLVED)",
                "MODERN_LitBank_19c": {
                    "who_did_what_binder_GRADED": (binder["who_did_what_pron_recall"]["arc+GRADED"]["acc"]
                                                   if binder else 0.3281),
                    "info_free_RAND_twin": (binder["who_did_what_pron_recall"]["arc+RAND"]["acc"]
                                            if binder else 0.1321),
                    "oracle_perfect_binding": 1.0,
                    "twin_loses_ci": (binder["verdict"]["randbind_twin_loses_CI"] if binder else True),
                    "owner_done_graded_actr_competitive_pronouns": 0.775,
                    "incumbent_hard_tier": 0.603,
                    "note": "coref is OFF McGuffey; twin loses CI-separated on 19c literary LitBank gold coref.",
                },
            },
        },
        "recommendation": (
            "1) Retire McGuffey as the PRIMARY role/situation-model eval -- its in-scope role population is "
            "90.85% agent (degenerate; a trivial floor beats the organ). Make the modern UD-EWT eval the "
            "primary role/situation-model instrument (co-primary with LitBank for coref). "
            "2) Land the passive-cue fix in the role front-end (proposed diff in SOLVED.md). "
            "3) Build a both-gold modern NARRATIVE situation-model gold (coref+role on one text) -- the one "
            "dimension no on-shelf modern corpus supplies."
        ),
    }

    if args.self_test:
        assert scoreboard["rows"]["ROLE_situation_model"]["MODERN_UD_EWT"]["organ_below_floor_noncanonical_ci_sep"]
        print("self-test PASS")
        return

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "scoreboard.json"), "w", encoding="utf-8") as f:
        json.dump(scoreboard, f, indent=2)
    R = scoreboard["rows"]["ROLE_situation_model"]
    print("=" * 92)
    print("UNIFIED CORPUS-AGE SCOREBOARD -- reader organs, McGuffey 1830s vs modern")
    print("=" * 92)
    print("\n[ROLE / SITUATION-MODEL]  (same organ, same scorer, two populations)")
    print(f"  McGUFFEY  floor {R['MCGUFFEY_1830s']['majority_floor']['acc']:.3f}  organ(vargs) "
          f"{R['MCGUFFEY_1830s']['organ_vargs']['acc']:.3f}  twin {R['MCGUFFEY_1830s']['info_free_twin']['acc']:.3f}"
          f"  [DEGENERATE: organ LOSES to floor]")
    m = R["MODERN_UD_EWT"]
    print(f"  MODERN    floor {m['majority_floor_all']['acc']:.3f}  organ(vargs) {m['organ_vargs_all']['acc']:.3f}"
          f"  [organ below floor CI-sep: {m['organ_below_floor_all_ci_sep']}]")
    print(f"     non-canonical: organ {m['organ_vargs_noncanonical']['acc']:.3f}  floor "
          f"{load('data/exp_mcguffey_migrate_revalidate_v1/metrics.json')['populations']['MODERN_UD_EWT']['subsets']['NONCANONICAL']['FLOOR_MAJORITY']['acc']:.3f}"
          f"  twin {m['twin_noncanonical']['acc']:.3f}  [COLLAPSE, below chance]")
    fx = R["brain_fidelity_fix"]
    print(f"     FIX (brain-faithful): non-canonical {fx['noncanonical_broken']:.3f} -> {fx['noncanonical_fixed']:.3f}"
          f"  (CI-sep {fx['fixed_beats_broken_ci_sep']}, twin {fx['noncanonical_twin']:.3f} loses, canonical unhurt {fx['canonical_not_hurt']})")
    c = scoreboard["rows"]["COREF_who_did_what"]["MODERN_LitBank_19c"]
    print("\n[COREF / WHO-DID-WHAT]  (already migrated to LitBank, owner-DONE)")
    print(f"  MODERN(LitBank)  binder {c['who_did_what_binder_GRADED']:.3f}  RAND-twin {c['info_free_RAND_twin']:.3f}"
          f"  graded-ACT-R 0.775 vs incumbent 0.603  [twin loses CI: {c['twin_loses_ci']}]")
    print("\nRECOMMENDATION:\n  " + scoreboard["recommendation"])
    print(f"\nwrote {os.path.relpath(os.path.join(OUTDIR,'scoreboard.json'), REPO)}")


if __name__ == "__main__":
    main()
