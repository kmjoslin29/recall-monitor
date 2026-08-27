"""
fetch_recalls.py  --  the updater / fetch engine
------------------------------------------------
Pulls US food recalls from the two official agencies, normalizes them into a
single schema, de-duplicates against what is already saved, and writes:

    data/recalls_master.csv
    data/recalls_master.json

Sources (both free, no key required; an FDA key just raises rate limits):
  * FDA  : openFDA Food Enforcement API   https://api.fda.gov/food/enforcement.json
           (FDA-regulated foods: produce, packaged goods, dairy, seafood, etc.)
  * USDA : FSIS Recall API                https://www.fsis.usda.gov/fsis/api/recall/v/1
           (meat, poultry, and egg products)

Uses only the Python standard library, so it runs on a clean Python 3.8+.
Region is DERIVED from where the product was distributed (per the design).

Typical use (Windows / PowerShell / CLI):
    python fetch_recalls.py                 # current year, both agencies
    python fetch_recalls.py --year 2026
    python fetch_recalls.py --since 2026-01-01
    python fetch_recalls.py --sample        # write labeled demo rows (no network)

Then rebuild the outputs:
    python build_workbook.py
    python build_dashboard.py
"""

import argparse
import csv
import datetime as dt
import gzip
import http.cookiejar
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import zlib

import reference_data as ref

# curl_cffi (optional) impersonates a real browser's TLS fingerprint, which is
# what USDA's Akamai bot protection checks. If it's installed we use it for the
# USDA endpoint; if not, we fall back to urllib and tell the user how to install
# it should USDA still return 403.
try:
    from curl_cffi import requests as _cffi
    _HAS_CURL = True
except Exception:
    _HAS_CURL = False

FDA_URL = "https://api.fda.gov/food/enforcement.json"
FSIS_URL = "https://www.fsis.usda.gov/fsis/api/recall/v/1"

# Order of columns in the master file. Everything downstream relies on this.
FIELDS = [
    "recall_id", "agency", "recall_number", "event_id",
    "firm", "firm_city", "firm_state",
    "product_description", "food_type",
    "reason", "hazard_category", "agent",
    "classification", "status",
    "distribution_pattern", "distribution_states", "regions", "nationwide",
    "quantity_raw", "quantity_value", "quantity_unit",
    "date_initiated", "date_reported", "date_closed", "days_open",
    "year", "month", "voluntary_mandated", "url",
    "source_fetched_at", "is_sample",
]

QTY_UNITS = (r"lb|lbs|pound|pounds|case|cases|unit|units|bottle|bottles|bag|bags|"
             r"box|boxes|carton|cartons|container|containers|jar|jars|package|"
             r"packages|can|cans|oz|ounce|ounces|kg|count|pouch|pouches|tray|trays")

# Control characters that are illegal in the .xlsx (XML 1.0) format. Stripping
# them here keeps the master clean for the workbook builder too.
ILLEGAL_XML_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


# USDA's server (behind Akamai) rejects non-browser requests. We send a full
# set of browser-like headers; FSIS-specific ones are added in fetch_fsis.
BROWSER_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}

# Shared cookie jar / opener so cookies from a priming request ride along on
# the following API request.
_OPENER = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def _read_body(resp):
    data = resp.read()
    enc = (resp.headers.get("Content-Encoding") or "").lower()
    if enc == "gzip":
        data = gzip.decompress(data)
    elif enc == "deflate":
        data = zlib.decompress(data)
    return data.decode("utf-8", "replace")


def _http_get(url, timeout=45, extra_headers=None):
    headers = dict(BROWSER_HEADERS)
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    with _OPENER.open(req, timeout=timeout) as resp:
        return json.loads(_read_body(resp))


def _curl_get(url, timeout=45):
    """Fetch via curl_cffi impersonating Chrome (browser TLS fingerprint)."""
    r = _cffi.get(url, impersonate="chrome", timeout=timeout)
    r.raise_for_status()
    return r.json()


def _iso(yyyymmdd):
    """Normalize FDA 'YYYYMMDD' or ISO-ish strings to 'YYYY-MM-DD' (or '')."""
    if not yyyymmdd:
        return ""
    s = str(yyyymmdd).strip()
    if re.fullmatch(r"\d{8}", s):
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    return m.group(0) if m else ""


def _days_between(a, b):
    try:
        da = dt.date.fromisoformat(a)
        db = dt.date.fromisoformat(b)
        return (db - da).days
    except Exception:
        return ""


