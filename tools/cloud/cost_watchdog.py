"""Cloud cost watchdog: live cost tracking + auto-shutdown daemon.

Long-running process. Every poll_interval_s:
  1. list_instances() from the Lambda API
  2. compute accumulated spend today + current hourly rate
  3. write data/cloud_cost_tracker.json (dashboard reads it)
  4. if accumulated >= cap: terminate ALL active instances + log CRITICAL
  5. if accumulated >= warn threshold (default 75% of cap): log a single
     HIGH-importance entry per breach event (debounced; not per-poll)

Run with:
  $env:LAMBDA_CLOUD_API_KEY = "..."
  python tools/cloud/cost_watchdog.py --daily-cap 50

Modes:
  --dry-run     prints decisions but does NOT call terminate_instances.
                Use this to validate the cap-firing math against real
                workloads before trusting the auto-shutdown path.
  --once        single poll + write + decision; exits. Useful for tests.

Safety floors (architecture v1 cost discipline):
  - If daily_cap <= 0: refuses to start (a zero/negative cap would either
    shut down everything immediately or never shut down anything).
  - If list_instances() fails: does NOT terminate (network blip should not
    cascade into mass termination). Logs the error; next poll re-evaluates.

The dashboard cost-line turns red at >= 85% of cap (see appendCostLine in
index.html); the daemon terminates at >= 100%. Buffer is intentional: gives
the user a visible warning before automatic action.
"""

from __future__ import annotations

import argparse
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cloud.lambda_client import (  # noqa: E402
    LambdaClient,
    LambdaClientError,
    compute_accumulated_cost,
)
from tools.cloud.cost_tracker import update_cost  # noqa: E402
from tools.orchestrator.state import log_event  # noqa: E402


_DEFAULT_POLL_INTERVAL_S = 60
_DEFAULT_WARN_FRAC = 0.75  # log a warning at this fraction of the cap


def _load_key(key_file_arg: str) -> str | None:
    key = os.environ.get("LAMBDA_CLOUD_API_KEY", "").strip()
    if key:
        return key
    kp = Path(key_file_arg)
    if not kp.is_absolute():
        kp = _REPO_ROOT / kp
    if not kp.is_file():
        return None
    for ln in kp.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln.startswith("LAMBDA_CLOUD_API_KEY="):
            v = ln.split("=", 1)[1].strip().strip('"').strip("'")
            return v
    return None


def _emit_status(event_kind: str, summary: str, importance: str, **extra) -> None:
    """Write a status_log entry tagged source=cloud (architecture v1)."""
    try:
        log_event(
            event_kind,
            summary,
            source="cloud",
            importance=importance,
            **extra,
        )
    except Exception as exc:
        print(f"[cost_watchdog] log_event failed: {exc}", flush=True)


def _format_per_instance(per_instance: list[dict]) -> str:
    """Compact one-line summary of per-instance spend for log messages."""
    if not per_instance:
        return "(no active instances)"
    parts = []
    for p in per_instance:
        parts.append(
            f"{p['instance_id'][:12]}({p['instance_type']}@${p['hourly_rate_usd']:.2f}/hr,"
            f"${p['accumulated_today_usd']:.2f})"
        )
    return ", ".join(parts)


