# AWS Setup — S3 bucket, IAM, EC2 (CS 8674 Part II)

Required by the syllabus repo-requirements list. Documents the S3 bucket structure, the
IAM policy used, and the EC2 instance config. For D1 only **S3** is needed (cleaned
dataset storage); EC2 GPU is for D2 Transformer training.

## 1. S3 bucket

```bash
aws s3 mb s3://pd-glove-data --region us-east-1
aws s3api put-public-access-block --bucket pd-glove-data \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

### Bucket layout

```
s3://pd-glove-data/
├── deliverable1/
│   ├── raw/            # original downloads (PPMI is DUA-restricted — keep private)
│   │   ├── alameda/  ppmi/  daphnet/  glove/
│   └── cleaned/        # parquet splits written by Dataset_Pipeline.ipynb
│       ├── alameda_{train,val,test,all}.parquet
│       ├── daphnet_{train,val,test,all}.parquet
│       ├── daphnet_raw_windows.npz
│       └── glove_wide.parquet
├── deliverable2/
│   └── models/         # .pt / .tflite artifacts (D2)
└── deliverable3/       # benchmarks, fairness outputs (D3)
```

> **PPMI note:** the LONI Data Use Agreement requires restricted access. Keep
> `deliverable1/raw/ppmi/` private; never make the bucket or that prefix public.

## 2. IAM policy (least privilege)

Attach to a dedicated `pd-glove-ml` IAM user (used by Kaggle Secrets and EC2):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBucket",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::pd-glove-data"
    },
    {
      "Sid": "ObjectRW",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
      "Resource": "arn:aws:s3:::pd-glove-data/*"
    }
  ]
}
```

## 3. Credentials

- **Kaggle:** Add-ons → Secrets → add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`,
  then in the notebook:
  ```python
  from kaggle_secrets import UserSecretsClient
  import os
  s = UserSecretsClient()
  os.environ["AWS_ACCESS_KEY_ID"] = s.get_secret("AWS_ACCESS_KEY_ID")
  os.environ["AWS_SECRET_ACCESS_KEY"] = s.get_secret("AWS_SECRET_ACCESS_KEY")
  ```
- **Local / EC2:** `aws configure` (writes `~/.aws/credentials`).

## 4. Upload cleaned datasets (from the pipeline notebook)

```python
# section 6 of Dataset_Pipeline.ipynb
BUCKET = "pd-glove-data"
upload_dir_to_s3(OUT_DIR, BUCKET, prefix="deliverable1/cleaned")
```

Or from the CLI:

```bash
aws s3 sync part2-ml/results/cleaned s3://pd-glove-data/deliverable1/cleaned
```

## 5. EC2 (D2 — not required for D1)

| Setting | Value |
|---|---|
| Instance | `g4dn.xlarge` (T4, default-available) — fallback if `p3.2xlarge` quota denied |
| AMI | Deep Learning AMI (Ubuntu, PyTorch) |
| Storage | 100 GB gp3 |
| IAM role | `pd-glove-ml` (same S3 policy above) |
| Security group | SSH (22) from your IP only |

```bash
# on the instance
git clone https://github.com/aqn96/pd-glove.git && cd pd-glove/part2-ml
pip install -r requirements.txt
aws s3 sync s3://pd-glove-data/deliverable1/cleaned results/cleaned
```

> If `p3.2xlarge` is unavailable, request a service-quota increase
> (EC2 → Limits → "Running On-Demand P instances") or use `g4dn.xlarge` — the per-finger
> encoder is small enough that this is fine (see `next-steps.md` §8 R3).
