# character-penguin-penny (video-7 sheet, approved)

```json
{
  "prompt_type": "character_reference_sheet",
  "objective": "Generate exactly one composite landscape image: a three-panel studio reference sheet of Penny, a hand-sculpted stop-motion plasticine penguin puppet, with one canonical outfit and her face visible only in the portrait panel.",
  "canvas": {
    "output_image_count": 1,
    "aspect_ratio": "16:9 landscape",
    "composite_rule": "All three views share one image canvas; do not create separate images or files for individual panels.",
    "layout": "Three panels left to right with thin solid #d1d1d2 vertical separators: headless front body about 30%, no-face back body about 30%, large shoulder-up portrait about 40%.",
    "framing": "Whole body and feet uncropped in the body panels with generous margins; portrait shows head and cardigan shoulders, no flippers.",
    "labels": "No captions, panel names, border or watermark."
  },
  "panels": [
    {
      "position": "left",
      "view": "full-body front",
      "subject": "Penny's plump, pear-shaped penguin body standing upright, feet together, both flippers hanging relaxed at her sides. Head completely absent: the cardigan's ribbed neckline is the topmost visible edge, with #504f50 background directly above and inside it; no neck, chin, beak or stump.",
      "wardrobe_visible": "Open dusty-rose cardigan hanging to her hips, showing the smooth cream-white clay belly between its front edges; five small round gold buttons down the left front edge; ribbed cuffs on both flipper sleeves; two short saffron-orange webbed clay feet below the hem."
    },
    {
      "position": "center",
      "view": "full-body back",
      "subject": "The same body from directly behind: the smooth charcoal-black clay back of her rounded head above the collar, no beak or eye visible, flippers relaxed at her sides, short pointed charcoal tail just below the cardigan hem, orange feet.",
      "wardrobe_visible": "Back of the dusty-rose cardigan with its vertical knit ribs and ribbed bottom hem; the pearl string's clasp is hidden under the collar."
    },
    {
      "position": "right",
      "view": "large shoulder-up portrait, visible three-quarter head turn",
      "subject": "Penny's head turned about 30 degrees to frame-left: smooth charcoal-black clay crown and back of head, a cream-white clay face patch around the eyes and cheeks blending into the white chest. Two big matte white clay disc eyes with glossy black bead pupils and a tiny white catch-light, under heavy sculpted charcoal lids that droop slightly; three short rolled-clay lashes on each upper lid; gentle sculpted laugh-line creases pressed at the outer eye corners and two soft dimples under the eyes, reading as a warm woman in her late 50s. A short rounded saffron-orange clay beak, slightly lighter at the tip, closed. Two soft rosy-pink blush dabs on the cheeks. Kind, gently tired, closed-beak half-smile. Both eyes readable, the right cheek more visible.",
      "wardrobe_visible": "Same dusty-rose cardigan ribbed collar and top two gold buttons; a short single string of small creamy-white clay pearls resting at the base of her neck, above the collar."
    }
  ],
  "identity": {
    "source": "New character: Penny, the hero of a claymation ad, a warm, slightly weary penguin woman in her late 50s who lives in a cosy home with her husband Walt.",
    "design": "Hand-sculpted plasticine stop-motion puppet in the style of a high-end modern claymation short: soft pear-shaped body about one and a half heads tall, charcoal-black back and head, cream-white belly and face patch, saffron-orange beak and feet, big white disc eyes with black pupils under heavy lids. Body volume is solid clay, gently uneven, never smooth CGI.",
    "scale": "An adult figure in her world: the same height as a kitchen chair seat-back; Walt is half a head taller and rounder. A Mysa bottle stands about as tall as her shoulder.",
    "distinctive_features": "Short pearl string, rosy blush dabs, three lashes per upper lid, laugh-line creases at the outer eye corners. No other marks.",
    "expression": "Warm closed-beak half-smile, slightly tired eyes."
  },
  "wardrobe": {
    "canonical_outfit": "One dusty-rose (#c98b94) chunky cardigan sculpted from clay with a pressed cable-knit texture (vertical cable ribs, tiny knit loops pressed in with a tool), worn open, hip length, ribbed collar, cuffs and hem; five small round shiny gold buttons on the left front edge, buttonholes on the right; a short single string of small creamy-white pearl beads at the neck. Nothing else; feet bare orange clay.",
    "text_and_logos": "None."
  },
  "background_and_lighting": {
    "background": "Uniform solid #504f50 studio backdrop in every panel.",
    "light": "Broad soft neutral frontal light with a slight key from frame-left, about 5500K; gentle contact shadow under the feet; no rim glow or coloured light."
  },
  "camera_and_style": {
    "camera": "Eye-level, normal-lens studio reference photography of a physical stop-motion puppet, near-orthographic, centred, deep readable focus across the whole figure.",
    "detail": "Matte plasticine with visible thumbprints, fingerprint whorls and small tool marks, slight asymmetry between left and right sides, tiny dust specks, faint seam where the beak meets the face, soft subsurface in the thin clay of the beak tip; cardigan knit texture pressed into the clay; gold buttons slightly glossy. A real handmade miniature, not a 3D render."
  },
  "consistency_locks": [
    "Exactly one 16:9 landscape image with three panels and #d1d1d2 dividers; panel 3 is the only face source.",
    "One puppet and one unchanged outfit in every panel: dusty-rose clay cable-knit cardigan worn open, five gold buttons on the left front edge, pearl string at the neck.",
    "Charcoal-black back and head, cream-white belly and face patch, saffron-orange beak and feet in every view.",
    "Big matte white disc eyes with black bead pupils, heavy lids, three lashes, laugh-line creases."
  ],
  "negative_prompt": [
    "head, beak or neck stump above the collar in the front panel", "eyes or beak visible in the back panel", "frontal symmetrical portrait, flippers in the portrait panel",
    "separate images for each view, portrait canvas, extra panels or extra penguins", "cropped feet or body",
    "smooth glossy 3D CGI render, plastic toy sheen, vinyl figure", "Pingu-style simple flat penguin with tiny dot eyes",
    "real fabric or wool yarn, felt", "realistic bird feathers", "glasses, hat, earrings, handbag, extra jewellery",
    "text, labels, logos, watermarks", "golden sunset light, heavy colour grade, dramatic shadows"
  ],
  "final_generation_instruction": "Generate exactly one 16:9 landscape studio photograph of a three-panel reference sheet of Penny, a hand-sculpted plasticine stop-motion penguin puppet in her late 50s: left, headless full-body front with the dusty-rose clay cable-knit cardigan worn open over her cream-white belly, five gold buttons on the left edge, orange feet, and nothing above the collar; centre, full-body back with no face; right, large shoulder-up portrait turned about 30 degrees, big matte white disc eyes with black pupils under heavy lids, three lashes, laugh-line creases, rosy blush, short saffron-orange beak closed in a warm half-smile, pearl string at the neck. Visible fingerprints and tool marks, uniform #504f50 backdrop, thin #d1d1d2 separators, soft neutral light, no scenery or labels."
}

```
