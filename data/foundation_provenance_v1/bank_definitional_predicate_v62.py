"""BANK the v6.2 definitional-PREDICATE facts into the provenance-tagged store.

READS  data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl   (221 facts, hand-scored
       94% MEANINGFUL / 4% RELATED / 2% NOISE -- notes/director_handscore_predicate_v62_2026-08-13.md)
WRITES data/foundation_provenance_v1/store                (ADDS rows; 7966 existing rows untouched)
       data/foundation_provenance_v1/quarantine_report.json
       data/foundation_provenance_v1/bank_manifest_predicate_v62.json
       data/foundation_provenance_v1/definitional_predicate_v62_ledger.jsonl  (fid -> source sentence)

NEVER WRITES data/foundation/reading_grounding_v1 -- the canonical store. Its per-file sha256 is
recorded BEFORE and AFTER and asserted identical; the script never opens it at all.

WHAT IS BANKED: predicate/condition facts ONLY (ENABLING_CONDITION, ENABLING_CONDITION_AGENT,
ENABLING_CONDITION_PATIENT, PROCESS_ACTION, PROCESS_PATIENT). The ISA / GROUNDED_MEANING
definitional output is deliberately NOT banked (the CALLED pattern is being edited concurrently
and the v5 ISA facts hand-scored 64%).

CHOICES, STATED:
  pipeline = DEFINITIONAL_EXTRACTOR  (HD-bound, glass-box recoverable, not ledger-only)
  source   = "definitional:BIO" | "definitional:ANAT" | "definitional:PSY" -- the corpus segment,
             derived from the fact's own provenance tags (all 221 are single-corpus). Deliberately
             NOT prefixed "reading:" and not "seed_base_vocabulary", so the backfill tagging rule
             can never mistake a banked predicate fact for a reading fact.
  trust    = TRUST_MID -- the SAME tag the reading loop used for these textbook corpora. Conservative
             on purpose: an equal-or-lower trust can never SUPERSEDE an existing fact.
  cardinality = MULTIVALUED for the five predicate relations. A process genuinely has several
             enabling conditions / several patients across sentences (VBNC state is entered when
             prokaryotes ENTER a dormant state and when they RESPOND to stressors); FUNCTIONAL
             would FLAG those as contradictions. This ADDS five keys to relation_cardinality and
             changes neither existing key (KNOWN_WORD / GROUNDED_MEANING stay FUNCTIONAL).
  strings  = banked VERBATIM as hand-scored (no re-casing, no re-stemming). 3 of 221 subjects
             carry an uppercase acronym ("VBNC state"); the reading rows are lowercased, so a
             case-sensitive join across the two pipelines misses those 3. Disclosed, not fixed.

SAFETY: written to a sibling tmp dir, verify-loaded there, then swapped in with os.replace and
verify-loaded again. All JSON side files written binary (newline hazard) + verify-loaded.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import torch  # noqa: E402

from hdlab.closed_class_lexicon import is_closed_class, lemma_verb  # noqa: E402
from hdlab.foundation_persistence import load_store, save_store  # noqa: E402
from hdlab.hd_fact_store import PIPELINE_UNKNOWN  # noqa: E402

CANONICAL = os.path.join(REPO_ROOT, "data", "foundation", "reading_grounding_v1")
OUT_DIR = os.path.join(REPO_ROOT, "data", "foundation_provenance_v1")
OUT_STORE = os.path.join(OUT_DIR, "store")
TMP_STORE = os.path.join(OUT_DIR, "store.__bank_tmp__")
BAK_STORE = os.path.join(OUT_DIR, "store.__prebank_backup__")
FACTS_JSONL = os.path.join(REPO_ROOT, "data", "exp_definitional_predicate_v62",
                           "predicate_facts_v62.jsonl")

PIPELINE = "DEFINITIONAL_EXTRACTOR"
TRUST = "TRUST_MID"
PREDICATE_RELATIONS = ("ENABLING_CONDITION", "ENABLING_CONDITION_AGENT",
                       "ENABLING_CONDITION_PATIENT", "PROCESS_ACTION", "PROCESS_PATIENT")
MEANING_RELATION = "GROUNDED_MEANING"
KNOWN_RELATION = "KNOWN_WORD"

# --- proper-noun table inputs: IDENTICAL to backfill_pipeline_provenance.py, on purpose, so the
# READING_GROUNDING / SEED_VOCABULARY rows of the quarantine table reproduce bit-for-bit.
import re  # noqa: E402

ONESTOP = os.path.join(REPO_ROOT, "data", "corpora", "onestop", "Texts-SeparatedByReadingLevel")
BIO_TXT = os.path.join(REPO_ROOT, "data", "corpora", "textbook_concepts_biology", "cleaned",
                       "concepts_biology.clean.txt")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")
_TOKEN = re.compile(r"[A-Za-z]+")


def _corpus_files() -> list:
    files = []
    for sub in ("Ele-Txt", "Int-Txt", "Adv-Txt"):
        d = os.path.join(ONESTOP, sub)
        files.extend(sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".txt")))
    if os.path.isfile(BIO_TXT):
        files.append(BIO_TXT)
    return files


def build_proper_noun_table() -> dict:
    counts: dict = {}
    for path in _corpus_files():
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        for sent in _SENT_SPLIT.split(text):
            toks = _TOKEN.findall(sent)
            for i, tok in enumerate(toks):
                if i == 0:
                    continue
                lem = lemma_verb(tok.lower())
                n, c = counts.get(lem, (0, 0))
                counts[lem] = (n + 1, c + (1 if tok[0].isupper() else 0))
    return counts


def classify_proper(lemma: str, table: dict) -> str:
    n, c = table.get(lemma, (0, 0))
    if n < 2:
        return "UNKNOWN"
    return "PROPER" if c * 2 > n else "COMMON"


def _file_shas(root: str) -> dict:
    out = {}
    for dp, dn, fn in os.walk(root):
        dn.sort()
        for name in sorted(fn):
            p = os.path.join(dp, name)
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    h.update(chunk)
            out[os.path.relpath(p, root).replace(os.sep, "/")] = h.hexdigest()
    return dict(sorted(out.items()))


def _tree_sha(root: str) -> str:
    """Single digest over the whole tree: sha256 of 'relpath:filesha\\n' lines, sorted."""
    per = _file_shas(root)
    blob = "".join(f"{k}:{v}\n" for k, v in per.items()).encode("ascii")
    return hashlib.sha256(blob).hexdigest()


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:                      # BINARY: text mode doubles CRLF
        f.write(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8"))
    os.replace(tmp, path)
    with open(path, encoding="utf-8") as f:         # verify-load
        json.load(f)


def _atomic_jsonl(path: str, rows: list) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        for r in rows:
            f.write((json.dumps(r, sort_keys=True, ensure_ascii=True) + "\n").encode("utf-8"))
    os.replace(tmp, path)
    with open(path, encoding="utf-8") as f:
        n = sum(1 for line in f if line.strip())
    assert n == len(rows), f"jsonl verify-load: {n} != {len(rows)}"


def quarantine_table(store, table: dict) -> dict:
    """Per-pipeline counts. Superset of the backfill report's schema: the pre-existing fields are
    computed EXACTLY as before (so READING_GROUNDING / SEED_VOCABULARY reproduce), plus per-relation
    counts and the predicate-relation buckets the new pipeline needs."""
    per: dict = {}
    for f in store._facts:
        b = per.setdefault(f.pipeline, {
            "n_facts": 0, "n_known_word": 0, "n_grounded_meaning": 0,
            "n_predicate_relation": 0,
            "n_tautology": 0, "n_nontautological": 0,
            "closed_class_object": 0, "proper_noun_object": 0, "noise_lower_bound_union": 0,
            "unclassified_object": 0, "unknown_too_rare_object": 0, "closed_class_subject": 0,
            "relations": Counter(), "sources": Counter(), "statuses": Counter(),
            "_proper_objects": Counter(), "_closed_class_objects": Counter(),
        })
        b["n_facts"] += 1
        b["relations"][f.relation] += 1
        b["sources"][f.source] += 1
        b["statuses"][f.status] += 1
        if f.relation == KNOWN_RELATION:
            b["n_known_word"] += 1
            continue
        if f.relation == MEANING_RELATION:
            b["n_grounded_meaning"] += 1
        elif f.relation in PREDICATE_RELATIONS:
            b["n_predicate_relation"] += 1
        else:
            continue
        if f.subject == f.obj:
            b["n_tautology"] += 1
            continue
        b["n_nontautological"] += 1
        cc = is_closed_class(f.obj)
        pn = classify_proper(lemma_verb(f.obj.lower()), table)
        if cc:
            b["closed_class_object"] += 1
            b["_closed_class_objects"][f.obj] += 1
        if pn == "PROPER":
            b["proper_noun_object"] += 1
            b["_proper_objects"][f.obj] += 1
        if cc or pn == "PROPER":
            b["noise_lower_bound_union"] += 1
        elif pn == "UNKNOWN":
            b["unknown_too_rare_object"] += 1
        else:
            b["unclassified_object"] += 1
        if is_closed_class(f.subject):
            b["closed_class_subject"] += 1

    for b in per.values():
        b["relations"] = dict(sorted(b["relations"].items()))
        b["sources"] = dict(sorted(b["sources"].items()))
        b["statuses"] = dict(sorted(b["statuses"].items()))
        b["proper_noun_objects"] = dict(sorted(b.pop("_proper_objects").items()))
        b["closed_class_objects"] = dict(sorted(b.pop("_closed_class_objects").items()))
    return per


def main() -> int:
    # ---------------------------------------------------------------- canonical store, BEFORE
    canon_before = _file_shas(CANONICAL)
    canon_tree_before = _tree_sha(CANONICAL)

    rows = []
    with open(FACTS_JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    assert len(rows) == 221, f"expected 221 predicate facts, got {len(rows)}"
    bad_rel = sorted({r["relation"] for r in rows} - set(PREDICATE_RELATIONS))
    assert not bad_rel, f"non-predicate relation in the bank set: {bad_rel}"
    assert not any(r["relation"] in (MEANING_RELATION, KNOWN_RELATION) for r in rows), \
        "ISA / GROUNDED_MEANING facts must NOT be banked in this pass"

    # ---------------------------------------------------------------- load + snapshot existing
    store = load_store(OUT_STORE)
    n_before = len(store._facts)
    assert n_before == 7966, f"provenance store had {n_before} rows, expected 7966"
    pre_vecs = [f.vec.clone() for f in store._facts]
    pre_rows = [(f.subject, f.relation, f.obj, f.source, f.trust_sym, f.status, f.pipeline)
                for f in store._facts]
    pre_card = dict(store.relation_cardinality)

    for rel in PREDICATE_RELATIONS:
        assert rel not in store.relation_cardinality, f"{rel} already declared"
        store.relation_cardinality[rel] = "MULTIVALUED"

    # ---------------------------------------------------------------- bank
    ledger, resolutions = [], Counter()
    for r in rows:
        prefixes = sorted({p.split(":")[0] for p in r["provenance"]})
        assert len(prefixes) == 1, f"multi-corpus provenance not handled: {r['provenance']}"
        source = f"definitional:{prefixes[0]}"
        res = store.store(r["subject"], r["relation"], r["object"], source, TRUST,
                          pipeline=PIPELINE)
        resolutions[res.resolution] += 1
        ledger.append({
            "fid": res.fid, "subject": r["subject"], "relation": r["relation"],
            "object": r["object"], "source": source, "trust": TRUST, "pipeline": PIPELINE,
            "resolution": res.resolution,
            "pattern": r["pattern"], "patterns_seen": r["patterns_seen"],
            "n_attestations": r["n_attestations"],
            "definiendum_surface": r["definiendum_surface"],
            "predicate_span": r["predicate_span"],
            "source_sentences": r["source_sentences"], "provenance": r["provenance"],
            "extractor_fid": r["fid"],
        })
    assert len(store._facts) == n_before + 221, "row count after banking is wrong"

    # existing rows must be untouched IN MEMORY (no REPLACE/FLAG side effects)
    for i in range(n_before):
        f = store._facts[i]
        assert torch.equal(f.vec, pre_vecs[i]), f"pre-existing vec changed at fid {f.fid}"
        assert (f.subject, f.relation, f.obj, f.source, f.trust_sym, f.status,
                f.pipeline) == pre_rows[i], f"pre-existing row changed at fid {f.fid}"

    # ---------------------------------------------------------------- write: tmp -> verify -> swap
    if os.path.isdir(TMP_STORE):
        shutil.rmtree(TMP_STORE)
    save_store(store, TMP_STORE)
    tmp_reload = load_store(TMP_STORE)
    assert len(tmp_reload._facts) == n_before + 221

    if os.path.isdir(BAK_STORE):
        shutil.rmtree(BAK_STORE)
    os.rename(OUT_STORE, BAK_STORE)
    try:
        os.rename(TMP_STORE, OUT_STORE)
    except Exception:
        os.rename(BAK_STORE, OUT_STORE)
        raise

    # ---------------------------------------------------------------- ROUND-TRIP verification
    re_store = load_store(OUT_STORE)
    assert len(re_store._facts) == n_before + 221
    for i in range(n_before):
        f = re_store._facts[i]
        assert torch.equal(f.vec, pre_vecs[i]), f"legacy vec changed on reload at fid {f.fid}"
        assert (f.subject, f.relation, f.obj, f.source, f.trust_sym, f.status,
                f.pipeline) == pre_rows[i], f"legacy row changed on reload at fid {f.fid}"
    legacy_glassbox = Counter(re_store.recover_fact(re_store._facts[i].vec)["pipeline"]
                              for i in range(0, n_before, 97))  # sampled sweep, deterministic
    assert set(legacy_glassbox) == {PIPELINE_UNKNOWN}, f"legacy glass-box drift: {legacy_glassbox}"

    new_facts = re_store._facts[n_before:]
    assert len(new_facts) == 221
    ledger_ok, glassbox_ok = 0, 0
    for f, row in zip(new_facts, ledger):
        assert f.pipeline == PIPELINE, f"fid {f.fid} ledger pipeline={f.pipeline}"
        ledger_ok += 1
        rec = re_store.recover_fact(f.vec)                       # GLASS-BOX (unbind + cleanup)
        assert rec["pipeline"] == PIPELINE, f"fid {f.fid} glass-box pipeline={rec['pipeline']}"
        assert rec["subject"] == row["subject"] and rec["object"] == row["object"]
        assert rec["relation"] == row["relation"] and rec["source"] == row["source"]
        assert rec["trust"] == TRUST
        glassbox_ok += 1
    assert re_store.relation_cardinality == {**pre_card,
                                             **{r: "MULTIVALUED" for r in PREDICATE_RELATIONS}}

    shutil.rmtree(BAK_STORE)

    # ---------------------------------------------------------------- canonical store, AFTER
    canon_after = _file_shas(CANONICAL)
    canon_tree_after = _tree_sha(CANONICAL)
    assert canon_before == canon_after, "CANONICAL STORE CHANGED -- hard rule violated"
    assert canon_tree_before == canon_tree_after

    # ---------------------------------------------------------------- quarantine report
    table = build_proper_noun_table()
    per_pipeline = quarantine_table(re_store, table)
    def_b = per_pipeline[PIPELINE]
    tautology_zero = def_b["n_tautology"] == 0

    prior_path = os.path.join(OUT_DIR, "quarantine_report.json")
    with open(prior_path, encoding="utf-8") as f:
        prior = json.load(f)
    prior_matches = {}
    for pipe in ("READING_GROUNDING", "SEED_VOCABULARY"):
        p_old, p_new = prior["per_pipeline"][pipe], per_pipeline[pipe]
        prior_matches[pipe] = {k: {"before": p_old[k], "after": p_new[k]}
                               for k in sorted(p_old)
                               if k in p_new and p_old[k] != p_new[k]}

    report = {
        "generated_ts_iso": datetime.now(timezone.utc).isoformat(),
        "supersedes": "the backfill-only report generated 2026-08-13T05:03:21Z",
        "provenance_store": "data/foundation_provenance_v1/store",
        "canonical_store_untouched": {
            "path": "data/foundation/reading_grounding_v1",
            "tree_sha256_before": canon_tree_before,
            "tree_sha256_after": canon_tree_after,
            "identical": canon_before == canon_after,
            "per_file_sha256": canon_after,
            "tree_sha256_recipe": "sha256 of sorted 'relpath:filesha256\\n' lines over the tree",
        },
        "banked_this_pass": {
            "pipeline": PIPELINE,
            "source_file": "data/exp_definitional_predicate_v62/predicate_facts_v62.jsonl",
            "n_facts": 221,
            "relations": dict(sorted(Counter(r["relation"] for r in rows).items())),
            "sources": dict(sorted(Counter(l["source"] for l in ledger).items())),
            "trust": TRUST,
            "store_resolutions": dict(sorted(resolutions.items())),
            "isa_or_grounded_meaning_banked": 0,
            "relation_cardinality_added": {r: "MULTIVALUED" for r in PREDICATE_RELATIONS},
        },
        "rows_before": n_before,
        "rows_after": len(re_store._facts),
        "roundtrip_verification": {
            "legacy_rows_bit_identical_after_reload": n_before,
            "legacy_glassbox_sampled_all_unknown_legacy": sorted(legacy_glassbox.items()),
            "new_rows_pipeline_in_ledger_after_reload": ledger_ok,
            "new_rows_pipeline_glassbox_recovered_after_reload": glassbox_ok,
            "new_rows_content_glassbox_matches_ledger": glassbox_ok,
        },
        "definitional_extractor_tautology_count": def_b["n_tautology"],
        "definitional_extractor_tautology_is_zero": tautology_zero,
        "criteria": {
            "tautology": "subject == obj (exact string) on a non-KNOWN_WORD row",
            "closed_class": "hdlab.closed_class_lexicon.is_closed_class(obj)",
            "proper_noun": ("corpus-derived: majority of NON-sentence-initial occurrences "
                            "capitalized, >=2 informative occurrences, lemma_verb-normalized"),
            "proper_noun_corpus_files": len(_corpus_files()),
            "proper_noun_table_scope_caveat": (
                "the table is built from OneStop + concepts_biology ONLY (unchanged from the "
                "backfill, so the READING_GROUNDING/SEED_VOCABULARY rows reproduce exactly). The "
                "ANAT and PSY textbooks the predicate facts come from are NOT in it, so most "
                "definitional-extractor objects fall in unknown_too_rare rather than being "
                "positively classified COMMON. The extractor's OWN subject_type field flags "
                "3/221 subjects PROPER."),
            "scope_note": ("closed-class / proper-noun buckets are measured on NON-TAUTOLOGICAL "
                           "GROUNDED_MEANING rows (reading/seed) and NON-TAUTOLOGICAL predicate "
                           "rows (definitional extractor)"),
        },
        "per_pipeline": {k: per_pipeline[k] for k in sorted(per_pipeline)},
        "prior_report_field_changes_for_existing_pipelines": prior_matches,
        "hd_binding_scope": (
            "BACKFILLED rows (7966): PLAINTEXT LEDGER ONLY -- their landed vectors carry no "
            "PIPELINE binding, so recover_fact() returns UNKNOWN_LEGACY for them. BANKED rows "
            "(221, DEFINITIONAL_EXTRACTOR): HD-BOUND -- pipeline is glass-box recoverable from "
            "the vector alone, verified above on the RELOADED store."),
        "out_of_scope_notes": [
            "ISA / GROUNDED_MEANING definitional facts were NOT banked (CALLED pattern under "
            "concurrent edit; v5 ISA hand-scored 64%).",
            "No tautology was deleted, deduped or cleaned anywhere; measurement only.",
            "Subjects banked verbatim; 3/221 carry an uppercase acronym while the reading rows "
            "are lowercased, so a case-sensitive cross-pipeline join misses those 3.",
            "The 221 facts are what a HAND-WRITTEN PARSER supplied; banking them is not evidence "
            "the substrate learned anything.",
        ],
    }
    _atomic_json(prior_path, report)
    _atomic_jsonl(os.path.join(OUT_DIR, "definitional_predicate_v62_ledger.jsonl"), ledger)

    manifest = {
        "generated_ts_iso": report["generated_ts_iso"],
        "action": "BANK definitional predicate v6.2 facts into the provenance store",
        "rows_before": n_before,
        "rows_after": len(re_store._facts),
        "pipeline_counts": {k: per_pipeline[k]["n_facts"] for k in sorted(per_pipeline)},
        "canonical_store_tree_sha256_before": canon_tree_before,
        "canonical_store_tree_sha256_after": canon_tree_after,
        "canonical_store_per_file_sha256": canon_after,
        "provenance_store_sha256": _file_shas(OUT_STORE),
    }
    _atomic_json(os.path.join(OUT_DIR, "bank_manifest_predicate_v62.json"), manifest)

    print(json.dumps({
        "rows_before": n_before, "rows_after": len(re_store._facts),
        "pipeline_counts": manifest["pipeline_counts"],
        "store_resolutions": dict(sorted(resolutions.items())),
        "roundtrip": report["roundtrip_verification"],
        "definitional_tautologies": def_b["n_tautology"],
        "definitional_closed_class_object": def_b["closed_class_object"],
        "definitional_proper_noun_object": def_b["proper_noun_object"],
        "definitional_unknown_too_rare_object": def_b["unknown_too_rare_object"],
        "definitional_unclassified_object": def_b["unclassified_object"],
        "canonical_tree_sha_before": canon_tree_before,
        "canonical_tree_sha_after": canon_tree_after,
        "canonical_identical": canon_before == canon_after,
        "prior_report_field_changes_for_existing_pipelines": prior_matches,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
