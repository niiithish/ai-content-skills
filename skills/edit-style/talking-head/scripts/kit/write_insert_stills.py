#!/usr/bin/env python3
"""Writes the insert still prompts (scene-2xx-vN) and their stills-batch jobs from SHOTS. Her shots pass the master still for her face."""
import json, sys
from pathlib import Path
V = Path(__file__).resolve().parents[1]
MASTER = str(V / "scenes/scene-1/scene-1-v1.jpg")
HER = ("the woman in @image1: 57, lightly tanned sun-kissed skin with freckles on her nose, cheeks, shoulders and chest, fine lines at the eyes, "
       "green-hazel eyes, a long oval face with a defined jaw, shoulder-length ash-honey-blonde hair in loose tousled waves with a side part, "
       "small gold huggie earrings, a thin flat gold chain necklace; a slim, fit, toned 57-year-old body with real skin texture")
PRO = ("A candid lifestyle photo, like a still from a real influencer's video: natural, unposed, slightly imperfect framing.",
       "Phone main lens or a 35 mm lens, natural perspective, the background a little soft.")
PHONE = ("An ordinary phone photo a woman took at home to show her legs, as in a real TikTok: handheld, slightly crooked, not composed, not a styled shoot.",
         "Phone main lens, everything fairly sharp, no creamy background blur.")
ROOM = ("Lit by the plain overhead ceiling light of the room, a little flat, with the slightly warm-white cast of indoor bulbs and soft shadows under the curves of the legs, so every dimple reads.",
        "True indoor colour, slightly warm-white, never orange or amber.")
SUN = ("Bright natural midday sun, real hard shadows, the sky clear blue.", "True colour, no orange cast, no haze.")
NEG_REAL = ["airbrushed or waxy skin, glow, beauty filter, smooth flawless skin, young model's legs", "a face in frame", "nudity, underwear, lingerie, sexualised pose or crop",
            "captions, subtitles, text overlays, labels, logos, brand names, watermarks, app UI", "CGI, illustration, studio sweep, amber or orange tint",
            "extra fingers, fused or bent fingers, a hand with no arm", "soft flattering window light, golden glow, a tidy styled room, slim model legs",
            "cellulite shown as raised bumps or lumps: it is shallow dents"]
NEG_HER = ["a different woman, a younger face, a different hair colour", "looking into the lens", "a bikini, a revealing or sexualised pose or crop, nudity",
           "captions, subtitles, text, logos, brand names, watermarks", "waxy plastic skin, heavy retouching, glow", "CGI, illustration",
           "extra fingers, fused fingers", "any bottle, jar or product in frame"]

