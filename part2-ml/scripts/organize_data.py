#!/usr/bin/env python3
"""Verify, unzip, and organize a pasted data folder into part2-ml/data/.

Usage:
    python scripts/organize_data.py <source>      # source = pasted folder or .zip
    python scripts/organize_data.py --verify      # just verify the current data/ layout

It auto-detects each D1 dataset by signature filenames anywhere under <source>
(recursively), unzips any .zip it finds, and copies files into the canonical layout:

    part2-ml/data/
    ├── alameda/ALAMEDA_PD_tremor_dataset.csv
    ├── daphnet/dataset_fog_release/dataset/S*R*.txt
    ├── ppmi/   (MDS-UPDRS Part III, Roche PD App v2, Demographics CSVs)
    └── glove/tremor_validation_master.csv

Then it verifies row/column counts against the known-good expectations so you can
confirm the paste matches the data already in the repo. Nothing is deleted from the
source; files are copied.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"

# Known-good expectations (from the data already verified in this repo).
EXPECT = {
    "alameda": {"rows": 4151, "cols": 99, "subjects": 11},  # 4152 lines incl. header
    "daphnet": {"sessions": 17, "subjects": 10, "cols": 11},
    "glove":   {"cols": 11},  # person_id..notes
}


def unzip_all(src: Path) -> None:
    """Recursively unzip any .zip under src, in place."""
    for z in list(src.rglob("*.zip")):
        target = z.with_suffix("")
        if target.exists():
            continue
        print(f"  unzip {z.name} -> {target.name}/")
        with zipfile.ZipFile(z) as zf:
            zf.extractall(target)


def find_one(src: Path, *patterns) -> Path | None:
    for pat in patterns:
        hits = sorted(src.rglob(pat))
        if hits:
            return hits[0]
    return None


def find_daphnet_dir(src: Path) -> Path | None:
    hits = [p.parent for p in src.rglob("S*R*.txt") if re.match(r"S\d+R\d+\.txt$", p.name)]
    return sorted(set(hits))[0] if hits else None


def copy_into(srcfile: Path, dstdir: Path) -> None:
    dstdir.mkdir(parents=True, exist_ok=True)
    dst = dstdir / srcfile.name
    if dst.resolve() == srcfile.resolve():
        return
    shutil.copy2(srcfile, dst)
    print(f"  -> {dst.relative_to(DATA.parent)}")


def organize(source: Path) -> None:
    print(f"Organizing from: {source}")
    if source.is_file() and source.suffix == ".zip":
        # unzip the top-level zip into a temp sibling then treat that as source
        tmp = source.with_suffix("")
        with zipfile.ZipFile(source) as zf:
            zf.extractall(tmp)
        source = tmp
    unzip_all(source)

    # ALAMEDA
    a = find_one(source, "ALAMEDA_PD_tremor_dataset.csv", "*ALAMEDA*tremor*.csv")
    if a:
        print("ALAMEDA found:", a.name); copy_into(a, DATA / "alameda")
    else:
        print("ALAMEDA: not found in source")

    # Daphnet — copy the whole dataset_fog_release tree if present, else the .txt dir
    drel = next((p for p in source.rglob("dataset_fog_release") if p.is_dir()), None)
    if drel:
        dst = DATA / "daphnet" / "dataset_fog_release"
        if not dst.exists():
            shutil.copytree(drel, dst)
            print(f"  -> {dst.relative_to(DATA.parent)}/ (full tree)")
        else:
            print("  daphnet/dataset_fog_release already present")
    else:
        ddir = find_daphnet_dir(source)
        if ddir:
            dst = DATA / "daphnet" / "dataset_fog_release" / "dataset"
            dst.mkdir(parents=True, exist_ok=True)
            for f in ddir.glob("S*R*.txt"):
                copy_into(f, dst)
        else:
            print("Daphnet: not found in source")

    # PPMI — copy any of the three known tables
    for pat, nice in [
        ("*UPDRS*Part*III*.csv", "Part III"), ("*MDS_UPDRS_Part_III*.csv", "Part III"),
        ("*NUPDRS3*.csv", "Part III"), ("*Roche*.csv", "Roche"), ("*roche*.csv", "Roche"),
        ("Demographics.csv", "Demographics"), ("*Demographics*.csv", "Demographics"),
    ]:
        f = find_one(source, pat)
        if f:
            print(f"PPMI {nice} found:", f.name); copy_into(f, DATA / "ppmi")

    # Glove
    g = find_one(source, "tremor_validation_master.csv")
    if g:
        print("Glove found:", g.name); copy_into(g, DATA / "glove")


def verify() -> int:
    import pandas as pd
    problems = 0
    print("\n=== VERIFY part2-ml/data ===")

    a = DATA / "alameda" / "ALAMEDA_PD_tremor_dataset.csv"
    if a.exists():
        df = pd.read_csv(a)
        ok = (df.shape == (EXPECT["alameda"]["rows"], EXPECT["alameda"]["cols"])
              and df["subject_id"].nunique() == EXPECT["alameda"]["subjects"])
        print(f"ALAMEDA  shape={df.shape} subjects={df['subject_id'].nunique()} "
              f"-> {'OK' if ok else 'MISMATCH'} (expect 4151x99, 11 subj)")
        problems += not ok
    else:
        print("ALAMEDA  MISSING"); problems += 1

    dd = DATA / "daphnet" / "dataset_fog_release" / "dataset"
    if dd.exists():
        files = sorted(p for p in dd.glob("S*R*.txt") if re.match(r"S\d+R\d+\.txt$", p.name))
        subs = {f.name.split("R")[0] for f in files}
        ok = len(files) == EXPECT["daphnet"]["sessions"] and len(subs) == EXPECT["daphnet"]["subjects"]
        print(f"Daphnet  sessions={len(files)} subjects={len(subs)} "
              f"-> {'OK' if ok else 'CHECK'} (expect 17 sessions, 10 subj)")
        problems += not ok
    else:
        print("Daphnet  MISSING"); problems += 1

    pp = DATA / "ppmi"
    p3 = sorted({*pp.glob("*Part_III*.csv"), *pp.glob("*UPDRS*III*.csv"),
                 *pp.glob("*NUPDRS3*.csv")}) if pp.exists() else []
    roche = sorted(f for f in pp.glob("*oche*.csv")) if pp.exists() else []
    demo = sorted(pp.glob("*emographics*.csv")) if pp.exists() else []
    print(f"PPMI     Part III={'yes' if p3 else 'NO'} "
          f"Roche={'yes' if roche else 'NO'} Demographics={'yes' if demo else 'NO'}")
    for f in dict.fromkeys(p3 + roche + demo):  # dedupe, preserve order
        df = pd.read_csv(f, nrows=5)
        note = " (long-format, no EVENT_ID — joins on PATNO only)" if f in roche else ""
        print(f"   {f.name}: {len(df.columns)} cols{note}")

    g = DATA / "glove" / "tremor_validation_master.csv"
    print(f"Glove    {'OK' if g.exists() else 'MISSING (optional)'}")

    print("=== VERIFY DONE ===")
    return problems


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", help="pasted data folder or .zip")
    ap.add_argument("--verify", action="store_true", help="verify current data/ only")
    args = ap.parse_args()
    if args.source:
        src = Path(args.source).expanduser().resolve()
        if not src.exists():
            sys.exit(f"source not found: {src}")
        organize(src)
    verify()
