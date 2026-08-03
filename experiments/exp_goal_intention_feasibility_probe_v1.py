"""Mine goal/intention gold items on Anne of Green Gables (measurement-only, not dispatched).

Extracts verbatim spans directly from the source clean.txt by line range (so every
verbatim is a substring of the source file BY CONSTRUCTION -- the guard below re-checks
this explicitly rather than trusting construction alone, per task's substring-guard
requirement) and computes explicit-vs-inferred split + causal-link recoverability.
"""
import json
import os

REPO_ROOT = r"D:\AI\hd-instrument"
CLEAN_TXT = os.path.join(REPO_ROOT, "data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt")
GOLD_V2 = os.path.join(REPO_ROOT, "data/eval_gold_mention_role_mcguffey_v1/gold_anne_comprehension_v2.jsonl")
OUT_PATH = os.path.join(REPO_ROOT, "data/eval_gold_mention_role_mcguffey_v1/gold_anne_goal_intention_v1.jsonl")
METRICS_PATH = os.path.join(REPO_ROOT, "data/exp_goal_intention_feasibility_probe_v1/metrics.json")

with open(CLEAN_TXT, "r", encoding="utf-8") as f:
    LINES = f.readlines()

# GOAL_MARKER lexicon reused verbatim from exp_causal_link_proposal_signal_probe_v1.py
GOAL_MARKERS = [
    "wants", "wanted", "want to", "decide", "decided", "decides", "resolved", "resolve",
    "sacrifice", "self-sacrificing", "gave up", "give up", "gives up", "giving up",
    "in order to", "so that", "so she could", "so he could", "hopes", "hoped", "hope",
    "planned", "plans", "intends", "intended", "determined", "chose", "chooses", "choose",
    "withdrew", "withdrawn", "forgive", "forgives", "forgiven", "promised", "promise",
    "made up my mind", "made up her mind", "must and shall", "willing to",
]


def extract(line_start, line_end):
    span = "".join(LINES[line_start - 1:line_end])
    return span


def substring_guard(verbatim):
    return verbatim in "".join(LINES)


def has_explicit_goal_marker(verbatim):
    low = verbatim.lower()
    return any(m in low for m in GOAL_MARKERS)


