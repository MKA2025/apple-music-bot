from enum import Enum

class DownloadMode(Enum):
    YTDLP = "ytdlp"
    NM3U8DLRE = "nm3u8dlre"

class RemuxMode(Enum):
    FFMPEG = "ffmpeg"
    MP4BOX = "mp4box"

class SongCodec(Enum):
    AAC = "aac"
    AAC_HE = "aac-he"
    ALAC = "alac"
    ATMOS = "atmos"
    AAC_LEGACY = "aac-legacy"
    AAC_HE_LEGACY = "aac-he-legacy"
    ASK = "ask"

    @property
    def display_name(self):
        names = {
            "aac": "🎵 AAC 256kbps",
            "aac-he": "🔥 HE-AAC 128kbps",
            "alac": "💎 ALAC Lossless",
            "atmos": "🌌 Dolby Atmos",
            "aac-legacy": "🕰 AAC Legacy",
            "aac-he-legacy": "⏳ HE-AAC Legacy",
            "ask": "❓ Ask Every Time"
        }
        return names[self.value]

class MusicVideoCodec(Enum):
    H264 = "h264"
    H265 = "h265"
    ASK = "ask"

class CoverFormat(Enum):
    JPG = "jpg"
    PNG = "png"
    RAW = "raw"

class SyncedLyricsFormat(Enum):
    LRC = "lrc"
    SRT = "srt"
    TTML = "ttml"
