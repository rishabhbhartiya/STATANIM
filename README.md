<div align="center">
<img src="https://raw.githubusercontent.com/rishabhbhartiya/STATANIM/main/banner.svg" alt="STATANIM — Statistical Animation for Manim" width="680"/>
</div>

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/statanim.svg?color=534AB7&labelColor=0C0C18)](https://pypi.org/project/statanim/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/statanim?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/statanim)
![Downloads](https://static.pepy.tech/badge/statanim)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-534AB7.svg?labelColor=0C0C18)](https://www.python.org/downloads/)
[![Manim Community](https://img.shields.io/badge/manim-community-1D9D74.svg?labelColor=0C0C18)](https://www.manim.community/)
[![License: MIT](https://img.shields.io/badge/license-MIT-888888.svg?labelColor=0C0C18)](./LICENSE)

**A Manim extension for animated statistical visualisations.**

Distributions, inference, regression, probability theory, and physical props —
all built on [Manim Community](https://www.manim.community/).

</div>

---

## Why statanim?

Manim is extraordinary at animating mathematics — but when it comes to statistics, you're on your own. Want to show a normal distribution shading its tails as sigma changes? A probability tree that builds itself node by node? A deck of cards dealing out to demonstrate hypergeometric sampling? With vanilla Manim, each of these requires hundreds of lines of low-level geometry code before you even start on the actual statistics.

`statanim` closes that gap. It gives statistics the same treatment Manim gives mathematics: objects that *understand* what they represent, animations that carry statistical meaning, and a workflow that stays out of your way so you can focus on the idea you're trying to communicate.

Whether you're building lecture slides, making YouTube explainers, or just trying to build intuition for a concept — statanim lets you go from idea to animation in minutes, not days.

---

## Demo

**Sample Space**

![Sample Space](https://raw.githubusercontent.com/rishabhbhartiya/STATANIM/main/videos/SampleSpaceScene.gif)

**Classical Probability**

![Classical Probability](https://raw.githubusercontent.com/rishabhbhartiya/STATANIM/main/videos/ClassicalProbabilityScene.gif)

**Conditional Probability**

![Conditional Probability](https://raw.githubusercontent.com/rishabhbhartiya/STATANIM/main/videos/ConditionalProbabilityScene.gif)

**Hypergeometric Distribution**

![Hypergeometric Distribution](https://raw.githubusercontent.com/rishabhbhartiya/STATANIM/main/videos/HypergeometricScene.gif)

**Birthday Paradox**

![Birthday Paradox](https://raw.githubusercontent.com/rishabhbhartiya/STATANIM/main/videos/BirthdayParadoxScene.gif)

---

## Installation

**Prerequisites**

```bash
pip install manim
```

LaTeX is required for formula rendering:

```bash
# macOS
brew install mactex-no-gui

# Ubuntu / Debian
sudo apt-get install texlive-full

# Windows: install MiKTeX from https://miktex.org/
```

**Install statanim**

```bash
pip install statanim
```

**Install from source**

```bash
git clone https://github.com/rishabhbhartiya/statanim.git
cd statanim
pip install -e .
```

**Verify**

```python
from manim import *
from statanim.props.card import Card3D
from statanim.distributions.normal3d import NormalCurve3D
from statanim.core.colors import DARK_THEME
```

---

## Quick Start

### Normal distribution with shaded region

```python
from manim import *
from statanim.distributions.normal3d import NormalCurve3D

class NormalDemo(Scene):
    def construct(self):
        axes = Axes(x_range=[-4, 4, 1], y_range=[0, 0.45, 0.1],
                    x_length=8, y_length=4)
        curve = NormalCurve3D(mu=0, sigma=1, axes=axes)

        self.play(Create(axes))
        self.play(Create(curve))
        self.play(curve.shade_region(x_min=-1, x_max=1))
        self.wait(2)
```

### Probability with playing cards

```python
from manim import *
from statanim.props.card import Deck3D, CardFacing, standard_deck

class CardDraw(Scene):
    def construct(self):
        deck = Deck3D(cards=standard_deck(shuffle=True, seed=0),
                      initial_facing=CardFacing.FACE_DOWN)
        deck.move_to(LEFT * 3)
        self.play(FadeIn(deck))
        self.play(deck.deal_one(target=RIGHT * 2, flip=True))
        self.wait(2)
```

---

## What's Inside

| Module | What it gives you |
|---|---|
| `distributions` | Normal, Binomial, Poisson, Hypergeometric, Beta, Gamma, Chi-squared, Student-t, F — all with PDF/PMF/CDF visualisers and shadeable regions |
| `charts` | BarChart3D, Histogram3D, BoxPlot3D, ViolinPlot3D, HeatMap3D, ScatterPlot3D, LinePlot3D — statistically correct, 3D-aware |
| `probability` | SampleSpace3D, VennDiagram3D, ProbabilityTree3D, BayesBox3D — builds event regions and conditional flows step by step |
| `inference` | HypothesisRegion3D, ConfidenceInterval3D, SamplingDistribution3D, Type I/II error visualisation |
| `regression` | RegressionPlane3D, ScatterCloud3D, residual diagnostics, correlation matrices, CI/PI shells |
| `props` | Card3D, Deck3D, Coin3D, Die3D (D4–D20), Spinner3D, Urn3D — physical probability objects with built-in logic and animations |
| `animations` | CLTDemo, DistMorph3D, ParameterSweep3D, BootstrapSampling3D, ScatterToRegression3D |
| `ui` | Ticker3D, PValueTicker3D, FormulaPanel3D, DataTable3D, AnnotationArrow3D |
| `core` | 6 built-in themes (DARK, LIGHT, PAPER, and more), diverging colormaps, 50+ LaTeX formula builders |

Full class and parameter documentation: [API_REFERENCE.md](./API_REFERENCE.md)

---

## Camera Orientation Reference

All `ThreeDScene` subclasses need an explicit camera orientation at the top of `construct()`.

```python
def construct(self):
    self.set_camera_orientation(phi=70*DEGREES, theta=-45*DEGREES)
```

| Scene type | phi | theta |
|---|---|---|
| 3D bar chart | 65° | -55° |
| Regression plane | 70° | -45° |
| Scatter cloud | 70° | -60° |
| Card grid (table-top) | 60° | -45° |
| Bivariate normal surface | 68° | -45° |

Use `Scene` (not `ThreeDScene`) for 2D content: PDF curves, PMF bars, Venn diagrams, histograms, box plots, probability trees, and hypothesis test plots.

---

## Development Setup

```bash
git clone https://github.com/rishabhbhartiya/statanim.git
cd statanim
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Contributing

Issues and pull requests are welcome at
[github.com/rishabhbhartiya/statanim](https://github.com/rishabhbhartiya/statanim).

When adding a new distribution, inherit from `BaseDistribution3D`,
implement `pdf`/`pmf`, `cdf`, `mean`, `variance`, and add a scene in
`scenes/demo_distributions.py`.

---

## Acknowledgements

Built on [Manim Community](https://www.manim.community/).
Statistical algorithms from [SciPy](https://scipy.org/) and [NumPy](https://numpy.org/).
Inspired by the mathematical animation work of 3Blue1Brown.

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

**Author:** Rishabh Bhartiya — [rishabh.bhartiya.in@gmail.com](mailto:rishabh.bhartiya.in@gmail.com)
