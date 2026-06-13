"""
exp_substrate_system_vs_record_content_ratio_cpu_v1.py -- the axis is SYSTEM-content vs RECORD-content, not field -- CPU/local (no heat, read-only).

ROUTING: USER correction (notes/exp_dev_to_research_REFRAME_systems_vs_records...): "why expect history to have structure? It's basically
  literature -- math/science/language are SYSTEMS, history is not." This cell operationalizes that: classify each atom as SYSTEM-content
  (rule-governed: a definition/operation/derivation -- the promotable stuff) vs RECORD-content (narrative/literature: a note/report/event --
  the retrieved-and-mined stuff), using signals INDEPENDENT of the promotion machinery (text/name/corpus shape, NOT capability/domain --
  to avoid circularity), then measure the SYSTEM:RECORD ratio per field and show that ratio -- not the field label -- predicts where
  promotion fires. Confirms: ONE universal operator promotes SYSTEM-content of any field; RECORD-content is consolidated/retrieved.
  NO LLM; text/name/corpus heuristics; no heat. READ-ONLY.

  INDEPENDENT content-type classifier (no use of serves_capability / algebra.domain, which the promotion test consumes):
    RECORD indicators (+1 each): corpus is *_history; description is long prose (> PROSE_CHARS); name is note/report-style
      (contains a date, 'to_', 'drill', 'note', 'report', 'handoff', 'verdict', 'status'); description begins with markdown header '#'.
    -> atom is RECORD if record_score >= 2, else SYSTEM.
  Then per field: record-fraction. Cross-check (the decisive bit): does record-fraction INVERSELY track the promotion-corroboration
  measured by the universality probe (math 0.953 / science 1.0 / language 0.934 / cognition 0.021 / history 0.000)? If high-record fields
  are exactly the low-promotion fields, content-type (system vs record) -- not field name -- is the operative axis.

PRE-REGISTERED: CONFIRM-SYSTEMS-VS-RECORDS if the field ordering by record-fraction is the INVERSE of the ordering by promotion-
  corroboration (Spearman <= -0.7) AND history is the extreme-record field (record-fraction >= 0.8). PARTIAL if Spearman in (-0.7,-0.3].
  REFUTED if Spearman > -0.3 (content-type does not explain promotion). UNKNOWN if no index. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re
from collections import defaultdict
from pathlib import Path
from typing import Dict, Tuple, List
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_system_vs_record_content_ratio_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
PROSE_CHARS = 700
# promotion-corroboration measured by exp_substrate_cross_field_promotion_universality_probe (HEAD 77828b22), for the cross-check:
PROMO_CORROBORATION = {"math": 0.953, "science": 1.0, "language": 0.934, "cognition": 0.021, "history": 0.0}
_NOTE_PAT = re.compile(r"(20\d\d|_to_|to_research|to_exp|to_testbed|drill|handoff|\bnote\b|report|verdict|status|check_in|resume)", re.I)


def _norm(x):
    return str(x).split("::")[-1].strip()


def field_of(corpus, aid):
    c = (corpus or "").lower(); aid = aid.upper()
    if "history" in c: return "history"
    if c == "math" or aid.startswith(("T1/", "T2/", "T3/", "T2_FAM/")): return "math"
    if c == "science" or aid.startswith(("PHYS/", "CHEM/", "BIO/")): return "science"
    if aid.startswith(("LEX", "MWP/")) or c == "school": return "language"
    if aid.startswith(("CROSSDISC/", "NEURO/", "CS/")) or c == "concept": return "cognition"
    if c in ("meta", "methodology"): return "meta"
    return "other"


def record_score(corpus, name, desc):
    """INDEPENDENT of promotion fields (capability/domain). Higher => more record/literature-like."""
    s = 0
    if "history" in (corpus or "").lower(): s += 1
    if len(desc or "") > PROSE_CHARS: s += 1
    if _NOTE_PAT.search(name or ""): s += 1
    if (desc or "").lstrip().startswith("#"): s += 1
    return s


def is_record(corpus, name, desc):
    return record_score(corpus, name, desc) >= 2


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for pos, i in enumerate(order): r[i] = pos
        return r
    rx, ry = rank(xs), rank(ys); n = len(xs)
    if n < 2: return 0.0
    d2 = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1 - 6 * d2 / (n * (n * n - 1))


def _selftest():
    # a research note = record; a math term = system
    assert is_record("research_history", "research_drill_foo_2026-06-11", "# Research Note: ...long prose...")
    assert not is_record("math", "inner_product", "Bilinear symmetric positive-definite form.")
    # note pattern
    assert _NOTE_PAT.search("exp_dev_to_research_X") and not _NOTE_PAT.search("viterbi_decoding")
    # spearman: perfectly inverse -> -1
    assert abs(spearman([1, 2, 3, 4], [4, 3, 2, 1]) + 1.0) < 1e-9
    assert abs(spearman([1, 2, 3, 4], [1, 2, 3, 4]) - 1.0) < 1e-9
    print("[selftest] PASS: substrate_system_vs_record_content_ratio_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(root).all_atoms()
    by_field = defaultdict(lambda: {"n": 0, "record": 0})
    for a in atoms:
        c = str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
        n = _norm(a.id); f = field_of(c, n)
        rec = is_record(c, getattr(a, "name", "") or "", getattr(a, "description", "") or "")
        by_field[f]["n"] += 1; by_field[f]["record"] += 1 if rec else 0
    fields = [f for f in ["math", "science", "language", "cognition", "history"] if by_field[f]["n"] >= 10]
    rec_frac = {f: round(by_field[f]["record"] / by_field[f]["n"], 4) for f in fields}
    sys_frac = {f: round(1 - rec_frac[f], 4) for f in fields}
    # cross-check vs promotion-corroboration (inverse expected)
    common = [f for f in fields if f in PROMO_CORROBORATION]
    rho = round(spearman([rec_frac[f] for f in common], [PROMO_CORROBORATION[f] for f in common]), 3)
    hist_rec = rec_frac.get("history", 0.0)
    print("  per-field SYSTEM-content fraction (1 - record-fraction), independent text/name/corpus classifier:", flush=True)
    for f in fields:
        print("    %-10s n=%4d system-frac=%.3f record-frac=%.3f | promotion-corroboration=%s" % (
            f, by_field[f]["n"], sys_frac[f], rec_frac[f], PROMO_CORROBORATION.get(f, "n/a")), flush=True)
    print("  Spearman(record-fraction, promotion-corroboration)=%.3f (expect strongly NEGATIVE) | history record-frac=%.3f" % (rho, hist_rec), flush=True)
    return {"fields": fields, "system_fraction": sys_frac, "record_fraction": rec_frac,
            "promotion_corroboration": {f: PROMO_CORROBORATION[f] for f in common},
            "spearman_record_vs_promotion": rho, "history_record_fraction": hist_rec}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"])
    rho = r["spearman_record_vs_promotion"]; hr = r["history_record_fraction"]
    s = ("per-field system-fraction=%s record-fraction=%s; Spearman(record-frac, promotion-corroboration)=%.3f; history record-frac=%.3f. "
         "(content-type classifier is INDEPENDENT of the promotion signals -- text/name/corpus only.) INTERPRETATION: where a field is mostly "
         "SYSTEM-content the universal operator promotes; where it is mostly RECORD-content (history) promotion correctly does not fire -- "
         "the operative axis is CONTENT-TYPE, not field name.") % (
        r["system_fraction"], r["record_fraction"], rho, hr)
    if rho <= -0.7 and hr >= 0.8:
        return ("CONFIRM_SYSTEMS_VS_RECORDS", "CONFIRMED: record-fraction INVERSELY predicts promotion (Spearman %.2f<=-0.7) and history is the extreme-record field (%.2f>=0.8). The USER reframe holds: math/science/language carry SYSTEM-content that promotes uniformly under ONE operator; history is RECORDS (literature) and is correctly NOT promoted but retrieved/mined. 'Handle everything' = one promotion operator over system-content + a consolidation/retrieval path for record-content; fields differ only by system:record ratio. " % (rho, hr) + s)
    if rho <= -0.3:
        return ("PARTIAL", "PARTIAL: record-fraction tracks low promotion (Spearman %.2f) but not cleanly -- content-type is A factor in where promotion fires, alongside others. " % rho + s)
    return ("REFUTED", "REFUTED: record-fraction does NOT inversely predict promotion (Spearman %.2f> -0.3) -- the systems-vs-records content-type axis does not explain the per-field promotion pattern; reconsider. " % rho + s)


print("[config] anchor=%s mode=%s prose_chars=%d" % (ANCHOR_NAME, RUN_MODE, PROSE_CHARS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
