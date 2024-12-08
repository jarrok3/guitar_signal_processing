# Wgranie odpowiednich bibliotek
import numpy as np
import pyaudio as pau
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import time

# Deklaracja zmiennych globalnych
CHUNK = 1024 * 4 # Ilość próbek przetwarzana przy każdej operacji "read", 
'''
The CHUNK size determines how much data is read per stream.read() call. Larger chunks reduce CPU load but increase latency, while smaller chunks allow more responsive and real-time data handling but can be more demanding on CPU.
For audio analysis or effects (like a Wah-Wah pedal), a smaller CHUNK (e.g., 512 or 1024) might be ideal for responsiveness, whereas for simple recording, a larger CHUNK (e.g., 4096) might improve stability.
'''
FORMAT = pau.paInt16 # ustawienie formatu hexadecymalnego 
CHANNELS = 1 # Ilość kanałów audio, 1 dla dźwięku MONO, 2 dla STEREO
RATE = 48000 # [Hz] określenie częstotliwości próbkowania

# deklaracja zmiennej pomocniczej
last_maxdb_update = time.time()

def on_key(event):
    """W wypadku zarejestrowania zdarzenia wyłącza wyświetlanie wykresów (zamyka je)

    Args:
        event (matplotlib.backend_bases.KeyEvent): Wykryte wydarzenie
    """
    print("Klawisz naciśnięty, zamykam okno.")
    
    plt.close()

def amplitude_to_db(amplitude):
    """Konwersja amplitudy w formacie int do decybeli

    Args:
        amplitude (paInt16): wartość amplitudy wyznaczona w formacie integer16 (-32768, 32768)

    Returns:
        amplitude (decibels): wartość amplitudy wyznaczona w decybelach po konwersji
    """
    # zabezpieczeni
    # e przed zwróceniem wartości 0, nieakceptowalnej do użycia w logarytmie
    amplitude = np.maximum(amplitude / 32767.0, 1e-9) # normalizacja wartości amplitudy z formatu 16bit (-32768,32767) do zakresu (-1,1)
    return 20 * np.log10(amplitude)
                         
def generate_whitenoise(duration=60):
    """Tworzy biały szum o długości trwania duration (podstawowo 60 sekund)

    Args:
        duration (int, optional): _description_. Jeśli nie zadeklarowano inaczej, podstawowo trwa 60 sekund.

    Returns:
        _type_: zwraca sygnał typu biały szum
    """
    white_noise = np.random.randn(RATE*duration)
    return (white_noise * 32767).astype(np.int16)
                   