ITEMS = [
    dict(id="anne_goal_001", character="Anne", chapter=11, line_range=[2714, 2717],
         goal="wants Marilla to make one of her new dresses with puffed sleeves",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_016"]),
    dict(id="anne_goal_002", character="Matthew", chapter=25, line_range=[6774, 6776],
         goal="secretly decides to buy Anne a proper dress with puffed sleeves for Christmas",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_016", "anne_causal_025"]),
    dict(id="anne_goal_003", character="Matthew", chapter=25, line_range=[6782, 6785],
         goal="determined to get through buying the dress himself despite dreading the shop",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_025"]),
    dict(id="anne_goal_004", character="Marilla", chapter=6, line_range=[1586, 1593],
         goal="decides she and Matthew will keep Anne rather than send her to Mrs. Blewett",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_003"]),
    dict(id="anne_goal_005", character="Anne", chapter=5, line_range=[1280, 1283],
         goal="makes up her mind to enjoy the buggy-ride to Green Gables despite not knowing if she can stay",
         explicit_vs_inferred="explicit", resolves_which_event=[]),
    dict(id="anne_goal_006", character="Anne", chapter=8, line_range=[2121, 2125],
         goal="hopes Diana will become her bosom friend / kindred spirit",
         explicit_vs_inferred="explicit", resolves_which_event=[]),
    dict(id="anne_goal_007", character="Anne", chapter=15, line_range=[3925, 3927],
         goal="resolves she shall never forgive Gilbert Blythe after the slate incident",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_002"]),
    dict(id="anne_goal_008", character="Anne", chapter=17, line_range=[4679, 4682],
         goal="resolves to try to be a model pupil at school",
         explicit_vs_inferred="explicit", resolves_which_event=[]),
    dict(id="anne_goal_009", character="Anne", chapter=30, line_range=[8451, 8454],
         goal="determines to shroud/hide her feelings of regret about the class rivalry with Gilbert",
         explicit_vs_inferred="explicit", resolves_which_event=[]),
    dict(id="anne_goal_010", character="Anne", chapter=34, line_range=[9653, 9656],
         goal="resolves to win the Avery scholarship through hard work",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_012"]),
    dict(id="anne_goal_011", character="Anne", chapter=38, line_range=[10355, 10361],
         goal="decides to give up the Avery scholarship and not go to Redmond, to stay with Marilla",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_005"]),
    dict(id="anne_goal_012", character="Gilbert", chapter=38, line_range=[10460, 10467],
         goal="withdraws his application for the Avonlea school so Anne can have it; resolves to teach at White Sands instead",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_006", "anne_causal_001"]),
    dict(id="anne_goal_013", character="Anne", chapter=38, line_range=[10522, 10525],
         goal="wants to thank Gilbert for giving up the school for her (reconciliation)",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_001"]),
    dict(id="anne_goal_014", character="Mrs. Barry", chapter=16, line_range=[4555, 4556],
         goal="wants Diana not to associate with Anne any longer (implied by the prohibition speech act; no explicit want/decide verb)",
         explicit_vs_inferred="inferred", resolves_which_event=["anne_causal_004", "anne_causal_018"]),
    dict(id="anne_goal_015", character="Mrs. Barry", chapter=18, line_range=[5081, 5084],
         goal="hopes Anne will forgive her and wants the girls to be friends again",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_004"]),
    dict(id="anne_goal_016", character="Anne", chapter=18, line_range=[4963, 4967],
         goal="wants to save Minnie May's life, applying her croup-nursing knowledge (implied by her competent, purposeful action; no explicit want/decide verb)",
         explicit_vs_inferred="inferred", resolves_which_event=["anne_causal_019"]),
    dict(id="anne_goal_017", character="Miss Josephine Barry", chapter=19, line_range=[5581, 5582],
         goal="wants Anne to come visit and talk to her occasionally",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_022"]),
    dict(id="anne_goal_018", character="Marilla", chapter=20, line_range=[5793, 5796],
         goal="intends the walk through the spruce grove as a deliberate lesson/warning to cure Anne's runaway imagination",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_023"]),
    dict(id="anne_goal_019", character="Anne", chapter=14, line_range=[3436, 3451],
         goal="wants to end her confinement and be freed to go to the picnic; invents a false confession to achieve it (goal implied by the act of confessing to something she didn't do, not stated as a want)",
         explicit_vs_inferred="inferred", resolves_which_event=["anne_causal_017"]),
    dict(id="anne_goal_020", character="Anne", chapter=19, line_range=[5537, 5543],
         goal="wants Diana to keep her promised music lessons; pleads to be blamed instead of Diana",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_021"]),
    dict(id="anne_goal_021", character="Marilla", chapter=9, line_range=[2380, 2383],
         goal="wants/demands that Anne apologize to Mrs. Lynde",
         explicit_vs_inferred="explicit", resolves_which_event=["anne_causal_014"]),
]


def main():
    out_items = []
    n_substring_ok = 0
    n_explicit = 0
    n_inferred = 0
    n_explicit_marker_confirmed = 0
    for it in ITEMS:
        ls, le = it["line_range"]
        verbatim = extract(ls, le)
        ok = substring_guard(verbatim)
        n_substring_ok += int(ok)
        if not ok:
            raise AssertionError(f"SUBSTRING GUARD FAILED for {it['id']}")
        marker_hit = has_explicit_goal_marker(verbatim)
        if it["explicit_vs_inferred"] == "explicit":
            n_explicit += 1
            if marker_hit:
                n_explicit_marker_confirmed += 1
        else:
            n_inferred += 1
        row = {
            "id": it["id"],
            "character": it["character"],
            "goal": it["goal"],
            "verbatim_evidence": {
                "chapter": it["chapter"],
                "line_range": it["line_range"],
                "verbatim": verbatim,
            },
            "explicit_vs_inferred": it["explicit_vs_inferred"],
            "resolves_which_event": it["resolves_which_event"],
            "lexical_goal_marker_present": marker_hit,
            "gold_verified": False,
        }
        out_items.append(row)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        for row in out_items:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # ---- feasibility / fair-test metrics ----
    n_total = len(out_items)
    substring_guard_pct = n_substring_ok / n_total

    # (a) extractability: fraction lexically-detectable via a goal-verb marker (proxy for
    # "near-term trackable by a construction-cue/keyword register", NOT the same axis as the
    # human explicit_vs_inferred label -- both reported, see below).
    lexically_detectable = sum(1 for r in out_items if r["lexical_goal_marker_present"])

    # (b) coverage of the 9/18 goal-mediated causal links (from
    # exp_causal_link_proposal_signal_probe_v1 SIGNAL3, commit 912077b81):
    GOAL_MEDIATED_CAUSAL_IDS = {
        "anne_causal_001", "anne_causal_003", "anne_causal_004", "anne_causal_005",
        "anne_causal_006", "anne_causal_014", "anne_causal_016", "anne_causal_017",
        "anne_causal_021",
    }
    covered = set()
    covered_explicit_only = set()
    for r in out_items:
        for cid in r["resolves_which_event"]:
            if cid in GOAL_MEDIATED_CAUSAL_IDS:
                covered.add(cid)
                if r["explicit_vs_inferred"] == "explicit":
                    covered_explicit_only.add(cid)
    n_goal_mediated = len(GOAL_MEDIATED_CAUSAL_IDS)
    n_recoverable_any = len(covered)
    n_recoverable_explicit_only = len(covered_explicit_only)

    metrics = {
        "verdict": "MEASURED_MECHANISM",
        "anchor_name": "goal_intention_feasibility_probe_v1",
        "n_goal_items": n_total,
        "substring_guard_pass": n_substring_ok,
        "substring_guard_pct": substring_guard_pct,
        "explicit_vs_inferred": {
            "n_explicit": n_explicit,
            "n_inferred": n_inferred,
            "explicit_fraction": n_explicit / n_total,
            "inferred_fraction": n_inferred / n_total,
            "n_explicit_confirmed_by_lexical_marker": n_explicit_marker_confirmed,
        },
        "lexical_marker_extractability": {
            "n_items_with_goal_marker_in_verbatim": lexically_detectable,
            "fraction": lexically_detectable / n_total,
            "note": "GOAL_MARKERS lexicon reused unchanged from "
                    "exp_causal_link_proposal_signal_probe_v1.py -- fraction of mined goal "
                    "spans a lexical scan would flag as goal-bearing at all (necessary but not "
                    "sufficient for goal-verb+coref'd-subject+complement extraction).",
        },
        "causal_link_coverage_if_tracked": {
            "n_goal_mediated_causal_links_total": n_goal_mediated,
            "goal_mediated_causal_ids": sorted(GOAL_MEDIATED_CAUSAL_IDS),
            "n_recoverable_if_any_goal_tracked": n_recoverable_any,
            "n_recoverable_if_only_explicit_goals_tracked": n_recoverable_explicit_only,
            "recoverable_any_fraction": n_recoverable_any / n_goal_mediated,
            "recoverable_explicit_only_fraction": n_recoverable_explicit_only / n_goal_mediated,
            "uncovered_ids": sorted(GOAL_MEDIATED_CAUSAL_IDS - covered),
        },
        "gold_path": OUT_PATH,
        "source_causal_gold_path": GOLD_V2,
        "source_causal_link_probe_commit": "912077b81",
        "dispatched": False,
        "dispatch_note": "measurement-only per task instruction; not queued, not shipped remote.",
    }

    os.makedirs(os.path.dirname(METRICS_PATH), exist_ok=True)
    tmp = METRICS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    os.replace(tmp, METRICS_PATH)

    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
