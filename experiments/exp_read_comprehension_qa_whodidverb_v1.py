"""COMPREHENSION QA -- first read->ANSWER step (v1): "Who did [verb]?"

The north-star read->ANSWER waypoint toward a conversable substrate. ONE runnable that
reads a REAL multi-sentence LitBank passage and ANSWERS a question FROM the situation
model, glass-box. Scoped to AVOID the noisy event/role extractor bottleneck (29518):
the QA composes only the SOLID dimensions -- PARSE (find a verb's grammatical subject) +
COREF (resolve a cross-sentence pronoun-subject to an entity).

THE QUESTION: "Who did [verb]?" where the verb's grammatical SUBJECT is a CROSS-SENTENCE
PRONOUN. To answer, the reader must: (a) locate the clause with the target verb, (b) find
its subject (parse: sent_role_rank==0 mention before the predicate), (c) since the subject
is a pronoun, RESOLVE it cross-sentence to an entity (the banked ~0.45 recency-centrality
coref), (d) ANSWER with the entity head. This is exactly the read->answer QUERY INTERFACE
over the consolidated situation model (hdlab/situation_reader.py, 29518) -- ASK a question,
get a JUSTIFIED entity answer with a hand-auditable trace.

GOLD (free, non-circular): derived from LitBank COREF gold. A QA item = a gendered-singular
pronoun mention that is (i) the SUBJECT of a verb (sent_role_rank==0, a verb follows it in
its clause) AND (ii) has its gold nearest antecedent in a PRIOR sentence (cross-sentence).
The question's verb comes from the TEXT; the gold answer = the pronoun's gold cluster (its
canonical head). The reader NEVER sees gold coref linking (anti-circular; 29506): gold is
used only to select QA items + score correctness.

CAN-FAIL VALIDITY GATE (established 29506/29518, sharpened here): a SINGLE-SENTENCE baseline
(overlay reset each sentence; no prior-sentence entity access) is STRUCTURALLY BLIND on a
SUBJECT pronoun -- the pronoun is the FIRST mention in its sentence, so the single-sentence
overlay is EMPTY at that point and it must abstain -> 0.0 on the cross-sentence-subject QA
set. The situation reader resolves the pronoun to the prior-sentence entity. The composed QA
reader must beat the single-sentence 0.0 (capability demonstration).

FAIR TEST (pre-registered BEFORE running):
  BASELINES (both genuine can-fail controls):
    * SINGLE_SENTENCE (validity gate)  : overlay reset per sentence -> 0.0 on the subject-
      pronoun cross-sentence set (structurally guaranteed; the pronoun is clause-initial).
    * RECENCY (the honest hard baseline): answer = the gold cluster of the MOST-RECENT prior
      gender-compatible specific nominal. The coref arc showed recency/locality is STRONG
      (29514/29516); the situation reader IS the recency-centrality reader, so it must at
      least MATCH/BEAT recency (no-regression = it reproduces the banked mechanism).
  DISCRIMINATOR: QA accuracy on cross-sentence-subject questions vs the single-sentence 0.0
    (capability demonstration) + vs RECENCY (no-regression). Accuracy is COREF-BOUND (~0.45)
    and reported HONESTLY, NOT inflated -- the POINT is the read->answer QUERY INTERFACE +
    glass-box, NOT a new accuracy. ONE variable (cross-sentence entity access). Difficulty
    ON (cross-sentence pronoun-SUBJECT). No gold linking seen by the resolver.

PRE-REGISTERED BANDS (set BEFORE this run; a QUERY-INTERFACE DEMONSTRATION cell -- "PASS"
  means it reads real text, ANSWERS from the situation model, the validity gate fires, the
  reader reproduces/beats recency, and traces are hand-auditable; NOT a new-capability claim):
  QA_RUNS              : every book read end-to-end with NO crash; n_qa_items > 0 (report n).
  VALIDITY_GATE_FIRES  : SINGLE_SENTENCE QA accuracy on the cross-sentence-subject set == 0.0
                         (structurally blind) AND reader QA acc > 0 (capability demonstrated).
  READER_COREF_BOUND   : 0.30 <= reader QA acc <= 0.75 (coref-bound; the UPPER bound is wider
                         than the banked general-xsent ~0.45 because the SUBJECT-pronoun (he/she,
                         clause-initial nominative) cross-sentence set is recency-EASY -- the
                         antecedent is usually the recent subject; still catches true saturation
                         >0.95 [gold leak] and floor <0.05 [broken]).
  NO_REGRESSION_RECENCY: reader QA acc >= recency QA acc - 0.02 (the reader IS recency-
                         centrality -> it reproduces/beats the raw-recency baseline).
  GLASS_BOX            : >= 2 CORRECT and >= 1 INCORRECT full answer traces printed
                         (question -> clause -> subject pronoun -> coref chain -> entity).
  FAIL bands           : any read() crash; reader QA acc > 0.95 (saturated/leak) or < 0.05
                         (floor); SINGLE_SENTENCE QA acc > 0.05 (validity gate did NOT fire);
                         reader QA acc < recency QA acc - 0.05 (regression vs recency).
  VERDICT: DEMONSTRATED iff ALL of {QA_RUNS, VALIDITY_GATE_FIRES, READER_COREF_BOUND,
    NO_REGRESSION_RECENCY, GLASS_BOX}. Else PARTIAL (report which hold) or FAIL.

HONEST SCOPE (deflated, no-smoke): COREF-BOUND. This adds NO accuracy beyond the banked coref;
  it is the QUERY INTERFACE + glass-box read->answer demonstration (the conversation precursor:
  ASK -> justified entity answer). If the QA merely reproduces coref accuracy with no added
  value, that is stated plainly. Misses are expected to be the SAME same-gender centering /
  pronoun-chain wall the coref arc triangulated (29513-29517) -- per-item autopsy reports it.

BRAIN-CHECK: reading comprehension = querying the situation model (Kintsch/van-Dijk). "Who did
  X?" retrieves the AGENT of the X-event; when the agent is realized as a pronoun, resolution
  is cue-based memory retrieval of the antecedent (L-MTG retrieval; recency-weighted). The
  single-sentence baseline is the corresponding null (no discourse memory).

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- per-book symbolic coref +
  small HD event-memory unbind/cleanup (n_dim=4096, Cowan-4); NO SGD/training/GPU-batchable
  primitive; wall < 30s for all 25 books. Storage: sharded event codevectors in a bounded
  ChunkedFocus (no bundled-composition collapse; 29512). Determinism: OMP/MKL/OPENBLAS=1, fixed
  seeds, no hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion. NO push / NO remote-persist
  / NO queue_add (routing contract: inline-local FULL, not banked -- skunkworks VETs + banks).

CELL-TEMPLATE MANDATORY (subset applicable to this LOCAL foreground demonstration cell):
  - arms_differ_verified at smoke (reader vs single-sentence QA decisions differ; hash-checked)
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - baseline_in_band: reader not saturated/floor; SINGLE_SENTENCE CAN fail (== 0 by structure)
  - discriminator fires: SINGLE_SENTENCE == 0 on the subject-pronoun xsent set; reader >> 0
  - glass-box: full answer traces (correct + incorrect)
  - deterministic seeding (fixed int seeds; sorted book order)
  - N/A CRLB (discrete accuracy, no HD noise floor on the discrete coref decision); N/A multi-
    seed (deterministic given fixed seeds)
  - progress_logging: print_flush_true (stdout line-buffered)

CITED anchors (all numbers MEASURED@ at run time except):
  - coref recency-centrality plateau ~0.45  CITED@29516 (event_centrality same-gender 0.4523)
  - single-sentence xsent == 0.0 validity gate  CITED@29506 / 29518
  - QA reader = hdlab/situation_reader.py coref backbone  CITED@29518
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import glob
import hashlib
import json
import platform
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import (  # noqa: E402
    CorefReader,
    build_pronoun_targets,
    load_name_gender,
    parse_litbank_conll,
    sent_dist_bucket,
)
from hdlab.event_centrality_coref import EVENT_N_DIM, EventCentralityReader  # noqa: E402
from hdlab.scene_segment import parse_conll_sentences  # noqa: E402
from experiments import _temporal_ordering as T  # noqa: E402

ANCHOR_NAME = "read_comprehension_qa_whodidverb_v1"
CORPUS_DIR = os.path.join(_REPO, "data", "corpora", "litbank_coref_conll")
SMOKE_N = 3

# banked EventCentralityReader config (reproduces the 29516/29518 coref backbone bit-for-bit)
SUP_KW = dict(suppress_generic=True, use_nonref=True, use_struct=True,
              chain_pronouns=True, use_gazetteer=True)
LOCAL_WINDOW = 5      # banked 29514 fixed local-window
MEM_SEED = 7

# NOMINATIVE subject pronouns only: "who did [verb]?" needs the DOER (grammatical subject),
# which is nominative he/she. Possessive/object forms (his/her/him) are NOT subjects -- including
# them mislabels object/possessive rank-0 mentions as subjects (honest restriction).
SUBJECT_PRONOUNS = frozenset({"he", "she"})


def _p(msg):
    print(msg, flush=True)


def _out_dir(mode):
    d = os.path.join(_REPO, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    os.makedirs(d, exist_ok=True)
    return d


# ===========================================================================
# QA item construction (from LitBank coref gold; anti-circular)
# ===========================================================================
@dataclass
class QAItem:
    book: str
    q_id: str
    sent_idx: int
    verb_lemma: str
    verb_wtok: int
    pronoun_head: str
    pronoun_midx: int
    pronoun_wtok: int
    gold_cluster: int
    gold_answer_head: str
    sent_dist: int
    bucket: str
    antecedent_head: str
    antecedent_is_pronoun: bool   # pronoun-chain signature (72% wall, 29517)
    sentence_text: str


def _canonical_head(cluster_mentions: List[dict]) -> str:
    """The gold cluster's display head = the most frequent non-pronoun span (else the
    most frequent pronoun). Used ONLY for glass-box display of the gold answer."""
    from collections import Counter
    noms = Counter(" ".join(m.get("span_toks", [m["head"]]))
                   for m in cluster_mentions if not m["is_pronoun"])
    if noms:
        return noms.most_common(1)[0][0]
    prons = Counter(m["head"] for m in cluster_mentions)
    return prons.most_common(1)[0][0] if prons else "?"


def _clause_verb(sent_toks: List[str], pron_wtok: int) -> Optional[Tuple[str, int]]:
    """Parse: the verb of the clause whose subject is the pronoun = the nearest content-verb
    predicate STRICTLY AFTER the pronoun position in the same sentence. Returns (lemma, wtok)
    or None. Uses the SHARED event extractor (POS tagger) so verb-finding is genuine parse,
    not a keyword list. idx aligns with wtok (banked _assign_roles relies on this alignment)."""
    text = " ".join(sent_toks)
    events, _tagged = T.extract_events(text)
    after = [e for e in events if e.idx > pron_wtok]
    if not after:
        return None
    after.sort(key=lambda e: e.idx)
    return (after[0].lemma, after[0].idx)


def build_qa_items(book: str, mentions: List[dict], sents: List[List[str]]
                   ) -> List[QAItem]:
    """Select QA items: gendered-singular pronoun that IS a subject (rank 0) with a verb in
    its clause AND a cross-sentence gold antecedent. gold answer = its gold cluster."""
    by_cluster: Dict[int, List[dict]] = {}
    for m in mentions:
        by_cluster.setdefault(m["cluster"], []).append(m)
    targets = build_pronoun_targets(mentions)
    items: List[QAItem] = []
    for t in targets:
        pron = t["target"]
        if t["sent_dist"] < 1:
            continue                                   # cross-sentence only
        if not pron.get("is_subject"):
            continue                                   # pronoun must be a SUBJECT (rank 0)
        if pron["head"] not in SUBJECT_PRONOUNS:
            continue
        si = pron["sent_idx"]
        if si >= len(sents):
            continue
        vb = _clause_verb(sents[si], pron["wtok_start"])
        if vb is None:
            continue                                   # no verb in the clause -> not "who did X?"
        verb_lemma, verb_wtok = vb
        ante = t["antecedent"]
        items.append(QAItem(
            book=book, q_id=f"{book}#m{pron['midx']}", sent_idx=si,
            verb_lemma=verb_lemma, verb_wtok=verb_wtok,
            pronoun_head=pron["head"], pronoun_midx=pron["midx"],
            pronoun_wtok=pron["wtok_start"],
            gold_cluster=pron["cluster"],
            gold_answer_head=_canonical_head(by_cluster[pron["cluster"]]),
            sent_dist=t["sent_dist"], bucket=sent_dist_bucket(t["sent_dist"]),
            antecedent_head=ante["head"],
            antecedent_is_pronoun=bool(ante["is_pronoun"]),
            sentence_text=" ".join(sents[si])))
    return items


# ===========================================================================
# baselines
# ===========================================================================
def recency_answer(pron: dict, mentions: List[dict]) -> Optional[int]:
    """RECENCY baseline: predict the gold cluster of the MOST-RECENT prior gender-compatible
    specific nominal mention (else most-recent prior nominal). No coref machinery."""
    pg = pron.get("gender")
    prior = [m for m in mentions if not m["is_pronoun"] and m["midx"] < pron["midx"]]
    if not prior:
        return None
    compat = [m for m in prior
              if (m.get("gender") == pg or m.get("name_gender") == pg)]
    pick = (compat[-1] if compat else prior[-1])       # mentions are midx-ordered
    return pick["cluster"]


# ===========================================================================
# the QA reader (composes parse + the banked coref backbone)
# ===========================================================================
class ComprehensionQAReader:
    """read(conll) -> answers "Who did [verb]?" for every cross-sentence subject-pronoun QA
    item, via the banked EventCentralityReader recency-centrality coref (29516/29518)."""

    def __init__(self, gaz: Optional[Dict[str, str]] = None) -> None:
        self.gaz = load_name_gender() if gaz is None else gaz
        self.reader_ec = EventCentralityReader(n_dim=EVENT_N_DIM, mem_seed=MEM_SEED)
        self.reader_ss = CorefReader()

    def answer_book(self, conll_path: str):
        book = os.path.splitext(os.path.basename(conll_path))[0]
        mentions, n_sents = parse_litbank_conll(conll_path, name_gender_map=self.gaz)
        sents = parse_conll_sentences(conll_path)
        if len(sents) != n_sents:
            raise RuntimeError("SENTENCE_MISALIGN %s: parse_litbank=%d sentences=%d"
                               % (book, n_sents, len(sents)))
        qa_items = build_qa_items(book, mentions, sents)
        targets = build_pronoun_targets(mentions)

        # reader coref pass (banked backbone) + single-sentence validity pass
        sid_fixed = [i // LOCAL_WINDOW for i in range(n_sents)]
        recs_ec = self.reader_ec.resolve_stream(
            mentions, targets, scene_ids=sid_fixed, topical_mode="rolemass",
            query_memory=True, centrality_mode="recency", **SUP_KW)
        recs_ss = self.reader_ss.resolve_stream(
            mentions, targets, reset_per_sentence=True, strategy="maintained")
        ec_by_midx = {r["target_midx"]: r for r in recs_ec}
        ss_by_midx = {r["target_midx"]: r for r in recs_ss}
        mention_by_midx = {m["midx"]: m for m in mentions}

        answers = []
        for it in qa_items:
            ec = ec_by_midx.get(it.pronoun_midx)
            ss = ss_by_midx.get(it.pronoun_midx)
            pron = mention_by_midx[it.pronoun_midx]
            rec_cluster = recency_answer(pron, mentions)
            reader_cluster = (ec.get("resolved_cluster") if ec else None)
            reader_head = (ec.get("resolved_head") if ec else None)
            reader_attempted = bool(ec.get("attempted")) if ec else False
            ss_cluster = (ss.get("resolved_cluster") if ss else None)
            ss_attempted = bool(ss.get("attempted")) if ss else False
            answers.append({
                "item": it,
                "reader_head": reader_head,
                "reader_cluster": reader_cluster,
                "reader_attempted": reader_attempted,
                "reader_correct": bool(reader_cluster is not None
                                       and reader_cluster == it.gold_cluster),
                "ss_cluster": ss_cluster,
                "ss_attempted": ss_attempted,
                "ss_correct": bool(ss_cluster is not None
                                   and ss_cluster == it.gold_cluster),
                "recency_cluster": rec_cluster,
                "recency_correct": bool(rec_cluster is not None
                                        and rec_cluster == it.gold_cluster),
            })
        return book, qa_items, answers


# ===========================================================================
# glass-box answer trace
# ===========================================================================
def print_trace(ans: dict, tag: str):
    it: QAItem = ans["item"]
    _p("-" * 78)
    chain = ("PRONOUN-CHAIN (antecedent is a pronoun)" if it.antecedent_is_pronoun
             else "nominal antecedent")
    _p(f"[{tag}]  Q: \"Who did {it.verb_lemma}?\"   (book={it.book}  S{it.sent_idx}  "
       f"dist={it.sent_dist}/{it.bucket})")
    _p(f"    clause     : {it.sentence_text}")
    _p(f"    subject    : pronoun '{it.pronoun_head}' @wtok{it.pronoun_wtok} (parse rank 0 = subject)"
       f" -> verb '{it.verb_lemma}' @wtok{it.verb_wtok}")
    _p(f"    coref chain: nearest gold antecedent '{it.antecedent_head}' [{chain}]")
    ra = (f"entity '{ans['reader_head']}' (cluster c{ans['reader_cluster']})"
          if ans["reader_attempted"] else "ABSTAINED (no cross-sentence candidate)")
    _p(f"    READER ans : {ra}")
    _p(f"    gold answer: '{it.gold_answer_head}' (cluster c{it.gold_cluster})  "
       f"=> {'CORRECT' if ans['reader_correct'] else 'INCORRECT'}")


# ===========================================================================
# main run
# ===========================================================================
def run(mode):
    out_dir = _out_dir(mode)
    _write_start_marker(out_dir, mode)
    books = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.conll")))
    books = [b for b in books if os.path.getsize(b) > 1000]
    if mode == "smoke":
        books = books[:SMOKE_N]
    _p(f"[run] mode={mode}  n_books={len(books)}")

    reader = ComprehensionQAReader()
    all_answers: List[dict] = []
    crashed = []
    t0 = time.time()
    for i, path in enumerate(books):
        try:
            book, qa_items, answers = reader.answer_book(path)
        except Exception as e:  # per-book failure-class instrumentation (no silent continue)
            crashed.append({"book": os.path.basename(path), "err": f"{type(e).__name__}: {e}"})
            _p(f"[BOOK-CRASH] {os.path.basename(path)}: {type(e).__name__}: {e}")
            continue
        all_answers.extend(answers)
        r_ok = sum(a["reader_correct"] for a in answers)
        _p(f"  [{i+1:2d}/{len(books)}] {book[:34]:36s} n_qa={len(qa_items):3d} "
           f"reader_ok={r_ok:3d} acc={ (r_ok/len(qa_items)) if qa_items else 0.0:.3f}")
    elapsed = time.time() - t0

    if crashed:
        raise RuntimeError(f"QA_RUNS FAIL: {len(crashed)} book(s) crashed: {crashed}")

    n_qa = len(all_answers)
    reader_ok = sum(a["reader_correct"] for a in all_answers)
    ss_ok = sum(a["ss_correct"] for a in all_answers)
    ss_attempted = sum(a["ss_attempted"] for a in all_answers)
    recency_ok = sum(a["recency_correct"] for a in all_answers)
    reader_attempted = sum(a["reader_attempted"] for a in all_answers)

    reader_acc = reader_ok / n_qa if n_qa else 0.0
    ss_acc = ss_ok / n_qa if n_qa else 0.0
    recency_acc = recency_ok / n_qa if n_qa else 0.0

    # per-item autopsy on MISSES (is it the same-gender centering / pronoun-chain wall?)
    misses = [a for a in all_answers if not a["reader_correct"]]
    n_miss = len(misses)
    miss_abstain = sum(1 for a in misses if not a["reader_attempted"])
    miss_wrong_entity = sum(1 for a in misses if a["reader_attempted"])
    miss_pronoun_chain = sum(1 for a in misses if a["item"].antecedent_is_pronoun)
    all_pronoun_chain = sum(1 for a in all_answers if a["item"].antecedent_is_pronoun)
    # accuracy on the two strata (nominal vs pronoun-chain antecedent)
    nomads = [a for a in all_answers if not a["item"].antecedent_is_pronoun]
    chainads = [a for a in all_answers if a["item"].antecedent_is_pronoun]
    acc_nominal = (sum(a["reader_correct"] for a in nomads) / len(nomads)) if nomads else None
    acc_chain = (sum(a["reader_correct"] for a in chainads) / len(chainads)) if chainads else None
    # bucket breakdown
    from collections import Counter
    bucket_tot = Counter(a["item"].bucket for a in all_answers)
    bucket_ok = Counter(a["item"].bucket for a in all_answers if a["reader_correct"])
    bucket_acc = {b: round(bucket_ok[b] / bucket_tot[b], 4) for b in bucket_tot}

    # ---- glass-box: 3 correct + 2 incorrect answer traces ----
    correct = [a for a in all_answers if a["reader_correct"]]
    incorrect_wrong = [a for a in misses if a["reader_attempted"]]
    incorrect_abstain = [a for a in misses if not a["reader_attempted"]]
    _p("")
    _p("################ GLASS-BOX QA ANSWER TRACES ################")
    for a in correct[:3]:
        print_trace(a, "CORRECT")
    for a in incorrect_wrong[:2]:
        print_trace(a, "INCORRECT/wrong-entity")
    if incorrect_abstain:
        print_trace(incorrect_abstain[0], "INCORRECT/abstain")

    # ---- verdict ----
    qa_runs = (len(crashed) == 0 and n_qa > 0)
    validity_gate = (ss_acc == 0.0 and reader_acc > 0.0 and n_qa > 0)
    coref_bound = 0.30 <= reader_acc <= 0.75
    no_regression = reader_acc >= recency_acc - 0.02
    n_correct_traces = min(len(correct), 3)
    n_incorrect_traces = min(len(incorrect_wrong), 2) + (1 if incorrect_abstain else 0)
    glass_box = (n_correct_traces >= 2 and n_incorrect_traces >= 1)

    gates = {
        "QA_RUNS": qa_runs,
        "VALIDITY_GATE_FIRES": validity_gate,
        "READER_COREF_BOUND": coref_bound,
        "NO_REGRESSION_RECENCY": no_regression,
        "GLASS_BOX": glass_box,
    }
    all_pass = all(gates.values())
    verdict = "DEMONSTRATED" if all_pass else "PARTIAL"

    # arms_differ: reader vs single-sentence decisions must differ (not bit-identical)
    reader_sig = hashlib.sha256(
        repr([(a["item"].q_id, a["reader_cluster"]) for a in all_answers]).encode()
    ).hexdigest()
    ss_sig = hashlib.sha256(
        repr([(a["item"].q_id, a["ss_cluster"]) for a in all_answers]).encode()
    ).hexdigest()
    arms_differ_verified = (reader_sig != ss_sig) and (reader_acc != ss_acc)

    verdict_msg = (
        f"comprehension QA 'who did [verb]?' {verdict}: n_qa={n_qa} "
        f"reader_acc={reader_acc:.4f}(band[.30,.75]={coref_bound}) "
        f"validity_gate(single_sentence_acc={ss_acc:.4f}==0)={validity_gate} "
        f"recency_acc={recency_acc:.4f}(no_regression={no_regression}) "
        f"pronoun_chain_frac={ (all_pronoun_chain/n_qa) if n_qa else 0.0:.3f} "
        f"[COREF-BOUND query-interface demonstration; NOT a new capability]")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": f"{verdict}: {sum(gates.values())}/{len(gates)} gates",
        "elapsed_s": round(elapsed, 2),
        "anchor_name": ANCHOR_NAME,
        "mode": mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_books": len(books),
        "gates": gates,
        "arms_differ_verified": bool(arms_differ_verified),
        "qa": {
            "n_qa_items": n_qa,
            "reader_acc": round(reader_acc, 4),
            "reader_attempted": reader_attempted,
            "single_sentence_acc": round(ss_acc, 4),
            "single_sentence_attempted": ss_attempted,
            "recency_acc": round(recency_acc, 4),
            "reader_minus_recency": round(reader_acc - recency_acc, 4),
            "bucket_acc": bucket_acc,
            "bucket_n": dict(bucket_tot),
            "acc_nominal_antecedent": (round(acc_nominal, 4) if acc_nominal is not None else None),
            "acc_pronoun_chain_antecedent": (round(acc_chain, 4) if acc_chain is not None else None),
        },
        "autopsy": {
            "n_miss": n_miss,
            "miss_abstain": miss_abstain,
            "miss_wrong_entity": miss_wrong_entity,
            "miss_pronoun_chain": miss_pronoun_chain,
            "miss_pronoun_chain_frac": (round(miss_pronoun_chain / n_miss, 4) if n_miss else None),
            "all_pronoun_chain": all_pronoun_chain,
            "all_pronoun_chain_frac": (round(all_pronoun_chain / n_qa, 4) if n_qa else None),
            "note": ("misses tested against the coref arc's triangulated wall: same-gender "
                     "centering + pronoun-chain propagation (29513-29517)"),
        },
        "validity_gate_note": ("single-sentence overlay is EMPTY at a SUBJECT pronoun (clause-"
                               "initial) -> structurally 0.0 on the xsent-subject QA set (29506)"),
        "honest_frame": ("COREF-BOUND read->answer QUERY INTERFACE demonstration (the conversation "
                         "precursor: ask -> justified entity answer + glass-box trace); adds NO "
                         "accuracy beyond the banked coref (~0.45). Reader IS recency-centrality; "
                         "no-regression-vs-recency confirms it reproduces the banked mechanism."),
    }
    _write_metrics(out_dir, metrics)
    _p("")
    _p("################ VERDICT ################")
    for g, v in gates.items():
        _p(f"  {'PASS' if v else 'FAIL'}  {g}")
    _p(verdict_msg)
    _p(f"[autopsy] misses={n_miss} abstain={miss_abstain} wrong_entity={miss_wrong_entity} "
       f"pronoun_chain_of_misses={ (miss_pronoun_chain/n_miss) if n_miss else 0.0:.3f}")
    _p(f"[metrics] {os.path.join(out_dir, 'metrics.json')}")
    return metrics


# ---------------------------------------------------------------------------
# infra (start-marker, atomic metrics, crash diagnostic)
# ---------------------------------------------------------------------------
def _write_start_marker(output_dir, mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def self_test():
    """Real code path: run the QA on the smoke slice + assert the query interface fires,
    the validity gate holds, and the reader beats the single-sentence 0.0."""
    _p("[self-test] running smoke QA (real code path: answer_book() on real LitBank) ...")
    m = run("smoke")
    assert m["qa"]["n_qa_items"] > 0, "no QA items constructed"
    assert m["qa"]["single_sentence_acc"] == 0.0, \
        f"validity gate broken: single_sentence_acc={m['qa']['single_sentence_acc']}"
    assert m["qa"]["reader_acc"] > 0.0, f"reader did not answer any QA: {m['qa']}"
    assert m["arms_differ_verified"], "reader vs single-sentence decisions bit-identical"
    _p("[self-test] PASSED: QA answers from the situation model; validity gate fires; "
       "reader beats single-sentence 0.0.")
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test()
        return
    run(args.mode)


if __name__ == "__main__":
    output_dir = _out_dir("full")
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(output_dir, e)
        raise
