#!/usr/bin/env python3
"""Writes the 360p clip prompts (clip-N-v1) and clips-batch jobs: talking clips 1-13 from the master still, insert clips 2xx from their approved stills."""
import json, random
from pathlib import Path
V = Path(__file__).resolve().parents[1]
MASTER = str(V / "scenes/scene-1/scene-1-v1.jpg")

# shot, duration, line, the join to name, the beats of the performance
TALK = [
 ("1", 6, "How to make thighs look thirty-five at fifty-seven. I'm fifty-seven.", ("fifty-seven.", "I'm"), "teasing on \"thirty-five at fifty-seven\", a small proud smile on \"I'm fifty-seven\""),
 ("2", 6, "How to get firm thighs back at fifty-seven. I'm fifty-seven.", ("fifty-seven.", "I'm"), "knowing on \"firm thighs back\", a small proud smile on \"I'm fifty-seven\""),
 ("3", 6, "How to wear shorts again at fifty-seven. I'm fifty-seven.", ("fifty-seven.", "I'm"), "playful on \"wear shorts again\", a small proud smile on \"I'm fifty-seven\""),
 ("4", 10, "I modeled for Victoria's Secret for thirty-five years, and here's the one thing I do to my thighs every single night that most mature women don't know about.", ("years,", "and"), "matter-of-fact on her career, leaning in and lowering her voice on \"the one thing\", conspiratorial on \"don't know about\""),
 ("5", 8, "I body oil. As we get older, our skin makes less collagen, the stuff that keeps it firm, tight and smooth.", ("oil.", "As"), "a small reveal on \"I body oil\" with raised brows, then explaining, counting softly on \"firm, tight and smooth\""),
 ("6", 6, "Your thighs get dimply, your cellulite starts moving down your legs, and your skin becomes saggy.", ("legs,", "and"), "sympathetic, a slight wince on \"saggy\""),
 ("7", 6, "That's why so many women our age stop wearing shorts, even when their weight hasn't changed.", ("shorts,", "even"), "understanding, a small shake of the head on \"hasn't changed\""),
 ("8", 8, "What you need to do is get collagen past the surface. Most creams just sit on top.", ("surface.", "Most"), "firm and clear on \"past the surface\", a little dismissive on \"just sit on top\""),
 ("9", 10, "That's why I use and always recommend this body oil. It contains collagen, stem cells and eucalyptus, which are perfect for cellulite at our age.", ("oil.", "It"), "warm and sure, listing the three ingredients lightly"),
 ("10", 8, "The eucalyptus carries the collagen and stem cells past the surface, making your thighs look naturally firmer.", ("surface,", "making"), "explaining, one hand pushing gently forward on \"past the surface\""),
 ("11", 8, "I massage it into my thighs every night right after my shower, and over time they looked smoother, firmer and less dimpled.", ("shower,", "and"), "personal, a pleased smile growing on \"smoother, firmer and less dimpled\""),
 ("12", 8, "If the cellulite on your thighs got worse with age and you've stopped wearing shorts, definitely give this a try.", ("shorts,", "definitely"), "caring, then encouraging on \"definitely give this a try\""),
 ("13", 8, "I'll leave a link below so you can try it risk-free for sixty days, and right now it's up to sixty-five percent off.", ("days,", "and"), "friendly and upbeat, a hand pointing down briefly on \"below\", excited on \"sixty-five percent off\""),
]

