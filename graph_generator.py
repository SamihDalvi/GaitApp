import socket
import matplotlib.pyplot as plt
import time
import numpy as np

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

# Close the socket
s.close()

def moving_average(data, window_size):
    """Compute the moving average of the given data."""
    weights = np.ones(window_size) / window_size
    return np.convolve(data, weights, mode='valid')

# Define the window size for the moving average
window_size = 5

# Plot the data
plt.figure(figsize=(9, 5))
for i in range(4):
    smoothed_data = moving_average(data_storage[i], window_size)
    plt.plot(smoothed_data, label=f'FSR {i}')

plt.title('Smoothed FSR Data Over Time')
plt.xlabel('Time (s)')
plt.ylabel('Force Reading')
plt.legend()
plt.tight_layout()

# Save the figure
plt.savefig('realtimegraph.png')
plt.savefig('realtimegraphextra.png')

