# My Exams — Work handoff / استكمال العمل
**Date:** 14 November 2026 (Asia/Muscat)  
**Repository:** https://github.com/rouhous/My-Exams  
**Student final release:** **NOT approved**; current GitHub Pages is a teacher-review and student-practice preview.

## Authoritative recovery checkpoint
- The last recovered Work conversation had progressed through Grades 5–8, Grade 9 and Grade 10 previews, a six-model Grade 11 Core review pilot, and 2026 SAH structural audits for Grade 11 Elective and Grade 12. The immediately pending stream was Grade 12 Elective's four separately unit-aligned tests and listening generation. **That unfinished Work task was not confirmed pushed.**
- The last commit prior to this chat's continuation was 54ec204 (Grade 11 Core separate nine-section teacher-led Paper A).
- User's scope: Grades 1–12; four fixed A–D models per semester/track where appropriate; E/F (and optional further comprehensive) mixed papers; large bank for random complete papers; full tests timed; isolated skills untimed; textbook and 2026 Oman ministry wording/SAH; validated natural Listening audio, not synthetic placeholders; Writing grading through the already deployed safe backend only after its integration is verified. Preserve distinct *My Exams* project.

## Verified pre-existing features
- Grades 5–8: A–F + random; 32 hosted natural MP3 across 5–8, technical browser checks pass. **Full skill-by-skill textbook unit matching and real-phone offline sign-off pending.**
- Grade 9: A–G with listening coverage including base-reuse; teacher review pending for three units and phone offline behavior.
- Grade 10: A–F; six audio files; curriculum-mapping page audit pending.
- Grade 11 Core: separate A–F five-broad-section revision page with six audio and one independent nine-section teacher-led semester Paper A. Only new A matches stored nine-section SAH *shape*; other five-broad-section pilot models must not be treated as official semester papers.
- Grade 11 Elective / Grade 12 Core / Grade 12 Elective: A–F parts in higher_grades_corrected.json, but A–D are provisional **themes**, NOT textbook-certified unit exams. Audio not validated/linked; some texts duplicated across tracks.

## New work committed in this ChatGPT conversation
1. upper-grades-practice.html — responsive teacher-review interface for Grade 11 Elective, Grade 12 Core and Grade 12 Elective:
   - fixed full A–F timed; random comprehensive full using *whole* skill sections from A–D (not arbitrarily shuffled subquestions); single-skill untimed; original model/skill provenance labelled.
   - automatically grades MCQ/TF/matching; short/gap and writing marked for teacher review; **never claims an overall 60/70 score** until these components are reviewed.
   - no fictitious audio: teachers can read the scripts via closed details panels.
   - locks track/model/mode during attempts to prevent mixing answer context.
2. UPPER_GRADES_RELEASE_GATE_2026-11-14.json — A–D content-level checkpoint: **8 model-theme versus textbook-unit-title mismatches, 7 exact cross-track repeated passages, and 24 listening sections without validated MP3**. Zero of these 12 fixed models approved as full unit exams.
3. Index link to preview; sw.js v5 shell precache entry.
4. tests/upper_grades_browser_smoke.cjs and .github/workflows/upper-grades-qa.yml — structural checks and Playwright mobile smoke; verify the latest successful Actions result rather than assuming a pass from job creation.
5. RELEASE_STATUS.json updated to preserve blockers and stage.
6. GitHub links:
   - https://rouhous.github.io/My-Exams/
   - https://rouhous.github.io/My-Exams/upper-grades-practice.html
   - https://github.com/rouhous/My-Exams/blob/main/UPPER_GRADES_RELEASE_GATE_2026-11-14.json

## Important format caution
The user-provided **2025/26 Grade 12 Core** first-session PDF is a 3-hour, 70-mark paper; its actual section labels include separate Vocabulary (2½), Grammar (2½), and Grammar/Vocabulary (5), in addition to two Listening, three Reading and two Writing tasks. The repository's separate **September 2026 SAH summary** presents combined grammar/vocabulary categories differently. Record reference year and the current applicable assessment handbook; do not merge old paper labels silently into the new claimed official schema.

