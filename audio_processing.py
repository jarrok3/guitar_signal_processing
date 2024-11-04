# Wgranie odpowiednich bibliotek
import numpy as np
import pyaudio as pau
import matplotlib.animation as animation
import matplotlib.pyplot as plt


# Deklaracja zmiennych globalnych
CHUNK = 1024 # Ilość próbek przetwarzana przy każdej operacji "read", 
'''
The CHUNK size determines how much data is read per stream.read() call. Larger chunks reduce CPU load but increase latency, while smaller chunks allow more responsive and real-time data handling but can be more demanding on CPU.
For audio analysis or effects (like a Wah-Wah pedal), a smaller CHUNK (e.g., 512 or 1024) might be ideal for responsiveness, whereas for simple recording, a larger CHUNK (e.g., 4096) might improve stability.
'''
FORMAT = pau.paInt16 # ustawienie formatu hexadecymalnego 
CHANNELS = 1 # Ilość kanałów audio, 1 dla dźwięku MONO, 2 dla STEREO
RATE = 48000 # [Hz] określenie częstotliwości próbkowania

def on_key(event):
    """W wypadku zarejestrowania zdarzenia wyłącza wyświetlanie wykresów (zamyka je)

    Args:
        event (matplotlib.backend_bases.KeyEvent): Wykryte wydarzenie
    """
    print("Klawisz naciśnięty, zamykam okno.")
    
    plt.close()
    
def update_plot(frame):
    """Aktualizuje wyświetlanie wykresów w każdej klatce

    Args:
        frame (_type_): _description_

    Returns:
        waveform_line: _description_,s
        spectrum_line: _description_
    """
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_data = np.frombuffer(data, dtype=np.int16)

    # Perform FFT
    fft_data = np.fft.fft(audio_data)
    frequencies = np.fft.fftfreq(len(fft_data), 1 / RATE)

    # Update line data for the first plot (waveform)
    waveform_line.set_ydata(audio_data)

    # Update line data for the second plot (frequency spectrum)
    spectrum_line.set_ydata(np.abs(fft_data[:len(fft_data) // 2]))
    return waveform_line, spectrum_line

if __name__ == "__main__": 
    p = pau.PyAudio() # deklaracja oraz inicjalizacja obiektu z biblioteki PyAudio klasy PyAudio
    
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    ) # otwarcie kanalu glosowego
    
    print("Nagrywanie...") # informacja do terminala
    
    fig,(ax1,ax2) = plt.subplots(2,1,figsize=(18,12)) # tworzy rysunek "fig", zawierający dwa wykresy
    fig.canvas.mpl_connect("key_press_event", on_key) # połączenie "fig" z funkcją on_key

    # # Konfiguracja wykresu przebiegu sygnała
    # Zainicjowanie osi
    x_waveform = np.arange(0, CHUNK) # ustalenie dostępnych wartości na osi odciętych
    y_waveform = np.zeros(CHUNK)
    
    # Zainicjowanie linii odwzorowującej przebieg sygnału
    waveform_line, = ax1.plot(x_waveform, y_waveform)
    
    # Edycja wykresu
    ax1.set_title('Przebieg sygnału audio w czasie rzeczywistym')
    ax1.set_xlabel('Próbki [-]')
    ax1.set_ylabel('Amplituda [-]')
    ax1.set_xlim(0, CHUNK)
    ax1.set_ylim(-32768, 32767) # ograniczenie na osi rzędncych ze względu na format paInt16 sygnału wejściowego
    
    # Dalsza konfiguracja wyglądu wykresu
    for decade in range(-32000, 32000, 4000):
        ax1.axhline(y=decade, color='gray', linestyle='-', linewidth=0.5)
    for semidecade in range(-32000, 32000, 1000):
        ax1.axhline(y=semidecade, color='lightgray', linestyle='-', linewidth=0.33)
    for xdecade in range(0,2*CHUNK,120):
        ax1.axvline(x=xdecade,color='lightgray',linestyle='-', linewidth=0.33)
    
    # # Konfiguracja wykresu częstotliwości f w zależności od poziomu natężenia L
    # Zainicjowanie osi
    x_spectrum = np.fft.fftfreq(CHUNK, 1 / RATE)[:CHUNK // 2]
    y_spectrum = np.zeros(CHUNK // 2)
    
    # Zainicjowanie linii odwzorowującej spektrum częstotliwości sygnału
    spectrum_line, = ax2.plot(x_spectrum, y_spectrum)
    
    # Edycja wykresu
    ax2.set_title('Analiza spektralna przebiegu sygnału')
    ax2.set_xlabel('Częstotliwość (Hz)')
    ax2.set_ylabel('Amplituda')
    ax2.set_xlim(0, RATE // 2)
    ax2.set_ylim(100, 10000)  # Badany zakres częstotliwości
    
    try:
        while plt.fignum_exists(fig.number):
            ani = animation.FuncAnimation(fig, update_plot, blit=True, interval=50)
            plt.show()
    except KeyboardInterrupt:
        stream.close() # zamknięcie kanału głosowego w wypadku naciśnięcia klawisza klawiatury przez użytkownika
        print("Zakonczono analize sygnalu")
    
    p.terminate() # usuniecie obiektu p klasy PyAudio

'''
Known problems:
    OSError: [Errno -9981] Input overflowed
For Chunk size 512, the system cannot handle the sampling quickly enough, and the buffer gets overflown
Had to change chunk size to 1024 to tackle the problem

    struct.error
For incorrect format handling (paint16 equals 2 bytes long sample)
'''

