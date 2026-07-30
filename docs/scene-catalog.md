# Scene catalog

Choose scenes by the job they perform in the argument. A project template
governs the full narrative; a component or atomic recipe should solve only one
beat.

```bash
uv run econ-manim scenes
uv run econ-manim preview-scene mechanism.channel-decomposition --theme midnight
```

## Opening

| Communication problem | Start with | Preserve |
|---|---|---|
| Pose one causal or equilibrium question | `CausalChain` with only its first node visible | The labels used in the conclusion |
| Introduce a decision | `AgentToken` or `ChoiceMap` | The same agent and alternatives |
| Introduce an empirical question | `empirical-result-led` project | The estimand in words |
| Introduce a method or theorem | `method-theory` project | The object transformed by the result |

Avoid an opening montage. Establish one object the viewer can recognize later.

## Mechanism

| Communication problem | Component or recipe | Use when |
|---|---|---|
| Movement through alternatives | `PathFlow` · `mechanism.path-flow` | The route has economic meaning |
| Several margins affect one outcome | `ChannelDecomposition` · `mechanism.channel-decomposition` | Channels are conceptually distinct |
| A change propagates sequentially | `CausalChain` | Order is part of the mechanism |
| One state has concrete and analytical views | `LinkedViews` | Both panels represent the same state |

Keep the underlying system fixed while highlighting the active route or
channel.

## Identification

Use `ShockDistribution` to show realized or constructed variation without
decorative bars. Use a directly labeled comparison or a short `CausalChain` to
connect variation to the estimand. The empirical-result-led project shows the
full handoff from question to variation to estimate.

Always state the treatment or exposure, comparison, timing, sample, and—when
applicable—the instrument before showing coefficients.

## Empirical evidence

| Result form | Component or recipe | Required nearby information |
|---|---|---|
| Small set of estimates | `CoefficientPlot` · `empirical.coefficient-intervals` | Estimand, units, reference, confidence level |
| Dynamic response | `ImpulseResponsePlot` · `empirical.impulse-response` | Horizon, event date, uncertainty, baseline |
| Benchmark restrictions | `DivergingBarChart` | Meaning of zero and changed assumption |
| Compact decomposition | `ResultTable` | Units, row definitions, total construction |
| Realized cross-section | `ShockDistribution` | Sample, unit, and classification |

Do not combine incomparable estimands on one axis or present illustrative values
as estimates.

## Theory and methods

Use `EquationBuild` to introduce a result term by term in words. Use
`CausalChain` for an operation whose sequence matters and `LinkedViews` when an
economic interpretation and formal object must change together. The
method-theory project supplies the complete problem → object → operation →
result → comparative static → application grammar.

Equations should follow meaning, not substitute for it.

## Welfare and policy value

Use `ChoiceMap` to establish the available adjustment margins,
`ChannelDecomposition` to separate economically distinct contributions, and
`EquationBuild` to assemble the welfare or policy object incrementally.
`ResultTable` is appropriate only for a compact, sourced decomposition.

State the population, baseline, horizon, units, and treatment of positive and
negative realizations.

## Conclusion

Return to the opening object. Reuse a short `CausalChain`, the persistent
estimand badge, the solved method object, or the original choice menu. Remove
technical detail that is no longer needed and stop at the paper's identification
or theoretical frontier.
