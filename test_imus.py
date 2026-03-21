import argparse
import time

import smbus2

TCA9548A_ADDR = 0x70
MPU6050_ADDR = 0x68
MPU6050_PWR_MGMT_1 = 0x6B
MPU6050_ACCEL_XOUT_H = 0x3B


def parse_channels(raw: str) -> list[int]:
    channels = []
    for token in raw.split(","):
        channel = int(token.strip())
        if channel < 0 or channel > 7:
            raise ValueError("Channel values must be in range 0..7")
        channels.append(channel)
    return channels


def main() -> None:
    parser = argparse.ArgumentParser(description="Quick MPU6050 per-channel check through TCA9548A.")
    parser.add_argument(
        "--channels",
        type=str,
        default="0,1,2,3,4",
        help="Comma-separated mux channels to probe (default: 0,1,2,3,4).",
    )
    args = parser.parse_args()

    channels = parse_channels(args.channels)
    bus = smbus2.SMBus(1)
    failures = 0

    try:
        for channel in channels:
            try:
                bus.write_byte_data(TCA9548A_ADDR, 0, 1 << channel)
                time.sleep(0.01)
                bus.write_byte_data(MPU6050_ADDR, MPU6050_PWR_MGMT_1, 0)
                time.sleep(0.01)
                ax_high = bus.read_byte_data(MPU6050_ADDR, MPU6050_ACCEL_XOUT_H)
                ax_low = bus.read_byte_data(MPU6050_ADDR, MPU6050_ACCEL_XOUT_H + 1)
                ax = (ax_high << 8) | ax_low
                print(f"CH{channel}: OK Accel X = {ax}")
            except OSError as error:
                failures += 1
                print(f"CH{channel}: FAIL {error}")
    finally:
        bus.close()

    print(f"Probe finished: tested={len(channels)} failures={failures}")


if __name__ == "__main__":
    main()
