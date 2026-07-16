"""Real-data test: does copy-CORRECTION beat NAIVE source-count at recovering
truth in an ERROR-PROPAGATING regime? (Book-Authors, Dong/Yin lineage.)

DESIGN-VALIDATION / REAL-DATA CHECK. NOT a substrate cell. Produces NO atoms.
No queue, no GPU/CPU dispatch, no origin push. Pure-Python (numpy + stdlib),
runs inline (plus a one-time dataset download).

WHY BOOK (closing the Weather wash): the sibling cell
`experiments/real_weather_copy_corroboration_validity_2026-07-16.py`
(commit ac491e78e) validated on the Weather corpus that the copy-DETECTOR
recovers a labeled copying graph (TEST 1 PASSED, perm p=0.0126). But its
TEST 2 -- does copy-CORRECTED corroboration beat NAIVE source-count at
recovering GROUND TRUTH -- was a WASH, because Weather copiers copy ACCURATE
values: with nothing wrong to propagate, correction had nothing to fix. The
Weather cell explicitly recommended Book as the follow-on. The Book-Authors
corpus is the truth-discovery hub's purpose-built ERROR-PROPAGATING benchmark:
online booksellers copy each other's author lists INCLUDING mistakes (wrong /
truncated / mis-ordered author attributions), so a naive vote can be captured
by a large clique of copiers all repeating the SAME wrong answer. This is
exactly the regime where one-vote-per-independent-cluster is supposed to pay
off. There is NO labeled copying graph for Book (copying must be inferred
blind), so this cell runs the detector unsupervised and tests ONLY the truth-
value question -- the axis Weather left open.

Corpus: Book / Book-Authors (Yin/Han/Yu 2008 TruthFinder; re-released Dong/
Berti-Equille/Srivastava). ~894 online booksellers x ~1263 books; each row is
(source, ISBN, title, author-list). Ground truth = the released per-book author
lists: book_golden.txt (~100 hand-verified) + book_silver.txt (all books,
derived). Download: https://lunadong.com/datasets/{book.zip,book_golden.txt,
book_silver.txt}.

REUSE (verbatim, per contract): the copy-detector
`detect_dependence_realvalued` and the reuse-integrity `equivalence_self_test`
are IMPORTED from the committed Weather cell (which in turn reduces exactly to
the committed toy `detect_dependence` at collision c=1). Author lists are
encoded as global integer value-ids (equal normalized last-name SET -> equal
id), so the same integer-matrix detector applies unchanged. Corroboration
scoring (naive = source count; corrected = distinct detected-cluster count) is
the committed toy `corroboration_scores` principle.

Pre-registered bands (truth-value of copy-correction, error-propagating regime):
  Let subset B = books where correction ACTUALLY CHANGES the answer
  (naive_pick != corrected_pick) -- the only books where copy-correction can
  matter. On B, cw = books where corrected pick is CLOSER to truth (higher
  last-name Jaccard), nw = books where naive is closer (ties excluded).
  HARD-PASS: |B| >= 20 AND corrected win-rate cw/(cw+nw) >= 0.60 AND one-sided
             binomial p(cw; cw+nw, 0.5) < 0.05 AND overall corrected mean-
             Jaccard NOT worse than naive (>= naive - 0.005). => copy-correction
             delivers the truth-value it is supposed to, now that copiers
             propagate errors.
  HARD-FAIL: cw <= nw on B (corrected no better than naive even where it acts)
             OR overall corrected mean-Jaccard < naive by a clear margin
             (< naive - 0.01). => copy-correction's truth-value UNCONFIRMED even
             in the error-propagating regime (honest negative).
  MIDDLE:    otherwise (corrected wins but not decisively, or |B| too thin).

HONEST CAVEATS (pre-registered): (1) the copy graph is INFERRED, not labeled --
the detector is unsupervised and untuned against truth, so an under-detecting
or over-merging detector is a real failure mode this test will expose. (2) Author
matching is on normalized last-name SETS (robust to "Last, First" vs "First Last"
vs lowercase across book.txt/gold/silver formats), scored by Jaccard; exact-set
accuracy is reported alongside as corroboration. (3) Only books with released
truth AND >= MIN_REPORTERS distinct source claims are evaluated.

Parse self-tests run FIRST (source/book/row counts vs documented figures, ISBN-10
->13 truth coverage, gold count, and an author-normalization coherence check on
the gold set). If any fails the metrics are meaningless and the script aborts.
"""

