"""Scaffold-free witness for the TWO board arms that make this session's landed brain-foundational fixes
board-visible (exp_situation_model_qa_modern_v1):

  state_closure     -- hdlab.state_register.incompatible now derives antonymy from WordNet (fix fee9337a1):
                       multi-clause state CLOSURE on the CONSTRUCTED n=25 gold. LIVE (WordNet-derived) beats
                       the HAND-LIST-ONLY floor + the info-free scrambled-antonymy twin + always-persist,
                       CI-separated, at a bounded honest OVER-CLOSE cost.
  affect_harm_help  -- hdlab.context_grounded_valence now decides harm/help by force dynamics (fix 406fa9dd7):
                       the SELF-AUTHORED balanced n=36 modern gold. FORCE-DYNAMICS beats the retired
                       closed-list + all-NEUTRAL majority + the scrambled-lexicon twin, CI-separated, with
                       0 false positives, and the LIVE reader's affect == the decision-level FD acc (wired).

Recomputes each arm from SOURCE (the arms reuse the solver cells' own gold + decision/closure machinery; no
landed-metrics read; this witness writes nowhere). If an arm degrades (asset/runtime unavailable -> model_acc
None) the relevant block SKIPs (asset-less safe, the established pattern). ~50s.
Run: .venv/Scripts/python.exe verification/test_board_state_closure_and_affect_harm_help.py
"""
from __future__ import annotations
import os, sys
_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

P = F = 0


def ok(cond, name, detail=""):
    global P, F
    print(("  PASS " if cond else "  FAIL ") + name + ("  [%s]" % detail if detail else ""))
    P += bool(cond); F += (not cond)


def check_state_closure():
    from experiments.exp_situation_model_qa_modern_v1 import board_state_closure_dimension
    row, _det = board_state_closure_dimension()
    if row.get("model_acc") is None:
        print("SKIP state_closure: gold/organ unavailable (arm degraded) -- %s"
              % row.get("error", row.get("population")))
        return
    import experiments.exp_state_closure_wordnet_v1 as S
    print("\nSTATE-CLOSURE (constructed n=%d, %d antonym should-close + %d co-state keep-open)"
          % (row["n"], len(S._CLOSURE_ANTONYM), len(S._CLOSURE_COSTATE)))
    print("  live(WordNet)=%.4f  hand-only=%.4f  persist=%.4f  twin=%.4f  over_close_cost=%+.4f"
          % (row["model_acc"], row["floor_accs"]["hand_list_only_closure"],
             row["floor_accs"]["always_persist"], row["twin_acc"], row["over_close_cost"]))
    print("  live-hand %s  live-twin %s  live-persist %s"
          % (row["model_minus_strongest"], row["model_minus_twin"], row["model_minus_persist"]))

    ok(row["strongest_floor_name"] == "hand_list_only_closure",
       "strongest floor is the HAND-LIST-ONLY closure", row["strongest_floor_name"])
    ok(row["ci_sep_over_strongest"] and row["model_minus_strongest"][0] > 0,
       "LIVE WordNet closure beats hand-list-only CI-sep", "d=%s" % row["model_minus_strongest"])
    ok(row["ci_sep_over_twin"] and row["twin_acc"] < row["model_acc"],
       "scrambled-antonymy twin LOSES CI-sep", "d=%s" % row["model_minus_twin"])
    ok(row["ci_sep_over_persist"] and row["model_minus_persist"][0] > 0,
       "beats always-persist floor CI-sep", "d=%s" % row["model_minus_persist"])
    # the landed WordNet wire IS live (closes wet/dry that the hand list misses)
    ok(row["live_wordnet_closure_wired"] is True,
       "landed WordNet antonymy is LIVE (wet/dry closes live, not in hand list)")
    ma = row["by_arm"]["model_live_wordnet"]["antonym_recall"]
    ha = row["by_arm"]["hand_list_only_floor"]["antonym_recall"]
    ok(ma > ha, "LIVE recovers antonym closures the hand list misses", "model %.4f > hand %.4f" % (ma, ha))
    # the over-close cost is a real but BOUNDED honesty cost (declared; not hidden)
    ok(0.0 <= row["over_close_cost"] < 0.30,
       "over-close cost is bounded + reported (WordNet noise)", "%+.4f %s"
       % (row["over_close_cost"], row["lexicon_probe"]["model_false_fires"]))
    ok("CONSTRUCTED" in row["population"] and row.get("informational") is True,
       "labelled CONSTRUCTED / informational (not a headline claim)")
    # magnitude band (SOLVED: live 1.00 vs hand 0.44, +0.56)
    ok(row["model_acc"] >= 0.96 and abs(row["strongest_floor"] - 0.44) < 0.06,
       "reproduces SOLVED band (live ~1.00, hand ~0.44)",
       "%.4f / %.4f" % (row["model_acc"], row["strongest_floor"]))


