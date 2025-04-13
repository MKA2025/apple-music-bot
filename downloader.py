import re
import shutil
from pathlib import Path
from typing import Optional
from gamdl.apple_music_api import AppleMusicApi
from gamdl.downloader import Downloader as BaseDownloader
from gamdl.downloader_song import DownloaderSong
from gamdl.enums import SongCodec
from config import Config

class DownloadError(Exception):
    pass

class Downloader:
    URL_PATTERN = r"https?://music\.apple\.com/\w+/(song|album|playlist)/[^\s]+"
    
    def __init__(self):
        self.am_api = AppleMusicApi(cookies_path=Config.COOKIES_PATH)
        self.base_downloader = BaseDownloader(
            apple_music_api=self.am_api,
            output_path=Config.DOWNLOAD_DIR,
            temp_path=Config.TEMP_DIR,
            download_mode="ytdlp",
            remux_mode="ffmpeg",
            codec=SongCodec.AAC,
            silent=True
        )
        self.song_downloader = DownloaderSong(self.base_downloader)

    def process(self, url: str, user_id: int) -> Path:
        try:
            if not re.match(self.URL_PATTERN, url):
                raise DownloadError("Invalid Apple Music URL")
            
            # Get track metadata
            url_info = self.base_downloader.get_url_info(url)
            queue = self.base_downloader.get_download_queue(url_info)
            
            if not queue.tracks_metadata:
                raise DownloadError("No tracks found")
            
            track = queue.tracks_metadata[0]
            return self._download_track(track)
        except Exception as e:
            raise DownloadError(str(e)) from e
        finally:
            self.cleanup()

    def _download_track(self, track: dict) -> Path:
        # Get streaming info
        webplayback = self.am_api.get_webplayback(track["id"])
        stream_info = self.song_downloader.get_stream_info(track)
        
        # Generate final path
        tags = self._generate_tags(webplayback)
        final_path = self.base_downloader.get_final_path(tags, ".m4a")
        
        if final_path.exists():
            return final_path
        
        # Download process
        encrypted_path = self.base_downloader.get_encrypted_path(track["id"])
        self.base_downloader.download(encrypted_path, stream_info.stream_url)
        
        # Handle decryption
        if stream_info.widevine_pssh:
            key = self.song_downloader.get_decryption_key(
                stream_info.widevine_pssh,
                track["id"]
            )
            decrypted_path = self.song_downloader.get_decrypted_path(track["id"])
            self.song_downloader.decrypt(encrypted_path, decrypted_path, key)
            self.song_downloader.remux(decrypted_path, final_path, stream_info.codec)
        else:
            encrypted_path.rename(final_path)
        
        return final_path

    def _generate_tags(self, webplayback: dict) -> dict:
        metadata = webplayback["assets"][0]["metadata"]
        return {
            "title": metadata.get("itemName", "Unknown"),
            "artist": metadata.get("artistName", "Unknown"),
            "album": metadata.get("playlistName", "Unknown"),
            "track_number": metadata.get("trackNumber", 1),
        }

    def cleanup(self):
        shutil.rmtree(Config.TEMP_DIR, ignore_errors=True)
        Config.TEMP_DIR.mkdir(exist_ok=True)
