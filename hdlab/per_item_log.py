"""Per-item stage-attribution logging -- reusable, low-overhead, ADDITIVE.

Persists ONE row per held-out eval item ALONGSIDE the existing metrics.json so
retrieval / composition / refuse outcomes can be sliced BY CAUSE (pipeline stage)
and BY ITEM PROPERTY (near-dup, branching/out-degree, polysemy, chain-depth).
This is the missing logging layer that structurally blocked clean stage-attribution
(status_log 2026-07-07T17:07:59Z: per-item outcomes were never persisted).

Design guarantees (load-bearing):
- ADDITIVE ONLY. Writes its own files (per_item_log.jsonl + per_item_log_manifest.json)
  next to metrics.json. It NEVER touches metrics.json, verdicts, or eval logic.
- FAIL-SAFE. Any internal error disables the logger and is recorded in the manifest;
  it NEVER raises into the caller's eval loop (instrumentation must not break science).
- LOW OVERHEAD. Streams append to one open file handle; holds nothing in memory but a
  small rollup counter. Honest cap: past `cap` rows it stops writing and counts the
  truncation (logged in the manifest) so the log is never silently partial.

Row schema (compact jsonl, one JSON object per line):
  {"id": <item id str>, "stage": <str>, "out": {...outcome...}, "tag": {...properties...}}

  stage   -- which pipeline stage/arm produced this outcome, e.g. "retrieval:GRADED_m6",
             "compose:SEM_BEAM", "refuse". The DELTA across stages is the attribution.
  out     -- stage outcome. Conventions (all optional, caller fills what applies):
               retrieval:   {"agree10": float, "rank": int|None, "hit": bool, "top": [ids]}
               composition: {"rank": int, "hit10": bool, "hop_ok": [bool,...]}
               refuse:      {"decision": "accept"|"refuse", "conf": float}
             If out contains "miss" (bool) it drives the miss-rate rollup; otherwise a
             miss is inferred from out["hit"] == False when present.
  tag     -- item properties for cause-slicing: {"neardup": bool, "polysemy": bool,
             "out_degree": int, "chain_depth": int, "with_path": bool, "trivial": bool}.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


class PerItemLogger:
    """Streaming, fail-safe, capped per-item stage-attribution writer.

    Usage:
        pil = PerItemLogger(out_dir, eval_name="marginpush_v1", cap=2_000_000)
        pil.log(item_id, stage="retrieval:GRADED_m6",
                outcome={"agree10": 0.4, "miss": False},
                tags={"neardup": True, "polysemy": False})
        summary = pil.close()   # writes manifest, returns rollup dict
    """

    def __init__(self, out_dir: os.PathLike | str, eval_name: str,
                 cap: int = 2_000_000, enabled: bool = True) -> None:
        self.out_dir = Path(out_dir)
        self.eval_name = str(eval_name)
        self.cap = int(cap)
        self.enabled = bool(enabled)
        self.n_written = 0
        self.n_capped = 0
        self.error: Optional[str] = None
        self._fh = None
        # rollups: miss counts per stage and per boolean tag, for instant attribution.
        self._stage_n: Dict[str, int] = {}
        self._stage_miss: Dict[str, int] = {}
        self._tag_n: Dict[str, int] = {}
        self._tag_miss: Dict[str, int] = {}
        self.log_path = self.out_dir / "per_item_log.jsonl"
        self.manifest_path = self.out_dir / "per_item_log_manifest.json"
        if not self.enabled:
            return
        try:
            self.out_dir.mkdir(parents=True, exist_ok=True)
            # truncate any stale log from a prior run (fresh per eval invocation)
            self._fh = open(self.log_path, "w", encoding="utf-8", buffering=1 << 20)
        except Exception as exc:  # noqa: BLE001 - instrumentation must never break eval
            self.enabled = False
            self.error = f"open_failed: {type(exc).__name__}: {str(exc)[:200]}"

    @staticmethod
    def _is_miss(outcome: Optional[Dict[str, Any]]) -> Optional[bool]:
        if not outcome:
            return None
        if "miss" in outcome:
            return bool(outcome["miss"])
        if "hit" in outcome:
            return not bool(outcome["hit"])
        if "hit10" in outcome:
            return not bool(outcome["hit10"])
        return None

    def log(self, item_id: Any, stage: str,
            outcome: Optional[Dict[str, Any]] = None,
            tags: Optional[Dict[str, Any]] = None) -> None:
        """Append one row. Fail-safe: never raises into the caller."""
        if not self.enabled:
            return
        if self.n_written >= self.cap:
            self.n_capped += 1
            return
        try:
            row = {"id": item_id, "stage": stage}
            if outcome is not None:
                row["out"] = outcome
            if tags is not None:
                row["tag"] = tags
            self._fh.write(json.dumps(row, separators=(",", ":")) + "\n")
            self.n_written += 1
            miss = self._is_miss(outcome)
            self._stage_n[stage] = self._stage_n.get(stage, 0) + 1
            if miss is not None and miss:
                self._stage_miss[stage] = self._stage_miss.get(stage, 0) + 1
            if tags:
                for k, v in tags.items():
                    if v is True:  # only roll up boolean-true property tags
                        self._tag_n[k] = self._tag_n.get(k, 0) + 1
                        if miss is not None and miss:
                            self._tag_miss[k] = self._tag_miss.get(k, 0) + 1
        except Exception as exc:  # noqa: BLE001
            self.enabled = False
            self.error = f"write_failed: {type(exc).__name__}: {str(exc)[:200]}"

    def log_array(self, item_ids: Iterable[Any], stage: str, agree,
                  miss_thresh: float, tag_masks: Optional[Dict[str, Any]] = None) -> None:
        """Convenience: bulk-log a retrieval per-item score array (agree10-style).

        agree[i] is the per-item score; miss = agree[i] < miss_thresh.
        tag_masks maps tag-name -> boolean sequence aligned with item_ids (e.g. neardup,
        polysemy). Lengths are min-clamped defensively so a short mask never raises.
        """
        if not self.enabled:
            return
        ids = list(item_ids)
        n = min(len(ids), len(agree))
        masks = tag_masks or {}
        for i in range(n):
            a = float(agree[i])
            tags = {}
            for k, seq in masks.items():
                try:
                    tags[k] = bool(seq[i])
                except Exception:  # noqa: BLE001 - defensive on ragged masks
                    pass
            self.log(ids[i], stage,
                     outcome={"agree10": a, "miss": a < miss_thresh},
                     tags=tags or None)

    def close(self) -> Dict[str, Any]:
        """Flush, close, write the manifest, and return the rollup summary."""
        try:
            if self._fh is not None:
                self._fh.flush()
                self._fh.close()
        except Exception as exc:  # noqa: BLE001
            self.error = self.error or f"close_failed: {type(exc).__name__}"
        self._fh = None

        def _rates(n_map: Dict[str, int], miss_map: Dict[str, int]) -> Dict[str, Dict[str, float]]:
            out = {}
            for k, n in sorted(n_map.items()):
                m = miss_map.get(k, 0)
                out[k] = {"n": n, "miss": m,
                          "miss_rate": (m / n) if n else float("nan")}
            return out

        manifest = {
            "eval_name": self.eval_name,
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "schema": "jsonl:{id,stage,out,tag}; ADDITIVE (does not affect metrics.json)",
            "log_file": self.log_path.name,
            "n_rows_written": self.n_written,
            "n_rows_capped_dropped": self.n_capped,
            "cap": self.cap,
            "capped": self.n_capped > 0,
            "enabled": self.enabled,
            "error": self.error,
            "miss_rate_by_stage": _rates(self._stage_n, self._stage_miss),
            "miss_rate_by_true_tag": _rates(self._tag_n, self._tag_miss),
        }
        try:
            tmp = self.manifest_path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            os.replace(tmp, self.manifest_path)
        except Exception as exc:  # noqa: BLE001
            manifest["error"] = manifest.get("error") or f"manifest_write_failed: {type(exc).__name__}"
        return manifest


def self_test() -> int:
    """Scaffold-free witness: inject a KNOWN miss and confirm it is attributed to the
    right stage + tag, and that overhead per row is negligible."""
    import tempfile
    import time as _time

    ok = True
    with tempfile.TemporaryDirectory() as td:
        pil = PerItemLogger(td, eval_name="selftest", cap=1000)
        # 3 clean hits (not neardup), 1 KNOWN miss that IS a near-dup.
        pil.log("hit_a", "retrieval:X", {"agree10": 0.9, "miss": False}, {"neardup": False})
        pil.log("hit_b", "retrieval:X", {"agree10": 0.8, "miss": False}, {"neardup": False})
        pil.log("hit_c", "retrieval:X", {"agree10": 0.7, "miss": False}, {"neardup": False})
        pil.log("MISS_d", "retrieval:X", {"agree10": 0.1, "miss": True}, {"neardup": True})
        summary = pil.close()

        # log file has exactly 4 rows
        lines = [l for l in Path(td, "per_item_log.jsonl").read_text().splitlines() if l]
        ok &= (len(lines) == 4)
        # the injected miss is attributed to stage retrieval:X (1 miss / 4)
        st = summary["miss_rate_by_stage"]["retrieval:X"]
        ok &= (st["miss"] == 1 and st["n"] == 4)
        # ...and to the neardup tag (100% miss-rate in the near-dup pool)
        nd = summary["miss_rate_by_true_tag"].get("neardup")
        ok &= (nd is not None and nd["miss"] == 1 and nd["n"] == 1 and nd["miss_rate"] == 1.0)
        # the miss row is traceable to exactly one item + stage in the raw log
        miss_rows = [json.loads(l) for l in lines if json.loads(l)["out"].get("miss")]
        ok &= (len(miss_rows) == 1 and miss_rows[0]["id"] == "MISS_d"
               and miss_rows[0]["stage"] == "retrieval:X"
               and miss_rows[0]["tag"]["neardup"] is True)
        ok &= (summary["error"] is None and summary["capped"] is False)

        # cap is honest: write 5 into a cap-2 logger -> 2 written, 3 counted-dropped
        pil2 = PerItemLogger(td, eval_name="captest", cap=2)
        for i in range(5):
            pil2.log(f"r{i}", "s", {"miss": False})
        s2 = pil2.close()
        ok &= (s2["n_rows_written"] == 2 and s2["n_rows_capped_dropped"] == 3
               and s2["capped"] is True)

        # overhead: per-row cost must be tiny (<50us/row on any sane machine)
        pil3 = PerItemLogger(td, eval_name="perf", cap=10_000_000)
        t0 = _time.perf_counter()
        N = 50_000
        for i in range(N):
            pil3.log(i, "retrieval:X", {"agree10": 0.5, "miss": False}, {"neardup": False})
        pil3.close()
        us_per_row = (_time.perf_counter() - t0) / N * 1e6
        ok &= (us_per_row < 50.0)
        print(f"[per_item_log] self-test {'OK' if ok else 'FAIL'} "
              f"(rows=4 attributed; cap honest 2+3; overhead={us_per_row:.2f} us/row)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(self_test())
