# From paper to storyboard

The hard part is deciding what the viewer should understand. Manim code comes
after that decision.

## Begin with a paper brief

Complete five objects:

1. **Question:** the motivating economic uncertainty.
2. **Agent and menu:** who chooses what, when, and where.
3. **Identification:** where the empirical variation comes from.
4. **Result:** the two or three moments that carry the argument.
5. **Interpretation:** the relevant baseline, horizon, approximation, and
   caveats.

Write these in words. Add notation only where it makes a relationship clearer.

## Choose the narrative format

Decide what must persist before allocating scenes:

- A mechanism-led paper usually keeps one system on screen while it is built,
  perturbed, and compared with restricted cases.
- An adjustment-and-welfare paper usually keeps one agent and its choice routes
  visible as responses become welfare inputs.
- An empirical-result-led paper usually keeps one estimand and one identifying
  contrast stable.
- A method or theory paper usually keeps one mathematical or economic object
  stable while successive operations transform it.

See [visual and narrative formats](visual-formats.md) and the copyable
[`templates/storyboards`](../templates/storyboards/) before creating a custom
beat structure.

## Build a claim-to-source crosswalk

For every factual statement that may appear on screen, record:

| Claim | Exact value or wording | Source | Transformation | Display status |
|---|---|---|---|---|
| Example | −1.06% | Table 2 | none | released |

If the source cannot be identified, the claim is not ready for the storyboard.

## Allocate time by learning goal

A concise video usually needs six or seven beats:

1. Question.
2. Economic agent and choices.
3. Mechanism.
4. Identification.
5. Evidence.
6. Welfare or policy interpretation.
7. Takeaway.

Give each beat one sentence the viewer should be able to repeat afterward.
Budget at least two seconds for a short sentence and longer for unfamiliar
notation or a multi-row result.

Add a **conceptual handoff** column. It should state why the last visual state of
one beat becomes the first visual state of the next. If the handoff cannot be
written in one sentence, the order may be wrong or the beats may be unrelated.

## Reuse visual objects

Use a worker, city, firm, market, or budget constraint repeatedly. Reusing the
same object lets the animation show changes in economic state rather than
reintroducing a new visual grammar on every slide.

## Treat transitions as part of the argument

A transition should explain continuity:

- Shocked labor market → available adjustment margins.
- Adjustment margins → estimated flow responses.
- Flow responses → first-order welfare.
- Interactions among those margins → second order.

If two adjacent beats have no conceptual handoff, reconsider their order.

## Approve before coding

Before implementing:

- Every empirical claim has a source.
- Illustrative elements are labeled.
- The opening and conclusion say compatible things.
- The proposed timing is realistic.
- The video does not imply stronger identification or welfare interpretation
  than the paper supports.
- The selected format fits the contribution rather than merely the available
  components.
- Every major handoff has a planned transition frame for QA.
