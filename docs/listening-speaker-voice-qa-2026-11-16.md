# My Exams — Speaker gender & natural voice QA
Date: 2026-11-16
Scope: English listening, Grades 5–12. Review branch only; no released MP3 overwritten.

## Confirmed generator defect (Grades 5–8)
Earlier generators assigned the guest/respondent to Ryan (male) by turn position, even when the named guest was female.
Confirmed affected examples in the source bank: Salma (G5 A), Mariam (G5 C), Fatma (G6 B/D), Dana (G6 C), Alya (G7 A), Maha (G7 C), Hind (G8 A), Dana (G8 C). Duplicate paper versions are deliberately listed.
Male guests include Hamad, Ahmed, Yousuf, Salim, Faris. These should remain on Ryan.

## Fix now on review branch
- `scripts/listening_voice_roles.py`: approved name-to-voice map and safe first-person self-identification handling.
- Sonia = default host/interviewer; Ryan = named male respondent; Libby = named female respondent, distinguished from Sonia.
- Use explicit `speakerGenders` for unusual or ambiguous named roles, and optional `speakerGender` / `textSpeakerGenders` for single-narrator short texts.
- A mention of `he/his/she/her` about somebody else **never** changes the narrator's voice. A speaker label (`Sam:`) or `My name is Sam` does.
- `scripts/generate_grades5_6_audio.py` and `scripts/generate_grades7_8_audio.py` use the new casting rules.
- Optional `ONLY_LISTENING_IDS` filter allows generating only affected files. New `usedVoices` manifest field reports voices **actually selected**, unlike the older `voices` field that listed all configured voices.
- Existing Text 1..5 full-sequence repetition is preserved.

## Higher grades — source-script casting checked, MP3 timbre still requires listening verification
- G9 named interviewees from the reviewed source bank include Maha (F), Salim (M), Alya (F), Rashid (M); distinct unit texts include Huda (F), Bilal (M), Noura (F).
- G10: Maha (F), Salim (M). Labels such as Teacher, Student, Engineer, Presenter and Guide do not specify gender; retain an explicit production cast instead of guessing based on pronouns about other people.
- G11 named speakers include Amina (F), Fatma (F), Hamid (M), Reem (F), Rana (F), Salma (F), Khalid (M), Layla (F), Salim (M), Hamad (M), and others identified in the named speaker registry.
- G12 named speakers include Noura (F), Sara (F), Mariam (F), Hamed (M), Hamad (M), Khalid (M), Maha (F), Fatma (F), Yousuf (M), Maya (F), Omar (M), Huda (F), Sami (M). Generic roles such as Adviser and Counsellor require separate casting if not specified.
- Natural MP3s already stored for G9 and any higher-grade models were **not** changed by the generator fix. A script hash or `playedTwice` flag does not verify gender of the voice heard.

## Review gates
1. Run `python -m unittest discover -s tests -p 'test_*voice*.py' -v` and compile speech generators.
2. Review the *my-exams-speaker-voice-audition* artifact from `.github/workflows/listening-speaker-preview-audio.yml`. This produces seven short test MP3 files using free Edge TTS and **never commits or publishes audio**.
3. Listen to each file for correct speaker gender and natural turn changes, especially two women in the same dialogue.
4. Resolve repeated listening texts before regenerating all corresponding MP3s. Regenerating an unmodified duplicate simply reproduces the same duplicate.
5. Keep main untouched until teacher content/audio review and student playback QA pass.
