"""Read-only SSH client for the dashboard.

Connects to marsh@home via paramiko, reuses one persistent transport,
and enforces a strict prefix-allowlist + blocked-token list on every
command. Anything not matching the allowlist raises before touching
the wire.
"""

from __future__ import annotations

import socket
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as _FuturesTimeout
from pathlib import Path
from typing import Optional

import paramiko


ALLOWED_PREFIXES: tuple[str, ...] = (
    'tasklist /FI "IMAGENAME eq python.exe"',
    'nvidia-smi --query-gpu=',
    'nvidia-smi --query-compute-apps=',
    'type C:\\dev\\hd-instrument\\data\\',
    'powershell -Command "Get-Content ',
    'powershell -Command "Get-ChildItem ',
    # UTF-8 variants: needed for files containing emoji / non-ASCII (capability map).
    # Prefix still requires Get-Content / Get-ChildItem after the encoding setup,
    # so this isn't an arbitrary-command escape hatch — the verb is locked in.
    'powershell -Command "[Console]::OutputEncoding = [Text.Encoding]::UTF8; Get-Content ',
    'powershell -Command "[Console]::OutputEncoding = [Text.Encoding]::UTF8; Get-ChildItem ',
)

BLOCKED_TOKENS: tuple[str, ...] = (
    'Remove-Item', 'Stop-Process', 'Copy-Item', 'New-Item',
    'Set-Content', 'Out-File', 'Add-Content', 'Move-Item',
    'taskkill', ' del ', ' rm ', '>', '|',
)


class CommandNotAllowed(ValueError):
    pass


class PollTimeout(RuntimeError):
    """run_parallel exceeded its wall-clock cap.

    Raised when the aggregate poll (all commands) does not complete within the
    wall cap. The dominant cause is a hung ``recv_exit_status()``: paramiko's
    exit-status wait does NOT honor the per-channel ``exec_command`` timeout, so
    when the remote force-closes the socket (WinError 10054) mid-poll the read
    blocks FOREVER and the poller process stays alive but wedged. The caller must
    treat this as a dead transport and ``reset()`` -- closing the transport wakes
    the wedged wait so the leaked worker thread can exit.
    """
    pass


def _resolve_alias(alias: str) -> dict:
    cfg = paramiko.SSHConfig()
    p = Path.home() / ".ssh" / "config"
    if p.exists():
        with open(p) as f:
            cfg.parse(f)
    return cfg.lookup(alias)


def _is_self(target_host: str) -> bool:
    """True if target_host resolves to a local interface (prevents self-SSH loop)."""
    target = target_host.strip().lower()
    if target in ("localhost", "127.0.0.1", "::1"):
        return True
    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror:
        return False
    if target_ip.startswith("127."):
        return True
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            if info[4][0] == target_ip:
                return True
    except socket.gaierror:
        pass
    return False


def _check_allowed(cmd: str) -> None:
    if not any(cmd.startswith(p) for p in ALLOWED_PREFIXES):
        raise CommandNotAllowed(f"prefix not in allowlist: {cmd[:80]!r}")
    for tok in BLOCKED_TOKENS:
        if tok in cmd:
            raise CommandNotAllowed(f"blocked token {tok!r} in command")


