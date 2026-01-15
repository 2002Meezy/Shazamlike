import argparse
import os
import sys
from collections import defaultdict

# Adiciona o diretório atual ao path para importar modulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import src.audio_processing as audio
import src.fingerprinting as fingerprinting
import src.database as db

def cmd_add(args):
    filename = args.path
    print(f"--> Processando: {filename}")
    
    # 1. Carregar Audio
    samples = audio.load_audio_file(filename)
    if samples is None:
        return
        
    print(f"    Leitura concluída. {len(samples)} amostras.")
    
    # 2. Gerar Espectrograma
    f, t, Sxx = audio.generate_spectrogram(samples)
    
    # 3. Encontrar Picos
    peaks = fingerprinting.get_2d_peaks(Sxx)
    print(f"    {len(peaks)} picos encontrados.")
    
    # 4. Gerar Fingerprints
    fingerprints = fingerprinting.generate_fingerprints(peaks)
    print(f"    {len(fingerprints)} fingerprints gerados.")
    
    # 5. Salvar no DB
    song_name = os.path.basename(filename)
    song_id = db.insert_song(song_name)
    db.insert_fingerprints(song_id, fingerprints)
    
    print(f"--> Sucesso! Música '{song_name}' adicionada com ID {song_id}.")

def cmd_recognize(args):
    filename = args.path
    print(f"--> Analisando amostra: {filename}")
    
    samples = audio.load_audio_file(filename)
    if samples is None: return

    # Processamento igual ao cadastro
    f, t, Sxx = audio.generate_spectrogram(samples)
    peaks = fingerprinting.get_2d_peaks(Sxx)
    fingerprints = fingerprinting.generate_fingerprints(peaks) # Lista de (hash, sample_offset)
    
    print(f"    {len(fingerprints)} fingerprints na amostra.")
    
    if len(fingerprints) == 0:
        print("Nenhum detalhe relevante encontrado na amostra. Tente uma gravação maior ou com menos ruído.")
        return

    # Buscar matches no DB
    # Extrair apenas os hashes para busca
    hashes_to_search = [fp[0] for fp in fingerprints]
    
    # matches_db é lista de (song_id, db_offset, hash)
    # Mas como enviar muitos hashes pode quebrar o limite do SQLite, idealmente faríamos em lotes.
    # Para teste simples, vai tudo de uma vez.
    matches_db = db.get_matches(hashes_to_search)
    
    print(f"    {len(matches_db)} coincidências brutas encontradas no banco.")
    
    # ALINHAMENTO TEMPORAL
    # Precisamos mapear hash -> sample_offset para calcular o delta
    # Como um hash pode aparecer varias vezes na amostra, criamos um mapa list
    sample_hash_offsets = defaultdict(list)
    for h, offset in fingerprints:
        sample_hash_offsets[h].append(offset)
        
    # Contabilizar os "Time Offsets" reais
    # Para cada match, calculamos: real_start_time = db_offset - sample_offset
    # Se a música é a mesma, esse 'real_start_time' deve se repetir muitas vezes.
    
    song_scores = defaultdict(lambda: defaultdict(int)) # song_id -> { time_diff -> count }
    
    for song_id, db_offset, h in matches_db:
        if h in sample_hash_offsets:
            for sample_offset in sample_hash_offsets[h]:
                diff = db_offset - sample_offset
                song_scores[song_id][diff] += 1
                
    # Analisar o melhor candidato
    best_song_id = None
    best_count = 0
    confidence = 0
    
    for song_id, diffs_histogram in song_scores.items():
        # Pega o offset que teve mais matches para essa música
        most_frequent_diff_count = max(diffs_histogram.values())
        
        if most_frequent_diff_count > best_count:
            best_count = most_frequent_diff_count
            best_song_id = song_id
            
    if best_song_id:
        # Recuperar nome da música (query simples, não implementada no db.py mas fácil de fazer ou inferir)
        # Vamos adicionar uma query rápida aqui ou assumir ID
        print(f"\nRESULTADO: Música detectada! (ID: {best_song_id})")
        print(f"Score de Confiança: {best_count} matches alinhados.")
    else:
        print("\nResultado: Nenhuma correspondência forte encontrada.")

def main():
    parser = argparse.ArgumentParser(description='Shazam-like Audio Recognizer')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Comando ADD
    parser_add = subparsers.add_parser('add', help='Adicionar música ao banco de dados')
    parser_add.add_argument('path', help='Caminho para o arquivo de áudio')
    parser_add.set_defaults(func=cmd_add)
    
    # Comando RECOGNIZE
    parser_rec = subparsers.add_parser('recognize', help='Reconhecer música de uma gravação')
    parser_rec.add_argument('path', help='Caminho para o arquivo de amostra')
    parser_rec.set_defaults(func=cmd_recognize)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
