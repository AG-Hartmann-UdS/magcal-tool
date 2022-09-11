# Magnetic Calibration Tool

## Introduction
Triaxial magnetic sensor calibration tool written in Tkinter. Performs magnetometer calibration from a 
set of data using Merayo technique with a non iterative algoritm [[1]](#1). Based on the octave scripts from [this](https://github.com/paynterf/MagCalTool) repository.

## Basic tutorial
- Flash an MCU device with a script that outputs the x, y and z components of the magnetic field measured by
a triaxial magnetometer. 
- Set the file and folder names for storing the collected calibration data.
- Select correct baud rate and serial port name. Connect to the serial port of the arduino device.
- Click "Open Port" and start collecting data by rotating the sensor in all possible orientations until an approximate sphere or ellipsoid is formed by the data. 
Then click "Close Port" to end the data collection.
- Click on calibrate to estimate the soft iron calibration matrix and the offset vector. Resolve any errors by collecting some more data
and click "Calibration". The new matrix should be displayed on the tool.
- Clicking "Save" outputs the data into a file.

More features to follow.

## References
<a id="1">[1]</a> 
J.Merayo et al. "Scalar calibration of vector magnemoters"
Meas. Sci. Technol. 11 (2000) 120-132.