def update_plot(frame):
    """Aktualizuje wyświetlanie wykresów w każdej klatce

    Args:
        frame (_type_): _description_

    Returns:
        waveform_line: _description_,s
        spectrum_line: _description_
    """
    global last_maxdb_update
    
    # Sczytanie danych z pojedynczej klatki
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
    # Zabezpieczenie przed brakiem/niepoprawnym czytaniem danych ze źródła audio (wyzerowanie wykresów)
    except IOError as err:
        print(f'Wystąpił problem ze sczytaniem sygnału audio: {err}')
        waveform_line.set_ydata(np.zeros)
        spectrum_line.set_ydata(np.zeros)
        return waveform_line,spectrum_line
    
    audio_data = np.frombuffer(data, dtype=np.int16) # konwersja danych do tablicy 16-bitowych integerów
    
    # Przeprowadzenie szybkiej transformaty Fouriera
    fft_data = np.fft.fft(audio_data) # przejście z domeny czasu na domenę częstotliwości (liczby złożone)
    #frequencies = np.fft.fftfreq(len(fft_data), 1 / RATE)

    # Konwersja danych do decybeli
    magnitude = np.abs(fft_data[:len(fft_data) // 2])
    db_magnitude = amplitude_to_db(magnitude)
    
    # Aktualizacja maksymalnego zarejestrowanego poziomu natężenia dźwięku co sekundę
    current_time = time.time()
    if current_time - last_maxdb_update >= 1.0:
        max_db = np.max(db_magnitude)
        
        last_maxdb_update = current_time
    
    # Aktualizacja pierwszego wykresu
    waveform_line.set_ydata(audio_data)

    # Aktualizacja drugiego wykresu
    spectrum_line.set_ydata(db_magnitude)
    return waveform_line, spectrum_line

if __name__ == "__main__": 
    p = pau.PyAudio() # deklaracja oraz inicjalizacja obiektu z biblioteki PyAudio klasy PyAudio
    
    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        ) # otwarcie kanalu glosowego
    except OSError as err:
        print(f'Podłącz urządzenie audio. Wystąpił błąd: {err}')
        # zakończenie działania programu
        quit()
        
    
    print("Nagrywanie...") # informacja do terminala
    
    fig,(ax1,ax2) = plt.subplots(2,1,figsize=(18,12)) # tworzy rysunek "fig", zawierający dwa wykresy
    fig.canvas.mpl_connect("key_press_event", on_key) # połączenie "fig" z funkcją on_key

    # # Konfiguracja wykresu przebiegu sygnału
    # Zainicjowanie osi
    x_waveform = np.arange(0, 2*CHUNK,2) # ustalenie dostępnych wartości na osi odciętych
    y_waveform = np.zeros(CHUNK)
    
    # Zainicjowanie linii odwzorowującej przebieg sygnału
    waveform_line, = ax1.plot(x_waveform, y_waveform)
    
    # Edycja wykresu
    ax1.set_title('Przebieg sygnału audio w czasie rzeczywistym')
    ax1.set_xlabel('Próbki [-]')
    ax1.set_ylabel('Amplituda [-]')
    ax1.set_xlim(0, CHUNK)
    ax1.set_ylim(-4096, 4096) # ograniczenie na osi rzędnych 
    
    # Dalsza konfiguracja wyglądu wykresu
    for decade in range(-4096, 4096, 128):
        ax1.axhline(y=decade, color='gray', linestyle='-', linewidth=0.5)
    for semidecade in range(-4096, 4096, 512):
        ax1.axhline(y=semidecade, color='lightgray', linestyle='-', linewidth=0.33)
    for xdecade in range(0,4*CHUNK,128):
        ax1.axvline(x=xdecade,color='gray',linestyle='-', linewidth=0.33)
    
    # # Konfiguracja wykresu częstotliwości f w zależności od poziomu natężenia L
    # Zainicjowanie osi
    x_spectrum = np.fft.fftfreq(CHUNK, 1 / RATE)[:CHUNK // 2]
    y_spectrum = np.zeros(CHUNK // 2)
    
    # Zainicjowanie linii odwzorowującej spektrum częstotliwości sygnału
    spectrum_line, = ax2.semilogx(x_spectrum, y_spectrum)
    
    # Edycja wykresu
    ax2.set_title('Analiza spektralna przebiegu sygnału')
    ax2.set_xlabel('Częstotliwość f(Hz)')
    ax2.set_ylabel('Poziom natężenia dźwięku L(dB)')
    ax2.set_xlim(20, RATE / 2)
    ax2.set_ylim(-50, 60)  # Badany zakres częstotliwości
    
    # Dalsza konfiguracja wyglądu wykresu
    for decade in range(-50, 60, 10):
        ax2.axhline(y=decade, color='darkgray', linestyle='-', linewidth=0.5)
    for semidecade in range(-45, 65, 10):
        ax2.axhline(y=semidecade, color='gray', linestyle='-', linewidth=0.33)
    for quarterdecade in range(-42,57,5):
        ax2.axhline(y=quarterdecade,color='lightgray',linestyle='--',linewidth=0.33)
    for xdecade in range(0,RATE//2,100):
        ax2.axvline(x=xdecade,color='lightgray',linestyle='-', linewidth=0.33)
        
    try:
        while plt.fignum_exists(fig.number):
            ani = animation.FuncAnimation(fig, update_plot, blit=False, interval=50, cache_frame_data=False) # zabezpieczenie przed używaniem nadmiernej ilości pamięci poprzez ustawienie cache_frame_data na wartość False
            plt.show()
    except KeyboardInterrupt:
        stream.close() # zamknięcie kanału głosowego w wypadku naciśnięcia klawisza klawiatury przez użytkownika
        print("Zakonczono analize sygnalu")
    finally:
        p.terminate() # zapewnienie stałego zamknięcia kanału głosowego po zakończeniu pracy programu

'''
Known problems:
    OSError: [Errno -9981] Input overflowed
For Chunk size 512, the system cannot handle the sampling quickly enough, and the buffer gets overflown
Had to change chunk size to 1024 to tackle the problem
'''

