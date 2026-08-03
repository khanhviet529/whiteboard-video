"""Sinh giong doc tieng Viet bang edge-tts (mien phi, khong can API key).

Mat xich quan trong nhat cua tool: sinh audio TRUOC, do duration THAT, roi
lay do lam thoi luong canh. Nho vay khong bao gio phai canh timing bang tay.

Ket qua duoc cache theo hash noi dung -> render lai khong goi mang lai.
"""
import asyncio
import hashlib
import os
import subprocess
import wave

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

VOICES = {
    "female": "vi-VN-HoaiMyNeural",
    "male": "vi-VN-NamMinhNeural",
}
SR = 48000  # tan so lay mau chuan cho mp4


def _key(text, voice, rate, pitch):
    h = hashlib.sha1(f"{text}|{voice}|{rate}|{pitch}".encode("utf-8")).hexdigest()
    return h[:16]


async def _synth(text, voice, rate, pitch, out_mp3):
    import edge_tts
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await c.save(out_mp3)


def speak(text, cache_dir, voice="female", rate="+6%", pitch="+0Hz"):
    """text -> (duong_dan_wav, so_giay). Tra ve (None, 0) neu text rong."""
    text = (text or "").strip()
    if not text:
        return None, 0.0
    os.makedirs(cache_dir, exist_ok=True)
    v = VOICES.get(voice, voice)
    k = _key(text, v, rate, pitch)
    mp3 = os.path.join(cache_dir, f"{k}.mp3")
    wav = os.path.join(cache_dir, f"{k}.wav")

    if not os.path.exists(wav):
        if not os.path.exists(mp3):
            asyncio.run(_synth(text, v, rate, pitch, mp3))
        subprocess.run(
            [FFMPEG, "-y", "-loglevel", "error", "-i", mp3,
             "-ar", str(SR), "-ac", "2", wav],
            check=True)

    with wave.open(wav, "rb") as w:
        dur = w.getnframes() / w.getframerate()
    return wav, dur


def silence(seconds, path):
    """Tao doan im lang de chen truoc/sau moi cau."""
    n = int(SR * seconds)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"\x00\x00\x00\x00" * n)
    return path


def concat(segments, out_path):
    """Noi cac doan wav (48k stereo 16-bit) thanh mot track duy nhat."""
    with wave.open(out_path, "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(SR)
        for kind, val in segments:
            if kind == "silence":
                out.writeframes(b"\x00\x00\x00\x00" * int(SR * val))
            else:
                with wave.open(val, "rb") as w:
                    out.writeframes(w.readframes(w.getnframes()))
    return out_path
