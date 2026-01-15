import numpy as np
from scipy.ndimage import maximum_filter

# Constantes para ajuste fino do algoritmo
PEAK_NEIGHBORHOOD_SIZE = 20  # Tamanho da vizinhança para definir um pico local
MIN_AMPLITUDE = 10           # Amplitude mínima para considerar um pico (filtro de ruído)

FINGERPRINT_REDUCTION = 20   # Se tivermos muitos picos, podemos limitar (fan-out)
# Constantes para geração de pares (Constellation Map)
MIN_HASH_TIME_DELTA = 0
MAX_HASH_TIME_DELTA = 200    # Janela de tempo para procurar pares

def get_2d_peaks(arr2d, plot=False):
    """
    Encontra picos locais em um array 2D (espectrograma).
    Retorna uma lista de tuplas (tempo_idx, frequencia_idx)
    """
    # 1. Filtro de máximo local
    # Cria uma máscara onde cada ponto é True se for o maior na vizinhança
    neighborhood = np.ones((PEAK_NEIGHBORHOOD_SIZE, PEAK_NEIGHBORHOOD_SIZE))
    local_max = maximum_filter(arr2d, footprint=neighborhood) == arr2d
    
    # 2. Filtro de amplitude mínima (background noise)
    background = (arr2d > MIN_AMPLITUDE)
    
    # Interseção dos dois filtros
    eroded_background = background & local_max
    
    # Obtém índices onde é True
    # time_indices corresponde ao eixo 1 (tempo) do espectrograma do scipy se Sxx for (freq, tempo)
    # Mas scipy.signal.spectrogram retorna Sxx como (n_freqs, n_times).
    # Então indices[0] é freq, indices[1] é tempo.
    detected_peaks = np.where(eroded_background)
    
    freq_indices = detected_peaks[0]
    time_indices = detected_peaks[1]
    
    # Retorna lista de (t, f)
    # Importante manter a ordem para iterar no tempo
    peaks = list(zip(time_indices, freq_indices))
    peaks.sort() # Ordena pelo tempo
    
    return peaks

def generate_fingerprints(peaks):
    """
    Gera hashes a partir da lista de picos (constellation map).
    Usa a estratégia de 'Anchor Point' e 'Target Zone'.
    
    Retorna lista de (hash_string, time_offset_anchor)
    """
    fingerprints = []
    
    # Itera sobre todos os picos para usá-los como âncora
    for i in range(len(peaks)):
        t1, f1 = peaks[i]
        
        # Procura picos alvo na "Target Zone" (janela à frente no tempo)
        for j in range(i + 1, len(peaks)):
            t2, f2 = peaks[j]
            t_delta = t2 - t1
            
            if t_delta < MIN_HASH_TIME_DELTA:
                continue
            if t_delta > MAX_HASH_TIME_DELTA:
                break # Como está ordenado, se passou do max, todos os próximos também passarão
            
            # Gera o Hash
            # O hash combina: Frequência Âncora | Frequência Alvo | Delta Tempo
            # Formato simples de string ou bytes. Usar string é mais fácil para debug e SQLite.
            # Ex: "f1|f2|dt" -> "102|500|25"
            h = f"{f1}|{f2}|{t_delta}"
            
            fingerprints.append((h, int(t1)))
            
    return fingerprints
