"""STEP-B RESEARCH_FINDING atomizer (USER GO research-onboarding; Skunkworks T0-T3 trust-tier + scope-VET).

Walks notes/*.md, classifies genuine research-FINDING notes (deterministic, no-LLM), and builds
kind=research_finding atoms at confidence_tier T2_RESEARCH_SUPPORTED / T3_HYPOTHESIS. Distilled context layer:
queryable but NON-load-bearing (USER: "research can be wrong; only PROVEN fully believed").

SCOPE (Skunkworks STEP-A + scope-VET 2026-06-17):
  INCLUDE: research_* + exp_dev_handoff_research_* (the ~444 BEST-distilled findings: ranked mechanisms + lit
     citations + prereg bands -- NOT work-requests) + drill-outputs + literature/lit_scan + probe-result notes.
  EXCLUDE: bus (_to_) + change_request_* (specs) + STATE/checkpoint/memo/status/resume/witness/ping/ack/TRACKING.

STRUCTURAL GUARD (USER trust-tier as HARD rule): RESEARCH_FINDING carries NO algebra field -> excluded from
  axiom_term -> never a capability current_best_solution unless cert-promoted. Research-being-wrong is SAFE.
  PROMOTION (Skunkworks cert-owner): T3 hypothesis -> experiment -> cert-grade PASS -> T0 (confirmed_by link);
  HARD_FAIL -> REFUTED + KEEP (negative knowledge). DISPLAYED tier T2/T3 is conservative (default-T3 if ambiguous).

DETERMINISTIC NO-LLM (11th rule): claim = note headline; MARKED-SECTION parse (what_found / citations /
  ranked_candidates) via regex on explicit markdown headers (NOT free-text distillation); confidence_tier from
  citation-markers; field/topic tags from keyword match; bears_on = in-store atoms referenced (token-set, no-phantom).

DISCIPLINE (Tier-3 atomizer precedent; helpers imported): DRY-RUN-FIRST + per-batch FRESH-LOAD + os.replace-retry +
  SERIAL + cap_pres(module 6/6) + axiom_term HARD-FAIL gates per batch + LIMIT failsafe + Skunkworks per-batch VET.

Env: HDLAB_ATOMIZE_APPLY=1 apply (default 0 dry-run); HDLAB_ATOMIZE_BATCH=50; HDLAB_ATOMIZE_LIMIT (default 50 dry / all apply).
Run on system python (atomizer deps present; cert-suite-only needs .venv).
"""
from __future__ import annotations
import os
import re
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, Corpus, Tier, AtomKind, RelationType
from atomize_experiment_records import (axiom_term, module_liveness_ok, build_atom_index,
                                        resolve_depends_on, sanitize, sha1_file)

REPO = Path(__file__).resolve().parents[1]
NOTES = REPO / "notes"
SRC_TAG = "STEP_B_research_finding_atomizer_T0_T3_trust_tier_USER_GO_skunkworks_scope_VET"
SESSION = "exp_dev"

# ---- classification (deterministic; Skunkworks scope-VET) ----
STATE_MARKERS = ("state", "checkpoint", "_status", "_memo", "_resume", "_close", "_witness",
                 "_ping", "_ack", "tracking", "director_state", "_health_check", "_cycle_summary")
INCLUDE_MARKERS = ("drill", "literature", "lit_scan", "_finding", "probe", "research_2x", "15_angles", "_lit_")

