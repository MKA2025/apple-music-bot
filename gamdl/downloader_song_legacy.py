import m3u8
import subprocess
from pathlib import Path
from typing import Optional
from .enums import SongCodec
from .models import StreamInfo
from .downloader_song import DownloaderSong
from .apple_music_api import AppleMusicApi

class DownloaderSongLegacy(DownloaderSong):
    CODEC_MAP = {
        SongCodec.AAC_LEGACY: "28:ctrp256",
        SongCodec.AAC_HE_LEGACY: "32:ctrp64"
    }

    def __init__(self, downloader):
        super().__init__(downloader)
        self.logger = downloader.logger

    def get_stream_info(self, track_metadata: dict) -> StreamInfo:
        stream_info = StreamInfo()
        try:
            webplayback = self.downloader.apple_music_api.get_webplayback(track_metadata["id"])
            flavor = self.CODEC_MAP[self.downloader.codec]
            
            for asset in webplayback.get("assets", []):
                if asset.get("flavor") == flavor:
                    stream_info.stream_url = asset["URL"]
                    stream_info.widevine_pssh = self._extract_pssh(stream_info.stream_url)
                    return stream_info
            raise ValueError("Legacy stream not found")
        except Exception as e:
            self.logger.error(f"Legacy stream error: {str(e)}")
            raise

    def _extract_pssh(self, stream_url: str) -> Optional[str]:
        try:
            playlist = m3u8.load(stream_url)
            return playlist.keys[0].uri if playlist.keys else None
        except Exception as e:
            self.logger.error(f"PSSH extraction failed: {str(e)}")
            return None

    def decrypt(self, encrypted_path: Path, decrypted_path: Path, key: str):
        subprocess.run([
            self.downloader.mp4decrypt_path_full,
            encrypted_path,
            "--key", f"1:{key}",
            decrypted_path
        ], check=True, **self.downloader.subprocess_additional_args)
