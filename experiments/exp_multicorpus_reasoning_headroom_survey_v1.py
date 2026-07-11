"""
multicorpus_reasoning_headroom_survey_v1 -- SURVEY of degree-stratified reasoning-HEADROOM over frequency
across a LADDER of real KG/commonsense corpora, to pick the durable-escape reasoning corpus ON MERIT.

WHY. The fairness VET (aa7f151f) proved FB15k-237's aggregate "beat frequency" bar is UNFAIR: its
high-degree hub tails are FREQUENCY-GUESSABLE by construction (POP hits@10 saturates the reach-ceiling at
the hub end -> HIGH stratum headroom collapses to ~0.03). The CSKG dense-core ACCEPTANCE cell
(exp_cskg_dense_core_headroom_acceptance_v1) landed the apparatus + validated its discriminator on two
SYNTHETIC anchors:
    CITED@notes: SYN_COMPOSITIONAL headroom=0.86 (reach 1.0, POP 0.14 -- what a GREAT reasoning corpus looks
    like); SYN_FREQ_GUESSABLE headroom=0.0 (the must-fail control fires).
This cell reuses that EXACT apparatus (identical Graph / mine_rules / reachable / pop_rank / headroom_table
code path) to run the SAME degree-stratified reach-ceiling-vs-frequency-headroom measurement across a whole
LADDER of real corpora side-by-side with the two synthetic anchors, and RANKS them by fair-derivable-
reasoning headroom. The winner = the real corpus with the best cross-strata (incl higher-degree) reasoning
headroom over frequency = our durable-escape corpus candidate. MEASURE, do not assume any corpus is best.

FAIR-HEADROOM SCORE (per corpus). fair_score = min(LOW, MID, HIGH) stratum headroom -- rewards a corpus
with material reasoning reach over frequency ACROSS ALL degree strata INCLUDING higher degree (a durable
reasoning testbed cannot collapse at the hub end the way FB15k-237 does). Tiebreak: HIGH-stratum headroom,
then ALL headroom. Corpora ranked descending; the two synthetics are FIXED references (upper / lower).

LADDER (each run through the IDENTICAL headroom apparatus, gold-tail degree-tertile stratified):
  SYN_COMPOSITIONAL   -- upper reference (analytic headroom-HIGH at any scale); POSITIVE control.
  SYN_FREQ_GUESSABLE  -- lower reference (analytic headroom~0 at any scale); MUST-FAIL control.
  FB15K237            -- the VET's corpus; reference reproducer + real-corpus hub-collapse witness.
  WN18RR              -- sparse/hierarchical control; expected LOW real-corpus must-fail witness.
  CODEX_S / CODEX_M / CODEX_L  -- CoDEx Wikidata subsets (small/med/large; degree ladder within Wikidata).
  CSKG_XCUT_CORE      -- CSKG cross-cutting commonsense k=12 dense core (the ACCEPTANCE candidate).
  CONCEPTNET_SLICE    -- ConceptNet English slice (best-effort; local file if present).

FAIRNESS + LOCALIZATION (mandatory). Per corpus per stratum: reach-ceiling (info-ceiling a perfect reasoner
could reach) + POP_RELFREQ (frequency baseline) + HEADROOM (achieved-reachable-AND-freq-misses = the win a
perfect reasoning ranker gets over frequency). The apparatus is proven to DISCRIMINATE by the two synthetic
anchors: SYN_FREQ_GUESSABLE + SYN_COMPOSITIONAL are scale-invariant analytic gates. If the freq-guessable
control shows headroom, the apparatus is broken and the WHOLE survey is INCONCLUSIVE (not a ranking).

RESILIENCE. A SURVEY stages what is reachable: each real corpus is best-effort. A corpus whose data cannot
be self-acquired (network / mirror failure) is recorded with a failure_class and EXCLUDED from the ranking
(surfaced in verdict_msg, NOT silently dropped). The survey requires the two synthetic anchors + FB15k-237
(the guaranteed reproducer) to succeed; other rungs are opportunistic.

## Compute architecture
Class (b) sequential-CPU with justification: pure symbolic relational hash-joins + dict lookups (mine_rules
L2 path composition, reachable-set traversal, filtered ranking, iterative k-core degree-peel). NO substrate
vectors, NO bind/unbind, NO matmul -- combinatorial graph traversal, not linear algebra; GPU batching does
not apply. Same justification as the imported FB15k-237 STEP-1 apparatus. Storage strategy: no_storage /
no_composition (no substrate vectors stored or composed).

ASCII-only. write_metrics (tmp+os.replace atomic). RUN_MODE defaults to full (runner invokes with no argv).
--smoke = tiny LOCAL harness validation (2 synthetic anchors + one capped-FB rung, offline, no downloads).
--self-test = scale-invariant synthetic discriminators + ranking-function unit test (no network).
"""
from __future__ import annotations
import sys, os, argparse, time, json, random, traceback, platform, urllib.request
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
# APPARATUS REUSE (apples-to-apples; identical code path as the FB15k-237 VET + the CSKG acceptance cell).
from experiments.exp_gt_induction_fb15k237_dense_v1 import _load_fb15k237, _load_triples
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (
    headroom_table, build_syn_compositional, build_syn_freq_guessable,
    build_cskg_core_triples, _table_digest, _mean_strata, _ensure_cskg,
)