# ---- field/topic tag vocab (Skunkworks A3 field map) ----
FIELD_KEYWORDS = {
    "composition_depth": ("composition", "compositional", "depth", "l10000", "compose"),
    "reasoning_multihop": ("reasoning", "multihop", "multi_hop", "khop", "k_hop", "hotpot", "inference_chain"),
    "capacity_theory": ("capacity", "scaling", "theory", "bound", "alpha_c", "willshaw"),
    "audit_safety_drift": ("audit", "safety", "drift", "deletion", "kappa", "refuse", "provenance"),
    "encoders_write_rules": ("encoder", "projection", "write_rule", "write-rule", "embedding", "whiten"),
    "lm_tier6_charlm": ("charlm", "char_lm", "tier6", "tier_6", "language_model", "tiny_transformer"),
    "nlp_seq_labeling": ("ner", "pos_tag", "sequence_label", "seq_label", "perceptron", "viterbi", "hmm"),
    "bio_neuro": ("bio", "neuro", "drosophila", "cortical", "hebbian", "spike", "dentate", "mushroom"),
    "sparse_coding": ("sparse", "sparsity", "topk", "top_k", "kenyon"),
    "knowledge_graph": ("knowledge_graph", "wikidata", "conceptnet", "kg_", "triple"),
    "binding_vsa_crt": ("binding", "vsa", "crt", "fhrr", "hrr", "residue", "fractional_power", "role_filler"),
    "attractor_hopfield": ("attractor", "hopfield", "resonator", "modern_hopfield", "softmax_readout"),
    "gating_efficiency": ("gating", "gate", "efficiency", "surprise", "active_inference"),
    "counterfactual_attribution": ("counterfactual", "attribution", "cf_rpe", "cfrpe", "ablation"),
}
TOPIC_KEYWORDS = {
    "drosophila_mb": ("drosophila", "mushroom_body", "mushroom body", "kenyon"),
    "kappa_drift": ("kappa", "drift_detect", "drift detection"),
    "tier6_charlm": ("tier6", "tier_6", "charlm", "char_lm"),
    "deletion_cert": ("deletion_cert", "deletion cert", "negative_knowledge"),
    "modern_hopfield": ("modern_hopfield", "modern hopfield", "ramsauer", "softmax_readout"),
    "composition_l10000": ("l10000", "l_10000", "composition"),
    "held_out_retrieval": ("held_out", "held-out", "generalization", "cross_domain", "cross-domain"),
}
CITATION_RE = re.compile(
    r'(arxiv[:\s]*\d{4}\.\d{4,5}|\bPMC\d{5,}|\bdoi[:\s]|10\.\d{4,}/|\b[A-Z][a-z]+ et al\.?,? \d{4}|\([A-Z][a-z]+,? \d{4}\))')
SECTION_FIND_RE = re.compile(r'^#{1,4}\s.*(found|finding|result|conclusion|takeaway|mechanism)', re.IGNORECASE)
SECTION_CAND_RE = re.compile(r'^#{1,4}\s.*(candidate|anchor|recommend|ranked|next.?step|proposal)', re.IGNORECASE)
# Skunkworks STEP-B ruling-A enhancement: capture PROSE result-lines (251 notes state findings under
# ## Trigger / **Anchor pointer** / prose that the header-only SECTION_FIND_RE misses). Deterministic (11th-rule).
RESULT_LINE_RE = re.compile(
    r'(HARD[_ ]?PASS|HARD[_ ]?FAIL|\bCONFIRMED\b|\bREFUTED\b|\bVALIDATED\b|MIDDLE_BAND|'   # pass/fail verdicts
    r'\d+(?:\.\d+)?\s*(?:x|%|pp)\b|->|'                                                    # x/%/pp ratios + deltas
    r'[=:]\s*-?\d|'                                                                        # a MEASURED value (key=0.x)
    r'\b(?:recall|precision|f1|acc(?:uracy)?|bpc|rmse|auc|p_?deflated)\b\s*[@=:]?\s*-?\d|' # metric WITH a number
    r'\bwe found\b|\bresults? show\b)',                                                    # explicit finding phrase
    re.IGNORECASE)   # NOTE: bare "measured"/"achieves" REMOVED -- they match PLAN/spec lines (precision leak)
# Skunkworks precision-guard: a STRONG result signal (numeric/arrow/pass-fail) lets a line survive even if it also
# reads as a request; a REQUEST line WITHOUT a strong result is DROPPED (so what_found carries findings, not requests).
STRONG_RESULT_RE = re.compile(r'(HARD[_ ]?PASS|HARD[_ ]?FAIL|\bCONFIRMED\b|\bREFUTED\b|\bVALIDATED\b|'
                              r'\d+(?:\.\d+)?\s*(?:x|%|pp)\b|->)', re.IGNORECASE)
REQUEST_RE = re.compile(r'\b(probe|dispatch|please run|should run|request|TODO|next.?step|propose|recommend\w* running|'
                        r'hand.?off|to run|will run|plan to)\b', re.IGNORECASE)


