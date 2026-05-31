# Daphnet Freezing of Gait Dataset

External dataset, downloaded 2026-05-31 for CS 8674 Part II Deliverable 1 (FOG baseline track, syllabus Week 3).

## Source

- UCI ML Repository: https://archive.ics.uci.edu/dataset/245/daphnet+freezing+of+gait
- Direct download: https://archive.ics.uci.edu/static/public/245/daphnet+freezing+of+gait.zip
- Recorded 2008, Tel Aviv Sourasky Medical Center (Laboratory for Gait and Neurodynamics) in collaboration with ETH Zurich Wearable Computing Lab.
- EU FP6 project Daphnet, grant 018474-2.

## Citation (required by license)

Bächlin, M., Plotnik, M., Roggen, D., Maidan, I., Hausdorff, J. M., Giladi, N., & Tröster, G. (2010). Wearable assistant for Parkinson's disease patients with the freezing of gait symptom. *IEEE Transactions on Information Technology in Biomedicine, 14*(2), 436–446. https://doi.org/10.1109/TITB.2009.2036165

(Lit-review entry #3.)

## Layout (after unzipping `daphnet+freezing+of+gait.zip`)

```
dataset_fog_release/
├── README                   # original UCI README
├── dataset/                 # 17 session files (space-separated .txt)
│   ├── S01R01.txt           # subject 01, run 01
│   ├── S01R02.txt
│   ├── S02R01.txt
│   └── ...                  # through S10R01.txt
├── doc/                     # PDF of the Bächlin 2010 paper + protocol notes
└── scripts/                 # MATLAB helper scripts (not used here)
```

- 10 PD patients, 17 recording sessions
- ~86 MB unzipped, ~1.9M rows total

## File format

Each `SXXRYY.txt` is whitespace-separated, no header, 11 columns:

| Col | Field | Unit |
|---|---|---|
| 1 | Time | ms |
| 2–4 | Ankle accel x, y, z | mg |
| 5–7 | Thigh (upper leg) accel x, y, z | mg |
| 8–10 | Trunk (hip) accel x, y, z | mg |
| 11 | Annotation label | 0 = not part of experiment, 1 = no freeze, 2 = freeze |

Sampling rate: 64 Hz. Three MEMS triaxial accelerometers on shank, thigh, trunk.

## Quick load (Python)

```python
import pandas as pd
from pathlib import Path

cols = ['time_ms',
        'ankle_x', 'ankle_y', 'ankle_z',
        'thigh_x', 'thigh_y', 'thigh_z',
        'trunk_x', 'trunk_y', 'trunk_z',
        'label']

session_files = sorted(Path('data/daphnet/dataset_fog_release/dataset').glob('S*R*.txt'))
df = pd.concat(
    [pd.read_csv(f, sep=r'\s+', header=None, names=cols).assign(session=f.stem)
     for f in session_files],
    ignore_index=True,
)
# Drop label==0 (windows outside the experiment)
df = df[df['label'] != 0]
df['is_freeze'] = (df['label'] == 2).astype(int)
```

## Why this dataset

- Syllabus mandate: required corpus for the FOG track in D1 (Week 3 baselines) and D2 (Week 7 auxiliary input).
- Provides the canonical must-beat baseline (Bächlin 2010 freeze-band/locomotion-band threshold: ~73% sensitivity / ~82% specificity) — see [`part2-ml/next-steps.md`](../../part2-ml/next-steps.md) §4.1 and §4.4.
- Open access, no DUA, immediate.

## Gitignore policy

Raw session files and the paper PDF are not committed (86 MB; reproducible via UCI). Only this README is tracked. To restore the data locally:

```bash
cd data/daphnet
curl -sSL -o daphnet.zip "https://archive.ics.uci.edu/static/public/245/daphnet+freezing+of+gait.zip"
unzip -q daphnet.zip && rm daphnet.zip
```

Canonical long-term storage for cross-environment access is the AWS S3 bucket (per syllabus); upload happens in Week 2.
