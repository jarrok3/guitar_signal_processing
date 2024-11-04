import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Parameters for audio stream
CHUNK = 1024  # Number of samples per frame
FORMAT = pyaudio.paInt16  # Format of audio stream
CHANNELS = 1  # Single channel for mono audio
RATE = 44100  # Sample rate (samples per second)

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)

# Function to update the plot in real-time
def update_plot(frame):
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_data = np.frombuffer(data, dtype=np.int16)

    # Perform FFT
    fft_data = np.fft.fft(audio_data)
    frequencies = np.fft.fftfreq(len(fft_data), 1 / RATE)

    # Update line data for the plot (positive frequency half)
    line.set_ydata(np.abs(fft_data[:len(fft_data) // 2]))
    return line,

# Set up Matplotlib figure and plot
fig, ax = plt.subplots()
x = np.fft.fftfreq(CHUNK, 1 / RATE)[:CHUNK // 2]
y = np.zeros(CHUNK // 2)
line, = ax.plot(x, y)

ax.set_title('Real-Time Frequency Spectrum')
ax.set_xlabel('Frequency (Hz)')
ax.set_ylabel('Amplitude')
ax.set_xlim(0, RATE // 2)
ax.set_ylim(0, 10000)  # Adjust as necessary for your input amplitude range

# Start animation
ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=50)
plt.show()

# Close stream after the plot window is closed
stream.stop_stream()
stream.close()
p.terminate()
