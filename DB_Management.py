import sqlite3

def create_connection():
    conn = sqlite3.connect('music_app_database.db')
    return conn


def create_table(conn):
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
                            user_id INTEGER PRIMARY KEY,
                            username TEXT UNIQUE,
                            password TEXT,
                            date_of_birth DATE)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS UserStatistics (
                            user_id INTEGER PRIMARY KEY,
                            most_listened_artist TEXT,
                            favorite_genre TEXT,
                            total_time_listened INTEGER,
                            FOREIGN KEY(user_id) REFERENCES Users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Playlists (
                            playlist_id INTEGER PRIMARY KEY,
                            user_id INTEGER,
                            playlist_name TEXT,
                            creation_date DATE,
                            FOREIGN KEY(user_id) REFERENCES Users(user_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS PlaylistTracks (
                            playlist_id INTEGER,
                            track_id INTEGER,
                            track_order INTEGER,
                            FOREIGN KEY(playlist_id) REFERENCES Playlists(playlist_id),
                            FOREIGN KEY(track_id) REFERENCES Tracks(track_id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Tracks (
                            track_id TEXT PRIMARY KEY,
                            artist TEXT,
                            album_name TEXT,
                            track_name TEXT,
                            popularity INTEGER,
                            duration_ms INTEGER,
                            tempo REAL,
                            track_genre TEXT)''')
    conn.commit()

def get_random_songs(conn, amount):
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM Tracks ORDER BY RANDOM() LIMIT {amount}")
    return cursor.fetchall()

def add_user(conn, username, password, date_of_birth):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Users (username, password, date_of_birth) VALUES (?, ?, ?)",
                   (username, password, date_of_birth))
    conn.commit()

def username_exists(conn, username):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Users WHERE username = ?", (username,))
    return cursor.fetchone() is not None

def user_exists(conn, username, password):
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM Users WHERE username = ? AND password = ?", (username, password))
    return cursor.fetchone() is not None

def add_playlist(conn, user_id, playlist_name, creation_date):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Playlists (user_id, playlist_name, creation_date) VALUES (?, ?, ?)",
                   (user_id, playlist_name, creation_date))
    conn.commit()

def add_track(conn, track_id, artist, album_name, track_name, popularity, duration_ms, tempo, track_genre):
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO Tracks (track_id, artist, album_name, track_name, popularity, duration_ms, tempo, 
    track_genre) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (track_id, artist, album_name, track_name, popularity, duration_ms, tempo, track_genre))
    conn.commit()

def add_song_to_playlist(conn, playlist_id, track_id, track_order):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO PlaylistTracks (playlist_id, track_id, track_order) VALUES (?, ?, ?)",
                   (playlist_id, track_id, track_order))
    conn.commit()

def edit_user(conn, user_id, username, password, date_of_birth):
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET username = ?, password = ?, date_of_birth = ? WHERE user_id = ?",
                   (username, password, date_of_birth, user_id))
    conn.commit()

def get_user_id(conn, username):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE username = ?", (username,))
    user_id = cursor.fetchone()
    return user_id[0] if user_id else None

def get_username(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM Users WHERE user_id = ?", (user_id,))
    username = cursor.fetchone()
    return username[0] if username else None

def delete_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM UserStatistics WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM Playlists WHERE user_id = ?", (user_id,))
    conn.commit()

def get_user_info(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def delete_playlist(conn, playlist_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM PlaylistTracks WHERE playlist_id = ?", (playlist_id,))
    cursor.execute("DELETE FROM Playlists WHERE playlist_id = ?", (playlist_id,))
    conn.commit()

def get_user_playlists(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Playlists WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def update_track(conn, track_id, artist, album_name, track_name, popularity, duration_ms, tempo, track_genre):
    cursor = conn.cursor()
    cursor.execute('''UPDATE Tracks SET artist = ?, album_name = ?, track_name = ?, popularity = ?, duration_ms = ?, 
    tempo = ?, track_genre = ? WHERE track_id = ?''',
                   (artist, album_name, track_name, popularity, duration_ms, tempo, track_genre, track_id))
    conn.commit()

def delete_track(conn, track_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM PlaylistTracks WHERE track_id = ?", (track_id,))
    cursor.execute("DELETE FROM Tracks WHERE track_id = ?", (track_id,))
    conn.commit()

def get_all_tracks(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tracks")
    return cursor.fetchall()

def remove_track_from_playlist(conn, playlist_id, track_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM PlaylistTracks WHERE playlist_id = ? AND track_id = ?", (playlist_id, track_id))
    conn.commit()

def get_tracks_in_playlist(conn, playlist_id):
    cursor = conn.cursor()
    cursor.execute('''SELECT Tracks.* FROM Tracks 
                          JOIN PlaylistTracks ON Tracks.track_id = PlaylistTracks.track_id 
                          WHERE PlaylistTracks.playlist_id = ? 
                          ORDER BY PlaylistTracks.track_order''', (playlist_id,))
    return cursor.fetchall()

def update_user_statistics(conn, user_id, most_listened_artist, favorite_genre, total_time_listened):
    cursor = conn.cursor()
    cursor.execute('''UPDATE UserStatistics 
                          SET most_listened_artist = ?, favorite_genre = ?, total_time_listened = ? 
                          WHERE user_id = ?''',
                   (most_listened_artist, favorite_genre, total_time_listened, user_id))
    conn.commit()

def get_user_statistics(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UserStatistics WHERE user_id = ?", (user_id,))
    return cursor.fetchone()

def get_playlist_details(conn, playlist_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Playlists WHERE playlist_id = ?", (playlist_id,))
    return cursor.fetchone()

def get_playlists_by_name(conn, playlist_name):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Playlists WHERE playlist_name LIKE ?", ('%' + playlist_name + '%',))
    return cursor.fetchall()

def get_playlist_total_duration(conn, playlist_id):
    cursor = conn.cursor()
    cursor.execute('''SELECT SUM(Tracks.duration_ms) FROM Tracks 
                          JOIN PlaylistTracks ON Tracks.track_id = PlaylistTracks.track_id 
                          WHERE PlaylistTracks.playlist_id = ?''', (playlist_id,))
    total_duration = cursor.fetchone()[0]
    return total_duration

def get_most_popular_tracks(conn, limit=10):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tracks ORDER BY popularity DESC LIMIT ?", (limit,))
    return cursor.fetchall()

def get_tracks_by_genre(conn, genre):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tracks WHERE track_genre = ?", (genre,))
    return cursor.fetchall()

def search_tracks_by_name(conn, track_name):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tracks WHERE track_name LIKE ?", ('%' + track_name + '%',))
    return cursor.fetchall()

def get_user_listening_statistics(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''SELECT 
                             COUNT(PlaylistTracks.track_id) AS track_count, 
                             SUM(Tracks.duration_ms) AS total_duration 
                          FROM PlaylistTracks 
                          JOIN Playlists ON PlaylistTracks.playlist_id = Playlists.playlist_id 
                          JOIN Tracks ON PlaylistTracks.track_id = Tracks.track_id 
                          WHERE Playlists.user_id = ?''', (user_id,))
    return cursor.fetchone()

def get_top_genres_for_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''SELECT Tracks.track_genre, COUNT(*) as genre_count 
                          FROM PlaylistTracks 
                          JOIN Playlists ON PlaylistTracks.playlist_id = Playlists.playlist_id 
                          JOIN Tracks ON PlaylistTracks.track_id = Tracks.track_id 
                          WHERE Playlists.user_id = ? 
                          GROUP BY Tracks.track_genre 
                          ORDER BY genre_count DESC''', (user_id,))
    return cursor.fetchall()

def change_user_password(conn, user_id, new_password):
    cursor = conn.cursor()
    cursor.execute("UPDATE Users SET password = ? WHERE user_id = ?", (new_password, user_id))
    conn.commit()

def get_all_users(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users")
    return cursor.fetchall()

def get_playlists_by_user(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Playlists WHERE user_id = ?", (user_id,))
    return cursor.fetchall()

def rename_playlist(conn, playlist_id, new_name):
    cursor = conn.cursor()
    cursor.execute("UPDATE Playlists SET playlist_name = ? WHERE playlist_id = ?", (new_name, playlist_id))
    conn.commit()

def get_track_details(conn, track_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tracks WHERE track_id = ?", (track_id,))
    return cursor.fetchone()

def get_user_favorite_artist(conn, user_id):
    cursor = conn.cursor()
    cursor.execute('''SELECT most_listened_artist FROM UserStatistics WHERE user_id = ?''', (user_id,))
    return cursor.fetchone()

def backup_database(source_db, backup_db):
    conn = sqlite3.connect(source_db)
    backup_conn = sqlite3.connect(backup_db)
    with backup_conn:
        conn.backup(backup_conn)
    backup_conn.close()
    conn.close()

def search_bar(conn, query):
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM Tracks 
                      WHERE track_name LIKE ? OR artist LIKE ?''',
                   ('%' + query + '%', '%' + query + '%'))
    return cursor.fetchall()



