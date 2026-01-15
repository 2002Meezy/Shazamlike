# 🎵 Shazamlike - Sistema de Reconhecimento Musical

Sistema de reconhecimento musical inspirado no algoritmo do Shazam. Utiliza **audio fingerprinting** para identificar músicas a partir de gravações curtas, mesmo com ruído de fundo.

![Visualização do Fingerprinting](assets/fingerprint_v2.png)

## ✨ Funcionalidades

- 🎙️ **Gravação via Microfone**: Grave 5 segundos de áudio e identifique músicas em tempo real
- 📂 **Importação de Arquivos**: Reconheça músicas de arquivos WAV/MP3 locais
- 💾 **Banco de Dados Local**: Adicione suas próprias músicas ao sistema
- 📊 **Visualização**: Veja como o algoritmo de fingerprinting funciona
- 🖥️ **Interface Gráfica**: UI moderna em Dark Mode (CustomTkinter)

## 🔬 Como Funciona

O sistema utiliza o algoritmo de **Constellation Map** baseado no paper de Avery Li-Chun Wang:

1. **Espectrograma**: Transforma o áudio do domínio do tempo para frequência (FFT)
2. **Detecção de Picos**: Identifica pontos de maior energia no espectrograma
3. **Hashing Combinatório**: Cria fingerprints únicos combinando pares âncora-alvo
4. **Alinhamento Temporal**: Valida matches verificando consistência temporal dos hashes

### Exemplo de Hash
```
hash = "2547|4821|35"
├─ 2547 Hz: Frequência âncora
├─ 4821 Hz: Frequência alvo  
└─ 35: Delta tempo (frames)
```

## 🚀 Instalação

### Requisitos
- Python 3.10+
- FFmpeg (opcional, apenas para MP3)

### Passo a Passo

1. Clone o repositório:
```bash
git clone https://github.com/2002Meezy/Shazamlike.git
cd Shazamlike
```

2. Crie um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 💻 Uso

### Interface Gráfica (Recomendado)

```bash
python src/gui.py
```

**Funcionalidades da GUI:**
- 🎙️ **Botão "OUVIR"**: Grava 5s do microfone e identifica
- 📂 **"Reconhecer Arquivo Local"**: Seleciona arquivo para reconhecer
- ➕ **"Adicionar Música ao Banco"**: Cadastra nova música no banco de dados

### Linha de Comando

**Adicionar música ao banco:**
```bash
python main.py add "data/musica.wav"
```

**Reconhecer música:**
```bash
python main.py recognize "data/amostra.wav"
```

### Visualização do Algoritmo

```bash
python visualize_fingerprinting.py "data/musica.wav" 10
```

Gera uma imagem mostrando:
- Espectrograma da música
- Picos detectados (Constellation Map)
- Formação de hashes (pares âncora-alvo)

## 📁 Estrutura do Projeto

```
shazamlike/
├── src/
│   ├── audio_processing.py   # Leitura e espectrograma
│   ├── fingerprinting.py     # Detecção de picos e hashing
│   ├── database.py            # SQLite (músicas e fingerprints)
│   ├── recorder.py            # Gravação de microfone
│   └── gui.py                 # Interface gráfica
├── data/                      # Arquivos de áudio
├── db/                        # Banco de dados SQLite
├── main.py                    # CLI principal
├── visualize_fingerprinting.py
└── requirements.txt
```

## 🧪 Testando

1. **Adicione uma música:**
```bash
python main.py add "data/sua_musica.wav"
```

2. **Teste o reconhecimento:**
   - Toque a música no celular/PC
   - Rode a interface: `python src/gui.py`
   - Clique em "🎙️ OUVIR"
   - Aguarde 5 segundos

3. **Resultado esperado:**
```
RESULTADO: Música detectada! (ID: 1)
Score de Confiança: 175091 matches alinhados.
```

## 🎯 Limitações Atuais

- ⚠️ Funciona melhor com áudio de **alta qualidade** (WAV não comprimido)
- ⚠️ Requer **ruído de fundo baixo** para melhores resultados
- ⚠️ Banco de dados local (não escala para milhões de músicas como o Shazam real)
- ⚠️ Algoritmo simplificado (sem otimizações de índice avançadas)

## 🛠️ Tecnologias

- **NumPy/SciPy**: Processamento de sinais (FFT, espectrogramas)
- **SQLite**: Armazenamento de fingerprints
- **SoundDevice**: Gravação de áudio
- **SoundFile**: Leitura/escrita de arquivos
- **CustomTkinter**: Interface gráfica moderna
- **Matplotlib**: Visualizações

## 📚 Referências

- [An Industrial-Strength Audio Search Algorithm (Avery Wang)](https://www.ee.columbia.edu/~dpwe/papers/Wang03-shazam.pdf)
- [How Does Shazam Work? (Toptal)](https://www.toptal.com/developers/algorithms/shazam-it-music-processing-fingerprinting-and-recognition)

## 📝 Licença

MIT License - Sinta-se livre para usar em projetos pessoais e educacionais.

## 🤝 Contribuições

Contribuições são bem-vindas! Abra uma issue ou pull request.

---

**Desenvolvido como projeto educacional para entender algoritmos de audio fingerprinting** 🎓
