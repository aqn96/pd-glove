import argparse
import time

import smbus2

TCA9548A_ADDR = 0x70
MPU6050_ADDR = 0x68
MPU6050_PWR_MGMT_1 = 0x6B
MPU6050_ACCEL_XOUT_H = 0x3B
<<<<<<< HEAD
=======
MPU6050_WHO_AM_I = 0x75
MPU6050_WHO_AM_I_EXPECTED = 0x68
COMPATIBLE_WHO_AM_I = {
    0x68: "MPU6050/MPU6000",
    0x70: "MPU6500-class clone",
    0x71: "MPU9250/MPU9255-class clone",
}
>>>>>>> 7428047 (improve test_imus.py test)


def parse_channels(raw: str) -> list[int]:
    channels = []
    for token in raw.split(","):
        channel = int(token.strip())
        if channel < 0 or channel > 7:
            raise ValueError("Channel values must be in range 0..7")
        channels.append(channel)
    return channels


<<<<<<< HEAD
=======
def select_mux_channel(bus: smbus2.SMBus, channel: int) -> None:
    bus.write_byte(TCA9548A_ADDR, 1 << channel)


def disable_all_mux_channels(bus: smbus2.SMBus) -> None:
    bus.write_byte(TCA9548A_ADDR, 0x00)


def read_who_am_i(bus: smbus2.SMBus) -> int:
    return bus.read_byte_data(MPU6050_ADDR, MPU6050_WHO_AM_I)


def who_am_i_is_compatible(who_am_i: int) -> bool:
    return who_am_i in COMPATIBLE_WHO_AM_I


def scan_channels(bus: smbus2.SMBus, channels: list[int]) -> None:
    print("Scanning mux channels for MPU6050 (0x68)...")
    for channel in channels:
        try:
            select_mux_channel(bus, channel)
            time.sleep(0.01)
            who_am_i = read_who_am_i(bus)
            if who_am_i_is_compatible(who_am_i):
                chip_label = COMPATIBLE_WHO_AM_I[who_am_i]
                print(f"CH{channel}: found 0x68 (WHO_AM_I=0x{who_am_i:02X} {chip_label})")
            else:
                print(f"CH{channel}: unexpected WHO_AM_I=0x{who_am_i:02X}")
        except OSError:
            print(f"CH{channel}: not found")


>>>>>>> 7428047 (improve test_imus.py test)
def main() -> None:
    parser = argparse.ArgumentParser(description="Quick MPU6050 per-channel check through TCA9548A.")
    parser.add_argument(
        "--channels",
        type=str,
        default="0,1,2,3,4",
        help="Comma-separated mux channels to probe (default: 0,1,2,3,4).",
    )
<<<<<<< HEAD
=======
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Only scan channels for presence at 0x68 without reading accel values.",
    )
    parser.add_argument(
        "--scan",
        nargs="?",
        const="only",
        choices=["only"],
        help="Alias for --scan-only. Supports legacy usage: --scan only.",
    )
>>>>>>> 7428047 (improve test_imus.py test)
    args = parser.parse_args()

    channels = parse_channels(args.channels)
    bus = smbus2.SMBus(1)
    failures = 0

    try:
<<<<<<< HEAD
        for channel in channels:
            try:
                bus.write_byte_data(TCA9548A_ADDR, 0, 1 << channel)
                time.sleep(0.01)
=======
        if args.scan_only or args.scan == "only":
            scan_channels(bus, channels)
            return

        for channel in channels:
            try:
                select_mux_channel(bus, channel)
                time.sleep(0.01)
                who_am_i = read_who_am_i(bus)
                if not who_am_i_is_compatible(who_am_i):
                    raise OSError(f"unexpected WHO_AM_I=0x{who_am_i:02X}")
>>>>>>> 7428047 (improve test_imus.py test)
                bus.write_byte_data(MPU6050_ADDR, MPU6050_PWR_MGMT_1, 0)
                time.sleep(0.01)
                ax_high = bus.read_byte_data(MPU6050_ADDR, MPU6050_ACCEL_XOUT_H)
                ax_low = bus.read_byte_data(MPU6050_ADDR, MPU6050_ACCEL_XOUT_H + 1)
                ax = (ax_high << 8) | ax_low
<<<<<<< HEAD
                print(f"CH{channel}: OK Accel X = {ax}")
=======
                chip_label = COMPATIBLE_WHO_AM_I[who_am_i]
                print(f"CH{channel}: OK WHO_AM_I=0x{who_am_i:02X} ({chip_label}) Accel X = {ax}")
>>>>>>> 7428047 (improve test_imus.py test)
            except OSError as error:
                failures += 1
                print(f"CH{channel}: FAIL {error}")
    finally:
<<<<<<< HEAD
=======
        disable_all_mux_channels(bus)
>>>>>>> 7428047 (improve test_imus.py test)
        bus.close()

    print(f"Probe finished: tested={len(channels)} failures={failures}")


if __name__ == "__main__":
    main()
