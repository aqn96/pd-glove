from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_DIR = REPO_ROOT / "data"
MASTER_CSV = DATA_DIR / "tremor_validation_master.csv"


def run_command(command: list[str]) -> None:
    print(f"$ {' '.join(command)}", flush=True)
    subprocess.run(command, check=True)


def run_dsp_for_channels(csv_path: Path, channels: tuple[int, ...], axis: str) -> dict[int, dict[str, float]]:
    """Run DSP analysis and return metrics for each channel."""
    print(f"\n=== DSP: {csv_path} axis={axis} ===", flush=True)
    metrics = {}
    for channel in channels:
        command = [
            sys.executable,
            str(SCRIPT_DIR / "dsp_pipeline.py"),
            "--input",
            str(csv_path),
            "--channel",
            str(channel),
            "--axis",
            axis,
        ]
        
        # Capture output to parse metrics
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout, flush=True)
        
        # Parse output for metrics
        lines = result.stdout.strip().split('\n')
        freq = amp = power = 0.0
        for line in lines:
            if 'Dominant tremor frequency' in line:
                freq = float(line.split(':')[1].split()[0])
            elif 'Dominant amplitude' in line:
                amp = float(line.split(':')[1].strip())
            elif 'Tremor band power' in line:
                power = float(line.split(':')[1].strip())
        
        metrics[channel] = {
            'dominant_freq_hz': freq,
            'dominant_amp': amp,
            'band_power': power
        }
    
    return metrics


def parse_channels(raw: str) -> tuple[int, ...]:
    channels: list[int] = []
    for token in raw.split(","):
        channel = int(token.strip())
        if channel < 0 or channel > 7:
            raise ValueError("Channel values must be in range 0..7")
        channels.append(channel)
    return tuple(channels)


def append_to_master_csv(person_id: str, test_name: str, timestamp: str, channels: tuple[int, ...],
                         rest_metrics: dict[int, dict[str, float]], 
                         tremor_metrics: dict[int, dict[str, float]],
                         sampling_hz: float, retries: int, notes: str = "") -> None:
    """Append validation results to master CSV."""
    
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    # Create CSV with headers if it doesn't exist
    if not MASTER_CSV.exists():
        with open(MASTER_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['person_id', 'test_name', 'timestamp', 'channel', 'condition', 
                           'dominant_freq_hz', 'dominant_amp', 'band_power', 
                           'sampling_hz', 'retries', 'notes'])
    
    # Append new data
    with open(MASTER_CSV, 'a', newline='') as f:
        writer = csv.writer(f)
        
        for channel in channels:
            # Write rest data
            rest = rest_metrics[channel]
            writer.writerow([
                person_id, test_name, timestamp, channel, 'rest',
                rest['dominant_freq_hz'], rest['dominant_amp'], rest['band_power'],
                sampling_hz, retries, notes
            ])
            
            # Write tremor data
            tremor = tremor_metrics[channel]
            writer.writerow([
                person_id, test_name, timestamp, channel, 'tremor',
                tremor['dominant_freq_hz'], tremor['dominant_amp'], tremor['band_power'],
                sampling_hz, retries, notes
            ])
    
    print(f"\n✅ Results appended to master CSV: {MASTER_CSV}", flush=True)


