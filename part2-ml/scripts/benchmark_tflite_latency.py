"""
D3 — Local latency benchmark for the INT8 TFLite CNN.

Runs the quantized model (part2-ml/results/d3_tflite/pads_cnn1d_int8.tflite)
on this machine and times inference. This is a SIMULATED proxy, not a
Raspberry Pi 5 measurement:

- Uses ai-edge-litert (Google's lightweight standalone TFLite interpreter,
  the same runtime family an actual Pi deployment would use) rather than
  pulling in full TensorFlow.
- Runs on Apple Silicon (ARM64) — the same instruction-set family as the
  Pi 5's Cortex-A76, which makes this a better proxy than an x86 machine,
  but the M3 Pro's cores are far more powerful. Treat this number as a
  best-case bound, not an equivalent to real Pi 5 latency.

Usage:
    .venv/bin/python3 scripts/benchmark_tflite_latency.py
"""
import json
import platform
import resource
import time
from pathlib import Path

import numpy as np
from ai_edge_litert.interpreter import Interpreter

MODEL_PATH  = Path(__file__).resolve().parents[1] / "results" / "d3_tflite" / "pads_cnn1d_int8.tflite"
OUTPUT_PATH = MODEL_PATH.parent / "local_latency_benchmark.json"

N_WARMUP = 20
N_TRIALS = 500


def peak_memory_mb():
    """Peak resident set size of this whole process so far, in MB. Reflects
    Python/numpy/interpreter import overhead too, not just the model's
    isolated footprint -- units differ by OS (macOS: bytes, Linux: KB)."""
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak / (1024 * 1024) if platform.system() == "Darwin" else peak / 1024


def main():
    interpreter = Interpreter(model_path=str(MODEL_PATH))
    interpreter.allocate_tensors()
    in_detail  = interpreter.get_input_details()[0]
    out_detail = interpreter.get_output_details()[0]

    shape = in_detail["shape"]
    dtype = in_detail["dtype"]
    print(f"Model      : {MODEL_PATH.name}  ({MODEL_PATH.stat().st_size / 1024:.1f} KB)")
    print(f"Input      : shape={shape}  dtype={dtype}")
    print(f"Machine    : {platform.machine()}  {platform.processor() or platform.platform()}")

    # Latency depends on shape/dtype, not on actual sensor values, so a
    # fixed random window is fine for timing purposes.
    rng = np.random.default_rng(42)
    x = rng.standard_normal(size=shape).astype(dtype)

    # Cold start: the very first inference call, including one-time
    # interpreter/delegate setup cost that every later call skips. This is
    # the number that matters for "how long after boot until the first
    # score is ready."
    cold_start_t0 = time.perf_counter()
    interpreter.set_tensor(in_detail["index"], x)
    interpreter.invoke()
    _ = interpreter.get_tensor(out_detail["index"])
    cold_start_ms = (time.perf_counter() - cold_start_t0) * 1000

    # Remaining warm-up: excludes setup cost from the steady-state
    # measurement below.
    for _ in range(N_WARMUP - 1):
        interpreter.set_tensor(in_detail["index"], x)
        interpreter.invoke()

    latencies_ms = []
    for _ in range(N_TRIALS):
        start = time.perf_counter()
        interpreter.set_tensor(in_detail["index"], x)
        interpreter.invoke()
        _ = interpreter.get_tensor(out_detail["index"])
        latencies_ms.append((time.perf_counter() - start) * 1000)

    peak_mem_mb = peak_memory_mb()

    latencies_ms = np.array(latencies_ms)
    result = {
        "model": MODEL_PATH.name,
        "model_size_kb": round(MODEL_PATH.stat().st_size / 1024, 1),
        "machine": platform.machine(),
        "n_trials": N_TRIALS,
        "cold_start_ms": round(cold_start_ms, 4),
        "peak_memory_mb": round(peak_mem_mb, 2),
        "latency_ms": {
            "mean":   round(float(latencies_ms.mean()), 4),
            "median": round(float(np.median(latencies_ms)), 4),
            "p95":    round(float(np.percentile(latencies_ms, 95)), 4),
            "p99":    round(float(np.percentile(latencies_ms, 99)), 4),
            "min":    round(float(latencies_ms.min()), 4),
            "max":    round(float(latencies_ms.max()), 4),
        },
        "note": (
            "Simulated on Apple M3 Pro (ARM64), not measured on Raspberry "
            "Pi 5. Same instruction-set family as the Pi 5's Cortex-A76, "
            "but a far more powerful chip -- treat as a best-case bound, "
            "not an equivalent number. peak_memory_mb is whole-process "
            "peak RSS (includes Python/numpy/interpreter import overhead), "
            "not the model's isolated memory footprint."
        ),
    }

    print(f"\nCold start (first call, incl. setup): {cold_start_ms:.4f} ms")
    print(f"Peak process memory: {peak_mem_mb:.2f} MB")
    print(f"\nSteady-state latency over {N_TRIALS} trials (ms):")
    for k, v in result["latency_ms"].items():
        print(f"  {k:>6}: {v}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
