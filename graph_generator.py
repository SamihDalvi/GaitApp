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

max = 0
for line in data_storage:
    for value in line:
        if value > max:
            max = value

with open('max_force.txt', 'w') as file:
    file.write(str(max) + ' N')

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

# Average force for each sensor
toe_force = sum(data_storage[0]) / len(data_storage[0])
medial_heel_force = sum(data_storage[1]) / len(data_storage[1])
lateral_heel_force = sum(data_storage[3]) / len(data_storage[3])

# Define a threshold for inversion and eversion detection
force_threshold = 20  # 20N difference to detect inversion or eversion

# Detect foot position
if lateral_heel_force - medial_heel_force > force_threshold:
    foot_position = "Inversion"
elif medial_heel_force - lateral_heel_force > force_threshold:
    foot_position = "Eversion"
else:
    foot_position = "Normal"

# Save the detected foot position to a file
with open('foot_position.txt', 'w') as file:
    file.write(foot_position)


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/start-analysis':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Starting Analysis')
            os.system('sh run.sh')  # Make sure the path to run.sh is correct
        else:
            super().do_GET()

def start_server():
    with socketserver.TCPServer(("", 8000), Handler) as httpd:
        print("serving at port", 8000)
        httpd.serve_forever()

# Start the server in a new thread
threading.Thread(target=start_server).start()
