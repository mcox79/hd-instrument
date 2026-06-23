"""Defensive gensim KeyedVectors loader.

Handles two compounding bugs observed on the marsh@home remote runner
(diagnostic 2026-06-23, after 3 cell-author dispatches silently failed):

  Bug 1: gensim.downloader.load() requires a shim file
         <BASE_DIR>/<model_name>/__init__.py with a load_data() function.
         If the model dir was populated by a non-gensim path (manual scp,
         partial download, etc) the shim is missing -> AttributeError
         ('module ... has no attribute load_data').

  Bug 2: a stale process can hold a Windows file-lock on the model .gz.
         gensim's KeyedVectors.load_word2vec_format() then fails with
         PermissionError (WinError 32) and the cell hard-fails before
         it gets to any metrics path.

Resolution order tried, in increasing destructiveness:
  1) gensim.downloader.load(name)                  (the normal path)
  2) write the missing __init__.py shim + retry    (Bug 1 fix)
  3) direct KeyedVectors.load_word2vec_format from an alternate cache_dir
     (e.g. data/gensim_cache_v2) bypassing the locked .gz path (Bug 2 fix)

The helper deliberately does NOT delete or rewrite the .gz under the
primary cache_dir -- that path is shared with the diagnostic ledger and
must remain in place for forensics. Bug 2 is sidestepped via the fresh
alt path, not by force-unlocking the original.

Usage:
    from tools.gensim_load_helper import load_gensim_kv
    kv = load_gensim_kv("word2vec-google-news-300",
                        cache_dir="C:/dev/hd-instrument/data/gensim_cache_v2")

ASCII-only. No third-party deps beyond gensim itself.
"""
from __future__ import annotations

import os
import sys
from typing import Optional

import gensim.downloader as gd
from gensim.models import KeyedVectors


_SHIM_TEMPLATE = (
    'def load_data():\n'
    '    from gensim.models import KeyedVectors\n'
    '    import os\n'
    '    path = os.path.join(os.path.dirname(__file__), "{name}.gz")\n'
    '    is_binary = "word2vec" in "{name}".lower()\n'
    '    return KeyedVectors.load_word2vec_format(path, binary=is_binary)\n'
)


def _write_shim(base_dir: str, name: str) -> str:
    """Write the gensim __init__.py shim for `name` under base_dir/name/."""
    model_dir = os.path.join(base_dir, name)
    os.makedirs(model_dir, exist_ok=True)
    shim_path = os.path.join(model_dir, "__init__.py")
    with open(shim_path, "w", encoding="utf-8") as f:
        f.write(_SHIM_TEMPLATE.format(name=name))
    return shim_path


def _direct_load(cache_dir: str, name: str) -> KeyedVectors:
    """Bypass gensim.downloader and load the .gz directly."""
    gz_path = os.path.join(cache_dir, name, name + ".gz")
    if not os.path.exists(gz_path):
        raise FileNotFoundError(
            "direct gensim load: no .gz at " + gz_path
            + " (cache_dir=" + cache_dir + ", name=" + name + ")"
        )
    is_binary = "word2vec" in name.lower()
    return KeyedVectors.load_word2vec_format(gz_path, binary=is_binary)


def load_gensim_kv(name: str, cache_dir: Optional[str] = None) -> KeyedVectors:
    """Defensive gensim KeyedVectors loader.

    Args:
        name: gensim model name (e.g. 'word2vec-google-news-300').
        cache_dir: absolute path to a gensim BASE_DIR. If provided, both
            gd.base_dir and gd.BASE_DIR are pointed at it. If the primary
            gd.load() path raises PermissionError (file lock), the fallback
            loads the .gz directly from cache_dir (or, failing that, from
            a parallel cache_dir + '_v2' if it exists).

    Returns:
        KeyedVectors instance.

    Raises:
        FileNotFoundError if no .gz can be found in any tried directory.
        Any other exception from KeyedVectors.load_word2vec_format passes
        through (so callers see e.g. corrupted-archive errors instead of
        a swallowed silent fallback).
    """
    if cache_dir:
        try:
            gd.base_dir = cache_dir
            gd.BASE_DIR = cache_dir
        except Exception:
            pass

    base_dir_eff = cache_dir or getattr(gd, "BASE_DIR", None) or os.path.expanduser("~/gensim-data")

    # Attempt 1: the normal gensim path.
    try:
        return gd.load(name)
    except AttributeError as e:
        # Bug 1: missing __init__.py shim. Write it + retry.
        msg = str(e)
        print("[gensim_load_helper] AttributeError on gd.load(" + name + "): "
              + msg + " -- writing __init__.py shim and retrying",
              file=sys.stderr)
        try:
            shim_path = _write_shim(base_dir_eff, name)
            print("[gensim_load_helper] wrote shim at " + shim_path, file=sys.stderr)
        except OSError as oe:
            print("[gensim_load_helper] could not write shim: " + str(oe),
                  file=sys.stderr)
            # Fall through to direct-load attempt below.
        else:
            try:
                return gd.load(name)
            except AttributeError as e2:
                print("[gensim_load_helper] AttributeError persists after shim: "
                      + str(e2) + " -- falling through to direct load",
                      file=sys.stderr)
            except PermissionError as pe2:
                print("[gensim_load_helper] PermissionError after shim retry: "
                      + str(pe2) + " -- falling through to direct load",
                      file=sys.stderr)
        # Final fallback after shim attempt: direct load.
        return _direct_load_with_alt(base_dir_eff, name)
    except PermissionError as pe:
        # Bug 2: file-locked .gz. Skip gensim.downloader; direct-load instead.
        print("[gensim_load_helper] PermissionError on gd.load(" + name + "): "
              + str(pe) + " -- bypassing gensim.downloader, direct .gz load",
              file=sys.stderr)
        return _direct_load_with_alt(base_dir_eff, name)


def _direct_load_with_alt(base_dir_eff: str, name: str) -> KeyedVectors:
    """Try direct .gz load at base_dir_eff; fall back to base_dir_eff + '_v2'."""
    try:
        return _direct_load(base_dir_eff, name)
    except FileNotFoundError as fnf_primary:
        alt = base_dir_eff.rstrip("/\\") + "_v2"
        if os.path.isdir(alt):
            print("[gensim_load_helper] primary .gz missing; trying alt cache_dir "
                  + alt, file=sys.stderr)
            try:
                return _direct_load(alt, name)
            except FileNotFoundError as fnf_alt:
                raise FileNotFoundError(
                    "no .gz under primary (" + base_dir_eff + ") OR alt (" + alt
                    + "): primary=" + str(fnf_primary) + " alt=" + str(fnf_alt)
                )
        raise


if __name__ == "__main__":
    # Smoke: load each of the 3 cells' models from data/gensim_cache_v2.
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache-dir", default="C:/dev/hd-instrument/data/gensim_cache_v2")
    ap.add_argument("--name", default="word2vec-google-news-300")
    args = ap.parse_args()
    print("[gensim_load_helper] smoke: cache_dir=" + args.cache_dir
          + " name=" + args.name)
    kv = load_gensim_kv(args.name, cache_dir=args.cache_dir)
    print("[gensim_load_helper] OK: vector_size=" + str(kv.vector_size)
          + " vocab=" + str(len(kv.key_to_index)))