def parse_quantity(*texts):
    """Best-effort numeric quantity + unit from free text.
    FDA/USDA quantities are unstructured, so this is deliberately conservative:
    it returns the first 'number + known unit' it finds, and leaves the rest
    to the raw text. Returns (value_str, unit_str)."""
    for text in texts:
        if not text:
            continue
        m = re.search(r"([\d][\d,\.]*)\s*(" + QTY_UNITS + r")\b", text, re.I)
        if m:
            val = m.group(1).replace(",", "")
            unit = m.group(2).lower()
            unit = {"lb": "lbs", "pound": "lbs", "pounds": "lbs"}.get(unit, unit)
            return val, unit
    return "", ""


def enrich(rec):
    """Fill derived fields shared by both agencies."""
    states, nationwide = ref.parse_states(rec.get("distribution_pattern", ""))
    rec["distribution_states"] = ", ".join(sorted(states))
    rec["nationwide"] = "Yes" if nationwide else "No"
    rec["regions"] = ", ".join(ref.regions_for(states, nationwide))
    rec["food_type"] = ref.categorize_food(rec.get("product_description", ""))
    cat, agent = ref.classify_hazard(rec.get("reason", ""))
    rec["hazard_category"] = cat
    rec["agent"] = agent
    di = rec.get("date_initiated", "")
    dc = rec.get("date_closed", "")
    ref_date = dc or dt.date.today().isoformat()
    rec["days_open"] = _days_between(di, ref_date) if di else ""
    basis = rec.get("date_reported") or rec.get("date_initiated") or ""
    if basis:
        rec["year"], rec["month"] = basis[:4], basis[5:7]
    else:
        rec["year"], rec["month"] = "", ""
    for f in FIELDS:
        rec.setdefault(f, "")
    for k, v in rec.items():                   # scrub XML-illegal control chars
        if isinstance(v, str) and ILLEGAL_XML_RE.search(v):
            rec[k] = ILLEGAL_XML_RE.sub(" ", v)
    return rec


# --------------------------------------------------------------------------- #
# FDA (openFDA food enforcement)
# --------------------------------------------------------------------------- #
def fetch_fda(year, api_key="", verbose=True):
    """Paginate openFDA for a calendar year. A single year of food recalls is
    well under openFDA's 25,000-skip ceiling, so skip-based paging is safe."""
    out, skip, limit = [], 0, 1000
    key_q = f"&api_key={api_key}" if api_key else ""
    while True:
        q = (f"?search=report_date:[{year}0101+TO+{year}1231]"
             f"&limit={limit}&skip={skip}{key_q}")
        try:
            data = _http_get(FDA_URL + q)
        except urllib.error.HTTPError as e:
            if e.code == 404:      # openFDA returns 404 when a page is empty
                break
            raise
        results = data.get("results", [])
        if not results:
            break
        for r in results:
            out.append(_norm_fda(r))
        if verbose:
            print(f"  FDA: fetched {len(out)} records...", file=sys.stderr)
        skip += len(results)
        if len(results) < limit or skip >= 25000:
            break
    return out


def _norm_fda(r):
    rec = {
        "agency": "FDA",
        "recall_number": r.get("recall_number", ""),
        "event_id": r.get("event_id", ""),
        "firm": r.get("recalling_firm", ""),
        "firm_city": r.get("city", ""),
        "firm_state": r.get("state", ""),
        "product_description": (r.get("product_description", "") or "")[:500],
        "reason": r.get("reason_for_recall", ""),
        "classification": r.get("classification", ""),
        "status": r.get("status", ""),
        "distribution_pattern": r.get("distribution_pattern", ""),
        "quantity_raw": r.get("product_quantity", ""),
        "date_initiated": _iso(r.get("recall_initiation_date", "")),
        "date_reported": _iso(r.get("report_date", "")),
        "date_closed": _iso(r.get("termination_date", "")),
        "voluntary_mandated": r.get("voluntary_mandated", ""),
        "url": ("https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts"),
        "source_fetched_at": dt.datetime.now().isoformat(timespec="seconds"),
        "is_sample": "No",
    }
    rec["recall_id"] = f"FDA:{rec['recall_number']}" if rec["recall_number"] else \
                       f"FDA:{rec['event_id']}:{rec['product_description'][:20]}"
    v, u = parse_quantity(rec["quantity_raw"])
    rec["quantity_value"], rec["quantity_unit"] = v, u
    return enrich(rec)


