#!/usr/bin/env python3

import time
try:
    from hailo_platform import Device
except ImportError:
    print("ImportError: The module 'hailo_platform' could not be imported. Please ensure that you have the 'pyhailort' or 'TAPPAS' virtual environments activated.")

def _run_periodic(delay=1):
    device_infos = Device.scan()
    targets = [Device(di) for di in device_infos]
    for i, target in enumerate(targets):
        target.control.stop_power_measurement()
        target.control.set_power_measurement()
        target.control.start_power_measurement()
    try:
        while True:
            for i, target in enumerate(targets):
                time.sleep(delay)
                power = target.control.get_power_measurement().average_value
                temp = target.control.get_chip_temperature().ts0_temperature
                print('[{}] {:.3f}W {:.3f}C'.format(device_infos[i], power, temp))
                if i == len(targets) - 1:  # If this is the last target
                    print('\033[{}A'.format(len(targets)), end='')  # Move the cursor up
    except KeyboardInterrupt:
        print('-I- Received keyboard interrupt, exiting')

    for i, target in enumerate(targets):
        target.control.stop_power_measurement()

if __name__ == "__main__":
    _run_periodic()
