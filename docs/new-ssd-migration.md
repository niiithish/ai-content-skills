# New SSD Migration & Optimization Guide (Linux / Arch / Omarchy + Intel Arc B570)

This guide covers everything to back up before swapping the SSD on this machine (`Intel Battlemage G21 [Arc B570]`, Arch/Omarchy), how to restore cleanly on the new OS, and a ready-to-paste **Agent Handoff Plan** to verify and optimize all local AI media tools on the new install.

> **Important path rule:** Keep the same Linux username and home path (`/home/nithish`) on the new OS. FilmCraft `.fcproj` files store absolute media paths — changing the home directory breaks media links across all existing client edits.

---

## 1. Pre-Swap Backup Checklist

### A. Push Unpushed Git Branches First
Check and push these local branches before wiping the old SSD:

| Repo Path | Size | Branch | Status | Action Before Swap |
| --- | ---: | --- | --- | --- |
| `~/Work/ai-content-skills` | 25 MB | `main` | Ahead of `origin/main` | `git push origin main` once refactor commits finish |
| `~/Work/filmcraft` | 36 GB | `patched` (+ `arc-vaapi`, `pr-1256`) | **No upstream** on `patched` (`c701645e`) | Push `patched` (and `arc-vaapi`/`pr-1256`) to `https://github.com/niiithish/filmcraft.git` |
| `~/Work/review-board` | 711 MB | `viewer-reference-and-keys` | **No upstream** (`1a1dcd9`) | Push branch to `https://github.com/niiithish/review-board` (or merge to `master` and push) |
| `~/Work/labflow` | 8 MB | `main` | Clean, synced | Already on `niiithish/labflow` |
| `~/Work/nithish-portfolio` | 1.1 GB | `main` | Clean, synced | Already on `niiithish/nithish-portfolio` |
| `~/Work/tries/parakeet-cpp/src` | 642 MB | `master` | Dirty submodule `third_party/ggml` | No need to push; either copy `~/.local/share/parakeet-cpp` or rebuild cleanly on new OS |

### B. Must-Back-Up Local-Only Data (NOT in Git)

Copy these to an external drive (preserve permissions with `rsync -aH --info=progress2`):

#### 1. Secrets, Logins & Configs (~5.3 GB — **keep private, never commit**)
| Path | Size | What It Contains |
| --- | ---: | --- |
| `~/.config/labflow/` | 5.3 GB | Saved Google Flow Chromium profiles, cookies, account configs, `.env` (`FLOW_PREFER_ACCOUNTS`, etc.) |
| `~/.config/cartesia/` | 4 KB | `api_key` (mode 600) for Cartesia Sonic 3.6 TTS |
| `~/.config/filmcraft/` | 4 KB | `control-token` (64-char hex token for FilmCraft live bridge on port 9876) |
| `~/Work/google-accounts/` | 4 KB | Local Google account notes/reference |
| `~/.ssh/` & `~/.config/gh/` | <1 MB | SSH keys and GitHub CLI auth (or re-auth with `gh auth login`) |

#### 2. Client Work & Media (~133.4 GB)
| Path | Size | What It Contains |
| --- | ---: | --- |
| `~/Work/upwork/` | 130 GB | All client projects (`calvin` 52G, `max` 36G, `brad` 13G, `alaria` 11G, `josh` 6.3G, `willams` 5.8G, `trevor` 3.8G, `jason` 3.0G, `jackson` 1.1G) |
| `~/Work/things-we-upload/` | 3.3 GB | Upload staging media |
| `~/Work/craft-fonts/` | 132 MB | Font library used by FilmCraft patched builds |
| `~/.local/share/fonts/` | 4 MB | **19 custom `.ttf` fonts** used in client `.fcproj` files (`MysaHookSans`, `NewsreaderReel`, `InstrumentSans`, `LibreBaskerville`, `AvenirNext`, `TikTokSans*`, `Montserrat*`) |

#### 3. Agent Rules, Custom Scripts & Optional History (~3.5 GB)
| Path | Size | What It Contains |
| --- | ---: | --- |
| `~/.local/bin/` | 2.4 MB | Custom wrappers (`transcribe`, `vocals`, `cartesia`, `filmcraft-live`, `filmcraft-update`, `ornith`/`lfm3`, `bt-dictation`, etc.) — `install.sh` will recreate the skill wrappers, but back up for non-skill utilities |
| `~/.claude/CLAUDE.md` & `~/.gemini/GEMINI.md` | 8 KB | Global agent rules (will also be synced by `scripts/install.sh`) |
| `~/.claude/projects/` | 3.5 GB | Optional: Claude Code session logs and per-project `memory/` (only needed if you want past chat history/memory) |

