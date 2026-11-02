"""Original jazz walking bass lines.

Tempos, lengths, and collections are fixed before the notes. The bass is
monophonic and stays between MIDI 28 and 55, standard EADG tuning. Chord
shells are a separate reference and are not core. Offsets are 0.
"""

from __future__ import annotations

from tools.midi_io import BAR_TICKS_4_4, PPQ, bpm_to_us, effective_bpm

GENERATOR_VERSION = "1.0.0"
PACK_ID = "jazz-walking-basslines"
PACK_NAME = "Jazz Walking Basslines"
BAR = BAR_TICKS_4_4


class Part:
    def __init__(self, study, part_id, role, variation, core, channel, slug, mono, poly, lo, hi):
        self.study = study
        self.part_id = part_id
        self.role = role
        self.variation = variation
        self.core = core
        self.channel = channel
        self.file_slug = slug
        self.monophonic = mono
        self.max_poly = poly
        self.lo = lo
        self.hi = hi
        self.container_ticks = study["bars"] * BAR
        self.notes = []

    def add(self, start, duration, pitch, velocity, departure=False):
        end = start + duration
        if start < 0 or duration <= 0 or end > self.container_ticks:
            raise ValueError(f"{self.part_id} boundary {start}+{duration}")
        if not self.lo <= pitch <= self.hi:
            raise ValueError(f"{self.part_id} pitch {pitch}")
        active = 1
        for other in self.notes:
            o0 = other["performed_start"]
            o1 = o0 + other["duration"]
            if start < o1 and o0 < end:
                if other["pitch"] == pitch or self.monophonic:
                    raise ValueError(f"{self.part_id} overlap {pitch}@{start}")
                active += 1
        if active > self.max_poly:
            raise ValueError(f"{self.part_id} poly {active}")
        self.notes.append({
            "nominal_start": start, "offset": 0, "performed_start": start,
            "duration": duration, "pitch": pitch, "velocity": velocity,
            "channel": self.channel, "departure": departure,
        })

    def finish(self):
        ordered = sorted(self.notes, key=lambda n: (n["performed_start"], n["pitch"]))
        if self.core and len(ordered) < 8:
            raise ValueError(f"{self.part_id} too few notes")
        if not ordered:
            raise ValueError(f"{self.part_id} empty")
        for i, note in enumerate(ordered, 1):
            note["id"] = f"{self.part_id}.n{i:04d}"
        return {
            "id": self.part_id, "study_id": self.study["id"], "slug": self.study["slug"],
            "role": self.role, "variation": self.variation, "core": self.core,
            "channel": self.channel, "file_slug": self.file_slug,
            "path": f"midi/{self.study['slug']}/{self.file_slug}.mid",
            "monophonic": self.monophonic, "max_poly": self.max_poly,
            "container_ticks": self.container_ticks, "container_bars": self.study["bars"],
            "bpm": self.study["bpm"], "tempo_us": self.study["tempo_us"], "notes": ordered,
        }


def bass(study, variation):
    return Part(study, f"{study['id']}.walk.{variation}", "walking-bass", variation, True, 0, f"walk-{variation}", True, 1, 28, 55)


def shells(study):
    return Part(study, f"{study['id']}.chords", "chord-reference", "ref", False, 1, "chords", False, 3, 48, 76)


def bar(n, beats=0):
    return n * BAR + beats * PPQ


def place_grid(part, rows, skip=0, drop=()):
    items = []
    for index, row in enumerate(rows):
        for beat, pair in enumerate(row):
            if (index, beat) in drop:
                continue
            items.append((index, beat, pair))
    for index, beat, (pitch, departure) in items[skip:]:
        part.add(bar(index, beat), PPQ, pitch, 92 if beat == 0 else 76, departure=departure)


def place_halves(part, rows):
    for index, row in enumerate(rows):
        for beat, (pitch, departure) in enumerate(row):
            part.add(bar(index) + beat * PPQ * 2, PPQ * 2, pitch, 90 if beat == 0 else 74, departure=departure)


