import numpy as np
import soundfile as sf
from scipy.signal import spectrogram, resample

# Configurações Padrão
SAMPLE_RATE = 44100
WINDOW_SIZE = 4096
OVERLAP_RATIO = 0.5

def load_audio_file(file_path):
    """
    Carrega um arquivo de áudio, converte para Mono e 44.1kHz, 
    e retorna as amostras como um array NumPy.
    Substituindo pydub por soundfile devido a problemas com Python 3.13
    """
    try:
        # soundfile lê como float entre -1 e 1 por padrão
        data, fs = sf.read(file_path)
        
        # Converte Stereo para Mono (média dos canais)
        if len(data.shape) > 1:
            data = np.mean(data, axis=1)
            
        # Resample se necessário
        if fs != SAMPLE_RATE:
            # Calcula novo número de amostras
            number_of_samples = int(len(data) * float(SAMPLE_RATE) / fs)
            data = resample(data, number_of_samples)
            
        # Importante: Nosso algoritmo de fingerprinting (constantes de amplitude)
        # espera valores na escala de 16-bit inteiro (ex: amplitude > 10).
        # Como soundfile retorna float (-1.0 a 1.0), precisamos normalizar para int16 (-32768 a 32767).
        if data.dtype == np.float32 or data.dtype == np.float64:
             data = data * 32767
             data = data.astype(np.int16)
             
        return data
        
    except Exception as e:
        print(f"Erro ao carregar {file_path}: {e}")
        return None

def generate_spectrogram(samples):
    """
    Gera o espectrograma a partir das amostras de áudio.
    """
    nperseg = WINDOW_SIZE
    noverlap = int(WINDOW_SIZE * OVERLAP_RATIO)
    
    f, t, Sxx = spectrogram(samples, fs=SAMPLE_RATE, nperseg=nperseg, noverlap=noverlap)
    
    return f, t, Sxx