#### 4. Prebuilt Binaries & Large Model Weights (Optional Backup vs. Re-download)
Backing these up saves 1–2 hours of compiling/downloading on the new SSD; all of them can also be rebuilt/re-downloaded cleanly:

| Path | Size | Rebuildable? | Notes |
| --- | ---: | --- | --- |
| `~/.local/opt/filmcraft-gpu/` | 457 MB | Yes (`filmcraft-update` from `patched` branch) | Copying avoids a full C++/Qt compile |
| `~/.local/share/parakeet-cpp/` | 1.5 GB | Yes (CMake + Vulkan + GGUF download) | Contains `bin/parakeet-cli`, `lib/`, and `model/tdt-0.6b-v3-f16.gguf` |
| `~/.local/share/separate-models/` | 871 MB | Yes (auto-downloads) | `vocals_mel_band_roformer.ckpt` + `.yaml` |
| `~/.local/share/rembg/` | 2.0 GB | Yes (auto-downloads) | `models/birefnet-general` + `models/isnet-general-use` |
| `~/models/` | 22 GB | Yes (HuggingFace) | Local LLMs (`ornith-35b-a3b`, `lfm3-vl-2b`) |
| `~/.local/share/transcribe-venv/` | 472 MB | **Recreate fresh** | Don't copy Python venvs across OS installs; recreate with `uv` |
| `~/.local/share/separate-xpu-venv/` | 7.4 GB | **Recreate fresh** | Recreate PyTorch XPU + `audio-separator` venv on new OS |
| `~/.local/share/asr-venv/` | 150 MB | **Skip** | Legacy venv superseded by `transcribe-venv` |

---

## 2. New OS Restore Steps

Run these after installing Arch/Omarchy with the same username (`/home/nithish`):

### Step 1: System Packages & GPU Drivers (Intel Arc B570)
```bash
sudo pacman -S --needed git github-cli ffmpeg libva-utils intel-media-driver \
  vulkan-intel vulkan-headers vulkan-icd-loader imagemagick chromium cmake ninja uv
```
Verify GPU visibility:
```bash
ls -l /dev/dri/renderD128
vainfo | grep -i h264
vulkaninfo --summary | grep -i -E 'deviceName|Intel'
```

### Step 2: Clone Core Repos
```bash
mkdir -p ~/Work && cd ~/Work
gh auth login
git clone https://github.com/niiithish/ai-content-skills.git
git clone https://github.com/niiithish/labflow.git
git clone https://github.com/niiithish/review-board.git
git clone https://github.com/niiithish/filmcraft.git
```

### Step 3: Restore Private Configs, Fonts & Client Media from External Drive
```bash
# Replace /mnt/backup with your external drive mount point
rsync -aH --info=progress2 /mnt/backup/.config/labflow/    ~/.config/labflow/
rsync -aH --info=progress2 /mnt/backup/.config/cartesia/   ~/.config/cartesia/
rsync -aH --info=progress2 /mnt/backup/.config/filmcraft/  ~/.config/filmcraft/
chmod 700 ~/.config/cartesia && chmod 600 ~/.config/cartesia/api_key ~/.config/filmcraft/control-token 2>/dev/null || true

# Fonts (critical for FilmCraft captions)
mkdir -p ~/.local/share/fonts
rsync -aH /mnt/backup/.local/share/fonts/ ~/.local/share/fonts/
cp ~/Work/ai-content-skills/skills/captions-filmcraft/fonts/*.ttf ~/.local/share/fonts/ 2>/dev/null || true
fc-cache -f

# Optional: restore prebuilt FilmCraft GPU & model weights to skip long rebuilds/downloads
rsync -aH --info=progress2 /mnt/backup/.local/opt/filmcraft-gpu/       ~/.local/opt/filmcraft-gpu/
rsync -aH --info=progress2 /mnt/backup/.local/share/parakeet-cpp/      ~/.local/share/parakeet-cpp/
rsync -aH --info=progress2 /mnt/backup/.local/share/separate-models/   ~/.local/share/separate-models/
rsync -aH --info=progress2 /mnt/backup/.local/share/rembg/             ~/.local/share/rembg/

# Client work (same path!)
rsync -aH --info=progress2 /mnt/backup/Work/upwork/      ~/Work/upwork/
rsync -aH --info=progress2 /mnt/backup/Work/craft-fonts/ ~/Work/craft-fonts/
```

