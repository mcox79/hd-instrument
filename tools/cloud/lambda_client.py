"""Lambda Cloud API client.

Minimum-viable wrapper for the Lambda Cloud API that supports the four
operations the testbed cloud session needs:

  1. List available instance types + their per-hour prices (`list_instance_types`)
  2. List currently-running instances (`list_instances`, `get_instance`)
  3. Launch a new instance (`launch_instance`)
  4. Terminate one or more instances (`terminate_instances`)

Plus SSH-key management for instance bootstrap.

NOTE on cost tracking: Lambda's API does not expose a real-time billing
endpoint. Cost-accumulation is computed locally by walking
`list_instances()` and multiplying each instance's `(now - started_at)` by
its hourly rate from the catalog. See `compute_accumulated_cost()`. This is
more precise than waiting on Lambda's billing aggregation lag, AND we own
the math the auto-shutdown daemon depends on.

Authentication:
  Lambda Cloud uses HTTP Basic Auth with the API key as the username and an
  empty password. We accept the key via env var `LAMBDA_CLOUD_API_KEY` so it
  never lives in code or git history.

Mock mode:
  Set `mock=True` to instantiate without an API key for unit-test purposes;
  every method then returns canned fixtures. Useful for verifying the
  cost-accumulator math + the auto-shutdown daemon's decision logic without
  any real API traffic.

Per architecture v1: this module lives under tools/cloud/ which is testbed-
owned. The cloud session (when active) imports it; until then, it's just
scaffolding that the canary scripts exercise.
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


# Lambda has been migrating from cloud.lambdalabs.com to the shorter
# cloud.lambda.ai domain. Both have been live; the newer endpoint is what
# the current dashboard hands users for `curl -u <key>:` examples.
LAMBDA_API_BASE = "https://cloud.lambda.ai/api/v1"
_DEFAULT_TIMEOUT_S = 60.0  # bumped from 30s; Cloudflare in front of Lambda
                            # API can return slow under load. Per-request retry
                            # gives 3 attempts; total worst case = 60s * 3 +
                            # 2s + 4s = ~186s before LambdaClientError raises.


@dataclass
class InstanceType:
    """Catalog entry for one Lambda instance SKU."""
    name: str                    # e.g. "gpu_1x_a100_sxm4"
    description: str             # human-readable
    price_cents_per_hour: int    # canonical cost field
    gpu_description: str         # e.g. "1x NVIDIA A100"
    regions_available: list[str] = field(default_factory=list)

    @property
    def hourly_rate_usd(self) -> float:
        return self.price_cents_per_hour / 100.0


@dataclass
class Instance:
    """A currently-running (or transitioning) Lambda instance."""
    instance_id: str
    instance_type_name: str
    status: str                  # 'booting' | 'active' | 'terminated' | 'unhealthy' | ...
    ip: Optional[str]
    region_name: str
    hourly_rate_usd: float
    started_at: Optional[datetime] = None  # parsed UTC


class LambdaClientError(RuntimeError):
    """Raised on any Lambda API failure (HTTP, parsing, auth)."""


class LambdaClient:
    """Thin wrapper around the Lambda Cloud REST API.

    Usage:
        client = LambdaClient()  # reads LAMBDA_CLOUD_API_KEY from env
        catalog = client.list_instance_types()
        instances = client.list_instances()

    For offline testing:
        client = LambdaClient(mock=True)
        # all methods return fixture data; no network calls.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = LAMBDA_API_BASE,
        timeout_s: float = _DEFAULT_TIMEOUT_S,
        mock: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.mock = mock
        if mock:
            self.api_key = "MOCK"
            return
        key = api_key or os.environ.get("LAMBDA_CLOUD_API_KEY", "").strip()
        if not key:
            raise LambdaClientError(
                "LAMBDA_CLOUD_API_KEY env var is empty. Set it or pass api_key=..., "
                "or use mock=True for offline testing."
            )
        self.api_key = key

    # ---- HTTP transport ----------------------------------------------------

    def _auth_header(self) -> str:
        """Basic auth with api_key as username, empty password."""
        raw = f"{self.api_key}:".encode("utf-8")
        return "Basic " + base64.b64encode(raw).decode("ascii")

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
    ) -> dict:
        """Make a single HTTP request and parse the JSON response.

        Raises LambdaClientError on any non-2xx response or parse failure.
        In mock mode this should never be called -- mock methods bypass it.
        """
        if self.mock:
            raise LambdaClientError("mock=True client made an HTTP call; this is a bug")
        url = f"{self.base_url}{path}"
        headers = {
            "Authorization": self._auth_header(),
            "Accept": "application/json",
            # Cloudflare in front of cloud.lambda.ai blocks Python's default
            # urllib User-Agent ('Python-urllib/3.x') with a 403. A standard
            # curl/browser UA passes the WAF cleanly.
            "User-Agent": "curl/8.4.0",
        }
        data: Optional[bytes] = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        # Retry policy: transient errors (timeout / URLError / 5xx / 429) get
        # up to 3 attempts with exponential backoff (2s / 4s / 8s). Permanent
        # errors (4xx auth / 404 not found) raise immediately.
        # Rationale: wait_for_active polls every ~5s for up to 5 min; a single
        # 30s timeout used to tank the entire multi-hour dispatch (Dispatch 11
        # 2026-06-02). Per-call retry isolates transient network blips.
        import time
        max_attempts = 3
        last_exc: Optional[Exception] = None
        for attempt in range(1, max_attempts + 1):
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    raw = resp.read()
                    if not raw:
                        return {}
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError as exc:
                        raise LambdaClientError(
                            f"non-JSON response from {method} {path}: {raw[:200]!r}"
                        ) from exc
            except urllib.error.HTTPError as exc:
                try:
                    err_body = exc.read().decode("utf-8", errors="replace")
                except Exception:
                    err_body = ""
                # 5xx and 429 are transient; 4xx (except 429) are permanent
                if exc.code >= 500 or exc.code == 429:
                    last_exc = exc
                    if attempt < max_attempts:
                        time.sleep(2 ** attempt)
                        continue
                raise LambdaClientError(
                    f"HTTP {exc.code} from {method} {path} "
                    f"(attempt {attempt}/{max_attempts}): {err_body[:400]}"
                ) from exc
            except urllib.error.URLError as exc:
                # Timeouts (socket.timeout wrapped in URLError), DNS, connection
                # reset, etc. -- all transient.
                last_exc = exc
                if attempt < max_attempts:
                    time.sleep(2 ** attempt)
                    continue
                raise LambdaClientError(
                    f"network error to {method} {path} "
                    f"after {max_attempts} attempts: {exc.reason}"
                ) from exc
            except TimeoutError as exc:
                # Python 3.10+ raises a top-level TimeoutError directly in some
                # scenarios (esp. ssl.read). Treat same as URLError.
                last_exc = exc
                if attempt < max_attempts:
                    time.sleep(2 ** attempt)
                    continue
                raise LambdaClientError(
                    f"timeout to {method} {path} after {max_attempts} attempts: {exc}"
                ) from exc
        # Unreachable; keeps mypy happy
        raise LambdaClientError(
            f"exhausted retries to {method} {path}: {last_exc!r}"
        )

    # ---- Instance types (catalog) ------------------------------------------

    def list_instance_types(self) -> list[InstanceType]:
        """Return the full catalog of instance SKUs available to this account.

        Each entry includes price_cents_per_hour (the canonical price source
        for cost tracking) and regions_available.
        """
        if self.mock:
            return _MOCK_INSTANCE_TYPES[:]
        resp = self._request("GET", "/instance-types")
        data = resp.get("data") or {}
        out: list[InstanceType] = []
        if isinstance(data, dict):
            for name, entry in data.items():
                info = entry.get("instance_type") or {}
                regions_raw = entry.get("regions_with_capacity_available") or []
                regions = [r.get("name") for r in regions_raw if isinstance(r, dict) and r.get("name")]
                out.append(InstanceType(
                    name=str(info.get("name") or name),
                    description=str(info.get("description") or ""),
                    price_cents_per_hour=int(info.get("price_cents_per_hour") or 0),
                    gpu_description=str(info.get("gpu_description") or ""),
                    regions_available=regions,
                ))
        return out

    def cheapest_available_gpu(self) -> Optional[InstanceType]:
        """Return the cheapest instance type that has capacity available now.

        Used by the canary lifecycle test to minimize spend on the smoke run.
        """
        types = self.list_instance_types()
        with_capacity = [t for t in types if t.regions_available]
        if not with_capacity:
            return None
        with_capacity.sort(key=lambda t: t.price_cents_per_hour)
        return with_capacity[0]

    # ---- Instances ---------------------------------------------------------

    def list_instances(self) -> list[Instance]:
        """List currently-running and recently-terminated instances."""
        if self.mock:
            return _MOCK_INSTANCES[:]
        resp = self._request("GET", "/instances")
        rows = resp.get("data") or []
        out: list[Instance] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            info_type = row.get("instance_type") or {}
            started_at = None
            ts_raw = row.get("started_at") or row.get("created_at")
            if ts_raw:
                try:
                    started_at = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                except ValueError:
                    started_at = None
            out.append(Instance(
                instance_id=str(row.get("id") or ""),
                instance_type_name=str(info_type.get("name") or ""),
                status=str(row.get("status") or "unknown"),
                ip=row.get("ip") or None,
                region_name=str((row.get("region") or {}).get("name") or ""),
                hourly_rate_usd=float(info_type.get("price_cents_per_hour") or 0) / 100.0,
                started_at=started_at,
            ))
        return out

    def get_instance(self, instance_id: str) -> Optional[Instance]:
        """Fetch a single instance by id, or None if absent."""
        for inst in self.list_instances():
            if inst.instance_id == instance_id:
                return inst
        return None

    def launch_instance(
        self,
        region_name: str,
        instance_type_name: str,
        ssh_key_names: list[str],
        file_system_names: Optional[list[str]] = None,
        quantity: int = 1,
        name: Optional[str] = None,
    ) -> list[str]:
        """Launch one or more instances. Returns the new instance IDs.

        The caller is responsible for waiting on `status == "active"` before
        attempting SSH. See `wait_for_active()`.
        """
        if self.mock:
            return [f"mock-instance-{int(time.time())}-{i}" for i in range(quantity)]
        body: dict[str, Any] = {
            "region_name": region_name,
            "instance_type_name": instance_type_name,
            "ssh_key_names": ssh_key_names,
            "quantity": int(quantity),
        }
        if file_system_names:
            body["file_system_names"] = file_system_names
        if name:
            body["name"] = name
        resp = self._request("POST", "/instance-operations/launch", body)
        data = resp.get("data") or {}
        ids = data.get("instance_ids") or []
        return [str(i) for i in ids]

    def terminate_instances(self, instance_ids: list[str]) -> list[str]:
        """Terminate the given instances. Returns the list actually terminated."""
        if not instance_ids:
            return []
        if self.mock:
            return list(instance_ids)
        body = {"instance_ids": list(instance_ids)}
        resp = self._request("POST", "/instance-operations/terminate", body)
        data = resp.get("data") or {}
        terminated = data.get("terminated_instances") or []
        out: list[str] = []
        for row in terminated:
            iid = (row.get("id") if isinstance(row, dict) else None)
            if iid:
                out.append(str(iid))
        return out

    def wait_for_active(
        self,
        instance_id: str,
        timeout_s: float = 900.0,
        poll_interval_s: float = 10.0,
    ) -> Instance:
        """Poll an instance until it reaches `active` status.

        Raises LambdaClientError on timeout or terminal failure status.
        """
        deadline = time.time() + timeout_s
        last_status = "unknown"
        while time.time() < deadline:
            inst = self.get_instance(instance_id)
            if inst is None:
                last_status = "missing"
            else:
                last_status = inst.status
                if last_status == "active":
                    return inst
                if last_status in ("terminated", "unhealthy"):
                    raise LambdaClientError(
                        f"instance {instance_id} entered terminal status {last_status}"
                    )
            time.sleep(poll_interval_s)
        raise LambdaClientError(
            f"instance {instance_id} not active after {timeout_s}s; last status {last_status}"
        )

    def wait_for_capacity(
        self,
        instance_type_name: str,
        regions: Optional[list[str]] = None,
        max_wait_s: float = 3600.0,
        poll_interval_s: float = 30.0,
        verbose: bool = True,
    ) -> list[str]:
        """Poll the instance-type catalog until the requested type has capacity.

        Lambda's API has no spot/preemptible/reservation primitive (verified
        against docs 2026-06-01: on-demand + off-API reserved contract only;
        no spot tier). This helper closes the obvious-zero-capacity case:
        before we make a billable launch_instance() call, verify the catalog
        reports regions_available non-empty for our type. If empty, poll
        until populated OR max_wait_s elapses.

        Net effect: zero billable cost during capacity-wait (no instance is
        created until capacity exists). Does NOT fully eliminate the race
        between "saw capacity" and "called launch" -- another customer can
        grab the slot in the gap -- but it does eliminate launches against
        a known-empty queue.

        Args:
            instance_type_name: e.g. "gpu_1x_h100_sxm5"
            regions: if non-empty, accept ONLY when regions_available
                contains at least one of these. Else accept any non-empty
                regions_available. (Use this when you have a region
                preference / data-locality requirement.)
            max_wait_s: hard cap on total polling wait time.
            poll_interval_s: between catalog refreshes. 30s default.
            verbose: print one-line status per poll.

        Returns: the regions_available list at the moment capacity was seen.
        Raises LambdaClientError on max_wait_s timeout.
        """
        deadline = time.time() + max_wait_s
        n_polls = 0
        while time.time() < deadline:
            n_polls += 1
            try:
                catalog = self.list_instance_types()
            except LambdaClientError as exc:
                if verbose:
                    print(f"  [capacity-poll {n_polls}] catalog query failed: {exc}",
                          flush=True)
                time.sleep(poll_interval_s)
                continue
            match = next((t for t in catalog if t.name == instance_type_name),
                         None)
            if match is None:
                raise LambdaClientError(
                    f"instance type {instance_type_name} not in catalog")
            available = list(match.regions_available)
            if regions:
                available = [r for r in available if r in regions]
            if available:
                if verbose:
                    print(f"  [capacity-poll {n_polls}] {instance_type_name} "
                          f"available in {available} (after {n_polls * poll_interval_s:.0f}s wait)",
                          flush=True)
                return available
            if verbose:
                req_str = f" requested-regions={regions}" if regions else ""
                print(f"  [capacity-poll {n_polls}] {instance_type_name} "
                      f"NO capacity{req_str}; sleeping {poll_interval_s:.0f}s",
                      flush=True)
            time.sleep(poll_interval_s)
        raise LambdaClientError(
            f"{instance_type_name} did not get capacity within {max_wait_s}s "
            f"(polled {n_polls} times). No billable launch attempted."
        )

    # ---- SSH key management ------------------------------------------------

    def list_ssh_keys(self) -> list[dict]:
        """List SSH keys registered for this account."""
        if self.mock:
            return [{"id": "mock-key-1", "name": "mock-key", "public_key": "ssh-rsa AAA..."}]
        resp = self._request("GET", "/ssh-keys")
        return list(resp.get("data") or [])

    def add_ssh_key(self, name: str, public_key: Optional[str] = None) -> dict:
        """Register a public key OR have Lambda generate one. Returns the API row.

        When `public_key` is None, Lambda generates a new key-pair and returns
        the private key in the response (one chance to record it; subsequent
        list_ssh_keys() will not surface the private half).
        """
        if self.mock:
            return {"id": "mock-key-new", "name": name, "public_key": "ssh-rsa MOCK..."}
        body: dict[str, Any] = {"name": name}
        if public_key:
            body["public_key"] = public_key
        return self._request("POST", "/ssh-keys", body).get("data", {})


