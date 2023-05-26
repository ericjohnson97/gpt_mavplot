
import matplotlib.pyplot as plt
from pymavlink import mavutil

# Open the MAVLink log file
mlog = mavutil.mavlink_connection('data/2023-01-04 20-51-25.tlog')

# Initialize lists to store the data
time_stamps = []
latitudes = []
longitudes = []
altitudes = []

# Loop through the log file and extract the data
while True:
    msg = mlog.recv_match()
    if not msg:
        break
    if msg.get_type() == 'GLOBAL_POSITION_INT':
        time_stamps.append(msg.time_boot_ms / 1000.0)
        latitudes.append(msg.lat / 1e7)
        longitudes.append(msg.lon / 1e7)
        altitudes.append(msg.alt / 1000.0)

# Plot the data
plt.plot(time_stamps, latitudes)
plt.xlabel('Time (s)')
plt.ylabel('Latitude')
plt.title('Aircraft Position Over Time')
plt.show()

plt.plot(time_stamps, longitudes)
plt.xlabel('Time (s)')
plt.ylabel('Longitude')
plt.title('Aircraft Position Over Time')
plt.show()

plt.plot(time_stamps, altitudes)
plt.xlabel('Time (s)')
plt.ylabel('Altitude (km)')
plt.title('Aircraft Position Over Time')
plt.show()