## The next CONTENT tasks, in order
1. **Grade 12 Elective**: rewrite A–D so unit 1 **The arts**, unit 2 **Doing the right thing**, unit 3 **Living in a Changing World**, unit 4 **Higher Education** each has genuinely distinct, book-grounded Listening 1/2, Reading 1/2, Writing 1/2. Use stored SAH length/task formats and attach provenance; NEVER merely relabel the old Coastal Science Station texts. Re-audit cross-track duplication. Generate/check scripts before authentic dual-voice/natural MP3.
2. **Grade 11 Elective**: independent A–D for Fame / The mind / In the past / Careers, replacing mismatched draft titles and duplicated reading/listening texts.
3. **Grade 12 Core**: check every section of A–D against Retail Therapy / Starting University / Tourism and Hospitality / Travel and Transport; replace the unrelated coast-research sections in ostensibly Retail Therapy model A and other repeated source texts; incorporate exam year/SAH distinctions.
4. **Grade 11 Core**: expand the independent nine-section Paper A into B/C/D (and mixed E/F only where whole-section sources are verified); then audio/QA.
5. **Grade 5–10**: complete per-unit, per-skill page-level source audit. Do not mark “certified” just because model theme matches unit label. Finish Grade 1–4 with the right age/assessment templates.
6. After all scripts are teacher-review-ready, produce/test natural MP3, validate full question/audio alignment, offline install/phone; only then final student release and verified server-side Writing AI marking.

## Technical checks and privacy
- Run upper-grade GitHub Actions and inspect failing logs. Pages workflow may cancel older runs whenever a newer commit is pushed.
- Keep exam practice separate from My English Journey and School Teacher Notebook. Do not copy API keys or user data into public HTML/JSON. No new writing-AI endpoint has been published by this continuation.
- Preserve existing bank material while working; repair in small reviewable commits and never claim educational approval without it.


## Update after user provided a closed Work conversation share link
- Shared link: https://chatgpt.com/share/6af7ab7f-7c00-83ed-aea0-8e3b1aa32fc6?ogimg=plain . Browser fetch returned no conversation text; **do not claim it was fully reviewed**.
- Recovered personal Library sources: English_Insights_3_Enhanced_Sem1_Grade12_EDITABLE.docx and elective 12 sem1.pdf. These are older 2025/26 practice booklets with two A/B unit tests for each of Grade 12 elective units 1–4, plus a final paper. They are NOT evidence of Work's latest 2026/27 state.
- QA: docs/PRIOR_G12_ELECTIVE_BOOKLET_AUDIT_2026-11-14.json. Eight unit tests + one full practice; all 18 Reading texts are short against the stored SAH 450–500 words (approx. 183–343 words). Only Unit 1 Test A has two Listening script fragments: 109-word five-turn dialogue plus 75-word monologue summary. Another 16 Listening scripts are absent. Answer keys are partial. Do NOT migrate blindly.
- New original teacher-led Grade 12 Elective Unit 1 The arts Listening 1+2 drafts:
  - grade12/elective/units/unit1-listening1-original-draft.json: 408 words / 28 turns / 6 MCQ + 4 T/F.
  - grade12/elective/units/unit1-listening2-original-draft.json: 461 words / 5 note-heading items + 5 short answers.
  - grade12/elective/units/index.html: choose task; L1 automatic objective score; L2 suggested teacher key, NO untrustworthy automatic score. Scripts are read aloud; NO validated natural MP3 yet.
  - SW shell cache includes both JSONs; Pages stages grade12/elective/units; QA in tests/upper_grades_browser_smoke.cjs and .github/workflows/upper-grades-qa.yml.
- Pages workflow now waits 25 seconds after uploading approx. 108 MB archive to mitigate GitHub Actions artifact indexing race. Verify latest deployment run before claiming the site is updated.
- Update: Grade 12 Elective Unit 1 now has SIX original teacher-review tasks (L1:408 words/28 turns/10 questions; L2:461 words/10; R1:496 words/12; R2:484 words/13; Writing 1:15 marks; Writing 2:10 marks and chart). A new complete 70-mark Paper A at grade12/elective/units/paper-a-preview.html offers a 180-minute full exam or six untimed individual skills. It auto-scores 23 objective items only, shows teacher keys for 22 short items, and leaves 2 writing tasks for rubric review. NO natural MP3 and NO textbook-page certification yet.
- Next: complete grade 12 elective Units 2–4 with original six-section papers and curated comprehensive mixed exams; build/validate audio only after all listening scripts are teacher-reviewed; expand the same paper model across grades/tracks.