# --------------------------------------------------------------------------- #
# USDA FSIS
# --------------------------------------------------------------------------- #
def _fsis_fetch_raw(timeout=45):
    """Get the raw FSIS array, working around Akamai bot protection.

    Strategy: if curl_cffi is installed, use it (it presents a real browser TLS
    fingerprint, which is what the block checks). Otherwise, prime cookies by
    loading the recalls page, then request the API with full browser headers.
    """
    if _HAS_CURL:
        return _curl_get(FSIS_URL, timeout=timeout)
    # No curl_cffi: best-effort urllib. Prime the Akamai cookie first.
    try:
        prime = urllib.request.Request(
            "https://www.fsis.usda.gov/recalls",
            headers={**BROWSER_HEADERS,
                     "Accept": "text/html,application/xhtml+xml,application/xml;"
                               "q=0.9,*/*;q=0.8",
                     "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate",
                     "Sec-Fetch-Dest": "document",
                     "Upgrade-Insecure-Requests": "1"})
        with _OPENER.open(prime, timeout=timeout) as r:
            r.read()
    except Exception:
        pass  # priming is best-effort
    return _http_get(FSIS_URL, timeout=timeout, extra_headers={
        "Referer": "https://www.fsis.usda.gov/recalls",
        "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"})


def fetch_fsis(year, verbose=True):
    """FSIS returns an array; filter to the target year via the recall number
    suffix (e.g. '017-2026') or field_year."""
    try:
        data = _fsis_fetch_raw()
    except Exception as e:
        code = getattr(e, "code", None)
        is_403 = code == 403 or "403" in str(e)
        if is_403 and not _HAS_CURL:
            print("  USDA: blocked with 403. This endpoint sits behind bot "
                  "protection that\n         checks the TLS fingerprint, so a "
                  "browser User-Agent alone isn't enough.\n"
                  "         Fix (one time):   pip install curl_cffi\n"
                  "         then re-run this fetch. FDA data is unaffected.",
                  file=sys.stderr)
        else:
            print(f"  USDA: fetch failed ({e})", file=sys.stderr)
        return []
    if isinstance(data, dict) and "results" in data:
        data = data["results"]
    out = []
    for r in data or []:
        num = str(r.get("field_recall_number", "")).strip()
        yr = str(r.get("field_year", "")).strip()
        num_year = num.split("-")[-1] if "-" in num else ""
        if str(year) not in (yr, num_year):
            continue
        out.append(_norm_fsis(r))
    if verbose:
        src = "curl_cffi" if _HAS_CURL else "urllib"
        print(f"  USDA: fetched {len(out)} records for {year} (via {src})",
              file=sys.stderr)
    return out


def _clean(s):
    if not s:
        return ""
    return re.sub(r"\s+", " ", str(s).replace("\u2022", " ").replace("\t", " ")).strip()


def _fsis_class(risk):
    """'High - Class I' -> 'Class I'; keep 'Public Health Alert'."""
    if not risk:
        return ""
    m = re.search(r"Class\s+I{1,3}", risk)
    if m:
        return m.group(0)
    if "alert" in risk.lower():
        return "Public Health Alert (USDA)"
    return risk


def _norm_fsis(r):
    reason = _clean(r.get("field_recall_reason", "") or r.get("field_summary", ""))
    prod = _clean(r.get("field_product_items", "") or r.get("field_title", ""))
    states = _clean(r.get("field_states", ""))
    active = str(r.get("field_active_notice", "")).lower() in ("true", "1", "yes")
    num = str(r.get("field_recall_number", "")).strip()
    rec = {
        "agency": "USDA-FSIS",
        "recall_number": num,
        "event_id": "",
        "firm": _clean(r.get("field_establishment", "")),
        "firm_city": "",
        "firm_state": "",
        "product_description": prod[:500],
        "reason": reason,
        "classification": _fsis_class(r.get("field_risk_level", "")),
        "status": "Active" if active else "Closed",
        "distribution_pattern": states,
        "quantity_raw": "",
        "date_initiated": _iso(r.get("field_recall_date", "")
                               or r.get("field_last_modified_date", "")),
        "date_reported": _iso(r.get("field_recall_date", "")
                              or r.get("field_last_modified_date", "")),
        "date_closed": _iso(r.get("field_closed_date", "")),
        "voluntary_mandated": "",
        "url": "https://www.fsis.usda.gov/recalls",
        "source_fetched_at": dt.datetime.now().isoformat(timespec="seconds"),
        "is_sample": "No",
    }
    rec["recall_id"] = f"USDA:{num}" if num else f"USDA:{prod[:24]}"
    v, u = parse_quantity(r.get("field_summary", ""), prod, r.get("field_title", ""))
    rec["quantity_value"], rec["quantity_unit"] = v, u
    rec["quantity_raw"] = _clean(r.get("field_summary", ""))[:300]
    return enrich(rec)


