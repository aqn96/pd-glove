# Quick Start Guide - Tremor Validation on Pi

## Pull Latest Changes

```bash
ssh aqnguyen96@iotpi5.local
cd ~/pd-glove
git pull
source venv/bin/activate
```

## Run Validation Test

```bash
python3 scripts/run_tremor_validation.py
```

For standardized task setup, see `docs/assessment-and-therapy-protocol.md`.

**You will be prompted to choose mode:**
1. Run validation capture
2. Delete rows from master CSV
3. Show workflow help

If you choose capture mode, you will be prompted for:
1. Person ID (e.g., `person_C`, `person_1`)
2. Test name (e.g., `test_one`, `test_two`)

**What happens:**
1. ✅ Hardware probe (checks all IMU channels)
2. ✅ **Rest capture** (10s) — keep hand completely still
3. ✅ **Tremor capture** (10s) — perform tremor motion
4. ✅ DSP analysis (extracts 4-6 Hz metrics)
5. ✅ **Appends to `tremor_validation_master.csv`** (permanent log)

## View Results

```bash
# View master CSV
cat ~/pd-glove/data/tremor_validation_master.csv | column -t -s,

# Or copy to laptop for analysis
scp aqnguyen96@iotpi5.local:~/pd-glove/data/tremor_validation_master.csv ~/Downloads/
```

## Advanced Options

```bash
# Specify person/test via CLI (skip prompts)
python3 scripts/run_tremor_validation.py --person-id person_C --test-name test_one

# Add notes
python3 scripts/run_tremor_validation.py --notes "High intensity tremor test"

# Custom duration
python3 scripts/run_tremor_validation.py --duration 15

# All options
python3 scripts/run_tremor_validation.py \
  --person-id person_C \
  --test-name test_three \
  --channels 0,1,2,3 \
  --duration 10 \
  --axis ax \
  --notes "Testing with new wiring"

# Show practical workflow help
python3 scripts/run_tremor_validation.py --workflow-help
```

## Troubleshooting

**If a test fails mid-run:**
- The master CSV won't be updated (transaction-safe)
- Just re-run the script

**If you need to delete a bad test:**
- Delete all rows for a person ID:
  ```bash
  python3 scripts/run_tremor_validation.py --delete-person-id test1
  ```
- Delete rows for a specific test name:
  ```bash
  python3 scripts/run_tremor_validation.py --delete-test-name test_one
  ```
- Combine both filters (more targeted):
  ```bash
  python3 scripts/run_tremor_validation.py --delete-person-id person_A --delete-test-name demo
  ```
- Skip confirmation prompt:
  ```bash
  python3 scripts/run_tremor_validation.py --delete-person-id test1 --yes
  ```

**Check hardware:**
```bash
python3 scripts/test_imus.py --channels 0,1,2,3
```

## Environmental Controls

✅ **DO:**
- Keep hand completely still during rest capture
- Perform tremor during tremor capture
- Ensure nobody is walking nearby
- Use stable desk/surface

❌ **DON'T:**
- Move hand during rest
- Allow distractions during capture
- Capture on unstable surface

## Clinical Scope

This system is intended for research monitoring and decision support. It is **not** a standalone diagnostic device.