class ReadOnlySSH:
    """Persistent SSH connection, read-only, allowlist-enforced."""

    def __init__(self, alias: str = "home", user_default: str = "marsh"):
        self.alias = alias
        self.user_default = user_default
        self._client: Optional[paramiko.SSHClient] = None

    def _connect(self) -> paramiko.SSHClient:
        if self._client is not None:
            t = self._client.get_transport()
            if t is not None and t.is_active():
                return self._client
            self._client.close()

        cfg = _resolve_alias(self.alias)
        hostname = cfg.get("hostname", self.alias)
        username = cfg.get("user", self.user_default)
        port = int(cfg.get("port", 22))
        identityfile = cfg.get("identityfile")

        if _is_self(hostname):
            raise RuntimeError(
                f"ReadOnlySSH: refusing to connect to {hostname!r}: target is this machine. "
                f"Dashboard must run on a different host than the one being polled "
                f"(else sshd MaxStartups exhaustion locks out the polled host)."
            )

        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        kwargs: dict = {
            "hostname": hostname,
            "username": username,
            "port": port,
            "timeout": 10.0,
            "auth_timeout": 10.0,
            "banner_timeout": 10.0,
        }
        if identityfile:
            kwargs["key_filename"] = identityfile
        client.connect(**kwargs)
        self._client = client
        return client

    def run(self, cmd: str, timeout: float = 10.0) -> str:
        """Run an allowlisted command, return stdout. Raises on non-zero exit."""
        _check_allowed(cmd)
        client = self._connect()
        stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="replace")
        err = stderr.read().decode("utf-8", errors="replace")
        rc = stdout.channel.recv_exit_status()
        if rc != 0:
            raise RuntimeError(f"exit {rc} for {cmd[:60]!r}: {err.strip()[:200]}")
        return out

    def run_parallel(
        self,
        cmds: list[str],
        timeout: float = 10.0,
        tolerate_errors: bool = False,
        wall_cap: float | None = None,
    ) -> list[str | None]:
        """Run allowlisted commands concurrently on one transport, preserve order.

        With tolerate_errors=True, a per-command failure yields None at that slot
        rather than raising. Useful when some targets (e.g. per-experiment .log)
        may not exist yet.

        wall_cap bounds the AGGREGATE wall time across all commands. paramiko's
        recv_exit_status() ignores the per-command exec_command timeout, so a
        remote socket force-close (WinError 10054) can wedge a read forever -- the
        exact failure that silently froze the feed for ~7.2h. When the aggregate
        exceeds wall_cap we raise PollTimeout instead of blocking; the caller
        resets the transport (which wakes the wedged read so the leaked worker
        thread exits). Default: max(60, timeout*6) -- generous above the per-cmd
        socket timeout so normal slow polls never trip, tight enough to convert a
        forever-hang into a ~60-90s bounded failure.
        """
        for cmd in cmds:
            _check_allowed(cmd)
        client = self._connect()

        def _one(cmd: str) -> str | None:
            channel = None
            try:
                stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
                channel = stdout.channel
                out = stdout.read().decode("utf-8", errors="replace")
                rc = channel.recv_exit_status()
                if rc != 0:
                    err = stderr.read().decode("utf-8", errors="replace")
                    raise RuntimeError(f"exit {rc} for {cmd[:60]!r}: {err.strip()[:200]}")
                return out
            except Exception:
                if tolerate_errors:
                    return None
                raise
            finally:
                # Explicit close — without this, channels accumulate faster than GC
                # can reclaim them and the SSH server hits its MaxSessions limit.
                if channel is not None:
                    try:
                        channel.close()
                    except Exception:
                        pass

        # Cap concurrency tightly. paramiko's Transport thread internally retries
        # failed channel opens (Secsh channel open FAILED messages in stderr); each
        # retry can leak a half-open channel + FD. With max_workers=5 and ~15 commands
        # per poll, channel pressure compounded until the OS terminated the process
        # silently after ~30-60 minutes (no Python traceback). max_workers=2 keeps
        # the in-flight channel count bounded and the SSH server's MaxSessions=10 has
        # plenty of headroom.
        if wall_cap is None:
            wall_cap = max(60.0, timeout * 6.0)
        if not cmds:
            return []
        deadline = time.monotonic() + wall_cap
        pool = ThreadPoolExecutor(max_workers=min(2, max(1, len(cmds))))
        futures = [pool.submit(_one, c) for c in cmds]
        results: list[str | None] = []
        timed_out = False
        try:
            for fut in futures:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    timed_out = True
                    break
                try:
                    results.append(fut.result(timeout=remaining))
                except _FuturesTimeout:
                    timed_out = True
                    break
        finally:
            # NEVER wait=True: a wedged recv_exit_status would make shutdown()
            # block forever, defeating the whole point of the wall cap. On the
            # happy path every future is already done so wait=False reclaims the
            # threads immediately; on timeout the wedged worker unblocks once the
            # caller calls reset() (closes the transport) and then exits on its own.
            pool.shutdown(wait=False)
        if timed_out:
            raise PollTimeout(
                f"run_parallel exceeded wall cap {wall_cap:.0f}s "
                f"({len(results)}/{len(cmds)} cmds returned before cap); "
                f"likely a wedged recv_exit_status / force-closed socket"
            )
        return results

    def reset(self) -> None:
        """Force-close the SSH transport; next call will reconnect cleanly."""
        self.close()

    # --- SFTP (used only for the capability_map atomic-read path) ---
    # SFTP bypasses the shell allowlist — to keep the read-only contract, every
    # SFTP method below validates the path against this strict prefix list.
    _SFTP_ALLOWED_PATH_PREFIXES: tuple[str, ...] = (
        "c:/dev/hd-instrument/",
        "c:\\dev\\hd-instrument\\",
    )

    def _check_sftp_path(self, path: str) -> None:
        norm = path.lower().replace("\\", "/")
        for prefix in self._SFTP_ALLOWED_PATH_PREFIXES:
            if norm.startswith(prefix.replace("\\", "/")):
                return
        raise CommandNotAllowed(f"sftp path not under hd-instrument root: {path!r}")

    def _get_sftp(self):
        """Open (and cache) an SFTPClient on the existing transport."""
        client = self._connect()
        sftp = getattr(self, "_sftp_client", None)
        if sftp is not None:
            try:
                # Best-effort liveness check; if dead, reopen.
                sftp.listdir(".")
                return sftp
            except Exception:
                try:
                    sftp.close()
                except Exception:
                    pass
                self._sftp_client = None
        self._sftp_client = client.open_sftp()
        return self._sftp_client

    def sftp_listdir(self, remote_dir: str) -> list[str]:
        self._check_sftp_path(remote_dir)
        return self._get_sftp().listdir(remote_dir)

    def sftp_stat(self, remote_path: str):
        self._check_sftp_path(remote_path)
        return self._get_sftp().stat(remote_path)

    def sftp_read_text(self, remote_path: str, encoding: str = "utf-8") -> str:
        self._check_sftp_path(remote_path)
        with self._get_sftp().file(remote_path, "rb") as f:
            return f.read().decode(encoding, errors="replace")

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, *exc):
        self.close()
