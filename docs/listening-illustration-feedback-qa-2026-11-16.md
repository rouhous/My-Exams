# My Exams — Listening and Illustration QA (Grades 5–12)

Updated: 2026-11-16. This checklist applies only to **My Exams**, not My English Journey.

## Listening playback contract

- Grades 5–9, Listening 1 when the task contains five independent numbered short texts: introduce the activity; read Text one, two, three, four, five **in order**; say **“Now listen again.”**; then repeat Text one, two, three, four, five in order. Never replay an item immediately after itself.
- For a continuous passage, interview or conversation (including appropriate tasks in Grades 10–12): play the **entire** passage once, then replay the **entire** passage. Match the actual assessment template for each grade/stream and section; do not force all tasks into five-item format.
- Number labels are not part of the answer content. Preserve speaker order, pauses between short texts and natural speech speed.
- Do not assume metadata such as `playedTwice: true` confirms the correct order. Inspect the audio timeline and listen to the full exported file.
- Re-run source-script-to-MP3 checks after any text change. Existing MP3 files remain provisional until regenerated and listened to.

## Picture contract

- Use detailed, recognizable **2D black-and-white cartoon** illustrations, not colored 3D pictures, generic symbols or thin ambiguous outlines.
- Ensure the tested object or action is immediately identifiable at the size shown in a student exam. Use appropriate context, solid contours and black/white shading; avoid visual clues that make the answer explicit.
- Keep A/B/C choices comparable in size, crop and detail. Do not reuse an identical illustration across differing meanings.
- Test readability on mobile screens, in grayscale printing and offline. Verify that correct picture-to-answer mappings remain valid after image replacement.
- Treat existing procedural SVG/simple line-art as candidates for review, not automatically approved assets.

## Feedback contract

- **Practice**: after submission of each answer, provide correct answer plus *why*, referring to an applicable grammar rule, vocabulary context, exact reading evidence, or listening transcript segment as appropriate. Let the learner retry incorrect items.
- **Timed exam**: do not reveal answers or explanations before submission; keep results/feedback until the end.
- Writing feedback requires rubric alignment and must be labeled an estimate when automated.

## Deployment gate

1. Compare against the latest review branch before changing `main`.
2. Check Grades 5–12 and Core/Elective where applicable against relevant assessment specs.
3. Regenerate and audit MP3s, verify exact transcript/text sequence.
4. Review illustration legibility and answer mapping.
5. Run student-route and offline-media tests, then teacher review.
6. Publish only after those checks pass.
