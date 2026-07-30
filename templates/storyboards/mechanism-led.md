# Mechanism-led storyboard template

Use this when the contribution explains how one intervention propagates through
an economic system. Replace every placeholder and adjust the timing to the
paper.

| Time | Learning goal | On-screen words | Visual action | Conceptual handoff | Evidence/status |
|---|---|---|---|---|---|
| 0:00–0:06 | Pose the system-wide question | How can [local intervention] affect [aggregate outcome]? | Show the intervention-to-outcome chain in words | The question identifies the system to build | Paper motivation |
| 0:06–0:24 | Build the baseline system | [agents, nodes, markets, or constraints] | Add one economically necessary object at a time | The completed system defines the pre-intervention state | Model primitives; illustrative geometry labeled |
| 0:24–0:34 | Introduce one intervention | [intervention in words] | Change one persistent object; do not reset the stage | The changed object generates the responses that follow | Policy or shock definition |
| 0:34–0:52 | Trace mechanisms | [mechanism 1], [mechanism 2], [mechanism 3] | Activate one route or margin at a time | Preserve the mechanism labels for the comparison | Model mechanism |
| 0:52–1:08 | Compare restricted cases | relative to [benchmark] | Grow each directly labeled result from a fixed zero line | The sign and size reveal which channels matter | Table, figure, or simulation output |
| 1:08–1:20 | Synthesize | [outcome] = [mechanisms] | Transform the preserved mechanism labels into the final expression | Return to the opening question | Supported interpretation |

Before coding:

- Write the benchmark for every comparison.
- Decide which single object persists through the whole video.
- Mark all mechanism geometry as illustrative unless it is calibrated data.
- Add named settled and transition frames to `project.toml`.
