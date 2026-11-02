"""Catalog page. The walk is measured from the MIDI files."""

from __future__ import annotations

import json
from pathlib import Path

from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING


def write_page(path: Path, catalog: dict, report: dict, preview: dict, film: dict) -> None:
    path.write_text(render_page(catalog, report, preview, film), encoding="utf-8")
    path.with_name("media.html").write_text(_media_html(), encoding="utf-8")


def render_page(catalog: dict, report: dict, preview: dict, film: dict) -> str:
    rows = []
    for part in catalog["parts"]:
        kind = "core" if part["core"] else "chord reference"
        rows.append(
            "<tr>"
            f"<td><a href=\"{part['path']}\">{part['id']}</a></td>"
            f"<td>{part['role']}</td>"
            f"<td>{part['variation']}</td>"
            f"<td>{kind}</td>"
            f"<td>{part['bpm']}</td>"
            f"<td>{part['notes']}</td>"
            "</tr>"
        )
    spell = {
        "s01": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
        "s02": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
        "s03": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
        "s04": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
        "s05": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
        "s06": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
        "s07": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
        "s08": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
    }
    payload = {
        "studies": [
            {
                "id": study["id"],
                "spell": spell[study["id"]],
                "title": study["title"],
                "bpm": study["bpm"],
                "bars": study["bars"],
                "collection": study["collection_name"],
                "tonic": study["tonal_reference"],
                "identity": study["identity"],
                "limitations": study["limitations"],
                "voicing": study["voicing"],
                "departures": study["departures"],
                "harmonic_rhythm": study["harmonic_rhythm"],
                "changes": study["changes"],
                "change_bars": study["change_bars"],
                "tempo_us": study["tempo_us"],
            }
            for study in catalog["studies"]
        ],
        "parts": [
            {
                "id": part["id"],
                "study_id": part["study_id"],
                "role": part["role"],
                "variation": part["variation"],
                "path": part["path"],
            }
            for part in catalog["parts"]
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    seconds = f"{preview['seconds_encoded']:.2f}"
    film_seconds = f"{film['duration_seconds']:.2f}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jazz Walking Basslines</title>
  <style>
    :root {{
      --ink: #16120e;
      --ivory: #f3efe4;
      --brass: #b08d57;
      --ox: #7a2e2a;
      --muted: #b7ab9a;
      --line: rgba(243, 239, 228, .16);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--ink);
      color: var(--ivory);
      font-family: Georgia, "Iowan Old Style", Palatino, serif;
      line-height: 1.45;
      padding-bottom: 84px;
    }}
    a {{ color: var(--brass); }}
    button, .transport, .meta, .sign, .step, .shell {{ font-family: ui-monospace, Menlo, Consolas, monospace; }}
    .top {{
      position: sticky; top: 0; z-index: 5;
      display: flex; justify-content: space-between; gap: 16px; align-items: center;
      padding: 12px 22px;
      background: rgba(22, 18, 14, .92);
      border-bottom: 1px solid var(--line);
    }}
    .brand {{ letter-spacing: .14em; text-transform: uppercase; font-size: .72rem; }}
    .top nav {{ display: flex; gap: 14px; font-size: .78rem; }}
    main {{ width: min(1180px, calc(100% - 2rem)); margin: 0 auto; }}
    .stage {{
      display: grid;
      grid-template-columns: minmax(0, .78fr) minmax(0, 1.22fr);
      gap: 28px;
      align-items: start;
      padding: 28px 0 8px;
    }}
    .stage > div {{ min-width: 0; }}
    h1 {{ font-weight: 500; font-size: clamp(2.6rem, 6vw, 5rem); line-height: .9; margin: 8px 0 12px; }}
    .kicker {{ letter-spacing: .16em; text-transform: uppercase; color: var(--brass); font-size: .75rem; margin: 0; }}
    .lede {{ font-size: 1.12rem; }}
    .meta, .note {{ color: var(--muted); font-size: .84rem; }}
    .hero {{ margin: 0 0 18px; }}
    .hero img {{ display: block; width: 100%; height: auto; }}
    .rail {{ display: flex; gap: 8px; overflow-x: auto; max-width: 100%; padding: 4px 0 12px; }}
    .rail button, .switch button, .transport button {{
      border: 1px solid var(--line);
      background: transparent;
      color: var(--ivory);
      border-radius: 999px;
      padding: 8px 12px;
      cursor: pointer;
    }}
    .rail button[aria-pressed="true"], .switch button[aria-pressed="true"], .transport button[aria-pressed="true"] {{
      background: var(--brass);
      color: var(--ink);
      border-color: var(--brass);
    }}
    .switch {{ display: flex; gap: 8px; align-items: center; margin: 0 0 10px; }}
    .scroller {{ overflow-x: auto; max-width: 100%; background: var(--ivory); color: var(--ink); border-radius: 18px; }}
    .signs {{ position: relative; height: 36px; }}
    .sign {{
      position: absolute; top: 8px; height: 22px;
      border-left: 2px solid var(--ox);
      padding-left: 6px;
      font-size: 11px;
      letter-spacing: .04em;
      white-space: nowrap;
      overflow: hidden;
    }}
    .lane {{ position: relative; height: 230px; }}
    .step {{
      position: absolute; width: 34px; height: 22px; margin-left: -17px;
      border: 0; border-radius: 999px;
      background: var(--brass); color: var(--ink);
      font-size: 10px; cursor: default;
    }}
    .step.change {{ background: var(--ox); color: var(--ivory); }}
    .step.now {{ outline: 2px solid var(--ink); }}
    .shells {{ position: relative; height: 28px; display: none; }}
    .shells.on {{ display: block; }}
    .shell {{
      position: absolute; top: 2px;
      font-size: 10px; color: var(--ox);
    }}
    .path {{ position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }}
    .status {{ min-height: 1.2em; }}
    .table-scroll {{ overflow-x: auto; max-width: 100%; }}
    .files {{ width: 100%; border-collapse: collapse; font-size: .82rem; }}
    .files th, .files td {{ text-align: left; padding: 8px 6px; border-bottom: 1px solid var(--line); }}
    .flow {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-size: .82rem; }}
    .flow span {{ border: 1px solid var(--line); border-radius: 999px; padding: 4px 8px; }}
    audio, video {{ display: block; width: 100%; height: auto; margin: 10px 0 16px; background: #000; }}
    .transport {{
      position: fixed; left: 0; right: 0; bottom: 0; z-index: 6;
      display: flex; gap: 10px; align-items: center; flex-wrap: wrap;
      padding: 10px 16px;
      background: #0e0c0a;
      border-top: 1px solid var(--line);
    }}
    @media (max-width: 860px) {{
      .stage {{ grid-template-columns: 1fr; }}
      .top nav {{ display: none; }}
      h1 {{ font-size: 2.7rem; }}
    }}
  </style>
</head>
<body>
  <header class="top">
    <a class="brand" href="index.html">Jazz Walking Basslines</a>
    <nav>
      <a href="#walk">Walk</a>
      <a href="#files">Files</a>
      <a href="#reading">Recorded reading</a>
      <a href="media.html">Stills</a>
      <a href="midi/arrangement.mid">Arrangement</a>
    </nav>
  </header>
  <main>
    <section class="stage">
      <div>
        <p class="kicker">Eight studies · quarter notes over explicit changes</p>
        <h1 id="title">Stroll</h1>
        <p class="lede" id="identity"></p>
        <p class="meta" id="facts"></p>
        <p id="rhythm"></p>
        <p id="voicing"></p>
        <p class="note" id="limits"></p>
        <p class="note" id="departures"></p>
      </div>
      <div id="walk">
        <figure class="hero">
          <img src="art/hero.jpg" width="1280" height="720" alt="Illustration of a walking path of steps across an ivory lane. Not a photograph of a studio or of performers.">
        </figure>
        <div class="rail" id="rail" role="tablist" aria-label="Studies"></div>
        <div class="switch" role="group" aria-label="Variation">
          <button type="button" id="var-a" aria-pressed="true">Variation A</button>
          <button type="button" id="var-b" aria-pressed="false">Variation B</button>
        </div>
        <div class="scroller" id="scroller">
          <div class="signs" id="signs"></div>
          <div class="lane" id="lane">
            <svg class="path" id="path" aria-hidden="true"></svg>
            <div id="steps"></div>
          </div>
          <div class="shells" id="shells"></div>
        </div>
        <p class="status" id="status" role="status">Reading the MIDI.</p>
      </div>
    </section>
    <p>{catalog['range_statement']}</p>
    <div class="flow" aria-label="File contract">
      <span>Canonical score</span><span>MIDI bytes</span><span>Reopened validation</span><span>MP3 preview</span><span>Film and captions</span>
    </div>
    <p class="note">Stills lead to the social drafts. The catalog leads to this page. <a href="articles/medium-draft-Cursor.md">Article draft</a> · <a href="articles/medium-paste-Cursor.txt">plain text</a></p>
    <p>{WARNING}</p>
    <h2 id="files">Files</h2>
    <p class="meta">Validation {report['result']}. Core {catalog['core_part_count']}. Chord references {catalog['reference_part_count']}. <a href="midi/validation-Cursor.json">validation report</a> · <a href="catalog/catalog-Cursor.json">catalog</a></p>
    <div class="table-scroll">
    <table class="files">
      <thead><tr><th>Part</th><th>Role</th><th>Var</th><th>Count</th><th>BPM</th><th>Notes</th></tr></thead>
      <tbody>
        {''.join(rows)}
      </tbody>
    </table>
    </div>
    <section id="reading">
      <p class="kicker">Recorded reading · study 01 variation A only</p>
      <p>This MP3 is {seconds} seconds. {PREVIEW_LINE}. The film is {film_seconds} seconds and shows {ON_PICTURE}.</p>
      <audio controls preload="metadata" src="preview/preview.mp3"></audio>
      <p><a href="preview/preview.mp3">preview/preview.mp3</a></p>
      <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
        <source src="film/preview.mp4" type="video/mp4">
        <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
      </video>
      <p><a href="film/preview.mp4">film/preview.mp4</a> · <a href="film/preview.vtt">film/preview.vtt</a></p>
    </section>
    <p>{PROGRAM}</p>
    <p>{AUDITION}</p>
    <p>{PUBLICATION}</p>
  </main>
  <div class="transport">
    <button type="button" id="play">Play walk</button>
    <button type="button" id="shell-toggle" aria-pressed="false">Chord pitches</button>
    <span id="transport-label">Space plays. J and K change study.</span>
  </div>
  <script id="pack" type="application/json">{data}</script>
  <script>
    const pack = JSON.parse(document.getElementById("pack").textContent);
    const NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"];
    const rail = document.getElementById("rail");
    const signs = document.getElementById("signs");
    const lane = document.getElementById("lane");
    const steps = document.getElementById("steps");
    const shells = document.getElementById("shells");
    const path = document.getElementById("path");
    const status = document.getElementById("status");
    let studyId = "s01";
    let variation = "a";
    let walkNotes = [];
    let shellNotes = [];
    let showShells = false;
    let audio = null;
    let playing = false;
    let followId = 0;

    function pitchName(pitch) {{
      return study().spell[pitch % 12] + (Math.floor(pitch / 12) - 1);
    }}

    function readVlq(view, offset) {{
      let value = 0;
      let byte = 0;
      do {{
        byte = view.getUint8(offset);
        offset += 1;
        value = (value << 7) | (byte & 0x7f);
      }} while (byte & 0x80);
      return [value, offset];
    }}

    function parseMidi(buffer) {{
      const view = new DataView(buffer);
      const head = String.fromCharCode(view.getUint8(0), view.getUint8(1), view.getUint8(2), view.getUint8(3));
      if (head !== "MThd" || view.getUint16(12) !== 960) throw new Error("unexpected MIDI header");
      const tracks = view.getUint16(10);
      let offset = 14;
      const notes = [];
      for (let track = 0; track < tracks; track += 1) {{
        const mark = String.fromCharCode(view.getUint8(offset), view.getUint8(offset + 1), view.getUint8(offset + 2), view.getUint8(offset + 3));
        if (mark !== "MTrk") throw new Error("missing track");
        const length = view.getUint32(offset + 4);
        offset += 8;
        const end = offset + length;
        let tick = 0;
        let running = 0;
        const open = new Map();
        while (offset < end) {{
          let delta;
          [delta, offset] = readVlq(view, offset);
          tick += delta;
          let byte = view.getUint8(offset);
          if (byte < 0x80) {{
            if (!running) throw new Error("running status");
          }} else {{
            running = byte;
            offset += 1;
          }}
          if (running === 0xff) {{
            offset += 1;
            let metaLen;
            [metaLen, offset] = readVlq(view, offset);
            offset += metaLen;
            continue;
          }}
          if (running === 0xf0 || running === 0xf7) {{
            let sysLen;
            [sysLen, offset] = readVlq(view, offset);
            offset += sysLen;
            continue;
          }}
          const kind = running & 0xf0;
          const channel = running & 0x0f;
          const data1 = byte < 0x80 ? byte : view.getUint8(offset);
          if (byte >= 0x80) offset += 1;
          let data2 = 0;
          if (kind !== 0xc0 && kind !== 0xd0) {{
            data2 = view.getUint8(offset);
            offset += 1;
          }}
          const key = channel + ":" + data1;
          if (kind === 0x90 && data2 > 0) open.set(key, tick);
          else if (kind === 0x80 || (kind === 0x90 && data2 === 0)) {{
            const start = open.get(key);
            if (start !== undefined) {{
              notes.push({{ pitch: data1, start: start, duration: tick - start, channel: channel }});
              open.delete(key);
            }}
          }}
        }}
      }}
      notes.sort((a, b) => a.start - b.start || a.pitch - b.pitch);
      return notes;
    }}

    function partPath(role) {{
      const found = pack.parts.find((part) => part.study_id === studyId && part.role === role && (role === "chord-reference" || part.variation === variation));
      if (!found) throw new Error("missing " + role);
      return found.path;
    }}

    function study() {{
      return pack.studies.find((item) => item.id === studyId);
    }}

    function renderCopy() {{
      const item = study();
      document.getElementById("title").textContent = item.title;
      document.getElementById("identity").textContent = item.identity;
      document.getElementById("facts").textContent = item.id + " · " + item.bpm + " BPM · " + item.bars + " bars · " + item.collection + " · tonic " + item.tonic;
      document.getElementById("rhythm").textContent = item.harmonic_rhythm;
      document.getElementById("voicing").textContent = item.voicing;
      document.getElementById("limits").textContent = item.limitations;
      document.getElementById("departures").textContent = item.departures.length ? item.departures.join(" ") : "No pitch in this study is flagged as a departure.";
      document.getElementById("transport-label").textContent = item.title + " " + variation.toUpperCase() + " · Space plays · J and K change study";
      for (const button of rail.querySelectorAll("button")) {{
        button.setAttribute("aria-pressed", button.dataset.id === studyId ? "true" : "false");
      }}
      document.getElementById("var-a").setAttribute("aria-pressed", variation === "a" ? "true" : "false");
      document.getElementById("var-b").setAttribute("aria-pressed", variation === "b" ? "true" : "false");
    }}

    function changeTicks(item) {{
      const ticks = new Set();
      let bar = 0;
      item.change_bars.forEach((span) => {{
        ticks.add(bar * 4 * 960);
        bar += span;
      }});
      return ticks;
    }}

    function draw() {{
      const item = study();
      const container = item.bars * 4 * 960;
      const width = Math.max(640, item.bars * 156);
      signs.style.width = width + "px";
      lane.style.width = width + "px";
      shells.style.width = width + "px";
      signs.innerHTML = "";
      steps.innerHTML = "";
      shells.innerHTML = "";
      path.innerHTML = "";
      let bar = 0;
      item.changes.forEach((name, index) => {{
        const span = item.change_bars[index];
        const sign = document.createElement("div");
        sign.className = "sign";
        sign.textContent = name;
        sign.style.left = (bar / item.bars) * width + "px";
        sign.style.width = (span / item.bars) * width + "px";
        signs.appendChild(sign);
        bar += span;
      }});
      if (!walkNotes.length) {{
        status.textContent = "This variation has no bass notes.";
        return;
      }}
      const low = Math.min(...walkNotes.map((note) => note.pitch));
      const high = Math.max(...walkNotes.map((note) => note.pitch));
      const span = Math.max(1, high - low);
      const changes = changeTicks(item);
      const points = [];
      walkNotes.forEach((note) => {{
        const step = document.createElement("div");
        step.className = "step" + (changes.has(note.start) ? " change" : "");
        step.textContent = pitchName(note.pitch);
        step.dataset.start = String(note.start);
        step.dataset.end = String(note.start + note.duration);
        const x = (note.start / container) * width;
        const y = 16 + (1 - (note.pitch - low) / span) * 180;
        step.style.left = x + "px";
        step.style.top = y + "px";
        steps.appendChild(step);
        points.push([x, y + 11]);
      }});
      path.setAttribute("viewBox", "0 0 " + width + " 230");
      path.setAttribute("width", String(width));
      path.setAttribute("height", "230");
      for (let index = 0; index < points.length - 1; index += 1) {{
        const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line.setAttribute("x1", String(points[index][0]));
        line.setAttribute("y1", String(points[index][1]));
        line.setAttribute("x2", String(points[index + 1][0]));
        line.setAttribute("y2", String(points[index + 1][1]));
        line.setAttribute("stroke", "#7a5a32");
        line.setAttribute("stroke-width", "1.2");
        path.appendChild(line);
      }}
      shells.classList.toggle("on", showShells);
      if (showShells) {{
        shellNotes.forEach((note) => {{
          const mark = document.createElement("div");
          mark.className = "shell";
          mark.textContent = pitchName(note.pitch);
          mark.style.left = (note.start / container) * width + "px";
          shells.appendChild(mark);
        }});
      }}
    }}

    async function loadStudy() {{
      stopPlayback();
      renderCopy();
      status.textContent = "Reading the MIDI.";
      try {{
        const walkRes = await fetch(partPath("walking-bass"));
        const shellRes = await fetch(partPath("chord-reference"));
        if (!walkRes.ok || !shellRes.ok) throw new Error("MIDI request failed");
        walkNotes = parseMidi(await walkRes.arrayBuffer());
        shellNotes = parseMidi(await shellRes.arrayBuffer());
        status.textContent = walkNotes.length + " bass notes. Chord names stay above the walk.";
        draw();
      }} catch (error) {{
        walkNotes = [];
        shellNotes = [];
        status.textContent = "The MIDI did not load. " + error.message;
      }}
    }}

    function freq(pitch) {{
      return 440 * Math.pow(2, (pitch - 69) / 12);
    }}

    function schedule(ctx, pitch, when, duration, amount, type) {{
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.value = freq(pitch);
      const attack = Math.min(0.012, duration * 0.2);
      const end = when + duration;
      gain.gain.setValueAtTime(0.0001, when);
      gain.gain.exponentialRampToValueAtTime(amount, when + attack);
      gain.gain.exponentialRampToValueAtTime(0.0001, Math.max(end, when + attack + 0.01));
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(when);
      osc.stop(end + 0.02);
    }}

    function stopPlayback() {{
      playing = false;
      cancelAnimationFrame(followId);
      if (audio) {{
        audio.close();
        audio = null;
      }}
      document.getElementById("play").textContent = "Play walk";
      document.querySelectorAll(".step.now").forEach((step) => step.classList.remove("now"));
    }}

    function playWalk() {{
      if (!walkNotes.length) return;
      stopPlayback();
      const ctx = new AudioContext();
      audio = ctx;
      playing = true;
      document.getElementById("play").textContent = "Stop";
      const item = study();
      const seconds = (tick) => tick / 960 * item.tempo_us / 1000000;
      const origin = ctx.currentTime + 0.05;
      for (const note of walkNotes) {{
        schedule(ctx, note.pitch, origin + seconds(note.start), Math.max(0.05, seconds(note.duration)), 0.16, "sine");
      }}
      if (showShells) {{
        for (const note of shellNotes) {{
          schedule(ctx, note.pitch, origin + seconds(note.start), Math.max(0.05, seconds(note.duration)), 0.03, "triangle");
        }}
      }}
      const container = seconds(item.bars * 4 * 960);
      const follow = () => {{
        if (!playing || !audio) return;
        const tick = (audio.currentTime - origin) * 1000000 / item.tempo_us * 960;
        document.querySelectorAll(".step").forEach((step) => {{
          const start = Number(step.dataset.start);
          const end = Number(step.dataset.end);
          step.classList.toggle("now", tick >= start && tick < end);
        }});
        if (audio.currentTime - origin < container) followId = requestAnimationFrame(follow);
        else stopPlayback();
      }};
      follow();
    }}

    function togglePlay() {{
      if (playing) stopPlayback();
      else playWalk();
    }}

    function stepStudy(direction) {{
      const index = pack.studies.findIndex((item) => item.id === studyId);
      studyId = pack.studies[(index + direction + pack.studies.length) % pack.studies.length].id;
      loadStudy();
    }}

    pack.studies.forEach((item) => {{
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.id = item.id;
      button.textContent = item.id.slice(1) + " " + item.title;
      button.addEventListener("click", () => {{
        studyId = item.id;
        loadStudy();
      }});
      rail.appendChild(button);
    }});
    document.getElementById("var-a").addEventListener("click", () => {{ variation = "a"; loadStudy(); }});
    document.getElementById("var-b").addEventListener("click", () => {{ variation = "b"; loadStudy(); }});
    document.getElementById("play").addEventListener("click", togglePlay);
    document.getElementById("shell-toggle").addEventListener("click", () => {{
      showShells = !showShells;
      document.getElementById("shell-toggle").setAttribute("aria-pressed", showShells ? "true" : "false");
      if (walkNotes.length) draw();
    }});
    window.addEventListener("keydown", (event) => {{
      const tag = document.activeElement && document.activeElement.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (event.code === "Space") {{
        event.preventDefault();
        togglePlay();
      }} else if (event.key === "j" || event.key === "J") stepStudy(-1);
      else if (event.key === "k" || event.key === "K") stepStudy(1);
    }});
    loadStudy();
  </script>
</body>
</html>
"""


def _media_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Jazz Walking Basslines, stills</title>
  <style>
    :root { --ink:#16120e; --ivory:#f3efe4; --muted:#b7ab9a; --line:rgba(243,239,228,.16); --brass:#b08d57; }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--ink); color: var(--ivory); font-family: Georgia, "Iowan Old Style", serif; line-height: 1.45; }
    a { color: var(--brass); }
    header, main { width: min(1120px, calc(100% - 2rem)); margin: 0 auto; }
    header { padding: 28px 0 8px; }
    h1 { font-weight: 500; font-size: clamp(2.2rem, 5vw, 4rem); line-height: 0.95; margin: 8px 0; }
    .kicker { font-family: ui-monospace, Menlo, Consolas, monospace; letter-spacing: .14em; text-transform: uppercase; color: var(--brass); font-size: .75rem; }
    .hero, .shot, .play { margin: 0 0 28px; }
    img, video, audio { display: block; width: 100%; height: auto; background: #000; }
    figcaption { color: var(--muted); font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .82rem; padding: 8px 0 0; }
    .gallery { display: grid; grid-template-columns: 1.1fr .7fr; gap: 18px; align-items: start; margin-bottom: 28px; }
    .play { border-top: 1px solid var(--line); padding-top: 22px; }
    @media (max-width: 800px) { .gallery { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <p class="kicker"><a href="index.html">Jazz Walking Basslines</a></p>
    <h1>Stills, then the recording.</h1>
    <p>Each frame keeps its own shape. The film and the MP3 sit under the pictures.</p>
  </header>
  <main>
    <figure class="hero">
      <img src="art/hero.jpg" width="1280" height="720" alt="Illustration of a walking path of steps across an ivory lane. Not a photograph of a studio or of performers.">
      <figcaption>art/hero.jpg · 1280 by 720</figcaption>
    </figure>
    <div class="gallery">
      <figure class="shot">
        <img src="art/square.jpg" width="1080" height="1080" alt="Square illustration of the walking path.">
        <figcaption>art/square.jpg · 1080 by 1080</figcaption>
      </figure>
      <figure class="shot">
        <img src="social/instagram-Cursor/portrait.jpg" width="1080" height="1350" alt="Vertical crop of the walking-path illustration.">
        <figcaption>portrait · 1080 by 1350</figcaption>
      </figure>
    </div>
    <div class="gallery">
      <figure class="shot">
        <img src="social/x-Cursor/card.jpg" width="1600" height="900" alt="Wide card of the walking-path illustration.">
        <figcaption>x card · 1600 by 900</figcaption>
      </figure>
      <figure class="shot">
        <img src="film/poster.jpg" width="1280" height="720" alt="Film poster with the words preview, not master.">
        <figcaption>film/poster.jpg · disclosure on the picture</figcaption>
      </figure>
    </div>
    <section class="play">
      <p class="kicker">Recorded reading · study 01 only</p>
      <audio controls preload="metadata" src="preview/preview.mp3"></audio>
      <p><a href="preview/preview.mp3">preview/preview.mp3</a></p>
      <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
        <source src="film/preview.mp4" type="video/mp4">
        <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
      </video>
    </section>
  </main>
</body>
</html>
"""