import argparse
import collections
import importlib.util
import io
import math
import os
import re
import sys
import urllib.request
import zipfile

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEATHER_PATH = os.path.join(
    REPO, "experiments", "real_weather_copy_corroboration_validity_2026-07-16.py")
BOOK_ZIP_URL = "https://lunadong.com/datasets/book.zip"
GOLD_URL = "https://lunadong.com/datasets/book_golden.txt"
SILVER_URL = "https://lunadong.com/datasets/book_silver.txt"

# Documented dataset figures (Yin/Han/Yu 2008; Dong/Berti-Equille/Srivastava).
DOC_SOURCES = 894      # ~894 booksellers
DOC_BOOKS = 1263       # ~1263 books
DOC_GOLD = 100         # ~100 hand-verified golden books

# Detector / evaluation parameters (all chosen here; rationale inline).
MIN_REPORTS_DET = 20   # only sources with >= this many book-claims join union-find
                       # (fewer claims -> too little overlap to certify copying;
                       # such sources vote but stay singleton clusters).
DEP_MIN_OVERLAP = 10   # min co-reported books before trusting a pair's agreement.
# PRIMARY excess-agreement threshold = 0.15, INHERITED from the sibling Weather
# cell (real_weather_copy_corroboration_validity_2026-07-16.py), where it was
# CALIBRATED against a LABELED gold copying graph (detector TEST 1 passed there,
# perm p=0.0126). Using the labeled-data-calibrated value is the principled,
# non-circular operating point for Book (which has NO copy labels to tune on).
# The verdict is threshold-CONTINGENT: a sensitivity sweep is printed and the
# sign flips at conservative thresholds (>=0.25) -- see the sweep block. Do NOT
# read the 0.15 headline without the sweep caveat.
DEP_EXCESS_THRESH = 0.15
SWEEP_THRESHOLDS = [0.15, 0.25, 0.35, 0.50]  # transparency: report all, verdict at primary
MIN_REPORTERS = 3      # a book is evaluable only if >= this many sources claim it.


