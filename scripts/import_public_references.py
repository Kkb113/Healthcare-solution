"""Import public aggregate names and dated ICD files into a bounded reference package.

Raw public downloads stay under ignored data/. The selected, hashed aggregate
reference package is versioned; normal generation never needs network access.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
import urllib.error
import zipfile
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data/public-reference-cache"
DEST = ROOT / "references"


def retrieve(name, url):
    path = CACHE / name
    if not path.exists():
        request = urllib.request.Request(url, headers={"User-Agent": "HealthcareSyntheticReferenceImporter/1.0 (public aggregate research)"})
        with urllib.request.urlopen(request, timeout=60) as response:
            content = response.read(35_000_001)
        if len(content) > 35_000_000:
            raise ValueError("reference download exceeds 35 MB bound")
        path.write_bytes(content)
    content = path.read_bytes()
    return content, {"file": name, "url": url, "sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}


def discover():
    content, _ = retrieve("cms-code-downloads.html", "https://www.cms.gov/medicare/coding-billing/icd-10-codes")
    text = content.decode("utf-8")
    for link, label in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', text, re.S):
        label = re.sub("<[^>]+>", "", label)
        if any(str(year) in label for year in (2023, 2024, 2025, 2026)) and any(part in label.lower() for part in ("descriptions", "codes file", "order file")):
            print(label.strip(), urllib.parse.urljoin("https://www.cms.gov", link))


def names():
    sources = []
    counts = defaultdict(Counter)
    try:
        raw, provenance = retrieve("ssa-national-names.zip", "https://www.ssa.gov/oact/babynames/names.zip")
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            for year in range(1920, 2010):
                for name, sex, count in csv.reader(archive.read(f"yob{year}.txt").decode("utf-8").splitlines()):
                    counts[f"{year // 10 * 10}/{sex}"][name] += int(count)
    except urllib.error.HTTPError as exc:
        if exc.code != 403:
            raise
        # Explicitly disclosed public aggregate mirror, never an access-control bypass.
        revision, _ = retrieve("ssa-mirror-revision.json", "https://api.github.com/repos/hackerb9/ssa-baby-names/commits/HEAD")
        commit = json.loads(revision)["sha"]
        raw, provenance = retrieve("ssa-aggregate-mirror.txt", f"https://raw.githubusercontent.com/hackerb9/ssa-baby-names/{commit}/alldata.txt")
        provenance.update({"origin": "https://www.ssa.gov/oact/babynames/names.zip", "access_note": "Official ZIP returned HTTP 403; pinned public mirror of SSA aggregate data", "mirror_commit": commit})
        for name, sex, count, year in csv.reader(io.StringIO(raw.decode("utf-8"))):
            if 1920 <= int(year) < 2010:
                counts[f"{int(year) // 10 * 10}/{sex}"][name] += int(count)
    sources.append(provenance)
    # SSA aggregates contain registration labels as well as human names. Curate
    # those explicitly before weighting; public provenance alone is not realism.
    excluded_labels = {"unknown", "unnamed", "infant", "babyboy", "babygirl", "male", "female", "fnu", "lnu", "notnamed", "test", "patient"}
    removed = {key: {name: count for name, count in values.items() if name.casefold() in excluded_labels} for key, values in counts.items()}
    given = {key: [[name, count] for name, count in sorted(values.items(), key=lambda p: (-p[1], p[0])) if name.casefold() not in excluded_labels][:400] for key, values in sorted(counts.items())}
    raw, provenance = retrieve("census-surnames.zip", "https://www2.census.gov/topics/genealogy/2010surnames/names.zip")
    sources.append(provenance)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        member = next(n for n in archive.namelist() if n.lower().endswith(".csv"))
        rows = list(csv.DictReader(io.StringIO(archive.read(member).decode("utf-8-sig"))))
    # Broad enough to satisfy >=1,000 observed surnames without flattening weights.
    rows = [r for r in rows if r["name"] != "ALL OTHER NAMES"][:12000]
    def case_name(value):
        name = value.title()
        return "Mc" + name[2:].capitalize() if name.startswith("Mc") and len(name) > 2 else name
    surnames = [[case_name(r["name"]), int(r["count"])] for r in rows]
    columns = {"White, non-Hispanic": ["pctwhite"], "Black, non-Hispanic": ["pctblack"],
               "Hispanic or Latino": ["pcthispanic"], "Asian, non-Hispanic": ["pctapi"],
               "Multiracial or other": ["pctaian", "pct2prace"]}
    surname_profiles = {}
    for category, fields in columns.items():
        # Suppressed small cells receive a one-basis-point smoothing weight.
        surname_profiles[category] = [[case_name(r["name"]), int(r["count"]) * max(1, sum(int(Decimal(r[f]) * 100) if r[f] != "(S)" else 1 for f in fields))] for r in rows]
    result = {"version": "1.0.0", "source_scope": "Public aggregate counts only; no individual records or contacts",
              "cohort_selection": "Birth decades 1920-2009; top 400 per decade/SSA series, renormalized at draw time",
              "surname_selection": "Top 12000 Census 2010 surnames. Self-report is drawn first; aggregate category weights only guide probabilistic surname selection, never infer a person's race. Unknown uses marginal counts; 5% cross-population mixing is configured. Mc capitalization normalized.",
              "sources": sources, "excluded_given_name_registration_labels": removed,
              "given_names": given, "surnames": surnames, "surname_profiles": surname_profiles}
    DEST.mkdir(exist_ok=True)
    (DEST / "person-name-weights.json").write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"name_cohorts": len(given), "surname_weights": len(surnames), "source_hashes": sources}))


def code_downloads():
    from concurrent.futures import ThreadPoolExecutor
    jobs = {
        "cm-2023-oct.zip": "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2023/icd10-Order-CodeFiles2023.zip",
        "cm-2023-apr.zip": "https://www.cms.gov/files/zip/2023-code-descriptions-tabular-order-updated-01/11/2023.zip",
        "cm-2024-oct.zip": "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2024/icd10cm-CodesDescriptions-2024.zip",
        "cm-2024-apr.zip": "https://www.cms.gov/files/zip/2024-code-descriptions-tabular-order-updated-02/01/2024.zip",
        "cm-2025-oct.zip": "https://www.cms.gov/files/zip/2025-code-descriptions-tabular-order.zip",
        "cm-2025-apr.zip": "https://www.cms.gov/files/zip/2025-code-descriptions-tabular-order-april.zip",
        "cm-2026-oct.zip": "https://www.cms.gov/files/zip/2026-code-descriptions-tabular-order.zip",
        "pcs-2023-oct.zip": "https://www.cms.gov/files/zip/2023-icd-10-pcs-codes-file.zip",
        "pcs-2023-apr.zip": "https://www.cms.gov/files/zip/2023-icd-10-pcs-codes-file-updated-01/11/2023.zip",
        "pcs-2024-oct.zip": "https://www.cms.gov/files/zip/2024-icd-10-pcs-codes-file.zip",
        "pcs-2024-apr.zip": "https://www.cms.gov/files/zip/2024-icd-10-pcs-codes-file-updated-12/19/2023.zip",
        "pcs-2025-oct.zip": "https://www.cms.gov/files/zip/2025-icd-10-pcs-codes-file.zip",
        "pcs-2025-apr.zip": "https://www.cms.gov/files/zip/2025-icd-10-pcs-codes-file-april.zip",
        "pcs-2026-oct.zip": "https://www.cms.gov/files/zip/2026-icd-10-pcs-codes-file.zip",
    }
    def download(job):
        name, url = job
        try:
            raw, source = retrieve(name, url)
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                members = archive.namelist()
            return {**source, "members": members}
        except Exception as exc:
            return {"file": name, "url": url, "error": str(exc)}
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(download, jobs.items()))
    (CACHE / "download-inventory.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for row in results:
        print(json.dumps(row))


def codes():
    inventory = json.loads((CACHE / "download-inventory.json").read_text())
    if any("error" in item for item in inventory):
        raise ValueError("complete dated downloads before selecting codes")
    source_by_file = {r["file"]: r for r in inventory}
    values, excluded = {}, set()
    for name in source_by_file:
        with zipfile.ZipFile(CACHE / name) as archive:
            member = next(n for n in archive.namelist() if n.lower().endswith(".txt") and "codes" in n.lower() and "addenda" not in n.lower())
            values[name] = dict(line.split(None, 1) for line in archive.read(member).decode("utf-8-sig").splitlines() if line.strip())
            if name.startswith("pcs-") and ("2023" in name or "2024" in name):
                for item in archive.namelist():
                    if "addenda" in item and item.endswith(".txt"):
                        excluded.update(re.findall(r"(?:Add|Revise(?: from| to)?|Delete|Rev):\s+([A-Z0-9]{7})", archive.read(item).decode("utf-8-sig")))
    cm_files = [n for n in values if n.startswith("cm-")]
    pcs_files = [n for n in values if n.startswith("pcs-")]
    common_cm = set.intersection(*(set(values[n]) for n in cm_files))
    common_pcs = set.intersection(*(set(values[n]) for n in pcs_files)) - excluded
    prefixes = ["I10", "I11", "I12", "I13", "I20", "I21", "I25", "I48", "I50", "J18", "J44", "J45", "E11", "E78", "N18", "N39", "K35", "K40", "K80", "M16", "M17", "D64", "G47", "R06", "R07", "R10", "R50", "Z79", "Z87"]
    required = ["I10", "I509", "J449", "E119", "N189", "E785", "J189", "M1711", "K4090"]
    selected_cm = list(required)
    groups = [[c for c in sorted(common_cm) if c.startswith(prefix)] for prefix in prefixes]
    for rank in range(max(map(len, groups))):
        for group in groups:
            if rank < len(group) and group[rank] not in selected_cm:
                selected_cm.append(group[rank])
            if len(selected_cm) == 300:
                break
        if len(selected_cm) == 300:
            break
    pcs_prefixes = ("0FT4", "0DTJ", "0WQF", "0WQG", "0SR9", "0SRB", "0SRC", "0SRD", "0BH1", "5A09")
    selected_pcs = []
    pcs_groups = [[c for c in sorted(common_pcs) if c.startswith(prefix) and "Greater than 96" not in values[pcs_files[0]][c]] for prefix in pcs_prefixes]
    for rank in range(max(map(len, pcs_groups))):
        for group in pcs_groups:
            if rank < len(group) and group[rank] not in selected_pcs:
                selected_pcs.append(group[rank])
            if len(selected_pcs) == 100:
                break
        if len(selected_pcs) == 100:
            break
    if len(selected_cm) != 300 or not set(selected_cm) <= common_cm or len(selected_pcs) != 100:
        raise ValueError(f"selection insufficient: CM={len(selected_cm)}, PCS={len(selected_pcs)}")
    periods = [(2023, "oct", "2022-10-01", "2023-04-01"), (2023, "apr", "2023-04-01", "2023-10-01"),
               (2024, "oct", "2023-10-01", "2024-04-01"), (2024, "apr", "2024-04-01", "2024-10-01"),
               (2025, "oct", "2024-10-01", "2025-04-01"), (2025, "apr", "2025-04-01", "2025-10-01"),
               (2026, "oct", "2025-10-01", "2026-04-01")]
    rows = []
    for year, part, start, end in periods:
        for family, selected, domain, system in (("cm", selected_cm, "DIAGNOSIS", "ICD-10-CM"), ("pcs", selected_pcs, "PROCEDURE", "ICD-10-PCS")):
            name = f"{family}-{year}-{part}.zip"
            for code in selected:
                rows.append({"domain": domain, "code_system": system, "code": code, "version": f"FY{year}-{part.upper()}",
                             "display": values[name][code], "valid_from": start, "valid_to": end, "source_file": name})
    result = {"version": "1.0.0", "sources": inventory,
              "policy": "300 CM and 100 PCS stable adult-scope codes in all seven applicable releases. Annual PCS 2023/24 files now alias updated files; exclude all touched addendum codes before using the unchanged subset in the earlier interval. No changed/new April code is backdated.",
              "excluded_midyear_touched_pcs_codes": sorted(excluded), "rows": rows}
    DEST.mkdir(exist_ok=True)
    (DEST / "clinical-code-releases.json").write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"code_rows": len(rows), "cm_codes": len(selected_cm), "pcs_codes": len(selected_pcs)}))


def lock_package():
    paths = ["person-name-weights.json", "clinical-code-releases.json", "hospital-reference-catalog.json"]
    lock = {"version": "1.0.0", "policy": "Reviewed public aggregates, historical official code subsets and explicit local references; no runtime network access.",
            "files": {"references/" + name: {"sha256": hashlib.sha256((DEST / name).read_bytes()).hexdigest(), "bytes": (DEST / name).stat().st_size} for name in paths}}
    (ROOT / "contracts/reference-package-lock.json").write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--names", action="store_true")
    parser.add_argument("--discover-codes", action="store_true")
    parser.add_argument("--download-codes", action="store_true")
    parser.add_argument("--codes", action="store_true")
    parser.add_argument("--lock", action="store_true", help="Explicitly refresh reviewed reference checksums")
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    if args.names:
        names()
    if args.discover_codes:
        discover()
    if args.download_codes:
        code_downloads()
    if args.codes:
        codes()
    if args.lock:
        lock_package()


if __name__ == "__main__":
    main()
