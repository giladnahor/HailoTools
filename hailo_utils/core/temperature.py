#!/usr/bin/env python3
"""
Temperature and power monitoring utilities for Hailo devices.

This module provides functions to monitor temperature and power consumption
of Hailo AI hardware devices.
"""

import time
from typing import List, Dict, Optional, Any

try:
    from hailo_platform import Device
    HAILO_AVAILABLE = True
except ImportError:
    HAILO_AVAILABLE = False
    Device = None


class HailoDeviceError(Exception):
    """Exception raised when Hailo device operations fail."""
    pass


def check_hailo_availability() -> bool:
    """
    Check if Hailo platform is available.
    
    Returns:
        bool: True if hailo_platform module is available, False otherwise.
    """
    return HAILO_AVAILABLE


def get_device_temperature() -> Dict[str, float]:
    """
    Get temperature readings from all available Hailo devices.
    
    Returns:
        dict: Dictionary mapping device info to temperature in Celsius.
        
    Raises:
        HailoDeviceError: If Hailo platform is not available or no devices found.
    """
    if not HAILO_AVAILABLE:
        raise HailoDeviceError(
            "Hailo platform not available. Please ensure that you have the "
            "'pyhailort' package installed or 'TAPPAS' virtual environment activated."
        )
    
    try:
        device_infos = Device.scan()
        if not device_infos:
            raise HailoDeviceError("No Hailo devices found")
        
        temperatures = {}
        for device_info in device_infos:
            device = Device(device_info)
            temp = device.control.get_chip_temperature().ts0_temperature
            temperatures[str(device_info)] = temp
            
        return temperatures
    except Exception as e:
        raise HailoDeviceError(f"Failed to get device temperature: {e}") from e


def get_device_power() -> Dict[str, float]:
    """
    Get power consumption readings from all available Hailo devices.
    
    Returns:
        dict: Dictionary mapping device info to power in Watts.
        
    Raises:
        HailoDeviceError: If Hailo platform is not available or measurement fails.
    """
    if not HAILO_AVAILABLE:
        raise HailoDeviceError(
            "Hailo platform not available. Please ensure that you have the "
            "'pyhailort' package installed or 'TAPPAS' virtual environment activated."
        )
    
    try:
        device_infos = Device.scan()
        if not device_infos:
            raise HailoDeviceError("No Hailo devices found")
        
        power_readings = {}
        devices = []
        
        # Initialize power measurement for all devices
        for device_info in device_infos:
            device = Device(device_info)
            device.control.stop_power_measurement()
            device.control.set_power_measurement()
            device.control.start_power_measurement()
            devices.append(device)
        
        # Get power readings
        for i, (device_info, device) in enumerate(zip(device_infos, devices)):
            power = device.control.get_power_measurement().average_value
            power_readings[str(device_info)] = power
            device.control.stop_power_measurement()
            
        return power_readings
    except Exception as e:
        raise HailoDeviceError(f"Failed to get device power: {e}") from e


def monitor_temperature(delay: float = 1.0, duration: Optional[float] = None) -> None:
    """
    Monitor temperature and power consumption of Hailo devices in real-time.
    
    Args:
        delay: Delay between measurements in seconds (default: 1.0).
        duration: Total monitoring duration in seconds. If None, monitor indefinitely.
        
    Raises:
        HailoDeviceError: If Hailo platform is not available or monitoring fails.
    """
    if not HAILO_AVAILABLE:
        raise HailoDeviceError(
            "Hailo platform not available. Please ensure that you have the "
            "'pyhailort' package installed or 'TAPPAS' virtual environment activated."
        )
    
    try:
        device_infos = Device.scan()
        if not device_infos:
            raise HailoDeviceError("No Hailo devices found")
        
        devices = []
        
        # Initialize power measurement for all devices
        for device_info in device_infos:
            device = Device(device_info)
            device.control.stop_power_measurement()
            device.control.set_power_measurement()
            device.control.start_power_measurement()
            devices.append(device)
        
        start_time = time.time()
        
        try:
            while True:
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    break
                
                for i, (device_info, device) in enumerate(zip(device_infos, devices)):
                    time.sleep(delay)
                    power = device.control.get_power_measurement().average_value
                    temp = device.control.get_chip_temperature().ts0_temperature
                    print(f'[{device_info}] {power:.3f}W {temp:.3f}°C')
                    
                    if i == len(devices) - 1:  # If this is the last device
                        # Move cursor up to overwrite previous output
                        print(f'\033[{len(devices)}A', end='')
                        
        except KeyboardInterrupt:
            print('\n-I- Received keyboard interrupt, exiting')
        
        # Clean up power measurement
        for device in devices:
            device.control.stop_power_measurement()
            
    except Exception as e:
        raise HailoDeviceError(f"Failed to monitor devices: {e}") from e


def main() -> None:
    """Command line interface for temperature monitoring."""
    try:
        monitor_temperature()
    except HailoDeviceError as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
