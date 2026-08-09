"""Offline human-narration recording and import helpers."""

from __future__ import annotations

import base64
import html
import json
import math
import re
import shutil
import subprocess
import tempfile
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from .config import ConfigError, load_project, sha256_file
from .media import probe_audio_duration


@dataclass(frozen=True, slots=True)
class NarrationCue:
    identifier: str
    text: str
    target_duration: float


@dataclass(frozen=True, slots=True)
class NarrationScript:
    title: str
    source: Path
    sha256: str
    rate: float
    target_loudness_lufs: float
    cues: tuple[NarrationCue, ...]


_RECORDER_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>__PAGE_TITLE__</title>
  <style>
    :root {
      --paper: #f4f5f1;
      --surface: #ffffff;
      --ink: #202523;
      --muted: #66706b;
      --line: #d8ddd9;
      --accent: #176e63;
      --accent-soft: #e1f0ed;
      --record: #b33a3a;
      --record-soft: #f6e6e4;
      --focus: #174f86;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
      letter-spacing: 0;
    }
    * { box-sizing: border-box; }
    html, body { width: 100%; max-width: 100%; overflow-x: hidden; }
    body {
      margin: 0;
      min-height: 100vh;
      color: var(--ink);
      background: var(--paper);
      font-size: 16px;
      line-height: 1.45;
      letter-spacing: 0;
    }
    button, select { font: inherit; letter-spacing: 0; }
    button:focus-visible, select:focus-visible {
      outline: 3px solid color-mix(in srgb, var(--focus) 35%, transparent);
      outline-offset: 2px;
    }
    header {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 18px;
      align-items: end;
      padding: 22px 28px 18px;
      background: var(--surface);
      border-bottom: 1px solid var(--line);
    }
    h1 {
      min-width: 0;
      margin: 0;
      overflow-wrap: anywhere;
      font-size: 22px;
      line-height: 1.2;
      font-weight: 680;
    }
    .privacy { color: var(--accent); font-size: 13px; font-weight: 650; }
    .progress-row {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: auto minmax(120px, 1fr) auto;
      align-items: center;
      gap: 12px;
      color: var(--muted);
      font-size: 13px;
    }
    progress { width: 100%; height: 7px; accent-color: var(--accent); }
    .workspace {
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr);
      min-width: 0;
      max-width: 100%;
      min-height: calc(100vh - 112px);
    }
    nav {
      border-right: 1px solid var(--line);
      background: #eef0ec;
      overflow: auto;
      max-height: calc(100vh - 112px);
      padding: 12px;
    }
    .cue-nav {
      width: 100%;
      display: grid;
      grid-template-columns: 30px minmax(0, 1fr) 10px;
      gap: 8px;
      align-items: center;
      border: 0;
      border-bottom: 1px solid var(--line);
      background: transparent;
      color: var(--ink);
      padding: 10px 8px;
      text-align: left;
      cursor: pointer;
    }
    .cue-nav:hover { background: rgba(255, 255, 255, 0.62); }
    .cue-nav[aria-current="true"] { background: var(--surface); }
    .cue-number { color: var(--muted); font-variant-numeric: tabular-nums; }
    .cue-preview { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .cue-dot { width: 8px; height: 8px; border-radius: 50%; background: #aeb5b1; }
    .cue-nav.recorded .cue-dot { background: var(--accent); }
    main {
      display: grid;
      grid-template-rows: minmax(360px, 1fr) auto;
      min-width: 0;
      padding: 38px clamp(28px, 6vw, 84px) 28px;
    }
    .cue-stage { max-width: 940px; width: 100%; margin: 0 auto; align-self: center; }
    .eyebrow {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      color: var(--muted);
      font-size: 13px;
      font-weight: 650;
      text-transform: uppercase;
    }
    .cue-content {
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
      gap: 34px;
      align-items: center;
      margin-top: 22px;
    }
    .reference-frame { min-width: 0; margin: 0; }
    .reference-frame img {
      display: block;
      width: 100%;
      aspect-ratio: 16 / 9;
      object-fit: contain;
      background: #e8ebe7;
      border: 1px solid var(--line);
    }
    .reference-frame figcaption {
      margin-top: 7px;
      color: var(--muted);
      font-size: 12px;
    }
    .script-column { min-width: 0; }
    .script {
      margin: 0 0 18px;
      max-width: 32em;
      font-family: Georgia, "Times New Roman", serif;
      font-size: 29px;
      line-height: 1.35;
      letter-spacing: 0;
    }
    .timing { color: var(--muted); font-size: 14px; }
    .meter {
      height: 5px;
      max-width: 520px;
      margin-top: 24px;
      background: var(--line);
      overflow: hidden;
    }
    .meter-fill { width: 0; height: 100%; background: var(--record); transition: width 60ms linear; }
    .controls {
      border-top: 1px solid var(--line);
      padding-top: 22px;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 10px;
    }
    button {
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--surface);
      color: var(--ink);
      padding: 9px 15px;
      cursor: pointer;
    }
    button:hover:not(:disabled) { border-color: #9da6a1; }
    button:disabled { opacity: 0.45; cursor: not-allowed; }
    .primary { color: white; background: var(--accent); border-color: var(--accent); font-weight: 680; }
    .record { color: white; background: var(--record); border-color: var(--record); font-weight: 680; }
    .record.recording { color: var(--record); background: var(--record-soft); }
    .spacer { flex: 1 1 24px; }
    .status {
      flex-basis: 100%;
      min-height: 24px;
      color: var(--muted);
      font-size: 14px;
    }
    .status.error { color: var(--record); }
    audio { width: min(100%, 360px); height: 42px; }
    .footer-note { margin-top: 14px; color: var(--muted); font-size: 12px; }
    @media (max-width: 780px) {
      header { grid-template-columns: minmax(0, 1fr); padding: 18px; }
      .privacy { grid-column: 1; min-width: 0; overflow-wrap: anywhere; }
      .progress-row {
        grid-column: 1;
        min-width: 0;
        grid-template-columns: auto minmax(0, 1fr) auto;
      }
      .progress-row progress { min-width: 0; }
      .workspace { display: block; width: 100%; max-width: 100vw; overflow: hidden; }
      nav {
        width: 100%;
        max-width: 100vw;
        max-height: none;
        border-right: 0;
        border-bottom: 1px solid var(--line);
        display: flex;
        overflow-x: auto;
        padding: 8px;
      }
      .cue-nav { min-width: 72px; width: 72px; display: flex; justify-content: center; }
      .cue-preview { display: none; }
      main {
        width: 100%;
        min-height: calc(100vh - 190px);
        overflow: hidden;
        padding: 28px 20px 20px;
      }
      .script { max-width: 100%; overflow-wrap: anywhere; font-size: 27px; }
      .cue-content { display: block; margin-top: 18px; }
      .reference-frame { margin-bottom: 22px; }
      .controls { position: static; }
    }
  </style>
</head>
<body>
  <header>
    <h1 id="projectTitle"></h1>
    <div class="privacy">Recorded locally. Nothing is uploaded.</div>
    <div class="progress-row">
      <span id="progressLabel">0 recorded</span>
      <progress id="progress" value="0" max="1"></progress>
      <span id="cueCount"></span>
    </div>
  </header>
  <div class="workspace">
    <nav id="cueList" aria-label="Narration cues"></nav>
    <main>
      <section class="cue-stage" aria-live="polite">
        <div class="eyebrow">
          <span id="cuePosition"></span>
          <span id="recordingClock">Ready</span>
        </div>
        <div class="cue-content">
          <figure class="reference-frame" id="referenceFrame">
            <img id="referenceImage" alt="Reference frame for the current narration cue">
            <figcaption id="referenceCaption">Reference frame from the current video</figcaption>
          </figure>
          <div class="script-column">
            <p class="script" id="cueText"></p>
            <div class="timing" id="timingGuide"></div>
          </div>
        </div>
        <div class="meter" aria-label="Microphone level"><div class="meter-fill" id="meterFill"></div></div>
      </section>
      <section>
        <div class="controls">
          <button id="previousButton" type="button">Previous</button>
          <button id="recordButton" class="record" type="button">Record</button>
          <button id="playButton" type="button" disabled>Play</button>
          <button id="downloadButton" type="button" disabled>Download cue</button>
          <audio id="player" controls hidden></audio>
          <span class="spacer"></span>
          <button id="nextButton" type="button">Next</button>
          <button id="saveAllButton" class="primary" type="button" disabled>Save all recordings</button>
          <div id="status" class="status">Allow microphone access when you begin.</div>
        </div>
        <div class="footer-note">Space: record or stop. Left and right arrows: change cue. Recordings remain in this browser tab until saved.</div>
      </section>
    </main>
  </div>
  <script>
    "use strict";
    const SCRIPT = __SCRIPT_JSON__;
    const recordings = new Map();
    const initialCue = Number(new URLSearchParams(location.hash.slice(1)).get("cue"));
    let currentIndex = Number.isInteger(initialCue) && initialCue > 0
      ? Math.min(initialCue - 1, SCRIPT.cues.length - 1)
      : 0;
    let recorder = null;
    let stream = null;
    let chunks = [];
    let startedAt = 0;
    let timerHandle = null;
    let meterHandle = null;
    let audioContext = null;

    const elements = Object.fromEntries([
      "projectTitle", "progressLabel", "progress", "cueCount", "cueList",
      "cuePosition", "recordingClock", "referenceFrame", "referenceImage",
      "referenceCaption", "cueText", "timingGuide", "meterFill",
      "previousButton", "recordButton", "playButton", "downloadButton", "player",
      "nextButton", "saveAllButton", "status"
    ].map(id => [id, document.getElementById(id)]));

    const escapeFilename = value => value.replace(/[^A-Za-z0-9._-]+/g, "-");
    const preferredMime = () => {
      const candidates = [
        "audio/webm;codecs=opus", "audio/ogg;codecs=opus", "audio/mp4", "audio/webm"
      ];
      return candidates.find(type => window.MediaRecorder && MediaRecorder.isTypeSupported(type)) || "";
    };
    const extensionFor = type => type.includes("ogg") ? "ogg" : type.includes("mp4") ? "m4a" : "webm";
    const setStatus = (message, error = false) => {
      elements.status.textContent = message;
      elements.status.classList.toggle("error", error);
    };
    const currentCue = () => SCRIPT.cues[currentIndex];

    function renderCueList() {
      elements.cueList.replaceChildren();
      SCRIPT.cues.forEach((cue, index) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "cue-nav" + (recordings.has(cue.id) ? " recorded" : "");
        button.setAttribute("aria-current", index === currentIndex ? "true" : "false");
        button.innerHTML = `<span class="cue-number">${index + 1}</span><span class="cue-preview"></span><span class="cue-dot"></span>`;
        button.querySelector(".cue-preview").textContent = cue.text;
        button.addEventListener("click", () => selectCue(index));
        elements.cueList.append(button);
      });
      const selected = elements.cueList.children[currentIndex];
      if (selected) selected.scrollIntoView({block: "nearest", inline: "nearest"});
    }

    function updateProgress() {
      elements.progress.max = SCRIPT.cues.length;
      elements.progress.value = recordings.size;
      elements.progressLabel.textContent = `${recordings.size} recorded`;
      elements.cueCount.textContent = `${SCRIPT.cues.length} cues`;
      elements.saveAllButton.disabled = recordings.size === 0 || Boolean(recorder);
    }

    function renderCue() {
      const cue = currentCue();
      const clip = recordings.get(cue.id);
      elements.cuePosition.textContent = `Cue ${currentIndex + 1} of ${SCRIPT.cues.length}`;
      elements.cueText.textContent = cue.text;
      elements.referenceFrame.hidden = !cue.image;
      if (cue.image) {
        elements.referenceImage.src = cue.image;
        elements.referenceCaption.textContent = "Reference frame from the current video";
      } else {
        elements.referenceImage.removeAttribute("src");
      }
      const target = cue.target_duration > 0 ? `Target pace: about ${cue.target_duration.toFixed(1)} seconds` : "Read at a natural pace";
      elements.timingGuide.textContent = `${cue.word_count} words. ${target}.`;
      elements.previousButton.disabled = currentIndex === 0 || Boolean(recorder);
      elements.nextButton.disabled = currentIndex === SCRIPT.cues.length - 1 || Boolean(recorder);
      elements.playButton.disabled = !clip || Boolean(recorder);
      elements.downloadButton.disabled = !clip || Boolean(recorder);
      elements.recordButton.textContent = recorder ? "Stop" : clip ? "Retake" : "Record";
      elements.recordButton.classList.toggle("recording", Boolean(recorder));
      elements.recordingClock.textContent = clip && !recorder ? `Recorded ${clip.duration.toFixed(1)} s` : recorder ? "Recording" : "Ready";
      if (clip) {
        elements.player.src = clip.url;
      } else {
        elements.player.removeAttribute("src");
        elements.player.load();
      }
      renderCueList();
      updateProgress();
    }

    function selectCue(index) {
      if (recorder) return;
      currentIndex = Math.max(0, Math.min(index, SCRIPT.cues.length - 1));
      history.replaceState(null, "", `#cue=${currentIndex + 1}`);
      elements.player.pause();
      renderCue();
      setStatus(recordings.has(currentCue().id) ? "This cue is recorded. Play it or make another take." : "Ready to record.");
    }

    function stopMeter() {
      if (meterHandle) cancelAnimationFrame(meterHandle);
      meterHandle = null;
      elements.meterFill.style.width = "0";
      if (audioContext) audioContext.close().catch(() => {});
      audioContext = null;
    }

    function startMeter(activeStream) {
      audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      audioContext.createMediaStreamSource(activeStream).connect(analyser);
      const samples = new Uint8Array(analyser.fftSize);
      const draw = () => {
        analyser.getByteTimeDomainData(samples);
        let sum = 0;
        for (const value of samples) {
          const centered = (value - 128) / 128;
          sum += centered * centered;
        }
        const rms = Math.sqrt(sum / samples.length);
        elements.meterFill.style.width = `${Math.min(100, rms * 420)}%`;
        meterHandle = requestAnimationFrame(draw);
      };
      draw();
    }

    async function startRecording() {
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        setStatus("Microphone recording is unavailable. Open this file in a current Chrome, Edge, Firefox, or Safari browser.", true);
        return;
      }
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: {echoCancellation: false, noiseSuppression: false, autoGainControl: false},
          video: false
        });
        chunks = [];
        const mimeType = preferredMime();
        recorder = mimeType ? new MediaRecorder(stream, {mimeType}) : new MediaRecorder(stream);
        recorder.addEventListener("dataavailable", event => { if (event.data.size) chunks.push(event.data); });
        recorder.addEventListener("stop", finishRecording, {once: true});
        startedAt = performance.now();
        recorder.start(200);
        startMeter(stream);
        timerHandle = window.setInterval(() => {
          elements.recordingClock.textContent = `Recording ${((performance.now() - startedAt) / 1000).toFixed(1)} s`;
        }, 100);
        renderCue();
        setStatus("Recording. Read the displayed cue, then press Stop.");
      } catch (error) {
        recorder = null;
        if (stream) stream.getTracks().forEach(track => track.stop());
        stream = null;
        setStatus(`Microphone access failed: ${error.message}`, true);
      }
    }

    function stopRecording() {
      if (recorder && recorder.state !== "inactive") recorder.stop();
    }

    function finishRecording() {
      window.clearInterval(timerHandle);
      timerHandle = null;
      stopMeter();
      const cue = currentCue();
      const type = recorder.mimeType || chunks[0]?.type || "audio/webm";
      const blob = new Blob(chunks, {type});
      const duration = (performance.now() - startedAt) / 1000;
      const previous = recordings.get(cue.id);
      if (previous) URL.revokeObjectURL(previous.url);
      recordings.set(cue.id, {
        blob,
        duration,
        mimeType: type,
        extension: extensionFor(type),
        url: URL.createObjectURL(blob)
      });
      if (stream) stream.getTracks().forEach(track => track.stop());
      stream = null;
      recorder = null;
      chunks = [];
      renderCue();
      setStatus("Take recorded. Play it back before moving on.");
    }

    function downloadBlob(blob, filename) {
      const anchor = document.createElement("a");
      anchor.href = URL.createObjectURL(blob);
      anchor.download = filename;
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      window.setTimeout(() => URL.revokeObjectURL(anchor.href), 1000);
    }

    function recordingManifest() {
      return {
        schema_version: 1,
        project_title: SCRIPT.title,
        narration_sha256: SCRIPT.narration_sha256,
        recorded_at: new Date().toISOString(),
        cues: SCRIPT.cues.map(cue => {
          const clip = recordings.get(cue.id);
          return {
            id: cue.id,
            text: cue.text,
            file: clip ? `${escapeFilename(cue.id)}.${clip.extension}` : null,
            duration_seconds: clip ? Number(clip.duration.toFixed(3)) : null
          };
        })
      };
    }

    async function saveAll() {
      const manifest = recordingManifest();
      const manifestBlob = new Blob([JSON.stringify(manifest, null, 2) + "\n"], {type: "application/json"});
      try {
        if (window.showDirectoryPicker) {
          const directory = await window.showDirectoryPicker({mode: "readwrite"});
          for (const cue of SCRIPT.cues) {
            const clip = recordings.get(cue.id);
            if (!clip) continue;
            const handle = await directory.getFileHandle(`${escapeFilename(cue.id)}.${clip.extension}`, {create: true});
            const writable = await handle.createWritable();
            await writable.write(clip.blob);
            await writable.close();
          }
          const manifestHandle = await directory.getFileHandle("recording-manifest.json", {create: true});
          const writable = await manifestHandle.createWritable();
          await writable.write(manifestBlob);
          await writable.close();
          setStatus(`Saved ${recordings.size} recordings and the manifest to the selected folder.`);
          return;
        }
        for (const cue of SCRIPT.cues) {
          const clip = recordings.get(cue.id);
          if (clip) downloadBlob(clip.blob, `${escapeFilename(cue.id)}.${clip.extension}`);
        }
        downloadBlob(manifestBlob, "recording-manifest.json");
        setStatus("Downloaded the recordings and manifest. Your browser may ask permission for multiple downloads.");
      } catch (error) {
        if (error.name !== "AbortError") setStatus(`Saving failed: ${error.message}`, true);
      }
    }

    elements.projectTitle.textContent = `${SCRIPT.title} - narration recorder`;
    elements.recordButton.addEventListener("click", () => recorder ? stopRecording() : startRecording());
    elements.previousButton.addEventListener("click", () => selectCue(currentIndex - 1));
    elements.nextButton.addEventListener("click", () => selectCue(currentIndex + 1));
    elements.playButton.addEventListener("click", () => { elements.player.hidden = false; elements.player.play(); });
    elements.downloadButton.addEventListener("click", () => {
      const clip = recordings.get(currentCue().id);
      if (clip) downloadBlob(clip.blob, `${escapeFilename(currentCue().id)}.${clip.extension}`);
    });
    elements.saveAllButton.addEventListener("click", saveAll);
    window.addEventListener("keydown", event => {
      if (event.target.matches("button, audio, input, select, textarea")) return;
      if (event.code === "Space") { event.preventDefault(); recorder ? stopRecording() : startRecording(); }
      if (event.code === "ArrowLeft") selectCue(currentIndex - 1);
      if (event.code === "ArrowRight") selectCue(currentIndex + 1);
    });
    window.addEventListener("beforeunload", event => {
      if (recordings.size) { event.preventDefault(); event.returnValue = ""; }
    });
    renderCue();
  </script>
