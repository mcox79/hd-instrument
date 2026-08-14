"""hdlab/corpus_registry.py -- THE SHELF. An enumerable registry over every entry in
data/corpora/, so that "what should I read next" is a question the substrate can even represent.
2026-08-14.

WHY THIS EXISTS. notes/gap_driven_learning_loop_audit_2026-08-13.md, section 4: repo-wide there
are ZERO occurrences of `select_corpus` / `choose_corpus` / `next_corpus` / `pick_corpus`. The
entire readable universe of the definitional reading pipeline is a 4-entry Python dict
(`experiments/exp_reading_grounding_loop_cycle2_v1.py:132-137`) while `data/corpora/` holds 36
entries. Simple Wikipedia (251 MB, cleaned) has been on disk since 2026-07-28 and is already read
by a DIFFERENT arc. The loop never declined to read it -- it could not represent it as an option.
This module is that representation, and nothing more: it does not decide, it enumerates.

DESIGN RULES
  * ENUMERATE FROM THE FILESYSTEM (CLAUDE.md Evidence discipline 2). `enumerate_corpora()` walks
    `data/corpora/` and assigns EVERY top-level entry a status. Entries with no usable prose are
    reported as such, with a reason, rather than being silently dropped -- so the registry's own
    coverage is auditable and "28 of 36 readable" is a measured number, not a curated list.
  * DETERMINISTIC. Every directory listing is `sorted(...)`; every dedupe is `sorted(set(...))`.
    No Python `hash()`, no unordered set iteration (PROT-023 / preflight F.5).
  * BOUNDED. A loader never reads more than `max_bytes` from any one file (default 12 MB) and
    never returns more than `max_sentences` sentences. `data/corpora/arc/.../ARC_Corpus.txt` is
    1.48 GB; an unbounded read would be a denial of service on the caller.
  * LAZY + CURSORED. `CorpusHandle` caches a corpus's sentence pool on first touch and serves
    slices from a cursor, so a forager can LEAVE a corpus and later RETURN to fresh material
    rather than re-reading the same opening. Touching a corpus for the first time is genuinely
    expensive, which is exactly the "travel cost" a foraging controller is supposed to pay.
  * SUBSTRATE-FREE. No numpy, no hdlab imports. Unit-testable in milliseconds.

SENTENCE SPLITTING is byte-identical to the recipe already used by the reading pipeline
(`hdlab.grounding_acquisition_loop._clean_sentences` /
`experiments/exp_reading_grounding_loop_cycle1_v1.clean_sentences`):
`re.split(r"[.!?]+['\"’”]?", text)`. Kept identical on purpose so a foraging-chosen
sentence and a schedule-chosen sentence are the same KIND of object.

ASCII-only source.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

__all__ = [
    "CORPORA_DIR",
    "CorpusSpec",
    "CorpusHandle",
    "CorpusRegistry",
    "enumerate_corpora",
    "clean_sentences",
    "STATUS_READABLE",
    "STATUS_NOT_PROSE",
    "STATUS_NO_TEXT_SOURCE",
    "run_all_selftests",
]

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPORA_DIR = os.path.join(_REPO_ROOT, "data", "corpora")

STATUS_READABLE = "READABLE_PROSE"
STATUS_NOT_PROSE = "NOT_PROSE"            # exists, but is a word list / ratings table / manifest
STATUS_NO_TEXT_SOURCE = "NO_TEXT_SOURCE"  # archives only, or a bare script

DEFAULT_MAX_BYTES = 12_000_000
MIN_SENTENCE_CHARS = 25
MAX_SENTENCE_CHARS = 400


def clean_sentences(text: str) -> List[str]:
    """Sentence split, byte-identical recipe to the live reading pipeline's."""
    parts = re.split(r"[.!?]+['\"’”]?", text)
    return [s.strip() for s in parts if s.strip()]


def _acceptable(s: str) -> bool:
    if not (MIN_SENTENCE_CHARS <= len(s) <= MAX_SENTENCE_CHARS):
        return False
    n_alpha = sum(1 for ch in s if ch.isalpha())
    return n_alpha >= 0.6 * len(s)


def _read_head(path: str, max_bytes: int) -> str:
    with open(path, "rb") as f:
        raw = f.read(max_bytes)
    return raw.decode("utf-8", errors="ignore")


