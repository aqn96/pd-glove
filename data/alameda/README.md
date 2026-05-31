# ALAMEDA PD Tremor Dataset

External dataset, downloaded 2026-05-31 for CS 8674 Part II Deliverable 1 (tremor/bradykinesia track, syllabus Week 2 feature alignment).

## Source

- Zenodo DOI: https://doi.org/10.5281/zenodo.10782573
- Direct file: https://zenodo.org/api/records/10782573/files/ALAMEDA_PD_tremor_dataset.csv/content
- License: CC BY 4.0
- Title: *Parkinson's Disease Tremor Dataset - ALAMEDA*

## Citation

ALAMEDA (Bridging the Early Diagnosis and Treatment Gap of Brain Diseases via Smart, Connected, Proactive and Evidence-based Technological Interventions) Tremor Dataset. (2024). Zenodo. https://doi.org/10.5281/zenodo.10782573

## Layout

```
data/alameda/
└── ALAMEDA_PD_tremor_dataset.csv   # 5.77 MB, 4152 rows, 99 columns
```

Single CSV — no raw sensor traces. The release ships **pre-extracted feature windows** (statistical + spectral descriptors of accelerometer magnitude and PC1 projection), already analogous to the glove DSP output schema.

## File format

99 columns total:

| Column group | Count | Examples | Notes |
|---|---|---|---|
| Metadata | 3 | `start_timestamp`, `end_timestamp`, `subject_id` | Window timestamps as `MM:SS.f`; subject_id integer |
| Magnitude features | 44 | `Magnitude_mean`, `Magnitude_std_dev`, `Magnitude_iqr`, `Magnitude_skewness`, `Magnitude_rms`, `Magnitude_energy`, `Magnitude_sampen`, `Magnitude_dfa`, `Magnitude_fft_dom_freq`, … | Statistical + frequency-domain descriptors of accelerometer magnitude |
| PC1 features | 48 | `PC1_mean`, `PC1_std_dev`, `PC1_fft_dom_freq`, `PC1_fft_entropy`, `PC1_fft_flatness`, … | Same descriptors over the first principal component of the 3-axis accel signal |
| Labels (tremor task / state) | 4 | `Constancy_of_rest`, `Kinetic_tremor`, `Postural_tremor`, `Rest_tremor` | MDS-UPDRS Part III tremor sub-task indicators |

Subject distribution (11 subjects): 392/84/350/350/175/700/350/1050/175/175/350 rows.

## Quick load (Python)

```python
import pandas as pd

df = pd.read_csv('data/alameda/ALAMEDA_PD_tremor_dataset.csv')
print(df.shape)                 # (4152, 99)
print(df['subject_id'].nunique())  # 11

# Tremor-task one-hot already separated:
LABEL_COLS = ['Rest_tremor', 'Postural_tremor', 'Kinetic_tremor', 'Constancy_of_rest']
FEATURE_COLS = [c for c in df.columns
                if c not in {'start_timestamp', 'end_timestamp', 'subject_id'} | set(LABEL_COLS)]
```

## Why this dataset, and how it pairs with the glove DSP

ALAMEDA ships at a feature granularity that **maps almost directly onto the PD-glove DSP output**:

| Glove output (per `tremor_validation_master.csv`) | ALAMEDA analog |
|---|---|
| `dominant_freq_hz` (4–6 Hz FFT peak) | `Magnitude_fft_dom_freq`, `PC1_fft_dom_freq` |
| `dominant_amp` | `Magnitude_fft_pw_ar_dom_freq` (power at dom freq) |
| `band_power` (4–6 Hz total power) | `Magnitude_fft_energy`, `PC1_fft_energy` |

This is the schema-alignment work the syllabus calls for in Week 2 ("ALAMEDA feature alignment; feature format aligned to glove DSP output schema"). The mapping above is the starting point — a documented unified-schema notebook lands in D1 (`Dataset_Pipeline.ipynb`).

## Gitignore policy

Raw CSV is not committed (5.77 MB; reproducible from Zenodo). Only this README is tracked. To restore:

```bash
mkdir -p data/alameda && cd data/alameda
curl -sSL -o ALAMEDA_PD_tremor_dataset.csv \
  "https://zenodo.org/api/records/10782573/files/ALAMEDA_PD_tremor_dataset.csv/content"
```

Canonical long-term storage for cross-environment access is the AWS S3 bucket (per syllabus); upload happens in Week 2.
