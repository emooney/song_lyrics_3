from flask import Flask, render_template, request, jsonify
import os
import requests
import json

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_lyrics', methods=['POST'])
def get_lyrics():
    data = request.json
    artist = data.get('artist')
    title = data.get('title')
    
    # First check if we have the lyrics locally
    filename = f"{sanitize_filename(title)}-{sanitize_filename(artist)}.txt"
    file_path = os.path.join(SONGS_DIR, filename)
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lyrics = f.read()
    else:
        # If not found locally, fetch from API
        try:
            response = requests.get(f'https://api.lyrics.ovh/v1/{artist}/{title}')
            if response.status_code == 200:
                lyrics = response.json()['lyrics']
                # Save to file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(lyrics)
            else:
                return jsonify({'error': 'Lyrics not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
