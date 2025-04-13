from pathlib import Path
from typing import Optional
from .apple_music_api import AppleMusicApi
from .downloader_song import DownloaderSong
from .downloader_song_legacy import DownloaderSongLegacy
from .enums import SongCodec, DownloadMode, RemuxMode
from .models import DownloadQueue, UrlInfo

class Downloader:
    def __init__(self, apple_music_api: AppleMusicApi):
        self.am_api = apple_music_api
        self.base_downloader = BaseDownloader(
            apple_music_api=am_api,
            output_path=Path("./downloads"),
            temp_path=Path("./temp"),
            download_mode=DownloadMode.YTDLP,
            remux_mode=RemuxMode.FFMPEG,
            codec=SongCodec.AAC,
            silent=True
        )
        self._init_downloader()

    def _init_downloader(self):
        if self.base_downloader.codec in [SongCodec.AAC_LEGACY, SongCodec.AAC_HE_LEGACY]:
            self.song_downloader = DownloaderSongLegacy(self.base_downloader)
            self.base_downloader.set_cdm(legacy=True)
        else:
            self.song_downloader = DownloaderSong(self.base_downloader)

    def process(self, url: str, user_id: int) -> Path:
        try:
            url_info = self.base_downloader.get_url_info(url)
            queue = self.base_downloader.get_download_queue(url_info)
            
            if not queue.tracks_metadata:
                raise ValueError("No tracks found")
            
            track = queue.tracks_metadata[0]
            return self._download_track(track)
        except Exception as e:
            raise DownloadError(str(e))

    def _download_track(self, track: dict) -> Path:
        # ... [Modern download logic] ...
        if self.base_downloader.codec in [SongCodec.AAC_LEGACY, SongCodec.AAC_HE_LEGACY]:
            return self._legacy_download(track)
        # ... [Modern download logic continues] ...

    def _legacy_download(self, track: dict) -> Path:
        stream_info = self.song_downloader.get_stream_info(track)
        # ... [Legacy specific download steps] ...
