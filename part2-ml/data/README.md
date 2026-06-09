# part2-ml/data — Deliverable 1 datasets

Canonical local home for the CS 8674 Part II datasets. The notebooks in
`../notebooks/` search this folder first (then `/kaggle/input`), so `part2-ml/` is
self-contained. **Only Part 2 ML datasets live here** — the Part 1 glove/flex data stays
at the repo root (`../../data/`).

## Layout (verified)

```
part2-ml/data/
├── alameda/
│   ├── ALAMEDA_PD_tremor_dataset.csv          # 4151 × 99, 11 subjects (md5 1e0b3bd…)
│   └── README.md                              # provenance, schema, restore cmd
├── daphnet/
│   ├── dataset_fog_release/dataset/S*R*.txt   # 17 sessions, 10 subjects, 64 Hz
│   └── README.md
├── ppmi/
│   ├── MDS-UPDRS_Part_III_08Jun2026.csv        # 38226 × 65, 5157 patients
│   ├── Demographics_08Jun2026.csv              # 8642 × 29
│   ├── Roche_PD_Monitoring_App_v2_data_08Jun2026.csv  # 108901 × 22, long-format, 32 pts
│   └── PPMI_Methods_Document_Roche_v1.1.pdf
└── glove/                                       # empty (Part 1 data intentionally excluded)
```

## Stage / verify

Paste a downloaded folder (or `.zip`) anywhere, then run the organizer — it unzips,
copies files into the layout above, and verifies counts against known-good values:

```bash
python scripts/organize_data.py /path/to/pasted_folder   # organize + verify
python scripts/organize_data.py --verify                 # verify current data/ only
```

Expected verification output:

```
ALAMEDA  shape=(4151, 99) subjects=11 -> OK
Daphnet  sessions=17 subjects=10 -> OK
PPMI     Part III=yes Roche=yes Demographics=yes
```

## Provenance & formats

- ALAMEDA — [`alameda/README.md`](alameda/README.md) (Zenodo, CC BY 4.0)
- Daphnet — [`daphnet/README.md`](daphnet/README.md) (UCI, Bächlin 2010)
- PPMI Part III / Demographics / Roche — LONI IDA (`ida.loni.usc.edu`); **DUA-restricted**.
  ⚠ Roche v2 is **CDISC/SDTM long format** (`PATNO`, `QRSTEST`, `QRSRESN`; **no `EVENT_ID`**,
  32 patients) — it cannot be joined on `EVENT_ID` as the syllabus assumes. See
  [`../docs/unified-feature-schema.md`](../docs/unified-feature-schema.md).
- Glove (Part 1) — `../../data/README.md`

## Git policy

Raw data is **gitignored** (large and/or DUA-restricted). Only the README files are
tracked (`part2-ml/data/**/README.md`). PPMI must never be committed or made public.
