from __future__ import annotations

import argparse
import csv
import time
from dataclasses import dataclass
from errno import ERREMOTEIO
from pathlib import Path

import smbus2

TCA9548A_ADDR = 0x70
MPU6050_ADDR = 0x68
MPU6050_PWR_MGMT_1 = 0x6B
MPU6050_ACCEL_XOUT_H = 0x3B
CHANNELS = (0, 1, 2, 3, 4)
SAMPLE_RATE_HZ = 100.0
SAMPLE_PERIOD_S = 1.0 / SAMPLE_RATE_HZ
MUX_SETTLE_S = 0.003
RETRY_COUNT = 3
RETRY_BACKOFF_S = 0.002


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

    def _select_channel(self, channel: int) -> None:
        self.bus.write_byte_data(TCA9548A_ADDR, 0x00, 1 << channel)
        time.sleep(MUX_SETTLE_S)

    @staticmethod
    def _to_signed(high: int, low: int) -> int:
        value = (high << 8) | low
        return value - 65536 if value >= 32768 else value

    def _read_word(self, register: int) -> int:
        high = self.bus.read_byte_data(MPU6050_ADDR, register)
        low = self.bus.read_byte_data(MPU6050_ADDR, register + 1)
        return self._to_signed(high, low)

    def _read_word_with_retry(self, channel: int, register: int) -> int:
        last_error: OSError | None = None
        for attempt in range(RETRY_COUNT):
            try:
                self._select_channel(channel)
                return self._read_word(register)
            except OSError as error:
                last_error = error
                if error.errno != ERREMOTEIO or attempt == RETRY_COUNT - 1:
                    raise
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
        ax = self._read_word_with_retry(channel, MPU6050_ACCEL_XOUT_H)
        ay = self._read_word_with_retry(channel, MPU6050_ACCEL_XOUT_H + 2)
        az = self._read_word_with_retry(channel, MPU6050_ACCEL_XOUT_H + 4)
        gx = self._read_word_with_retry(channel, MPU6050_ACCEL_XOUT_H + 8)
        gy = self._read_word_with_retry(channel, MPU6050_ACCEL_XOUT_H + 10)
        gz = self._read_word_with_retry(channel, MPU6050_ACCEL_XOUT_H + 12)
        return ImuSample(sample_time, channel, ax, ay, az, gx, gy, gz)

    def stream(self, duration_s: float) -> list[ImuSample]:
        total_ticks = int(duration_s * SAMPLE_RATE_HZ)
        samples: list[ImuSample] = []
        next_tick = time.monotonic()
        for _ in range(total_ticks):
            tick_timestamp = time.time()
            for channel in self.channels:
                samples.append(self.read_channel(channel, tick_timestamp))
            next_tick += SAMPLE_PERIOD_S
            sleep_for = next_tick - time.monotonic()
            if sleep_for > 0:
                time.sleep(sleep_for)
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
    parser = argparse.ArgumentParser(description="Read 5 MPU6050 sensors at 100Hz via TCA9548A.")
    parser.add_argument("--duration", type=float, default=10.0, help="Capture duration in seconds.")
    parser.add_argument("--output", type=Path, default=Path("imu_capture.csv"), help="CSV output path.")
    args = parser.parse_args()

    reader = MultiImuReader()
    try:
        reader.wake_all()
        samples = reader.stream(duration_s=args.duration)
        write_csv(samples, args.output)
    finally:
        reader.close()

    print(
        f"Captured {len(samples)} rows across {len(CHANNELS)} channels at {SAMPLE_RATE_HZ:.0f}Hz loop "
        f"for {args.duration:.2f}s -> {args.output}"
    )


if __name__ == "__main__":
    main()
