import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import sys

# Adiciona diretório src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import database as db
import audio_processing as audio
import fingerprinting
import recorder
from collections import defaultdict

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ShazamApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Shazam-Like Project")
        self.geometry("400x500")
        
        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Espaço vazio em cima
        self.grid_rowconfigure(4, weight=1) # Espaço vazio em baixo
        
        self.label_status = ctk.CTkLabel(self, text="Pronto para Ouvir", font=("Roboto", 16))
        self.label_status.grid(row=0, column=0, pady=20, sticky="s")
        
        # Botão Principal (Ouvir)
        self.btn_listen = ctk.CTkButton(self, text="🎙️ OUVIR", width=200, height=80, 
                                        font=("Roboto", 24, "bold"),
                                        command=self.start_listening_thread,
                                        fg_color="#E91E63", hover_color="#C2185B")
        self.btn_listen.grid(row=1, column=0, pady=20)

        # Botão Upload Arquivo
        self.btn_file = ctk.CTkButton(self, text="Reconhecer Arquivo Local", command=self.recognize_file_dialog)
        self.btn_file.grid(row=2, column=0, pady=10)

        # Resultado
        self.label_result = ctk.CTkLabel(self, text="---", font=("Roboto", 20), text_color="#4CAF50")
        self.label_result.grid(row=3, column=0, pady=20)

        # Seção Admin
        self.frame_admin = ctk.CTkFrame(self)
        self.frame_admin.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        
        self.lbl_admin = ctk.CTkLabel(self.frame_admin, text="Admin Zone")
        self.lbl_admin.pack(pady=5)
        
        self.btn_add = ctk.CTkButton(self.frame_admin, text="Adicionar Música ao Banco", 
                                     command=self.add_song_dialog, fg_color="#555")
        self.btn_add.pack(pady=10, side="bottom")

    def start_listening_thread(self):
        self.label_status.configure(text="Gravando (5s)...", text_color="orange")
        self.label_result.configure(text="---")
        self.btn_listen.configure(state="disabled")
        
        # Roda em thread para não travar a GUI
        threading.Thread(target=self.run_listening_process).start()

    def run_listening_process(self):
        temp_file = "data/temp_mic.wav"
        success = recorder.record_audio(temp_file, duration=5)
        
        if success:
            self.run_recognition(temp_file)
        else:
            self.label_status.configure(text="Erro na gravação!", text_color="red")
            self.btn_listen.configure(state="normal")

    def recognize_file_dialog(self):
        filename = filedialog.askopenfilename(filetypes=[("Audio", "*.wav *.mp3")])
        if filename:
            self.label_status.configure(text="Processando arquivo...", text_color="yellow")
            threading.Thread(target=self.run_recognition, args=(filename,)).start()

    def run_recognition(self, filepath):
        # Chama a lógica de backend (similar ao main.py)
        # Atenção: Isso roda na Thread secundária
        
        try:
            samples = audio.load_audio_file(filepath)
            if samples is None: raise Exception("Falha ao ler áudio")

            f, t, Sxx = audio.generate_spectrogram(samples)
            peaks = fingerprinting.get_2d_peaks(Sxx)
            fingerprints = fingerprinting.generate_fingerprints(peaks)

            if not fingerprints:
                self.update_ui_result("Sem detalhes suficientes.", None)
                return

            hashes_to_search = [fp[0] for fp in fingerprints]
            matches_db = db.get_matches(hashes_to_search)

            # Lógica de Alinhamento
            sample_hash_offsets = defaultdict(list)
            for h, offset in fingerprints:
                sample_hash_offsets[h].append(offset)
            
            song_scores = defaultdict(lambda: defaultdict(int))
            for song_id, db_offset, h in matches_db:
                if h in sample_hash_offsets:
                    for sample_offset in sample_hash_offsets[h]:
                        diff = db_offset - sample_offset
                        song_scores[song_id][diff] += 1
            
            best_song_id = None
            best_count = 0
            
            for song_id, diffs_histogram in song_scores.items():
                most_frequent_diff_count = max(diffs_histogram.values())
                if most_frequent_diff_count > best_count:
                    best_count = most_frequent_diff_count
                    best_song_id = song_id
            
            # Limiar básico de confiança
            if best_count > 10: # Valor arbitrário baixo para teste
                # Buscar nome da musica (precisaria de query no DB, vamos adicionar rapidinho)
                song_name = self.get_song_name(best_song_id)
                self.update_ui_result(f"{song_name}", f"ID: {best_song_id}")
            else:
                self.update_ui_result("Não reconhecida.", None)

        except Exception as e:
            print(e)
            self.update_ui_result(f"Erro: {str(e)}", None)
        
    def get_song_name(self, song_id):
        conn = db.get_db_connection()
        c = conn.cursor()
        c.execute("SELECT name FROM songs WHERE id = ?", (song_id,))
        res = c.fetchone()
        conn.close()
        return res['name'] if res else "Desconhecida"

    def update_ui_result(self, main_text, sub_text):
        # Tkinter não é thread-safe, usar after se for critico, mas configure as vezes funciona
        # Correto é agendar no main loop
        def _update():
            self.label_status.configure(text="Pronto", text_color="white")
            self.label_result.configure(text=main_text)
            self.btn_listen.configure(state="normal")
            
        self.after(0, _update)

    def add_song_dialog(self):
        filename = filedialog.askopenfilename(filetypes=[("Audio", "*.wav *.mp3")])
        if filename:
            # Roda processo de adição em thread
            threading.Thread(target=self.run_add_process, args=(filename,)).start()

    def run_add_process(self, filename):
        try:
            samples = audio.load_audio_file(filename)
            f, t, Sxx = audio.generate_spectrogram(samples)
            peaks = fingerprinting.get_2d_peaks(Sxx)
            fingerprints = fingerprinting.generate_fingerprints(peaks)
            
            song_name = os.path.basename(filename)
            song_id = db.insert_song(song_name)
            db.insert_fingerprints(song_id, fingerprints)
            
            self.after(0, lambda: messagebox.showinfo("Sucesso", f"Música '{song_name}' adicionada!"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))

if __name__ == "__main__":
    app = ShazamApp()
    app.mainloop()
