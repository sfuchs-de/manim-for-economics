# Add narration or music

The core workflow is silent-first. Audio is an optional publication step, not a
dependency of scene design.

## Rights first

Before adding a track, record in `project.toml`:

```toml
[audio]
enabled = true
track = "assets/my-track.wav"
license = "CC BY 4.0"
attribution = "Title — Artist — source URL"
embedded_narration = true
music_gain_db = -21.0
narration_gain_db = 0.0
```

Do not commit audio merely because it can be downloaded or generated. Confirm
that the license allows redistribution and the intended platform use.

## Install FFmpeg

The `audio` command uses FFmpeg even though normal Manim 0.20.1 rendering does
not require the external executable.

```bash
# macOS
brew install ffmpeg

# Debian or Ubuntu
sudo apt install ffmpeg
```

Windows users can follow the official
[FFmpeg download page](https://ffmpeg.org/download.html).

## Mix after the silent master passes

```bash
uv run econ-manim render <project>
uv run econ-manim audio <project>
```

When a project contains several themes or render variants, select the silent
video explicitly:

```bash
uv run econ-manim audio <project> --video path/to/silent-master.mp4
```

The command loops or trims the documented track, applies a three-second ending
fade, preserves the video stream, and writes an AAC audio master below
`build/final/`. If the Manim render already contains narration, the command
preserves that stream and mixes the music beneath it at `music_gain_db`.

## Let narration set the pace

For narration-led work, write one cue per scene section. Start the cue before
the section's first reveal and call `finish_voiceover` before the next section.
The final state then remains on screen until the cue ends. Visual sections that
run longer than their narration fail explicitly.

```python
self.next_section("mechanism")
self.start_voiceover(
    "assets/narration/mechanism.wav",
    text="A local cost change first reaches the link endpoints.",
)
# Animate the direct effect and later propagation rounds.
self.finish_voiceover()
```

During script development, pass an explicit `duration` without an audio file.
This creates narration-paced holds and subtitle timing before a final voice is
recorded. Replace estimated timing with the finished WAV files before release.

## Separate display numbers from spoken numbers

Compact chart labels and natural narration need different formatting. Use
`format_metric` or `format_metric_change` to derive both from the same exact
value:

```python
from econ_manim import format_metric_change

phrase = format_metric_change(
    -0.0260,
    display_unit="bp",
    speech_unit="basis points",
)

phrase.display  # "subtracts ≈0.03 bp"
phrase.speech   # "subtracts about point zero three basis points"
```

This avoids asking a speech engine to infer how `0.03 bp` should be pronounced.
The formatter preserves trailing zeros intentionally because they determine the
spoken decimal and the precision communicated by the chart.

## Ask a coauthor to record the script

Keep the approved script in `narration.toml`, with one entry for each visual
cue:

```toml
[narration]
rate = 150
target_loudness_lufs = -18

[[cue]]
id = "question"
text = "How should we value a transportation improvement?"
```

Generate a single self-contained recording page:

```bash
uv run econ-manim record-narration projects/my-paper
```

The command writes `build/narration-recorder.html`. When the build directory
contains a rendered MP4 and matching SRT file, the page also embeds a reference
frame from the end of every cue. Supply `--video` and `--subtitles` to select a
particular cut, or `--no-stills` to generate a text-only recorder. Subtitle text
must match the narration script, apart from display-number substitutions such
as `0.04` for the spoken phrase `point zero four`. This prevents frames from an
older cut being paired with a revised script.

Send the single HTML file to the speaker. It embeds the reference images, cue
text, target pace, recording controls, playback, retakes, and file names. The
page has no external dependencies and does not upload audio. In a current
desktop browser, the speaker allows microphone access, records each cue, and
chooses **Save all recordings**. Chrome and Edge can write the complete set to
a selected folder. Other browsers download the cue files and
`recording-manifest.json` separately.

The speaker returns the folder. Prepare consistent 48 kHz mono WAV files using
the cue IDs already referenced by the scene:

```bash
uv run econ-manim prepare-narration \
  projects/my-paper path/to/returned-recordings \
  --speaker "Speaker Name"
```

This command requires FFmpeg. It checks that every scripted cue has exactly one
recording before writing anything, normalizes loudness, and creates
`assets/narration/manifest.json`. Rerender the project after import so the human
recording determines each cue's final duration. Keep raw and prepared voice
recordings private unless the speaker has explicitly approved redistribution.