SHOTS = [
 ("201", True, "Her seated on a white linen daybed in a white one-piece swimsuit, knees together, one hand at her chin, smiling just off camera.",
  "Full body seated, from just above her head to her feet, slightly from the side, filling the frame.",
  "A bright white-walled villa room with a white linen daybed, soft daylight from a big window behind the camera.",
  "Seated on the daybed edge, legs angled to one side, knees together, smooth toned thighs; one hand at her chin, a relaxed confident smile, eyes just left of the lens.",
  "A plain white one-piece swimsuit with a modest scoop neck and wide straps.", PRO,
  ("Soft bright daylight from a large window, gentle shadows.", "Clean whites, warm neutral, no orange cast.")),
 ("202", True, "Her standing on a sunny white villa terrace in a white tank top and white linen shorts, one hand on her hip, smooth toned thighs.",
  "Full length from head to just below the knees, she fills the frame.",
  "A white-washed villa terrace with a low white wall, terracotta pots with olive trees, the sea far behind, softly blurred.",
  "Standing with her weight on one leg, one hand on her hip, turning slightly to the side, smiling, looking just left of the camera.",
  "A white ribbed tank top and short white linen shorts.", PRO, SUN),
 ("203", True, "Her walking toward the camera along a sunny seaside promenade in white denim shorts and a white tank, sunglasses pushed up on her head.",
  "Full length, head to feet, she is mid-stride in the centre of the frame.",
  "A sunny seaside promenade with pale paving, a white railing and the blue sea on one side, a few blurred people far behind.",
  "Mid-stride walking toward the camera, arms swinging naturally, smiling, eyes just to the left of the camera.",
  "White denim shorts, a white ribbed tank top, tortoiseshell sunglasses pushed up in her hair, flat tan sandals.", PRO, SUN),
 ("204", True, "The woman from @image1 at about 22, decades younger, walking a glittering fashion-show runway in a crystal-studded white bodysuit and huge white feathered wings.",
  "Full length, low angle from the end of the runway, she walks straight toward the camera in the centre.",
  "A glamorous fashion-show runway with a glittering reflective floor, blue and white stage lights, a dark packed audience on both sides with camera flashes; no logos, no signs, no text.",
  "Mid-stride, one foot in front of the other, shoulders back, a confident runway look just past the camera.",
  "A long-sleeved white bodysuit covered in crystals with a high neck and opaque tights, huge white feathered angel wings on her back, white heels.",
  ("A photo from a real fashion show, shot by a photographer at the end of the runway: sharp, flash-lit.", "A 70 mm lens, the audience softly blurred."),
  ("Bright stage spotlights from above and in front, glints on the crystals, camera flashes in the crowd.", "True colour, cool blue stage light behind, no orange cast.")),
 ("206", True, "Her walking along a resort pool deck in a white one-piece swimsuit, a white towel in one hand.",
  "Full length from head to feet, she walks toward the camera, slightly off centre.",
  "A luxury resort pool deck with pale stone paving, white sun loungers with folded towels, palm trees and turquoise water at the side.",
  "Mid-stride toward the camera, a rolled white towel in one hand, the other arm swinging, a relaxed smile, eyes just left of the camera.",
  "A plain white one-piece swimsuit with a modest scoop neck and wide straps, flat white sandals.", PRO, SUN),
 ("207", False, "A woman of about 35 on a sunny resort terrace in a red one-piece swimsuit, firm smooth legs, adjusting her sunglasses.",
  "From her shoulders to her knees, slightly from the side, her face cropped above the mouth or turned away.",
  "A sunny resort terrace with a white balustrade and the sea behind.",
  "Standing with one knee bent, one hand lifting her sunglasses on her head; firm, smooth, toned thighs with real skin texture.",
  "A plain red one-piece swimsuit with a modest cut.", PRO, SUN),
 ("208", False, "A real woman of about 60 with an average build, standing in her bedroom in a plain black one-piece swimsuit, seen from behind from the hips to the calves: shallow cellulite dents run down the backs of her thighs right to the backs of her knees.",
  "From behind at hip height, from the bottom of the swimsuit to the middle of her calves, filling the frame.",
  "A lived-in bedroom, beige carpet, the edge of a bed and a chair with clothes on it at the frame edges.",
  "Standing still, weight even, her arms out of frame; the dimpled skin runs from the swimsuit edge down to the creases behind her knees.",
  "A plain black one-piece swimsuit, only its lower edge in frame.", PHONE, ROOM),
 ("209", False, "A real woman of about 62 seated on the edge of her bed in grey cotton shorts: her fingers lift the loose, crepey skin just above her knee and it folds into fine crinkles.",
  "Close, from above at an angle, from the shorts hem to just below the knee.",
  "A lived-in bedroom, a patterned duvet under her legs.",
  "Seated, her thumb and two fingers lifting a soft fold of loose skin above the kneecap, the skin crinkled and sagging, faint veins and age spots.",
  "Plain grey cotton shorts.", PHONE, ROOM),
 ("210", False, "Two real women of about 60 in modest one-piece swimsuits walking and laughing together toward the camera along a sunny beach.",
  "Full length, both side by side in the middle of the frame, seen from a little distance so faces are small and natural.",
  "A wide sunny sandy beach with gentle waves and blue sky.",
  "Mid-stride, one with her arm through the other's, both laughing, their bodies real for 60: soft tummies, real thighs, confident.",
  "One in a plain navy one-piece, one in a coral one-piece, both modest cuts; one has a sarong over her shoulder.", PRO, SUN),
 ("211", False, "A real woman of about 58 in a navy one-piece swimsuit stepping along a resort pool edge in the sun, firm smooth thighs, a sarong in her hand.",
  "From her waist to her feet, slightly from the side, mid-step, face out of frame.",
  "A resort pool edge with pale stone paving and turquoise water beside her.",
  "Mid-step along the pool edge, a folded white sarong in one hand; her thighs look smooth and firm for her age, real skin with freckles.",
  "A plain navy one-piece swimsuit, modest cut.", PRO, SUN),
 ("212", True, "Her in a white waffle bathrobe seated on a wooden bathroom stool after a shower, massaging oil into her thigh with both hands.",
  "From her face to her knees, slightly from the side, her head tilted down toward her leg.",
  "A bright white bathroom with a glass shower behind her, a little steam on the glass, a folded towel on a shelf.",
  "Seated, the robe parted over one leg, both hands smoothing glossy oil up the front of her thigh; she looks down at her leg with a soft smile.",
  "A white waffle cotton bathrobe tied at the waist.", PRO,
  ("Soft bright daylight from a window beside her.", "Clean whites, warm neutral.")),
 ("213", True, "Her from behind walking past a sunny seaside café terrace in white linen shorts and a white tank top.",
  "Full length from behind, head to feet, she walks away from the camera along the café front.",
  "A seaside café with a striped awning, small round tables and a few people at them, the sea at the end of the street.",
  "Mid-stride away from the camera, relaxed, her hair moving; the backs of her thighs smooth and toned.",
  "Short white linen shorts, a white ribbed tank top, flat tan sandals.", PRO, SUN),
 ("214", True, "Her seated on a white sun lounger in a white one-piece swimsuit, her hand gliding down her smooth thigh, smiling.",
  "From her face to her feet, slightly from above and the side.",
  "A sunny resort terrace by a pool, a white lounger with a white cushion, palm shadows.",
  "Sitting up on the lounger, legs stretched out, one hand gliding slowly down the outer side of her smooth, firm thigh; a contented smile, eyes on her leg.",
  "A plain white one-piece swimsuit with a modest scoop neck.", PRO, SUN),
 ("215", False, "A real woman of about 60 with short grey curly hair, in a navy tank top and beige cotton shorts, sitting on the edge of her bed looking down at her dimpled thighs and pressing one with her fingertips.",
  "From her shoulders to her knees, a little from the side, her face turned down and partly hidden by her hair.",
  "A lived-in bedroom, a navy duvet, a bedside lamp.",
  "Sitting on the bed edge, head bowed, fingertips pressing the front of her thigh, where shallow cellulite dents show; a worried, tired posture.",
  "A navy tank top and beige cotton shorts.", PHONE, ROOM),
]

