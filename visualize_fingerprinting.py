import matplotlib
matplotlib.use('Agg')  # Modo não-interativo
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import audio_processing as audio
import fingerprinting

def visualize_fingerprinting(audio_file, duration_seconds=10):
    """
    Visualização simplificada do fingerprinting em um trecho curto da música.
    """
    print(f"Carregando {audio_file}...")
    samples = audio.load_audio_file(audio_file)
    
    if samples is None:
        print("Erro ao carregar arquivo.")
        return
    
    # Pegar apenas os primeiros X segundos
    samples = samples[:audio.SAMPLE_RATE * duration_seconds]
    print(f"Usando apenas primeiros {duration_seconds} segundos.")
    
    print("Gerando espectrograma...")
    f, t, Sxx = audio.generate_spectrogram(samples)
    
    print("Detectando picos...")
    peaks = fingerprinting.get_2d_peaks(Sxx)
    print(f"Encontrados {len(peaks)} picos.")
    
    print("Gerando fingerprints...")
    fingerprints = fingerprinting.generate_fingerprints(peaks)
    print(f"Gerados {len(fingerprints)} fingerprints.")
    
    # Criar figura com subplots
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Espectrograma com escala log
    ax1 = axes[0]
    Sxx_log = 10 * np.log10(Sxx + 1e-10)
    im = ax1.pcolormesh(t, f, Sxx_log, shading='gouraud', cmap='viridis')
    ax1.set_ylabel('Frequência (Hz)')
    ax1.set_xlabel('Tempo (s)')
    ax1.set_title('1. Espectrograma - Representação visual do áudio no domínio frequência/tempo')
    ax1.set_ylim([0, 8000])
    plt.colorbar(im, ax=ax1, label='Magnitude (dB)')
    
    # Plot 2: Constellation Map (Picos + alguns pares)
    ax2 = axes[1]
    ax2.pcolormesh(t, f, Sxx_log, shading='gouraud', cmap='gray', alpha=0.3)
    
    # Plotar picos
    if len(peaks) > 0:
        peak_times = [t[p[0]] for p in peaks]
        peak_freqs = [f[p[1]] for p in peaks]
        ax2.scatter(peak_times, peak_freqs, c='red', s=10, alpha=0.7, label=f'{len(peaks)} Picos detectados')
    
    # Mostrar conexões de apenas UMA âncora como exemplo
    if len(peaks) > 10:
        anchor_idx = len(peaks) // 4  # Pegar âncora no meio
        t_anchor, f_anchor = peaks[anchor_idx]
        
        # Marcar a âncora especial
        ax2.scatter([t[t_anchor]], [f[f_anchor]], c='lime', s=100, marker='*', 
                   zorder=10, label='Âncora (exemplo)', edgecolors='black', linewidths=1.5)
        
        # Desenhar linhas para alvos próximos no tempo
        target_count = 0
        for peak_target in peaks[anchor_idx+1:]:
            t_target, f_target = peak_target
            time_diff = t_target - t_anchor
            
            if time_diff > fingerprinting.MAX_HASH_TIME_DELTA:
                break
            
            # Desenhar linha
            ax2.plot([t[t_anchor], t[t_target]], 
                    [f[f_anchor], f[f_target]], 
                    'cyan', alpha=0.6, linewidth=1.5, zorder=5)
            
            # Marcar alvo
            ax2.scatter([t[t_target]], [f[f_target]], c='yellow', s=50, 
                       marker='o', zorder=8, edgecolors='black', linewidths=0.5)
            
            target_count += 1
            if target_count >= 10:  # Limitar a 10 alvos visíveis
                break
        
        # Adicionar texto explicativo
        ax2.text(0.02, 0.98, 
                f'Cada linha cyan = 1 Hash\n'
                f'Hash = [freq_âncora, freq_alvo, Δtempo]\n'
                f'Total de {len(fingerprints)} hashes criados',
                transform=ax2.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax2.set_ylabel('Frequência (Hz)')
    ax2.set_xlabel('Tempo (s)')
    ax2.set_title('2. Constellation Map - Picos + Formação de Hashes (mostrando 1 âncora)')
    ax2.set_ylim([0, 8000])
    ax2.legend(loc='upper right')
    
    plt.tight_layout()
    
    # Salvar imagem
    output_file = os.path.join('data', 'fingerprint_visualization.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✅ Visualização salva em: {output_file}")
    plt.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python visualize_fingerprinting.py <caminho_audio.wav> [duração_em_segundos]")
        print("\nExemplo: python visualize_fingerprinting.py data/Rihanna-Don_t-Stop-The-Music-RihannaVEVO.wav 10")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    visualize_fingerprinting(audio_file, duration)
