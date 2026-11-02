"""Factual article draft. Not published."""

from __future__ import annotations

from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING

TITLE = "Jazz Walking Basslines is a note-only MIDI study pack"
SUBTITLE = "Eight walks over explicit changes, a matched byte check, and a simple-synth preview that is not a master"
TAGS = ["midi", "jazz", "bass", "music-production", "composition"]
TAG_LINE = "Tags: " + ", ".join(TAGS)

PARAGRAPHS = [
    "DRAFT. " + PUBLICATION,
    TAG_LINE,
    "The pack is eight walking-bass studies in 4/4. Tempos sit between 90 and 150 BPM. Lengths are 8 or 16 bars, chosen before the notes. Each study has two bass variations. That is the core: sixteen files. Each study also has one chord-reference file, a shell voicing of the changes. Those eight files are not part of the core count, and they are not merged into the bass files.",
    "A variation has to change the line. Holding the same pitches and only editing velocity does not count. Stroll walks one chord per bar in Bb. Chorus is sixteen bars in F, roots in variation A and sevenths in variation B. Drop rests on beat 4. Two Feel is half notes, and variation B breaks them into quarters. Pickup leaves the first downbeat empty. Push arrives an eighth early at each change. Cadence walks four bars and then sits on a half-note pedal. Breather leaves three downbeats silent.",
    "The bass stays between MIDI 28 and 55, E1 to G3, and it is monophonic. That is the range of a standard four-string bass in EADG. No alternate tuning is claimed. Chord shells stay between MIDI 48 and 76, with at most three notes. C4 is 60. The resolution is 960 ticks per quarter note. There is no swing offset. Not every beat is a root. The harmonic rhythm is written on each study.",
    PROGRAM,
    "Swing, pedal, and upright-bass technique are not in the files. The preview synth uses a sine for the bass and a quiet triangle for the shells. That mapping is documented. It is not a program change.",
    "The primary preview is study 01, Stroll, variation A, for all 8 bars: the walking bass and the chord reference together. The other studies are in the MIDI and are not in that audio file. "
    + PREVIEW_LINE
    + ". The film takes its audio from that preview file and shows the words "
    + ON_PICTURE
    + " on the picture and in the WebVTT captions.",
    AUDITION
    + " The validator reopened the MIDI bytes and compared them with the canonical score. That is a structural check. The sample peak written beside the preview is the peak of the integer mix. It is not LUFS and it is not a true-peak reading. Nothing in this build is claimed as a master.",
    "The stills are procedural illustrations of a walking path on an ivory lane. They are not photographs of a session or of performers.",
    "When a public URL exists, use either the combined arrangement or the separate parts. " + WARNING,
    "Call to action: the MIDI, the matched report, and the preview belong together. Do not publish this draft to Medium, Instagram, or X from the draft files alone.",
]


def markdown() -> str:
    body = "\n\n".join(PARAGRAPHS)
    return f"# {TITLE}\n\n{SUBTITLE}\n\n{body}\n"


def plain_text() -> str:
    lines = [TITLE, "", SUBTITLE, "", *PARAGRAPHS, ""]
    return "\n".join(lines) + "\n"
