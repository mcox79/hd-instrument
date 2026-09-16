"""_space_reader -- RE-EXPORT ALIAS for the ONE space organ, `hdlab/space_reader.py`.

ONE BRAIN STRUCTURE = ONE ORGAN WITH ARMS (owner 2026-09-11). Until 2026-09-16 this file was a full SECOND COPY of
the space reader, left behind by the 2026-09-09 promotion ("promote _space_reader -> hdlab/space_reader.py
(byte-faithful); reader _read_space repointed", 3ed0c7f4a), and the two copies had DRIFTED four landings apart:

  pri 109  the copy called `parse_litbank_conll` WITHOUT the category organ (no `span_upos` on its mentions)
  pri 116  the copy read the CoNLL through `parse_conll_sentences(path)` when that default was still lowercasing
  pri 125  `build_backbone` / `read_locations_in_substrate` grew a `mentions=` parameter (the reader's OWN
           discovered stream) that the copy never had
  pri 127  the copy still imported `nltk.corpus.wordnet` at read time, the organ reads `hdlab.lexicon_foundation`

That drift is what pri 137 exists to close, and it caused a measurement defect that ran for a week: W4 of
`verification/test_space_ground_binding.py` switched the named-ground lever off by stubbing
`experiments._space_reader.ground_bind_events` -- a function in THIS copy, which the live reader had stopped
running -- so both of its arms ran the lever ON and the check could not fail for the reason it was written.

WHY THE ALIAS IS AT `sys.modules` LEVEL AND NOT `from hdlab.space_reader import *`: a star-import COPIES references
into this module's namespace, so `import experiments._space_reader as SP; SP.f = stub` would rebind a private copy
of the name and the organ would keep running its own -- the same defect with a new spelling. Replacing the
`sys.modules` entry makes `experiments._space_reader is hdlab.space_reader` TRUE, so every one of the 45 experiment
cells and 12 witnesses that address the old path -- including every monkeypatch and every
`from experiments._space_reader import f` -- reaches the ONE organ. (CPython's `importlib._bootstrap._load`
re-reads `sys.modules[spec.name]` after executing the module, which is what makes this supported rather than a
trick.) The organ's module-level surface is a strict SUPERSET of this copy's, so no importer loses a name.

Repoint new code at `hdlab.space_reader` directly; this alias exists so the transition needs no flag day.
"""
import sys

from hdlab import space_reader as _organ

sys.modules[__name__] = _organ
