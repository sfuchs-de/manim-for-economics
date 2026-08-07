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
