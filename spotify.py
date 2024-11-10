import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

init(autoreset=True)

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
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
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
            print(Fore.RED + f"Error getting playlist tracks: {str(e)}")
            return []

    def find_youtube_url(self, search_query):
        max_retries = 3
        for _ in range(max_retries):
            try:
                videos_search = VideosSearch(search_query, limit=1)
                results = videos_search.result()
                
                if results and results['result']:
                    return f"https://www.youtube.com/watch?v={results['result'][0]['id']}"
                time.sleep(1)
            except Exception as e:
                print(Fore.RED + f"Error finding YouTube URL for {search_query}: {str(e)}")
                time.sleep(2)
        return None

    def download_track(self, track_info):
        try:
            filename = f"downloads/{track_info['filename']}.mp3"
            if os.path.exists(filename):
                print(Fore.YELLOW + f"Skipping (already exists): {track_info['filename']}")
                return True

            youtube_url = self.find_youtube_url(track_info['search_query'])
            if not youtube_url:
                print(Fore.RED + f"Could not find YouTube URL for: {track_info['search_query']}")
                return False

            opts = dict(self.ydl_opts)
            opts['outtmpl'] = f"downloads/{track_info['filename']}.%(ext)s"

            with YoutubeDL(opts) as ydl:
                ydl.download([youtube_url])
            print(Fore.GREEN + f"Successfully downloaded: {track_info['filename']}")
            return True

        except Exception as e:
            print(Fore.RED + f"Error downloading {track_info['search_query']}: {str(e)}")
            return False

    def download_playlist(self, playlist_url, max_workers=3):
        if not os.path.exists('downloads'):
            os.makedirs('downloads')
            
        print(Fore.CYAN + "Getting playlist tracks...")
        tracks = self.get_playlist_tracks(playlist_url)
        
        if not tracks:
            print(Fore.RED + "No tracks found in playlist.")
            return
            
        total_tracks = len(tracks)
        print(Fore.CYAN + f"Found {total_tracks} tracks. Starting download...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.download_track, tracks))
        
        successful = sum(1 for x in results if x)
        print(Fore.GREEN + f"\nDownload completed!")
        print(Fore.GREEN + f"Successfully downloaded: {successful}/{total_tracks} tracks")
        if successful != total_tracks:
            print(Fore.RED + f"Failed to download: {total_tracks - successful} tracks")

def main():
    CLIENT_ID = "REPLACE_WITH_CLIENT_ID"
    CLIENT_SECRET = "REPLACE_WITH_CLIENT_SECRET"
    
    hackify_banner = f"""
{Fore.GREEN}{Style.BRIGHT}
██╗  ██╗ █████╗  ██████╗██╗  ██╗██╗███████╗██╗   ██╗
██║  ██║██╔══██╗██╔════╝██║ ██╔╝██║██╔════╝╚██╗ ██╔╝
███████║███████║██║     █████╔╝ ██║█████╗   ╚████╔╝ 
██╔══██║██╔══██║██║     ██╔═██╗ ██║██╔══╝    ╚██╔╝  
██║  ██║██║  ██║╚██████╗██║  ██╗██║██║        ██║   
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝        ╚═╝   
By Coder-Soft                                       
    """
    print(hackify_banner + Style.RESET_ALL)
    
    try:
        downloader = SpotifyDownloader(CLIENT_ID, CLIENT_SECRET)
        
        while True:
            playlist_url = input(Fore.CYAN + "\nEnter Spotify playlist URL (or 'exit' to quit): ").strip()
            
            if playlist_url.lower() == 'exit':
                break
                
            if not playlist_url:
                print(Fore.YELLOW + "Please enter a valid URL")
                continue
                
            if 'spotify.com/playlist/' not in playlist_url:
                print(Fore.YELLOW + "Please enter a valid Spotify playlist URL")
                continue
                
            downloader.download_playlist(playlist_url)
            
            another = input(Fore.CYAN + "\nWould you like to download another playlist? (y/n): ").strip().lower()
            if another != 'y':
                break
                
    except KeyboardInterrupt:
        print(Fore.RED + "\nDownload interrupted by user")
    except Exception as e:
        print(Fore.RED + f"\nAn error occurred: {str(e)}")
    finally:
        print(Fore.CYAN + "\nThank you for using Hackify Playlist Downloader!")

if __name__ == "__main__":
    main()
