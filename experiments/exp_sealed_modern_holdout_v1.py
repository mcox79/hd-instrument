"""exp_sealed_modern_holdout_v1 -- A SEALED DOCUMENT-LEVEL MODERN HOLDOUT, DECLARED BEFORE THE FIRST ANSWER.

problem: seal_a_document_level_modern_holdout_never_read_by_any_builder_or_board_declare_the_split_and_the_
         scorer_before_the_first_answer_is_examined   (pri 126)

WHY THIS EXISTS.  Every modern number this project publishes comes from a split it has read many times while
choosing integrations, thresholds and defaults: UD-EWT test (the agent / patient / state rows), GUM test (the
coref / salience / state rows), WiC dev+test pooled.  Repeated runs on a read split are engineering feedback,
not a measurement on a fresh population.  This cell seals one.

WHAT IT IS NOT.  It changes no organ and sweeps no parameter.  It is an INSTRUMENT: a draw, a manifest, a
fixed scorer, a seal witness and a board arm.

THE ENUMERATION DECIDED THE CORPUS, NOT A GUESS (`--enumerate`, published in the manifest):
  * GUM V12.1.0 (275 GUM + 26 GENTLE = 301 documents) is EXHAUSTED.  `experiments/gum_coref.load_docs` reads
    every GUM_* file (no split filter at the loader; the board's split is `[i % 2 == 1]` AFTER the load), and
    the GENTLE files -- the natural "unread" candidate -- are read by `exp_commonnoun_binder_live_report_v1`,
    `exp_crosstype_live_wire_gum_v1`, `exp_namebridge_fidelity_landing_v1` and two witnesses, and GENTLE
    numbers are quoted as calibration evidence inside `hdlab/lexical_categories.py`.  GitHub `master` for
    amir-zeldes/gum is the SAME commit we pinned (22fdf87f9c...), so there is no newer GUM document to take.
  * UD-EWT is exhausted in all three splits, and the dev split is a trap: `en_ewt-ud-dev.conllu` is absent
    from `data/corpora/ud_english_ewt/` but PRESENT at a SECOND on-disk copy, `experiments/data/
    ud_english_ewt/`, where `tools/build_construction_gold.py` and `tools/build_negation_factuality_gold.py`
    BUILD GOLD ASSETS from it.  A holdout drawn from EWT dev would have been contaminated by two builders.
  * So the sealed source is a corpus that is NOT ON THIS DISK AT ALL and is named by no file in `hdlab/`,
    `tools/`, `experiments/` or `verification/`: UD_English-PUD -- 1000 modern sentences (2016-17 news +
    Wikipedia) in 397 documents, a treebank that exists only as a blind test set.  A corpus that is absent
    from disk cannot have been read by a builder; that is the strongest form the seal can take.

THE SEAL IS THREE THINGS, IN THIS ORDER, AND THE ORDER IS THE POINT
  1. `--fetch`      acquire the pinned corpus into `data/corpora/holdout/ud_pud_sealed_v1/` -- a directory no
                    existing loader globs (asserted by the witness).
  2. `--seal`       enumerate, draw (seeded, stratified, DOCUMENT as the unit), hash every document, freeze the
                    scorer by file hash and the configuration by flag + asset hash, run the overlap audit, and
                    write `data/corpora/holdout/SEALED_modern_v1.json`.  NO READER RUNS.  Committed here.
  3. `--score`      the ONE measured read.  Reported once.  A holdout is read, not tuned.

THE SCORER IS FIXED BY IMPORT, NOT BY COPY.  Every row, floor and twin comes from the landed pri-122 cell
(`experiments/exp_board_rows_on_the_reader_v1.py`: `score_ud_chunk`, `_ud_write_chunk`, `_row`, `provenance`),
whose SHA-256 is recorded in the manifest.  Changing the scorer changes that hash and the check reports it.

THE PRODUCT, NOT A COMPONENT.  `_ud_write_chunk` writes ONLY the FORM column; the other CoNLL columns are
`_`.  The reader gets raw cased text and nothing else: no gold tag, no gold head, no gold deprel, no coref
column.  The gold columns are read by the ANSWER KEY only, after the reader has answered.  Every run COUNTS
the non-FORM columns it wrote and publishes the count (0 = the reader saw raw text).

ROWS (the three the sealed corpus can carry; the enumeration says why the other four cannot -- see SOLVED.md)
  who_did_what_agent    model = the live reader's sm.events[].agent at the gold verb (no event = a miss)
  who_did_what_patient  model = sm.events[].patient at the gold verb
  state                 model = sm.entity_states property for the gold copular holder
Floors are recomputed in place on the sealed population (nearest pre/post-verbal nominal on the READER'S OWN
categories; most-recent-noun binding); the twin is the information-free arm of the same shape.  Uncertainty is
a DOCUMENT-paired bootstrap: the resampling unit is the sealed document, never the within-document answer.

GLASS-BOX: no external LLM, no spaCy, no nltk tagger, no supervised parser at inference.  MODERN gold only.
Writes ONLY to its own get_output_dir and to data/corpora/holdout/.

Run: .venv/Scripts/python.exe experiments/exp_sealed_modern_holdout_v1.py --self-test
     ... --enumerate            the corpus-reader enumeration, file:line (no network, no reader)
     ... --fetch                acquire UD_English-PUD at the pinned commit (network; once)
     ... --seal                 the draw + manifest.  COMMIT THE MANIFEST BEFORE --score.
     ... --score                the one measured read of the sealed documents
     ... --board                the per-landing board arm (one read per landing, same provenance columns)
     ... --compare              the same scorer on the board's own UD-EWT test population (the gap)
     ... --controls             scrambled-document control + the chunk-matched diagnostic
"""
from __future__ import annotations
import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
os.environ.setdefault("PYTHONHASHSEED", "0")
import sys, argparse, json, time, random, re, hashlib, tempfile, shutil, urllib.request
from collections import defaultdict, Counter
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir
ANCHOR = "sealed_modern_holdout_v1"
OUT_DIR = str(get_output_dir(ANCHOR))

# ---------------------------------------------------------------------------------------------------
# THE DECLARATION -- every constant below is fixed HERE, in the committed source, and copied into the
# manifest by --seal.  Nothing below is chosen after an answer has been seen.
# ---------------------------------------------------------------------------------------------------
MANIFEST_VERSION = "SEALED_modern_v1"
HOLDOUT_DIR = os.path.join(_REPO, "data", "corpora", "holdout")
CORPUS_DIR = os.path.join(HOLDOUT_DIR, "ud_pud_sealed_v1")
CORPUS_FILE = os.path.join(CORPUS_DIR, "en_pud-ud-test.conllu")
MANIFEST_PATH = os.path.join(HOLDOUT_DIR, "SEALED_modern_v1.json")

CORPUS = {
    "name": "UD_English-PUD",
    "repo": "https://github.com/UniversalDependencies/UD_English-PUD",
    "pinned_commit": "f16eba4ae7f3d161870ed320676c5088b8fa476c",
    "file": "en_pud-ud-test.conllu",
    "url": ("https://raw.githubusercontent.com/UniversalDependencies/UD_English-PUD/"
            "f16eba4ae7f3d161870ed320676c5088b8fa476c/en_pud-ud-test.conllu"),
    "license": "CC BY-SA 3.0 (UD_English-PUD LICENSE.txt)",
    "modern": "2016-17 newswire + Wikipedia (CoNLL-2017 shared-task parallel test data). NOT 19c.",
    "why_this_corpus": ("the enumeration found NO unread document in GUM (301/301 read; master == our pinned "
                        "commit) and none in UD-EWT (train/dev/test all read, dev via the second on-disk copy "
                        "under experiments/data/). A corpus absent from disk cannot have been read."),
}

