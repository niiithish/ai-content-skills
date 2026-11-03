# Setting up a new machine

What the edit needs, where each piece lives, and how to check it. Git holds only the skills repo. Everything else is copied over or installed. Work through this list top to bottom on the new PC. Then run the checks at the end before touching a client project.

## 1. Skills (git)

```bash
mkdir -p ~/Work && cd ~/Work
git clone https://github.com/niiithish/ai-content-skills.git
mkdir -p ~/.claude/skills
for d in ~/Work/ai-content-skills/skills/*/; do n=$(basename "$d"); [ -f "$d/SKILL.md" ] && ln -sfn "$d" ~/.claude/skills/$n; done
ln -sfn ~/Work/ai-content-skills/skills/video-production/talking-head ~/.claude/skills/talking-head-video-production
ln -sfn ~/Work/ai-content-skills/skills/edit-style/talking-head ~/.claude/skills/talking-head-edit
ln -sfn ~/Work/ai-content-skills/skills/edit-style/voiceover ~/.claude/skills/voiceover-edit
```

Sub-skills live inside their parent (`video-production/talking-head`, `edit-style/talking-head`, `edit-style/voiceover`), so each needs its own link. Check with `ls -l ~/.claude/skills`.

## 2. Client work (copy, not in git)

`~/Work/upwork/upwork-max` is about 18 GB and holds:

- the playbook `AGENTS.md`;
- `tools/` (`new_video.sh`, `loom.sh`, `edit-kit/`);
- `assets/` (the clip library, music, emoji, sfx);
- every video folder, with its media, `.fcproj` files and backups.

Copy the whole folder to the **same path** with `rsync -a --info=progress2`, or from an external drive. The `.fcproj` files store absolute media paths, so a different home or user name breaks every link. If the path must change, relink with `media.replaceFootage`, or by FilmCraft's Link Media.

Also copy:

- `~/Work/review-board`: or clone `https://github.com/niiithish/review-board`, then run `bin/review` once.
- `~/Work/labflow` (the `flow` CLI): clone `https://github.com/niiithish/labflow`, make its `.venv`, then `ln -s ~/Work/labflow/.venv/bin/flow ~/.local/bin/flow`. Log in again with `flow account …` (see the `flow` skill).
- `~/.config/elevenlabs`, `~/.config/cartesia`, `~/.config/labflow`: API keys and accounts. Copy them over a private channel; never commit them.

Claude's memory (`~/.claude/projects/*/memory/`) is tied to each folder path on this machine. The rules that matter from it are already written into `edit-style/SKILL.md` (Working with the user) and the client playbooks. Copy `~/.claude/projects/` across too if the paths stay the same.

## 3. Tools

| Tool | Install | Check |
|---|---|---|
| FilmCraft + `filmcraft-cli` (0.17+) | `edit-style/scripts/setup/filmcraft-update`: copy it to `~/.local/bin/`. It installs the latest `storytold/filmcraft` GitHub release into `/opt/filmcraft` and needs `gh auth login` | `filmcraft-cli --version` |
| FilmCraft MCP (bridge) | `claude mcp add filmcraft -s user -- /usr/local/bin/filmcraft-cli mcp --bridge 127.0.0.1:9876` | `/mcp` lists filmcraft |
| ffmpeg with VAAPI | `pacman -S ffmpeg libva-utils` (Intel: `intel-media-driver`; AMD: `libva-mesa-driver`) | `vainfo` shows H264 encode; `ls /dev/dri/renderD128` |
| Fonts | `cp ~/Work/ai-content-skills/skills/captions-filmcraft/fonts/*.ttf ~/.local/share/fonts/ && fc-cache -f`: TikTok Sans SemiBold, Montserrat Bold, ExtraBold, Light | `fc-list \| grep -i -E 'tiktok\|montserrat'` |
| Parakeet (offline words) | `pip install "onnx-asr[cpu,hub]"`. The model downloads once (or copy `~/.local/share/voxtype/models/parakeet-tdt-0.6b-v3`) | `transcribe.py any.mp4 --engine parakeet` |
| Python 3 + numpy | system or `mise` | `python3 -c "import numpy"` |
| `gh` | `pacman -S github-cli` and `gh auth login` | `gh auth status` |
| ElevenLabs | the claude.ai ElevenLabs connector (creative tools), signed in with the same account | `creative_list_flows` answers |
| Chromium | for `plan.py pdf` | `chromium --version` |

## 4. Checks before the first edit

1. Ask the new session to read `upwork-max/AGENTS.md` and load `edit-style` + `talking-head-edit`. It should name the house style without guessing: y 1360, template 6, 2 %/s pushes, 100/110 steps, −26/−27 dB music.
2. Open `DCT-2190/edit/hook-1.fcproj` in FilmCraft. There should be no missing-media warnings, and the captions should be in TikTok Sans. A fallback font means the fonts aren't installed.
3. `filmcraft-cli --project DCT-2190/edit/hook-1.fcproj render --seconds 10 --out /tmp/f.png` gives a frame with a caption.
4. `python3 ~/.claude/skills/captions-filmcraft/scripts/fc_inserts.py check DCT-2190/edit/hook-1.fcproj` gives 47 / 3 / 0.
5. `flow accounts` lists the accounts. `~/Work/review-board/bin/review DCT-2190` gives a URL.
