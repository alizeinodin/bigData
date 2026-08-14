#!/usr/bin/env python3
"""Build viral Persian Instagram Reel for cafejoon.ir."""

from __future__ import annotations

import asyncio
import io
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageEnhance

from text_render import paste_text_on_image

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "output"
TMP = OUT / "tmp"
BG_MUSIC = ASSETS / "bg_music.mp3"
VOICE = "fa-IR-FaridNeural"
TTS_RATE = "+22%"
WIDTH, HEIGHT = 1080, 1920
FPS = 30
BRAND = "cafejoon.ir"

# Viral format: hook → fast personality beats → save CTA → brand (user + cafe owner)
SCENES = [
    {
        "id": "01_hook",
        "image": "scene-espresso.png",
        "title": "❌ اینو قاطی نکن!",
        "subtitle": "لاته ≠ کاپوچینو",
        "voice": "لاته و کاپوچینو رو قاطی می‌کنی؟ این ویدیو مال توئه!",
        "min_duration": 2.0,
    },
    {
        "id": "02_date",
        "image": "scene-latte.png",
        "title": "قرار اول؟",
        "subtitle": "→ لاته ☕",
        "voice": "قرار اول؟ لاته. نرم و همیشه جواب می‌ده.",
        "min_duration": 1.9,
    },
    {
        "id": "03_work",
        "image": "scene-americano.png",
        "title": "می‌خوای کار کنی؟",
        "subtitle": "→ آمریکانو 💻",
        "voice": "کار کردن؟ آمریکانو. سبک و بدون خواب‌آلودگی.",
        "min_duration": 1.9,
    },
    {
        "id": "04_rush",
        "image": "scene-espresso.png",
        "title": "عجله داری؟",
        "subtitle": "→ اسپرسو ⚡",
        "voice": "عجله؟ اسپرسو. یک جرعه، تمام.",
        "min_duration": 1.7,
    },
    {
        "id": "05_sweet",
        "image": "scene-mocha.png",
        "title": "شیرینی‌خور؟",
        "subtitle": "→ موکا 🍫",
        "voice": "شیرینی‌خور؟ موکا. مثل دسره.",
        "min_duration": 1.7,
    },
    {
        "id": "06_summer",
        "image": "scene-coldbrew.png",
        "title": "هواش گرمه؟",
        "subtitle": "→ کولد برو 🧊",
        "voice": "گرما؟ کولد برو. خنک و اعتیادآور.",
        "min_duration": 1.7,
    },
    {
        "id": "07_save",
        "image": "scene-cappuccino.png",
        "title": "سیو کن 🔖",
        "subtitle": "برای دفعه بعد که سفارش می‌دی",
        "voice": "سیو کن. دفعه بعد دقیق سفارش بده.",
        "min_duration": 1.9,
    },
    {
        "id": "08_brand",
        "image": "coffee-reel-cover.png",
        "title": "بهترین کافه شهرت؟",
        "subtitle": f"→ {BRAND}\nکافه‌داری؟ باهامون همکاری کن ☕",
        "voice": f"کافه نزدیکت رو توی {BRAND} پیدا کن. کافه‌داری؟ بیا همکاری کنیم.",
        "min_duration": 2.8,
    },
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def render_scene_image(scene: dict) -> Path:
    base = Image.open(ASSETS / scene["image"]).convert("RGB")
    base = ImageEnhance.Contrast(base).enhance(1.1)
    base = ImageEnhance.Color(base).enhance(1.08)
    base = base.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).convert("RGBA")

    # Dark bands for readable text
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    from PIL import ImageDraw

    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, WIDTH, 480), fill=(0, 0, 0, 165))
    draw.rectangle((0, HEIGHT - 700, WIDTH, HEIGHT), fill=(0, 0, 0, 180))
    base = Image.alpha_composite(base, overlay)

    paste_text_on_image(base, scene["title"], y_center=200, font_size=86, bold=True, color=(1, 0.97, 0.93))
    paste_text_on_image(base, scene["subtitle"], y_center=HEIGHT - 320, font_size=58, bold=False, color=(1, 1, 1))

    # Brand watermark on all scenes except final
    if scene["id"] != "08_brand":
        paste_text_on_image(base, BRAND, y_center=HEIGHT - 80, font_size=34, bold=True, color=(0.95, 0.85, 0.7))

    out = TMP / f"{scene['id']}.png"
    base.convert("RGB").save(out, quality=96)
    return out


async def synthesize_voice(scene: dict) -> Path:
    out = TMP / f"{scene['id']}_voice.mp3"
    communicate = edge_tts.Communicate(scene["voice"], VOICE, rate=TTS_RATE)
    await communicate.save(str(out))
    return out


def media_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(result.stdout.strip())


def mix_voice_with_music(voice: Path, duration: float, scene_id: str) -> Path:
    """Mix voiceover with ducked background music."""
    out = TMP / f"{scene_id}_audio.m4a"
    music_vol = "0.18" if scene_id == "01_hook" else "0.14"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(voice),
            "-stream_loop",
            "-1",
            "-i",
            str(BG_MUSIC),
            "-filter_complex",
            (
                f"[1:a]atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,volume={music_vol}[bg];"
                f"[0:a]volume=1.0[v];"
                f"[bg][v]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            ),
            "-map",
            "[aout]",
            "-t",
            f"{duration:.3f}",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(out),
        ]
    )
    return out


def build_scene_clip(scene: dict, image_path: Path, audio_path: Path, duration: float) -> Path:
    frames = max(int(duration * FPS), 1)
    clip = TMP / f"{scene['id']}_clip.mp4"
    zoom_speed = "0.0012" if scene["id"] == "01_hook" else "0.0009"

    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(image_path),
            "-i",
            str(audio_path),
            "-filter_complex",
            (
                f"[0:v]scale=1250:2220,crop=1080:1920,"
                f"zoompan=z='min(zoom+{zoom_speed},1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={frames}:s=1080x1920:fps={FPS},format=yuv420p[v]"
            ),
            "-map",
            "[v]",
            "-map",
            "1:a",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "19",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            f"{duration:.3f}",
            str(clip),
        ]
    )
    return clip


def concat_clips(clips: list[Path], output: Path) -> None:
    list_file = TMP / "concat.txt"
    list_file.write_text("\n".join(f"file '{c}'" for c in clips), encoding="utf-8")
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c",
            "copy",
            str(output),
        ]
    )


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    if not BG_MUSIC.exists():
        raise FileNotFoundError(f"Background music missing: {BG_MUSIC}")

    clips: list[Path] = []
    for scene in SCENES:
        print(f"Rendering {scene['id']}...")
        image_path = render_scene_image(scene)
        voice_path = await synthesize_voice(scene)
        duration = max(scene["min_duration"], media_duration(voice_path) + 0.05)
        audio_path = mix_voice_with_music(voice_path, duration, scene["id"])
        clip = build_scene_clip(scene, image_path, audio_path, duration)
        clips.append(clip)

    final = OUT / "cafejoon_viral_reel_fa.mp4"
    concat_clips(clips, final)
    print(f"Done: {final} ({media_duration(final):.1f}s)")


if __name__ == "__main__":
    asyncio.run(main())