# --------------------------------------------------------------------------- readers by format
def _read_txt(paths: Sequence[str], max_bytes: int) -> List[str]:
    out: List[str] = []
    for p in paths:
        text = _read_head(p, max_bytes)
        kept = []
        for ln in text.splitlines():
            s = ln.strip()
            if not s or s.startswith("#") or s.startswith("<"):
                continue
            s = re.sub(r"^[-*]\s+", "", s)
            s = re.sub(r"^\d+\.\s+", "", s)
            kept.append(s)
        out.extend(clean_sentences(" ".join(kept)))
    return out


def _read_conllu(paths: Sequence[str], max_bytes: int) -> List[str]:
    """Universal Dependencies: the raw sentence is on a `# text = ` comment line."""
    out: List[str] = []
    for p in paths:
        for ln in _read_head(p, max_bytes).splitlines():
            if ln.startswith("# text ="):
                out.append(ln.split("=", 1)[1].strip())
    return out


def _read_conll(paths: Sequence[str], max_bytes: int) -> List[str]:
    """LitBank brat-CoNLL: token per line, blank line between sentences, token in column 3."""
    out: List[str] = []
    for p in paths:
        toks: List[str] = []
        for ln in _read_head(p, max_bytes).splitlines():
            if not ln.strip():
                if toks:
                    out.extend(clean_sentences(" ".join(toks)))
                    toks = []
                continue
            cols = ln.split("\t")
            if len(cols) >= 4:
                toks.append(cols[3])
        if toks:
            out.extend(clean_sentences(" ".join(toks)))
    return out


def _harvest_strings(obj, acc: List[str], depth: int = 0) -> None:
    if depth > 8:
        return
    if isinstance(obj, str):
        acc.append(obj)
    elif isinstance(obj, list):
        for x in obj:
            _harvest_strings(x, acc, depth + 1)
    elif isinstance(obj, dict):
        for k in sorted(obj):
            _harvest_strings(obj[k], acc, depth + 1)


def _read_jsonl(paths: Sequence[str], max_bytes: int) -> List[str]:
    out: List[str] = []
    for p in paths:
        text = _read_head(p, max_bytes)
        for ln in text.splitlines():
            ln = ln.strip()
            if not ln.startswith("{") or not ln.endswith("}"):
                continue
            try:
                row = json.loads(ln)
            except json.JSONDecodeError:
                continue          # a truncated final line from the bounded read; never silent-continue on anything else
            acc: List[str] = []
            _harvest_strings(row, acc)
            for s in acc:
                out.extend(clean_sentences(s))
    return out


