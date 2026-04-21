#!/usr/bin/env python3
"""PD Glove — Tremor Assessment Demo Server"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request, stream_with_context

REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "data"
MASTER_CSV = DATA_DIR / "tremor_validation_master.csv"
SCRIPTS_DIR = REPO_ROOT / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
from dsp_pipeline import analyze_signal, load_channel_axis  # noqa: E402

app = Flask(__name__)

CHANNELS = (0, 1, 2, 3)
DURATION = 10.0
AXIS = "ax"
REST_CSV = REPO_ROOT / "rest_4ch.csv"
TREMOR_CSV = REPO_ROOT / "tremor_4ch.csv"
REST_COUNTDOWN_S = 5
TREMOR_COUNTDOWN_S = 3
CSV_HEADERS = [
    "person_id", "test_name", "timestamp", "channel", "condition",
    "dominant_freq_hz", "dominant_amp", "band_power", "sampling_hz", "retries", "notes",
]

_lock = threading.Lock()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def sse(event: str, **data) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def classify_severity(band_power: float) -> tuple[str, str]:
    if band_power < 1000:
        return "Minimal", "#6b7280"
    elif band_power < 2500:
        return "Light", "#3b82f6"
    elif band_power < 7000:
        return "Mild", "#f59e0b"
    elif band_power < 15000:
        return "Moderate", "#f97316"
    else:
        return "Marked", "#ef4444"


def read_all_rows() -> list[dict]:
    if not MASTER_CSV.exists():
        return []
    with open(MASTER_CSV, "r", newline="") as f:
        return list(csv.DictReader(f))


def subject_summary(rows: list[dict]) -> list[dict]:
    """Aggregate rows into one entry per person_id."""
    subjects: dict[str, dict] = {}
    for row in rows:
        pid = row["person_id"]
        if pid not in subjects:
            subjects[pid] = {
                "person_id": pid,
                "tests": set(),
                "rest": [],
                "tremor": [],
                "latest": "",
            }
        subjects[pid]["tests"].add(row["test_name"])
        subjects[pid]["latest"] = max(subjects[pid]["latest"], row["timestamp"])
        bp = float(row["band_power"])
        if row["condition"] == "rest":
            subjects[pid]["rest"].append(bp)
        else:
            subjects[pid]["tremor"].append(bp)

    result = []
    for s in subjects.values():
        ar = sum(s["rest"]) / len(s["rest"]) if s["rest"] else 0
        at = sum(s["tremor"]) / len(s["tremor"]) if s["tremor"] else 0
        label, color = classify_severity(at)
        result.append({
            "person_id": s["person_id"],
            "test_count": len(s["tests"]),
            "avg_rest_power": round(ar, 1),
            "avg_tremor_power": round(at, 1),
            "severity_label": label,
            "severity_color": color,
            "latest": s["latest"],
        })
    result.sort(key=lambda x: x["latest"])
    return result


def _per_subject_averages(rows: list[dict]) -> tuple[float, float, int]:
    """Return (avg_rest, avg_tremor, subject_count) weighted equally per subject."""
    by_subject: dict[str, dict[str, list[float]]] = {}
    for r in rows:
        pid = r["person_id"]
        if pid not in by_subject:
            by_subject[pid] = {"rest": [], "tremor": []}
        bp = float(r["band_power"])
        if r["condition"] == "rest":
            by_subject[pid]["rest"].append(bp)
        elif r["condition"] == "tremor":
            by_subject[pid]["tremor"].append(bp)
    rest_avgs = [sum(v["rest"]) / len(v["rest"]) for v in by_subject.values() if v["rest"]]
    tremor_avgs = [sum(v["tremor"]) / len(v["tremor"]) for v in by_subject.values() if v["tremor"]]
    avg_rest = sum(rest_avgs) / len(rest_avgs) if rest_avgs else 0.0
    avg_tremor = sum(tremor_avgs) / len(tremor_avgs) if tremor_avgs else 0.0
    return avg_rest, avg_tremor, len(by_subject)


def population_stats(rows: list[dict]) -> dict:
    avg_rest, avg_tremor, n = _per_subject_averages(rows)
    pids = set(r["person_id"] for r in rows)
    return {
        "avg_rest_power": round(avg_rest, 1),
        "avg_tremor_power": round(avg_tremor, 1),
        "subject_count": len(pids),
    }


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/records")
def get_records():
    rows = read_all_rows()
    return jsonify({
        "subjects": subject_summary(rows),
        "population": population_stats(rows),
    })


@app.route("/api/records/<person_id>", methods=["DELETE"])
def delete_person(person_id: str):
    if not MASTER_CSV.exists():
        return jsonify({"error": "No data"}), 404
    rows = read_all_rows()
    kept = [r for r in rows if r["person_id"] != person_id]
    if len(kept) == len(rows):
        return jsonify({"error": f"No records for '{person_id}'"}), 404
    _write_csv(kept)
    return jsonify({"deleted": len(rows) - len(kept), "remaining": len(kept)})


@app.route("/api/records/<person_id>/<test_name>", methods=["DELETE"])
def delete_test(person_id: str, test_name: str):
    if not MASTER_CSV.exists():
        return jsonify({"error": "No data"}), 404
    rows = read_all_rows()
    kept = [r for r in rows if not (r["person_id"] == person_id and r["test_name"] == test_name)]
    if len(kept) == len(rows):
        return jsonify({"error": "No matching records"}), 404
    _write_csv(kept)
    return jsonify({"deleted": len(rows) - len(kept), "remaining": len(kept)})


def _write_csv(rows: list[dict]) -> None:
    with open(MASTER_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


@app.route("/api/assess")
def assess():
    person_id = request.args.get("person_id", "").strip()
    test_name = request.args.get("test_name", "").strip()
    notes = request.args.get("notes", "").strip()

    if not person_id or not test_name:
        return jsonify({"error": "person_id and test_name are required"}), 400

    if not _lock.acquire(blocking=False):
        return jsonify({"error": "An assessment is already running"}), 409

    def generate():
        try:
            yield from _run_assessment(person_id, test_name, notes)
        finally:
            _lock.release()

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _run_assessment(person_id: str, test_name: str, notes: str):
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    ch_str = ",".join(str(c) for c in CHANNELS)

    # ── Step 1: Hardware probe ────────────────────────────────────────────────
    yield sse("step", num=1, label="Hardware Check", message="Connecting to sensors…")
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS_DIR / "test_imus.py"), "--channels", ch_str],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
    )
    for line in proc.stdout:
        yield sse("log", text=line.rstrip())
    proc.wait()
    if proc.returncode != 0:
        yield sse("error", message="Hardware probe failed — check sensor connections.")
        return
    yield sse("step_done", num=1)

    # ── Rest countdown ────────────────────────────────────────────────────────
    yield sse("prompt",
              icon="✋",
              heading="Hold Still",
              sub="Place your hand flat on the table and hold completely still.",
              seconds=REST_COUNTDOWN_S,
              color="#3b82f6")
    for i in range(REST_COUNTDOWN_S, 0, -1):
        yield sse("tick", seconds=i)
        time.sleep(1)
    yield sse("tick", seconds=0)

    # ── Step 2: Rest capture ──────────────────────────────────────────────────
    yield sse("step", num=2, label="Rest Recording", message="Recording rest — don't move")
    yield sse("capture", duration=DURATION, label="Rest Recording")
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS_DIR / "sensor_reader.py"),
         "--channels", ch_str, "--duration", str(DURATION), "--output", str(REST_CSV)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
    )
    for line in proc.stdout:
        yield sse("log", text=line.rstrip())
    proc.wait()
    yield sse("step_done", num=2)

    # ── Tremor countdown ──────────────────────────────────────────────────────
    yield sse("prompt",
              icon="🖐",
              heading="Vibrate Your Fingers",
              sub="Keep your wrist still. Gently tremble your fingers in place — like a pill-rolling motion.",
              seconds=TREMOR_COUNTDOWN_S,
              color="#f59e0b")
    for i in range(TREMOR_COUNTDOWN_S, 0, -1):
        yield sse("tick", seconds=i)
        time.sleep(1)
    yield sse("tick", seconds=0)

    # ── Step 3: Tremor capture ────────────────────────────────────────────────
    yield sse("step", num=3, label="Tremor Recording", message="Recording tremor — keep shaking")
    yield sse("capture", duration=DURATION, label="Tremor Recording")
    proc = subprocess.Popen(
        [sys.executable, str(SCRIPTS_DIR / "sensor_reader.py"),
         "--channels", ch_str, "--duration", str(DURATION), "--output", str(TREMOR_CSV)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env,
    )
    for line in proc.stdout:
        yield sse("log", text=line.rstrip())
    proc.wait()
    yield sse("step_done", num=3)

    # ── Step 4: DSP analysis ──────────────────────────────────────────────────
    yield sse("step", num=4, label="Signal Analysis", message="Processing DSP pipeline…")
    rest_m: dict[int, dict] = {}
    tremor_m: dict[int, dict] = {}
    for ch in CHANNELS:
        try:
            rest_m[ch] = analyze_signal(load_channel_axis(REST_CSV, ch, AXIS))
            tremor_m[ch] = analyze_signal(load_channel_axis(TREMOR_CSV, ch, AXIS))
            yield sse("log", text=f"ch{ch}  rest={rest_m[ch]['band_power']:.1f}  tremor={tremor_m[ch]['band_power']:.1f}")
        except Exception as exc:
            yield sse("log", text=f"ch{ch} error: {exc}")
    yield sse("step_done", num=4)

    # ── Step 5: Save ──────────────────────────────────────────────────────────
    yield sse("step", num=5, label="Saving", message="Appending to dataset…")
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    DATA_DIR.mkdir(exist_ok=True)
    if not MASTER_CSV.exists():
        with open(MASTER_CSV, "w", newline="") as f:
            csv.writer(f).writerow(CSV_HEADERS)
    with open(MASTER_CSV, "a", newline="") as f:
        w = csv.writer(f)
        for ch in CHANNELS:
            if ch not in rest_m:
                continue
            rm, tm = rest_m[ch], tremor_m[ch]
            w.writerow([person_id, test_name, ts, ch, "rest",
                        rm["dominant_freq_hz"], rm["dominant_amp"], rm["band_power"], 89.0, 0, notes])
            w.writerow([person_id, test_name, ts, ch, "tremor",
                        tm["dominant_freq_hz"], tm["dominant_amp"], tm["band_power"], 89.0, 0, notes])
    yield sse("step_done", num=5)

    # ── Compute summary ───────────────────────────────────────────────────────
    all_rows = read_all_rows()
    this_rest = [float(r["band_power"]) for r in all_rows
                 if r["person_id"] == person_id and r["test_name"] == test_name and r["condition"] == "rest"]
    this_tremor = [float(r["band_power"]) for r in all_rows
                   if r["person_id"] == person_id and r["test_name"] == test_name and r["condition"] == "tremor"]

    avg_rest = sum(this_rest) / len(this_rest) if this_rest else 0
    avg_tremor = sum(this_tremor) / len(this_tremor) if this_tremor else 0
    pop_avg_rest, pop_avg_tremor, pop_count = _per_subject_averages(all_rows)
    ratio = avg_tremor / avg_rest if avg_rest > 0 else 0

    # Dominant freq: average across channels for rest capture
    freqs = [rest_m[ch]["dominant_freq_hz"] for ch in rest_m]
    avg_freq = sum(freqs) / len(freqs) if freqs else 0

    label, color = classify_severity(avg_tremor)

    yield sse("done",
              person_id=person_id,
              test_name=test_name,
              avg_rest_power=round(avg_rest, 1),
              avg_tremor_power=round(avg_tremor, 1),
              pop_avg_rest=round(pop_avg_rest, 1),
              pop_avg_tremor=round(pop_avg_tremor, 1),
              pop_count=pop_count,
              severity_label=label,
              severity_color=color,
              separation_ratio=round(ratio, 1),
              dominant_freq=round(avg_freq, 2))


if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"\n  PD Glove — Tremor Assessment")
    print(f"  Running at  http://{local_ip}:5000")
    print(f"              http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