# --------------------------------------------------------------------------- #
# Sample data (clearly labeled, structurally realistic, illustrative only)
# --------------------------------------------------------------------------- #
def sample_records(year):
    """Illustrative rows so the workbook/dashboard render before a live pull.
    Firm names are generic placeholders; these are NOT real recall records.
    Every row is flagged is_sample = Yes."""
    raw = [
        # firm, city, state, agency, class, product, reason, dist, init, closed, qty
        ("Northvale Dairy Co. (SAMPLE)", "Rochester", "NY", "FDA", "Class I",
         "Soft-ripened cheese, 8 oz rounds", "Possible Listeria monocytogenes contamination",
         "CT, MA, NY, NJ, PA", f"{year}-01-14", f"{year}-03-02", "3,200 units"),
        ("Cascade Produce LLC (SAMPLE)", "Salinas", "CA", "FDA", "Class I",
         "Bagged chopped romaine lettuce", "E. coli O157:H7 contamination",
         "Nationwide", f"{year}-02-03", "", "18,000 cases"),
        ("Gulfline Seafood (SAMPLE)", "Biloxi", "MS", "FDA", "Class II",
         "Frozen cooked shrimp", "Undeclared sulfites",
         "AL, FL, GA, LA, MS, TX", f"{year}-02-20", f"{year}-04-10", "5,400 bags"),
        ("Sunbelt Snack Foods (SAMPLE)", "Austin", "TX", "FDA", "Class II",
         "Chocolate granola bars", "Undeclared peanut",
         "Nationwide", f"{year}-03-11", "", "42,000 units"),
        ("Great Lakes Bakery (SAMPLE)", "Milwaukee", "WI", "FDA", "Class III",
         "Whole wheat sandwich bread", "Mislabeled net weight",
         "IL, IN, MI, OH, WI", f"{year}-03-28", f"{year}-05-01", "9,000 units"),
        ("Cornerstone Foods (SAMPLE)", "Fresno", "CA", "FDA", "Class I",
         "Frozen diced onions", "Possible Salmonella contamination",
         "AZ, CA, NV, OR, WA", f"{year}-04-09", "", "22,500 cases"),
        ("Little Sprout Nutrition (SAMPLE)", "Columbus", "OH", "FDA", "Class I",
         "Powdered infant formula", "Possible Cronobacter sakazakii",
         "Nationwide", f"{year}-04-22", f"{year}-06-30", "60,000 containers"),
        ("Harbor Provisions (SAMPLE)", "Portland", "ME", "FDA", "Class II",
         "Smoked salmon fillets", "Possible Listeria monocytogenes",
         "CT, MA, ME, NH, NY, RI, VT", f"{year}-05-06", "", "3,800 packages"),
        ("Prairie Harvest Mills (SAMPLE)", "Wichita", "KS", "FDA", "Class II",
         "All-purpose flour, 5 lb", "Possible E. coli contamination",
         "Nationwide", f"{year}-05-19", f"{year}-07-15", "31,000 bags"),
        ("Rio Grande Peppers (SAMPLE)", "El Paso", "TX", "FDA", "Class I",
         "Fresh jalapeno peppers", "Possible Salmonella contamination",
         "AZ, NM, OK, TX", f"{year}-06-02", "", "14,000 cases"),
        # USDA-FSIS
        ("Summit Meat Packing (SAMPLE)", "Greeley", "CO", "USDA-FSIS", "Class I",
         "Ready-to-eat beef franks", "Possible Listeria monocytogenes contamination",
         "Colorado, Kansas, Nebraska, Wyoming", f"{year}-01-27", f"{year}-03-18",
         "approximately 24,000 pounds"),
        ("Heritage Poultry Co. (SAMPLE)", "Springdale", "AR", "USDA-FSIS", "Class I",
         "Frozen breaded chicken patties", "Possible Salmonella contamination",
         "Arkansas, Missouri, Oklahoma, Texas", f"{year}-02-14", "",
         "approximately 68,000 pounds"),
        ("Cedar Valley Foods (SAMPLE)", "Cedar Rapids", "IA", "USDA-FSIS", "Class II",
         "Ready-to-eat chicken salad wraps", "Misbranding and undeclared egg",
         "Illinois, Iowa, Minnesota, Wisconsin", f"{year}-03-20", f"{year}-04-30",
         "approximately 7,200 pounds"),
        ("Coastal Cured Meats (SAMPLE)", "Richmond", "VA", "USDA-FSIS", "Class I",
         "Sliced deli ham", "Produced without benefit of inspection",
         "Maryland, North Carolina, Virginia", f"{year}-04-15", "",
         "approximately 1,900 pounds"),
        ("Mountain State Sausage (SAMPLE)", "Charleston", "WV", "USDA-FSIS", "Class II",
         "Pork breakfast sausage", "Possible foreign matter contamination (plastic)",
         "Kentucky, Ohio, Virginia, West Virginia", f"{year}-05-28", f"{year}-06-25",
         "approximately 12,500 pounds"),
        ("Valley Fresh Eggs (SAMPLE)", "Modesto", "CA", "USDA-FSIS",
         "Public Health Alert (USDA)",
         "Hard-cooked egg products", "Possible Listeria monocytogenes contamination",
         "California, Nevada, Oregon", f"{year}-06-11", "",
         "quantity not estimated"),
    ]
    out = []
    for (firm, city, st, agency, cls, prod, reason, dist, init, closed, qty) in raw:
        rec = {
            "agency": agency,
            "recall_number": f"SAMPLE-{len(out)+1:03d}-{year}",
            "event_id": "",
            "firm": firm, "firm_city": city, "firm_state": st,
            "product_description": prod, "reason": reason,
            "classification": cls,
            "status": "Terminated" if closed else "Ongoing",
            "distribution_pattern": dist,
            "quantity_raw": qty,
            "date_initiated": init, "date_reported": init, "date_closed": closed,
            "voluntary_mandated": "Voluntary: Firm Initiated" if agency == "FDA" else "",
            "url": "", "source_fetched_at": "SAMPLE", "is_sample": "Yes",
        }
        rec["recall_id"] = f"{agency}:{rec['recall_number']}"
        v, u = parse_quantity(qty)
        rec["quantity_value"], rec["quantity_unit"] = v, u
        out.append(enrich(rec))
    return out


