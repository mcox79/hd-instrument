#!/usr/bin/env python3
"""Queue-time NLTK-corpus DEPENDENCY CHECK (runs on the remote runner host).

Given the NLTK corpus names a cell's transitive closure imports (from
`extract_sibling_imports.py --nltk-corpora`), verify each is LOADABLE on this
host; auto-PROVISION (download into the venv nltk_data) any that are missing;
re-verify. Exit 0 iff every corpus is loadable, else 1 with a clear per-corpus
report -- so queue_add.sh can REJECT the queue BEFORE committing a GPU slot,
instead of the run dying 7 minutes in with `LookupError: Resource 'X' not found`
(the sg_lite/semcor failure, 2026-09-02). This is the DATA analogue of Pattern 7
(missing code modules) and PROT-022 (missing KB_REFERENT files): NLTK corpora are
neither, and the --self-test often does not exercise the load path.

Usage: python check_nltk_deps.py <corpus> [<corpus> ...]
"""
from __future__ import annotations

import os
import sys

# Import name (nltk.corpus.<X>) -> nltk.download id, for the cases where they differ.
DOWNLOAD_ID = {"framenet": "framenet_v17", "wordnet": "wordnet"}
# Corpora whose load also needs Open Multilingual WordNet.
ALSO = {"wordnet": ["omw-1.4"]}


def _venv_nltk_data() -> str:
    import nltk
    dest = os.path.abspath(os.path.join(os.path.dirname(nltk.__file__), "..", "..", "..", "nltk_data"))
    os.makedirs(dest, exist_ok=True)
    return dest


def _loadable(name: str) -> bool:
    """True iff nltk.corpus.<name> loads (handles .zip corpora transparently, unlike
    a bare nltk.data.find('corpora/<name>') which misses zipped corpora)."""
    import nltk
    try:
        corp = getattr(nltk.corpus, name)
        corp.ensure_loaded()
        return True
    except Exception:
        return False


def main() -> int:
    names = sys.argv[1:]
    if not names:
        return 0
    import nltk
    dest = _venv_nltk_data()
    if dest not in nltk.data.path:
        nltk.data.path.insert(0, dest)
    unresolved = []
    for name in names:
        if _loadable(name):
            print("[nltk-dep] OK          %s" % name)
            continue
        # provision
        dl_ids = [DOWNLOAD_ID.get(name, name)] + ALSO.get(name, [])
        for did in dl_ids:
            try:
                nltk.download(did, download_dir=dest, quiet=True)
            except Exception as e:
                print("[nltk-dep] download err %s (%s): %s" % (name, did, e))
        if _loadable(name):
            print("[nltk-dep] PROVISIONED %s (-> %s)" % (name, ",".join(dl_ids)))
        else:
            print("[nltk-dep] MISSING     %s (could not auto-provision; declare/cache it or download on the runner)" % name)
            unresolved.append(name)
    if unresolved:
        print("[nltk-dep] FAIL: %d NLTK corpus dep(s) unresolvable on this host: %s" % (len(unresolved), ", ".join(unresolved)))
        return 1
    print("[nltk-dep] OK: all %d NLTK corpus dep(s) loadable" % len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
