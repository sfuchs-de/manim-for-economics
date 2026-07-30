# Troubleshooting

## `manim` is not found

Use commands through the project environment:

```bash
uv run manim --version
uv run econ-manim doctor
```

With a manually activated environment, try `python -m manim`.

## ManimPango or Cairo fails to install

Install the system packages in [setup](setup.md). On macOS, verify:

```bash
brew install cairo pkg-config
```

On Linux, verify the compiler, Python headers, Cairo, and Pango development
headers listed in the official Manim installation guide.

## `MathTex` fails

Run:

```bash
latex --version
dvisvgm --version
uv run econ-manim doctor --strict
```

Restart the shell after installing TeX so its binaries are on `PATH`.

## The render succeeds but text overlaps

Render with the overlay and inspect transition frames:

```bash
uv run econ-manim preview <project> --overlay
uv run econ-manim frames <project> --times 8.0 8.5 9.0
```

Do not solve persistent overlap by shrinking everything. Reduce simultaneous
content, move labels outside paths, or split the beat.

## `frames` cannot find a video

Run `preview` or `render` first, or pass an explicit file:

```bash
uv run econ-manim frames <project> --video /absolute/path/to/video.mp4
```

## A checksum changes

Do not immediately replace the manifest hash. Determine whether:

- The source file genuinely changed.
- A transformation was rerun with different ordering or rounding.
- A private or generated file was accidentally substituted.

Update the checksum and provenance note only after the difference is understood.

## Audio is rejected

`audio.enabled` must be true, and the track, license, and attribution fields must
all be present. FFmpeg must be installed. This guard prevents an undocumented
soundtrack from slipping into a public release.
