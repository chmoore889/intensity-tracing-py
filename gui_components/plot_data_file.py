import os
import struct

import matplotlib.pyplot as plt


def get_recent_intensity_tracing_file():
    data_folder = os.path.join(os.environ["USERPROFILE"], ".flim-labs", "data")
    files = [f for f in os.listdir(data_folder) if f.startswith("intensity-tracing")]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(data_folder, x)), reverse=True)
    return os.path.join(data_folder, files[0])


file_path = get_recent_intensity_tracing_file()
print("Using data file: " + file_path)
# file_path = "INSERT DATA FILE PATH HERE" # You can also manually insert the path to the data file here

times = []

with open(file_path, 'rb') as f:
    # first 4 bytes must be IT01
    if f.read(4) != b'IT02':
        print("Invalid data file")
        exit(0)

    # read metadata from file
    (json_length,) = struct.unpack('I', f.read(4))
    null = None
    metadata = eval(f.read(json_length).decode("utf-8"))

    if "channels" in metadata and metadata["channels"]:
        print("Enabled channels: " + (", ".join(["Channel " + str(ch + 1) for ch in metadata["channels"]])))

    if "bin_width_micros" in metadata and metadata["bin_width_micros"] is not None:
        print("Bin width: " + str(metadata["bin_width_micros"]) + "\u00B5s")

    if "acquisition_time_millis" in metadata and metadata["acquisition_time_millis"] is not None:
        print("Acquisition time: " + str(metadata["acquisition_time_millis"] / 1000) + "s")

    if "laser_period_ns" in metadata and metadata["laser_period_ns"] is not None:
        print("Laser period: " + str(metadata["laser_period_ns"]) + "ns")

    channel_lines = [[] for _ in range(len(metadata["channels"]))]

    number_of_channels = len(metadata["channels"])
    channel_values_unpack_string = 'I' * number_of_channels
    bin_width_seconds = metadata["bin_width_micros"] / 1000000

    while True:
        data = f.read(4 * number_of_channels + 8)
        if not data:
            break
        (time,) = struct.unpack('d', data[:8])
        channel_values = struct.unpack(channel_values_unpack_string, data[8:])
        for i in range(len(channel_lines)):
            channel_lines[i].append(channel_values[i])
        times.append(time)
        
    
    print("TOTAL COUNTS:")    
    print(len(channel_lines[0]))
    print("FIRST 100 TIME NS:")
    print(times[:100])
    print("LAST 100 TIME NS:")
    print(times[-100:])
        

    
    # Plot data
    for i in range(len(metadata["channels"])):
        channel_line = channel_lines[i]
        plt.plot(
            times,
            channel_line,
            label="Channel " + str(metadata["channels"][i] + 1),
            linewidth=0.5
        )

    # Set plot title with metadata information
    title_str = 'Bin Width: {} us, Laser Period: {} ns'.format(
        metadata['bin_width_micros'],
        metadata['laser_period_ns']
    )

    if metadata['acquisition_time_millis'] is not None:
        title_str += ', Acquisition Time: {} s'.format(metadata['acquisition_time_millis'] / 1000)

    plt.title(title_str)

    # Set x and y axis labels
    plt.xlabel("Time (s)")
    plt.ylabel("Intensity (counts)")

    # Display grid
    plt.grid(True)

    # Set legend
    plt.legend(bbox_to_anchor = (1.05, 1), fancybox=True, shadow=True)
    plt.tight_layout()


    # Show the plot
    plt.show()