# ---------------------------------------------------------------------------
# Cost-accumulation math (local; no API call)
# ---------------------------------------------------------------------------

def compute_accumulated_cost(
    instances: list[Instance],
    now: Optional[datetime] = None,
) -> tuple[float, float, list[dict]]:
    """Sum running cost from a list of instances.

    Returns (accumulated_today_usd, current_hourly_rate_usd, per_instance).

    - accumulated_today_usd: dollars spent since UTC midnight on all
      currently-or-recently active instances (we treat 'terminating' as
      still billing for safety).
    - current_hourly_rate_usd: sum of hourly rates of active instances.
    - per_instance: list of dicts with instance_id, instance_type, hourly_rate,
      started_at, accumulated_today_usd (rounded to cents).
    """
    if now is None:
        now = datetime.now(timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    midnight_utc = now.replace(hour=0, minute=0, second=0, microsecond=0)

    acc_today = 0.0
    hourly = 0.0
    per_instance: list[dict] = []
    BILLABLE = {"active", "booting", "terminating", "unhealthy"}
    for inst in instances:
        if inst.status not in BILLABLE:
            continue
        rate = float(inst.hourly_rate_usd or 0.0)
        if rate <= 0:
            continue
        # Started this billing day; clamp the window.
        if inst.started_at is None:
            # Without a start time, account for at least the rate.
            inst_acc = 0.0
        else:
            start = inst.started_at
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            billing_start = max(start, midnight_utc)
            elapsed_hours = max(0.0, (now - billing_start).total_seconds() / 3600.0)
            inst_acc = rate * elapsed_hours
        acc_today += inst_acc
        if inst.status in ("active", "booting"):
            hourly += rate
        per_instance.append({
            "instance_id": inst.instance_id,
            "instance_type": inst.instance_type_name,
            "hourly_rate_usd": round(rate, 4),
            "started_at": (inst.started_at.isoformat() if inst.started_at else None),
            "accumulated_today_usd": round(inst_acc, 2),
            "status": inst.status,
        })
    return (round(acc_today, 2), round(hourly, 2), per_instance)


# ---------------------------------------------------------------------------
# Mock fixtures (offline / unit-test mode)
# ---------------------------------------------------------------------------

_MOCK_INSTANCE_TYPES: list[InstanceType] = [
    InstanceType(
        name="gpu_1x_a10",
        description="1x NVIDIA A10 (24 GB)",
        price_cents_per_hour=75,
        gpu_description="1x NVIDIA A10",
        regions_available=["us-east-1"],
    ),
    InstanceType(
        name="gpu_1x_a100_sxm4",
        description="1x NVIDIA A100 SXM4 (40 GB)",
        price_cents_per_hour=140,
        gpu_description="1x NVIDIA A100 SXM4",
        regions_available=["us-west-1"],
    ),
    InstanceType(
        name="gpu_1x_h100_pcie",
        description="1x NVIDIA H100 PCIe (80 GB)",
        price_cents_per_hour=249,
        gpu_description="1x NVIDIA H100 PCIe",
        regions_available=["us-west-2"],
    ),
]

_MOCK_INSTANCES: list[Instance] = []
