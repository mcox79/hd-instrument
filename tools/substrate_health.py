#!/usr/bin/env python
"""substrate_health.py -- THE single DERIVED view of substrate health + the maintenance dashboard.

Owner 2026-09-10 ("we don't yet have a robust process that ensures the substrate is optimally managed and
evaluated ... you are strategy, own this project"). The substrate's state was spread across STATUS.md,
INTEGRATION_LEDGER.md, bf_status_registry.jsonl, WIRING_MAP.md, CROSS_SOLUTION_IMPROVEMENT_MAP.md and
KNOWLEDGE_ASSET_REGISTER.md -- so "is it healthy / what's next" had no one answer. This DERIVES the answer from
disk on every run (nothing hand-maintained here -> it cannot rot), and prints TOP ISSUES worst-first + the
consistency GATES that must hold. It is the health half of the process; the plan half is
notes/SUBSTRATE_PROCESS_AND_ROADMAP.md.

    python tools/substrate_health.py            full report
    python tools/substrate_health.py --gaps     only the failing gates + top issues
    python tools/substrate_health.py --check     exit 1 if any gate FAILS (for a pre-flight / cron)

Read-only. No writes. Degrades gracefully (a missing input is reported, never a crash)."""
import ast
import json
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def _load_registry():
    path = os.path.join(REPO, "notes", "bf_status_registry.jsonl")
    rows = []
    try:
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    except OSError:
        pass
    return rows


def _live_imports():
    """The organs situation_reader.py directly imports (the load-bearing live set)."""
    imp = set()
    try:
        src = open(os.path.join(REPO, "hdlab", "situation_reader.py"), encoding="utf-8").read()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("hdlab."):
                imp.add("hdlab/" + node.module.split("hdlab.", 1)[1].split(".")[0] + ".py")
            elif isinstance(node, ast.Import):
                for n in node.names:
                    if n.name.startswith("hdlab."):
                        imp.add("hdlab/" + n.name.split("hdlab.", 1)[1].split(".")[0] + ".py")
    except (OSError, SyntaxError):
        pass
    return {m for m in imp if os.path.exists(os.path.join(REPO, m))}


def _board_aggregate():
    """The most-recent board aggregate on disk + its age (days)."""
    best = None
    for name in ("exp_situation_model_qa_modern_v1", "exp_situation_model_qa_modern_v1_selftest"):
        mp = os.path.join(REPO, "data", name, "metrics.json")
        if os.path.exists(mp):
            try:
                d = json.load(open(mp, encoding="utf-8"))
                agg = d.get("aggregate_19c_free") or (d.get("aggregate") or {})
                # the board writes the aggregate accuracy under "model_acc" (fall back to "model" for older dumps)
                val = (agg.get("model_acc") or agg.get("model")) if isinstance(agg, dict) else agg
                age = (time.time() - os.path.getmtime(mp)) / 86400.0
                if val is not None and (best is None or age < best[2]):
                    best = (name, val, age)
            except Exception:
                pass
    return best


def _bf_update_bearing(slug):
    """True if this problem folder carries a BF component update (a BF side-doc, or an AUDIT UPDATE in SOLVED.md)."""
    d = os.path.join(REPO, "notes", "problems", slug)
    try:
        for fn in os.listdir(d):
            up = fn.upper()
            if ("BF_AUDIT" in up or "UPSTREAM_BF" in up or "UPSTREAM_CHAIN_BF" in up
                    or "COMPONENT_REGISTER" in up):
                return True
        sp = os.path.join(d, "SOLVED.md")
        if os.path.exists(sp):
            if "AUDIT UPDATE" in open(sp, encoding="utf-8", errors="ignore").read():
                return True
    except OSError:
        pass
    return False


def _bf_ledger_missing(in_flight_slugs):
    """In-review submissions that carry a BF component update but are NOT represented in the BF ledger."""
    path = os.path.join(REPO, "notes", "BF_COMPONENT_UPDATE_LEDGER.md")
    try:
        ledger = open(path, encoding="utf-8").read()
    except OSError:
        return None  # ledger absent -> reported separately, not a per-slug miss
    missing = []
    for slug in in_flight_slugs:
        if _bf_update_bearing(slug) and slug[:34] not in ledger:
            missing.append(slug)
    return missing


