import sqlite3
import os
import time

def extract_info(segments):
    info = {}
    for i in range(len(segments)):
        if segments[i] == 'title' and i > 0:
            info['title'] = segments[i - 1]
        elif segments[i] == 'artist' and i > 0:
            info['artist'] = segments[i - 1]
    return info

def extract_segments(buffer, start_marker, end_marker):
    segments = []
    start_index = 0
    end_index = 0
    while start_index != -1:
        start_index = buffer.find(start_marker, end_index)
        if start_index != -1:
            end_index = buffer.find(end_marker, start_index + 1)
            if end_index != -1:
                segment = buffer[start_index + len(start_marker):end_index]
                segments.append(segment)
    return segments

def save_now_playing(artist, title):
    with open('nowplaying.txt', 'w') as file:
        file.write(f"{artist} - {title}")  # Grava no formato "Artist - Title"

def get_latest_track():
    home_directory = os.path.expanduser("~")
    db_path = os.path.join(home_directory, 'Music', 'djay', 'djay Media Library', 'MediaLibrary.db')

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Query para buscar a última faixa tocada
    cursor.execute("SELECT data FROM database2 WHERE collection = 'historySessionItems' ORDER BY rowid DESC LIMIT 1;")
    row = cursor.fetchone()
    
    if row:
        try:
            incoming_buffer = row[0].decode('utf-8', errors='replace')  # Usa 'replace' para substituir caracteres inválidos
        except UnicodeDecodeError as e:
            print(f"Erro de decodificação: {e}")
            return
        
        start_marker = '\x08'
        end_marker = '\x00'

        segments = extract_segments(incoming_buffer, start_marker, end_marker)
        track_info = extract_info(segments)
        
        if 'artist' in track_info and 'title' in track_info:
            save_now_playing(track_info['artist'], track_info['title'])
            print(f"Now playing - {track_info['artist']} - {track_info['title']}")
        else:
            print("Could not extract artist and title.")
    else:
        print("No track found.")

    connection.close()

# Loop para verificar a cada 15 segundos
while True:
    get_latest_track()   # Atualiza o nowplaying.txt com a faixa mais recente
    time.sleep(5)       # Aguardar 5 segundos antes da próxima atualização
