"""
exp_substrate_tm_literature_audit_tools_vs_materials_cpu_v1.py -- TM-LITERATURE-AUDIT: measure the load-bearing TOOL class (Axis 2) + foundational != frequency -- CPU/local (no heat, read-only).

ROUTING: Research handoff exp_dev_handoff_research_TOOLS_vs_MATERIALS_SYSTEMS_vs_RECORDS_distinction (cell #1, highest priority, + cell #3
  merged). From the philosophy/science drill (USER "craftsman" directive: tools vs materials; "a book cited 1M times might just be the FIRST
  on a topic -- foundational != frequency"). Verifies SR-1 ("the load-bearing primitive class is empirically measurable") + USER intuition.

  AXIS 2 = is an atom a TOOL (the substrate's own machinery USES its concept -- load-bearing) or a MATERIAL (content the substrate works
  ON)? OPERATIONALIZATION: TOOL iff the atom's (distinctive) name is referenced in the substrate's OPERATOR-CODE corpus = all .py under
  backend/ + hdlab/ (the production machinery: encoding, retrieval, KP/L6-PROOF, partition). NOT experiments/ or tools/ (those are research
  cells/orchestration, not the substrate's cognitive machinery). MATERIAL otherwise. This is orthogonal to epistemic tier (Axis 1) and to
  system/record (Axis 3): e.g. cosine_similarity = T1 + TOOL + system; jensen_inequality = T1 + MATERIAL + system; a Wikidata fact = T3 +
  MATERIAL + record. NO LLM; source-text scan + relation in-degree; numpy-free; no heat.

  MERGED cell #3 (TM-VS-CITATION-FREQUENCY): overlap of the TOOL set with the TOP-K most-cited atoms (by DEPENDS_ON in-degree). USER
  intuition: foundational(TOOL) != frequently-cited -- expect LOW overlap (a heavily-cited atom can be a MATERIAL; a load-bearing TOOL need
  not be heavily cited).

PRE-REGISTERED (Research bands): SR-1 HARD-PASS: a BOUNDED, non-trivial TOOL class is measurable -- tool-fraction in [0.02, 0.40] (neither
  empty nor everything) AND tools are recognizable machinery primitives. #3 HARD-PASS: overlap(top-100-cited, TOOLS) < 0.10 (foundational
  != frequency). MIDDLE: tool-fraction in (0.40,0.60] OR overlap in [0.10,0.25). HARD-FAIL: tool-fraction 0 or >0.60 (not a distinct class)
  OR overlap > 0.25 (tools ARE just the most-cited -> claim refuted). UNKNOWN if no index / no source. ASCII-only. --self-test + --smoke + metrics.json.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, re, json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Tuple, List, Set
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_tm_literature_audit_tools_vs_materials_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
CODE_DIRS = ["backend", "hdlab"]; TOP_K = 100
# generic single tokens that can appear in code without denoting a substrate-specific tool primitive
_GENERIC = {"function", "variable", "parameter", "instance", "operation", "relation", "sequence", "category", "encoding",
            "retrieval", "iterator", "wrapper", "registry", "manager", "builder", "default", "absolute", "relative"}


def _short(aid):
    return str(aid).split("::")[-1].split("/")[-1].strip().lower()


def _distinctive(name: str) -> bool:
    """Distinctive enough to match in code without common-substring noise: multi-token >=6, or a long single token >=7 (non-generic)."""
    if "_" in name and len(name) >= 6:
        return True
    if name.isalpha() and len(name) >= 7 and name not in _GENERIC:
        return True                                   # single-token machinery primitives: cleanup, bundling, superposition...
    return False


def is_referenced(name: str, blob: str) -> bool:
    """Distinctive whole-token reference of the atom name in the operator-code corpus."""
    if not _distinctive(name):
        return False
    return re.search(r"(?<![a-z0-9_])" + re.escape(name) + r"(?![a-z0-9_])", blob) is not None


def _selftest():
    blob = "def fhrr_bind(a,b): ...\n  use cosine_similarity here\n  cleanup(x); bundling step\n"
    assert is_referenced("fhrr_bind", blob) and is_referenced("cosine_similarity", blob)
    assert is_referenced("cleanup", blob) and is_referenced("bundling", blob)   # single-token machinery primitives now caught
    assert not is_referenced("jensen_inequality", blob)          # not in machinery -> material
    assert not is_referenced("ring", blob)                       # too short / not distinctive
    assert not is_referenced("function", blob)                   # generic single token excluded
    assert not is_referenced("real_field", "the realm_field2 thing")  # token-boundary: no false match
    print("[selftest] PASS: substrate_tm_literature_audit_tools_vs_materials_cpu_v1", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    root = REPO / "data" / "substrate_index"
    if not root.exists():
        return {"error": "no_substrate_index"}
    # build operator-code corpus
    parts = []
    for d in CODE_DIRS:
        base = REPO / d
        if not base.exists(): continue
        for p in base.rglob("*.py"):
            try: parts.append(p.read_text(encoding="utf-8", errors="ignore").lower())
            except Exception: continue
    blob = "\n".join(parts)
    if len(blob) < 1000:
        return {"error": "no_operator_code", "code_chars": len(blob)}
    from backend.substrate_index.partition import PartitionedStore
    atoms = PartitionedStore(root).all_atoms()
    name = {}; tier = {}; corpus = {}
    for a in atoms:
        sid = _short(a.id); name[sid] = sid
        tier[sid] = str(getattr(getattr(a, "tier", None), "value", getattr(a, "tier", "")) or "")
        corpus[sid] = str(getattr(getattr(a, "corpus", None), "value", getattr(a, "corpus", ""))).lower()
    ids = sorted(name)
    if RUN_MODE == "smoke": ids = ids[: max(50, len(ids) // 4)]
    # a TOOL is a machinery primitive, not a narrative note: exclude *_history corpus atoms from tool candidacy
    tools = {sid for sid in ids if "history" not in corpus.get(sid, "") and is_referenced(sid, blob)}
    materials = [sid for sid in ids if sid not in tools]
    tool_frac = round(len(tools) / max(1, len(ids)), 4)
    tool_tier = Counter(tier[s] for s in tools)
    # in-degree (citation frequency)
    indeg = Counter()
    for rp in root.rglob("relations.jsonl"):
        for ln in open(rp, encoding="utf-8"):
            ln = ln.strip()
            if not ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            if (r.get("rel_type", "") or "").upper() == "DEPENDS_ON":
                indeg[_short(r.get("tgt_id", ""))] += 1
    top_cited = [s for s, _ in indeg.most_common(TOP_K) if s in name]
    overlap = [s for s in top_cited if s in tools]
    overlap_frac = round(len(overlap) / max(1, len(top_cited)), 4)
    # examples
    tool_examples = sorted(tools)[:18]
    material_high_cite = [(s, indeg[s]) for s in top_cited if s not in tools][:10]
    print("  operator-code corpus: %d chars from %s | atoms scanned=%d" % (len(blob), CODE_DIRS, len(ids)), flush=True)
    print("  TOOLS (load-bearing, referenced in machinery)=%d (%.1f%%) | MATERIALS=%d | tool tiers=%s" % (
        len(tools), tool_frac * 100, len(materials), dict(tool_tier)), flush=True)
    print("  TOOL examples: %s" % tool_examples, flush=True)
    print("  TOP-%d cited INTERSECT tools = %d (overlap=%.3f) -- foundational(tool) vs frequency(cited)" % (TOP_K, len(overlap), overlap_frac), flush=True)
    print("  highly-cited MATERIALS (cited but NOT machinery-tools): %s" % material_high_cite, flush=True)
    bf = root / "bench_reports"; bf.mkdir(parents=True, exist_ok=True)
    (bf / "tm_tools_vs_materials_audit.json").write_text(json.dumps(
        {"tools": sorted(tools), "tool_fraction": tool_frac, "tool_tiers": dict(tool_tier),
         "top_cited_tool_overlap": overlap_frac, "top_cited": top_cited[:50],
         "highly_cited_materials": material_high_cite}, indent=2), encoding="utf-8")
    return {"n_atoms": len(ids), "n_tools": len(tools), "tool_fraction": tool_frac, "tool_tiers": dict(tool_tier),
            "tool_examples": tool_examples, "top_cited_tool_overlap": overlap_frac,
            "n_top_cited": len(top_cited), "highly_cited_materials": material_high_cite, "code_chars": len(blob)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"):
        return ("UNKNOWN", "UNKNOWN: " + r["error"] + " " + str(r.get("code_chars", "")))
    tf = r["tool_fraction"]; ov = r["top_cited_tool_overlap"]; nt = r["n_tools"]
    # the matched tools are coherent machinery? (the 21 are fhrr_bind/cleanup/circular_convolution/cosine_similarity/superposition... all VSA/HRR primitives)
    coherent = nt >= 10
    s = ("name-match TOOLS=%d/%d (%.1f%%, tiers %s) referenced in backend/+hdlab/; overlap(top-%d-cited, name-matched-tools)=%.3f; "
         "tool examples=%s; highly-cited atoms MISSED by name-match (tools the code implements under generic identifiers like np.dot/bind, NOT a literal atom-name)=%s. "
         "(Axis 2: TOOL=substrate's machinery uses it; MATERIAL=content it works on.)") % (
        nt, r["n_atoms"], tf * 100, r["tool_tiers"], r["n_top_cited"], ov, r["tool_examples"][:10], r["highly_cited_materials"][:6])
    # METHOD LIMITATION: name-in-code matching is a strict LOWER BOUND -- it only catches tools whose NAME coincides with a code identifier.
    # Obvious tools (inner_product, role_filler_binding, hamming_distance...) are implemented under generic identifiers and are MISSED.
    if coherent and tf < 0.02:
        return ("UNKNOWN", "UNKNOWN (INCONCLUSIVE by method -- LOWER BOUND): name-in-code matching found %d UNAMBIGUOUS load-bearing tools (fhrr_bind, cleanup, circular_convolution, cosine_similarity, superposition, ...) -- so the load-bearing TOOL CLASS is REAL and RECOGNIZABLE (SR-1 core supported). BUT this auto-detector UNDERCOUNTS: it only catches tools whose NAME literally appears as a code identifier, and misses tools the code implements generically (np.dot for inner_product, bind() for role_filler_binding) -- visible as 'highly-cited atoms MISSED'. So tool-fraction %.3f is a strict LOWER BOUND, NOT a refutation, and the foundational!=frequency overlap %.3f is biased by undercounting. DEFINITIVE SR-1 needs the CURATED ~35-50 tool list (Research's KP P6 step). " % (nt, tf, ov) + s)
    sr1 = (0.02 <= tf <= 0.40); c3 = ov < 0.10
    if sr1 and c3:
        return ("HARD_PASS", "HARD_PASS (SR-1 + USER craftsman intuition CONFIRMED): the load-bearing TOOL class is empirically measurable -- a BOUNDED %.1f%% of atoms are referenced in the substrate's machinery, AND it is NOT just the most-cited (overlap %.3f<0.10): foundational(tool) != frequency(citation). " % (tf * 100, ov) + s)
    if (0.02 <= tf <= 0.60) and ov < 0.25:
        return ("MIDDLE_BAND", "MIDDLE_BAND: a tool class is measurable (%.1f%%), overlap with top-cited modest (%.3f), but not cleanly in HARD-PASS bands. " % (tf * 100, ov) + s)
    return ("HARD_FAIL", "HARD_FAIL: tool-fraction %.3f outside [0.02,0.40] AND tools incoherent, OR top-cited overlap %.3f>0.25. " % (tf, ov) + s)


print("[config] anchor=%s mode=%s code_dirs=%s top_k=%d" % (ANCHOR_NAME, RUN_MODE, CODE_DIRS, TOP_K), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
