# Manim Statistics Extension

A comprehensive 3D visualization framework for statistical concepts, probability theory, and data analysis built on top of [Manim Community](https://www.manim.community/).

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Manim](https://img.shields.io/badge/manim-community-orange.svg)](https://www.manim.community/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Overview

`manim_stats` extends Manim's animation capabilities to create publication-quality visualizations for:

- **Probability Distributions** (Normal, Binomial, Poisson, Exponential, etc.)
- **Statistical Inference** (Hypothesis testing, confidence intervals, sampling distributions)
- **Bayesian Analysis** (Prior/posterior visualization, Bayes theorem demonstrations)
- **Data Visualization** (3D charts, plots, and statistical graphics)
- **Probabilistic Props** (Interactive dice, coins, cards, urns for stochastic simulations)
- **Central Limit Theorem** (Animated demonstrations and convergence visualizations)

### Why This Extension?

Standard Manim excels at mathematical animations but lacks domain-specific tools for statistics. This extension provides:

- **Statistically-aware objects** that understand distributions, parameters, and sampling
- **Automatic probability calculations** embedded in visual elements
- **Preset animations** for common statistical demonstrations (CLT, hypothesis testing, Bayesian updates)
- **3D statistical charts** with proper depth perception and rotation
- **Configurable color schemes** optimized for statistical interpretation

---

## 📦 Installation

### Prerequisites

```bash
# Ensure you have Manim Community installed
pip install manim

# For LaTeX rendering (recommended)
# macOS
brew install mactex-no-gui

# Ubuntu/Debian
sudo apt-get install texlive-full

# Windows: Install MiKTeX from https://miktex.org/
```

### Install manim_stats

```bash
# From source (recommended for development)
git clone https://github.com/yourusername/manim_stats.git
cd manim_stats
pip install -e .

# Or via pip (when published)
pip install manim-stats
```

### Verify Installation

```python
from manim import *
from manim_stats import Normal3D, Coin, BayesianUpdater

# If no errors, you're ready!
```

---

## 🚀 Quick Start

### Example 1: Normal Distribution Visualization

```python
from manim import *
from manim_stats.distributions import Normal3D
from manim_stats.axes import Axes3D

class NormalDemo(ThreeDScene):
    def construct(self):
        # Create 3D axes
        axes = Axes3D(
            x_range=[-4, 4, 1],
            y_range=[0, 0.5, 0.1],
            z_range=[0, 1, 0.2]
        )
        
        # Create normal distribution
        normal = Normal3D(
            mean=0,
            std=1,
            x_range=[-4, 4],
            color=BLUE,
            fill_opacity=0.7
        )
        
        # Shade area under curve (P(-1 < X < 1))
        shaded_area = normal.get_shaded_region(
            x_min=-1,
            x_max=1,
            color=YELLOW
        )
        
        # Animate
        self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES)
        self.play(Create(axes))
        self.play(Create(normal))
        self.play(FadeIn(shaded_area))
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(5)
```

### Example 2: Central Limit Theorem Animation

```python
from manim import *
from manim_stats.animations import CLTDemo
from manim_stats.distributions import UniformDistribution, Normal3D

class CLTScene(Scene):
    def construct(self):
        # Create CLT demonstration
        clt = CLTDemo(
            source_distribution=UniformDistribution(a=0, b=1),
            sample_sizes=[1, 5, 10, 30],
            n_samples=1000
        )
        
        # Animate the convergence
        self.play(clt.animate_convergence(run_time=10))
        
        # Show theoretical vs empirical comparison
        self.play(clt.show_comparison())
```

### Example 3: Bayesian Updating

```python
from manim import *
from manim_stats.probability import BayesianUpdater
from manim_stats.animations import BayesianAnimation

class BayesDemo(Scene):
    def construct(self):
        # Define hypothesis space
        hypotheses = ["Fair Coin", "Biased (70% H)", "Biased (90% H)"]
        priors = [0.33, 0.33, 0.34]
        
        # Create Bayesian updater
        updater = BayesianUpdater(
            hypotheses=hypotheses,
            priors=priors,
            likelihood_func=self.coin_likelihood
        )
        
        # Observe data and update
        data = ["H", "H", "T", "H", "H"]
        animation = BayesianAnimation(updater, data)
        
        self.play(animation.animate_updates(run_time=8))
    
    def coin_likelihood(self, hypothesis, data):
        """Calculate P(data | hypothesis)"""
        p_heads = {"Fair Coin": 0.5, "Biased (70% H)": 0.7, "Biased (90% H)": 0.9}
        return p_heads[hypothesis] if data == "H" else (1 - p_heads[hypothesis])
```

---

## 🏗️ Architecture

### Module Structure

```
manim_stats/
├── animations/          # Preset statistical animations
│   ├── clt_demo.py      # Central Limit Theorem demonstrations
│   ├── flip_roll.py     # Stochastic process animations
│   ├── sampling.py      # Sampling distribution builders
│   └── transitions.py   # Distribution morphing/transitions
│
├── axes/                # 3D coordinate systems
│   ├── axes3d.py        # Enhanced 3D axes with stat features
│   ├── grid3d.py        # Statistical grid overlays
│   └── number_plane3d.py # 3D number planes for bivariate data
│
├── charts/              # Statistical charts in 3D
│   ├── bar_chart3d.py   # 3D bar charts (frequency, grouped)
│   ├── box_plot3d.py    # Box-and-whisker plots
│   ├── heat_map3d.py    # Correlation/confusion matrices
│   ├── histogram3d.py   # 3D histograms with binning
│   ├── line_plot3d.py   # Time series and trend lines
│   ├── scatter_plot3d.py # 3D scatter with regression
│   └── violin_plot3d.py # Distribution shape comparisons
│
├── core/                # Base utilities
│   ├── base.py          # Abstract base classes
│   ├── colors.py        # Statistical color schemes
│   ├── math_utils.py    # Probability/statistics functions
│   └── tex_utils.py     # LaTeX formula rendering
│
├── distributions/       # Probability distributions
│   ├── base_dist.py     # Distribution base class
│   ├── continuous_dists.py # Normal, Exponential, Beta, etc.
│   ├── discrete_dists.py   # Binomial, Poisson, Geometric, etc.
│   ├── normal3d.py      # Special 3D normal implementation
│   ├── pdf_viz.py       # PDF visualization tools
│   ├── pmf_viz.py       # PMF visualization tools
│   └── cdf_viz.py       # CDF visualization tools
│
├── inference/           # Statistical inference
│   ├── hypothesis.py    # Hypothesis testing framework
│   ├── confidence_interval.py # CI visualization
│   ├── sampling_dist.py # Sampling distribution theory
│   └── error_types.py   # Type I/II error visualization
│
├── probability/         # Probability theory
│   ├── bayes.py         # Bayesian updating and visualization
│   ├── prob_tree.py     # Probability tree diagrams
│   ├── sample_space.py  # Sample space representations
│   └── venn3d.py        # 3D Venn diagrams for events
│
├── props/               # Probabilistic objects
│   ├── card.py          # Playing cards with deck operations
│   ├── coin.py          # Coin flipping animations
│   ├── die.py           # Dice rolling and outcomes
│   ├── spinner.py       # Probability spinners
│   └── urn.py           # Urn models for sampling
│
├── regression/          # Regression analysis
│   ├── correlation.py   # Correlation visualization
│   ├── regression_plane.py # 3D regression surfaces
│   └── residuals.py     # Residual analysis plots
│
├── scenes/              # Complete demonstration scenes
│   ├── demo_bayes.py    # Bayesian inference examples
│   ├── demo_clt.py      # CLT demonstrations
│   ├── demo_distributions.py # Distribution showcase
│   └── demo_hypothesis.py    # Hypothesis testing examples
│
└── ui/                  # UI components
    ├── labels.py        # Statistical labels and annotations
    ├── panels.py        # Information panels
    ├── table3d.py       # Data tables in 3D space
    └── ticker.py        # Real-time value tickers
```

---

## 🎨 Core Concepts

### 1. Statistical Objects

All statistical objects inherit from base classes that provide common functionality:

```python
from manim_stats.core.base import StatisticalObject

class MyDistribution(StatisticalObject):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mean = None
        self.variance = None
    
    def calculate_probability(self, x_min, x_max):
        """Calculate P(x_min < X < x_max)"""
        pass
    
    def generate_samples(self, n):
        """Generate n random samples"""
        pass
```

### 2. Distribution System

Distributions are first-class objects with built-in sampling and probability methods:

```python
from manim_stats.distributions import Normal3D, Binomial

# Continuous distribution
normal = Normal3D(mean=100, std=15)
samples = normal.generate_samples(1000)
prob = normal.calculate_probability(85, 115)  # P(85 < X < 115)

# Discrete distribution
binomial = Binomial(n=10, p=0.5)
pmf_values = binomial.get_pmf_values()
```

### 3. Automatic Probability Visualization

Distributions can automatically visualize probabilities:

```python
from manim_stats.distributions import Exponential3D

exp_dist = Exponential3D(lambda_param=1.5)

# Shade and label P(X > 2)
shaded = exp_dist.shade_tail(
    x_min=2,
    direction="right",
    color=RED,
    show_probability=True  # Automatically calculates and displays
)
```

### 4. Statistical Animations

Preset animations for common demonstrations:

```python
from manim_stats.animations import SamplingAnimation

# Animate drawing samples from a distribution
sampling = SamplingAnimation(
    distribution=normal,
    n_samples=50,
    show_histogram=True,
    show_statistics=True  # Display mean, std, etc.
)

self.play(sampling.run())
```

---

## 🎓 Advanced Usage

### Custom Distribution Implementation

```python
from manim_stats.distributions.base_dist import ContinuousDistribution
import numpy as np

class CustomDistribution(ContinuousDistribution):
    def __init__(self, alpha, beta, **kwargs):
        self.alpha = alpha
        self.beta = beta
        super().__init__(**kwargs)
    
    def pdf(self, x):
        """Probability density function"""
        return self.alpha * np.exp(-self.beta * x) * (x >= 0)
    
    def cdf(self, x):
        """Cumulative distribution function"""
        return 1 - np.exp(-self.beta * x) if x >= 0 else 0
    
    def mean(self):
        return 1 / self.beta
    
    def variance(self):
        return 1 / (self.beta ** 2)
    
    def sample(self, n=1):
        """Generate random samples"""
        return np.random.exponential(1/self.beta, n)
```

### Interactive Hypothesis Testing

```python
from manim_stats.inference import HypothesisTest
from manim_stats.distributions import TDistribution

class TTestVisualization(Scene):
    def construct(self):
        # Set up hypothesis test
        test = HypothesisTest(
            null_distribution=TDistribution(df=20),
            alpha=0.05,
            alternative="two-sided"
        )
        
        # Add test statistic
        t_statistic = 2.3
        test.add_test_statistic(t_statistic)
        
        # Visualize rejection regions
        self.play(test.show_rejection_regions())
        
        # Show p-value calculation
        self.play(test.show_p_value())
        
        # Decision
        self.play(test.show_decision())
```

### Multivariate Visualizations

```python
from manim_stats.charts import Scatter3D
from manim_stats.regression import RegressionPlane

class MultivariateDemo(ThreeDScene):
    def construct(self):
        # Generate correlated data
        n = 100
        x = np.random.normal(0, 1, n)
        y = np.random.normal(0, 1, n)
        z = 2*x + 3*y + np.random.normal(0, 0.5, n)
        
        # Create 3D scatter plot
        scatter = Scatter3D(
            x_data=x,
            y_data=y,
            z_data=z,
            point_color=BLUE,
            point_size=0.05
        )
        
        # Fit regression plane
        plane = RegressionPlane(
            x_data=x,
            y_data=y,
            z_data=z,
            color=RED,
            opacity=0.5
        )
        
        # Show residuals
        residuals = plane.get_residual_lines(scatter)
        
        self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES)
        self.play(Create(scatter))
        self.play(Create(plane))
        self.play(Create(residuals))
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(10)
```

### Bayesian Network Visualization

```python
from manim_stats.probability import ProbabilityTree, BayesNet

class BayesNetDemo(Scene):
    def construct(self):
        # Define network structure
        network = BayesNet()
        
        # Add nodes (random variables)
        network.add_node("Disease", ["Present", "Absent"], prior=[0.01, 0.99])
        network.add_node("Test", ["Positive", "Negative"])
        
        # Add conditional probabilities
        network.add_conditional(
            child="Test",
            parent="Disease",
            table={
                "Present": [0.95, 0.05],   # P(Test|Disease=Present)
                "Absent": [0.05, 0.95]      # P(Test|Disease=Absent)
            }
        )
        
        # Visualize network
        self.play(network.draw())
        
        # Perform inference
        posterior = network.infer(evidence={"Test": "Positive"})
        self.play(network.show_posterior(posterior))
```

---

## 🎬 Animation Recipes

### Recipe 1: Confidence Interval Construction

```python
from manim_stats.inference import ConfidenceInterval
from manim_stats.animations import SamplingDistributionBuilder

class CIConstruction(Scene):
    def construct(self):
        # True population
        population = Normal3D(mean=50, std=10)
        
        # Build sampling distribution
        builder = SamplingDistributionBuilder(
            population=population,
            sample_size=30,
            n_samples=100
        )
        
        self.play(builder.animate_sampling())
        
        # Construct CI
        ci = ConfidenceInterval(
            sampling_dist=builder.get_distribution(),
            confidence_level=0.95
        )
        
        self.play(ci.show_construction())
        self.play(ci.animate_interpretation())
```

### Recipe 2: Type I and Type II Errors

```python
from manim_stats.inference import ErrorVisualization

class ErrorTypes(Scene):
    def construct(self):
        error_viz = ErrorVisualization(
            null_dist=Normal3D(mean=0, std=1),
            alt_dist=Normal3D(mean=1.5, std=1),
            alpha=0.05
        )
        
        # Show Type I error
        self.play(error_viz.show_type_i_error())
        self.wait(2)
        
        # Show Type II error
        self.play(error_viz.show_type_ii_error())
        self.wait(2)
        
        # Show power
        self.play(error_viz.show_power())
```

### Recipe 3: Monte Carlo Simulation

```python
from manim_stats.props import Die, Coin
from manim_stats.animations import MonteCarloSimulation

class MonteCarloDemo(Scene):
    def construct(self):
        # Simulate: What's P(sum of 2 dice > 9)?
        
        dice = [Die() for _ in range(2)]
        
        simulation = MonteCarloSimulation(
            props=dice,
            condition=lambda outcomes: sum(outcomes) > 9,
            n_trials=1000,
            show_convergence=True
        )
        
        self.play(simulation.run(run_time=15))
        
        # Show theoretical probability
        self.play(simulation.show_theoretical(prob=6/36))
```

---

## 🎨 Color Schemes

### Built-in Statistical Color Palettes

```python
from manim_stats.core.colors import (
    STAT_BLUE,      # Primary distribution color
    STAT_RED,       # Rejection region
    STAT_GREEN,     # Acceptance region
    STAT_YELLOW,    # Highlight/warning
    STAT_PURPLE,    # Alternative hypothesis
    SEQUENTIAL,     # Blue gradient
    DIVERGING,      # Red-Blue diverging
    CATEGORICAL     # Distinct colors for categories
)

# Use in distributions
normal = Normal3D(color=STAT_BLUE, shaded_color=STAT_YELLOW)

# Use in charts
chart = BarChart3D(data=[1,2,3,4], colors=CATEGORICAL)
```

### Custom Color Mapping

```python
from manim_stats.core.colors import create_color_gradient

# Create custom gradient
gradient = create_color_gradient(
    start_color=BLUE,
    end_color=RED,
    n_colors=10
)

# Apply to histogram bins
histogram = Histogram3D(
    data=samples,
    bins=10,
    color_gradient=gradient
)
```

---

## 📊 Data Integration

### Working with Real Data

```python
import pandas as pd
from manim_stats.charts import Scatter3D, Histogram3D

class DataVisualization(ThreeDScene):
    def construct(self):
        # Load data
        df = pd.read_csv("data.csv")
        
        # Create visualizations
        scatter = Scatter3D.from_dataframe(
            df,
            x_col="age",
            y_col="income",
            z_col="satisfaction",
            color_col="category"
        )
        
        self.play(Create(scatter))
        
        # Add regression surface
        self.play(scatter.add_regression_surface())
```

### Statistical Summary Tables

```python
from manim_stats.ui import SummaryTable

class SummaryDemo(Scene):
    def construct(self):
        data = np.random.normal(100, 15, 1000)
        
        table = SummaryTable(
            data=data,
            statistics=["mean", "std", "median", "q1", "q3", "iqr"],
            title="Sample Statistics"
        )
        
        self.play(table.build())
```

---

## 🧪 Testing and Validation

### Unit Testing Distributions

```python
import unittest
from manim_stats.distributions import Normal3D

class TestNormal3D(unittest.TestCase):
    def test_pdf_integration(self):
        """Test that PDF integrates to 1"""
        normal = Normal3D(mean=0, std=1)
        integral = normal.integrate_pdf(-10, 10)
        self.assertAlmostEqual(integral, 1.0, places=5)
    
    def test_empirical_rule(self):
        """Test 68-95-99.7 rule"""
        normal = Normal3D(mean=0, std=1)
        p1 = normal.calculate_probability(-1, 1)
        self.assertAlmostEqual(p1, 0.683, places=2)
```

### Visual Regression Testing

```python
# tests/test_visual_regression.py
from manim_stats.testing import VisualTest

class TestDistributions(VisualTest):
    def test_normal_rendering(self):
        """Ensure normal distribution renders consistently"""
        scene = self.create_scene(NormalDemo)
        self.assertImageMatches(scene, "normal_distribution.png")
```

---

## 🔧 Configuration

### Global Settings

Create `manim_stats_config.py`:

```python
from manim_stats.config import Config

Config.set_defaults(
    # Rendering
    resolution="1080p",
    fps=60,
    
    # Statistical
    alpha_level=0.05,
    confidence_level=0.95,
    n_bootstrap_samples=10000,
    
    # Visual
    distribution_resolution=100,
    chart_style="modern",  # or "classic", "minimal"
    color_scheme="viridis",
    
    # Animation
    default_run_time=2,
    transition_time=0.5
)
```

### Per-Scene Configuration

```python
class MyScene(Scene):
    config = {
        "stat_alpha": 0.01,
        "distribution_color": BLUE,
        "show_calculations": True
    }
```

---

## 📚 API Reference

See [API_REFERENCE.md](./API_REFERENCE.md) for complete API documentation.

**Key Modules:**

- **Distributions**: `manim_stats.distributions.*`
- **Charts**: `manim_stats.charts.*`
- **Inference**: `manim_stats.inference.*`
- **Probability**: `manim_stats.probability.*`
- **Props**: `manim_stats.props.*`
- **Animations**: `manim_stats.animations.*`

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/manim_stats.git
cd manim_stats

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Check code style
black manim_stats/
flake8 manim_stats/
mypy manim_stats/
```

### Adding New Distributions

1. Inherit from `ContinuousDistribution` or `DiscreteDistribution`
2. Implement required methods: `pdf/pmf`, `cdf`, `mean`, `variance`, `sample`
3. Add visualization methods
4. Write tests
5. Document with examples

---

## 📖 Educational Resources

### Tutorials

- [Getting Started with Statistical Animations](./docs/tutorials/01_getting_started.md)
- [Creating Custom Distributions](./docs/tutorials/02_custom_distributions.md)
- [Advanced Bayesian Visualizations](./docs/tutorials/03_bayesian_viz.md)
- [Hypothesis Testing Animations](./docs/tutorials/04_hypothesis_testing.md)

### Example Gallery

Browse complete examples at [examples/](./examples/):

- `examples/distributions/` - All distribution types
- `examples/inference/` - Hypothesis tests, CIs, power analysis
- `examples/bayesian/` - Bayesian updating, MCMC visualization
- `examples/regression/` - Linear and nonlinear regression
- `examples/timeseries/` - Time series and forecasting

---

## 🎯 Use Cases

### Academic Teaching

Create lecture materials for:
- Introductory Statistics courses
- Probability Theory
- Bayesian Statistics
- Machine Learning (probability foundations)
- Experimental Design

### Research Presentations

Generate publication-quality animations for:
- Conference talks
- Paper supplementary materials
- Grant proposals
- Public outreach

### Online Education

Build content for:
- YouTube educational channels
- Online courses (Coursera, edX, etc.)
- Interactive tutorials
- Statistical concept explainers

---

## 🐛 Troubleshooting

### Common Issues

**Issue: LaTeX rendering fails**
```bash
# Solution: Install LaTeX distribution
# See Installation section for platform-specific instructions
```

**Issue: 3D scenes render incorrectly**
```python
# Solution: Explicitly set camera orientation
self.set_camera_orientation(phi=60*DEGREES, theta=-45*DEGREES)
```

**Issue: Slow rendering for complex distributions**
```python
# Solution: Reduce resolution for previews
normal = Normal3D(mean=0, std=1, resolution=50)  # Instead of 100
```

**Issue: Colors don't match between objects**
```python
# Solution: Use color scheme manager
from manim_stats.core.colors import StatColorScheme
scheme = StatColorScheme("viridis")
normal = Normal3D(color=scheme.primary)
```

---

## 📊 Performance Tips

### Optimization Strategies

1. **Reduce polygon resolution for drafts**
   ```python
   # Draft mode
   Config.distribution_resolution = 50
   
   # Final render
   Config.distribution_resolution = 200
   ```

2. **Use object caching**
   ```python
   @cached_distribution
   class MyDistribution(Normal3D):
       pass
   ```

3. **Batch similar operations**
   ```python
   # Instead of multiple separate animations
   self.play(Create(obj1), Create(obj2), Create(obj3))
   ```

4. **Limit camera movements**
   ```python
   # Smoother rendering
   self.move_camera(phi=60*DEGREES, run_time=2)  # Instead of multiple small moves
   ```

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

- Built on [Manim Community](https://www.manim.community/)
- Inspired by 3Blue1Brown's animations
- Statistical algorithms from SciPy and NumPy
- Color schemes from matplotlib and seaborn

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/manim_stats/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/manim_stats/discussions)
- **Email**: stats-manim@example.com
- **Twitter**: [@manim_stats](https://twitter.com/manim_stats)

---

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Core distributions (Normal, Binomial, Poisson, etc.)
- ✅ 3D statistical charts
- ✅ Basic hypothesis testing
- ✅ Bayesian updating

### Version 1.1 (Planned)
- 🔲 MCMC visualization (Metropolis-Hastings, Gibbs)
- 🔲 Survival analysis (Kaplan-Meier curves)
- 🔲 Time series decomposition
- 🔲 Interactive parameter sliders

### Version 2.0 (Future)
- 🔲 Machine learning visualizations
- 🔲 Causal inference diagrams
- 🔲 Network/graph statistics
- 🔲 Real-time data streaming

---

**Happy Visualizing! 📊✨**