def classify(fname: str) -> bool:
    """True iff fname is a genuine research-FINDING note (deterministic; Skunkworks scope-VET)."""
    low = fname.lower()
    if "_to_" in low:
        return False                                            # coordination bus
    if low.startswith("change_request_"):
        return False                                            # specs, not findings
    if any(mk in low for mk in STATE_MARKERS):
        return False                                            # state/memo/decision-process
    if low.startswith("research_") or low.startswith("exp_dev_handoff_research"):
        return True                                             # research-authored findings + ~444 handoff-distilled
    return any(mk in low for mk in INCLUDE_MARKERS)             # drills / literature / probes


def _ascii(s: str) -> str:
    """ASCII-only normalize (CLAUDE.md): map common unicode punctuation -> ASCII, drop the rest."""
    return (s.replace("—", "--").replace("–", "-").replace("‘", "'").replace("’", "'")
            .replace("“", '"').replace("”", '"').encode("ascii", "ignore").decode()).strip()


def headline_of(text: str) -> str:
    for ln in text.splitlines():
        s = ln.strip().lstrip("#").strip()
        if s:
            return _ascii(s)
    return ""


def section_body(text: str, header_re) -> str:
    """Deterministic marked-section extract: lines under the first header matching header_re until the next header."""
    lines = text.splitlines()
    out, capon = [], False
    for ln in lines:
        if ln.startswith("#"):
            if capon:
                break
            if header_re.match(ln):
                capon = True
            continue
        if capon and ln.strip():
            out.append(ln.strip())
    return _ascii(" ".join(out))[:600]


def capture_findings(text: str) -> str:
    """what_found = header-section (SECTION_FIND_RE) PLUS prose result-lines (RESULT_LINE_RE) -- Skunkworks ruling-A
    enhancement so the 251 prose-finding notes land semantically substantive (the bge index retrieves the finding,
    not just the headline). Deterministic, no-LLM (11th rule)."""
    body = section_body(text, SECTION_FIND_RE)
    prose = []
    for ln in text.splitlines():
        s = ln.strip().lstrip("#*->-").strip()
        if not s or ln.lstrip().startswith("#"):
            continue
        if RESULT_LINE_RE.search(s):
            if REQUEST_RE.search(s) and not STRONG_RESULT_RE.search(s):
                continue   # request/intent line without a strong result -> NOT a finding (precision-guard)
            if s not in prose:
                prose.append(s)
        if len(prose) >= 6:
            break
    combined = " | ".join(x for x in ([body] if body else []) + prose)
    return _ascii(combined)[:700]


def tags_for(blob: str, vocab: dict) -> list:
    low = blob.lower()
    return sorted([t for t, kws in vocab.items() if any(k in low for k in kws)])


