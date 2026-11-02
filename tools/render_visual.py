"""Procedural raster artwork and ffmpeg media steps.

The painter is original and deterministic. It draws a walking path of steps
across an ivory lane, with brass change marks. It is an illustration,
not a photograph of a session or of performers.

DejaVu Sans Bold is used only to rasterize the disclosure into the film and the
poster. The font file is not shipped.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ON_PICTURE = "preview, not master"


def _clamp(value: int) -> int:
    return 0 if value < 0 else 255 if value > 255 else value


def paint(width: int, height: int, framing: str) -> bytes:
    steps = 32
    heights = (
        0.62, 0.48, 0.36, 0.42, 0.55, 0.46, 0.34, 0.50,
        0.44, 0.30, 0.38, 0.52, 0.58, 0.40, 0.28, 0.46,
        0.50, 0.36, 0.42, 0.60, 0.48, 0.32, 0.40, 0.54,
        0.46, 0.34, 0.28, 0.44, 0.56, 0.38, 0.30, 0.48,
    )
    margin_x = int(width * (0.08 if framing == "wide" else 0.1))
    lane_top = int(height * (0.28 if framing == "square" else 0.34))
    lane_bottom = int(height * (0.78 if framing == "square" else 0.74))
    span = max(1, width - margin_x * 2)
    dot = max(4, width // 160)
    pixels = bytearray(width * height * 3)
    for y in range(height):
        shade = y / max(1, height - 1)
        base_r = int(22 + 10 * shade)
        base_g = int(18 + 8 * shade)
        base_b = int(14 + 6 * shade)
        row = y * width * 3
        for x in range(width):
            r, g, b = base_r, base_g, base_b
            if lane_top <= y <= lane_bottom and margin_x <= x <= width - margin_x:
                r, g, b = 243, 239, 228
            pixels[row + x * 3] = r
            pixels[row + x * 3 + 1] = g
            pixels[row + x * 3 + 2] = b
    points = []
    for index, level in enumerate(heights):
        cx = int(margin_x + span * (index + 0.5) / steps)
        cy = int(lane_top + level * (lane_bottom - lane_top))
        points.append((cx, cy))
        if index % 8 == 0:
            for y in range(lane_top, lane_bottom + 1):
                for x in range(cx - 1, cx + 2):
                    if 0 <= x < width:
                        offset = (y * width + x) * 3
                        pixels[offset] = 122
                        pixels[offset + 1] = 46
                        pixels[offset + 2] = 42
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        run = max(1, abs(x1 - x0))
        for step in range(run + 1):
            x = x0 + (x1 - x0) * step // run
            y = y0 + (y1 - y0) * step // run
            if 0 <= x < width and 0 <= y < height:
                offset = (y * width + x) * 3
                pixels[offset] = 90
                pixels[offset + 1] = 68
                pixels[offset + 2] = 40
    for index, (cx, cy) in enumerate(points):
        color = (176, 141, 87) if index % 4 else (122, 46, 42)
        radius = dot + (1 if index % 4 == 0 else 0)
        for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(width, cx + radius + 1)):
                if (x - cx) * (x - cx) + (y - cy) * (y - cy) <= radius * radius:
                    offset = (y * width + x) * 3
                    pixels[offset] = color[0]
                    pixels[offset + 1] = color[1]
                    pixels[offset + 2] = color[2]
    return bytes(pixels)


def write_ppm(path: Path, width: int, height: int, rgb: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = f"P6\n{width} {height}\n255\n".encode("ascii")
    path.write_bytes(header + rgb)


def run(command: list[str]) -> None:
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "command failed\n"
            + " ".join(command)
            + "\n"
            + completed.stderr[-2000:]
        )


def ppm_to_jpeg(ppm: Path, jpeg: Path, quality: int = 3) -> None:
    jpeg.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-i", str(ppm), "-frames:v", "1", "-q:v", str(quality), str(jpeg)])


def draw_disclosure(source: Path, dest: Path, textfile: Path) -> list[str]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y", "-i", str(source),
        "-vf",
        (
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-frames:v", "1",
        "-q:v", "3",
        str(dest),
    ]
    run(command)
    return command


def encode_mp3(wav: Path, mp3: Path) -> list[str]:
    mp3.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg", "-y", "-i", str(wav),
        "-codec:a", "libmp3lame", "-b:a", "192k",
        str(mp3),
    ]
    run(command)
    return command


def encode_film(plate: Path, mp3: Path, mp4: Path, textfile: Path, duration: str) -> list[str]:
    mp4.parent.mkdir(parents=True, exist_ok=True)
    textfile.write_text(ON_PICTURE + "\n", encoding="utf-8")
    command = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "24", "-i", str(plate),
        "-i", str(mp3),
        "-t", duration,
        "-vf",
        (
            "scale=1280:720,"
            f"drawtext=textfile={textfile}:fontfile={FONT}:fontsize=48:"
            "fontcolor=white:x=(w-text_w)/2:y=h-100:box=1:boxcolor=black@0.68:boxborderw=22"
        ),
        "-r", "24",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest",
        "-movflags", "+faststart",
        str(mp4),
    ]
    run(command)
    return command


def derive_social(hero: Path, square: Path, portrait: Path, card: Path) -> dict[str, list[str]]:
    portrait.parent.mkdir(parents=True, exist_ok=True)
    card.parent.mkdir(parents=True, exist_ok=True)
    portrait_cmd = [
        "ffmpeg", "-y", "-i", str(square),
        "-vf", "crop=864:1080:108:0,scale=1080:1350",
        "-q:v", "3",
        str(portrait),
    ]
    card_cmd = [
        "ffmpeg", "-y", "-i", str(hero),
        "-vf", "scale=1600:900",
        "-q:v", "3",
        str(card),
    ]
    run(portrait_cmd)
    run(card_cmd)
    return {"portrait": portrait_cmd, "card": card_cmd}
