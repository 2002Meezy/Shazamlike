import sqlite3
import os

# Caminho ajustado para a nova estrutura
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db', 'shazam.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Tabela de Músicas
    c.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            file_hash TEXT UNIQUE 
        )
    ''')
    
    # Tabela de Fingerprints
    c.execute('''
        CREATE TABLE IF NOT EXISTS fingerprints (
            hash TEXT NOT NULL,
            song_id INTEGER NOT NULL,
            offset INTEGER NOT NULL,
            FOREIGN KEY (song_id) REFERENCES songs (id)
        )
    ''')
    
    c.execute('CREATE INDEX IF NOT EXISTS idx_fingerprints_hash ON fingerprints (hash)')
    
    conn.commit()
    conn.close()

def insert_song(name, file_hash=None):
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('INSERT INTO songs (name, file_hash) VALUES (?, ?)', (name, file_hash))
        song_id = c.lastrowid
    except sqlite3.IntegrityError:
        c.execute('SELECT id FROM songs WHERE name = ?', (name,))
        result = c.fetchone()
        song_id = result['id'] if result else None
        
    conn.commit()
    conn.close()
    return song_id

def insert_fingerprints(song_id, fingerprints):
    conn = get_db_connection()
    c = conn.cursor()
    data = [(f[0], song_id, f[1]) for f in fingerprints]
    c.executemany('INSERT INTO fingerprints (hash, song_id, offset) VALUES (?, ?, ?)', data)
    conn.commit()
    conn.close()

def get_matches(hashes):
    conn = get_db_connection()
    c = conn.cursor()
    # SQLite tem limite de variaveis em uma query (geralmente 999 ou 32766)
    # Por segurança, vamos processar em chunks de 900
    CHUNK_SIZE = 900
    results = []
    
    for i in range(0, len(hashes), CHUNK_SIZE):
        chunk = hashes[i:i + CHUNK_SIZE]
        placeholders = ',' .join('?' for _ in chunk)
        
        query = f"""
            SELECT song_id, offset, hash 
            FROM fingerprints 
            WHERE hash IN ({placeholders})
        """
        
        c.execute(query, chunk)
        results.extend(c.fetchall())

    conn.close()
    
    return [(r['song_id'], r['offset'], r['hash']) for r in results]

if not os.path.exists(DB_PATH):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    init_db()
else:
    init_db()
