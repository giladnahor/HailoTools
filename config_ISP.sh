#!/bin/bash

# Change this to /dev/v4l-subdev2 or /dev/v4l-subdev3 if you get "unknown command" error
readonly V4L_DEVICE="/dev/v4l-subdev2"
readonly EXPOSURE_INCREMENT=100
readonly ANALOG_GAIN_INCREMENT=1
readonly DIGITAL_GAIN_INCREMENT=50


# Exposure values between 1 - 4400
readonly DEFAULT_EXPOSURE=4400
# Sensor gain values between 1 - 240
readonly DEFAULT_ANALOG_GAIN=40
# ISP gain enable values 0 or 1
readonly DEFAULT_DIGITAL_GAIN_ENABLED=0
# ISP gain values between 100 - 25999
readonly DEFAULT_DIGITAL_GAIN=100

exposure=$DEFAULT_EXPOSURE
analog_gain=$DEFAULT_ANALOG_GAIN
digital_gain_enabled=$DEFAULT_DIGITAL_GAIN_ENABLED
digital_gain=$DEFAULT_DIGITAL_GAIN

echo "Hailo-15 Low light demo config tool"
echo "Press q to exit and r for reset"
echo "Exposure     press x (value down) and X (value up)"
echo "Analog Gain  press a (value down) and A (value up)"
echo "Digital Gain press d (value down) and D (value up)"
echo

while true; 
do
    if [ $digital_gain_enabled = 1 ]
    then
        # \33[2K clear current line
        printf "\33[2K\rExposure: $exposure, Analog Gain: $analog_gain, Digital Gain: Enabled,  ISP Gain: $digital_gain"
    else
        printf "\33[2K\rExposure: $exposure, Analog Gain: $analog_gain, Digital Gain: Disabled, ISP Gain: $digital_gain"
    fi

    # -n 1 get one character, -t 0.1 timeout
    read -n 1 -t 0.1 input
    if [ "$input" = "q" ] || [ "$input" = "Q" ];
    then
        echo
        break
    fi

    if [ "$input" = "r" ] || [ "$input" = "R" ];
    then
        exposure=$DEFAULT_EXPOSURE
        analog_gain=$DEFAULT_ANALOG_GAIN
        digital_gain_enabled=$DEFAULT_DIGITAL_GAIN_ENABLED
        digital_gain=$DEFAULT_DIGITAL_GAIN    
        v4l2-ctl --set-ctrl exposure=$exposure -d $V4L_DEVICE
        v4l2-ctl --set-ctrl analogue_gain=$analog_gain -d $V4L_DEVICE
        v4l2-ctl -d /dev/video0 -c isp_dg_gain=$digital_gain
        v4l2-ctl -d /dev/video0 -c isp_dg_enable=$digital_gain_enabled
    fi

    if [ "$input" = "x" ];
    then
        exposure="$((exposure-$EXPOSURE_INCREMENT))"
        if [ "$exposure" -lt "1" ];
        then
            exposure=1
        fi
        v4l2-ctl --set-ctrl exposure=$exposure -d $V4L_DEVICE
    fi

    if [ "$input" = "X" ];
    then
        exposure="$((exposure+$EXPOSURE_INCREMENT))"
        if [ "$exposure" -gt "4400" ];
        then
            exposure=4400
        fi
        v4l2-ctl --set-ctrl exposure=$exposure -d $V4L_DEVICE
    fi

    if [ "$input" = "a" ];
    then
        analog_gain="$((analog_gain-$ANALOG_GAIN_INCREMENT))"
        if [ "$analog_gain" -lt "1" ];
        then
            analog_gain=1
        fi
        v4l2-ctl --set-ctrl analogue_gain=$analog_gain -d $V4L_DEVICE
    fi

    if [ "$input" = "A" ];
    then
        analog_gain="$((analog_gain+$ANALOG_GAIN_INCREMENT))"
        if [ "$analog_gain" -gt "240" ];
        then
            analog_gain=240
        fi
        v4l2-ctl --set-ctrl analogue_gain=$analog_gain -d $V4L_DEVICE
    fi

    if [ "$input" = "d" ];
    then
        digital_gain="$((digital_gain-$DIGITAL_GAIN_INCREMENT))"
        if [ "$digital_gain" -lt "100" ];
        then
            digital_gain=100
            digital_gain_enabled=0
            v4l2-ctl -d /dev/video0 -c isp_dg_enable=$digital_gain_enabled
        fi
        v4l2-ctl -d /dev/video0 -c isp_dg_gain=$digital_gain
    fi

    if [ "$input" = "D" ];
    then
        if [ "$digital_gain_enabled" = "0" ];
        then
            digital_gain=100
            digital_gain_enabled=1
            v4l2-ctl -d /dev/video0 -c isp_dg_enable=$digital_gain_enabled
        else
            digital_gain="$((digital_gain+$DIGITAL_GAIN_INCREMENT))"
            if [ "$digital_gain" -gt "25999" ];
            then
                digital_gain=25999
            fi
        fi
        v4l2-ctl -d /dev/video0 -c isp_dg_gain=$digital_gain
    fi
done