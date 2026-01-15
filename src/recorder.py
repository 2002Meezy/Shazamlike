import sounddevice as sd
import soundfile as sf
import numpy as np
import os

def record_audio(filename, duration=10, samplerate=44100):
    """
    Grava áudio do microfone padrão por 'duration' segundos
    e salva no 'filename'.
    """
    try:
        print(f"Iniciando gravação de {duration}s...")
        # Grava como array float32
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
        sd.wait()  # Espera terminar
        print("Gravação concluída.")
        
        # Garante diretório
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Salva como WAV PCM 16-bit (padrão do nosso sistema)
        sf.write(filename, recording, samplerate, subtype='PCM_16')
        return True
    except Exception as e:
        print(f"Erro na gravação: {e}")
        return False

if __name__ == '__main__':
    # Teste rápido
    record_audio("data/test_mic.wav", duration=3)