ANCHOR_NAME = "multicorpus_reasoning_headroom_survey_v1"

# ---- run mode / config -------------------------------------------------------
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Rule-mining params -- MATCHED to the FB15k-237 FULL / CSKG-acceptance regime (calibration_check:
# default_ok_for_this_regime; the same MIN_SUPPORT/MIN_CONF the VET + acceptance cell used -> comparable).
MIN_SUPPORT_REAL = 10
CSKG_KCORE = 12
CSKG_MAX_LINES = 0
CSKG_MAX_NODES = 0

if RUN_MODE == "smoke":
    SEEDS = [7]
    N_EVAL = 150
    FB_SMOKE_CAP = 15000          # cap FB train so mining is fast; smoke proves HARNESS wiring, not FB values
    MIN_SUPPORT_SMOKE = 3
    LADDER_KIND = "smoke"
else:
    SEEDS = [7, 17, 23]
    N_EVAL = 3000
    FB_SMOKE_CAP = 0
    MIN_SUPPORT_SMOKE = MIN_SUPPORT_REAL
    LADDER_KIND = "full"

VILLMOW = "https://raw.githubusercontent.com/villmow/datasets_knowledge_embedding/master/"
DETTMERS = "https://raw.githubusercontent.com/TimDettmers/ConvE/master/"
CODEX_BASE = "https://raw.githubusercontent.com/tsafavi/codex/master/data/triples/codex-%s/"


# ============================ corpus loaders ==================================
def _basic_prov(name, train, valid, test):
    nodes = set()
    for tr in (train, valid, test):
        for (h, _r, t) in tr:
            nodes.add(h); nodes.add(t)
    n = len(train) + len(valid) + len(test)
    rels = {r for tr in (train, valid, test) for (_h, r, _t) in tr}
    return dict(corpus=name, n_nodes=len(nodes), n_edges=n, avgdeg=(2.0 * n / max(1, len(nodes))),
                n_train=len(train), n_valid=len(valid), n_test=len(test), n_rel=len(rels))


def _fetch_split_files(dest_dir, bases, files=("train.txt", "valid.txt", "test.txt")):
    """Provision train/valid/test.txt into dest_dir, trying each base URL in turn (explicit mirror
    fallback; NOT a silent-continue -- if ALL mirrors fail for a file we return False loudly)."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    errs = []
    for fn in files:
        p = dest_dir / fn
        if p.exists() and p.stat().st_size > 0:
            continue
        ok = False
        for base in bases:
            try:
                tmp = str(p) + ".tmp"
                urllib.request.urlretrieve(base + fn, tmp)
                if os.path.getsize(tmp) > 0:
                    os.replace(tmp, str(p)); ok = True; break
            except Exception as e:                       # explicit mirror-fallback; last error recorded
                errs.append("%s: %s: %s" % (base + fn, type(e).__name__, str(e)[:80]))
                continue
        if not ok:
            print("[fetch] FAILED %s (all mirrors): %s" % (fn, " | ".join(errs[-3:])), flush=True)
            return False
    return True


def _load_fb(seed):
    tr, va, te = _load_fb15k237()
    if FB_SMOKE_CAP and len(tr) > FB_SMOKE_CAP:          # smoke-only: cap train so mining is fast
        rng = random.Random(1234)
        tr = rng.sample(tr, FB_SMOKE_CAP)
    return tr, va, te, _basic_prov("FB15K237", tr, va, te)


def _load_wn18rr(seed):
    d = REPO / "data" / "wn18rr_testbed"
    bases = [VILLMOW + "WN18RR/text/", VILLMOW + "WN18RR/", DETTMERS + "WN18RR/"]
    if not _fetch_split_files(d, bases):
        return None
    tr = _load_triples(d / "train.txt"); va = _load_triples(d / "valid.txt"); te = _load_triples(d / "test.txt")
    if not tr or not te:
        return None
    return tr, va, te, _basic_prov("WN18RR", tr, va, te)


def _load_codex(size):
    d = REPO / "data" / ("codex_%s_testbed" % size)
    if not _fetch_split_files(d, [CODEX_BASE % size]):
        return None
    tr = _load_triples(d / "train.txt"); va = _load_triples(d / "valid.txt"); te = _load_triples(d / "test.txt")
    if not tr or not te:
        return None
    return tr, va, te, _basic_prov("CODEX_%s" % size.upper(), tr, va, te)


def _load_cskg_core(seed):
    if not _ensure_cskg():
        return None
    tr, va, te, prov = build_cskg_core_triples(CSKG_MAX_LINES, CSKG_KCORE, CSKG_MAX_NODES, seed)
    if not tr or not te:
        return None
    return tr, va, te, prov


def _load_conceptnet_slice(seed):
    """Best-effort ConceptNet English slice from a local jsonl (subject/predicate/object). Returns None if
    the local slice is absent on this host (survey stages what is reachable)."""
    p = REPO / "data" / "datasets" / "conceptnet5_en_100k.jsonl"
    if not p.exists():
        return None
    edges = []
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            h = str(o.get("subject", "")).strip(); r = str(o.get("predicate", "")).strip()
            t = str(o.get("object", "")).strip()
            if h and r and t and h != t:
                edges.append((h, r, t))
    edges = list({e for e in edges})
    if len(edges) < 100:
        return None
    rng = random.Random(seed); rng.shuffle(edges)
    n = len(edges); nt = max(1, int(0.05 * n)); nv = max(1, int(0.05 * n))
    test = edges[:nt]; valid = edges[nt:nt + nv]; train = edges[nt + nv:]
    return train, valid, test, _basic_prov("CONCEPTNET_SLICE", train, valid, test)


# Ladder spec: (name, loader, seed_dependent, role). Fixed-split corpora (seed_dependent=False) are loaded
# once and only the eval-query sampling varies per seed; random-split corpora re-split per seed.
def _real_ladder():
    if LADDER_KIND == "smoke":
        return [("FB15K237", _load_fb, False, "reference_reproducer")]
    return [
        ("FB15K237", _load_fb, False, "reference_reproducer"),
        ("WN18RR", _load_wn18rr, False, "sparse_mustfail_witness"),
        ("CODEX_S", lambda s: _load_codex("s"), False, "candidate"),
        ("CODEX_M", lambda s: _load_codex("m"), False, "candidate"),
        ("CODEX_L", lambda s: _load_codex("l"), False, "candidate"),
        ("CSKG_XCUT_CORE", _load_cskg_core, True, "candidate"),
        ("CONCEPTNET_SLICE", _load_conceptnet_slice, True, "candidate_besteffort"),
    ]


# ============================ ranking =========================================
def _fair_score(mean_strata):
    """Cross-strata fair-headroom score = min headroom over LOW/MID/HIGH (durable reasoning reach must not
    collapse at any stratum, incl higher degree)."""
    lo = mean_strata["low"]["headroom"]; mi = mean_strata["mid"]["headroom"]; hi = mean_strata["high"]["headroom"]
    return min(lo, mi, hi)


def _full_digest(tbl):
    """Richer fingerprint than _table_digest (which hashes headroom only): includes reach_ceiling,
    pop_relfreq_h10, headroom, and n per stratum. Two corpora with the SAME headroom (e.g. both 0) but
    DIFFERENT reach/pop (a genuinely different arm) are correctly distinguished -- the AF assertion must
    not false-fire on legitimately-degenerate all-zero-headroom tables (e.g. a capped/sparse smoke rung)."""
    import hashlib
    if tbl.get("empty"):
        return hashlib.sha256(("empty:%s" % tbl.get("corpus", "")).encode()).hexdigest()
    vals = []
    for st in ["low", "mid", "high", "all"]:
        s = tbl["strata"][st]
        vals.append((round(s["reach_ceiling"], 4), round(s["pop_relfreq_h10"], 4),
                     round(s["headroom"], 4), s["n"]))
    return hashlib.sha256(json.dumps(vals).encode()).hexdigest()


def _rank_real(real_means):
    """Rank real corpora descending by (fair_score, HIGH headroom, ALL headroom)."""
    items = list(real_means.items())
    items.sort(key=lambda kv: (_fair_score(kv[1]), kv[1]["high"]["headroom"], kv[1]["all"]["headroom"]),
               reverse=True)
    return items


# ============================ per-corpus runner ===============================
def run_real_corpus(name, loader, seed_dependent, seeds, n_eval, min_support, hb):
    """Returns (tables_list_or_None, prov_or_None, status_str). status in {OK, UNAVAILABLE, ERROR:<class>}."""
    try:
        tables = []
        prov = None
        if not seed_dependent:
            splits = loader(seeds[0])
            if splits is None:
                return None, None, "UNAVAILABLE"
            train, valid, test, prov = splits
            print("[corpus %s] loaded nodes=%d edges=%d avgdeg=%.1f rels=%d train=%d test=%d"
                  % (name, prov["n_nodes"], prov["n_edges"], prov["avgdeg"], prov["n_rel"],
                     prov["n_train"], prov["n_test"]), flush=True)
            for seed in seeds:
                ts = time.time()
                tbl = headroom_table(train, valid, test, name, n_eval, seed, min_support)
                tables.append(tbl)
                s = tbl["strata"]
                print("[corpus %s seed=%d] headroom LOW=%.3f MID=%.3f HIGH=%.3f ALL=%.3f | ceil ALL=%.3f pop ALL=%.3f (%.1fs)"
                      % (name, seed, s["low"]["headroom"], s["mid"]["headroom"], s["high"]["headroom"],
                         s["all"]["headroom"], s["all"]["reach_ceiling"], s["all"]["pop_relfreq_h10"],
                         time.time() - ts), flush=True)
                hb(name, seed)
        else:
            for seed in seeds:
                splits = loader(seed)
                if splits is None:
                    return None, None, "UNAVAILABLE"
                train, valid, test, prov = splits
                ts = time.time()
                tbl = headroom_table(train, valid, test, name, n_eval, seed, min_support)
                tables.append(tbl)
                s = tbl["strata"]
                print("[corpus %s seed=%d] nodes=%d edges=%d avgdeg=%.1f | headroom LOW=%.3f MID=%.3f HIGH=%.3f ALL=%.3f (%.1fs)"
                      % (name, seed, prov.get("n_nodes", prov.get("n_core_nodes_in_split", 0)), prov.get("n_core_edges", prov.get("n_edges", 0)),
                         prov.get("avgdeg", prov.get("core_avgdeg", 0.0)),
                         s["low"]["headroom"], s["mid"]["headroom"], s["high"]["headroom"],
                         s["all"]["headroom"], time.time() - ts), flush=True)
                hb(name, seed)
        if not tables or all(t.get("empty") for t in tables):
            return None, prov, "UNAVAILABLE"
        return tables, prov, "OK"
    except Exception as e:                               # per-corpus loud failure; recorded, survey continues
        print("[corpus %s] ERROR %s: %s" % (name, type(e).__name__, str(e)[:200]), flush=True)
        return None, None, "ERROR:%s" % type(e).__name__


# ============================ verdict =========================================
def compute_verdict(real_means, syn_comp, syn_freq, statuses):
    syn_comp_h = syn_comp["strata"]["all"]["headroom"]
    syn_freq_h = syn_freq["strata"]["all"]["headroom"]
    control_fires = (syn_freq_h <= 0.02) and (syn_comp_h >= 0.15)

    ranked = _rank_real(real_means)
    winner = ranked[0][0] if ranked else None
    winner_fair = _fair_score(ranked[0][1]) if ranked else None
    winner_high = ranked[0][1]["high"]["headroom"] if ranked else None

    # WN18RR real-corpus sparse must-fail witness (reported; not the analytic gate).
    wn = real_means.get("WN18RR")
    wn_all = wn["all"]["headroom"] if wn else None
    wn_fires = None if wn_all is None else (wn_all <= 0.10)

    if not control_fires:
        v = "INCONCLUSIVE_CONTROL_BROKEN"
    elif len(ranked) >= 2:
        v = "SURVEY_COMPLETE"
    else:
        v = "INCONCLUSIVE_INSUFFICIENT_CORPORA"

    rank_str = "; ".join("%s[fair=%.3f HIGH=%.3f ALL=%.3f]"
                         % (nm, _fair_score(m), m["high"]["headroom"], m["all"]["headroom"])
                         for nm, m in ranked)
    gates = {
        "control_fires": control_fires, "syn_compositional_headroom": syn_comp_h,
        "syn_freq_guessable_headroom": syn_freq_h,
        "winner": winner, "winner_fair_score": winner_fair, "winner_high_headroom": winner_high,
        "wn18rr_all_headroom": wn_all, "wn18rr_mustfail_fires": wn_fires,
        "n_real_ranked": len(ranked), "statuses": statuses,
        "ranking": [(nm, _fair_score(m), m["high"]["headroom"], m["all"]["headroom"]) for nm, m in ranked],
    }
    msg = ("WINNER=%s (fair=%s HIGH=%s) | control[SYN_COMP=%.3f SYN_FREQ=%.3f fires=%s] | "
           "WN18RR_all=%s mustfail_fires=%s | ladder: %s :: %s"
           % (winner, ("%.3f" % winner_fair) if winner_fair is not None else "n/a",
              ("%.3f" % winner_high) if winner_high is not None else "n/a",
              syn_comp_h, syn_freq_h, control_fires,
              ("%.3f" % wn_all) if wn_all is not None else "n/a", wn_fires, rank_str, v))
    return v, msg, gates, ranked


# ============================ self-test =======================================
def _selftest():
    print("[selftest] scale-invariant synthetic discriminators + ranking unit test...", flush=True)
    tc_tr, tc_v, tc_te = build_syn_compositional(seed=0, n_person=200, n_tail=50)
    tc = headroom_table(tc_tr, tc_v, tc_te, "SYN_COMPOSITIONAL", 0, 0, 3)
    comp_h = tc["strata"]["all"]["headroom"]; comp_reach = tc["strata"]["all"]["reach_ceiling"]
    assert comp_reach >= 0.8, "D1 FAIL: compositional gold not reachable (ceiling=%.3f)" % comp_reach
    assert comp_h >= 0.15, "D1 FAIL: compositional headroom too low (%.3f)" % comp_h

    tf_tr, tf_v, tf_te = build_syn_freq_guessable(seed=0, n_person=200)
    tf = headroom_table(tf_tr, tf_v, tf_te, "SYN_FREQ_GUESSABLE", 0, 0, 3)
    freq_h = tf["strata"]["all"]["headroom"]; freq_reach = tf["strata"]["all"]["reach_ceiling"]
    assert freq_reach >= 0.8, "D2 FAIL: freq-guessable gold not reachable (ceiling=%.3f) -> vacuous" % freq_reach
    assert freq_h <= 0.02, "D2 FAIL: freq-guessable shows headroom (%.3f); must-fail did NOT fire" % freq_h
    assert _table_digest(tc) != _table_digest(tf), "D3 FAIL: SYN arms bit-identical"

    # D4: ranking function orders by min-strata (fair_score) then HIGH then ALL.
    def mk(lo, mi, hi, al):
        return {"low": {"headroom": lo}, "mid": {"headroom": mi}, "high": {"headroom": hi},
                "all": {"headroom": al}}
    fake = {"A": mk(0.20, 0.20, 0.20, 0.20),   # fair=0.20 -> rank 1
            "B": mk(0.30, 0.30, 0.05, 0.25),   # fair=0.05 -> rank 3
            "C": mk(0.10, 0.15, 0.12, 0.13)}   # fair=0.10 -> rank 2
    order = [nm for nm, _m in _rank_real(fake)]
    assert order == ["A", "C", "B"], "D4 FAIL: ranking order wrong: %s" % order
    assert abs(_fair_score(fake["B"]) - 0.05) < 1e-9, "D4 FAIL: fair_score not min-strata"
    print("[selftest] PASS: SYN_COMP=%.3f (reach %.3f) SYN_FREQ=%.3f (reach %.3f) | ranking order %s"
          % (comp_h, comp_reach, freq_h, freq_reach, order), flush=True)


# ============================ start-marker / crash ============================
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE}
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ============================ main ============================================
def main():
    out_dir = get_output_dir(ANCHOR_NAME)
    ladder = _real_ladder()
    _write_start_marker(out_dir, RUN_MODE, len(ladder) + 2)
    t0 = time.time()
    print("[config] anchor=%s mode=%s seeds=%s N_EVAL=%d ladder=%s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_EVAL, [n for (n, _l, _sd, _r) in ladder]), flush=True)
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.time() - t0}) + "\n")

    min_support = MIN_SUPPORT_SMOKE if RUN_MODE == "smoke" else MIN_SUPPORT_REAL

    # ---- scale-invariant synthetic anchors (fixed upper/lower references; seed 7 build) ----
    sc_tr, sc_v, sc_te = build_syn_compositional(seed=7)
    syn_comp = headroom_table(sc_tr, sc_v, sc_te, "SYN_COMPOSITIONAL", 0, 7, min_support)
    sf_tr, sf_v, sf_te = build_syn_freq_guessable(seed=7)
    syn_freq = headroom_table(sf_tr, sf_v, sf_te, "SYN_FREQ_GUESSABLE", 0, 7, min_support)
    print("[anchor] SYN_COMPOSITIONAL headroom_all=%.3f reach=%.3f | SYN_FREQ_GUESSABLE headroom_all=%.3f reach=%.3f"
          % (syn_comp["strata"]["all"]["headroom"], syn_comp["strata"]["all"]["reach_ceiling"],
             syn_freq["strata"]["all"]["headroom"], syn_freq["strata"]["all"]["reach_ceiling"]), flush=True)
    _hb("anchors", 0)

    # ---- real-corpus ladder (best-effort; each rung staged) ----
    real_tables = {}         # name -> [per-seed tables]
    real_means = {}          # name -> mean strata (only OK corpora)
    real_prov = {}
    statuses = {}
    for ci, (name, loader, seed_dep, role) in enumerate(ladder):
        tables, prov, status = run_real_corpus(name, loader, seed_dep, SEEDS, N_EVAL, min_support, _hb)
        statuses[name] = {"status": status, "role": role}
        if status == "OK":
            real_tables[name] = tables
            real_means[name] = _mean_strata(tables)
            real_prov[name] = prov
        else:
            print("[corpus %s] status=%s role=%s -> excluded from ranking" % (name, status, role), flush=True)
        _hb("ladder_done", ci)

    # ---- ARMS-MUST-DIFFER (META_RULE_AF): available (non-empty) headroom tables must not be bit-identical ----
    digests = {"SYN_COMPOSITIONAL": _table_digest(syn_comp), "SYN_FREQ_GUESSABLE": _table_digest(syn_freq)}
    for name, tables in real_tables.items():
        if tables and not tables[0].get("empty"):
            digests[name] = _table_digest(tables[0])
    # AF assertion uses the FULL fingerprint (reach+pop+headroom+n) so genuinely-different arms that happen
    # to share an all-zero headroom vector (e.g. a sparse capped smoke rung vs SYN_FREQ) are not false-flagged.
    af_digests = {"SYN_COMPOSITIONAL": _full_digest(syn_comp), "SYN_FREQ_GUESSABLE": _full_digest(syn_freq)}
    for name, tables in real_tables.items():
        if tables and not tables[0].get("empty"):
            af_digests[name] = _full_digest(tables[0])
    names = list(af_digests)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            assert af_digests[names[i]] != af_digests[names[j]], \
                "META_RULE_AF VIOLATION: %s and %s headroom tables bit-identical (full fingerprint)" % (names[i], names[j])

    verdict, vmsg, gates, ranked = compute_verdict(real_means, syn_comp, syn_freq, statuses)
    elapsed = time.time() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "summary": vmsg[:200],
        "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "elapsed_s": elapsed, "gates": gates,
        "arms_differ_verified": True, "table_digests": digests,
        "ranking": [(nm, _fair_score(m), m["high"]["headroom"], m["all"]["headroom"]) for nm, m in ranked],
        "real_mean_strata": real_means, "real_per_seed": real_tables, "real_provenance": real_prov,
        "corpus_statuses": statuses,
        "syn_compositional": syn_comp, "syn_freq_guessable": syn_freq,
        "reference_fb_vet_table": {"low": 0.320, "mid": 0.299, "high": 0.027, "all": 0.011,
                                   "source": "CITED@notes VET aa7f151f (FB15k-237 headroom)"},
        "reference_syn_anchors": {"syn_compositional_expected": 0.86, "syn_freq_guessable_expected": 0.0,
                                  "source": "CITED@data/exp_cskg_dense_core_headroom_acceptance_v1_smoke/metrics.json"},
    }
    write_metrics(out_dir, metrics, list(real_tables.values()))
    print("[verdict] %s :: %s" % (verdict, vmsg), flush=True)
    # WN18RR genuine-vs-artifact diagnostic (logging-only; does NOT gate). The pre-registered sparse
    # must-fail inverted (high headroom). Discriminator on already-computed values: if the frequency
    # baseline (pop_relfreq_h10) is near-useless yet ALL headroom is high, the headroom is genuine
    # compositional-hierarchy derivability (is-a/part-of transitivity, frequency-useless); if the freq
    # baseline is non-trivial, it is likely a frequency artifact. Informs the durable-escape corpus pick.
    _wn = real_means.get("WN18RR")
    if _wn is not None:
        _wn_h = _wn["all"].get("headroom", 0.0)
        _wn_pop = _wn["all"].get("pop_relfreq_h10", 0.0)
        _wn_genuine = (_wn_h >= 0.10) and (_wn_pop <= 0.05)
        print("[wn18rr-note] ALL_headroom=%.3f freq_baseline_pop_h10=%.3f mustfail_fired=%s -> %s"
              % (_wn_h, _wn_pop, gates.get("wn18rr_mustfail_fires"),
                 "GENUINE_compositional_hierarchy_derivability(freq-useless)" if _wn_genuine
                 else "LIKELY_FREQUENCY_ARTIFACT(freq-baseline-nontrivial)"), flush=True)
    print("[metrics] written to %s (%.1fs)" % (out_dir, elapsed), flush=True)


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        sys.exit(0)
    out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir_for_crash, e)
        raise