class CostWatchdog:
    """Stateful watchdog so warnings are debounced across polls."""

    def __init__(
        self,
        client: LambdaClient,
        daily_cap_usd: float,
        warn_frac: float = _DEFAULT_WARN_FRAC,
        dry_run: bool = False,
    ):
        if daily_cap_usd <= 0:
            raise ValueError(f"daily_cap_usd must be > 0; got {daily_cap_usd}")
        if not (0.0 < warn_frac < 1.0):
            raise ValueError(f"warn_frac must be in (0, 1); got {warn_frac}")
        self.client = client
        self.daily_cap_usd = float(daily_cap_usd)
        self.warn_frac = float(warn_frac)
        self.dry_run = bool(dry_run)
        # Debounce state — only emit each event once per (UTC day, threshold).
        self._warned_today: str | None = None
        self._capped_today: str | None = None

    def _today_key(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def poll_once(self) -> dict:
        """Single poll cycle. Returns the snapshot it wrote (or None if no-op).

        Always writes cloud_cost_tracker.json (even when no instances) so the
        dashboard reflects fresh state.
        """
        try:
            instances = self.client.list_instances()
        except LambdaClientError as exc:
            print(f"[cost_watchdog] list_instances failed: {exc}", flush=True)
            _emit_status(
                "cloud_api_error",
                f"list_instances failed: {exc}",
                importance="MEDIUM",
            )
            return {"ok": False, "error": str(exc)}

        active = [
            i for i in instances
            if i.status in ("active", "booting", "terminating", "unhealthy")
        ]
        accumulated, hourly_rate, per_instance = compute_accumulated_cost(active)
        snapshot = {
            "ok": True,
            "accumulated_today_usd": accumulated,
            "current_hourly_rate_usd": hourly_rate,
            "active_instances": per_instance,
            "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        }

        # Always write cost tracker (zero-instance state is also signal).
        try:
            update_cost(
                daily_budget_usd=self.daily_cap_usd,
                accumulated_today_usd=accumulated,
                current_hourly_rate_usd=hourly_rate,
                active_instances=per_instance,
            )
        except Exception as exc:
            print(f"[cost_watchdog] update_cost failed: {exc}", flush=True)

        # Warn threshold (debounced: one warning per UTC day per threshold).
        today = self._today_key()
        warn_threshold = self.daily_cap_usd * self.warn_frac
        if accumulated >= warn_threshold and accumulated < self.daily_cap_usd:
            if self._warned_today != today:
                self._warned_today = today
                ratio_pct = (accumulated / self.daily_cap_usd) * 100
                _emit_status(
                    "cloud_cost_alert",
                    f"Cloud spend ${accumulated:.2f} / ${self.daily_cap_usd:.2f} "
                    f"({ratio_pct:.0f}%); auto-shutdown at 100%",
                    importance="HIGH",
                    plain_language=(
                        f"Cloud cost has crossed {self.warn_frac*100:.0f}% of the daily "
                        f"budget cap (${accumulated:.2f} of ${self.daily_cap_usd:.2f}). "
                        f"At 100% the watchdog terminates all running instances "
                        f"automatically. Consider terminating non-essential runs."
                    ),
                    accumulated_today_usd=accumulated,
                    daily_cap_usd=self.daily_cap_usd,
                    active=_format_per_instance(per_instance),
                )

        # Hard cap: terminate all active instances.
        if accumulated >= self.daily_cap_usd:
            if self._capped_today == today:
                # Already terminated today; just keep reporting.
                return snapshot
            self._capped_today = today
            active_ids = [p["instance_id"] for p in per_instance]
            ratio_pct = (accumulated / self.daily_cap_usd) * 100
            if self.dry_run:
                print(f"[cost_watchdog] [DRY-RUN] would terminate {active_ids} "
                      f"(${accumulated:.2f} >= cap ${self.daily_cap_usd:.2f})",
                      flush=True)
                _emit_status(
                    "cloud_budget_exceeded",
                    f"[DRY-RUN] Cloud spend ${accumulated:.2f} >= cap "
                    f"${self.daily_cap_usd:.2f}; would terminate {len(active_ids)}",
                    importance="CRITICAL",
                    plain_language=(
                        f"DRY-RUN: cloud cost ${accumulated:.2f} crossed the daily cap "
                        f"of ${self.daily_cap_usd:.2f}. In live mode the watchdog "
                        f"would now terminate {len(active_ids)} running instance(s) "
                        f"to stop further spend."
                    ),
                    accumulated_today_usd=accumulated,
                    daily_cap_usd=self.daily_cap_usd,
                    active_instances=active_ids,
                    action="dry_run_simulated_terminate",
                )
            else:
                print(f"[cost_watchdog] BUDGET EXCEEDED — terminating {active_ids}",
                      flush=True)
                try:
                    terminated = self.client.terminate_instances(active_ids)
                except LambdaClientError as exc:
                    print(f"[cost_watchdog] terminate_instances failed: {exc}",
                          flush=True)
                    _emit_status(
                        "cloud_budget_exceeded",
                        f"CRITICAL: spend ${accumulated:.2f} >= cap "
                        f"${self.daily_cap_usd:.2f} but TERMINATE API CALL FAILED: {exc}",
                        importance="CRITICAL",
                        plain_language=(
                            f"Cloud cost crossed the daily cap and the auto-shutdown "
                            f"call FAILED with error: {exc}. Manually terminate "
                            f"instances {active_ids} via the Lambda web console NOW."
                        ),
                        accumulated_today_usd=accumulated,
                        daily_cap_usd=self.daily_cap_usd,
                        active_instances=active_ids,
                        action="terminate_failed",
                    )
                    return snapshot
                _emit_status(
                    "cloud_budget_exceeded",
                    f"AUTO-SHUTDOWN: spend ${accumulated:.2f} >= cap "
                    f"${self.daily_cap_usd:.2f}; terminated {len(terminated)}",
                    importance="CRITICAL",
                    plain_language=(
                        f"Cloud cost ${accumulated:.2f} crossed the daily cap "
                        f"of ${self.daily_cap_usd:.2f}. The watchdog auto-shutdown "
                        f"{len(terminated)} running instance(s) to stop further "
                        f"spend. Manual review needed before relaunching."
                    ),
                    accumulated_today_usd=accumulated,
                    daily_cap_usd=self.daily_cap_usd,
                    terminated_instances=terminated,
                    action="auto_shutdown",
                )

        return snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Lambda Cloud cost watchdog + auto-shutdown")
    parser.add_argument("--daily-cap", type=float, default=50.0,
                        help="Daily spend cap in USD (default 50)")
    parser.add_argument("--warn-frac", type=float, default=_DEFAULT_WARN_FRAC,
                        help="Warn-event firing threshold as fraction of cap (default 0.75)")
    parser.add_argument("--poll-interval", type=float, default=_DEFAULT_POLL_INTERVAL_S,
                        help=f"Poll cadence in seconds (default {_DEFAULT_POLL_INTERVAL_S})")
    parser.add_argument("--key-file", default=".env.lambda",
                        help="Env-file containing LAMBDA_CLOUD_API_KEY")
    parser.add_argument("--dry-run", action="store_true",
                        help="Log decisions but DO NOT actually terminate instances")
    parser.add_argument("--once", action="store_true",
                        help="Single poll + exit (useful for cron and testing)")
    args = parser.parse_args()

    key = _load_key(args.key_file)
    if not key:
        print("[ERROR] no LAMBDA_CLOUD_API_KEY env var and no key file.")
        return 1
    try:
        client = LambdaClient(api_key=key)
    except LambdaClientError as exc:
        print(f"[ERROR] client init failed: {exc}")
        return 1

    try:
        wd = CostWatchdog(
            client=client,
            daily_cap_usd=args.daily_cap,
            warn_frac=args.warn_frac,
            dry_run=args.dry_run,
        )
    except ValueError as exc:
        print(f"[ERROR] watchdog init: {exc}")
        return 1

    mode = "DRY-RUN" if args.dry_run else "LIVE"
    print(f"[cost_watchdog] starting in {mode} mode; daily cap ${args.daily_cap:.2f}; "
          f"warn at {args.warn_frac*100:.0f}%; poll every {args.poll_interval:.0f}s")
    _emit_status(
        "cloud_watchdog_armed",
        f"Cost watchdog armed in {mode} mode; daily cap ${args.daily_cap:.2f}",
        importance="MEDIUM",
        plain_language=(
            f"The cloud cost watchdog is now running in {mode} mode. It will check "
            f"Lambda spend every {args.poll_interval:.0f} seconds and "
            + ("simulate" if args.dry_run else "automatically")
            + f" terminate all running instances if accumulated spend reaches "
            f"${args.daily_cap:.2f} in a UTC day."
        ),
        daily_cap_usd=args.daily_cap,
        dry_run=args.dry_run,
    )

    # Honor Ctrl-C without traceback noise.
    stop = {"flag": False}

    def _on_sigint(signum, frame):
        stop["flag"] = True
        print("\n[cost_watchdog] caught signal; exiting after current poll", flush=True)

    try:
        signal.signal(signal.SIGINT, _on_sigint)
    except (AttributeError, ValueError):
        # Not in main thread or unsupported on this platform; tolerable.
        pass

    while True:
        snap = wd.poll_once()
        if snap.get("ok"):
            acc = snap["accumulated_today_usd"]
            hr = snap["current_hourly_rate_usd"]
            n = len(snap["active_instances"])
            print(f"[cost_watchdog] {snap['ts']}  ${acc:.2f} accumulated  "
                  f"${hr:.2f}/hr  {n} active",
                  flush=True)
        if args.once or stop["flag"]:
            break
        # Sleep in 1s slices so SIGINT is responsive.
        for _ in range(int(args.poll_interval)):
            if stop["flag"]:
                break
            time.sleep(1)
        if stop["flag"]:
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())
