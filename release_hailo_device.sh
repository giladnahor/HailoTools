#!/bin/bash
# Define Hailo device
HAILO_DEVICE="/dev/hailo0"
# Find and kill any processes using the Hailo device
for pid in $(sudo lsof -t $HAILO_DEVICE); do
  echo "Terminating process $pid using $HAILO_DEVICE"
  sudo kill -9 $pid
done
echo "All processes using $HAILO_DEVICE have been terminated."
