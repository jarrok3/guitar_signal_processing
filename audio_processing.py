# Wgranie odpowiednich bibliotek
import numpy as np
import pyaudio as pau
import struct
import matplotlib.pyplot as plt
import time

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
    """Obsługa wydarzenia - działa gdy zostanie naciśnięty przycisk na klawiaturze"""
    print("Klawisz naciśnięty, zamykam okno.")
    plt.close()
    

if __name__ == "__main__": 
    p = pau.PyAudio() # deklaracja obiektu z biblioteki PyAudio klasy PyAudio
    
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    ) # otwarcie kanalu glosowego
    
    print("Nagrywanie...") # informacja do terminala
    
    fig,ax = plt.subplots(figsize=(18,8)) # tworzy wykres "fig" z pojedynczą osią odciętych "ax"
    fig.canvas.mpl_connect("key_press_event", on_key) # połączenie wykresu z funkcją on_key
    
    x = np.arange(0,2*CHUNK,2) # definiuje wartości (koordynaty) dostępne na osi odciętych, od 0 do 2024 z odstępem co 2 próbki
    
    line, = ax.plot(x, np.random.rand(CHUNK),'r') # inicjalizacja linii reprezentującej przebieg sygnału, ustawienie koloru czerwonego
    ax.set_ylim(-32768,32767) # definicja ograniczeń wyświetlanych wartości na osi rzędnych, odpowiadająca formatowi 16-bitowemu
    ax.set_xlim = (0,CHUNK) # definicja ograniczeń wyświetlanych wartości na osi odciętych
    ax.set_ylabel('Amplituda dźwięku [-]')
    ax.set_xlabel('Próbki [-]')
    
    #Konfiguracja wyświetlanych linii na wykresie
    for decade in range(-32000, 32000, 4000):
        ax.axhline(y=decade, color='gray', linestyle='-', linewidth=0.5)
    for semidecade in range(-32000, 32000, 1000):
        ax.axhline(y=semidecade, color='lightgray', linestyle='-', linewidth=0.33)
    for xdecade in range(0,2*CHUNK,120):
        ax.axvline(x=xdecade,color='lightgray',linestyle='-', linewidth=0.33)
    
    fig.show() # wyświetlenie okna z wykresem

    try:
        while plt.fignum_exists(fig.number):
            data = stream.read(CHUNK) # sczytanie danych z otwartego kanału głosowego w pojedynczej iteracji
            dataInt = struct.unpack(str(CHUNK) + 'h', data) # konwersja danych z bitów na tabelę zawierającą 16-bitowe integery odpowiadające każdej z próbek
            
            line.set_ydata(dataInt) # ustawienie wartości funkcji na przetworzone dane, dla zainicjowaniej wcześniej czerwonej linii
            
            fig.canvas.draw() # zaktualizowanie danych na wykresie nowymi danymi
            fig.canvas.flush_events() # odświerzenie wykresu dla wyświetlania w czasie rzeczywistym
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