def _read_json(paths: Sequence[str], max_bytes: int) -> List[str]:
    out: List[str] = []
    for p in paths:
        with open(p, encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        acc: List[str] = []
        _harvest_strings(data, acc)
        for s in acc:
            out.extend(clean_sentences(s))
    return out


def _read_tsv_text_cols(paths: Sequence[str], max_bytes: int) -> List[str]:
    out: List[str] = []
    for p in paths:
        for ln in _read_head(p, max_bytes).splitlines():
            for cell in ln.split("\t"):
                cell = cell.strip()
                if len(cell) >= MIN_SENTENCE_CHARS and " " in cell:
                    out.extend(clean_sentences(cell))
    return out


_READERS: Dict[str, Callable[[Sequence[str], int], List[str]]] = {
    "txt": _read_txt,
    "conllu": _read_conllu,
    "conll": _read_conll,
    "jsonl": _read_jsonl,
    "json": _read_json,
    "tsv": _read_tsv_text_cols,
}


# --------------------------------------------------------------------------- the spec table
@dataclass
class CorpusSpec:
    """One shelf entry. `rel_paths` are repo-relative; `domain` is a coarse hand label used ONLY
    for reporting the domain balance of what got read -- never for any decision."""

    name: str
    status: str
    fmt: str = "txt"
    rel_paths: List[str] = field(default_factory=list)
    domain: str = "unknown"
    note: str = ""

    def abs_paths(self, root: str = _REPO_ROOT) -> List[str]:
        return [os.path.join(root, p.replace("/", os.sep)) for p in self.rel_paths]


# Hand-written per-corpus routing, one row per top-level entry in data/corpora/. The list of NAMES
# is not hand-written -- `enumerate_corpora()` walks the directory and every name it finds must
# appear here or it is reported as UNROUTED, which is a loud failure rather than a silent drop.
_SPECS: List[CorpusSpec] = [
    CorpusSpec("agreement", STATUS_NO_TEXT_SOURCE, note="gzip/tar archives of agreement probes only"),
    CorpusSpec("alice_in_wonderland", STATUS_READABLE, "txt", ["data/corpora/alice_in_wonderland/cleaned/alice_in_wonderland.clean.txt"], "narrative_fiction"),
    CorpusSpec("anne_of_green_gables", STATUS_READABLE, "txt", ["data/corpora/anne_of_green_gables/cleaned/anne_of_green_gables.clean.txt"], "narrative_fiction"),
    CorpusSpec("arc", STATUS_READABLE, "txt", ["data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt"], "science_general", "1.48 GB; bounded head read only"),
    CorpusSpec("base_vocabulary", STATUS_NOT_PROSE, note="ordered word list + AoA/frequency ratings (used as the SEED lexicon and as a held-out probe list, never as reading material)"),
    CorpusSpec("binder", STATUS_NOT_PROSE, note="Binder 2016 experiential-attribute ratings table"),
    CorpusSpec("breadth_v1", STATUS_READABLE, "txt", ["data/corpora/breadth_v1/breadth_corpus_v1.txt"], "mixed"),
    CorpusSpec("clean_gutenberg_multi_v1.py", STATUS_NO_TEXT_SOURCE, note="a cleaning script, not a corpus"),
    CorpusSpec("graded_readers_grade1", STATUS_READABLE, "txt", [
        "data/corpora/graded_readers_grade1/cleaned/mcguffey_primer.clean.txt",
        "data/corpora/graded_readers_grade1/cleaned/mcguffey_first_reader.clean.txt"], "graded_reader_early"),
    CorpusSpec("graded_readers_graded", STATUS_READABLE, "txt", [
        "data/corpora/graded_readers_graded/cleaned/mcguffey_second_reader.clean.txt",
        "data/corpora/graded_readers_graded/cleaned/mcguffey_third_reader.clean.txt",
        "data/corpora/graded_readers_graded/cleaned/mcguffey_fourth_reader.clean.txt"], "graded_reader_mid"),
    CorpusSpec("litbank_coref_conll", STATUS_READABLE, "conll", ["data/corpora/litbank_coref_conll"], "narrative_fiction"),
    CorpusSpec("litbank_ic_derived_v1", STATUS_NOT_PROSE, note="derived implicit-causality disagreement scores"),
    CorpusSpec("little_women", STATUS_READABLE, "txt", ["data/corpora/little_women/cleaned/little_women.clean.txt"], "narrative_fiction"),
    CorpusSpec("mcguffey_graded", STATUS_READABLE, "txt", ["data/corpora/mcguffey_graded/clean"], "graded_reader_full"),
    CorpusSpec("mcguffey_readers", STATUS_READABLE, "txt", ["data/corpora/mcguffey_readers"], "graded_reader_raw"),
    CorpusSpec("mcscript2", STATUS_NO_TEXT_SOURCE, note="zip archive; extracted tree holds no .txt/.json prose"),
    CorpusSpec("onestop", STATUS_READABLE, "txt", [
        "data/corpora/onestop/Texts-SeparatedByReadingLevel/Ele-Txt",
        "data/corpora/onestop/Texts-SeparatedByReadingLevel/Int-Txt",
        "data/corpora/onestop/Texts-SeparatedByReadingLevel/Adv-Txt"], "news", "the frozen 4-entry schedule's entire source"),
    CorpusSpec("openstax_common", STATUS_NO_TEXT_SOURCE, note="fetch/measure scripts only"),
    CorpusSpec("process_articles_v1", STATUS_READABLE, "json", ["data/corpora/process_articles_v1/process_articles.json"], "science_process"),
    CorpusSpec("race", STATUS_READABLE, "jsonl", [
        "data/corpora/race/middle_test.jsonl", "data/corpora/race/high_test.jsonl"], "exam_passages"),
    CorpusSpec("sherlock_holmes", STATUS_READABLE, "txt", [
        "data/corpora/sherlock_holmes/cleaned/adventures.clean.txt",
        "data/corpora/sherlock_holmes/cleaned/memoirs.clean.txt"], "narrative_fiction"),
    CorpusSpec("simplewiki", STATUS_READABLE, "txt", ["data/corpora/simplewiki/simplewiki_clean_v1.txt"], "encyclopedic", "251 MB; on disk since 2026-07-28, never readable by the loop until now"),
    CorpusSpec("social_iqa", STATUS_READABLE, "jsonl", ["data/corpora/social_iqa/hf_dataset/train.jsonl"], "social_commonsense"),
    CorpusSpec("textbook_anatomy_physiology_2e", STATUS_READABLE, "txt", ["data/corpora/textbook_anatomy_physiology_2e/cleaned/anatomy_physiology_2e.clean.txt"], "textbook_biology"),
    CorpusSpec("textbook_biology_2e", STATUS_READABLE, "txt", ["data/corpora/textbook_biology_2e/cleaned/biology_2e.clean.txt"], "textbook_biology"),
    CorpusSpec("textbook_chemistry_2e", STATUS_READABLE, "txt", ["data/corpora/textbook_chemistry_2e/cleaned/chemistry_2e.clean.txt"], "textbook_chemistry"),
    CorpusSpec("textbook_concepts_biology", STATUS_READABLE, "txt", ["data/corpora/textbook_concepts_biology/cleaned/concepts_biology.clean.txt"], "textbook_biology", "the 'bio_new' segment of the frozen schedule"),
    CorpusSpec("textbook_microbiology", STATUS_READABLE, "txt", ["data/corpora/textbook_microbiology/cleaned/microbiology.clean.txt"], "textbook_biology"),
    CorpusSpec("textbook_psychology_2e", STATUS_READABLE, "txt", ["data/corpora/textbook_psychology_2e/cleaned/psychology_2e.clean.txt"], "textbook_psychology"),
    CorpusSpec("tinyshakespeare.txt", STATUS_READABLE, "txt", ["data/corpora/tinyshakespeare.txt"], "drama_verse"),
    CorpusSpec("tom_sawyer", STATUS_READABLE, "txt", ["data/corpora/tom_sawyer/cleaned/tom_sawyer.clean.txt"], "narrative_fiction"),
    CorpusSpec("ud_english_ewt", STATUS_READABLE, "conllu", ["data/corpora/ud_english_ewt/en_ewt-ud-train.conllu"], "web_mixed"),
    CorpusSpec("wiqa", STATUS_READABLE, "jsonl", ["data/corpora/wiqa/raw_official/train_with_expl.jsonl"], "science_process"),
    CorpusSpec("wizard_of_oz", STATUS_READABLE, "txt", ["data/corpora/wizard_of_oz/cleaned/wizard_of_oz.clean.txt"], "narrative_fiction"),
    CorpusSpec("word_image_early_vocab", STATUS_NOT_PROSE, note="image/word manifest only"),
    CorpusSpec("worldtree", STATUS_READABLE, "txt", [
        "data/corpora/worldtree/WorldtreeExplanationCorpusV2.1_Feb2020/explanations-plaintext/explanations.plaintext.train.txt"], "science_explanation"),
]

_SPEC_BY_NAME: Dict[str, CorpusSpec] = {s.name: s for s in _SPECS}


def enumerate_corpora(corpora_dir: str = CORPORA_DIR) -> Tuple[List[CorpusSpec], List[str]]:
    """Walk `corpora_dir`, return (specs_for_every_entry_found, unrouted_names).

    Filesystem first, table second (CLAUDE.md Evidence discipline 2): an entry on disk with no
    row in `_SPECS` shows up in `unrouted` rather than vanishing."""
    if not os.path.isdir(corpora_dir):
        raise FileNotFoundError(corpora_dir)
    found = sorted(os.listdir(corpora_dir))
    specs, unrouted = [], []
    for name in found:
        spec = _SPEC_BY_NAME.get(name)
        if spec is None:
            unrouted.append(name)
        else:
            specs.append(spec)
    return specs, unrouted


# --------------------------------------------------------------------------- handles / registry
class CorpusHandle:
    """A lazily-loaded, cursored view of one corpus. `take(n)` yields the NEXT n unread sentences
    and advances the cursor, so leaving and returning gives fresh material."""

    def __init__(self, spec: CorpusSpec, max_sentences: int, max_bytes: int, root: str = _REPO_ROOT) -> None:
        self.spec = spec
        self.max_sentences = int(max_sentences)
        self.max_bytes = int(max_bytes)
        self.root = root
        self._pool: Optional[List[str]] = None
        self.cursor = 0
        self.n_loads = 0
        self.load_seconds = 0.0

    # ---- loading
    def _expand(self) -> List[str]:
        out: List[str] = []
        for p in self.spec.abs_paths(self.root):
            if os.path.isdir(p):
                for dp, _dn, fn in os.walk(p):
                    for f in sorted(fn):
                        if f.lower().endswith(("." + self.spec.fmt, ".txt")) and self.spec.fmt in ("txt", "conll", "conllu"):
                            out.append(os.path.join(dp, f))
                        elif f.lower().endswith("." + self.spec.fmt):
                            out.append(os.path.join(dp, f))
            elif os.path.isfile(p):
                out.append(p)
        return sorted(set(out))

    @property
    def available(self) -> bool:
        return self.spec.status == STATUS_READABLE and bool(self._expand())

    def pool(self) -> List[str]:
        if self._pool is not None:
            return self._pool
        import time
        t0 = time.time()
        reader = _READERS[self.spec.fmt]
        raw = reader(self._expand(), self.max_bytes)
        seen = set()
        kept: List[str] = []
        for s in raw:
            if not _acceptable(s):
                continue
            if s in seen:
                continue
            seen.add(s)
            kept.append(s)
            if len(kept) >= self.max_sentences:
                break
        self._pool = kept
        self.n_loads += 1
        self.load_seconds += time.time() - t0
        return self._pool

    # ---- cursored access
    def remaining(self) -> int:
        return max(0, len(self.pool()) - self.cursor)

    def take(self, n: int) -> List[str]:
        pool = self.pool()
        out = pool[self.cursor:self.cursor + n]
        self.cursor += len(out)
        return out

    def peek(self, n: int, stride: int = 1) -> List[str]:
        """A non-consuming sample used for RANKING candidate material. Deterministic."""
        pool = self.pool()
        return pool[::max(1, stride)][:n]


class CorpusRegistry:
    """The shelf. Enumerates once, hands out handles."""

    def __init__(self, corpora_dir: str = CORPORA_DIR, *, max_sentences_per_corpus: int = 20000,
                 max_bytes: int = DEFAULT_MAX_BYTES, root: str = _REPO_ROOT) -> None:
        specs, unrouted = enumerate_corpora(corpora_dir)
        self.entries_on_disk = len(specs) + len(unrouted)
        self.unrouted = unrouted
        self.specs = specs
        self.handles: Dict[str, CorpusHandle] = {
            s.name: CorpusHandle(s, max_sentences_per_corpus, max_bytes, root) for s in specs}

    def names(self) -> List[str]:
        return sorted(self.handles)

    def readable_names(self) -> List[str]:
        return sorted(n for n in self.handles if self.handles[n].spec.status == STATUS_READABLE)

    def status_table(self) -> List[dict]:
        rows = []
        for n in sorted(self.handles):
            h = self.handles[n]
            rows.append({"name": n, "status": h.spec.status, "fmt": h.spec.fmt,
                         "domain": h.spec.domain, "n_source_files": len(h._expand()),
                         "note": h.spec.note})
        for n in sorted(self.unrouted):
            rows.append({"name": n, "status": "UNROUTED", "fmt": None, "domain": None,
                         "n_source_files": 0, "note": "on disk but absent from _SPECS"})
        return rows

    def domain_of(self, name: str) -> str:
        h = self.handles.get(name)
        return h.spec.domain if h else "unknown"


# ===================================================================== formula self-tests
def _selftest_every_disk_entry_is_routed() -> None:
    specs, unrouted = enumerate_corpora()
    assert not unrouted, f"UNROUTED corpora on disk (add a _SPECS row): {unrouted}"
    assert len(specs) >= 30, len(specs)


def _selftest_status_counts_are_measured_not_asserted() -> None:
    reg = CorpusRegistry(max_sentences_per_corpus=50)
    names, readable = reg.names(), reg.readable_names()
    assert len(names) == reg.entries_on_disk, (len(names), reg.entries_on_disk)
    assert len(readable) >= 25, readable
    assert "simplewiki" in readable and "textbook_concepts_biology" in readable
    assert "base_vocabulary" not in readable   # a word list is not reading material


def _selftest_every_readable_corpus_actually_yields_sentences() -> None:
    """The whole point of the shelf is that each item can be picked up. Any READABLE row that
    yields nothing is a broken row and must fail loudly here, not silently at forage time."""
    reg = CorpusRegistry(max_sentences_per_corpus=40, max_bytes=400_000)
    empty = []
    for n in reg.readable_names():
        if len(reg.handles[n].pool()) < 5:
            empty.append((n, len(reg.handles[n].pool())))
    assert not empty, f"READABLE corpora that yield <5 sentences: {empty}"


def _selftest_cursor_advances_and_does_not_repeat() -> None:
    reg = CorpusRegistry(max_sentences_per_corpus=200, max_bytes=400_000)
    h = reg.handles["wizard_of_oz"]
    a, b = h.take(10), h.take(10)
    assert len(a) == 10 and len(b) == 10
    assert not (sorted(set(a)) == sorted(set(b))), "cursor must advance"
    assert not (set(a) & set(b)), "returning to a corpus must give FRESH material"
    p1, p2 = h.peek(5), h.peek(5)
    assert p1 == p2, "peek must be non-consuming and deterministic"


def _selftest_loading_is_deterministic() -> None:
    r1 = CorpusRegistry(max_sentences_per_corpus=60, max_bytes=300_000)
    r2 = CorpusRegistry(max_sentences_per_corpus=60, max_bytes=300_000)
    for n in ("simplewiki", "ud_english_ewt", "race", "litbank_coref_conll", "worldtree"):
        assert r1.handles[n].pool() == r2.handles[n].pool(), n


def _selftest_bounded_read_on_the_1_5gb_file() -> None:
    """arc/ARC_Corpus.txt is 1.48 GB. Loading it must be bounded in both bytes and sentences."""
    reg = CorpusRegistry(max_sentences_per_corpus=25, max_bytes=200_000)
    pool = reg.handles["arc"].pool()
    assert 5 <= len(pool) <= 25, len(pool)


def _selftest_frozen_schedule_sources_are_present() -> None:
    """The 4-entry frozen schedule reads onestop (ele/int/adv) + concepts_biology. Both must be
    addressable through the registry, or the FROZEN control arm cannot be run from it."""
    reg = CorpusRegistry(max_sentences_per_corpus=30, max_bytes=200_000)
    for n in ("onestop", "textbook_concepts_biology"):
        assert reg.handles[n].spec.status == STATUS_READABLE
        assert len(reg.handles[n].pool()) >= 5, n


def run_all_selftests() -> dict:
    _selftest_every_disk_entry_is_routed()
    _selftest_status_counts_are_measured_not_asserted()
    _selftest_every_readable_corpus_actually_yields_sentences()
    _selftest_cursor_advances_and_does_not_repeat()
    _selftest_loading_is_deterministic()
    _selftest_bounded_read_on_the_1_5gb_file()
    _selftest_frozen_schedule_sources_are_present()
    reg = CorpusRegistry(max_sentences_per_corpus=10, max_bytes=200_000)
    return {
        "every_disk_entry_routed_ok": True,
        "status_counts_measured_ok": True,
        "every_readable_corpus_yields_sentences_ok": True,
        "cursor_advances_no_repeat_ok": True,
        "loading_deterministic_ok": True,
        "bounded_read_on_1_5gb_file_ok": True,
        "frozen_schedule_sources_present_ok": True,
        "n_entries_on_disk": reg.entries_on_disk,
        "n_readable": len(reg.readable_names()),
        "readable": reg.readable_names(),
        "not_readable": sorted(n for n in reg.names() if n not in set(reg.readable_names())),
    }


if __name__ == "__main__":
    print(json.dumps(run_all_selftests(), indent=2))
    print("ALL SELF-TESTS PASSED")
