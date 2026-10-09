#!/usr/bin/env python3
"""Make anything Resolve-ready and import it into the Master bin, in one command.

Usage:
  add-media.py [options] ITEM [ITEM ...]

ITEM is a file or a URL:
  video (mp4, webm, mkv, H.264 .mov...)  -> ProRes LT .mov (free Resolve on Linux can't decode H.264/AAC)
  ProRes / DNxHR .mov, wav, mp3, png, jpg -> imported as is
  webp, avif, heic, gif image             -> png (alpha kept)
  m4a, aac, ogg, opus, flac audio         -> wav 48 kHz
  URL (YouTube...)                        -> mp3 via yt-dlp (--video for the picture too)

Options:
  -o DIR          where converted files go (default: <project>/resolve-media, the folder above the first file
                  holding AGENTS.md / PLAN.md / project.conf, else next to the file)
  --no-audio      drop the clips' own sound (AI clips under a voiceover)
  --upscale       scale video to 1080 wide (Lanczos) when it is smaller (a 720p take)
  --speed X       audio and video sped up by X (1.1 = 10 % faster, pitch kept); file gets -speed110
  --video         for URLs: keep the video (as ProRes) instead of mp3 only
  --no-import     convert only
Imports go to the Master (root) bin of the open project, skip files already in the pool, then save.
It never touches a timeline. Needs the bridge running in Resolve (Workspace > Scripts > claude_bridge).
"""
import argparse, os, subprocess, sys
from pathlib import Path

for p in (os.path.expanduser("~/.local/share/davinci-resolve-mcp/lua_bridge/Modules"),
          os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bridge")):
    if os.path.isfile(os.path.join(p, "resolve_lua_bridge.py")):
        sys.path.insert(0, p)
        break

AS_IS = {".wav", ".mp3", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".exr"}
IMAGE = {".webp", ".avif", ".heic", ".gif", ".bmp"}
AUDIO = {".m4a", ".aac", ".ogg", ".opus", ".flac", ".wma"}


def run(*cmd):
    subprocess.run(cmd, check=True)


def vcodec(f):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name,width",
                           "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.strip().split(",")


def has_audio(f):
    return bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                                "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.strip())


def project_dir(f):
    for d in [f.parent, *f.parent.parents]:
        if any((d / m).is_file() for m in ("AGENTS.md", "PLAN.md", "project.conf")):
            return d
    return None


def atempo(x):
    return f"atempo={x}"   # one atempo handles 0.5-100


def to_prores(src, out, a):
    codec, width = (vcodec(src) + ["", ""])[:2]
    vf = []
    if a.upscale and width and int(width) < 1080:
        vf.append("scale=1080:-2:flags=lanczos")
    if a.speed != 1:
        vf.append(f"setpts=PTS/{a.speed}")
    keep = not a.no_audio and has_audio(src)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src)]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    cmd += ["-c:v", "prores_aw", "-profile:v", "1", "-pix_fmt", "yuv422p10le", "-vendor", "apl0"]
    cmd += (["-c:a", "pcm_s16le", "-ar", "48000"] + (["-af", atempo(a.speed)] if a.speed != 1 else [])) if keep else ["-an"]
    tmp = out.with_suffix(".tmp.mov")
    run(*cmd, str(tmp))
    tmp.rename(out)


def prepare(item, a):
    """-> path Resolve can import."""
    tag = f"-speed{round(a.speed * 100)}" if a.speed != 1 else ""
    if item.startswith(("http://", "https://")):
        pd = project_dir(Path.cwd() / "x")
        out = Path(a.o).resolve() if a.o else (pd / "resolve-media" if pd else Path.cwd())
        out.mkdir(parents=True, exist_ok=True)
        base = ["yt-dlp", "--no-playlist", "--extractor-args", "youtube:player_client=mweb",   # default client: 403
                "-o", str(out / "%(title).60s.%(ext)s"), "--print", "after_move:filepath"]
        fmt = ["-f", "bv*+ba/b", "--merge-output-format", "mp4"] if a.video else ["-x", "--audio-format", "mp3"]
        got = Path(subprocess.run(base + fmt + [item], check=True, capture_output=True, text=True).stdout.strip().splitlines()[-1])
        return prepare(str(got), a) if a.video or a.speed != 1 else got
    src = Path(item).resolve()
    if not src.is_file():
        sys.exit(f"missing {src}")
    pd = project_dir(src)
    out_dir = Path(a.o).resolve() if a.o else (pd / "resolve-media" if pd else src.parent)
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = src.suffix.lower()
    if ext in IMAGE:
        out = out_dir / f"{src.stem}.png"
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-frames:v", "1", "-pix_fmt", "rgba", str(out))
        return out
    if ext in AS_IS or ext in AUDIO:
        if ext in AS_IS and a.speed == 1:
            return src
        out = out_dir / f"{src.stem}{tag}.wav"
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-vn",
            *(["-af", atempo(a.speed)] if a.speed != 1 else []), "-c:a", "pcm_s16le", "-ar", "48000", str(out))
        return out
    codec = vcodec(src)[0]
    if codec in ("prores", "dnxhd") and a.speed == 1 and not a.upscale and not (a.no_audio and has_audio(src)):
        return src
    out = out_dir / f"{src.stem}{tag}{'-up' if a.upscale else ''}{'-noaudio' if a.no_audio else ''}.mov"
    if out.is_file() and out.stat().st_size:
        print(f"skip {out.name} (exists)")
        return out
    to_prores(src, out, a)
    return out


def import_master(files):
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    if not resolve:
        sys.exit("bridge not running: in Resolve click Workspace > Scripts > claude_bridge (files are converted: "
                 + ", ".join(map(str, files)) + ")")
    proj = resolve.GetProjectManager().GetCurrentProject() or sys.exit("no project open")
    mp = proj.GetMediaPool()
    root = mp.GetRootFolder()
    have, stack = set(), [root]
    while stack:
        f = stack.pop()
        have |= {c.GetClipProperty("File Path") for c in f.GetClipList() or []}
        stack.extend(f.GetSubFolderList() or [])
    need = [str(f) for f in files if str(f) not in have]
    if need:
        mp.SetCurrentFolder(root)
        got = mp.ImportMedia(need) or []
        if len(got) < len(need):
            print(f"warning: Resolve imported {len(got)} of {len(need)}")
        resolve.GetProjectManager().SaveProject()
    print(f"project {proj.GetName()}: {len(need)} imported to Master, {len(files) - len(need)} already there; saved")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("items", nargs="+")
    ap.add_argument("-o")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--upscale", action="store_true")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--video", action="store_true")
    ap.add_argument("--no-import", action="store_true")
    a = ap.parse_args()
    files = []
    for it in a.items:
        f = prepare(it, a)
        print(f"ready {f}", flush=True)
        files.append(Path(f).resolve())
    if not a.no_import:
        import_master(files)


if __name__ == "__main__":
    main()