def talk(shot, dur, line, join, acting):
    last = line.split()[-1]
    return f"""# Clip {shot} v1: the speaker says line {shot} at the podcast mic (reference: scenes/scene-1/scene-1-v1.jpg)

```text
{dur}-second vertical 9:16 video, real footage from a video podcast: a woman of 57 sits at a dark studio table and talks to an unseen host just off camera, one continuous shot with no cuts. @image1 is the reference for the woman, her clothes, the microphone, the studio, the framing and the light. It is not the first frame: she does not start in the exact pose of @image1; she is already in the middle of talking, moving naturally.

The woman: the woman in @image1, 57, lightly tanned sun-kissed skin with freckles, fine lines at the eyes, green-hazel eyes, shoulder-length ash-honey-blonde hair in loose tousled waves with a side part, small gold huggie earrings, a thin flat gold chain necklace, in a fitted white ribbed tank top and white linen shorts. Same face, hair and clothes in every frame.

Dialogue: she starts speaking on the very first frame and says this line, word for word, in English, in one natural, flowing delivery at a brisk, conversational pace with no long pauses, finishing the whole line at least one second before the clip ends, her mouth clearly lip-synced to every word: "{line}" Every word is said exactly once, in order, with no repeats or restarts, and no word is added. She goes straight on from "{join[0]}" into "{join[1]}" with only a quick breath, never a silent pause, so the line runs as one continuous thought, and she says the last word, "{last}", herself, her lips clearly moving. This is the only speech in the clip. She is alone with the microphone: no other voice is ever heard, no "yeah", no "mm-hm", no laugh, no reply. Voice: a 57-year-old American woman, warm, smooth and a little low, confident and clear, a neutral General American accent, talking like a friend sharing her secret. Only she speaks.

Performance: she looks just past the left side of the lens, as in @image1, the whole time; she never looks into the lens. {acting[0].upper() + acting[1:]}. Natural movements throughout: head nods and tilts on the key words, her brows lifting, her shoulders shifting, blinking and breathing. Her hands rise into frame in relaxed, open explaining gestures in front of her chest, fingers loose, then settle on her lap; her hands never touch the microphone or its arm. After the last word she stops talking and says nothing more: she closes her mouth, keeps a soft, matching expression and keeps looking just past the lens with small natural movements until the clip ends.

Camera: a fixed camera on a tripod, never seen in the frame. Exactly the same crop, angle and distance as @image1 from the first frame to the last: no zoom, no push-in, no pan, no shake. The black microphone and its boom arm stay exactly where they are in @image1, still, entering from frame right. Only the woman moves.

Setting: the same place as @image1: the black acoustic panels behind her, the dark grey table, the same soft warm key light from the front left. Nothing is added.

Sound: her voice recorded close on the podcast microphone, clear and natural, the loudest sound, in a quiet studio. No music, no score, no beeps, no other voices or reactions from anyone off camera, no echo.

No captions, subtitles or text on screen, and no logos or readable writing on the microphone.
```
"""

