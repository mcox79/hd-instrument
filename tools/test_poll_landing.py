"""Witness for tools/orchestrator/poll_landing.py landing-detection robustness.

Exercises the EXACT failure modes from the 2026-07-08/09 incident (bxa1qe5l7
timeout, b526tzfrg silent miss): SSH banner / MOTD lines, CRLF injection, and
OEM-codepage mojibake surrounding the base64 sentinel block. Asserts:

  A. extract_b64_payload recovers the payload despite all of that noise.
  B. A blanked / banner-only / sentinel-missing stdout classifies as UNKNOWN --
     NEVER as an empty-but-OK payload (the root cause: noise read as "not landed").
  C. parse_queue_status + classify_status FIRE (TERMINAL) on a known-landed cell
     and do NOT false-fire (NONTERMINAL) on a running cell.
  D. The whole pre-check chain, fed the noisy stdout, agrees with C.

Run:
    python tools/test_poll_landing.py
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR / "orchestrator"))
import poll_landing as pl  # noqa: E402


def _assert(cond: bool, msg: str):
    if not cond:
        raise AssertionError(msg)


# A realistic queue.json: one landed (completed) cell + one still-running cell.
QUEUE = {
    "experiments": [
        {"name": "b526tzfrg", "status": "completed", "completed_at": "2026-07-08T23:10:00Z"},
        {"name": "bxa1qe5l7", "status": "running", "claimed_at": "2026-07-08T22:50:00Z"},
        {"name": "some_pending_cell", "status": "pending"},
    ]
}
QUEUE_BYTES = json.dumps(QUEUE, indent=2).encode("utf-8")
QUEUE_B64 = base64.b64encode(QUEUE_BYTES).decode("ascii")


def _noisy_stdout(b64: str) -> str:
    """Wrap a base64 payload in the SSH noise that broke the old grep poller."""
    return (
        # SSH banner / MOTD lines the old `type queue.json | grep` matched against
        "Microsoft Windows [Version 10.0.26200.1234]\r\n"
        "(c) Microsoft Corporation. All rights reserved.\r\n"
        "Last login: Wed Jul  8 22:59:01 2026 from 192.168.1.5\r\n"
        # codepage mojibake line (OEM 437 box-drawing bytes decoded as latin-1)
        "█▓░ motd banner ÄÅÉ\r\n"
        f"{pl.B64_BEGIN}\r\n"
        # base64 body, split with CRLF the way a pty would inject it
        f"{b64[:40]}\r\n{b64[40:]}\r\n"
        f"{pl.B64_END}\r\n"
        "Connection to home closed.\r\n"
    )


def run_tests() -> bool:
    tests = 0
    passed = 0

    # A. Payload extraction survives banner + CRLF + codepage noise.
    payload, state = pl.extract_b64_payload(_noisy_stdout(QUEUE_B64))
    _assert(state == "OK", f"A: expected OK extraction, got {state}")
    _assert(payload == QUEUE_B64, "A: extracted payload != original base64")
    _assert(base64.b64decode(payload) == QUEUE_BYTES, "A: decoded bytes mismatch")
    passed += 1; tests += 1

    # B1. Blank stdout (the b526tzfrg silent-miss shape) -> UNKNOWN, not OK/empty.
    _, s_blank = pl.extract_b64_payload("")
    _assert(s_blank == "UNKNOWN", f"B1: blank must be UNKNOWN, got {s_blank}")
    passed += 1; tests += 1

    # B2. Banner-only, sentinels never printed (bxa1qe5l7 timeout shape) -> UNKNOWN.
    banner_only = ("Last login: ...\r\nConnection to home closed.\r\n")
    _, s_banner = pl.extract_b64_payload(banner_only)
    _assert(s_banner == "UNKNOWN", f"B2: banner-only must be UNKNOWN, got {s_banner}")
    passed += 1; tests += 1

    # B3. Truncated block (END sentinel dropped by a mid-stream disconnect) -> UNKNOWN.
    truncated = f"noise\r\n{pl.B64_BEGIN}\r\n{QUEUE_B64}\r\n"  # no END
    _, s_trunc = pl.extract_b64_payload(truncated)
    _assert(s_trunc == "UNKNOWN", f"B3: truncated must be UNKNOWN, got {s_trunc}")
    passed += 1; tests += 1

    # B4. NOFILE marker -> NOFILE (distinct from UNKNOWN).
    _, s_nofile = pl.extract_b64_payload(f"banner\r\n{pl.NOFILE_MARK}\r\n")
    _assert(s_nofile == "NOFILE", f"B4: expected NOFILE, got {s_nofile}")
    passed += 1; tests += 1

    # C1. Known-landed cell -> status completed -> classify TERMINAL (FIRES).
    st, pstate = pl.parse_queue_status(QUEUE_BYTES, "b526tzfrg")
    _assert(pstate == "FOUND" and st == "completed", f"C1: got {st!r},{pstate}")
    _assert(pl.classify_status(st, pstate) == "TERMINAL",
            "C1: landed cell must classify TERMINAL")
    passed += 1; tests += 1

    # C2. Still-running cell -> status running -> classify NONTERMINAL (NO false fire).
    st2, pstate2 = pl.parse_queue_status(QUEUE_BYTES, "bxa1qe5l7")
    _assert(pstate2 == "FOUND" and st2 == "running", f"C2: got {st2!r},{pstate2}")
    _assert(pl.classify_status(st2, pstate2) == "NONTERMINAL",
            "C2: running cell must classify NONTERMINAL (no false landing)")
    passed += 1; tests += 1

    # C3. Absent anchor -> NOTFOUND -> UNKNOWN (escalate, never false 'not landed').
    st3, pstate3 = pl.parse_queue_status(QUEUE_BYTES, "never_dispatched")
    _assert(pstate3 == "NOTFOUND", f"C3: expected NOTFOUND, got {pstate3}")
    _assert(pl.classify_status(st3, pstate3) == "UNKNOWN",
            "C3: absent anchor must classify UNKNOWN")
    passed += 1; tests += 1

    # C4. Corrupt (non-JSON) payload -> UNKNOWN (not a crash, not a false decision).
    st4, pstate4 = pl.parse_queue_status(b"\xff\xfe not json", "b526tzfrg")
    _assert(pstate4 == "UNKNOWN", f"C4: expected UNKNOWN on garbage, got {pstate4}")
    passed += 1; tests += 1

    # D. Full pre-check chain from noisy stdout agrees with C (end-to-end, no live SSH).
    for anchor, want in [("b526tzfrg", "TERMINAL"), ("bxa1qe5l7", "NONTERMINAL")]:
        payload, state = pl.extract_b64_payload(_noisy_stdout(QUEUE_B64))
        raw = base64.b64decode(payload)
        st, pstate = pl.parse_queue_status(raw, anchor)
        got = pl.classify_status(st, pstate)
        _assert(got == want, f"D: {anchor} chain -> {got}, expected {want}")
        passed += 1; tests += 1

    # E. SH-4 double-prefix anchor resolution (name may be exp_exp_<anchor>).
    q_sh4 = {"experiments": [{"name": "exp_exp_foo", "status": "completed"}]}
    st5, pstate5 = pl.parse_queue_status(json.dumps(q_sh4).encode(), "foo")
    _assert(pstate5 == "FOUND" and pl.classify_status(st5, pstate5) == "TERMINAL",
            "E: SH-4 double-prefix must resolve + classify TERMINAL")
    passed += 1; tests += 1

    print(f"\n[test_poll_landing] {passed}/{tests} tests passed")
    return passed == tests


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