def delete_rows_from_master_csv(person_id: str | None, test_name: str | None, assume_yes: bool) -> None:
    """Delete rows from master CSV matching person_id and/or test_name."""
    if not MASTER_CSV.exists():
        print(f"Error: Master CSV not found: {MASTER_CSV}", flush=True)
        sys.exit(1)

    if not person_id and not test_name:
        print("Error: Provide at least one filter: --delete-person-id and/or --delete-test-name.", flush=True)
        sys.exit(1)

    with open(MASTER_CSV, "r", newline="") as source:
        reader = csv.DictReader(source)
        headers = reader.fieldnames
        if not headers:
            print(f"Error: CSV appears empty or missing headers: {MASTER_CSV}", flush=True)
            sys.exit(1)
        rows = list(reader)

    total_rows = len(rows)
    if total_rows == 0:
        print("Master CSV has no data rows.", flush=True)
        return

    def matches_filters(row: dict[str, str]) -> bool:
        person_match = person_id is None or row.get("person_id") == person_id
        test_match = test_name is None or row.get("test_name") == test_name
        return person_match and test_match

    rows_to_delete = [row for row in rows if matches_filters(row)]
    if not rows_to_delete:
        print("No matching rows found. No changes made.", flush=True)
        return

    kept_rows = [row for row in rows if not matches_filters(row)]
    delete_count = len(rows_to_delete)
    percent = (delete_count / total_rows) * 100

    filter_text = []
    if person_id:
        filter_text.append(f"person_id='{person_id}'")
    if test_name:
        filter_text.append(f"test_name='{test_name}'")
    print(f"Matched {delete_count}/{total_rows} rows ({percent:.1f}%) for {' and '.join(filter_text)}.", flush=True)

    if not assume_yes:
        response = input("Proceed with deletion? Type 'yes' to confirm: ").strip().lower()
        if response != "yes":
            print("Deletion cancelled. No changes made.", flush=True)
            return

    temp_path: Path | None = None
    try:
        with NamedTemporaryFile("w", delete=False, newline="", dir=str(MASTER_CSV.parent)) as temp:
            temp_path = Path(temp.name)
            writer = csv.DictWriter(temp, fieldnames=headers)
            writer.writeheader()
            writer.writerows(kept_rows)
        temp_path.replace(MASTER_CSV)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()

    print(f"✅ Deleted {delete_count} rows from {MASTER_CSV}", flush=True)
    print(f"Remaining rows: {len(kept_rows)}", flush=True)