def place_push(part, rows):
    for index, row in enumerate(rows):
        if index in (1, 3, 5):
            for beat in range(3):
                pitch, departure = row[beat]
                part.add(bar(index, beat), PPQ, pitch, 80, departure=departure)
            pitch, departure = row[3]
            part.add(bar(index, 3), PPQ // 2, pitch, 74, departure=departure)
            nxt, ndep = rows[index + 1][0]
            part.add(bar(index, 3) + PPQ // 2, PPQ // 2, nxt, 98, departure=ndep)
        else:
            for beat, (pitch, departure) in enumerate(row):
                part.add(bar(index, beat), PPQ, pitch, 88 if beat == 0 else 76, departure=departure)


def add_shells(part, chords):
    for start_bar, length, notes in chords:
        for pitch, departure in notes:
            part.add(bar(start_bar), length * BAR, pitch, 68, departure=departure)


def n(pitch, departure=False):
    return (pitch, departure)


def studies():
    rows = [
        {"id": "s01", "slug": "s01-stroll", "title": "Stroll", "bpm": 108, "bars": 8,
         "tonic": "Bb", "tonal_reference": "Bb", "collection_name": "Bb major",
         "pitch_classes": [10, 0, 2, 3, 5, 7, 9],
         "departures": ["F# and B leave Bb major. They are the chromatic approach into G and the third of G7."],
         "seed": 10801,
         "harmonic_rhythm": "One chord per bar: Bbmaj7, Ebmaj7, Dm7, G7, Cm7, F7, Bbmaj7, F7.",
         "changes": ["Bbmaj7", "Ebmaj7", "Dm7", "G7", "Cm7", "F7", "Bbmaj7", "F7"],
         "change_bars": [1, 1, 1, 1, 1, 1, 1, 1],
         "identity": "Quarter notes for eight bars. Beat 1 is a root on Bb, Eb, Dm, G, Cm, and F, then the last two bars move to a third and a fifth. Variation B starts each bar on a third or fifth instead.",
         "limitations": "Both bass variations walk this one chord reference. They are alternatives. Beat 4 of bar 3 is B, the third of G7, and it is flagged.",
         "voicing": "Bass range E1 to G3. The chord reference is a third and a seventh, held for the bar. Roots are not doubled into the chord file."},
        {"id": "s02", "slug": "s02-chorus", "title": "Chorus", "bpm": 124, "bars": 16,
         "tonic": "F", "tonal_reference": "F", "collection_name": "F major",
         "pitch_classes": [5, 7, 9, 10, 0, 2, 4],
         "departures": ["B, F#, and C# leave F major. B is the third of G7. F# is the third of D7 and one approach. C# approaches D."],
         "seed": 12402,
         "harmonic_rhythm": "Two bars per chord: Dm7, G7, Gm7, C7, Am7, D7, Gm7, C7.",
         "changes": ["Dm7", "G7", "Gm7", "C7", "Am7", "D7", "Gm7", "C7"],
         "change_bars": [2, 2, 2, 2, 2, 2, 2, 2],
         "identity": "A 16-bar chorus of quarter notes. Variation A aims at roots on the downbeats. Variation B aims at sevenths and turns the bar around.",
         "limitations": "The chord reference holds each shell for two bars. Use it with either bass variation, not with both at once.",
         "voicing": "Shells are the third and seventh. The bass walks inside E1 to G3."},
        {"id": "s03", "slug": "s03-drop", "title": "Drop", "bpm": 132, "bars": 8,
         "tonic": "G", "tonal_reference": "G", "collection_name": "G natural minor",
         "pitch_classes": [7, 9, 10, 0, 2, 3, 5],
         "departures": ["F# leaves G natural minor. It is the third of D7."],
         "seed": 13203,
         "harmonic_rhythm": "Two bars per chord: Gm7, Cm7, D7, Gm7. Variation A rests on beat 4 of every bar.",
         "changes": ["Gm7", "Cm7", "D7", "Gm7"],
         "change_bars": [2, 2, 2, 2],
         "identity": "The walk stops on beat 4, so the chord change has air. Variation B fills those beats and keeps moving.",
         "limitations": "The rest is written as silence, not as a tied note. The chord reference still holds through beat 4.",
         "voicing": "Two-note shells. Bass notes are quarters on beats 1, 2, and 3 in variation A."},
        {"id": "s04", "slug": "s04-two-feel", "title": "Two Feel", "bpm": 96, "bars": 8,
         "tonic": "C", "tonal_reference": "C", "collection_name": "C major",
         "pitch_classes": [0, 2, 4, 5, 7, 9, 11], "departures": [], "seed": 9604,
         "harmonic_rhythm": "Two bars per chord: Cmaj7, Am7, Dm7, G7.",
         "changes": ["Cmaj7", "Am7", "Dm7", "G7"],
         "change_bars": [2, 2, 2, 2],
         "identity": "Half notes only: root then fifth, or third then root. Variation B breaks the same changes into quarter notes.",
         "limitations": "Variation A is a two-feel, not a missing walk. Nothing in this study leaves C major, so nothing is flagged.",
         "voicing": "Half-note bass against shells held for two bars."},
        {"id": "s05", "slug": "s05-pickup", "title": "Pickup", "bpm": 140, "bars": 16,
         "tonic": "Eb", "tonal_reference": "Eb", "collection_name": "Eb major",
         "pitch_classes": [3, 5, 7, 8, 10, 0, 2],
         "departures": ["A leaves Eb major as the third of F7. E leaves Eb major as the third of C7."],
         "seed": 14005,
         "harmonic_rhythm": "One chord per bar across 16 bars: Ebmaj7, Fm7, Gm7, Abmaj7, Bb7, Ebmaj7, Cm7, F7, Bb7, Ebmaj7, Abmaj7, Ebmaj7, Fm7, Bb7, Ebmaj7, C7.",
         "changes": ["Ebmaj7", "Fm7", "Gm7", "Abmaj7", "Bb7", "Ebmaj7", "Cm7", "F7", "Bb7", "Ebmaj7", "Abmaj7", "Ebmaj7", "Fm7", "Bb7", "Ebmaj7", "C7"],
         "change_bars": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
         "identity": "Variation A leaves beat 1 empty and enters on beat 2. Variation B plays the downbeat and aims at thirds.",
         "limitations": "The first downbeat of variation A is silent on purpose. The chord reference still sounds there.",
         "voicing": "Shells last one bar. The bass pickup is inside the file, not a negative start."},
        {"id": "s06", "slug": "s06-push", "title": "Push", "bpm": 116, "bars": 8,
         "tonic": "D", "tonal_reference": "D", "collection_name": "D Dorian",
         "pitch_classes": [2, 4, 5, 7, 9, 11, 0],
         "departures": ["Bb leaves D Dorian as the fifth of Em7b5. C# leaves D Dorian as the third of A7."],
         "seed": 11606,
         "harmonic_rhythm": "Two bars per chord: Dm7, G7, Em7b5, A7. Variation A arrives an eighth early at each change.",
         "changes": ["Dm7", "G7", "Em7b5", "A7"],
         "change_bars": [2, 2, 2, 2],
         "identity": "Quarter notes, with the next downbeat pushed onto the last eighth of the previous bar. Variation B waits for the downbeat and aims at sevenths.",
         "limitations": "The pushed note is the same pitch as the following downbeat. They meet at the barline and do not overlap.",
         "voicing": "The anticipation is an eighth note in the bass file. The chord reference still changes on the downbeat."},
        {"id": "s07", "slug": "s07-cadence", "title": "Cadence", "bpm": 100, "bars": 8,
         "tonic": "A", "tonal_reference": "A", "collection_name": "A major",
         "pitch_classes": [9, 11, 1, 2, 4, 6, 8],
         "departures": ["Variation B ends on G2, a step below A. That G is flagged. Variation A stays inside A major."],
         "seed": 10007,
         "harmonic_rhythm": "One bar each of Amaj7, Dmaj7, Bm7, E7, then four bars of A.",
         "changes": ["Amaj7", "Dmaj7", "Bm7", "E7", "A"],
         "change_bars": [1, 1, 1, 1, 4],
         "identity": "Four bars of quarters, then a half-note pedal on A. Variation B keeps walking and ends on a flagged G.",
         "limitations": "The four-bar pedal is the cadence. The chord reference holds Amaj7 shells under it.",
         "voicing": "Half notes in the pedal are root then fifth or third. The last chord shell lasts four bars."},
        {"id": "s08", "slug": "s08-breather", "title": "Breather", "bpm": 148, "bars": 16,
         "tonic": "C", "tonal_reference": "C", "collection_name": "C natural minor",
         "pitch_classes": [0, 2, 3, 5, 7, 8, 10],
         "departures": ["B leaves C natural minor. It is the third of G7."],
         "seed": 14808,
         "harmonic_rhythm": "Two bars per chord: Cm7, Fm7, G7, Cm7, Abmaj7, Bb7, Gm7, G7. Variation A rests on beat 1 of bars 4, 8, and 12.",
         "changes": ["Cm7", "Fm7", "G7", "Cm7", "Abmaj7", "Bb7", "Gm7", "G7"],
         "change_bars": [2, 2, 2, 2, 2, 2, 2, 2],
         "identity": "A 16-bar walk with three downbeat breaths. Variation B plays those downbeats as the third of the chord.",
         "limitations": "The breaths are rests, not ties. Bars are numbered from 1 in the description and from 0 in the file.",
         "voicing": "Shells last two bars. The B on G7 is flagged in both the bass and the chord reference."},
    ]
    for row in rows:
        if not 90 <= row["bpm"] <= 150:
            raise ValueError(row["bpm"])
        if sum(row["change_bars"]) != row["bars"] or len(row["change_bars"]) != len(row["changes"]):
            raise ValueError(row["id"])
        row["tempo_us"] = bpm_to_us(row["bpm"])
        row["effective_bpm"] = effective_bpm(row["tempo_us"])
        row["meter"] = "4/4"
        row["bar_ticks"] = BAR
        row["ppq"] = PPQ
        row["stochastic_draws"] = 0
    return rows


def _s01(study):
    a, b, chords = bass(study, "a"), bass(study, "b"), shells(study)
    place_grid(a, [
        [n(34), n(41), n(46), n(45)],
        [n(39), n(41), n(43), n(38)],
        [n(38), n(41), n(43), n(42, True)],
        [n(43), n(47, True), n(46), n(45)],
        [n(36), n(39), n(41), n(43)],
        [n(41), n(45), n(48), n(46)],
        [n(46), n(43), n(41), n(39)],
        [n(41), n(45), n(43), n(34)],
    ])
    place_grid(b, [
        [n(41), n(46), n(48), n(50)],
        [n(51), n(50), n(48), n(46)],
        [n(50), n(46), n(43), n(42, True)],
        [n(43), n(45), n(46), n(48)],
        [n(48), n(51), n(53), n(50)],
        [n(53), n(50), n(48), n(45)],
        [n(46), n(48), n(50), n(51)],
        [n(41), n(39), n(36), n(34)],
    ])
    add_shells(chords, [
        (0, 1, [n(62), n(69)]),
        (1, 1, [n(67), n(74)]),
        (2, 1, [n(65), n(72)]),
        (3, 1, [n(59, True), n(65)]),
        (4, 1, [n(63), n(70)]),
        (5, 1, [n(69), n(75)]),
        (6, 1, [n(62), n(69)]),
        (7, 1, [n(69), n(75)]),
    ])
    return [a, b, chords]


def _s02(study):
    a, b, chords = bass(study, "a"), bass(study, "b"), shells(study)
    rows_a = [
        [n(38), n(41), n(43), n(42, True)],
        [n(41), n(45), n(43), n(41)],
        [n(43), n(47, True), n(45), n(43)],
        [n(47, True), n(46), n(45), n(43)],
        [n(43), n(46), n(48), n(50)],
        [n(46), n(48), n(45), n(43)],
        [n(48), n(52), n(50), n(48)],
        [n(52), n(50), n(48), n(45)],
        [n(45), n(48), n(50), n(52)],
        [n(48), n(50), n(52), n(49, True)],
        [n(50), n(54, True), n(52), n(50)],
        [n(42, True), n(45), n(47, True), n(45)],
        [n(43), n(46), n(48), n(46)],
        [n(41), n(43), n(45), n(43)],
        [n(48), n(52), n(53), n(52)],
        [n(50), n(48), n(45), n(43)],
    ]
    leads = [n(48), n(48), n(41), n(41), n(41), n(41), n(46), n(46), n(43), n(43), n(48), n(48), n(41), n(41), n(46), n(46)]
    rows_b = []
    for row, lead in zip(rows_a, leads):
        body = [pair for pair in reversed(row) if pair[0] != lead[0]][:3]
        while len(body) < 3:
            body.append(row[1])
        rows_b.append([lead, *body])
    place_grid(a, rows_a)
    place_grid(b, rows_b)
    add_shells(chords, [
        (0, 2, [n(65), n(72)]),
        (2, 2, [n(59, True), n(65)]),
        (4, 2, [n(58), n(65)]),
        (6, 2, [n(64), n(70)]),
        (8, 2, [n(60), n(67)]),
        (10, 2, [n(66, True), n(72)]),
        (12, 2, [n(58), n(62)]),
        (14, 2, [n(64), n(70)]),
    ])
    return [a, b, chords]


def _s03(study):
    a, b, chords = bass(study, "a"), bass(study, "b"), shells(study)
    place_grid(a, [
        [n(31), n(34), n(36)],
        [n(38), n(36), n(34)],
        [n(36), n(39), n(41)],
        [n(43), n(41), n(39)],
        [n(38), n(42, True), n(41)],
        [n(45), n(43), n(42, True)],
        [n(43), n(41), n(39)],
        [n(38), n(36), n(31)],
    ])
    place_grid(b, [
        [n(31), n(34), n(36), n(38)],
        [n(38), n(36), n(34), n(31)],
        [n(36), n(39), n(41), n(43)],
        [n(43), n(41), n(39), n(36)],
        [n(38), n(42, True), n(41), n(43)],
        [n(45), n(43), n(42, True), n(38)],
        [n(43), n(41), n(39), n(38)],
        [n(36), n(34), n(31), n(34)],
    ])
    add_shells(chords, [
        (0, 2, [n(58), n(65)]),
        (2, 2, [n(63), n(70)]),
        (4, 2, [n(66, True), n(72)]),
        (6, 2, [n(58), n(62)]),
    ])
    return [a, b, chords]


def _s04(study):
    a, b, chords = bass(study, "a"), bass(study, "b"), shells(study)
    place_halves(a, [
        [n(36), n(43)],
        [n(40), n(36)],
        [n(33), n(40)],
        [n(36), n(33)],
        [n(38), n(41)],
        [n(45), n(38)],
        [n(43), n(47)],
        [n(45), n(43)],
    ])
    place_grid(b, [
        [n(36), n(40), n(43), n(41)],
        [n(40), n(43), n(45), n(47)],
        [n(33), n(36), n(40), n(38)],
        [n(36), n(40), n(43), n(41)],
        [n(38), n(41), n(45), n(43)],
        [n(41), n(43), n(45), n(40)],
        [n(43), n(47), n(45), n(43)],
        [n(47), n(45), n(43), n(36)],
    ])
    add_shells(chords, [
        (0, 2, [n(64), n(71)]),
        (2, 2, [n(60), n(67)]),
        (4, 2, [n(65), n(72)]),
        (6, 2, [n(59), n(65)]),
    ])
    return [a, b, chords]


def _s05(study):
    a, b, chords = bass(study, "a"), bass(study, "b"), shells(study)
    roots = [39, 41, 43, 44, 46, 39, 36, 41, 46, 39, 44, 39, 41, 46, 39, 36]
    allowed = set(study["pitch_classes"])
    rows_a = []
    for index, root in enumerate(roots):
        nxt = roots[(index + 1) % len(roots)]
        second = root + 2 if (root + 2) % 12 in allowed and root + 2 <= 55 else root - 2
        fifth = root + 7 if root + 7 <= 55 and (root + 7) % 12 in allowed else root - 5
        approach = nxt - 1
        rows_a.append([
            n(root),
            n(second, (second % 12) not in allowed),
            n(fifth, (fifth % 12) not in allowed),
            n(approach, (approach % 12) not in allowed),
        ])
    thirds = {
        39: 43, 41: 44, 43: 46, 44: 48, 46: 50, 36: 39,
    }
    rows_b = []
    for row, root in zip(rows_a, roots):
        lead = n(thirds[root], (thirds[root] % 12) not in allowed)
        body = [pair for pair in row[1:]]
        rows_b.append([lead, *body])
    place_grid(a, rows_a, skip=1)
    place_grid(b, rows_b)
    add_shells(chords, [
        (0, 1, [n(67), n(74)]),
        (1, 1, [n(68), n(75)]),
        (2, 1, [n(58), n(65)]),
        (3, 1, [n(60), n(67)]),
        (4, 1, [n(62), n(68)]),
        (5, 1, [n(67), n(74)]),
        (6, 1, [n(63), n(70)]),
        (7, 1, [n(69, True), n(75)]),
        (8, 1, [n(62), n(68)]),
        (9, 1, [n(67), n(74)]),
        (10, 1, [n(60), n(67)]),
        (11, 1, [n(58), n(67)]),
        (12, 1, [n(68), n(72)]),
        (13, 1, [n(62), n(65)]),
        (14, 1, [n(67), n(70)]),
        (15, 1, [n(64, True), n(70)]),
    ])
    return [a, b, chords]


def _s06(study):
    a, b, chords = bass(study, "a"), bass(study, "b"), shells(study)
    rows = [
        [n(38), n(41), n(43), n(45)],
        [n(43), n(41), n(40), n(38)],
        [n(43), n(47), n(45), n(43)],
        [n(47), n(45), n(43), n(41)],
        [n(40), n(43), n(46, True), n(45)],
        [n(43), n(40), n(38), n(36)],
        [n(45), n(49, True), n(48), n(47)],
        [n(45), n(43), n(40), n(38)],
    ]
    place_push(a, rows)
    place_grid(b, [
        [n(36), n(38), n(40), n(41)],
        [n(40), n(38), n(36), n(35)],
        [n(41), n(43), n(45), n(47)],
        [n(45), n(43), n(41), n(40)],
        [n(38), n(40), n(41), n(46, True)],
        [n(43), n(41), n(40), n(38)],
        [n(43), n(45), n(47), n(49, True)],
        [n(47), n(45), n(43), n(38)],
    ])
    add_shells(chords, [
        (0, 2, [n(65), n(72)]),
        (2, 2, [n(59), n(65)]),
        (4, 2, [n(67), n(70, True)]),
        (6, 2, [n(61, True), n(67)]),
    ])
    return [a, b, chords]


def _s07(study):
    a, b, chords = bass(study, "a"), bass(study, "b"), shells(study)
    place_grid(a, [
        [n(33), n(37), n(40), n(42)],
        [n(38), n(42), n(45), n(44)],
        [n(35), n(38), n(40), n(42)],
        [n(40), n(44), n(47), n(45)],
    ])
    for index, row in enumerate(([n(33), n(40)], [n(33), n(42)], [n(33), n(37)], [n(28), n(33)])):
        for beat, (pitch, departure) in enumerate(row):
            a.add(bar(4 + index) + beat * PPQ * 2, PPQ * 2, pitch, 86 if beat == 0 else 72, departure=departure)
    place_grid(b, [
        [n(45), n(42), n(40), n(37)],
        [n(50), n(47), n(45), n(42)],
        [n(47), n(45), n(42), n(40)],
        [n(40), n(44), n(47), n(50)],
        [n(45), n(49), n(52), n(54)],
        [n(50), n(52), n(49), n(47)],
        [n(52), n(49), n(47), n(45)],
        [n(40), n(37), n(35), n(43, True)],
    ])
    add_shells(chords, [
        (0, 1, [n(61), n(68)]),
        (1, 1, [n(66), n(73)]),
        (2, 1, [n(62), n(69)]),
        (3, 1, [n(68), n(74)]),
        (4, 4, [n(61), n(68)]),
    ])
    return [a, b, chords]


def _s08(study):
    a, b, chords = bass(study, "a"), bass(study, "b"), shells(study)
    rows = [
        [n(36), n(39), n(41), n(43)],
        [n(41), n(39), n(36), n(34)],
        [n(41), n(44), n(46), n(48)],
        [n(46), n(44), n(41), n(39)],
        [n(43), n(47, True), n(46), n(43)],
        [n(41), n(43), n(46), n(48)],
        [n(48), n(46), n(44), n(43)],
        [n(41), n(39), n(36), n(34)],
        [n(44), n(48), n(51), n(53)],
        [n(51), n(48), n(46), n(44)],
        [n(46), n(50), n(53), n(51)],
        [n(48), n(46), n(43), n(41)],
        [n(43), n(46), n(48), n(50)],
        [n(46), n(43), n(41), n(39)],
        [n(43), n(47, True), n(46), n(43)],
        [n(41), n(39), n(36), n(43)],
    ]
    place_grid(a, rows, drop={(3, 0), (7, 0), (11, 0)})
    thirds = [n(39), n(39), n(44), n(44), n(47, True), n(47, True), n(39), n(39), n(48), n(48), n(50), n(50), n(46), n(46), n(47, True), n(47, True)]
    rows_b = []
    for row, lead in zip(rows, thirds):
        rows_b.append([lead, *row[1:]])
    place_grid(b, rows_b)
    add_shells(chords, [
        (0, 2, [n(63), n(70)]),
        (2, 2, [n(68), n(75)]),
        (4, 2, [n(59, True), n(65)]),
        (6, 2, [n(63), n(67)]),
        (8, 2, [n(60), n(67)]),
        (10, 2, [n(62), n(68)]),
        (12, 2, [n(58), n(62)]),
        (14, 2, [n(59, True), n(62)]),
    ])
    return [a, b, chords]


BUILDERS = {f"s0{i}": fn for i, fn in enumerate([_s01, _s02, _s03, _s04, _s05, _s06, _s07, _s08], 1)}


def _sig(notes):
    return tuple((note["performed_start"], note["pitch"], note["duration"]) for note in notes)


def assert_collections(catalog_studies, parts):
    allowed = {study["id"]: set(study["pitch_classes"]) for study in catalog_studies}
    for part in parts:
        pool = allowed[part["study_id"]]
        for note in part["notes"]:
            inside = (note["pitch"] % 12) in pool
            if note["departure"] and inside:
                raise ValueError(f"{part['id']} departure {note['pitch']} is inside the collection")
            if not note["departure"] and not inside:
                raise ValueError(f"{part['id']} note {note['pitch']} left the collection")


def assert_identities(parts):
    walks = [part for part in parts if part["role"] == "walking-bass"]
    by = {}
    for part in walks:
        by.setdefault(part["study_id"], {})[part["variation"]] = part
    rhythms = {}
    report = []
    for study_id, vars_ in by.items():
        if _sig(vars_["a"]["notes"]) == _sig(vars_["b"]["notes"]):
            raise ValueError(f"{study_id} variations match")
        rhythm = tuple(note["performed_start"] for note in vars_["a"]["notes"])
        if rhythm in rhythms:
            raise ValueError(f"{study_id} rhythm repeats {rhythms[rhythm]}")
        rhythms[rhythm] = study_id
        report.append({"study_id": study_id, "a": len(vars_["a"]["notes"]), "b": len(vars_["b"]["notes"])})
    return {"studies": report, "method": "bass variations differ; variation A attack times are not shared"}


def compose():
    catalog_studies = studies()
    parts = []
    for study in catalog_studies:
        for part in BUILDERS[study["id"]](study):
            parts.append(part.finish())
    assert_collections(catalog_studies, parts)
    identity = assert_identities(parts)
    core = [part for part in parts if part["core"]]
    refs = [part for part in parts if not part["core"]]
    if len(core) != 16 or len(refs) != 8:
        raise ValueError((len(core), len(refs)))
    arrangement = {
        "id": "arrangement-preview-s01a",
        "path": "midi/arrangement.mid",
        "format": 1,
        "container_ticks": 8 * BAR,
        "bpm": 108,
        "tempo_us": bpm_to_us(108),
        "meter": "4/4",
        "description": "Study 01 variation A walking bass with its chord reference. The shells are not inside the bass file.",
        "tracks": [
            {"name": "Conductor", "source_part": None, "channel": None},
            {"name": "Walking Bass", "source_part": "s01.walk.a", "channel": 0},
            {"name": "Chord Reference", "source_part": "s01.chords", "channel": 1},
        ],
    }
    catalog = {
        "pack_id": PACK_ID, "pack_name": PACK_NAME,
        "catalog_version": GENERATOR_VERSION, "generator_version": GENERATOR_VERSION,
        "ppq": PPQ, "meter": {"numerator": 4, "denominator": 4, "bar_ticks": BAR},
        "pitched_range": [28, 76], "c4": 60,
        "note_policy": "note-only MIDI. Swing, pedal, and upright-bass technique are not encoded.",
        "microtiming": "offset is 0; performed_start = nominal_start",
        "stochastic_draws": 0,
        "seed_meaning": "Seeds identify studies. Nothing is random.",
        "core_part_count": len(core), "reference_part_count": len(refs),
        "range_statement": "Walking bass is monophonic, MIDI 28 to 55 (E1 to G3), standard four-string tuning EADG. Chord references are separate shells from MIDI 48 to 76 and are not part of the core count.",
        "studies": [{key: study[key] for key in (
            "id", "slug", "title", "bpm", "tempo_us", "effective_bpm", "bars", "meter", "bar_ticks",
            "tonic", "tonal_reference", "collection_name", "pitch_classes", "departures", "seed",
            "harmonic_rhythm", "changes", "change_bars", "identity", "limitations", "voicing", "stochastic_draws",
        )} for study in catalog_studies],
        "parts": [{
            "id": part["id"], "study_id": part["study_id"], "role": part["role"], "variation": part["variation"],
            "core": part["core"], "channel": part["channel"], "path": part["path"], "notes": len(part["notes"]),
            "container_bars": part["container_bars"], "bpm": part["bpm"], "monophonic": part["monophonic"],
        } for part in parts],
        "arrangement": arrangement,
        "preview_part_ids": ["s01.walk.a", "s01.chords"],
        "stack_warning": "Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.",
    }
    score = {
        "pack_id": PACK_ID, "generator_version": GENERATOR_VERSION, "ppq": PPQ,
        "parts": parts, "arrangement": arrangement, "identity_check": identity,
    }
    return {"catalog": catalog, "score": score}
