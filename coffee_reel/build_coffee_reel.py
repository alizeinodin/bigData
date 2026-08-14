#!/usr/bin/env python3
"""Build professional viral Persian Instagram Reel for cafejoon.ir."""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from text_render import paste_text_on_image

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "output"
TMP = OUT / "tmp"
BG_MUSIC = ASSETS / "bg_music.mp3"
VOICE = "fa-IR-FaridNeural"
TTS_RATE = "+25%"
WIDTH, HEIGHT = 1080, 1920
FPS = 30
BRAND = "cafejoon.ir"
XFADE = 0.10
ACCENT = (1.0, 0.78, 0.35)
WHITE = (1.0, 1.0, 1.0)
CREAM = (1.0, 0.97, 0.93)

# Algorithm-optimized: hook <2s, cuts ~2s, save CTA, comment bait, brand
SCENES = [
    {
        "id": "01_hook",
        "image": "scene-espresso.png",
        "badge": "قهوه",
        "title": "۹۰٪ اشتباه سفارش می‌دن!",
        "subtitle": "۳ ثانیه بعد می‌فهمی چرا 👇",
        "voice": "۹۰ درصد آدما اشتباه قهوه سفارش می‌دن! این سه ثانیه رو از دست نده.",
        "min_duration": 2.1,
        "zoom": 0.0016,
    },
    {
        "id": "02_date",
        "image": "scene-latte.png",
        "badge": "۱/۴",
        "title": "قرار اول؟",
        "subtitle": "لاته ☕",
        "voice": "قرار اول؟ لاته. امن و همیشه جواب می‌ده.",
        "min_duration": 1.9,
        "zoom": 0.0010,
    },
    {
        "id": "03_work",
        "image": "scene-americano.png",
        "badge": "۲/۴",
        "title": "می‌خوای کار کنی؟",
        "subtitle": "آمریکانو 💻",
        "voice": "کار کردن؟ آمریکانو. سبک و بدون خواب‌آلودگی.",
        "min_duration": 1.9,
        "zoom": 0.0010,
    },
    {
        "id": "04_rush",
        "image": "scene-espresso.png",
        "badge": "۳/۴",
        "title": "عجله داری؟",
        "subtitle": "اسپرسو ⚡",
        "voice": "عجله؟ اسپرسو. یک جرعه، تمام.",
        "min_duration": 1.7,
        "zoom": 0.0012,
    },
    {
        "id": "05_sweet",
        "image": "scene-mocha.png",
        "badge": "۴/۴",
        "title": "شیرینی‌خور؟",
        "subtitle": "موکا 🍫",
        "voice": "شیرین‌کار؟ موکا. مثل دسره.",
        "min_duration": 1.7,
        "zoom": 0.0010,
    },
    {
        "id": "06_save",
        "image": "scene-cappuccino.png",
        "badge": "سیو کن",
        "title": "سیو کن 🔖",
        "subtitle": "۱ لاته  ۲ آمریکانو  ۳ اسپرسو  ۴ موکا\nکامنت کن کدوم شماره‌اته!",
        "voice": "سیو کن! کدوم شماره‌اته؟ توی کامنت بنویس.",
        "min_duration": 2.2,
        "zoom": 0.0009,
    },
    {
        "id": "07_brand",
        "image": "coffee-reel-cover.png",
        "badge": BRAND,
        "title": "بهترین کافه شهرت؟",
        "subtitle": f"→ {BRAND}\nکافه‌داری؟ برای همکاری پیام بده",
        "voice": f"بهترین کافه نزدیکت رو توی {BRAND} پیدا کن. کافه‌داری؟ بیا همکاری کنیم.",
        "min_duration": 2.6,
        "zoom": 0.0008,
    },
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def draw_rounded_rect(draw: ImageDraw.ImageDraw, box: tuple, radius: int, fill: tuple) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def render_scene_image(scene: dict, index: int, total: int) -> Path:
    base = Image.open(ASSETS / scene["image"]).convert("RGB")
    base = ImageEnhance.Contrast(base).enhance(1.12)
    base = ImageEnhance.Color(base).enhance(1.1)
    base = base.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    base = base.filter(ImageFilter.GaussianBlur(radius=0.3))
    base = base.convert("RGBA")

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 45))
    draw.rectangle((0, 0, WIDTH, 500), fill=(0, 0, 0, 175))
    draw.rectangle((0, HEIGHT - 760, WIDTH, HEIGHT), fill=(0, 0, 0, 190))

    progress_w = int((WIDTH - 120) * (index + 1) / total)
    draw.rounded_rectangle((60, HEIGHT - 48, WIDTH - 60, HEIGHT - 28), radius=10, fill=(255, 255, 255, 60))
    draw.rounded_rectangle((60, HEIGHT - 48, 60 + progress_w, HEIGHT - 28), radius=10, fill=(255, 190, 80, 220))

    draw_rounded_rect(draw, (48, 52, 300, 128), 28, (255, 190, 80, 230))
    base = Image.alpha_composite(base, overlay)

    paste_text_on_image(base, scene["badge"], y_center=90, font_size=38, bold=True, color=(0.12, 0.08, 0.05), x_center=174)

    paste_text_on_image(base, scene["title"], y_center=210, font_size=92, bold=True, color=ACCENT)
    paste_text_on_image(base, scene["subtitle"], y_center=HEIGHT - 340, font_size=56, bold=False, color=WHITE)

    if scene["id"] != "07_brand":
        paste_text_on_image(base, BRAND, y_center=HEIGHT - 95, font_size=36, bold=True, color=(0.95, 0.85, 0.68))

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
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def mix_voice_with_music(voice: Path, duration: float, scene_id: str, music_offset: float) -> Path:
    out = TMP / f"{scene_id}_audio.m4a"
    music_vol = "0.20" if scene_id == "01_hook" else "0.15"
    run([
        "ffmpeg", "-y",
        "-i", str(voice),
        "-ss", f"{music_offset:.3f}",
        "-stream_loop", "-1", "-i", str(BG_MUSIC),
        "-filter_complex",
        (
            f"[1:a]atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,volume={music_vol}[bg];"
            f"[0:a]volume=1.05,highpass=f=80[v];"
            f"[bg][v]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        ),
        "-map", "[aout]", "-t", f"{duration:.3f}",
        "-c:a", "aac", "-b:a", "192k",
        str(out),
    ])
    return out


def build_scene_clip(scene: dict, image_path: Path, audio_path: Path, duration: float) -> Path:
    frames = max(int(duration * FPS), 1)
    clip = TMP / f"{scene['id']}_clip.mp4"
    zoom = scene.get("zoom", 0.0010)

    run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-i", str(audio_path),
        "-filter_complex",
        (
            f"[0:v]scale=1280:2280,crop=1080:1920,"
            f"zoompan=z='min(zoom+{zoom},1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s=1080x1920:fps={FPS},"
            f"eq=brightness=0.02:saturation=1.08,format=yuv420p[v]"
        ),
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{duration:.3f}",
        str(clip),
    ])
    return clip