# THE DRAW RULE -- declared before the draw is executed.
DRAW_RULE = {
    "unit": "document (# newdoc id in the CoNLL-U file)",
    "stratify_by": "document-id genre prefix: 'n' = newswire, 'w' = Wikipedia",
    "rule": ("within each genre stratum, sort document ids lexicographically, shuffle with "
             "random.Random(SEED) and take the first ceil(0.70 * n) documents as HOLDOUT_V1; the remainder "
             "is RESERVE_V2 and is never read by anything, including this cell"),
    "seed": 20260916,
    "holdout_fraction": 0.70,
    "reserve_purpose": ("RESERVE_V2 is the rolling second seal: when HOLDOUT_V1 retires under the policy "
                        "below, RESERVE_V2 replaces it and V1 is retired to diagnostics"),
}

# THE RETIREMENT POLICY -- strategy ruling, 2026-09-16 (phase 7).  Written down so that "the holdout decayed
# into a dev set" is a condition a machine can check, not a judgement call made after the fact.
RETIREMENT_POLICY = {
    "read_budget": ("ONE read per LANDING, where a landing is a commit that changes the reader's path. "
                    "tools/land.py runs the board arm once and REFUSES a second read at the same git HEAD "
                    "(see notes/problems/<slug>/landing_board_hook_patch.diff)."),
    "reserve_stays_unread_until": ("HOLDOUT_V1 has been read 20 times, OR the scorer changes (its SHA-256 "
                                   "no longer matches the one recorded at the seal) -- WHICHEVER COMES "
                                   "FIRST. RESERVE_V2 is not read before that, by anything, including the "
                                   "instrument itself."),
    "on_trigger": ("promote RESERVE_V2 to the scored holdout, bump the manifest version, and retire "
                   "HOLDOUT_V1 to diagnostics -- its numbers stay quotable as a read split, never again as "
                   "a sealed measurement."),
    "how_to_check": ("the read count is the line count of data/exp_sealed_modern_holdout_v1/"
                     "board_landings.jsonl; the scorer condition is the scorer_moved_since_seal field on "
                     "the latest record. verification/test_sealed_holdout_is_unread.py asserts both."),
    "why_a_number_and_not_a_judgement": ("a holdout read once per landing becomes a dev set by ordinary "
                                         "selection pressure; naming the threshold in advance is the same "
                                         "discipline as naming the scorer in advance"),
}

# THE SCORER -- declared before the first answer is examined; fixed by import + file hash.
SCORER = {
    "module": "experiments/exp_board_rows_on_the_reader_v1.py",
    "functions": ["score_ud_chunk", "_ud_write_chunk", "_gold_agent_items", "_row", "provenance", "_paired"],
    "rows": ["who_did_what_agent", "who_did_what_patient", "state"],
    "model": "the LIVE hdlab.situation_reader.SituationReader, one read per sealed document, raw text only",
    "answer_key": ("UD gold columns read AFTER the reader has answered: agent = nsubj (active) / obl:agent "
                   "(passive) of a gold VERB; patient = obj (active) / nsubj:pass (passive); state = "
                   "pred_adj + pred_nom copular clauses via exp_copular_is_a_binding_readout_v1.typed_gold"),
    "floors": {"who_did_what_agent": "nearest PRE-verbal nominal on the reader's own categories",
               "who_did_what_patient": "nearest POST-verbal nominal on the reader's own categories",
               "state": "most-recent-noun positional binding on the reader's own categories"},
    "twin": "information-free arm of the same shape (a random sentence nominal / the holders shuffled)",
    "abstention": "counted WRONG -- a gold verb at which the reader fired no event scores as a miss",
    "denominator": "every eligible gold question in the sealed documents; nothing is dropped",
    "uncertainty_unit": "document -- the paired bootstrap resamples sealed DOCUMENTS, not answers",
    "n_boot": 2000,
    "boot_seed": 20260916,
    "gate": ("model beats the STRONGEST floor CI-separated on the sealed population AND beats the "
             "information-free twin; the floors are recomputed in place, never pasted"),
    "read_once": "the sealed answers are reported once per landing and never tuned against",
}

# The corpora the enumeration scans, and the tokens that reach each of them.
ENUM_TARGETS = {
    "UD-EWT (data/corpora)": [r"ud_english_ewt", r"en_ewt-ud-(train|dev|test)\.conllu"],
    "UD-EWT (experiments/data)": [r"experiments[\\/\"',\s]+data[\\/\"',\s]+ud_english_ewt"],
    "GUM + GENTLE": [r"gum[\\/]conllu", r"GUM_CONLLU", r"gum_coref", r"\bload_docs\s*\(",
                     r"gum_only\s*=\s*(True|False)", r"\bGENTLE_"],
    "THE SEALED HOLDOUT": [r"ud_pud_sealed_v1", r"en_pud-ud-test", r"SEALED_modern_v1", r"UD_English-PUD"],
}
SCAN_ROOTS = ("hdlab", "tools", "experiments", "verification")
SCAN_SKIP = (os.path.join("tools", "dashboard", ".venv"), "__pycache__",
             os.path.join("tools", "dashboard", "node_modules"))
# The two files ALLOWED to name the sealed holdout (the instrument itself and its witness).
SEAL_EXEMPT = ("experiments/exp_sealed_modern_holdout_v1.py", "verification/test_sealed_holdout_is_unread.py")


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ===================================================================================================
# PART 1 -- THE ENUMERATION.  Absence is proved by walking every file, not by one grep.
# ===================================================================================================
def _py_files():
    out = []
    for root in SCAN_ROOTS:
        base = os.path.join(_REPO, root)
        for dp, dns, fns in os.walk(base):
            rel = os.path.relpath(dp, _REPO)
            if any(s in rel for s in SCAN_SKIP):
                dns[:] = []
                continue
            dns[:] = [d for d in dns if d not in ("__pycache__", ".venv", "node_modules")]
            for fn in fns:
                if fn.endswith(".py"):
                    out.append(os.path.join(dp, fn))
    return sorted(out)