</body>
</html>
"""


def _load_target_durations(project_root: Path) -> dict[str, tuple[float, str | None]]:
    path = project_root / "assets" / "narration" / "manifest.json"
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    durations: dict[str, tuple[float, str | None]] = {}
    for identifier, item in raw.get("cues", {}).items():
        try:
            duration = float(item["duration"])
        except (KeyError, TypeError, ValueError):
            continue
        if math.isfinite(duration) and duration > 0:
            text = item.get("text")
            durations[str(identifier)] = (
                duration,
                str(text).strip() if text is not None else None,
            )
    return durations


def load_narration_script(project: str | Path) -> NarrationScript:
    config = load_project(project)
    source = config.root / "narration.toml"
    try:
        raw = tomllib.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ConfigError(f"narration script does not exist: {source}") from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"invalid TOML in {source}: {error}") from error

    settings = raw.get("narration", {})
    rate = float(settings.get("rate", 150))
    target_loudness = float(settings.get("target_loudness_lufs", -18))
    if not math.isfinite(rate) or rate <= 0:
        raise ConfigError("narration.rate must be a positive finite words-per-minute value")
    if not math.isfinite(target_loudness):
        raise ConfigError("narration.target_loudness_lufs must be finite")

    target_durations = _load_target_durations(config.root)
    cues: list[NarrationCue] = []
    seen: set[str] = set()
    for index, item in enumerate(raw.get("cue", ())):
        identifier = str(item.get("id", "")).strip()
        text = str(item.get("text", "")).strip()
        if not identifier:
            raise ConfigError(f"narration cue {index + 1} requires an id")
        if identifier in seen:
            raise ConfigError(f"duplicate narration cue id: {identifier}")
        if not text:
            raise ConfigError(f"narration cue {identifier!r} requires text")
        seen.add(identifier)
        estimated = max(1.0, len(text.split()) / rate * 60.0)
        prior = target_durations.get(identifier)
        target_duration = (
            prior[0]
            if prior is not None and (prior[1] is None or prior[1] == text)
            else estimated
        )
        cues.append(
            NarrationCue(
                identifier=identifier,
                text=text,
                target_duration=target_duration,
            )
        )
    if not cues:
        raise ConfigError(f"{source} requires at least one [[cue]] entry")
    return NarrationScript(
        title=config.title,
        source=source,
        sha256=sha256_file(source),
        rate=rate,
        target_loudness_lufs=target_loudness,
        cues=tuple(cues),
    )


def _normalize_subtitle_text(value: str) -> str:
    without_tags = re.sub(r"<[^>]+>", "", value)
    return " ".join(without_tags.split())


_DIGIT_WORDS = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}


def _alignment_text(value: str) -> str:
    normalized = _normalize_subtitle_text(value)
    digit_words = "|".join(_DIGIT_WORDS)
    pattern = re.compile(
        rf"\b(?P<sign>minus )?point(?P<digits>(?: (?:{digit_words}))+)",
        flags=re.IGNORECASE,
    )

    def decimal(match: re.Match[str]) -> str:
        digits = "".join(
            _DIGIT_WORDS[word.lower()] for word in match.group("digits").split()
        )
        sign = "-" if match.group("sign") else ""
        return f"{sign}0.{digits}"

    return pattern.sub(decimal, normalized)


def _srt_time(value: str) -> float:
    match = re.fullmatch(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", value.strip())
    if not match:
        raise ConfigError(f"invalid SRT timestamp: {value!r}")
    hours, minutes, seconds, milliseconds = (int(item) for item in match.groups())
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def _parse_srt(path: Path) -> tuple[tuple[float, float, str], ...]:
    try:
        source = path.read_text(encoding="utf-8-sig")
    except FileNotFoundError as error:
        raise ConfigError(f"subtitle file does not exist: {path}") from error
    entries: list[tuple[float, float, str]] = []
    for block in re.split(r"\r?\n\s*\r?\n", source.strip()):
        lines = block.splitlines()
        if len(lines) < 3 or " --> " not in lines[1]:
            raise ConfigError(f"invalid SRT cue in {path}: {block[:80]!r}")
        start_text, end_text = lines[1].split(" --> ", maxsplit=1)
        entries.append(
            (
                _srt_time(start_text),
                _srt_time(end_text),
                _normalize_subtitle_text(" ".join(lines[2:])),
            )
        )
    return tuple(entries)


def _discover_visual_sources(project_root: Path) -> tuple[Path, Path] | None:
    candidates: list[tuple[float, Path, Path]] = []
    for subtitles in (project_root / "build").glob("**/*.srt"):
        video = subtitles.with_suffix(".mp4")
        if video.is_file() and "partial_movie_files" not in video.parts:
            candidates.append((max(video.stat().st_mtime, subtitles.stat().st_mtime), video, subtitles))
    if not candidates:
        return None
    _, video, subtitles = max(candidates, key=lambda item: item[0])
    return video, subtitles


def _resolve_visual_sources(
    project_root: Path,
    video: str | Path | None,
    subtitles: str | Path | None,
) -> tuple[Path, Path] | None:
    if video is None and subtitles is None:
        return _discover_visual_sources(project_root)
    video_path = Path(video).expanduser().resolve() if video is not None else None
    subtitle_path = (
        Path(subtitles).expanduser().resolve() if subtitles is not None else None
    )
    if video_path is None and subtitle_path is not None:
        video_path = subtitle_path.with_suffix(".mp4")
    if subtitle_path is None and video_path is not None:
        subtitle_path = video_path.with_suffix(".srt")
    assert video_path is not None and subtitle_path is not None
    if not video_path.is_file():
        raise ConfigError(f"reference video does not exist: {video_path}")
    if not subtitle_path.is_file():
        raise ConfigError(f"matching subtitles do not exist: {subtitle_path}")
    return video_path, subtitle_path


def _reference_stills(
    script: NarrationScript,
    video: Path,
    subtitles: Path,
) -> dict[str, dict[str, object]]:
    entries = _parse_srt(subtitles)
    if len(entries) != len(script.cues):
        raise ConfigError(
            f"subtitle cue count ({len(entries)}) does not match narration cue count "
            f"({len(script.cues)})"
        )
    for cue, (_, _, subtitle_text) in zip(script.cues, entries, strict=True):
        if _alignment_text(cue.text) != _alignment_text(subtitle_text):
            raise ConfigError(f"subtitle text does not match narration cue {cue.identifier!r}")

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise ConfigError("FFmpeg is required to embed reference frames")
    stills: dict[str, dict[str, object]] = {}
    with tempfile.TemporaryDirectory(prefix="econ-manim-recorder-") as temporary:
        temporary_root = Path(temporary)
        for index, (cue, (start, end, _)) in enumerate(
            zip(script.cues, entries, strict=True)
        ):
            timestamp = max(start, end - 0.20)
            frame = temporary_root / f"{index:04d}.jpg"
            subprocess.run(
                [
                    ffmpeg,
                    "-loglevel",
                    "error",
                    "-y",
                    "-ss",
                    f"{timestamp:.3f}",
                    "-i",
                    str(video),
                    "-frames:v",
                    "1",
                    "-vf",
                    "scale=720:-2",
                    "-q:v",
                    "5",
                    str(frame),
                ],
                check=True,
            )
            encoded = base64.b64encode(frame.read_bytes()).decode("ascii")
            stills[cue.identifier] = {
                "image": f"data:image/jpeg;base64,{encoded}",
                "visual_time": timestamp,
            }
    return stills


def write_narration_recorder(
    project: str | Path,
    output: str | Path | None = None,
    *,
    video: str | Path | None = None,
    subtitles: str | Path | None = None,
    include_stills: bool = True,
) -> Path:
    script = load_narration_script(project)
    config = load_project(project)
    target = (
        Path(output).expanduser().resolve()
        if output
        else config.root / "build" / "narration-recorder.html"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    stills: dict[str, dict[str, object]] = {}
    if include_stills:
        visual_sources = _resolve_visual_sources(config.root, video, subtitles)
        if visual_sources is not None:
            stills = _reference_stills(script, *visual_sources)
    payload = {
        "title": script.title,
        "narration_sha256": script.sha256,
        "cues": [
            {
                "id": cue.identifier,
                "text": cue.text,
                "word_count": len(cue.text.split()),
                "target_duration": cue.target_duration,
                **stills.get(cue.identifier, {"image": None, "visual_time": None}),
            }
            for cue in script.cues
        ],
    }
    payload_json = json.dumps(payload, ensure_ascii=True).replace("<", "\\u003c")
    page = _RECORDER_TEMPLATE.replace(
        "__PAGE_TITLE__",
        html.escape(f"{script.title} - narration recorder", quote=True),
    ).replace("__SCRIPT_JSON__", payload_json)
    target.write_text(page, encoding="utf-8")
    return target


_RECORDING_EXTENSIONS = (".wav", ".webm", ".ogg", ".m4a", ".mp4")


def _recording_files(source: Path, identifier: str) -> tuple[Path, ...]:
    candidates = (source / f"{identifier}{suffix}" for suffix in _RECORDING_EXTENSIONS)
    return tuple(path for path in candidates if path.is_file())


def _validate_recording_manifest(source: Path, script: NarrationScript) -> Path | None:
    path = source / "recording-manifest.json"
    if not path.is_file():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ConfigError(f"invalid recording manifest {path}: {error}") from error
    if raw.get("schema_version") != 1:
        raise ConfigError(f"unsupported recording manifest schema in {path}")
    if raw.get("narration_sha256") != script.sha256:
        raise ConfigError("recordings were made from a different narration script")
    recorded_cues = {
        str(item.get("id", "")): str(item.get("text", "")).strip()
        for item in raw.get("cues", ())
    }
    expected = {cue.identifier: cue.text for cue in script.cues}
    if recorded_cues != expected:
        raise ConfigError("recording manifest cues do not match the current narration script")
    return path


def prepare_recorded_narration(
    project: str | Path,
    recordings: str | Path,
    *,
    speaker: str = "",
) -> Path:
    script = load_narration_script(project)
    config = load_project(project)
    source = Path(recordings).expanduser().resolve()
    if not source.is_dir():
        raise ConfigError(f"recordings directory does not exist: {source}")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise ConfigError("FFmpeg is required to prepare recorded narration")
    recording_manifest = _validate_recording_manifest(source, script)

    selected: dict[str, Path] = {}
    for cue in script.cues:
        matches = _recording_files(source, cue.identifier)
        if not matches:
            raise ConfigError(f"recording is missing for cue {cue.identifier!r}")
        if len(matches) > 1:
            names = ", ".join(path.name for path in matches)
            raise ConfigError(f"multiple recordings found for cue {cue.identifier!r}: {names}")
        selected[cue.identifier] = matches[0]

    target_root = config.root / "assets" / "narration"
    target_root.mkdir(parents=True, exist_ok=True)
    cue_manifest: dict[str, dict[str, object]] = {}
    for cue in script.cues:
        input_path = selected[cue.identifier]
        target = target_root / f"{cue.identifier}.wav"
        subprocess.run(
            [
                ffmpeg,
                "-loglevel",
                "error",
                "-y",
                "-i",
                str(input_path),
                "-af",
                (
                    "adelay=150:all=1,apad=pad_dur=0.35,"
                    f"loudnorm=I={script.target_loudness_lufs}:TP=-2:LRA=7"
                ),
                "-ar",
                "48000",
                "-ac",
                "1",
                str(target),
            ],
            check=True,
        )
        cue_manifest[cue.identifier] = {
            "file": str(target.relative_to(config.root)),
            "duration": probe_audio_duration(target),
            "sha256": sha256_file(target),
            "text": cue.text,
        }

    manifest = {
        "provider": "human-recording",
        "speaker": speaker.strip() or None,
        "prepared_at": datetime.now(UTC).isoformat(),
        "source_script": str(script.source.relative_to(config.root)),
        "source_script_sha256": script.sha256,
        "recording_manifest_sha256": (
            sha256_file(recording_manifest) if recording_manifest is not None else None
        ),
        "target_loudness_lufs": script.target_loudness_lufs,
        "sample_rate_hz": 48000,
        "channels": 1,
        "cues": cue_manifest,
    }
    manifest_path = target_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path