def prompt(sid, her, obj, framing, place, pose, wear, cam, light):
    subj = {"role": "Hero", "pose_or_state": pose, "wardrobe_if_visible": wear}
    if her:
        subj["appearance"] = HER + (" (here about 22, decades younger, the same face)" if sid == "204" else "") + "."
    d = {"prompt_type": "real_world_still", "objective": obj}
    if her:
        d["references"] = {"@image1": "Identity only: her face, hair and skin. Take nothing else from it: not the studio, the microphone, the framing, the pose or the clothes."}
    d |= {"canvas": {"output_image_count": 1, "aspect_ratio": "9:16", "orientation": "portrait", "framing": framing + " It fills a phone screen, so keep it simple and readable at a glance."},
          "scene": {"place": place}, "subjects": [subj],
          "camera": {"capture_style": cam[0], "perspective_and_focus": cam[1]},
          "lighting": {"primary_source": light[0], "color_balance": light[1]},
          "capture_details": {"overall": "Real photo: real skin with pores, fine hairs, freckles and small marks; nothing retouched."},
          "negative_prompt": NEG_HER if her else NEG_REAL,
          "final_generation_instruction": f"Generate one 9:16 portrait photograph. {obj} {framing} {light[0]} No text, no logos."}
    return f"# Scene {sid} v1\n\n```text\n{json.dumps(d, indent=2, ensure_ascii=False)}\n```\n"

def main():
    batch = json.loads((V / "scenes/stills-batch.json").read_text())
    have = {j["id"] for j in batch["jobs"]}
    for s in SHOTS:
        sid, her = s[0], s[1]
        p = V / f"scenes/scene-{sid}/prompts/scene-{sid}-v1.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(prompt(*s))
        jid = f"scene-{sid}-v1"
        if jid not in have:
            job = {"id": jid, "kind": "image", "prompt_file": str(p), "aspect": "9:16", "output": str(p.parents[1] / f"scene-{sid}-v1.jpg")}
            if her:
                job["ingredient"] = [MASTER]
            batch["jobs"].append(job)
    (V / "scenes/stills-batch.json").write_text(json.dumps(batch, indent=2))
    print(len(SHOTS), "prompts")

main()
