"""Checks edit/exports/{host,guest}-talking.mp4: transcript vs the script lines, and every silence over 0.3 s."""
import json, re, subprocess, sys, difflib, pathlib
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
LINES = [l for l in (ROOT / "voiceover/script.md").read_text().splitlines() if l.strip() and not l.startswith("#")]
HOOKS = [h.split(":", 1)[1].strip() for h in (ROOT / "voiceover/hooks.md").read_text().splitlines() if h.startswith("HOOK")]
host = [LINES[i - 1] for i in (2, 12, 18)]
guest = [l for i, l in enumerate(LINES, 1) if i not in (2, 12, 18)] + HOOKS
def norm(t):
    t = t.lower().replace("omega-7", "omega seven").replace("third-generation", "third generation").replace("trymysa.store", "try mysa dot store")
    t = re.sub(r"\b116\b", "a hundred and sixteen", t).replace("90", "ninety").replace("softgels", "soft gels").replace("-", " ")
    return re.findall(r"[a-z']+", t)
for name, lines in [("host-talking", host), ("guest-talking", guest)]:
    f = ROOT / f"edit/exports/{name}.mp4"
    subprocess.run(["transcribe", str(f)], check=True, capture_output=True)
    w = json.loads(f.with_suffix(".words.json").read_text())
    got, want = norm(" ".join(x["word"] for x in w)), norm(" ".join(lines))
    diff = [(op, " ".join(want[i1:i2]), " ".join(got[j1:j2])) for op, i1, i2, j1, j2 in
            difflib.SequenceMatcher(None, want, got, autojunk=False).get_opcodes() if op != "equal"]
    a = subprocess.run(["ffmpeg", "-v", "error", "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(a, np.float32); n = len(x) // 160
    db = 20 * np.log10(np.sqrt((x[:n * 160].reshape(n, 160) ** 2).mean(1) + 1e-12))
    thr = np.percentile(db, 95) - 32; on = db > thr
    sil, i = [], 0
    while i < n:
        if not on[i]:
            j = i
            while j < n and not on[j]: j += 1
            if (j - i) / 100 > 0.3: sil.append((i / 100, round((j - i) / 100, 2)))
            i = j
        else: i += 1
    print(f"== {name}: {n / 100:.1f} s, {len(got)} words (script {len(want)})")
    print("   word diffs:", diff or "none")
    print("   silences > 0.3 s:", sil or "none")