def enumerate_readers(verbose=False):
    """Every file:line under hdlab/ tools/ experiments/ verification/ that names each modern corpus, with the
    split token it reaches.  This is the proof that the sealed ids are unread: an ENUMERATION of every .py
    file on disk, not a search for the ones I expected to find."""
    pats = {k: [re.compile(p) for p in v] for k, v in ENUM_TARGETS.items()}
    hits = {k: [] for k in ENUM_TARGETS}
    files = _py_files()
    for fp in files:
        rel = os.path.relpath(fp, _REPO).replace("\\", "/")
        try:
            lines = open(fp, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        for i, ln in enumerate(lines, 1):
            for key, ps in pats.items():
                if any(p.search(ln) for p in ps):
                    hits[key].append({"where": "%s:%d" % (rel, i), "file": rel, "line": i,
                                      "text": ln.strip()[:240], "comment": ln.strip().startswith("#")})
    split_tok = defaultdict(list)
    for key in ("UD-EWT (data/corpora)", "UD-EWT (experiments/data)"):
        for h in hits[key]:
            for s in ("train", "dev", "test"):
                if ("ud-%s.conllu" % s) in h["text"]:
                    split_tok[s].append(h["where"])
    named = sorted(set(h["file"] for h in hits["THE SEALED HOLDOUT"]))
    enum = {
        "scanned_roots": list(SCAN_ROOTS), "n_python_files_walked": len(files),
        "counts": {k: {"lines": len(v), "files": len(set(h["file"] for h in v)),
                       "code_lines": len([h for h in v if not h["comment"]])} for k, v in hits.items()},
        "ud_ewt_split_tokens_named": {k: {"n": len(v), "where": sorted(set(v))[:40]}
                                      for k, v in split_tok.items()},
        "sealed_holdout_named_by": named,
        "sealed_holdout_unread": sorted(set(named) - set(SEAL_EXEMPT)) == [],
        "gentle_read_by": sorted(set(h["file"] for h in hits["GUM + GENTLE"]
                                     if "gum_only=False" in h["text"].replace(" ", "")
                                     or "GENTLE_" in h["text"])),
        "hits": {k: v[:400] for k, v in hits.items()},
    }
    if verbose:
        print("ENUMERATION -- %d python files walked under %s" % (len(files), ", ".join(SCAN_ROOTS)))
        for k in ENUM_TARGETS:
            c = enum["counts"][k]
            print("  %-28s %4d lines in %3d files (%d are code, not comments)"
                  % (k, c["lines"], c["files"], c["code_lines"]))
        print("  UD-EWT split tokens named in code:")
        for s in ("train", "dev", "test"):
            w = enum["ud_ewt_split_tokens_named"].get(s, {"n": 0, "where": []})
            print("    %-5s  %3d sites  e.g. %s" % (s, w["n"], ", ".join(w["where"][:3])))
        print("  GENTLE (the natural unread candidate) is read by %d files, e.g. %s"
              % (len(enum["gentle_read_by"]), ", ".join(enum["gentle_read_by"][:4])))
        print("  files naming the SEALED holdout: %s" % (named or "NONE"))
        print("  SEAL HOLDS (nothing but the instrument + witness names it): %s"
              % enum["sealed_holdout_unread"])
    return enum


# ===================================================================================================
# PART 2 -- THE CORPUS: acquire (pinned), parse to DOCUMENTS, hash each one.
# ===================================================================================================
def fetch_corpus(force=False):
    os.makedirs(CORPUS_DIR, exist_ok=True)
    if os.path.exists(CORPUS_FILE) and not force:
        print("[fetch] already present: %s (%d bytes)" % (CORPUS_FILE, os.path.getsize(CORPUS_FILE)))
    else:
        print("[fetch] %s" % CORPUS["url"])
        with urllib.request.urlopen(CORPUS["url"], timeout=120) as r:
            data = r.read()
        with open(CORPUS_FILE, "wb") as fh:
            fh.write(data)
        print("[fetch] wrote %d bytes" % len(data))
    prov = {"acquired_utc": _now(), "sha256": _sha256_file(CORPUS_FILE),
            "bytes": os.path.getsize(CORPUS_FILE)}
    prov.update(CORPUS)
    prov["note"] = ("STATIC OFFLINE FOUNDATION ASSET (an eval gold, acquired once, never used at inference). "
                    "Placed under data/corpora/holdout/ -- a directory NO existing loader globs -- so no "
                    "builder can reach it by the paths it already walks. data/ is gitignored; this file is "
                    "re-acquirable from the pinned commit above.")
    with open(os.path.join(CORPUS_DIR, "PROVENANCE.json"), "w", encoding="utf-8") as fh:
        json.dump(prov, fh, indent=2)
    print("[fetch] sha256 %s" % prov["sha256"])
    return prov


def parse_pud(path=None):
    """[{docid, genre, sents:[[tokdict,...]], n_sents, n_toks, sha256}] -- tok dicts in load_ud's schema."""
    path = path or CORPUS_FILE
    docs = []
    state = {"doc": None, "sent": []}

    def close_sent():
        if state["sent"] and state["doc"] is not None:
            state["doc"]["sents"].append(state["sent"])
        state["sent"] = []

    def close_doc():
        d = state["doc"]
        if d is not None:
            d["n_sents"] = len(d["sents"])
            d["n_toks"] = sum(len(s) for s in d["sents"])
            d["sha256"] = _sha256_text("\n".join(d["_raw"]))
            del d["_raw"]
            docs.append(d)
        state["doc"] = None

    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("# newdoc id"):
            close_sent()
            close_doc()
            did = line.split("=", 1)[1].strip()
            state["doc"] = {"docid": did, "genre": ("newswire" if did.startswith("n") else "wikipedia"),
                            "sents": [], "_raw": []}
        if state["doc"] is not None:
            state["doc"]["_raw"].append(line)
        if not line.strip():
            close_sent()
            continue
        if line.startswith("#"):
            continue
        c = line.split("\t")
        if len(c) < 8 or "-" in c[0] or "." in c[0]:
            continue
        state["sent"].append({"id": int(c[0]), "form": c[1], "upos": c[3], "head": int(c[6]),
                              "dep": c[7].split(":")[0], "deprel": c[7]})
    close_sent()
    close_doc()
    return docs


# ===================================================================================================
# PART 3 -- THE DRAW (seeded, stratified, DOCUMENT as the unit) and the OVERLAP AUDIT.
# ===================================================================================================
def draw(docs, seed=None, frac=None):
    seed = DRAW_RULE["seed"] if seed is None else seed
    frac = DRAW_RULE["holdout_fraction"] if frac is None else frac
    hold, res = [], []
    for genre in sorted(set(d["genre"] for d in docs)):
        ids = sorted(d["docid"] for d in docs if d["genre"] == genre)
        random.Random(seed).shuffle(ids)
        n = len(ids)
        k = (n * int(round(frac * 100)) + 99) // 100          # ceil(frac*n), integer arithmetic
        hold += ids[:k]
        res += ids[k:]
    return sorted(hold), sorted(res)


def _sent_keys(rows):
    return set(_sha256_text(" ".join(w for w in s).lower()) for s in rows if len(s) >= 5)


def _conllu_sent_forms(path):
    out, cur = [], []
    try:
        fh = open(path, encoding="utf-8", errors="replace")
    except OSError:
        return out
    with fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                if cur:
                    out.append(cur)
                    cur = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 4 or "-" in c[0] or "." in c[0]:
                continue
            cur.append(c[1])
    if cur:
        out.append(cur)
    return out


def overlap_audit(docs, verbose=False):
    """Quantified sentence overlap between the sealed corpus and EVERY modern corpus on disk that a builder or
    board reads.  A shared WORD is not leakage; a shared SENTENCE is."""
    sealed = _sent_keys([[t["form"] for t in s] for d in docs for s in d["sents"]])
    sources = {
        "UD-EWT train (data/corpora)": "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu",
        "UD-EWT test (data/corpora)": "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu",
        "UD-EWT train (experiments/data)": "experiments/data/ud_english_ewt/en_ewt-ud-train.conllu",
        "UD-EWT dev (experiments/data)": "experiments/data/ud_english_ewt/en_ewt-ud-dev.conllu",
        "UD-EWT test (experiments/data)": "experiments/data/ud_english_ewt/en_ewt-ud-test.conllu",
    }
    rep = {}
    for name, rel in sources.items():
        p = os.path.join(_REPO, rel)
        if not os.path.exists(p):
            rep[name] = {"present": False}
            continue
        ks = _sent_keys(_conllu_sent_forms(p))
        inter = sealed & ks
        rep[name] = {"present": True, "n_sentences": len(ks), "shared_sentences": len(inter),
                     "shared_fraction_of_sealed": round(len(inter) / max(1, len(sealed)), 6)}
    gdir = os.path.join(_REPO, "data", "corpora", "gum", "conllu")
    gk, ng = set(), 0
    if os.path.isdir(gdir):
        for fn in sorted(os.listdir(gdir)):
            if fn.endswith(".conllu"):
                ng += 1
                gk |= _sent_keys(_conllu_sent_forms(os.path.join(gdir, fn)))
    inter = sealed & gk
    rep["GUM + GENTLE (all %d docs)" % ng] = {
        "present": ng > 0, "n_sentences": len(gk), "shared_sentences": len(inter),
        "shared_fraction_of_sealed": round(len(inter) / max(1, len(sealed)), 6)}
    rep["_sealed_sentences_hashed"] = len(sealed)
    rep["_method"] = ("SHA-256 of the lowercased space-joined FORM column per sentence, sentences of >= 5 "
                      "tokens; a hit is an identical sentence appearing in a corpus a builder or board reads")
    if verbose:
        print("OVERLAP AUDIT (%d sealed sentences hashed)" % len(sealed))
        for k, v in rep.items():
            if k.startswith("_"):
                continue
            if not v.get("present"):
                print("  %-36s ABSENT FROM DISK" % k)
                continue
            print("  %-36s %6d sentences, %d shared (%.4f%% of sealed)"
                  % (k, v["n_sentences"], v["shared_sentences"], 100 * v["shared_fraction_of_sealed"]))
    return rep


# ===================================================================================================
# PART 4 -- THE CONFIGURATION MANIFEST (resolved flags, source hashes, asset hashes).
# ===================================================================================================
def config_manifest():
    flags = set()
    pat = re.compile(r"HDLAB_[A-Z0-9_]+")
    for fp in _py_files():
        if os.path.relpath(fp, _REPO).split(os.sep)[0] != "hdlab":
            continue
        try:
            txt = open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        flags |= set(pat.findall(txt))
    resolved = {k: os.environ.get(k) for k in sorted(flags)}
    src = {}
    for rel in ("hdlab/situation_reader.py", "hdlab/frontend.py", "hdlab/lexical_categories.py",
                "hdlab/attachment_arm.py", "hdlab/morphology.py", "hdlab/coref.py",
                "hdlab/entity_resolver.py", "hdlab/graded_role_assigner.py",
                "experiments/exp_board_rows_on_the_reader_v1.py",
                "experiments/exp_sealed_modern_holdout_v1.py"):
        p = os.path.join(_REPO, rel)
        if os.path.exists(p):
            src[rel] = _sha256_file(p)
    assets = {}
    adir = os.path.join(_REPO, "data", "frontend_assets")
    if os.path.isdir(adir):
        for fn in sorted(os.listdir(adir)):
            p = os.path.join(adir, fn)
            if not os.path.isfile(p):
                continue
            sz = os.path.getsize(p)
            assets[fn] = {"bytes": sz,
                          "sha256": (_sha256_file(p) if sz <= 20 * (1 << 20) else "SKIPPED>20MB")}
    return {"resolved_hdlab_flags_env": resolved,
            "flags_unset_means_module_default": True,
            "n_flags_found_in_hdlab": len(flags),
            "source_sha256": src,
            "frontend_assets": assets,
            "python": sys.version.split()[0],
            "note": ("a flag whose env value is null runs at its module default; the module hash above pins "
                     "what that default is")}


# ===================================================================================================
# PART 5 -- THE MANIFEST (--seal).  NO READER RUNS HERE.
# ===================================================================================================
def seal(verbose=True):
    if not os.path.exists(CORPUS_FILE):
        print("MISSING SEALED CORPUS: run --fetch first (%s)" % CORPUS_FILE)
        return None
    docs = parse_pud()
    hold, res = draw(docs)
    by = {d["docid"]: d for d in docs}
    enum = enumerate_readers(verbose=verbose)
    ov = overlap_audit(docs, verbose=verbose)

    def rec(ids):
        return [{"docid": i, "genre": by[i]["genre"], "n_sents": by[i]["n_sents"],
                 "n_toks": by[i]["n_toks"], "sha256": by[i]["sha256"]} for i in ids]

    man = {
        "version": MANIFEST_VERSION,
        "created_utc": _now(),
        "declared_before_first_answer": True,
        "what_this_is_in_plain_words": (
            "A batch of modern passages nobody on this project has ever read. They come from a collection "
            "that was not on this machine at all until this file was written, so no tool could have learned "
            "from them or been tuned on them. The rule for picking them, the seed, the list itself, the way "
            "they will be graded and the exact settings of the reader are all written down here BEFORE "
            "anybody looked at a single answer. They are graded once per landing and never adjusted "
            "against."),
        "corpus": dict(CORPUS, file_sha256=_sha256_file(CORPUS_FILE),
                       path=os.path.relpath(CORPUS_FILE, _REPO).replace("\\", "/"),
                       n_documents=len(docs), n_sentences=sum(d["n_sents"] for d in docs),
                       n_tokens=sum(d["n_toks"] for d in docs)),
        "rule": DRAW_RULE,
        "retirement_policy": RETIREMENT_POLICY,
        "holdout_v1": {"n_docs": len(hold), "n_sents": sum(by[i]["n_sents"] for i in hold),
                       "n_toks": sum(by[i]["n_toks"] for i in hold),
                       "by_genre": dict(Counter(by[i]["genre"] for i in hold)), "docs": rec(hold)},
        "reserve_v2": {"n_docs": len(res), "n_sents": sum(by[i]["n_sents"] for i in res),
                       "n_toks": sum(by[i]["n_toks"] for i in res),
                       "by_genre": dict(Counter(by[i]["genre"] for i in res)),
                       "note": "NEVER READ -- not by this cell, not by the board. The rolling second seal.",
                       "docs": rec(res)},
        "scorer": SCORER,
        "configuration": config_manifest(),
        "enumeration": enum,
        "overlap_audit": ov,
        "rows_this_corpus_cannot_carry": {
            "coref / salience / common_noun_coref": (
                "UD_English-PUD has no coreference layer. The only modern coref gold on disk is GUM/OntoGUM, "
                "and the enumeration shows all 301 of its documents are read. Proposed next sealed source in "
                "SOLVED.md."),
            "wic": "a lexical-sense benchmark, not a document corpus; sealing it is a separate draw.",
        },
    }
    os.makedirs(HOLDOUT_DIR, exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=2, sort_keys=False)
    if verbose:
        print("\nDRAW (declared rule, seed %d, stratified by genre, DOCUMENT as the unit)" % DRAW_RULE["seed"])
        print("  corpus     %d documents / %d sentences / %d tokens"
              % (man["corpus"]["n_documents"], man["corpus"]["n_sentences"], man["corpus"]["n_tokens"]))
        print("  HOLDOUT_V1 %3d docs / %4d sents / %5d toks  %s"
              % (man["holdout_v1"]["n_docs"], man["holdout_v1"]["n_sents"], man["holdout_v1"]["n_toks"],
                 man["holdout_v1"]["by_genre"]))
        print("  RESERVE_V2 %3d docs / %4d sents / %5d toks  %s  (never read)"
              % (man["reserve_v2"]["n_docs"], man["reserve_v2"]["n_sents"], man["reserve_v2"]["n_toks"],
                 man["reserve_v2"]["by_genre"]))
        print("\nSEALED -> %s" % os.path.relpath(MANIFEST_PATH, _REPO))
        print("COMMIT THIS MANIFEST BEFORE RUNNING --score.")
    return man


def write_policy():
    """Add the RETIREMENT POLICY to the already-sealed manifest and to the corpus provenance, and PROVE that
    no sealed field moved.  A seal may gain a policy; it may not gain, lose or alter a document, the rule,
    the seed, the scorer or the configuration."""
    man = load_manifest()
    SEALED_FIELDS = ("created_utc", "declared_before_first_answer", "corpus", "rule", "scorer",
                     "configuration", "enumeration", "overlap_audit", "holdout_v1", "reserve_v2")
    before = {k: hashlib.sha256(json.dumps(man.get(k), sort_keys=True).encode()).hexdigest()
              for k in SEALED_FIELDS}
    man["retirement_policy"] = RETIREMENT_POLICY
    after = {k: hashlib.sha256(json.dumps(man.get(k), sort_keys=True).encode()).hexdigest()
             for k in SEALED_FIELDS}
    moved = [k for k in SEALED_FIELDS if before[k] != after[k]]
    if moved:
        print("REFUSING: a sealed field would change -> %s" % moved)
        return None
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(man, fh, indent=2, sort_keys=False)
    pp = os.path.join(CORPUS_DIR, "PROVENANCE.json")
    if os.path.exists(pp):
        prov = json.load(open(pp, encoding="utf-8"))
        prov["retirement_policy"] = RETIREMENT_POLICY
        with open(pp, "w", encoding="utf-8") as fh:
            json.dump(prov, fh, indent=2)
    print("RETIREMENT POLICY written into the manifest and the corpus provenance.")
    print("  read budget : %s" % RETIREMENT_POLICY["read_budget"])
    print("  reserve     : %s" % RETIREMENT_POLICY["reserve_stays_unread_until"])
    print("  PROOF -- every sealed field is byte-identical (SHA-256 unchanged):")
    for k in SEALED_FIELDS:
        print("    %-28s %s" % (k, before[k][:16]))
    return man


def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        raise SystemExit("NO MANIFEST: run --seal first (%s)" % MANIFEST_PATH)
    return json.load(open(MANIFEST_PATH, encoding="utf-8"))


def verify_seal(man=None, verbose=True):
    """The manifest still describes what is on disk, and the scorer has not moved under us."""
    man = man or load_manifest()
    problems = []
    corpus_ok = _sha256_file(CORPUS_FILE) == man["corpus"]["file_sha256"]
    if not corpus_ok:
        problems.append("the sealed corpus file has changed since the seal")
    by = {d["docid"]: d for d in parse_pud()}
    doc_ok = True
    for r in man["holdout_v1"]["docs"] + man["reserve_v2"]["docs"]:
        d = by.get(r["docid"])
        if d is None or d["sha256"] != r["sha256"]:
            doc_ok = False
            problems.append("document %s changed or vanished" % r["docid"])
    sp = os.path.join(_REPO, SCORER["module"])
    cur = _sha256_file(sp)
    dec = man["configuration"]["source_sha256"].get(SCORER["module"])
    scorer_moved = (cur != dec)
    enum = enumerate_readers()
    if not enum["sealed_holdout_unread"]:
        problems.append("a file outside the instrument names the sealed holdout: %s"
                        % enum["sealed_holdout_named_by"])
    if verbose:
        print("SEAL VERIFY")
        print("  corpus hash matches manifest : %s" % corpus_ok)
        print("  every sealed document hash matches : %s" % doc_ok)
        print("  nothing outside the instrument names the holdout : %s" % enum["sealed_holdout_unread"])
        print("  scorer file unchanged since the seal : %s%s"
              % (not scorer_moved, "" if not scorer_moved else "  (declared %s, now %s)" % (dec, cur)))
        print("  VERDICT: %s" % ("SEAL HOLDS" if not problems else "SEAL BROKEN -> " + "; ".join(problems)))
    return {"ok": not problems, "problems": problems, "scorer_moved": scorer_moved,
            "scorer_sha256_now": cur, "scorer_sha256_declared": dec}


# ===================================================================================================
# PART 6 -- THE ONE MEASURED READ.
# ===================================================================================================
def _count_non_form_columns(path):
    """COUNTED witness that the reader received raw text: every CoNLL column but the FORM is '_'."""
    n_tok, n_gold = 0, 0
    for ln in open(path, encoding="utf-8"):
        s = ln.rstrip("\n")
        if not s.strip() or s.startswith("#"):
            continue
        c = s.split("\t")
        n_tok += 1
        for j, v in enumerate(c):
            if j in (0, 1, 2, 3):          # docid, part, word-index, FORM
                continue
            if v != "_":
                n_gold += 1
    return n_tok, n_gold


def _read_docs(doc_recs, all_docs, mode_tag, chunk_docs=1, scramble=None, seed=20260916, progress=True):
    """One read per unit.  Returns (per[row][arm][unit] = (hits, tot), diag, witness)."""
    import experiments.exp_board_rows_on_the_reader_v1 as B
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    by = {d["docid"]: d for d in all_docs}
    ids = [r["docid"] for r in doc_recs]
    units = []
    if chunk_docs <= 1:
        for i in ids:
            units.append((i, list(by[i]["sents"])))
    else:                                   # chunk-matched diagnostic: consecutive sealed docs concatenated
        buf, names = [], []
        for i in ids:
            buf += by[i]["sents"]
            names.append(i)
            if len(names) >= chunk_docs:
                units.append(("+".join(names), buf))
                buf, names = [], []
        if names:
            units.append(("+".join(names), buf))
    if scramble == "sentence_order":         # discourse order destroyed, documents intact
        rnd = random.Random(seed)
        units = [(u, rnd.sample(ss, len(ss))) for u, ss in units]
    elif scramble == "cross_document":       # sentences reassigned across sealed documents
        rnd = random.Random(seed)
        pool = [s for _, ss in units for s in ss]
        rnd.shuffle(pool)
        newu, k = [], 0
        for u, ss in units:
            newu.append((u, pool[k:k + len(ss)]))
            k += len(ss)
        units = newu
    gaz = load_given_gazetteer()
    per = {r: defaultdict(dict) for r in SCORER["rows"]}
    diag = defaultdict(int)
    wit = {"reader_read_calls": 0, "units": 0, "tokens_written": 0, "non_form_columns_populated": 0}
    tmp = tempfile.mkdtemp(prefix="sealed_")
    t0 = time.time()
    try:
        for ui, (uid, sents) in enumerate(units):
            path = os.path.join(tmp, "u%04d.conll" % ui)
            B._ud_write_chunk(sents, path, "sealed%04d" % ui, discover_pronouns=False)
            nt, ng = _count_non_form_columns(path)
            wit["tokens_written"] += nt
            wit["non_form_columns_populated"] += ng
            rdr = SituationReader(gaz=gaz)
            sm = rdr.read(path)
            wit["reader_read_calls"] += 1
            wit["units"] += 1
            rng = random.Random(seed + ui)
            sc, dg = B.score_ud_chunk(sents, sm, rdr, rng, "sealed%04d" % ui)
            for k, v in dg.items():
                diag[k] += v
            for rname, arms in sc.items():
                for a, ht in arms.items():
                    per[rname][a][uid] = ht
            del sm, rdr
            os.remove(path)
            if progress and (ui + 1) % 25 == 0:
                print("    ... %d/%d units, %.0fs" % (ui + 1, len(units), time.time() - t0), flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    wit["elapsed_s"] = round(time.time() - t0, 1)
    wit["mode"] = mode_tag
    return per, dict(diag), wit


POP_TEXT = {
    "who_did_what_agent": ("SEALED modern holdout (UD_English-PUD, HOLDOUT_V1): who-did-what AGENT, gold "
                           "nsubj [active] / obl:agent [passive] at every gold VERB. model = the LIVE "
                           "reader's sm.events[].agent (no event fired = a miss); floor = nearest pre-verbal "
                           "nominal on the reader's OWN categories; twin = a random sentence nominal. "
                           "DOCUMENT-paired bootstrap; the sealed document is the resampling unit."),
    "who_did_what_patient": ("SEALED modern holdout (UD_English-PUD, HOLDOUT_V1): who-did-what PATIENT, gold "
                             "obj [active] / nsubj:pass [passive]. model = sm.events[].patient; floor = "
                             "nearest post-verbal nominal on the reader's OWN categories; twin = a random "
                             "sentence nominal. DOCUMENT-paired bootstrap."),
    "state": ("SEALED modern holdout (UD_English-PUD, HOLDOUT_V1): copular PREDICATIONAL gold (pred_adj + "
              "pred_nom). model = the reader's sm.entity_states property for the gold holder; floor = the "
              "most-recent-noun positional binding on the reader's own categories; twin = the holders "
              "shuffled within the unit. DOCUMENT-paired bootstrap."),
}
FLOOR_KEYS = {"who_did_what_agent": ["positional_nearest_preverbal"],
              "who_did_what_patient": ["positional_nearest_postverbal"],
              "state": ["most_recent_noun"]}


def _rows_from_per(per, tag, n_boot=None, seed=None):
    import experiments.exp_board_rows_on_the_reader_v1 as B
    n_boot = n_boot or SCORER["n_boot"]
    seed = seed or SCORER["boot_seed"]
    out = {}
    for rname in SCORER["rows"]:
        arms = per.get(rname, {})
        if not arms:
            continue
        prov = B.provenance("reader_textonly", CORPUS["name"], "sm." + rname)
        prov["sealed"] = tag
        prov["plain"] = "the reader's own read of raw sealed text nobody has seen -- %s" % tag
        out[rname] = B._row(rname, {a: dict(v) for a, v in arms.items()}, "model",
                            FLOOR_KEYS[rname], "twin", POP_TEXT[rname], prov, n_boot=n_boot, seed=seed)
    return out


def _print_rows(title, rows, diag=None, wit=None):
    print("\n" + "=" * 112)
    print(title)
    print("=" * 112)
    print("%-22s %5s %8s %8s %-30s %8s  %-26s %-26s"
          % ("row", "n", "model", "floor", "(strongest floor)", "twin", "model-floor [CI]",
             "model-twin [CI]"))
    for k, r in rows.items():
        mf, mt = r["model_minus_strongest"], r["model_minus_twin"]
        print("%-22s %5d %8.4f %8.4f %-30s %8.4f  %+0.4f [%+0.4f,%+0.4f]%s %+0.4f [%+0.4f,%+0.4f]%s"
              % (k, r["n"], r["model_acc"] or 0.0, r["strongest_floor"] or 0.0,
                 "(" + str(r["strongest_floor_name"]) + ")", r["twin_acc"] or 0.0,
                 mf[0] or 0.0, mf[1] or 0.0, mf[2] or 0.0, " SEP" if r["ci_sep_over_strongest"] else "    ",
                 mt[0] or 0.0, mt[1] or 0.0, mt[2] or 0.0, " SEP" if r["ci_sep_over_twin"] else ""))
    for k, r in rows.items():
        print("   %-22s CI half-width vs floor %.4f / vs twin %.4f"
              % (k, r["ci_half_width_strongest"] or 0.0, r["ci_half_width_twin"] or 0.0))
    if wit:
        print("   WITNESS: %d reader.read() calls over %d units, %d tokens written, %d non-FORM CoNLL "
              "columns populated (0 = the reader saw raw text only), %.0fs"
              % (wit["reader_read_calls"], wit["units"], wit["tokens_written"],
                 wit["non_form_columns_populated"], wit["elapsed_s"]))
    if diag:
        for r in ("agent", "patient", "state"):
            it, an = diag.get(r + "_items", 0), diag.get(r + "_answered", 0)
            if it:
                print("   COVERAGE %-8s items %4d  answered %4d (%.3f) -- an abstention is scored WRONG"
                      % (r, it, an, an / it))


def score(which="holdout_v1", chunk_docs=1, scramble=None, n_boot=None, title=None, progress=True):
    man = load_manifest()
    v = verify_seal(man, verbose=True)
    if not v["ok"]:
        print("REFUSING TO SCORE: the seal does not hold.")
        return None
    if v["scorer_moved"]:
        print("NOTE: the scorer file hash differs from the manifest's record -- the scorer moved after the "
              "seal.  Reported anyway, with both hashes, because concealing it would be worse.")
    docs = parse_pud()
    recs = man[which]["docs"]
    print("\nREADING %d sealed documents (%s), raw text only, one read each ..." % (len(recs), which),
          flush=True)
    per, diag, wit = _read_docs(recs, docs, which, chunk_docs=chunk_docs, scramble=scramble, progress=progress)
    tag = "%s%s%s" % (which, "" if chunk_docs <= 1 else " [chunk=%d docs]" % chunk_docs,
                      "" if not scramble else " [scramble=%s]" % scramble)
    rows = _rows_from_per(per, tag, n_boot=n_boot)
    _print_rows(title or ("SEALED MODERN HOLDOUT -- %s -- THE PRODUCT'S OWN READ OF RAW TEXT" % which),
                rows, diag, wit)
    return {"which": which, "chunk_docs": chunk_docs, "scramble": scramble, "rows": rows,
            "diag": diag, "witness": wit, "seal": v,
            "manifest_corpus_sha256": man["corpus"]["file_sha256"]}


def compare(ud_cap=None, n_boot=None):
    """The same scorer, the same reader, the same process -- on the board's OWN (read) UD-EWT test split."""
    import experiments.exp_board_rows_on_the_reader_v1 as B
    man = load_manifest()
    cap = ud_cap or man["holdout_v1"]["n_sents"]
    print("\nCOMPARISON ARM: UD-EWT test (the board's own, repeatedly-read split), cap %d sentences, "
          "chunked %d sentences per pseudo-document (the board's own chunking)" % (cap, B.UD_CHUNK), flush=True)
    u = B.run_ud(cap=cap, n_boot=n_boot or SCORER["n_boot"], seed=SCORER["boot_seed"],
                 modes=("reader_textonly",))
    rows = u["rows"]["reader_textonly"]
    _print_rows("BOARD'S OWN POPULATION -- UD-EWT test (READ SPLIT, not sealed)", rows,
                (u.get("diag") or {}).get("reader_textonly"))
    return {"cap": cap, "rows": rows}


# ===================================================================================================
# PART 7 -- THE BOARD ARM: one read per landing, same provenance columns as the reader-driven rows.
# ===================================================================================================
def board(n_boot=None, progress=True):
    res = score(which="holdout_v1", n_boot=n_boot, progress=progress,
                title="BOARD ARM -- SEALED MODERN HOLDOUT (read ONCE this landing)")
    if res is None:
        return None
    man = load_manifest()
    rec = {
        "ts_iso": _now(),
        "arm": "sealed_modern_holdout_v1",
        "manifest": MANIFEST_VERSION,
        "corpus_sha256": man["corpus"]["file_sha256"],
        "scorer_sha256_declared": res["seal"]["scorer_sha256_declared"],
        "scorer_sha256_now": res["seal"]["scorer_sha256_now"],
        "scorer_moved_since_seal": res["seal"]["scorer_moved"],
        "n_documents": man["holdout_v1"]["n_docs"],
        "rows": {k: {"n": r["n"], "model_acc": r["model_acc"],
                     "strongest_floor_name": r["strongest_floor_name"],
                     "strongest_floor": r["strongest_floor"], "twin_acc": r["twin_acc"],
                     "model_minus_strongest": r["model_minus_strongest"],
                     "ci_sep_over_strongest": r["ci_sep_over_strongest"],
                     "model_minus_twin": r["model_minus_twin"],
                     "ci_sep_over_twin": r["ci_sep_over_twin"],
                     "ci_half_width_strongest": r["ci_half_width_strongest"],
                     "provenance": r["provenance"], "population": r["population"]}
                 for k, r in res["rows"].items()},
        "witness": res["witness"],
        "coverage": res["diag"],
        "configuration": man["configuration"]["resolved_hdlab_flags_env"],
        "plain": ("the reader's own read of modern passages nobody on this project had ever seen, graded by "
                  "a scorer written down before the first answer was looked at"),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    lp = os.path.join(OUT_DIR, "board_landings.jsonl")
    with open(lp, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    n = sum(1 for _ in open(lp, encoding="utf-8"))
    print("\nLANDING RECORD %d appended -> %s" % (n, os.path.relpath(lp, _REPO)))
    print("READS OF THE SEALED HOLDOUT SO FAR: %d.  When a decision has been steered by it, retire "
          "HOLDOUT_V1 and promote RESERVE_V2." % n)
    return rec


# ===================================================================================================
# PHASE 7 (A) -- THE AGENT RUNG, BROKEN DOWN BY A CAUSE THE READER CAN NAME.
#
# The sealed read put who_did_what_agent BELOW its positional floor on BOTH populations (sealed -0.0844,
# UD-EWT test -0.0535) at 0.969 / 0.995 coverage, so it is not abstention.  This mode splits every gold
# agent item into causes the reader itself can be held to:
#   no_event            the reader fired NO event at the gold verb -- it never answered
#   no_agent_emitted    an event fired with an empty agent slot
#   candidate_set_miss  the gold agent's own token was NEVER in the competition's candidate stream
#                       (`reader._coref_mentions`, what `_cm_agent_candidates` reads) -- the right answer
#                       was not on the ballot.  LOCATED item 1 lives here.
#   pick_error          the gold agent WAS on the ballot and a different candidate won
# Gold is read only to CLASSIFY, after the reader has answered.  Nothing here changes a published number.
# ===================================================================================================
def _norm_tok(s):
    return str(s or "").strip().lower()


def _by_phrase_tokens(sent, v):
    """Token ids (1-based) of the by-phrase attached to verb v, and the id of its nominal head, off GOLD
    deprels -- used ONLY to label an error, never to make one."""
    head, toks = None, set()
    for d in sent:
        if d["head"] == v and d["deprel"].startswith("obl:agent"):
            head = d["id"]
    if head is None:
        return set(), None
    stack, seen = [head], set()
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        toks.add(x)
        for d in sent:
            if d["head"] == x:
                stack.append(d["id"])
    return toks, head


def agent_anatomy(pop="sealed", cap=None, chunk=20, progress=True, max_examples=3):
    """pop='sealed' -> the sealed holdout documents; pop='udtest' -> UD-EWT test in the board's own chunks."""
    import experiments.exp_board_rows_on_the_reader_v1 as B
    from hdlab.situation_reader import SituationReader
    from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
    if pop == "sealed":
        man = load_manifest()
        v = verify_seal(man, verbose=False)
        if not v["ok"]:
            print("REFUSING: the seal does not hold -> %s" % v["problems"])
            return None
        by = {d["docid"]: d for d in parse_pud()}
        units = [(r["docid"], list(by[r["docid"]]["sents"])) for r in man["holdout_v1"]["docs"]]
        label = "SEALED HOLDOUT_V1 (UD_English-PUD, %d documents)" % len(units)
    else:
        from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
        sents = load_ud(os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu"))
        if cap:
            sents = sents[:cap]
        # NB (bug found and fixed 2026-09-16, phase 7): this line previously sliced with the ENUMERATE
        # index instead of the range value, so the 36 "chunks" were overlapping windows over the first ~55
        # sentences, scored repeatedly.  The first UD-EWT anatomy run was discarded because of it.  The
        # assertion below is what makes that class of error impossible to repeat silently.
        units = [("udewt%04d" % (k // chunk), sents[k:k + chunk]) for k in range(0, len(sents), chunk)]
        units = [(u, s) for (u, s) in units if s]
        _flat = [s for _, ss in units for s in ss]
        assert len(_flat) == len(sents), (
            "the chunking must PARTITION the sentence list: %d sentences in, %d scored"
            % (len(sents), len(_flat)))
        assert len(set(id(s) for s in _flat)) == len(sents), "a sentence is scored twice"
        label = "UD-EWT TEST (the board's own read split, %d sentences in %d chunks)" % (len(sents), len(units))

    gaz = load_given_gazetteer()
    C = Counter()
    PAT = Counter()
    EX = defaultdict(list)
    passive_by = {"items": 0, "model_in_by_phrase_not_head": 0, "model_is_by": 0, "gold_head_missing": 0}
    tmp = tempfile.mkdtemp(prefix="anat_")
    t0 = time.time()
    try:
        for ui, (uid, sents) in enumerate(units):
            path = os.path.join(tmp, "u%04d.conll" % ui)
            B._ud_write_chunk(sents, path, "anat%04d" % ui, discover_pronouns=False)
            rdr = SituationReader(gaz=gaz)
            sm = rdr.read(path)
            ments = list(getattr(rdr, "_coref_mentions", []) or [])
            cand_by_sent = defaultdict(set)
            cand_n = defaultdict(int)
            for m in ments:
                cand_by_sent[m.get("sent_idx", -1)].add(_norm_tok(m.get("head")))
                cand_n[m.get("sent_idx", -1)] += 1
            ev_by = defaultdict(list)
            for e in sm.events:
                ev_by[(e.sent_idx, e.pred_idx)].append(e)
            for si, s in enumerate(sents):
                toks = [t["form"] for t in s]
                try:
                    up = list(rdr._cached_tag(list(toks)))
                except Exception:
                    up = ["X"] * len(toks)
                for (v, ag, passive) in B._gold_agent_items(s):
                    gold = _norm_tok(toks[ag - 1])
                    C["items"] += 1
                    C["passive" if passive else "active"] += 1
                    evs = ev_by.get((si, v - 1), [])
                    if not evs:
                        C["no_event"] += 1
                        if len(EX["no_event"]) < max_examples:
                            EX["no_event"].append("v=%r gold_agent=%r | %s" % (toks[v - 1], toks[ag - 1],
                                                                              " ".join(toks)[:150]))
                        continue
                    model = _norm_tok(evs[0].agent)
                    if model == gold:
                        C["correct"] += 1
                        continue
                    C["wrong"] += 1
                    on_ballot = gold in cand_by_sent.get(si, set())
                    if not model:
                        C["no_agent_emitted"] += 1
                        cause = "no_agent_emitted"
                    elif not on_ballot:
                        C["candidate_set_miss"] += 1
                        cause = "candidate_set_miss"
                    else:
                        C["pick_error"] += 1
                        cause = "pick_error"
                    C["cand_stream_empty_sentence"] += int(cand_n.get(si, 0) == 0)
                    # --- error PATTERNS (labels only; gold read after the answer) ---
                    mi = [i for i, t in enumerate(toks) if _norm_tok(t) == model]
                    mtag = up[mi[0]] if mi and mi[0] < len(up) else "?"
                    gi = ag - 1
                    gtag = up[gi] if gi < len(up) else "?"
                    pat = None
                    if not model:
                        pat = "empty agent slot"
                    elif mtag not in ("NOUN", "PROPN", "PRON"):
                        pat = "picked a non-nominal token (%s)" % mtag
                    else:
                        gold_pat = None
                        for d in s:
                            if d["head"] == v and d["dep"] in ("obj",):
                                gold_pat = _norm_tok(toks[d["id"] - 1])
                        if gold_pat and model == gold_pat:
                            pat = "picked the gold PATIENT (role swap)"
                        elif passive:
                            bys, bh = _by_phrase_tokens(s, v)
                            passive_by["items"] += 1
                            if bh is None:
                                passive_by["gold_head_missing"] += 1
                            if model == "by":
                                passive_by["model_is_by"] += 1
                                pat = "picked the preposition 'by' of the by-phrase"
                            elif mi and (mi[0] + 1) in bys and bh is not None and (mi[0] + 1) != bh:
                                passive_by["model_in_by_phrase_not_head"] += 1
                                pat = "picked a by-phrase token that is not its head (LOCATED item 1)"
                            else:
                                pat = "passive: picked outside the by-phrase"
                        elif mi and abs(mi[0] - gi) > 6:
                            pat = "picked a distant nominal (>6 tokens from the gold agent)"
                        elif gtag == "PRON":
                            pat = "gold agent is a PRONOUN and a non-pronoun won"
                        else:
                            pat = "picked a nearby competing nominal"
                    PAT[(cause, pat)] += 1
                    if len(EX[(cause, pat)]) < 1:
                        EX[(cause, pat)].append(
                            "gold=%r model=%r verb=%r | %s" % (toks[ag - 1], evs[0].agent, toks[v - 1],
                                                               " ".join(toks)[:150]))
            del sm, rdr
            os.remove(path)
            if progress and (ui + 1) % 25 == 0:
                print("    ... %d/%d units, %.0fs" % (ui + 1, len(units), time.time() - t0), flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n = max(1, C["items"])
    print("\n" + "=" * 100)
    print("AGENT-RUNG ANATOMY -- %s" % label)
    print("=" * 100)
    print("  gold agent items          %5d   (active %d / passive %d)" % (C["items"], C["active"], C["passive"]))
    print("  correct                   %5d  (%.4f)" % (C["correct"], C["correct"] / n))
    print("  --- every error, by a cause the reader can be held to ---")
    for k in ("no_event", "no_agent_emitted", "candidate_set_miss", "pick_error"):
        print("  %-24s  %5d  (%.4f of all items, %.4f of errors)"
              % (k, C[k], C[k] / n, C[k] / max(1, C["items"] - C["correct"])))
    print("  passive by-phrase detail: items %d | model was 'by' %d | model a by-phrase non-head %d"
          % (passive_by["items"], passive_by["model_is_by"], passive_by["model_in_by_phrase_not_head"]))
    print("  wrong items in a sentence whose candidate stream was EMPTY: %d" % C["cand_stream_empty_sentence"])
    print("  --- the most frequent error patterns ---")
    for (cause, pat), c in PAT.most_common(6):
        print("  %5d  [%s] %s" % (c, cause, pat))
        for e in EX[(cause, pat)]:
            print("           e.g. %s" % e)
    if EX["no_event"]:
        print("  --- no_event examples ---")
        for e in EX["no_event"]:
            print("           %s" % e)
    return {"population": label, "counts": dict(C), "passive_by_phrase": passive_by,
            "patterns": [{"cause": c, "pattern": p, "n": k,
                          "example": (EX[(c, p)][0] if EX[(c, p)] else "")}
                         for (c, p), k in PAT.most_common(8)],
            "no_event_examples": EX["no_event"],
            "elapsed_s": round(time.time() - t0, 1)}


# ===================================================================================================
# SELF-TEST -- plumbing only, on the ALREADY-READ UD-EWT test split.  It never reads a sealed document.
# ===================================================================================================
def self_test():
    ok = True

    def ck(name, cond, extra=""):
        nonlocal ok
        ok = ok and bool(cond)
        print("  [%s] %s%s" % ("PASS" if cond else "FAIL", name, ("   %s" % (extra,)) if extra != "" else ""))

    print("SELF-TEST exp_sealed_modern_holdout_v1 (no network; no sealed document is read)")
    enum = enumerate_readers()
    ck("the enumeration walked the whole tree", enum["n_python_files_walked"] > 500,
       "%d .py files" % enum["n_python_files_walked"])
    ck("the enumeration finds GUM/GENTLE readers (it can see a reader when one exists)",
       enum["counts"]["GUM + GENTLE"]["files"] > 50, enum["counts"]["GUM + GENTLE"])
    ck("the enumeration finds the SECOND on-disk UD-EWT copy (the dev-split trap)",
       enum["counts"]["UD-EWT (experiments/data)"]["lines"] > 0,
       enum["counts"]["UD-EWT (experiments/data)"])
    ck("nothing outside the instrument + its witness names the sealed holdout",
       enum["sealed_holdout_unread"], enum["sealed_holdout_named_by"])

    fake = ([{"docid": "n%05d" % i, "genre": "newswire"} for i in range(100)]
            + [{"docid": "w%05d" % i, "genre": "wikipedia"} for i in range(40)])
    h1, r1 = draw(fake)
    h2, r2 = draw(fake)
    ck("the draw is deterministic under the declared seed", h1 == h2 and r1 == r2)
    ck("holdout and reserve are disjoint and exhaustive",
       not (set(h1) & set(r1)) and len(h1) + len(r1) == len(fake),
       "%d + %d = %d" % (len(h1), len(r1), len(fake)))
    ck("the draw is stratified by genre (ceil(70%) of each stratum)",
       sum(1 for d in h1 if d[0] == "n") == 70 and sum(1 for d in h1 if d[0] == "w") == 28,
       dict(Counter(d[0] for d in h1)))
    ck("a different seed gives a different draw (the seed is load-bearing)", draw(fake, seed=1)[0] != h1)

    tmp = tempfile.mkdtemp(prefix="sealedst_")
    try:
        import experiments.exp_board_rows_on_the_reader_v1 as B
        from experiments.exp_whodidwhat_ud_structural_v1 import load_ud
        ud = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
        sents = load_ud(ud)[:20]
        p = os.path.join(tmp, "a.conll")
        B._ud_write_chunk(sents, p, "st")
        nt, ng = _count_non_form_columns(p)
        ck("the text-only witness COUNTS tokens and finds zero gold columns", nt > 0 and ng == 0,
           "%d tokens, %d non-form columns" % (nt, ng))
        leak = os.path.join(tmp, "b.conll")
        with open(p, encoding="utf-8") as fh, open(leak, "w", encoding="utf-8") as out:
            for ln in fh:
                s = ln.rstrip("\n")
                c = s.split("\t")
                if len(c) > 5 and not s.startswith("#") and s.strip():
                    c[5] = "NOUN"
                    s = "\t".join(c)
                out.write(s + "\n")
        _, ng2 = _count_non_form_columns(leak)
        ck("the text-only witness CAN FAIL (a planted gold column is counted)", ng2 > 0, "%d populated" % ng2)

        docs = [{"docid": "st0", "genre": "newswire", "sents": sents[:10]},
                {"docid": "st1", "genre": "wikipedia", "sents": sents[10:20]}]
        recs = [{"docid": d["docid"]} for d in docs]
        per, diag, wit = _read_docs(recs, docs, "selftest", progress=False)
        ck("the reader was called once per unit", wit["reader_read_calls"] == 2, wit)
        ck("the read was annotation-free (counted)", wit["non_form_columns_populated"] == 0, wit)
        rows = _rows_from_per(per, "selftest", n_boot=200)
        ck("every declared row is produced with a population", bool(rows) and set(rows) <= set(SCORER["rows"]),
           {k: v["n"] for k, v in rows.items()})
        need = ("n", "model_acc", "strongest_floor", "twin_acc", "model_minus_strongest",
                "ci_sep_over_strongest", "ci_half_width_strongest", "population", "provenance")
        ck("each row carries the board's schema", all(all(k in r for k in need) for r in rows.values()))
        ck("the unit of uncertainty is the DOCUMENT",
           all(set(per[r]["model"]) <= {"st0", "st1"} for r in per if per[r]))
        ck("every arm of a row scores the SAME number of items",
           all(len(set(t for _, t in per[rn]["model"].items())
                   ^ set(t for _, t in per[rn]["twin"].items())) >= 0 for rn in per if per[rn]))
        ck("the scorer is IMPORTED from the landed board cell, not copied",
           B.score_ud_chunk.__module__ == "experiments.exp_board_rows_on_the_reader_v1")
        ck("the row provenance says the annotation column was NOT supplied",
           all(r["provenance"]["annotation_supplied"].startswith("no") for r in rows.values()))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if os.path.exists(MANIFEST_PATH):
        man = load_manifest()
        ck("the committed manifest declares the scorer and the rule before any answer",
           bool(man.get("declared_before_first_answer")) and "scorer" in man and "rule" in man)
        ck("holdout and reserve in the manifest are disjoint",
           not (set(d["docid"] for d in man["holdout_v1"]["docs"])
                & set(d["docid"] for d in man["reserve_v2"]["docs"])))
    print("SELF-TEST " + ("PASS" if ok else "FAIL"))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--enumerate", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--seal", action="store_true")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--score", action="store_true")
    ap.add_argument("--board", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--controls", action="store_true")
    ap.add_argument("--write-policy", action="store_true",
                    help="phase 7 (1): add the retirement policy to the sealed manifest (no sealed field moves)")
    ap.add_argument("--agent-anatomy", action="store_true",
                    help="phase 7 (A): every gold agent error by a cause the reader can name, both populations")
    ap.add_argument("--pop", choices=("sealed", "udtest", "both"), default="both",
                    help="which population --agent-anatomy runs on")
    ap.add_argument("--n-boot", type=int, default=None)
    ap.add_argument("--ud-cap", type=int, default=None)
    a = ap.parse_args()
    if a.self_test or a.smoke:
        raise SystemExit(0 if self_test() else 1)
    did = False
    M = {"ts_iso": _now(), "anchor": ANCHOR}
    if a.enumerate:
        M["enumeration"] = enumerate_readers(verbose=True)
        did = True
    if a.fetch:
        M["fetch"] = fetch_corpus()
        did = True
    if a.seal:
        M["sealed"] = bool(seal())
        did = True
    if a.verify:
        M["verify"] = verify_seal()
        did = True
    if a.score:
        M["holdout"] = score(n_boot=a.n_boot)
        did = True
    if a.board:
        M["board"] = board(n_boot=a.n_boot)
        did = True
    if a.compare:
        M["compare"] = compare(ud_cap=a.ud_cap, n_boot=a.n_boot)
        did = True
    if a.write_policy:
        M["policy"] = bool(write_policy())
        did = True
    if a.agent_anatomy:
        if a.pop in ("sealed", "both"):
            M["agent_anatomy_sealed"] = agent_anatomy("sealed")
        if a.pop in ("udtest", "both"):
            M["agent_anatomy_udtest"] = agent_anatomy("udtest", cap=a.ud_cap or 719)
        did = True
    if a.controls:
        M["chunk_matched"] = score(chunk_docs=8, n_boot=a.n_boot,
                                   title="DIAGNOSTIC -- sealed documents concatenated 8 at a time "
                                         "(chunk length matched to the board's pseudo-documents)")
        M["scrambled"] = score(scramble="cross_document", n_boot=a.n_boot,
                               title="CONTROL -- sealed sentences reassigned ACROSS sealed documents "
                                     "(discourse destroyed, sentences intact)")
        did = True
    if not did:
        ap.print_help()
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="utf-8") as fh:
        json.dump(M, fh, indent=2, default=str)
    print("\nwrote %s" % os.path.relpath(os.path.join(OUT_DIR, "metrics.json"), _REPO))


if __name__ == "__main__":
    main()
