# JSON blueprint for an animated scene still

Use this as a guide, not a form to fill mechanically. Remove unused fields and replace all bracketed examples. A source image gets one job in `references`; do not infer a reference that was not supplied. Keep `final_generation_instruction` consistent with the structured fields.

```json
{
  "prompt_type": "animated_scene_still",
  "objective": "One composed 3D animated opening frame of [subject and story moment] in [place].",
  "references": [
    {
      "source": "[supplied image handle]",
      "use_for": "[character identity, environment, prop identity, or framing]",
      "preserve": ["[specific visible details]"],
      "adapt": "Render within the established feature-animation CG world."
    }
  ],
  "canvas": {
    "image_count": 1,
    "aspect_ratio": "[match project; 9:16 for unspecified short-form vertical video]",
    "orientation": "[portrait or landscape]",
    "crop": "[what enters and leaves the frame]"
  },
  "world_and_action": {
    "location": "[recognizable setting and fixed landmarks]",
    "first_frame_moment": "[visible state immediately before the clip's main action]",
    "spatial_layout": "[foreground, middle ground, background, entrances, and contact surfaces]"
  },
  "subjects": [
    {
      "identity_or_design": "[match approved reference or specify a new design]",
      "position_and_scale": "[frame position and size relative to set and other subjects]",
      "pose_and_gaze": "[specific starting pose, expression, eye line, and hand contact]",
      "wardrobe_or_surface": "[visible locked costume, hair, or prop material details]"
    }
  ],
  "viewpoint": {
    "height_distance_angle": "[viewpoint relative to subjects]",
    "field_of_view_and_depth": "[scene-appropriate perspective and depth]",
    "composition": "[subject placement, visual hierarchy, and useful open space]"
  },
  "visual_design": {
    "forms_and_materials": "[expressive sculpted forms and specific material response]",
    "palette": "[rich, controlled colour roles tied to characters and set]",
    "lighting": "[physical source, direction, falloff, and matching shadows]"
  },
  "visible_text": {
    "exact_words": ["[only approved wording that must be readable]"],
    "placement": "[where the text belongs in the world]"
  },
  "continuity_locks": ["[identity, costume, prop markings, location geometry, light, and screen direction that matter]"],
  "negative_prompt": ["[only concrete likely failure modes for this shot]"],
  "final_generation_instruction": "Create one [aspect ratio] feature-animation CG frame of [moment]. Preserve [critical references], [starting composition], and [light direction]; show only [approved visible text]."
}
```

Omit `references` when none are supplied, `visible_text` when no text belongs in the shot, and fields within `subjects` that do not apply. If accurate lettering is critical, verify it in the rendered image and plan a separate compositing pass if the generator distorts it.
