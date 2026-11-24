#!/usr/bin/env python3
"""Local background removal CLI using rembg + local model weights.

Usage:
  rembg_cutout.py INPUT -o OUTPUT [--model birefnet-general|isnet-general-use]
                                  [--models-dir DIR] [--bg transparent|#RRGGBB]

INPUT may be a single image file or a directory of images (batch mode).
"""

import argparse
import os
import sys
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
DEFAULT_MODELS_DIR = Path(
    os.environ.get("REMBG_MODELS_DIR", str(Path.home() / ".local/share/rembg/models"))
)
DEFAULT_VENV_PY = Path(
    os.environ.get("REMBG_VENV_PY", str(Path.home() / ".local/share/rembg-venv/bin/python"))
)

INSTALL_HINT = (
    "rembg is not installed in this Python environment.\n"
    "Install it into the dedicated venv:\n"
    "  uv venv ~/.local/share/rembg-venv --python 3.12\n"
    '  uv pip install --python ~/.local/share/rembg-venv/bin/python "rembg[cpu]" pillow\n'
)


def _maybe_reexec_venv() -> None:
    """If rembg is missing in current Python, transparently re-exec in rembg-venv."""
    if os.environ.get("_REMBG_CUTOUT_REEXEC") == "1":
        return
    try:
        import rembg  # noqa: F401
        return
    except ImportError:
        if DEFAULT_VENV_PY.exists() and Path(sys.executable).resolve() != DEFAULT_VENV_PY.resolve():
            env = {**os.environ, "_REMBG_CUTOUT_REEXEC": "1"}
            os.execve(str(DEFAULT_VENV_PY), [str(DEFAULT_VENV_PY), __file__, *sys.argv[1:]], env)


def _resolve_u2net_home(models_dir: Path, model: str) -> Path:
    """Support both <models_dir>/<model>/<model>.onnx and <models_dir>/<model>.onnx."""
    nested = models_dir / model
    if (nested / f"{model}.onnx").exists():
        return nested
    return models_dir


def _parse_hex_color(value: str) -> tuple[int, int, int]:
    cleaned = value.strip().lstrip("#")
    if len(cleaned) != 6:
        raise ValueError(f"Expected 6-digit hex color like #FFFFFF, got: {value}")
    return int(cleaned[0:2], 16), int(cleaned[2:4], 16), int(cleaned[4:6], 16)


def _process_file(src: Path, dst: Path, session, bg_rgb: tuple[int, int, int] | None) -> None:
    from PIL import Image
    from rembg import remove

    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        rgba = remove(img.convert("RGBA"), session=session)
        if bg_rgb is not None:
            canvas = Image.new("RGBA", rgba.size, (*bg_rgb, 255))
            canvas.alpha_composite(rgba)
            out = canvas.convert("RGB")
        else:
            out = rgba
        out.save(dst)


def main() -> int:
    _maybe_reexec_venv()

    parser = argparse.ArgumentParser(description="Remove backgrounds locally with rembg.")
    parser.add_argument("input", type=Path, help="Input image file or directory of images.")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output file or directory.")
    parser.add_argument(
        "--model",
        default="birefnet-general",
        choices=["birefnet-general", "isnet-general-use"],
        help="Local rembg model to use (default: birefnet-general).",
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=DEFAULT_MODELS_DIR,
        help=f"Directory holding model weights (default: {DEFAULT_MODELS_DIR}).",
    )
    parser.add_argument(
        "--bg",
        default="transparent",
        help="Background fill: 'transparent' (default) or hex color like '#FFFFFF' / '#00FF00'.",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input path not found: {args.input}", file=sys.stderr)
        return 1

    bg_rgb = None if args.bg.lower() == "transparent" else _parse_hex_color(args.bg)

    u2net_home = _resolve_u2net_home(args.models_dir, args.model)
    os.environ["U2NET_HOME"] = str(u2net_home)

    try:
        from rembg import new_session
    except ImportError:
        print(INSTALL_HINT, file=sys.stderr)
        return 2

    session = new_session(args.model)

    if args.input.is_file():
        dst = args.output / f"{args.input.stem}.png" if args.output.is_dir() else args.output
        _process_file(args.input, dst, session, bg_rgb)
        print(f"Saved: {dst}")
        return 0

    files = sorted(p for p in args.input.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS)
    if not files:
        print(f"No supported image files found in {args.input}", file=sys.stderr)
        return 1

    args.output.mkdir(parents=True, exist_ok=True)
    for idx, src in enumerate(files, 1):
        dst = args.output / f"{src.stem}.png"
        _process_file(src, dst, session, bg_rgb)
        print(f"[{idx}/{len(files)}] {src.name} -> {dst.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