def print_workflow_help() -> None:
    """Print practical usage guidance for demo operation."""
    print("\nTremor Validation Workflow Help", flush=True)
    print("- Run capture flow (interactive):", flush=True)
    print("  python3 scripts/run_tremor_validation.py", flush=True)
    print("- Delete demo rows by person ID:", flush=True)
    print("  python3 scripts/run_tremor_validation.py --delete-person-id test1", flush=True)
    print("- Delete by test name:", flush=True)
    print("  python3 scripts/run_tremor_validation.py --delete-test-name demo", flush=True)
    print("- Combine filters for targeted cleanup:", flush=True)
    print("  python3 scripts/run_tremor_validation.py --delete-person-id person_A --delete-test-name demo", flush=True)
    print("- Skip delete confirmation:", flush=True)
    print("  python3 scripts/run_tremor_validation.py --delete-person-id test1 --yes", flush=True)
    print("- Show this help page:", flush=True)
    print("  python3 scripts/run_tremor_validation.py --workflow-help\n", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full rest+tremor validation workflow.")
    parser.add_argument("--person-id", type=str, help="Person identifier (e.g., person_1, person_A). If not provided, will prompt.")
    parser.add_argument("--test-name", type=str, help="Test name (e.g., test_one). If not provided, will prompt.")
    parser.add_argument("--channels", type=str, default="0,1,2,3", help="Comma-separated channels.")
    parser.add_argument("--duration", type=float, default=10.0, help="Capture duration per trial.")
    parser.add_argument(
        "--axis",
        type=str,
        default="ax",
        choices=["ax", "ay", "az", "gx", "gy", "gz"],
        help="Axis to analyze with DSP pipeline.",
    )
    parser.add_argument("--rest-output", type=Path, default=Path("rest_4ch.csv"), help="Rest CSV output path.")
    parser.add_argument(
        "--tremor-output",
        type=Path,
        default=Path("tremor_4ch.csv"),
        help="Tremor CSV output path.",
    )
    parser.add_argument("--notes", type=str, default="", help="Optional notes about this test.")
    parser.add_argument("--sampling-hz", type=float, default=89.0, help="Expected sampling rate (for CSV metadata).")
    parser.add_argument(
        "--delete-person-id",
        type=str,
        help="Delete mode: remove all rows matching this person_id from the master CSV.",
    )
    parser.add_argument(
        "--delete-test-name",
        type=str,
        help="Delete mode: remove all rows matching this test_name from the master CSV.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Delete mode: skip confirmation prompt.",
    )
    parser.add_argument(
        "--workflow-help",
        action="store_true",
        help="Show practical run/delete examples and exit.",
    )
    args = parser.parse_args()

    if args.workflow_help:
        print_workflow_help()
        return

    if (
        not args.delete_person_id
        and not args.delete_test_name
        and not args.person_id
        and not args.test_name
        and sys.stdin.isatty()
    ):
        print("\nSelect mode:", flush=True)
        print("1) Run validation capture", flush=True)
        print("2) Delete rows from master CSV", flush=True)
        print("3) Show workflow help", flush=True)
        mode_choice = input("Enter choice [1/2/3] (default 1): ").strip()
        if mode_choice == "2":
            delete_person = input("Person ID to delete (leave blank to skip): ").strip()
            delete_test = input("Test name to delete (leave blank to skip): ").strip()
            args.delete_person_id = delete_person or None
            args.delete_test_name = delete_test or None
            if not args.delete_person_id and not args.delete_test_name:
                print("Error: Enter at least one delete filter.", flush=True)
                sys.exit(1)
        elif mode_choice in {"3", "h", "H", "?"}:
            print_workflow_help()
            return

    if args.delete_person_id or args.delete_test_name:
        if (
            args.person_id
            or args.test_name
            or args.notes
            or args.rest_output != Path("rest_4ch.csv")
            or args.tremor_output != Path("tremor_4ch.csv")
            or args.channels != "0,1,2,3"
            or args.duration != 10.0
            or args.axis != "ax"
            or args.sampling_hz != 89.0
        ):
            print(
                "Error: Delete mode cannot be combined with capture options. "
                "Use only --delete-person-id/--delete-test-name and optional --yes.",
                flush=True,
            )
            sys.exit(1)

        delete_rows_from_master_csv(
            person_id=args.delete_person_id,
            test_name=args.delete_test_name,
            assume_yes=args.yes,
        )
        return

    # Prompt for person_id if not provided
    person_id = args.person_id
    if not person_id:
        person_id = input("\nEnter person ID (e.g., person_1, person_A, person_B): ").strip()
        if not person_id:
            print("Error: Person ID is required.", flush=True)
            sys.exit(1)
    
    # Prompt for test_name if not provided
    test_name = args.test_name
    if not test_name:
        test_name = input("Enter test name (e.g., test_one, test_two): ").strip()
        if not test_name:
            print("Error: Test name is required.", flush=True)
            sys.exit(1)

    channels = parse_channels(args.channels)
    channels_arg = ",".join(str(c) for c in channels)
    timestamp = datetime.now().isoformat() + 'Z'

    print(f"\n{'='*60}")
    print(f"Person ID: {person_id}")
    print(f"Test Name: {test_name}")
    print(f"Timestamp: {timestamp}")
    print(f"{'='*60}\n")

    print("Step 1/4: Hardware probe", flush=True)
    run_command([sys.executable, str(SCRIPT_DIR / "test_imus.py"), "--channels", channels_arg])

    print("\nStep 2/4: Rest capture", flush=True)
    run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "sensor_reader.py"),
            "--channels",
            channels_arg,
            "--duration",
            f"{args.duration}",
            "--output",
            str(args.rest_output),
        ]
    )

    print("\nStep 3/4: Tremor capture", flush=True)
    print("Perform tremor motion now while recording this segment.", flush=True)
    run_command(
        [
            sys.executable,
            str(SCRIPT_DIR / "sensor_reader.py"),
            "--channels",
            channels_arg,
            "--duration",
            f"{args.duration}",
            "--output",
            str(args.tremor_output),
        ]
    )

    print("\nStep 4/4: DSP analysis", flush=True)
    rest_metrics = run_dsp_for_channels(args.rest_output, channels, args.axis)
    tremor_metrics = run_dsp_for_channels(args.tremor_output, channels, args.axis)

    # Append to master CSV
    append_to_master_csv(
        person_id=person_id,
        test_name=test_name,
        timestamp=timestamp,
        channels=channels,
        rest_metrics=rest_metrics,
        tremor_metrics=tremor_metrics,
        sampling_hz=args.sampling_hz,
        retries=0,  # Extracted from sensor_reader output if needed
        notes=args.notes
    )

    print("\nValidation workflow complete.", flush=True)
    print(f"Rest CSV:   {args.rest_output}", flush=True)
    print(f"Tremor CSV: {args.tremor_output}", flush=True)
    print(f"Master CSV: {MASTER_CSV}", flush=True)


if __name__ == "__main__":
    main()
