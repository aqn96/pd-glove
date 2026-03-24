from __future__ import annotations

import argparse
import csv
import time
from dataclasses import dataclass
from errno import EREMOTEIO
from pathlib import Path

import smbus2

TCA9548A_ADDR = 0x70
MPU6050_ADDR = 0x68
MPU6050_PWR_MGMT_1 = 0x6B
MPU6050_ACCEL_XOUT_H = 0x3B
CHANNELS = (0, 1, 2, 3, 4)
SAMPLE_RATE_HZ = 100.0
SAMPLE_PERIOD_S = 1.0 / SAMPLE_RATE_HZ
MUX_SETTLE_S = 0.0008
RETRY_COUNT = 3
RETRY_BACKOFF_S = 0.002


def parse_channels(raw: str) -> tuple[int, ...]:
    channels: list[int] = []
    for token in raw.split(","):
        channel = int(token.strip())
        if channel < 0 or channel > 7:
            raise ValueError("Channel values must be in range 0..7")
        channels.append(channel)
    return tuple(channels)


@dataclass(frozen=True)
class ImuSample:
    timestamp: float
    channel: int
    ax: int
    ay: int
    az: int
    gx: int
    gy: int
    gz: int


class MultiImuReader:
    def __init__(self, bus_id: int = 1, channels: tuple[int, ...] = CHANNELS) -> None:
        self.bus = smbus2.SMBus(bus_id)
        self.channels = channels
        self.retry_events = 0

    def _select_channel(self, channel: int) -> None:
        self.bus.write_byte_data(TCA9548A_ADDR, 0x00, 1 << channel)
        time.sleep(MUX_SETTLE_S)

    @staticmethod
    def _to_signed(high: int, low: int) -> int:
        value = (high << 8) | low
        return value - 65536 if value >= 32768 else value

    def _read_channel_block_with_retry(self, channel: int) -> list[int]:
        last_error: OSError | None = None
        for attempt in range(RETRY_COUNT):
            try:
                self._select_channel(channel)
                return self.bus.read_i2c_block_data(MPU6050_ADDR, MPU6050_ACCEL_XOUT_H, 14)
            except OSError as error:
                last_error = error
                if error.errno != EREMOTEIO or attempt == RETRY_COUNT - 1:
                    raise
                self.retry_events += 1
                time.sleep(RETRY_BACKOFF_S * (attempt + 1))
        assert last_error is not None
        raise last_error

    def wake_all(self) -> None:
        for channel in self.channels:
            self._select_channel(channel)
            self.bus.write_byte_data(MPU6050_ADDR, MPU6050_PWR_MGMT_1, 0)
            time.sleep(0.005)

    def read_channel(self, channel: int, timestamp: float | None = None) -> ImuSample:
        sample_time = time.time() if timestamp is None else timestamp
        block = self._read_channel_block_with_retry(channel)
        ax = self._to_signed(block[0], block[1])
        ay = self._to_signed(block[2], block[3])
        az = self._to_signed(block[4], block[5])
        gx = self._to_signed(block[8], block[9])
        gy = self._to_signed(block[10], block[11])
        gz = self._to_signed(block[12], block[13])
        return ImuSample(sample_time, channel, ax, ay, az, gx, gy, gz)

    def stream(self, duration_s: float, log_interval_s: float = 1.0) -> list[ImuSample]:
        total_ticks = int(duration_s * SAMPLE_RATE_HZ)
        samples: list[ImuSample] = []
        start = time.monotonic()
        next_log = start + max(log_interval_s, 0.1)
        next_tick = time.monotonic()
        for tick in range(total_ticks):
            tick_timestamp = time.time()
            for channel in self.channels:
                samples.append(self.read_channel(channel, tick_timestamp))
            next_tick += SAMPLE_PERIOD_S
            sleep_for = next_tick - time.monotonic()
            if sleep_for > 0:
                time.sleep(sleep_for)
            now = time.monotonic()
            if now >= next_log:
                elapsed = now - start
                completed_ticks = tick + 1
                effective_hz = completed_ticks / elapsed if elapsed > 0 else 0.0
                print(
                    f"[progress] elapsed={elapsed:.1f}s ticks={completed_ticks}/{total_ticks} "
                    f"effective_hz={effective_hz:.1f} retries={self.retry_events}",
                    flush=True,
                )
                next_log = now + log_interval_s
        return samples

    def close(self) -> None:
        self.bus.close()


def write_csv(samples: list[ImuSample], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "channel", "ax", "ay", "az", "gx", "gy", "gz"])
        for sample in samples:
            writer.writerow(
                [
                    f"{sample.timestamp:.6f}",
                    sample.channel,
                    sample.ax,
                    sample.ay,
                    sample.az,
                    sample.gx,
                    sample.gy,
                    sample.gz,
                ]
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Read MPU6050 sensors at 100Hz via TCA9548A.")
    parser.add_argument("--duration", type=float, default=10.0, help="Capture duration in seconds.")
    parser.add_argument("--output", type=Path, default=Path("imu_capture.csv"), help="CSV output path.")
    parser.add_argument("--log-interval", type=float, default=1.0, help="Progress log interval in seconds.")
    parser.add_argument(
        "--channels",
        type=str,
        default="0,1,2,3,4",
        help="Comma-separated mux channels to capture (default: 0,1,2,3,4).",
    )
    args = parser.parse_args()

    channels = parse_channels(args.channels)
    reader = MultiImuReader(channels=channels)
    wall_start = time.monotonic()
    try:
        reader.wake_all()
        print(
            f"Starting capture: duration={args.duration:.2f}s channels={len(channels)} "
            f"target_hz={SAMPLE_RATE_HZ:.0f}",
            flush=True,
        )
        samples = reader.stream(duration_s=args.duration, log_interval_s=args.log_interval)
        write_csv(samples, args.output)
    finally:
        reader.close()

    wall_elapsed = time.monotonic() - wall_start
    loop_hz = (len(samples) / len(channels)) / wall_elapsed if wall_elapsed > 0 else 0.0
    print(
        f"Captured {len(samples)} rows across {len(channels)} channels at {SAMPLE_RATE_HZ:.0f}Hz loop "
        f"for {args.duration:.2f}s -> {args.output}"
    )
    print(
        f"Final stats: wall_time={wall_elapsed:.2f}s effective_hz={loop_hz:.2f} retries={reader.retry_events}",
        flush=True,
    )


if __name__ == "__main__":
    main()