### Step 4: Install Labflow CLI & Run the Skills Installer + Doctor
```bash
# Install labflow CLI (flow / labflow)
uv tool install --editable ~/Work/labflow

# Install all skills (symlinks to ~/.agents/skills, ~/.claude/skills, ~/.gemini/config/skills, ~/.codex/skills),
# CLI wrappers (~/.local/bin/{transcribe,vocals,cartesia,rembg-cutout}), fonts, and global rules:
bash ~/Work/ai-content-skills/scripts/install.sh

# Set up FilmCraft live bridge + MCP
bash ~/Work/ai-content-skills/skills/filmcraft/scripts/setup.sh

# Verify every dependency, symlink, binary, font, GPU device, and model
bash ~/Work/ai-content-skills/scripts/doctor.sh
```

---

## 3. Agent Handoff Plan for New OS (Verification & Optimization)

Once the new OS is booted and Step 1–4 above are done, paste the prompt below into Claude Code, Codex, or Antigravity to have an agent audit, benchmark, and optimize the entire local media toolchain on the Intel Arc B570:

```markdown
I just migrated to a fresh Arch/Omarchy SSD on this Intel Arc B570 machine and restored `~/Work/ai-content-skills`.
Please run a full verification and optimization pass across all four local media systems below. Do not modify client projects; test on a short sample in `/tmp/` and report exact timings, pass/fail status, and any fixes applied.

### 1. Skills & Environment Baseline
- Run `bash ~/Work/ai-content-skills/scripts/doctor.sh` and fix any missing symlinks, fonts, Python packages, or PATH wrappers across Claude Code, Gemini/Antigravity, and Codex.
- Confirm `flow summary`, `cartesia models`, `filmcraft-cli --version`, and `~/Work/review-board/bin/review` all respond cleanly.

### 2. Intel Arc B570 GPU Stack (Vulkan, VA-API, XPU)
- Verify VA-API H.264 hardware encoding (`ffmpeg -vaapi_device /dev/dri/renderD128 ... -c:v h264_vaapi`).
- Verify patched FilmCraft (`~/.local/opt/filmcraft-gpu/filmcraft-cli`) renders and exports using GPU VA-API, and confirm the live bridge (`127.0.0.1:9876` with `~/.config/filmcraft/control-token`) is active.
- Verify Intel Vulkan (`vulkaninfo`) and Intel oneAPI/XPU runtime visibility for PyTorch XPU.

### 3. Local Speech-to-Text & Custom Caption Pipeline (`transcribe` + `fc_captions.py`)
- Verify/rebuild `~/.local/share/transcribe-venv` (Python 3.12 via `uv` with `onnx-asr[hub]`, CPU `onnxruntime`, `faster-whisper`, `numpy`; do NOT mix `onnxruntime-openvino` with `onnxruntime`).
- Verify `~/.local/share/parakeet-cpp/bin/parakeet-cli` runs on `Vulkan0` (not silently falling back to CPU) and benchmark a 60 s clip (target: ~1.5–2 s on Arc B570). If the copied binary fails on new system libs, rebuild `parakeet.cpp` with Vulkan enabled.
- Test `transcribe <sample.wav> --verify` and `fc_captions.py` (`words` -> `plan` -> `build` -> `check`) end-to-end on a dummy `.fcproj`, verifying waveform onset/dip snapping and font rendering (`TikTok Sans`, `Montserrat`, `AvenirNext`).

### 4. Vocal Separator (`vocals` — MelBand RoFormer on Arc XPU)
- Verify/recreate `~/.local/share/separate-xpu-venv` (Python 3.12 via `uv`, PyTorch XPU + `audio-separator`) pointing at `~/.local/share/separate-models/vocals_mel_band_roformer.ckpt`.
- Benchmark `vocals <sample-song.mp3>` on `xpu` (target: ~1 min for a 4-min song, ~15 s for 1 min, zero silent CPU fallback) and verify `transcribe <song> --vocals` produces clean silence gaps between sung lines.

### 5. Background Remover (`rembg` — `birefnet-general` & `isnet-general-use`)
- Create a dedicated, clean venv (e.g. `~/.local/share/rembg-venv` via `uv`) with `rembg` + `onnxruntime` (or Intel OpenVINO/GPU execution provider if stable on Arc B570 — benchmark CPU vs GPU and keep whichever is faster and artifact-free).
- Point `U2NET_HOME=~/.local/share/rembg/models` so it reuses the restored `birefnet-general` and `isnet-general-use` weights without re-downloading.
- Ensure a clean CLI wrapper exists in `~/.local/bin/` and is wired into `scripts/doctor.sh` + documented in the repo. Test both `isnet-general-use` (fast product/brand cutouts for tier boards) and `birefnet-general` (high-detail hair/edge cutouts) on a test image and report speed + edge quality.

Deliver a concise table at the end showing each tool, device used (Arc GPU vs CPU), benchmark time, and whether it is ready for production.
```
