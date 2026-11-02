# Jazz Walking Basslines

Original note-only MIDI studies of quarter-note walking lines over explicit chord changes. Eight studies, two variations of the walking bass. Chord shells are cataloged separately and are not part of the core count. They are not merged into the bass files.

This repository is the pack. The GitHub repository is https://github.com/mizcausevic-dev/jazz-walking-basslines and it is public. The catalog page is https://mizcausevic-dev.github.io/jazz-walking-basslines/ .

## What you can open

- `index.html` is the file catalog. The walk is drawn from the MIDI bytes.
- `media.html` is the stills page. The film sits under the pictures.
- `midi/arrangement.mid` is a Format 1 preview arrangement of study 01, variation A: walking bass and chord reference.
- Individual Format 0 parts live under `midi/`.
- `midi/validation-Cursor.json` is the report from reopening those exact bytes.
- `preview/preview.mp3` is the primary music preview. It is 17.778 seconds in the encoded file. preview, not a master.
- `film/preview.mp4` and `film/preview.vtt` are the film. On-picture and caption text is `preview, not master`.
- `art/hero.jpg` is a 1280x720 illustration. `art/square.jpg` is 1080x1080. Neither is a photograph.

Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.

## Studies

- s01 Stroll: 108 BPM, 8 bars, Bb major, tonic reference Bb.
- s02 Chorus: 124 BPM, 16 bars, F major, tonic reference F.
- s03 Drop: 132 BPM, 8 bars, G natural minor, tonic reference G.
- s04 Two Feel: 96 BPM, 8 bars, C major, tonic reference C.
- s05 Pickup: 140 BPM, 16 bars, Eb major, tonic reference Eb.
- s06 Push: 116 BPM, 8 bars, D Dorian, tonic reference D.
- s07 Cadence: 100 BPM, 8 bars, A major, tonic reference A.
- s08 Breather: 148 BPM, 16 bars, C natural minor, tonic reference C.

Core files: 16. Reference files: 8.

Walking bass is monophonic, MIDI 28 to 55 (E1 to G3), standard four-string tuning EADG. Chord references are separate shells from MIDI 48 to 76 and are not part of the core count. C4 is 60. PPQ is 960. Meter is 4/4. Offsets are 0. Seeds identify studies and are not random draws. Generator 1.0.0. Not every beat is a root. Harmonic rhythm is written on each study.

## Preview path

The preview renders the canonical notes for `s01.walk.a` and `s01.chords` with `simple-synth-1.0.0`. Tempo authority is the encoded microsecond value in the MIDI, 555556 us per quarter note. Sample positions use `floor(seconds * 44100 + 0.5)` from tick 0. Intervals are not summed. Sample-exact repeating loops at an arbitrary BPM are not promised.

The synth mapping is a sine for the walking bass and a quiet triangle for the chord shells. No program changes are encoded. A conventional GM player will normally use its default piano program for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. Player behavior may vary. The mapping is not encoded in the MIDI.

Encoded MP3 settings: libmp3lame, 192 kbps. Film audio is AAC at 160 kbps re-encoded from that MP3, so the decoded film audio is not byte-identical to the MP3. Film duration probe: 17.778 seconds. MP3 container probe 17.778 seconds. MP4 probe 17.778 seconds. The film ends on a video frame, so it is slightly shorter than the MP3 container. The music is the same preview, not a different excerpt. The picture is a still illustration with rasterized disclosure text. DejaVu Sans Bold from the build machine supplies the glyphs. The font file is not in this pack.

No human listening audition was performed for this build. A sample peak is recorded in the preview manifest. It is not LUFS and it is not a true peak.

## Build

From the repository root, with Python 3.11+ and ffmpeg (libmp3lame, aac, libx264):

```bash
python3 tools/build_pack.py
python3 -m http.server 41773
```

The page is static. It is served with Python's HTTP server so the MIDI and media keep working relative paths. There is no application server and no package install. Standard library only.

`build/` holds the intermediate WAV, the procedural PPM, and the film plate. Those files are gitignored. The delivered audio is the MP3.

## Checks the validator actually runs

File existence, parse, PPQ, tempo, 4/4, end-of-track boundary, note pairing, ranges, monophonic bass, chord-reference polyphony cap of three, note-off before note-on at a shared tick, absence of program changes and other channel messages, departure flags against the declared pitch-class set, agreement with the canonical score, and agreement between `arrangement.mid` and the two source files. A negative overlap fixture is written outside the pack and must be rejected.

## Drafts and publication

Social captions, the X post, and the Medium article are drafts. They are not access controls. If this repository is public, the drafts are public. Do not treat them as posted to Instagram, X, or Medium.

Prepared repository description: Original note-only MIDI studies of jazz walking basslines, with matched validation and a simple-synth preview.

Prepared topics: midi, jazz, walking-bass, music-production, composition, general-midi, study-pack.

No release tag was created. `index.html` keeps its name because players and links depend on it. This page is the file catalog the pack requires.

## Limitations

Variation compatibility is per study and is written on the page. Variation A and variation B of a study are alternatives. Both walk the same chord reference. The arrangement is only study 01. Stacking it with the part files doubles those notes.
