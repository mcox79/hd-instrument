"""One-shot CUDA-eligibility scanner for pending remote_cpu_queue cells."""
import json
import os
import re


def main():
    q = json.load(open("C:/dev/hd-instrument/data/remote_cpu_queue/queue.json"))
    pending = [e for e in q["experiments"] if e.get("status") == "pending"]
    print(f"PENDING COUNT: {len(pending)}")
    for i, e in enumerate(pending):
        script = e.get("script", "")
        path = os.path.join("C:/dev/hd-instrument", script)
        src_has_cuda = False
        src_has_arg = False
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                src = f.read()
            src_has_cuda = bool(re.search(r"torch\.cuda", src))
            if not src_has_cuda:
                src_has_cuda = ".cuda()" in src or "device='cuda'" in src or 'device="cuda"' in src
            src_has_arg = "--device" in src or "args.device" in src
        flag = "CUDA" if (src_has_cuda or src_has_arg) else "----"
        print(f"[{i:2d}] {flag} | {e['name']:60s} | cuda_in_src={src_has_cuda} arg={src_has_arg}")


if __name__ == "__main__":
    main()
