import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

class SpotifyDownloader:
    def __init__(self, client_id, client_secret):
        self.spotify = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )
        
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

    def sanitize_filename(self, filename):
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Remove or replace other problematic characters
        filename = filename.replace('&', 'and')
        return filename.strip()

    def get_playlist_tracks(self, playlist_url):
        try:
            playlist_id = playlist_url.split('/')[-1].split('?')[0]
            results = self.spotify.playlist_tracks(playlist_id)
            tracks = []
            
            while results:
                for item in results['items']:
                    track = item['track']
                    if track:
                        track_name = track['name']
                        artist_name = track['artists'][0]['name']
                        search_query = f"{track_name} - {artist_name}"
                        
                        # Create sanitized filename
                        filename = self.sanitize_filename(f"{artist_name} - {track_name}")
                        
                        tracks.append({
                            'name': track_name,
                            'artist': artist_name,
                            'search_query': search_query,
                            'filename': filename
                        })
                
                if results['next']:
                    results = self.spotify.next(results)
                else:
                    results = None
                    
            return tracks
        except Exception as e:
            print(f"Error getting playlist tracks: {str(e)}")
            return []

    def find_youtube_url(self, search_query):
        max_retries = 3
        for _ in range(max_retries):
            try:
                videos_search = VideosSearch(search_query, limit=1)
                results = videos_search.result()
                
                if results and results['result']:
                    return f"https://www.youtube.com/watch?v={results['result'][0]['id']}"
                time.sleep(1)  # Add delay between retries
            except Exception as e:
                print(f"Error finding YouTube URL for {search_query}: {str(e)}")
                time.sleep(2)  # Add longer delay after error
        return None

    def download_track(self, track_info):
        try:
            # Check if file already exists
            filename = f"downloads/{track_info['filename']}.mp3"
            if os.path.exists(filename):
                print(f"Skipping (already exists): {track_info['filename']}")
                return True

            youtube_url = self.find_youtube_url(track_info['search_query'])
            if not youtube_url:
                print(f"Could not find YouTube URL for: {track_info['search_query']}")
                return False

            # Customize output template for this specific download
            opts = dict(self.ydl_opts)
            opts['outtmpl'] = f"downloads/{track_info['filename']}.%(ext)s"

            with YoutubeDL(opts) as ydl:
                ydl.download([youtube_url])
            print(f"Successfully downloaded: {track_info['filename']}")
            return True

        except Exception as e:
            print(f"Error downloading {track_info['search_query']}: {str(e)}")
            return False

    def download_playlist(self, playlist_url, max_workers=3):
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
            
        print("Getting playlist tracks...")
        tracks = self.get_playlist_tracks(playlist_url)
        
        if not tracks:
            print("No tracks found in playlist.")
            return
            
        total_tracks = len(tracks)
        print(f"Found {total_tracks} tracks. Starting download...")
        
        # Using ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.download_track, tracks))
        
        # Print summary
        successful = sum(1 for x in results if x)
        print(f"\nDownload completed!")
        print(f"Successfully downloaded: {successful}/{total_tracks} tracks")
        if successful != total_tracks:
            print(f"Failed to download: {total_tracks - successful} tracks")

def main():
    # Replace these with your Spotify API credentials
    CLIENT_ID = "REQ*"
    CLIENT_SECRET = "REQ*"
    
    try:
        downloader = SpotifyDownloader(CLIENT_ID, CLIENT_SECRET)
        
        while True:
            playlist_url = input("\nEnter Spotify playlist URL (or 'exit' to quit): ").strip()
            
            if playlist_url.lower() == 'exit':
                break
                
            if not playlist_url:
                print("Please enter a valid URL")
                continue
                
            if 'spotify.com/playlist/' not in playlist_url:
                print("Please enter a valid Spotify playlist URL")
                continue
                
            downloader.download_playlist(playlist_url)
            
            another = input("\nWould you like to download another playlist? (y/n): ").strip().lower()
            if another != 'y':
                break
                
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        print("\nThank you for using Spotify Playlist Downloader!")

if __name__ == "__main__":
    main()