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

**You will be prompted for:**
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
cat ~/pd-glove/tremor_validation_master.csv | column -t -s,

# Or copy to laptop for analysis
scp aqnguyen96@iotpi5.local:~/pd-glove/tremor_validation_master.csv ~/Downloads/
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
```

## Troubleshooting

**If a test fails mid-run:**
- The master CSV won't be updated (transaction-safe)
- Just re-run the script

**If you need to delete a bad test:**
- Edit `tremor_validation_master.csv` manually and remove the rows
- Or use a CSV editor on your laptop after copying

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
