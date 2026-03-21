from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.signal import butter, filtfilt

SAMPLE_RATE_HZ = 100.0
LOWCUT_HZ = 3.0
HIGHCUT_HZ = 15.0
FILTER_ORDER = 4
TREMOR_MIN_HZ = 4.0
TREMOR_MAX_HZ = 6.0


def butter_bandpass_filter(
    signal: np.ndarray,
    lowcut_hz: float = LOWCUT_HZ,
    highcut_hz: float = HIGHCUT_HZ,
    sample_rate_hz: float = SAMPLE_RATE_HZ,
    order: int = FILTER_ORDER,
) -> np.ndarray:
    nyquist = 0.5 * sample_rate_hz
    b, a = butter(order, [lowcut_hz / nyquist, highcut_hz / nyquist], btype="band")
    return filtfilt(b, a, signal)


def compute_fft(signal: np.ndarray, sample_rate_hz: float = SAMPLE_RATE_HZ) -> tuple[np.ndarray, np.ndarray]:
    n = len(signal)
    spectrum = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(n, d=1.0 / sample_rate_hz)
    magnitudes = np.abs(spectrum) / n
    return freqs, magnitudes


def tremor_metrics(freqs: np.ndarray, magnitudes: np.ndarray) -> dict[str, float]:
    band_mask = (freqs >= TREMOR_MIN_HZ) & (freqs <= TREMOR_MAX_HZ)
    if not np.any(band_mask):
        return {"dominant_freq_hz": 0.0, "dominant_amp": 0.0, "band_power": 0.0}

    band_freqs = freqs[band_mask]
    band_mags = magnitudes[band_mask]
    peak_idx = int(np.argmax(band_mags))
    band_power = float(np.sum(np.square(band_mags)))
    return {
        "dominant_freq_hz": float(band_freqs[peak_idx]),
        "dominant_amp": float(band_mags[peak_idx]),
        "band_power": band_power,
    }


def analyze_signal(signal: np.ndarray, sample_rate_hz: float = SAMPLE_RATE_HZ) -> dict[str, float]:
    filtered = butter_bandpass_filter(signal, sample_rate_hz=sample_rate_hz)
    freqs, mags = compute_fft(filtered, sample_rate_hz=sample_rate_hz)
    return tremor_metrics(freqs, mags)


def load_channel_axis(csv_path: Path, channel: int, axis: str) -> np.ndarray:
    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    if axis not in data.dtype.names:
        raise ValueError(f"Axis '{axis}' not found in CSV columns: {data.dtype.names}")
    channel_data = data[data["channel"] == channel]
    if channel_data.size == 0:
        raise ValueError(f"No samples found for channel {channel} in {csv_path}")
    return np.asarray(channel_data[axis], dtype=np.float64)


def synthetic_signal(duration_s: float = 10.0, sample_rate_hz: float = SAMPLE_RATE_HZ) -> np.ndarray:
    t = np.arange(0.0, duration_s, 1.0 / sample_rate_hz)
    tremor = 0.8 * np.sin(2 * np.pi * 5.0 * t)
    motion = 0.2 * np.sin(2 * np.pi * 1.0 * t)
    noise = 0.08 * np.random.randn(len(t))
    return tremor + motion + noise


def main() -> None:
    parser = argparse.ArgumentParser(description="Run tremor DSP pipeline (3-15Hz + FFT 4-6Hz metrics).")
    parser.add_argument("--input", type=Path, help="Optional CSV from sensor_reader.py")
    parser.add_argument("--channel", type=int, default=0, help="Channel to analyze when --input is provided.")
    parser.add_argument("--axis", type=str, default="ax", choices=["ax", "ay", "az", "gx", "gy", "gz"])
    args = parser.parse_args()

    if args.input:
        signal = load_channel_axis(args.input, channel=args.channel, axis=args.axis)
        source = f"{args.input} (ch={args.channel}, axis={args.axis})"
    else:
        signal = synthetic_signal()
        source = "synthetic 5Hz tremor signal"

    metrics = analyze_signal(signal)
    print(f"Source: {source}")
    print(f"Dominant tremor frequency (4-6Hz): {metrics['dominant_freq_hz']:.3f} Hz")
    print(f"Dominant amplitude (4-6Hz): {metrics['dominant_amp']:.6f}")
    print(f"Tremor band power (4-6Hz): {metrics['band_power']:.6f}")


if __name__ == "__main__":
    main()
