import smbus2
import time

bus = smbus2.SMBus(1)

for channel in range(5):
    bus.write_byte_data(0x70, 0, 1 << channel)
    time.sleep(0.01)
    bus.write_byte_data(0x68, 0x6B, 0)
    time.sleep(0.01)
    ax_high = bus.read_byte_data(0x68, 0x3B)
    ax_low = bus.read_byte_data(0x68, 0x3C)
    ax = (ax_high << 8) | ax_low
    print(f'Channel {channel}: Accel X = {ax}')
