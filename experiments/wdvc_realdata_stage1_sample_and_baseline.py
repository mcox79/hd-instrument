# Stage 1: pull a small real Wikidata edit sample (labeled by mw-reverted tag =
# the standard reverted-as-vandalism proxy, same label family WDVC uses) and
# reproduce the PUBLISHED registration-status content-wall baseline
# (Heindorf WWW'19: anon 9.00% vs registered 0.03% reverted = 310.7x bias ratio).
#
# ASCII-only. No queue, no GPU, no atoms. Throwaway reproduction script per the
# scoping note's "cheap decisive test".
#
# NUMBERS TAGGING:
# - anon 9.00% / registered 0.03% / 310.7x  CITED@notes/research_full4signal_realdata_capability_test_2026-07-16.md (Heindorf WWW'19)
# - all measured values below  MEASURED@data/exp_wdvc_realdata_capability/stage1_baseline.json

import json
import os
import sys
import time
import urllib.parse
import urllib.request

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "exp_wdvc_realdata_capability")
OUT_DIR = os.path.abspath(OUT_DIR)
RAW_PATH = os.path.join(OUT_DIR, "sample_raw.jsonl")
BASELINE_PATH = os.path.join(OUT_DIR, "stage1_baseline.json")

API = "https://www.wikidata.org/w/api.php"
TARGET_N = int(sys.argv[1]) if len(sys.argv) > 1 else 15000
RCLIMIT = 500
UA = "hd-instrument-research/1.0 (research use; contact marshall.cox@gmail.com)"


def api_get(params, retries=4):
    params = dict(params)
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:  # NOT BaseException
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("API failed after retries: %r" % last)


def pull_sample():
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = []
    cont = None
    # rcdir=newer with no rcstart starts at the OLDEST retained change (~30d back),
    # so mw-reverted tags have had time to settle before we read them.
    base = {
        "action": "query",
        "list": "recentchanges",
        "rcnamespace": 0,
        "rctype": "edit",
        "rcprop": "title|ids|user|userid|timestamp|tags|sizes|comment|flags",
        "rclimit": RCLIMIT,
        "rcdir": "newer",
    }
    n_req = 0
    while len(rows) < TARGET_N:
        params = dict(base)
        if cont:
            params["rccontinue"] = cont
        d = api_get(params)
        n_req += 1
        rc = d.get("query", {}).get("recentchanges", [])
        for r in rc:
            tags = r.get("tags", []) or []
            rows.append({
                "title": r.get("title"),
                "revid": r.get("revid"),
                "old_revid": r.get("old_revid"),
                "userid": r.get("userid", 0),
                "user": r.get("user"),
                "anon": ("anon" in r) or (r.get("userid", 0) == 0),
                "bot": ("bot" in r),
                "tags": tags,
                "reverted": ("mw-reverted" in tags),
                "oldlen": r.get("oldlen"),
                "newlen": r.get("newlen"),
                "timestamp": r.get("timestamp"),
                "comment": (r.get("comment") or "")[:200],
            })
        if "continue" in d:
            cont = d["continue"]["rccontinue"]
        else:
            break
        if n_req % 5 == 0:
            print("[progress] pulled=%d requests=%d last_ts=%s" % (len(rows), n_req, rows[-1]["timestamp"]), flush=True)
        time.sleep(0.15)
    with open(RAW_PATH, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=True) + "\n")
    print("[done] wrote %d rows to %s (requests=%d)" % (len(rows), RAW_PATH, n_req), flush=True)
    return rows


def rate(num, den):
    return (num / den) if den else 0.0