def check_affect_harm_help():
    from experiments.exp_situation_model_qa_modern_v1 import board_affect_harm_help_dimension
    row, _det = board_affect_harm_help_dimension()
    if row.get("model_acc") is None:
        print("SKIP affect_harm_help: gold/reader unavailable (arm degraded) -- %s"
              % row.get("error", row.get("population")))
        return
    print("\nAFFECT harm/help (self-authored balanced n=%d: 12 HARM / 12 HELP / 12 NEUTRAL)" % row["n"])
    print("  force-dynamics=%.4f  closed-list=%.4f  majority=%.4f  twin=%.4f"
          % (row["model_acc"], row["floor_accs"]["retired_closed_list"],
             row["floor_accs"]["majority_all_neutral"], row["twin_acc"]))
    print("  FD-closed %s  FD-majority %s  FD-twin %s   by_class=%s (closed=%s)"
          % (row["model_minus_strongest"], row["model_minus_majority"], row["model_minus_twin"],
             row["by_class"], row["closed_list_by_class"]))

    ok(row["ci_sep_over_strongest"] and row["model_minus_strongest"][0] > 0,
       "force-dynamics beats retired closed-list CI-sep", "d=%s" % row["model_minus_strongest"])
    ok(row["ci_sep_over_majority"] and row["model_minus_majority"][0] > 0,
       "force-dynamics beats all-NEUTRAL majority CI-sep", "d=%s" % row["model_minus_majority"])
    ok(row["ci_sep_over_twin"] and row["twin_acc"] < row["model_acc"],
       "scrambled-lexicon twin LOSES CI-sep", "d=%s" % row["model_minus_twin"])
    ok(row["zero_false_positives"] is True,
       "0 false positives (FD never labels a NEUTRAL scene HARM/HELP)", str(row["false_positives_on_neutral"]))
    # the closed list is STRUCTURALLY unable to emit HELP (0/12); FD recovers it
    ok(row["closed_list_by_class"]["HELP"].startswith("0/") and not row["by_class"]["HELP"].startswith("0/"),
       "closed-list can't emit HELP (0/12); FD recovers HELP",
       "FD %s vs closed %s" % (row["by_class"]["HELP"], row["closed_list_by_class"]["HELP"]))
    # the mechanism is WIRED, not an island: the LIVE reader's affect == the decision-level FD acc
    lc = row["live_reader_crosscheck"]
    ok(isinstance(lc, dict) and lc.get("live_matches_decision") is True,
       "LIVE reader affect == decision-level FD acc (mechanism is wired)",
       "live=%s decision=%s" % (lc.get("live_reader_acc"), row["model_acc"]))
    ok("SELF-AUTHORED" in row["population"] and row.get("informational") is True,
       "labelled SELF-AUTHORED / informational (not a headline claim)")
    ok(abs(row["model_acc"] - 0.7778) < 0.02 and abs(row["strongest_floor"] - 0.3333) < 0.02,
       "reproduces SOLVED band (FD ~0.778 vs closed/majority ~0.333)",
       "%.4f / %.4f" % (row["model_acc"], row["strongest_floor"]))


def main():
    check_state_closure()
    check_affect_harm_help()
    print("\n[%d PASS / %d FAIL]" % (P, F))
    return 1 if F else 0


if __name__ == "__main__":
    sys.exit(main())
