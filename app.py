from flask import Flask, render_template, request, jsonify
import os
import requests
import json
import re

app = Flask(__name__)
SONGS_DIR = 'songs'

# Create songs directory if it doesn't exist
if not os.path.exists(SONGS_DIR):
    os.makedirs(SONGS_DIR)

def sanitize_filename(filename):
    # Remove invalid characters from filename
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename

def parse_song_input(input_text):
    # Try to split by " by " (case insensitive)
    parts = re.split(r'\s+by\s+', input_text, flags=re.IGNORECASE, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_lyrics', methods=['POST'])
def get_lyrics():
    data = request.json
    search_text = data.get('search_text', '')
    
    title, artist = parse_song_input(search_text)
    if not title or not artist:
        return jsonify({'error': 'Please enter song in format: "Song Title by Artist"'}), 400
    
    # First check if we have the lyrics locally
    filename = f"{sanitize_filename(title)}-{sanitize_filename(artist)}.txt"
    file_path = os.path.join(SONGS_DIR, filename)
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lyrics = f.read()
    else:
        # If not found locally, fetch from API
        try:
            response = requests.get(f'https://api.lyrics.ovh/v1/{artist}/{title}', timeout=10)
            if response.status_code == 404:
                return jsonify({'error': 'Lyrics not found for this song'}), 404
            elif response.status_code != 200:
                return jsonify({'error': 'Failed to fetch lyrics from server'}), response.status_code
            
            lyrics = response.json().get('lyrics')
            if not lyrics:
                return jsonify({'error': 'No lyrics found for this song'}), 404
                
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(lyrics)
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Request timed out. Please try again.'}), 504
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Error fetching lyrics: {str(e)}'}), 500
    
    return jsonify({
        'lyrics': lyrics,
        'filename': filename
    })

@app.route('/list_songs')
def list_songs():
    files = []
    for filename in os.listdir(SONGS_DIR):
        if filename.endswith('.txt'):
            files.append(filename)
    return jsonify(files)

@app.route('/update_lyrics', methods=['POST'])
def update_lyrics():
    data = request.json
    filename = data.get('filename')
    new_lyrics = data.get('lyrics')
    
    file_path = os.path.join(SONGS_DIR, filename)
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_lyrics)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/rename_file', methods=['POST'])
def rename_file():
    data = request.json
    old_filename = data.get('old_filename')
    new_filename = sanitize_filename(data.get('new_filename'))
    
    old_path = os.path.join(SONGS_DIR, old_filename)
    new_path = os.path.join(SONGS_DIR, new_filename)
    
    try:
        os.rename(old_path, new_path)
        return jsonify({'success': True, 'new_filename': new_filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_file', methods=['POST'])
def delete_file():
    data = request.json
    filename = data.get('filename')
    
    file_path = os.path.join(SONGS_DIR, filename)
    try:
        os.remove(file_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_saved_lyrics', methods=['POST'])
def get_saved_lyrics():
    data = request.json
    filename = data.get('filename')
    
    file_path = os.path.join(SONGS_DIR, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lyrics = f.read()
        return jsonify({
            'lyrics': lyrics,
            'filename': filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