def main(argv):
    gaps_only = "--gaps" in argv
    check = "--check" in argv
    import tools.problem_ledger as pl

    reg = _load_registry()
    by_status = {}
    notbf = []
    for e in reg:
        by_status[e["status"]] = by_status.get(e["status"], 0) + 1
        if e["status"] == "NOT_BF":
            notbf.append(e["module"].replace("hdlab/", "").replace(".py", ""))

    rows = pl.scan()
    owner_done_backlog = [r["slug"] for r in rows if not r["integrated"]
                          and pl.load_owner(r["slug"]).get("verdict") == "DONE"]
    in_flight = [(r.get("priority"), r["state"], r["slug"]) for r in rows
                 if not r["integrated"] and r["state"] in ("PARTIAL", "SOLVED")
                 and pl.load_owner(r["slug"]).get("verdict") != "DONE"]
    assignable = sorted([(r.get("priority") or 99, r["slug"]) for r in rows
                         if not r["integrated"] and r["state"] == "OPEN"])
    n_integrated = sum(1 for r in rows if r["integrated"])

    live = _live_imports()
    reg_mods = {e["module"] for e in reg}
    untagged = sorted(m for m in live if m not in reg_mods)

    board = _board_aggregate()

    # STATUS.md freshness
    status_age = None
    sp = os.path.join(REPO, "notes", "STATUS.md")
    if os.path.exists(sp):
        status_age = (time.time() - os.path.getmtime(sp)) / 86400.0

    # --- GATES (must hold) ---
    gates = []
    gates.append(("every live situation_reader import is BF-tagged", not untagged,
                  "" if not untagged else "UNTAGGED: " + ", ".join(untagged)))
    ranked = [(r["priority"], r["slug"]) for r in rows if r.get("priority") is not None]
    dupes = sorted({p for p, _ in ranked if [q for q, _ in ranked].count(p) > 1})
    gates.append(("open-problem priorities are unique", not dupes,
                  "" if not dupes else "DUP priorities: %s" % dupes))
    gates.append(("owner-DONE fold-in backlog is empty", not owner_done_backlog,
                  "" if not owner_done_backlog else "%d awaiting fold-in: %s" % (len(owner_done_backlog), owner_done_backlog)))
    gates.append(("STATUS.md is fresh (<2 days)", status_age is not None and status_age < 2.0,
                  "" if (status_age is not None and status_age < 2.0) else "age=%.1fd" % (status_age or 99)))
    bf_missing = _bf_ledger_missing([sl for _, _, sl in in_flight])
    gates.append(("in-review BF-bearing submissions are tracked in BF_COMPONENT_UPDATE_LEDGER", not bf_missing,
                  "" if not bf_missing else "MISSING from BF ledger: %s" % [s[:34] for s in bf_missing]))
    n_fail = sum(1 for _, ok, _ in gates if not ok)

    out = []
    out.append("=" * 78)
    out.append("SUBSTRATE HEALTH  (derived from disk; git log + the notes OUTRANK recollection)")
    out.append("=" * 78)
    if not gaps_only:
        out.append("BRAIN-FOUNDATIONAL: %d organs tagged | %s" % (
            len(reg), " ".join("%s=%d" % (k, by_status[k]) for k in ("BF", "BF_SPIRIT", "NOT_BF", "BF_UNPINNED", "BF_UNVERIFIED") if by_status.get(k))))
        if notbf:
            out.append("  NOT_BF (defects) -> resolution:")
            rmap = {r["slug"]: r for r in rows}
            # map organs to their fix problems (best-effort by keyword)
            fixmap = {
                "pos_tagger": "the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse",
                "arc_parser": "the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse",
                "arceager_parser": "the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse",
                "arc_labeler": "the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse",
                "parse_confidence": "the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse",
                "commonnoun_binder": "the_common_noun_binder_is_string_identity_not_the_brains_content_addressable_typed_coref",
                "force_dynamics_valence": "harm_help_valence_is_a_fitted_verb_list_not_the_substrates_force_dynamic_arithmetic",
            }
            for o in notbf:
                slug = fixmap.get(o)
                if slug and slug in rmap:
                    r = rmap[slug]; v = pl.load_owner(slug).get("verdict", "")
                    out.append("    %-24s -> %s [%s, owner=%s]" % (o, slug[:34], r["state"], v or "-"))
                else:
                    out.append("    %-24s -> (dead/superseded or no mapped problem)" % o)
        out.append("INTEGRATION:")
        out.append("  owner-DONE awaiting fold-in : %d  %s" % (len(owner_done_backlog), owner_done_backlog or ""))
        out.append("  in-flight (awaiting review): %d  %s" % (len(in_flight), [(p, s, sl[:34]) for p, s, sl in in_flight]))
        out.append("  assignable OPEN (fleet)    : %d  %s" % (len(assignable), [(p, sl[:34]) for p, sl in assignable]))
        out.append("  integrated (lifetime)      : %d" % n_integrated)
        out.append("BOARD (eval): %s" % (
            "aggregate=%.4f  (%s, %.1fd old)" % (board[1], board[0], board[2]) if board else "no metrics.json on disk -- run --self-test"))
        out.append("")
    out.append("CONSISTENCY GATES:")
    for name, ok, detail in gates:
        out.append("  [%s] %s%s" % ("OK" if ok else "FAIL", name, ("  <- " + detail) if detail else ""))
    # TOP ISSUES worst-first
    issues = []
    for name, ok, detail in gates:
        if not ok:
            issues.append("GATE FAIL: %s (%s)" % (name, detail))
    if owner_done_backlog:
        issues.append("INTEGRATE: %d owner-DONE awaiting fold-in -> integrate now" % len(owner_done_backlog))
    if by_status.get("NOT_BF"):
        pend = [o for o in notbf if o not in ("scene_segment",)]
        issues.append("BF: %d NOT_BF organs remain (%d have fleet solutions in review; the rest await a fix/prune)" % (by_status["NOT_BF"], len(pend)))
    if in_flight:
        issues.append("REVIEW: %d solver submissions await OWNER review (owner's move)" % len(in_flight))
    if not assignable:
        issues.append("FLEET: 0 assignable OPEN problems -> post the next roadmap items (see SUBSTRATE_PROCESS_AND_ROADMAP.md)")
    if board and board[2] > 3:
        issues.append("EVAL: board aggregate is %.1f days old -> re-run --run for a fresh trend point" % board[2])
    out.append("")
    out.append("TOP ISSUES (worst-first):")
    if issues:
        for i, s in enumerate(issues, 1):
            out.append("  %d. %s" % (i, s))
    else:
        out.append("  (none -- all gates hold, no backlog)")
    out.append("=" * 78)
    print("\n".join(out))
    if check and n_fail:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
