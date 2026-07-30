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

The command loops or trims the documented track, applies a three-second ending
fade, preserves the video stream, and writes an AAC audio master below
`build/final/`.

For narration-led work, establish the narration script and timestamps before
animation. This repository documents that extension but does not automate
speech generation or alignment in v0.1.0.
