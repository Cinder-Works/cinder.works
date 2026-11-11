#!/usr/bin/env python3
"""Badwater Market price refresher, run by GitHub Actions.

Fetches the AHledger price table for PvP Alliance US
(forever.pvp.alliance.us) with NO API key — the pricetable endpoint is
public, unauthenticated requests are allowed, and at one call per run
(12/hour at a 5-minute cadence) it is far under both the current 300/min
limit and the Dec 10 2026 cap of 60 pricetable downloads/hour.

Usage (from the repo root, as the workflow does):
    python3 wow/update.py

What it does:
  1. GET https://api.ahledger.com/v1/pricetable/forever.pvp.alliance.us
     (plain text: header AHL1|market|unix|count, rows
     item:median:min:qty:median7d:median30d:low30d:high30d:salesPerDay*10)
  2. Compares the table asOf to the asOf baked into wow/index.html.
  3. NO_NEW_SCAN: exits 0, changes nothing.
  4. NEW_SCAN: updates only the latest price fields per item in the
     page's market-data JSON (p=median, lo=minBuyout, qty=quantity,
     t=asOf) plus the page asOf/built/scanDay, and updates the visible
     note. The 7-day price series, forecasts and Sell/Buy/Craft calls
     are left untouched — they are still from the Nov 10 snapshot.

Scans arrive roughly every 1-2 hours, not every 5 minutes, so most runs
are no-ops. No key, token or secret appears in this file.
"""

import datetime
import json
import re
import sys
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX = REPO_ROOT / "wow" / "index.html"
MARKET = "forever.pvp.alliance.us"
URL = f"https://api.ahledger.com/v1/pricetable/{MARKET}"
PHOENIX = ZoneInfo("America/Phoenix")
SNAPSHOT_LABEL = "Nov 10 snapshot"

MARKET_DATA_RE = re.compile(
    r'(<script id="market-data" type="application/json">)(.*?)(</script>)',
    re.S,
)
STALE_NOTE_RE = re.compile(r'(<p class="stale-note" id="stale-note" hidden></p>)')
LIVE_NOTE_RE = re.compile(r'<p class="live-note" id="live-note">.*?</p>', re.S)
LIVE_NOTE_CSS = (
    ".live-note { flex-basis: 100%; margin: 0; padding: 0.6rem 0.9rem; "
    "border-radius: 4px; background: rgba(255, 209, 0, 0.10); "
    "border: 1px solid rgba(255, 209, 0, 0.4); }"
)


def fmt_mst(unix):
    return datetime.datetime.fromtimestamp(unix, PHOENIX).strftime(
        "%b %-d, %-I:%M %p MST"
    )


def fetch_pricetable():
    req = urllib.request.Request(URL, headers={"User-Agent": "cinder.works-badwater-refresh"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        text = resp.read().decode("utf-8")
    lines = text.strip().splitlines()
    header = lines[0].split("|")
    as_of = int(header[2])
    items = {}
    for line in lines[1:]:
        parts = line.split(":")
        if len(parts) < 9:
            continue
        item_id = parts[0]
        num = lambda s: int(s) if s else None  # noqa: E731
        items[item_id] = {
            "median": num(parts[1]),
            "minBuyout": num(parts[2]),
            "quantity": num(parts[3]),
            "median7d": num(parts[4]),
            "median30d": num(parts[5]),
            "low30d": num(parts[6]),
            "high30d": num(parts[7]),
            "salesPerDay": (int(parts[8]) / 10) if parts[8] else None,
        }
    return {"market": MARKET, "asOf": as_of, "count": int(header[3]), "items": items}


def main():
    now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    table = fetch_pricetable()
    as_of = table["asOf"]
    table_items = table["items"]

    html = INDEX.read_text()
    match = MARKET_DATA_RE.search(html)
    if not match:
        print("market-data JSON block not found in wow/index.html", file=sys.stderr)
        sys.exit(1)
    data = json.loads(match.group(2))
    previous_asof = data["asOf"]
    items = data["items"]

    new_scan = as_of != previous_asof
    changed = 0
    unchanged = 0
    missing = 0
    movers = []
    for item_id, row in items.items():
        latest = table_items.get(item_id)
        if latest is None or latest.get("median") is None:
            missing += 1
            continue
        old = row.get("p")
        new = latest["median"]
        if old is not None and old != new:
            changed += 1
            movers.append({
                "id": int(item_id),
                "name": row.get("n"),
                "oldMedian": old,
                "newMedian": new,
                "pctChange": round((new - old) / old * 100, 1) if old else None,
            })
        else:
            unchanged += 1
    movers.sort(key=lambda m: abs(m["pctChange"] or 0), reverse=True)

    summary = {
        "status": "NEW_SCAN" if new_scan else "NO_NEW_SCAN",
        "market": MARKET,
        "asOf": as_of,
        "asOfMST": fmt_mst(as_of),
        "previousAsOf": previous_asof,
        "previousAsOfMST": fmt_mst(previous_asof),
        "itemsInTable": table["count"],
        "itemsOnPage": len(items),
        "itemsChanged": changed,
        "itemsUnchanged": unchanged,
        "itemsMissingFromTable": missing,
        "topMovers": movers[:3],
        "rebuilt": False,
    }

    if not new_scan:
        print(json.dumps(summary, indent=2))
        return

    for item_id, row in items.items():
        latest = table_items.get(item_id)
        if latest is None or latest.get("median") is None:
            continue
        row["p"] = latest["median"]
        if latest.get("minBuyout") is not None:
            row["lo"] = latest["minBuyout"]
        if latest.get("quantity") is not None:
            row["qty"] = latest["quantity"]
        row["t"] = as_of
    data["asOf"] = as_of
    data["built"] = now
    data["scanDay"] = datetime.datetime.fromtimestamp(as_of, PHOENIX).strftime("%Y-%m-%d")

    new_json = json.dumps(data, separators=(",", ":"))
    new_html = MARKET_DATA_RE.sub(
        lambda m: m.group(1) + new_json + m.group(3), html, count=1
    )

    note = (
        "Latest prices updated from the %s scan. "
        "Sell / Buy / Craft calls are still from the %s."
        % (fmt_mst(as_of), SNAPSHOT_LABEL)
    )
    note_tag = '<p class="live-note" id="live-note">%s</p>' % note
    if LIVE_NOTE_RE.search(new_html):
        new_html = LIVE_NOTE_RE.sub(lambda m: note_tag, new_html, count=1)
    else:
        new_html = STALE_NOTE_RE.sub(
            lambda m: m.group(1) + "\n    " + note_tag, new_html, count=1
        )
    if ".live-note {" not in new_html:
        new_html = new_html.replace(
            ".stale-note { flex-basis: 100%; margin: 0; padding: 0.6rem 0.9rem; "
            "border-radius: 4px; background: rgba(255, 122, 107, 0.12); "
            "border: 1px solid rgba(255, 122, 107, 0.4); }",
            ".stale-note { flex-basis: 100%; margin: 0; padding: 0.6rem 0.9rem; "
            "border-radius: 4px; background: rgba(255, 122, 107, 0.12); "
            "border: 1px solid rgba(255, 122, 107, 0.4); }\n"
            + LIVE_NOTE_CSS,
            1,
        )

    INDEX.write_text(new_html)
    summary["rebuilt"] = True
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