# shot, still version, what happens, camera, sound
INS = [
 ("201", 1, "A woman of 57 seated on a white linen daybed in a white one-piece swimsuit. 0–4 s: she turns her head slightly, her smile widening, her hand moving from her chin to rest on her knee.", "a slow gentle push-in", "soft room ambience"),
 ("202", 1, "A woman of 57 standing on a sunny villa terrace in a white tank top and white linen shorts. 0–4 s: she shifts her weight, turns a little toward the sea and back, her hair moving in the breeze, smiling.", "a slow gentle push-in", "a light sea breeze and distant waves"),
 ("203", 1, "A woman of 57 walking toward the camera along a sunny seaside promenade in white denim shorts. 0–4 s: she keeps walking at an easy pace, arms swinging, smiling, her hair moving.", "the camera moves slowly backward ahead of her at her pace, keeping her the same size", "footsteps on paving, light breeze, distant waves"),
 ("204", 1, "A young model in a crystal bodysuit and huge white feathered wings walks a glittering fashion-show runway. 0–4 s: she walks straight toward the camera with a confident runway stride, the feathers swaying, camera flashes popping in the crowd.", "locked at the end of the runway, she grows larger as she approaches", "the hum of a crowd and camera shutters, no music"),
 ("206", 1, "A woman of 57 walking along a resort pool deck in a white one-piece swimsuit, a rolled white towel in one hand. 0–4 s: she keeps walking toward the camera at an easy pace, smiling, the pool water glittering beside her.", "the camera moves slowly backward ahead of her, keeping her the same size", "footsteps on stone, gentle pool water, birds"),
 ("207", 2, "A woman of about 35 in a red one-piece swimsuit on a sunny terrace by the sea. 0–4 s: she lifts her sunglasses up onto her head and shifts her weight to the other leg.", "a slow gentle drift to the side", "a light sea breeze and distant waves"),
 ("208", 2, "A woman of about 60 standing in her bedroom in a black one-piece swimsuit, seen from behind. 0–4 s: she stands still, shifting her weight slightly from one leg to the other.", "handheld phone, tilting slowly down from her back to the backs of her knees", "quiet room ambience"),
 ("209", 1, "A woman of about 62 seated on the edge of her bed in grey shorts. 0–4 s: her fingers lift a fold of loose skin above her knee, hold it, then let it go and it settles back slowly.", "handheld phone, a slight natural sway, the same framing throughout", "quiet room ambience"),
 ("210", 1, "Two women of about 60 in one-piece swimsuits walking arm in arm along a sunny beach. 0–4 s: they keep walking toward the camera, laughing together, the waves rolling in beside them.", "the camera moves slowly backward ahead of them", "waves, wind and their soft laughter, no words"),
 ("211", 1, "A woman of about 58 in a navy one-piece swimsuit walking along the edge of a pool, a white sarong in her hand. 0–4 s: she keeps walking slowly along the pool edge, the sarong swinging.", "the camera tracks slowly alongside her", "bare footsteps on stone, gentle pool water"),
 ("212", 1, "A woman of 57 in a white waffle bathrobe seated on a wooden stool in a bright bathroom. 0–4 s: she spreads oil on her leg above the knee with both hands in slow circles, looking down with a soft smile.", "a slow gentle push-in", "quiet bathroom ambience, a soft rub of hands"),
 ("213", 1, "A woman of 57 in white linen shorts and a white tank top walking away from the camera past a seaside café. 0–4 s: she keeps walking at an easy pace away from the camera, her bag swinging, people at the café tables chatting.", "the camera follows slowly behind her", "café chatter without words, cups, footsteps, distant waves"),
 ("214", 1, "A woman of 57 in a white one-piece swimsuit sitting on a white sun lounger by a pool. 0–4 s: her hand moves slowly down from her knee toward her ankle, she looks down at her leg and smiles.", "a slow gentle push-in", "gentle pool water, birds, a light breeze"),
 ("215", 1, "A woman of about 60 with grey curly hair sitting on the edge of her bed in a navy tank top and beige shorts. 0–4 s: she presses the top of her leg with her fingertips in two places, then lets her hand rest, her head bowed.", "handheld phone, a slight natural sway, the same framing throughout", "quiet room ambience"),
]

def ins(shot, ver, what, cam, sound):
    return f"""# Clip {shot} v1: from scenes/scene-{shot}/scene-{shot}-v{ver}.jpg

```text
Vertical 9:16 short film shot, starting exactly from @image1.

{what}

Camera: {cam}.
Natural real-life motion at normal speed, real skin and fabric, the same people and place as @image1. Sound: {sound}; nobody speaks, no music. No text, captions or graphics on screen. One continuous shot, no cuts.
```
"""

def main():
    rnd = random.Random(529)
    jobs = []
    for t in TALK:
        p = V / f"clips/clip-{t[0]}/prompts/clip-{t[0]}-v1.md"
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(talk(*t))
        jobs.append(job(t[0], p, t[1], MASTER, rnd))
    for s in INS:
        p = V / f"clips/clip-{s[0]}/prompts/clip-{s[0]}-v1.md"
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text(ins(*s))
        jobs.append(job(s[0], p, 4, str(V / f"scenes/scene-{s[0]}/scene-{s[0]}-v{s[1]}.jpg"), rnd))
    (V / "clips/clips-batch.json").write_text(json.dumps({"jobs": jobs}, indent=2))
    print(len(jobs), "clip jobs")

def job(shot, p, dur, still, rnd):
    return {"id": f"clip-{shot}-v1", "kind": "video", "prompt_file": str(p), "aspect": "9:16", "duration": dur, "resolution": "360p",
            "timeout": 900, "seed": rnd.randint(1000, 9999), "ingredient": [still], "output": str(p.parents[1] / f"clip-{shot}-v1.mp4")}

main()