def concat_with_xfade(clips: list[Path], durations: list[float], output: Path) -> None:
    if len(clips) == 1:
        run(["ffmpeg", "-y", "-i", str(clips[0]), "-c", "copy", str(output)])
        return

    inputs: list[str] = []
    for c in clips:
        inputs.extend(["-i", str(c)])

    v_filters: list[str] = []
    a_filters: list[str] = []
    offset = durations[0] - XFADE
    v_prev = "[0:v]"
    a_prev = "[0:a]"

    for i in range(1, len(clips)):
        v_out = f"[v{i}]" if i < len(clips) - 1 else "[vout]"
        a_out = f"[a{i}]" if i < len(clips) - 1 else "[aout]"
        v_filters.append(
            f"{v_prev}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}{v_out}"
        )
        a_filters.append(
            f"{a_prev}[{i}:a]acrossfade=d={XFADE}:c1=tri:c2=tri{a_out}"
        )
        v_prev = v_out
        a_prev = a_out
        if i < len(clips) - 1:
            offset += durations[i] - XFADE

    fc = ";".join(v_filters + a_filters)
    run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        str(output),
    ])


def generate_bg_music() -> None:
    """Warm lo-fi bed track for cafe reels."""
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "sine=frequency=196:duration=90",
        "-f", "lavfi", "-i", "sine=frequency=247:duration=90",
        "-f", "lavfi", "-i", "sine=frequency=294:duration=90",
        "-f", "lavfi", "-i", "anoisesrc=d=90:c=brown:a=0.006",
        "-filter_complex",
        (
            "[0:a][1:a][2:a]amix=inputs=3:weights=0.35 0.3 0.25,volume=0.07[tones];"
            "[tones][3:a]amix=inputs=2:duration=first,volume=0.9,"
            "lowpass=f=900,highpass=f=120,"
            "afade=t=in:st=0:d=1.5,afade=t=out:st=88:d=2"
        ),
        "-c:a", "libmp3lame", "-b:a", "160k",
        str(BG_MUSIC),
    ])


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    generate_bg_music()

    clips: list[Path] = []
    durations: list[float] = []
    music_offset = 0.0
    total = len(SCENES)

    for i, scene in enumerate(SCENES):
        print(f"Rendering {scene['id']}...")
        image_path = render_scene_image(scene, i, total)
        voice_path = await synthesize_voice(scene)
        duration = max(scene["min_duration"], media_duration(voice_path) + 0.02)
        audio_path = mix_voice_with_music(voice_path, duration, scene["id"], music_offset)
        clip = build_scene_clip(scene, image_path, audio_path, duration)
        clips.append(clip)
        durations.append(duration)
        music_offset += duration

    final = OUT / "cafejoon_pro_reel_fa.mp4"
    concat_with_xfade(clips, durations, final)
    print(f"Done: {final} ({media_duration(final):.1f}s)")


if __name__ == "__main__":
    asyncio.run(main())
