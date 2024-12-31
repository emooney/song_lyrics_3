# Lyrics Manager

A Flask-based CRUD application for managing song lyrics using the lyrics.ovh API.

## Features

- Search for song lyrics by artist and title
- Automatically save lyrics to local storage
- Filter through saved lyrics
- Edit saved lyrics
- Rename lyrics files
- Delete lyrics files
- Light/Dark theme support with automatic preference saving
- All lyrics are stored in text files in the `songs` directory
- Responsive and modern UI with smooth transitions

## Running with Docker (Recommended)

1. Make sure you have Docker and Docker Compose installed

2. Build and run the application:
```bash
docker-compose up --build
```

3. Open your browser and navigate to `http://localhost:5000`

The application will be running in a container, and the `songs` directory will be mounted as a volume, so your lyrics will persist even if you restart the container.

## Running Locally (Alternative)

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Theme Toggle:
   - Click the "Toggle Theme" button in the header to switch between light and dark themes
   - Your theme preference will be saved automatically

2. Search for lyrics:
   - Enter the artist name and song title
   - Click "Search" or press Enter
   - If the lyrics are found locally, they will be displayed
   - If not found locally, they will be fetched from lyrics.ovh API and saved

3. Filter saved lyrics:
   - Use the filter input box to search through saved lyrics files
   - Results are filtered in real-time as you type

4. Managing Lyrics:
   - Click on any saved lyrics file to view its contents
   - Edit the text in the textarea
   - Use the following options:
     - "Back": Return to the main view
     - "Save Changes": Update the lyrics content
     - "Rename File": Change the filename
     - "Delete File": Remove the file (requires confirmation)

## File Storage

All lyrics are stored as text files in the `songs` directory with the format:
```
[songTitle]-[artist].txt
```

When running with Docker, the `songs` directory is mounted as a volume, ensuring your data persists between container restarts.