# --------------------------------------------------------------------------- #
# Master read / merge / write
# --------------------------------------------------------------------------- #
def load_master(path):
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {row["recall_id"]: row for row in csv.DictReader(f)}


def write_master(records, data_dir):
    os.makedirs(data_dir, exist_ok=True)
    rows = sorted(records.values(),
                  key=lambda r: (r.get("date_reported", ""), r.get("recall_id", "")),
                  reverse=True)
    csv_path = os.path.join(data_dir, "recalls_master.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    json_path = os.path.join(data_dir, "recalls_master.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)
    return csv_path, json_path, len(rows)


def main():
    ap = argparse.ArgumentParser(description="Fetch & normalize US food recalls.")
    ap.add_argument("--year", type=int, default=dt.date.today().year)
    ap.add_argument("--since", help="ISO date; keep only recalls reported on/after")
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--fda-only", action="store_true")
    ap.add_argument("--usda-only", action="store_true")
    ap.add_argument("--sample", action="store_true",
                    help="Write labeled demo rows instead of fetching (offline).")
    ap.add_argument("--replace", action="store_true",
                    help="Replace the master instead of merging into it.")
    ap.add_argument("--api-key", default=os.environ.get("FDA_API_KEY", ""))
    args = ap.parse_args()

    csv_path = os.path.join(args.data_dir, "recalls_master.csv")
    master = {} if args.replace else load_master(csv_path)

    new = []
    if args.sample:
        print("Writing labeled SAMPLE data (no network).", file=sys.stderr)
        new = sample_records(args.year)
    else:
        if not args.usda_only:
            print(f"Fetching FDA food recalls for {args.year}...", file=sys.stderr)
            try:
                new += fetch_fda(args.year, args.api_key)
            except Exception as e:
                print(f"  FDA fetch error: {e}", file=sys.stderr)
        if not args.fda_only:
            print(f"Fetching USDA FSIS recalls for {args.year}...", file=sys.stderr)
            try:
                new += fetch_fsis(args.year)
            except Exception as e:
                print(f"  USDA fetch error: {e}", file=sys.stderr)

    if not new and not master:
        print("\nNo records fetched (network may be blocked) and no existing "
              "master. Writing SAMPLE data so you can preview the tool.\n"
              "Re-run without --sample once you have API access.", file=sys.stderr)
        new = sample_records(args.year)

    if args.since:
        new = [r for r in new if r.get("date_reported", "") >= args.since]

    added = 0
    for r in new:
        if r["recall_id"] not in master:
            added += 1
        master[r["recall_id"]] = r        # newest fetch wins (updates status)

    cpath, jpath, total = write_master(master, args.data_dir)
    print(f"\nDone. {added} new, {total} total records.")
    print(f"  {cpath}\n  {jpath}")
    print("Next:  python build_workbook.py   &&   python build_dashboard.py")


if __name__ == "__main__":
    main()