def parse_note(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    headline = headline_of(text)
    citations = sorted(set(m.group(0).strip() for m in CITATION_RE.finditer(text)))[:8]
    tier = "T2_RESEARCH_SUPPORTED" if citations else "T3_HYPOTHESIS"   # default-T3 when ambiguous (Skunkworks (c))
    blob = headline + " " + path.name + " " + text[:4000]
    return dict(
        headline=headline,
        confidence_tier=tier,
        citations=citations,
        what_found=capture_findings(text),
        ranked_candidates=section_body(text, SECTION_CAND_RE),
        field_tags=tags_for(blob, FIELD_KEYWORDS),
        topic_tags=tags_for(blob, TOPIC_KEYWORDS),
        text_blob=blob,
    )


def discover():
    notes, dropped = [], 0
    for p in sorted(NOTES.glob("*.md")):
        if not classify(p.name):
            dropped += 1
            continue
        notes.append(p)
    return notes, dropped


def build_spec(path: Path, parsed: dict, all_qids, primitive_targets):
    slug = sanitize(path.stem)[:90]
    local_id = f"RF/{slug}"
    qid = f"{Corpus.CONCEPT.value}::{local_id}"
    bears_on = resolve_depends_on(parsed["text_blob"], primitive_targets, all_qids)  # no-phantom (token-set)
    claim = parsed["headline"][:300] or path.stem
    desc = (f"Research finding ({parsed['confidence_tier']}; NON-load-bearing): {claim} "
            f"Fields {parsed['field_tags'] or 'n/a'}; topics {parsed['topic_tags'] or 'n/a'}; "
            f"citations {len(parsed['citations'])}; bears_on {len(bears_on)}.")
    metadata = dict(
        record_class="research_finding",
        term_class="RESEARCH_KNOWLEDGE_NON_LOAD_BEARING",
        claim=claim,
        source_note=str(path.relative_to(REPO)),
        confidence_tier=parsed["confidence_tier"],
        field_tags=parsed["field_tags"],
        topic_tags=parsed["topic_tags"],
        citations=parsed["citations"],
        what_found=parsed["what_found"],
        ranked_candidates=parsed["ranked_candidates"],
        bears_on=bears_on,
        bears_on_count=len(bears_on),
        promotion_status="UNPROMOTED",     # -> T0 only via cert-grade experiment PASS (Skunkworks cert-owner)
        confirmed_by=None,                 # set on T0 promotion
        provenance=dict(note_sha=sha1_file(path), source_path=str(path.relative_to(REPO)), session_authored=SESSION),
        structural_guard="NO_ALGEBRA_FIELD_excluded_from_axiom_term_never_current_best_unless_cert_promoted",
        eleventh_rule_clean=True,
        deterministic_no_llm=True,
        source=SRC_TAG,
    )
    return dict(id=local_id, qid=qid, corpus=Corpus.CONCEPT, tier=Tier.TIER_NA,
                name=f"RF {claim}"[:120], description=desc[:1200], metadata=metadata, bears_on=bears_on,
                confidence_tier=parsed["confidence_tier"])


def summarize(specs, dropped):
    from collections import Counter
    tc, fc, bc = Counter(), Counter(), Counter()
    edge_total = 0
    for s in specs:
        tc[s["confidence_tier"]] += 1
        for f in s["metadata"]["field_tags"]:
            fc[f] += 1
        bc[s["metadata"]["bears_on_count"]] += 1
        edge_total += s["metadata"]["bears_on_count"]
    print("=" * 80)
    print(f"DISCOVERED: {len(specs)} candidate RESEARCH_FINDING atoms | note files EXCLUDED: {dropped}")
    print(f"  confidence_tier: {dict(tc.most_common())}")
    print(f"  field_tags:      {dict(fc.most_common())}")
    print(f"  bears_on edges total: {edge_total}; per-atom dist: {dict(sorted(bc.items()))}")
    print(f"  atoms with citations (T2): {tc.get('T2_RESEARCH_SUPPORTED', 0)} | conjecture (T3): {tc.get('T3_HYPOTHESIS', 0)}")
    print("=" * 80)


def main():
    apply = os.environ.get("HDLAB_ATOMIZE_APPLY", "0") == "1"
    batch = int(os.environ.get("HDLAB_ATOMIZE_BATCH", "50"))
    limit = int(os.environ.get("HDLAB_ATOMIZE_LIMIT", "1000000" if apply else "50"))
    print(f"[rf-atomizer] mode={'APPLY' if apply else 'DRY-RUN'} batch={batch} limit={limit}", flush=True)

    ps = PartitionedStore(REPO / "data/substrate_index")
    all_qids, primitive_targets, _cap = build_atom_index(ps)
    print(f"[rf-atomizer] in-store: {len(all_qids)} atoms ({len(primitive_targets)} primitive targets) for no-phantom bears_on", flush=True)

    notes, dropped = discover()
    print(f"[rf-atomizer] {len(notes)} finding-notes pass classification; {dropped} excluded (bus/spec/state)", flush=True)

    # SCOPE (Director-lean Option B; Skunkworks cert-owner ruling): "signal" (default) keeps only notes with a
    # finding-signal (what_found OR citations OR ranked_candidates) -> drops borderline request-only notes (881);
    # "broad" keeps every classified note (1229; also SAFE per the non-load-bearing structural guard).
    scope = os.environ.get("HDLAB_RF_SCOPE", "broad").lower()   # Skunkworks RULING = A (broad, 1229); B lost 251 real prose-findings
    specs, skipped, scope_filtered = [], 0, 0
    for p in notes:
        parsed = parse_note(p)
        has_signal = bool(parsed["what_found"] or parsed["citations"] or parsed["ranked_candidates"])
        if scope == "signal" and not has_signal:
            scope_filtered += 1
            continue
        spec = build_spec(p, parsed, all_qids, primitive_targets)
        if ps._store_for(Corpus.CONCEPT).get_atom(spec["id"]) is not None:
            skipped += 1
            continue
        spec["bears_on"] = [b for b in spec["bears_on"] if b in all_qids]   # no-phantom re-assert
        specs.append(spec)
    print(f"[rf-atomizer] scope={scope}: {len(specs)} new specs ({skipped} in-store-skip; "
          f"{scope_filtered} dropped no-finding-signal)", flush=True)
    summarize(specs, dropped)

    if not apply:
        sample = specs[:limit]
        out = REPO / "data" / "atomize_research_findings_dryrun_sample.jsonl"
        with open(out, "w", encoding="utf-8") as f:
            for s in sample:
                f.write(json.dumps(dict(id=s["qid"], name=s["name"], confidence_tier=s["confidence_tier"],
                                        bears_on=s["bears_on"], metadata=s["metadata"]), ensure_ascii=False) + "\n")
        print(f"[rf-atomizer] DRY-RUN sample ({len(sample)}) -> {out.relative_to(REPO)}")
        print("[rf-atomizer] NO substrate mutation. Skunkworks: SCHEMA-VET sample (classification + T2/T3 + no-phantom bears_on + no-algebra).")
        return 0

    # ===== APPLY: per-batch fresh-load + os.replace-retry + per-batch HARD-FAIL gates (cap_pres + axiom_term) =====
    to_ingest = specs[:limit]
    RETRIES = 6
    done = 0
    print(f"[rf-atomizer] APPLY (per-batch fresh-load; concurrent-safe) target={len(to_ingest)} batch={batch}", flush=True)
    for i in range(0, len(to_ingest), batch):
        planned = to_ingest[i:i + batch]
        bnum = i // batch + 1
        applied = False
        for attempt in range(RETRIES):
            psb = PartitionedStore(REPO / "data/substrate_index")
            qids_b = {a.qualified_id for a in psb.all_atoms()}
            chunk = []
            for s in planned:
                if psb._store_for(Corpus.CONCEPT).get_atom(s["id"]) is not None:
                    continue
                s2 = dict(s); s2["bears_on"] = [b for b in s["bears_on"] if b in qids_b]
                chunk.append(s2)
            if not chunk:
                applied = True; break
            pre_t, _ = axiom_term(psb)
            pre_atoms = len(psb.all_atoms()); pre_rels = sum(1 for _ in psb.iter_all_relations())
            edges = 0
            try:
                for s in chunk:
                    psb._store_for(Corpus.CONCEPT).add_atom(Atom(
                        id=s["id"], name=s["name"], corpus=Corpus.CONCEPT, tier=Tier.TIER_NA,
                        kind=AtomKind.RESEARCH_FINDING, description=s["description"],
                        metadata=s["metadata"], solution_history=tuple()))
                for s in chunk:
                    for tgt in s["bears_on"]:
                        psb.add_relation(s["qid"], RelationType.RELATES, tgt, source=SRC_TAG,
                                         note=f"{s['id']} bears_on {tgt} (rf-atomizer)")
                        edges += 1
                psb._store_for(Corpus.CONCEPT)._flush_relations()
            except (PermissionError, OSError) as e:
                print(f"[rf-atomizer] batch {bnum} attempt {attempt+1}: os.replace race ({type(e).__name__}); retry fresh", flush=True)
                continue
            post_t, post_total = axiom_term(psb)
            post_atoms = len(psb.all_atoms()); post_rels = sum(1 for _ in psb.iter_all_relations())
            landed = all(psb._store_for(Corpus.CONCEPT).get_atom(s["id"]) is not None for s in chunk)
            gate_ok = (post_atoms == pre_atoms + len(chunk) and post_rels == pre_rels + edges
                       and post_t == pre_t and module_liveness_ok() and landed)
            print(f"[rf-atomizer] batch {bnum}: +{len(chunk)} atoms +{edges} edges | axiom_term={post_t}/{post_total} "
                  f"cap_pres(mod6/6)={module_liveness_ok()} landed={landed} -> {'OK' if gate_ok else 'HARD_FAIL'}", flush=True)
            if not gate_ok:
                print(f"[rf-atomizer] HARD_FAIL at batch {bnum}: invariant violation. STOPPING.")
                return 1
            done += len(chunk); applied = True; break
        if not applied:
            print(f"[rf-atomizer] batch {bnum}: contended-skipped after {RETRIES} retries (re-invoke to pick up)", flush=True)
    print(f"[rf-atomizer] APPLY DONE: +{done} RESEARCH_FINDING atoms this run. axiom_term + cap_pres gates passed per batch.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