# ---------------------------------------------------------------------------
# Reuse the committed Weather cell's detector + reuse-integrity self-test.
# ---------------------------------------------------------------------------
def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------
# Data acquisition
# ---------------------------------------------------------------------------
def _fetch(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def ensure_dataset(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    book_txt = os.path.join(data_dir, "book.txt")
    gold_txt = os.path.join(data_dir, "book_golden.txt")
    silver_txt = os.path.join(data_dir, "book_silver.txt")
    if not os.path.exists(book_txt):
        print("  downloading book.zip ...")
        blob = _fetch(BOOK_ZIP_URL, book_txt)
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            z.extractall(data_dir)
    if not os.path.exists(gold_txt):
        print("  downloading book_golden.txt ...")
        with open(gold_txt, "wb") as fh:
            fh.write(_fetch(GOLD_URL, gold_txt))
    if not os.path.exists(silver_txt):
        print("  downloading book_silver.txt ...")
        with open(silver_txt, "wb") as fh:
            fh.write(_fetch(SILVER_URL, silver_txt))
    return book_txt, gold_txt, silver_txt


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------
def isbn13(s):
    """Normalize an ISBN to 13-digit form (ISBN-10 -> ISBN-13). Returns the
    cleaned string; non-convertible inputs returned cleaned as-is."""
    s = re.sub(r"[^0-9Xx]", "", s.strip())
    if len(s) == 13:
        return s
    if len(s) == 10:
        core = "978" + s[:9]
        tot = sum((1 if i % 2 == 0 else 3) * int(d) for i, d in enumerate(core))
        chk = (10 - tot % 10) % 10
        return core + str(chk)
    return s


def lastname_set(authorstr):
    """Robust author-list -> frozenset of normalized last names. Handles
    'Last, First; Last, First' (book.txt / gold) and 'First Last; First Last'
    (silver), case-insensitively, punctuation-stripped."""
    if not authorstr:
        return frozenset()
    out = set()
    for a in re.split(r"[;|]", authorstr):
        a = a.strip()
        if not a:
            continue
        if "," in a:
            last = a.split(",")[0]
        else:
            toks = a.split()
            last = toks[-1] if toks else ""
        last = re.sub(r"[^a-z-]", "", last.lower())
        if last:
            out.add(last)
    return frozenset(out)


def jaccard(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
def parse_book(book_txt):
    """Return (claims, sources, books) where claims[(isbn,src)] = frozenset last
    names (mode over that source's rows for the book)."""
    raw = collections.defaultdict(list)   # (isbn,src) -> [frozenset,...]
    sources = set()
    books = set()
    with open(book_txt, encoding="latin-1") as fh:
        for line in fh:
            p = line.rstrip("\n").split("\t")
            if len(p) < 4:
                continue
            src, isbn, _title, authors = p[0].strip(), isbn13(p[1]), p[2], p[3]
            if not src or not isbn:
                continue
            sources.add(src)
            books.add(isbn)
            raw[(isbn, src)].append(lastname_set(authors))
    claims = {}
    for key, lst in raw.items():
        # mode over a source's multiple rows for the same book (ties -> first).
        cnt = collections.Counter(lst)
        claims[key] = cnt.most_common(1)[0][0]
    return claims, sources, books


def parse_truth(path, gold=False):
    """Return {isbn13: frozenset last names}. Gold file is blank-line separated;
    silver is one line per book."""
    truth = {}
    with open(path, encoding="latin-1") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            p = line.split("\t")
            if len(p) < 2:
                continue
            isbn = isbn13(p[0])
            if len(isbn) < 10:
                continue
            truth[isbn] = lastname_set(p[1])
    return truth


# ---------------------------------------------------------------------------
# Binomial one-sided p (P(X >= k) under Binom(n, 0.5)); stdlib only.
# ---------------------------------------------------------------------------
def binom_sf_half(k, n):
    if n == 0:
        return 1.0
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i)
    return total / (2.0 ** n)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    default_dir = os.path.join(REPO, "data", "book_dong")
    ap.add_argument("--data-dir", default=default_dir)
    ap.add_argument("--truth", choices=["silver", "gold", "gold+silver"],
                    default="silver",
                    help="ground-truth set for the primary metric (default silver "
                         "= all books; gold = ~100 hand-verified)")
    ap.add_argument("--self-test", action="store_true",
                    help="run self-tests only and exit")
    args = ap.parse_args()

    w = _load_module(WEATHER_PATH, "weather_cell")

    print("=" * 78)
    print("REAL-DATA COPY-CORRECTION-ON-TRUTH  (Book-Authors, error-propagating)")
    print("=" * 78)

    # -- reuse-integrity self-test (imported detector reduces to committed one) --
    eq_ok = w.equivalence_self_test(w._load_toy())
    print("SELF-TEST reused-detector equivalence (c=1 == committed toy): %s"
          % ("PASS" if eq_ok else "FAIL"))
    if not eq_ok:
        print("VERDICT: DETECTOR_REUSE_INVALID")
        return 2

    book_txt, gold_txt, silver_txt = ensure_dataset(args.data_dir)
    claims, sources, books = parse_book(book_txt)
    gold = parse_truth(gold_txt, gold=True)
    silver = parse_truth(silver_txt)

    # ---- PARSE SELF-TESTS ----
    print("\n--- PARSE SELF-TESTS ---")
    fails = []
    n_src, n_book = len(sources), len(books)
    n_rows_with_author = sum(1 for k, v in claims.items() if v)
    print("  sources parsed: %d (doc ~%d)" % (n_src, DOC_SOURCES))
    print("  books parsed:   %d (doc ~%d)" % (n_book, DOC_BOOKS))
    print("  (isbn,src) claims: %d  nonempty-author: %d"
          % (len(claims), n_rows_with_author))
    if not (DOC_SOURCES * 0.9 <= n_src <= DOC_SOURCES * 1.15):
        fails.append("source count %d far from documented ~%d" % (n_src, DOC_SOURCES))
    if not (DOC_BOOKS * 0.9 <= n_book <= DOC_BOOKS * 1.1):
        fails.append("book count %d far from documented ~%d" % (n_book, DOC_BOOKS))

    # ISBN normalization: what fraction of parsed books map to a silver truth?
    covered = sum(1 for b in books if b in silver)
    print("  books with silver truth (ISBN-13 normalized): %d/%d (%.1f%%)"
          % (covered, n_book, 100.0 * covered / max(n_book, 1)))
    if covered < 0.9 * n_book:
        fails.append("ISBN normalization: only %d/%d books map to silver truth"
                     % (covered, n_book))
    print("  gold truth books: %d (doc ~%d) ; silver truth books: %d"
          % (len(gold), DOC_GOLD, len(silver)))
    if not (DOC_GOLD * 0.85 <= len(gold) <= DOC_GOLD * 1.2):
        fails.append("gold count %d far from documented ~%d" % (len(gold), DOC_GOLD))

    # Author-normalization coherence: on the gold set, do source claims align
    # with gold truth under our normalization? (If normalization were broken,
    # claims and truth would be mutually incomparable and all metrics garbage.)
    # Metric: fraction of gold books whose CONSENSUS (mode source claim) exactly
    # equals gold truth, and fraction with >=1 source exactly matching.
    per_book_src = collections.defaultdict(dict)   # isbn -> {src: frozenset}
    for (isbn, src), fs in claims.items():
        if fs:
            per_book_src[isbn][src] = fs
    gold_consensus_match = gold_any_match = gold_tested = 0
    for isbn, tset in gold.items():
        srcvals = per_book_src.get(isbn, {})
        if len(srcvals) < MIN_REPORTERS or not tset:
            continue
        gold_tested += 1
        vals = list(srcvals.values())
        mode = collections.Counter(vals).most_common(1)[0][0]
        if mode == tset:
            gold_consensus_match += 1
        if any(v == tset for v in vals):
            gold_any_match += 1
    cons_rate = gold_consensus_match / max(gold_tested, 1)
    any_rate = gold_any_match / max(gold_tested, 1)
    print("  author-norm coherence on gold (n=%d evaluable): consensus==truth=%.2f "
          " any-source==truth=%.2f" % (gold_tested, cons_rate, any_rate))
    if gold_tested < 30:
        fails.append("too few evaluable gold books (%d) for coherence check"
                     % gold_tested)
    if any_rate < 0.5:
        fails.append("author normalization incoherent: only %.2f of gold books have "
                     "any source exactly matching truth" % any_rate)

    if fails:
        print("\nSELF-TEST FAILED -- metrics meaningless, aborting:")
        for f in fails:
            print("  FAIL: " + f)
        print("\nVERDICT: PARSE_INVALID")
        return 2
    print("  all parse self-tests PASS")

    if args.self_test:
        print("\n--self-test only: OK")
        return 0

    # ---- build book x source value-id matrix ----
    # global int id per distinct normalized last-name set (equal set -> equal id).
    set_id = {}

    def gid(fs):
        if fs not in set_id:
            set_id[fs] = len(set_id)
        return set_id[fs]

    src_list = sorted(sources)
    src_idx = {s: i for i, s in enumerate(src_list)}
    book_list = sorted(books)
    book_idx = {b: k for k, b in enumerate(book_list)}
    K, S = len(book_list), len(src_list)
    MISSING = w.MISSING
    val = np.full((K, S), MISSING, dtype=int)
    for (isbn, src), fs in claims.items():
        if not fs:
            continue   # empty author list = no usable claim
        val[book_idx[isbn], src_idx[src]] = gid(fs)

    reports_per_src = (val != MISSING).sum(axis=0)
    n_det_sources = int((reports_per_src >= MIN_REPORTS_DET).sum())
    print("\n--- VALUE MATRIX ---")
    print("  books=%d sources=%d distinct-value-ids=%d fill=%.2f%%"
          % (K, S, len(set_id), 100.0 * (val != MISSING).mean()))
    print("  sources with >=%d claims (join union-find): %d/%d"
          % (MIN_REPORTS_DET, n_det_sources, S))

    # consensus (mode among >= MIN_REPORTERS reporters) + per-source reliability.
    cons = np.full(K, MISSING)
    for k in range(K):
        row = val[k][val[k] != MISSING]
        if len(row) >= MIN_REPORTERS:
            vals, cnts = np.unique(row, return_counts=True)
            cons[k] = int(vals[np.argmax(cnts)])
    rel = np.zeros(S)
    for si in range(S):
        m = (val[:, si] != MISSING) & (cons != MISSING)
        rel[si] = float((val[m, si] == cons[m]).mean()) if m.sum() else 0.0

    # empirical collision c: P(two independent WRONG claims on a book coincide).
    coll_terms = []
    for k in range(K):
        if cons[k] == MISSING:
            continue
        row = val[k][val[k] != MISSING]
        wrong = row[row != cons[k]]
        if len(wrong) >= 2:
            _, cnts = np.unique(wrong, return_counts=True)
            p = cnts / cnts.sum()
            coll_terms.append(float((p ** 2).sum()))
    c_collision = float(np.mean(coll_terms)) if coll_terms else 0.0
    print("  mean source reliability=%.3f  empirical collision c=%.4f"
          % (rel.mean(), c_collision))

    # invert id -> frozenset once (used by every evaluation).
    inv = {i: fs for fs, i in set_id.items()}
    truth_map = silver if args.truth == "silver" else (
        gold if args.truth == "gold" else {**silver, **gold})
    det_srcs = [si for si in range(S) if reports_per_src[si] >= MIN_REPORTS_DET]
    sub = val[:, det_srcs]
    sub_rel = rel[det_srcs]

    def evaluate_at(thr):
        """Run the reused unsupervised detector at excess-threshold thr, then
        score naive source-count vs copy-corrected corroboration on truth.
        Returns a metrics dict. Pure function of thr (no printing)."""
        sub_clusters, sub_edges, _ = w.detect_dependence_realvalued(
            sub, sub_rel, c_collision, thr, DEP_MIN_OVERLAP)
        # global cluster ids: big sources -> detector clusters; others singleton.
        clusters = np.arange(S) + 10_000_000
        for local_i, si in enumerate(det_srcs):
            clusters[si] = int(sub_clusters[local_i])
        n_clu = len(set(clusters[si] for si in det_srcs))

        jn_all, jc_all, en_all, ec_all = [], [], [], []
        n_disagree = B_cw = B_nw = B_tie = B_size = 0
        B_exact_c = B_exact_n = evaluated = 0
        for k in range(K):
            tset = truth_map.get(book_list[k])
            if not tset:
                continue
            row_srcs = np.where(val[k] != MISSING)[0]
            if len(row_srcs) < MIN_REPORTERS:
                continue
            evaluated += 1
            by_val = collections.defaultdict(list)
            for si in row_srcs:
                by_val[int(val[k, si])].append(si)
            if len(by_val) >= 2:
                n_disagree += 1
            naive_score = {v: len(ss) for v, ss in by_val.items()}
            corr_score = {v: len(set(clusters[s] for s in ss))
                          for v, ss in by_val.items()}

            def pick(score):
                # tie-break: higher score, then more raw sources, then id.
                return max(score, key=lambda v: (score[v], naive_score[v], -v))
            npick, cpick = pick(naive_score), pick(corr_score)
            pn, pc = inv[npick], inv[cpick]
            jn, jc = jaccard(pn, tset), jaccard(pc, tset)
            jn_all.append(jn); jc_all.append(jc)
            en_all.append(float(pn == tset)); ec_all.append(float(pc == tset))
            if npick != cpick:
                B_size += 1
                B_exact_c += int(pc == tset); B_exact_n += int(pn == tset)
                if jc > jn:
                    B_cw += 1
                elif jn > jc:
                    B_nw += 1
                else:
                    B_tie += 1
        denom = B_cw + B_nw
        return dict(
            thr=thr, edges=len(sub_edges), n_clu=n_clu, evaluated=evaluated,
            n_disagree=n_disagree, B_size=B_size, B_cw=B_cw, B_nw=B_nw,
            B_tie=B_tie, B_exact_c=B_exact_c, B_exact_n=B_exact_n,
            mjn=float(np.mean(jn_all)), mjc=float(np.mean(jc_all)),
            men=float(np.mean(en_all)), mec=float(np.mean(ec_all)),
            denom=denom,
            win_rate=(B_cw / denom if denom else float("nan")),
            p_bin=(binom_sf_half(B_cw, denom) if denom else float("nan")),
        )

    def band(r):
        overall_not_worse = r["mjc"] >= r["mjn"] - 0.005
        overall_clearly_worse = r["mjc"] < r["mjn"] - 0.01
        hp = (r["B_size"] >= 20 and r["denom"] > 0 and r["win_rate"] >= 0.60
              and r["p_bin"] < 0.05 and overall_not_worse)
        hf = (r["denom"] > 0 and r["B_cw"] <= r["B_nw"]) or overall_clearly_worse
        return "HARD-PASS" if hp else ("HARD-FAIL" if hf else "MIDDLE")

    # ---- PRIMARY evaluation at the inherited-calibrated threshold ----
    print("\n" + "=" * 78)
    print("CORROBORATION-ON-TRUTH  (truth=%s)  naive source-count vs copy-corrected"
          % args.truth)
    print("  PRIMARY threshold=%.2f (inherited from Weather labeled-copy calibration)"
          % DEP_EXCESS_THRESH)
    print("=" * 78)
    r = evaluate_at(DEP_EXCESS_THRESH)
    print("  detector: flagged_pairs=%d  clusters_among_%d_big_sources=%d"
          % (r["edges"], len(det_srcs), r["n_clu"]))
    print("  evaluable books: %d  (sources disagree on %d, correction changes pick "
          "on %d)" % (r["evaluated"], r["n_disagree"], r["B_size"]))
    print("  OVERALL mean last-name Jaccard: naive=%.4f corrected=%.4f delta=%+.4f"
          % (r["mjn"], r["mjc"], r["mjc"] - r["mjn"]))
    print("  OVERALL exact-set accuracy:     naive=%.4f corrected=%.4f delta=%+.4f"
          % (r["men"], r["mec"], r["mec"] - r["men"]))
    print("  DECISION-DIFFER SUBSET B (naive_pick != corrected_pick), n=%d:"
          % r["B_size"])
    print("    corrected closer (Jaccard): cw=%d  naive closer: nw=%d  ties=%d"
          % (r["B_cw"], r["B_nw"], r["B_tie"]))
    print("    corrected win-rate (excl ties) = %.3f  one-sided binomial p = %.4g"
          % (r["win_rate"], r["p_bin"]))
    print("    exact-set on B: corrected=%d naive=%d" % (r["B_exact_c"], r["B_exact_n"]))
    primary_verdict = band(r)

    # ---- THRESHOLD-SENSITIVITY SWEEP (transparency; verdict is contingent) ----
    print("\n--- THRESHOLD-SENSITIVITY SWEEP (unsupervised detector, no copy labels)---")
    print("  %-6s %-6s %-6s | %-8s %-8s | %-4s %-11s %-8s | %s"
          % ("thr", "edges", "nclu", "mJ_naive", "mJ_corr", "|B|", "cw/nw/tie",
             "winrate", "band"))
    sweep = []
    for thr in SWEEP_THRESHOLDS:
        rr = evaluate_at(thr)
        sweep.append(rr)
        print("  %-6.2f %-6d %-6d | %-8.4f %-8.4f | %-4d %d/%d/%-5d %-8.3f | %s"
              % (thr, rr["edges"], rr["n_clu"], rr["mjn"], rr["mjc"], rr["B_size"],
                 rr["B_cw"], rr["B_nw"], rr["B_tie"], rr["win_rate"], band(rr)))
    bands = set(band(x) for x in sweep)
    contingent = len(bands) > 1

    # ---- verdict ----
    print("\n" + "=" * 78)
    print("VERDICT BLOCK")
    print("  regime: ERROR-PROPAGATING (booksellers copy wrong author lists)")
    print("  PRIMARY (thr=%.2f, calibrated): overall Jaccard delta=%+.4f  "
          "subset-B win-rate=%.3f (p=%.4g, |B|=%d) -> %s"
          % (DEP_EXCESS_THRESH, r["mjc"] - r["mjn"], r["win_rate"], r["p_bin"],
             r["B_size"], primary_verdict))
    print("  SWEEP bands across thr%s: %s%s"
          % (SWEEP_THRESHOLDS, sorted(bands),
             "  <- THRESHOLD-CONTINGENT (sign flips)" if contingent else ""))
    print("  N-CAVEAT: copy graph is INFERRED (unsupervised, untunable on Book -- no "
          "copy labels). Author match on normalized last-name sets. The verdict "
          "hinges on the detector operating point; 0.15 is the ONLY externally-")
    print("            calibrated (Weather labeled-data) choice, NOT tuned on Book "
          "truth. SUGGESTIVE on real data, not definitive.")
    print("  PRE-REG VERDICT (at primary calibrated threshold): %s" % primary_verdict)
    if primary_verdict == "HARD-PASS":
        print("  CALL: at the calibrated operating point, copy-correction beats naive "
              "on truth where copiers propagate errors -- closes the Weather wash;")
        print("        BUT the win is threshold-contingent (reverses at thr>=0.25), so "
              "it is CONDITIONAL on correct unsupervised copy-detection, not free.")
    elif primary_verdict == "HARD-FAIL":
        print("  CALL: copy-correction no better than naive even here -- truth-value "
              "UNCONFIRMED (honest negative).")
    else:
        print("  CALL: MIDDLE -- correction directionally helps but not decisively at "
              "the calibrated point.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
