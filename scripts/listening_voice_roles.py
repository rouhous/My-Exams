"""Deterministic, reviewed English voices for My Exams listening passages.

A pronoun about a third person is NOT evidence about who is speaking.
Assign voice by an explicit speaker label, approved role metadata, or a
first-person self-identification. Never guess the gender of an unknown name.
"""
import re

VOICE_NAMES = (
    'en-GB-SoniaNeural',  # 0: female narrator / interviewer
    'en-GB-RyanNeural',   # 1: male interviewee
    'en-GB-LibbyNeural',  # 2: female interviewee (distinct from host)
)
MALE, FEMALE = 'male', 'female'
KNOWN_GENDERS = {
    'sam': MALE, 'salim': MALE, 'faris': MALE, 'hamad': MALE,
    'ahmed': MALE, 'yousuf': MALE, 'nasser': MALE, 'rashid': MALE,
    'sami': MALE, 'ali': MALE, 'hassan': MALE, 'hamed': MALE,
    'salma': FEMALE, 'mariam': FEMALE, 'fatma': FEMALE,
    'dana': FEMALE, 'alya': FEMALE, 'maha': FEMALE,
    'hind': FEMALE, 'amal': FEMALE, 'sara': FEMALE, 'aisha': FEMALE,
    'huda': FEMALE, 'noura': FEMALE, 'bilal': MALE,
    'amina': FEMALE, 'reem': FEMALE, 'rana': FEMALE, 'layla': FEMALE,
    'maya': FEMALE, 'hamid': MALE, 'khalid': MALE, 'omar': MALE,
}
HOST_ROLES = {'interviewer', 'host', 'presenter', 'narrator', 'counsellor', 'counselor', 'adviser', 'advisor', 'teacher', 'engineer', 'guide'}
SPEAKER_RE = re.compile(r'(?<![A-Za-z0-9])([A-Za-z][A-Za-z0-9]*)\s*:\s*')
SELF_NAME_RE = re.compile(r"\b(?:my name is|i am|i'm)\s+([A-Za-z]+)\b", re.I)


def _gender(value):
    if value is None or str(value).strip() == '':
        return None
    value = str(value).lower().strip()
    if value not in (MALE, FEMALE):
        raise ValueError('speaker gender must be male/female, got: ' + value)
    return value


def voice_for_speaker(name, overrides=None):
    """Return a VOICE_NAMES index. Unknown named speakers need explicit metadata."""
    overrides = {str(k).lower(): v for k, v in (overrides or {}).items()}
    key = name.strip().lower()
    g = _gender(overrides.get(key))
    if g is None:
        if key in HOST_ROLES or key == 'a':
            return 0  # unspecified host/anonymous role; not a gender inference
        if key == 'b':
            return 1  # anonymous second role; not a gender inference
        g = KNOWN_GENDERS.get(key)
    if g is None:
        raise ValueError('Unmapped speaker ' + repr(name) + ': provide speakerGenders metadata')
    # A female interviewer/host uses the main presenter voice (Sonia),
    # distinct from the female interviewee (Libby). Explicit male hosts
    # still use Ryan; never infer their gender from third-person pronouns.
    if key in HOST_ROLES and g == FEMALE:
        return 0
    return 1 if g == MALE else 2


def voice_for_narration(text, explicit_gender=None, fallback_voice=0):
    """Only infer from the narrator's OWN identity, not he/his/she/her about others."""
    g = _gender(explicit_gender)
    if g is None:
        match = SELF_NAME_RE.search(text)
        if match:
            name = match.group(1).lower()
            if name in KNOWN_GENDERS:
                g = KNOWN_GENDERS[name]
    if g is None:
        if re.search(r"\b(?:i am|i'm) a (?:boy|man)\b", text, re.I):
            g = MALE
        elif re.search(r"\b(?:i am|i'm) a (?:girl|woman)\b", text, re.I):
            g = FEMALE
    return 1 if g == MALE else (0 if g == FEMALE else fallback_voice)  # unknown narrator: editorial fallback, never infer from he/she


def parse_dialogue(text, overrides=None):
    """Return (spoken text, voice index, speaker) for named A:/B:/Sam:/etc turns."""
    matches = list(SPEAKER_RE.finditer(text))
    if not matches:
        return []
    if text[:matches[0].start()].strip():
        raise ValueError('Unassigned text before first speaker: ' + text[:60])
    turns = []
    for i, match in enumerate(matches):
        label = match.group(1)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        utterance = text[match.end():end].strip()
        if not utterance:
            raise ValueError('Empty speech for ' + label)
        turns.append((utterance, voice_for_speaker(label, overrides), label))
    return turns
