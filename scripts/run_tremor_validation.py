from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run_command(command: list[str]) -> None:
    print(f"$ {' '.join(command)}", flush=True)
    subprocess.run(command, check=True)


def run_dsp_for_channels(csv_path: Path, channels: tuple[int, ...], axis: str) -> None:
    print(f"\n=== DSP: {csv_path} axis={axis} ===", flush=True)
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
        run_command(command)


def parse_channels(raw: str) -> tuple[int, ...]:
    channels: list[int] = []
    for token in raw.split(","):
        channel = int(token.strip())
        if channel < 0 or channel > 7:
            raise ValueError("Channel values must be in range 0..7")
        channels.append(channel)
    return tuple(channels)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full rest+tremor validation workflow.")
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
    args = parser.parse_args()

    channels = parse_channels(args.channels)
    channels_arg = ",".join(str(c) for c in channels)

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
    run_dsp_for_channels(args.rest_output, channels, args.axis)
    run_dsp_for_channels(args.tremor_output, channels, args.axis)

    print("\nValidation workflow complete.", flush=True)
    print(f"Rest CSV:   {args.rest_output}", flush=True)
    print(f"Tremor CSV: {args.tremor_output}", flush=True)


if __name__ == "__main__":
    main()
