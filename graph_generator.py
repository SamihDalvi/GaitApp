import socket
import matplotlib.pyplot as plt
import time
import numpy as np

import http.server
import socketserver
import threading
import os

# Setup the socket client
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '192.168.137.91'  # Raspberry Pi's IP address
port = 12345
s.connect((host, port))

# Initialize data storage
data_storage = [[] for _ in range(4)]  # For storing data from each FSR

start_time = time.time()
duration = 10  # duration in seconds to collect data

# Collect data for 10 seconds
while time.time() - start_time < duration:
    data = s.recv(1024).decode('ascii').split(',')
    if len(data) == 4:
        for i in range(4):
            data_storage[i].append(float(data[i]))

max_force = 0
max_sensor_index = 0
for i, line in enumerate(data_storage):
    for value in line:
        if value > max_force:
            max_force = value
            max_sensor_index = i

max_sensor_label = ["Toe Sensor", "Lateral Heel Sensor","Backheel Sensor", "Medial Heel Sensor"][max_sensor_index]
with open('max_force.txt', 'w') as file:
    file.write(f'Max Force: {max_force} N \n'  +  max_sensor_label )

# Close the socket
s.close()

# Plot the data
plt.figure(figsize=(9, 5))
for i in range(4):
    plt.plot(data_storage[i], label=["Toe Sensor", "Lateral Heel Sensor","Backheel Sensor", "Medial Heel Sensor"][i])

plt.title('Smoothed FSR Data Over Time')
plt.xlabel('Time (s)')
plt.ylabel('Force Reading')
plt.legend()
plt.legend(loc='upper left')
plt.tight_layout()

# Save the figure
plt.savefig('realtimegraph.png')
plt.savefig('realtimegraphextra.png')

# Average force for each sensor
toe_force = sum(data_storage[0]) / len(data_storage[0])
medial_heel_force = sum(data_storage[3]) / len(data_storage[3])
lateral_heel_force = sum(data_storage[1]) / len(data_storage[1])
back_heel_force = sum(data_storage[2]) / len(data_storage[2])


# Define a threshold for inversion and eversion detection
force_threshold = 40  # 20N difference to detect inversion or eversion

# Detect foot position
if (lateral_heel_force - medial_heel_force) > force_threshold and medial_heel_force < 50 :
    foot_position = "Inversion"
elif medial_heel_force - lateral_heel_force > force_threshold and lateral_heel_force < 60:
    foot_position = "Eversion"
else:
    foot_position = "Normal"

# Save the detected foot position to a file
with open('foot_position.txt', 'w') as file:
    file.write(foot_position)

# Analysis
max_force = 0
max_sensor_index = 0
heel_strikes_times = []
previous_force = 0
heel_strike_threshold = 50  # Threshold to detect heel strike, needs calibration
stride_times = []

for i, force in enumerate(data_storage[2]):  # Assuming data_storage[2] is the middle heel sensor
    if force > max_force:
        max_force = force
        max_sensor_index = 2

    # Detect heel strike
    if force > heel_strike_threshold and previous_force <= heel_strike_threshold:
        current_time = start_time + i * (duration / len(data_storage[2]))
        heel_strikes_times.append(current_time)
        if len(heel_strikes_times) > 1:
            stride_time = heel_strikes_times[-1] - heel_strikes_times[-2]
            stride_times.append(stride_time)

    previous_force = force

# Calculate and save average stride time
if stride_times:
    average_stride_time = sum(stride_times) / len(stride_times)
    with open('average_stride_time.txt', 'w') as file:
        file.write(f'Average Stride Time: {average_stride_time:.2f} s\n')