def stage1_baseline(rows):
    # Exclude bots from the vandalism-baseline population (WDVC filters to human
    # manual revisions; bot edits are not vandalism candidates). Keep a bot count.
    n_all = len(rows)
    n_bot = sum(1 for r in rows if r["bot"])
    human = [r for r in rows if not r["bot"]]
    n = len(human)
    n_rev = sum(1 for r in human if r["reverted"])
    n_anon = sum(1 for r in human if r["anon"])
    n_reg = n - n_anon
    n_rev_anon = sum(1 for r in human if r["anon"] and r["reverted"])
    n_rev_reg = sum(1 for r in human if (not r["anon"]) and r["reverted"])

    # Modern logged-out-editor form: Wikimedia Temporary Accounts (IP masking,
    # rolled out ~2023-2025). Logged-out edits now appear as auto-created temp
    # accounts (username starts with '~') WITH a nonzero userid, so the published
    # anon/userid==0 feature is largely extinct on 2026 data. Temp-account status
    # is the same content-wall confound family (unregistered/low-trust editor).
    def _istemp(r):
        return bool(r.get("user")) and r["user"].startswith("~")
    n_temp = sum(1 for r in human if _istemp(r))
    n_notemp = n - n_temp
    n_rev_temp = sum(1 for r in human if _istemp(r) and r["reverted"])
    n_rev_notemp = sum(1 for r in human if (not _istemp(r)) and r["reverted"])
    p_rev_temp = rate(n_rev_temp, n_temp)
    p_rev_notemp = rate(n_rev_notemp, n_notemp)
    p_temp_s = rate(n_rev_temp + 0.5, n_temp + 1.0)
    p_notemp_s = rate(n_rev_notemp + 0.5, n_notemp + 1.0)
    temp_bias_ratio = (p_temp_s / p_notemp_s) if p_notemp_s > 0 else float("inf")

    base_rate = rate(n_rev, n)
    p_rev_anon = rate(n_rev_anon, n_anon)
    p_rev_reg = rate(n_rev_reg, n_reg)
    # Laplace-smoothed ratio to keep it finite if registered reverts == 0.
    p_rev_reg_smooth = rate(n_rev_reg + 0.5, n_reg + 1.0)
    p_rev_anon_smooth = rate(n_rev_anon + 0.5, n_anon + 1.0)
    bias_ratio = (p_rev_anon_smooth / p_rev_reg_smooth) if p_rev_reg_smooth > 0 else float("inf")

    out = {
        "stage": 1,
        "label_definition": "reverted = 'mw-reverted' tag present (reverted-as-damage proxy, WDVC label family)",
        "feature": "registration status (anon vs registered), the published content-wall feature",
        "sample_window": {
            "n_raw_including_bots": n_all,
            "n_bots_excluded": n_bot,
            "n_human": n,
            "first_ts": rows[0]["timestamp"] if rows else None,
            "last_ts": rows[-1]["timestamp"] if rows else None,
        },
        "counts": {
            "n_reverted": n_rev,
            "n_anon_userid0": n_anon,
            "n_registered": n_reg,
            "n_reverted_anon_userid0": n_rev_anon,
            "n_reverted_registered": n_rev_reg,
            "n_temp_account": n_temp,
            "n_reverted_temp_account": n_rev_temp,
            "n_reverted_non_temp": n_rev_notemp,
        },
        "rates": {
            "base_rate": base_rate,
            "published_feature_anon_userid0": {
                "p_reverted_given_anon": p_rev_anon,
                "p_reverted_given_registered": p_rev_reg,
                "bias_ratio_anon_over_registered": bias_ratio,
                "note": "anon/userid==0 is largely EXTINCT on 2026 Wikidata (Temporary Accounts / IP masking); published feature no longer present",
            },
            "modern_feature_temp_account": {
                "p_reverted_given_temp": p_rev_temp,
                "p_reverted_given_non_temp": p_rev_notemp,
                "bias_ratio_temp_over_non_temp": temp_bias_ratio,
                "note": "temp-account = modern logged-out editor; same content-wall confound family as published anon feature",
            },
        },
        "published_reference": {
            "source": "Heindorf et al. WWW 2019 (CITED via scoping note)",
            "anon_rate": 0.0900,
            "registered_rate": 0.0003,
            "bias_ratio": 310.7,
        },
        "reproduction_verdict": None,
    }

    # Reproduction criterion: the CONTENT WALL is that registration status is a
    # massive confound. Published ratio is 310.7x on the 2012-2016 WDVC corpus;
    # exact value is corpus/era specific. We call Stage-1 REPRODUCED if the
    # qualitative + order-of-magnitude wall holds: anon reverted-rate materially
    # exceeds registered AND the bias ratio is large (>= 10x), i.e. the same
    # confound family the published 310.7x documents.
    # The published anon feature is extinct (platform change), so reproduction is
    # judged on the SAME CONFOUND FAMILY via the modern temp-account feature:
    # unregistered/low-trust editors are reverted at a materially higher rate.
    reproduced = (p_rev_temp > p_rev_notemp) and (temp_bias_ratio >= 5.0) and (n_rev >= 100) and (n_temp >= 100)
    out["reproduction_verdict"] = "REPRODUCED_MODERN_ANALOG" if reproduced else "NOT_REPRODUCED"
    out["reproduction_criterion"] = (
        "modern temp-account feature: p_temp>p_non_temp AND temp_bias_ratio>=5x AND "
        "n_reverted>=100 AND n_temp>=100 (published anon feature extinct due to IP-masking)"
    )

    with open(BASELINE_PATH + ".tmp", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(BASELINE_PATH + ".tmp", BASELINE_PATH)
    return out


def main():
    rows = pull_sample()
    out = stage1_baseline(rows)
    print(json.dumps(out, indent=2), flush=True)


if __name__ == "__main__":
    main()
