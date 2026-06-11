from manim import *
from statanim.props.card import Card3D, CardFacing, CardFace, CardSuit, CardValue
from statanim.props.coin import Coin3D, FlipCoin
from statanim.props.urn import Urn3D, Ball3D
from statanim.probability.prob_tree import ProbabilityTree3D, ProbTreeNode, ProbTreeConfig
from statanim.inference.confidence_interval import ConfidenceInterval3D, BuildCI, NarrowCI
from statanim.inference.hypothesis import HypothesisTest3D, BuildTest, DropStatistic, RevealPValue, RevealDecision
from statanim.animations.clt_demo import CLTDemo, CLTConfig
import numpy as np

BRAND_GRAY = "#888888"
BRAND_DIM  = "#1A1A1A"

LABEL_COLORS = {
    "Central Limit Theorem": "#A78BFA",
    "Probability Trees":     "#60A5FA",
    "Confidence Intervals":  "#34D399",
    "Hypothesis Testing":    "#F87171",
    "Physical Props":        "#FBBF24",
}

def section_label(text, scene):
    color = LABEL_COLORS.get(text, "#888888")
    t = Text(text, font_size=18, color=color, weight=BOLD)
    t.to_corner(DL, buff=0.35)
    scene.play(FadeIn(t, shift=UP * 0.1), run_time=0.3)
    return t

def clear_except(scene, *keep):
    to_remove = [m for m in scene.mobjects if m not in keep]
    scene.remove(*to_remove)

def info_card(lines, colors, scene):
    """Animate bullet points sliding in from right."""
    group = VGroup()
    for i, (line, color) in enumerate(zip(lines, colors)):
        t = Text(line, font_size=22, color=color)
        t.move_to(RIGHT * 3.5 + UP * (0.8 - i * 0.7))
        group.add(t)
    scene.play(
        LaggedStart(*[FadeIn(t, shift=LEFT * 0.3) for t in group], lag_ratio=0.2),
        run_time=1.0,
    )
    return group


class StatanimIntro(ThreeDScene):
    def construct(self):

        # Force 2D camera for all non-CLT sections
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

        # ════════════════════════════════════════════════════════════════
        # 1. COLD OPEN
        # ════════════════════════════════════════════════════════════════
        axes = Axes(
            x_range=[-4, 4, 1], y_range=[0, 0.45, 0.1],
            x_length=9, y_length=3.5,
            axis_config={"color": GRAY, "stroke_width": 1},
        ).shift(DOWN * 0.3)
        static_curve = axes.plot(
            lambda x: np.exp(-0.5*x**2)/np.sqrt(2*np.pi),
            x_range=[-4, 4], color=GRAY, stroke_width=1.5,
        )
        boring = Text(
            "Static diagrams don't build intuition.",
            font_size=26, color=GRAY, slant=ITALIC,
        ).to_edge(UP, buff=0.5)

        self.play(FadeIn(axes), Create(static_curve), run_time=0.8)
        self.play(FadeIn(boring, shift=DOWN * 0.2), run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(VGroup(axes, static_curve, boring)), run_time=0.6)

        # ════════════════════════════════════════════════════════════════
        # 2. TITLE
        # ════════════════════════════════════════════════════════════════
        title = Text("statanim", font_size=100, color=WHITE, weight=BOLD)
        sub = Text("A Manim extension for animated statistics", font_size=26, color=BRAND_GRAY)
        sub.next_to(title, DOWN, buff=0.5)

        self.play(
            LaggedStart(GrowFromCenter(title), FadeIn(sub, shift=UP*0.15), lag_ratio=0.35),
            run_time=1.0,
        )
        self.wait(0.9)
        self.play(title.animate.scale(0.32).to_corner(UL, buff=0.3), FadeOut(sub), run_time=0.6)

        # ════════════════════════════════════════════════════════════════
        # 3. CLT DEMO — fix camera to top-down before CLT
        # ════════════════════════════════════════════════════════════════
        lbl = section_label("Central Limit Theorem", self)
        self.set_camera_orientation(phi=75 * DEGREES, theta=-90 * DEGREES)

        clt = CLTDemo(CLTConfig(
            source="uniform", n=30, n_trials=60,
            pop_color=ManimColor("#A78BFA"),
            xbar_color_lo=ManimColor("#FFFFFF"),
            xbar_color_hi=ManimColor("#666666"),
            normal_color=ManimColor("#A78BFA"),
            particle_color=ManimColor("#FBBF24"),
            glow_normal=True,
            show_formula_panel=False,
            show_variance_annotation=False,
            show_source_label=False,
        ))
        clt.phase_population(self)
        clt.phase_accumulate(self, n_visible=40)
        clt.phase_normal_overlay(self)
        self.wait(0.8)
        self.play(FadeOut(lbl), run_time=0.2)
        clear_except(self)

        # Reset camera for 2D sections
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        self.wait(0.3)

        # ════════════════════════════════════════════════════════════════
        # 4. PROBABILITY TREE
        # ════════════════════════════════════════════════════════════════
        lbl = section_label("Probability Trees", self)

        r_r  = ProbTreeNode("Red",  prob=0.38)
        r_b  = ProbTreeNode("Blue", prob=0.62)
        b_r  = ProbTreeNode("Red",  prob=0.42)
        b_b  = ProbTreeNode("Blue", prob=0.58)
        red  = ProbTreeNode("Red",  prob=0.4, children=[r_r, r_b])
        blue = ProbTreeNode("Blue", prob=0.6, children=[b_r, b_b])
        root = ProbTreeNode("Draw", prob=1.0, children=[red, blue])

        tree = ProbabilityTree3D(root, config=ProbTreeConfig(show_edge_arrows=False))
        tree.scale(0.85).move_to(ORIGIN)
        self.play(tree.animate_grow_tree(), run_time=2.5)
        self.wait(0.8)

        # Slide tree left, show info card right
        self.play(tree.animate.shift(LEFT * 2.5), run_time=0.7)
        info = info_card(
            ["P(Red | 1st Red) = 0.38", "P(Blue | 1st Red) = 0.62", "Joint probability", "at every leaf node"],
            ["#F87171", "#60A5FA", BRAND_GRAY, BRAND_GRAY],
            self,
        )
        self.wait(1.2)
        self.play(FadeOut(lbl), FadeOut(tree), FadeOut(info), run_time=0.6)

        # ════════════════════════════════════════════════════════════════
        # 5. CONFIDENCE INTERVAL — slide 1: build, slide 2: narrow + explain
        # ════════════════════════════════════════════════════════════════
        lbl = section_label("Confidence Intervals", self)

        ci = ConfidenceInterval3D(center=70.0, std_err=2.5, confidence=0.95)
        ci.scale(0.85).move_to(ORIGIN)
        self.play(BuildCI(ci), run_time=2.0)
        self.wait(0.6)

        # Slide 2 — move left, show explanation
        self.play(ci.animate.shift(LEFT * 2.0), run_time=0.7)
        ci_info = info_card(
            ["95% Confidence Interval", "Center: 70.0 ± 4.9", "Narrowing with larger n", "σ/√n → precision"],
            ["#34D399", WHITE, BRAND_GRAY, BRAND_GRAY],
            self,
        )
        self.play(NarrowCI(ci, new_half_width=ci._hw_px * 0.45), run_time=1.8)
        self.wait(0.8)
        self.play(FadeOut(lbl), FadeOut(ci), FadeOut(ci_info), run_time=0.6)

        # ════════════════════════════════════════════════════════════════
        # 6. HYPOTHESIS TEST — slide 1: build, slide 2: result + explain
        # ════════════════════════════════════════════════════════════════
        lbl = section_label("Hypothesis Testing", self)

        ht = HypothesisTest3D(
            dist="t", obs_stat=2.34, tail="both", alpha=0.05,
            dist_kw={"df": 29},
            show_panel=False, show_badge=False,
        )
        ht.scale(0.88).move_to(ORIGIN)
        self.play(BuildTest(ht), run_time=2.0)
        self.play(DropStatistic(ht), run_time=1.0)
        self.wait(0.5)

        # Slide 2 — move left, show result panel
        self.play(ht.animate.shift(LEFT * 1.8), run_time=0.7)
        ht_info = info_card(
            ["t = 2.340,  df = 29", "p = 0.0264  <  α = 0.05", "✓ REJECT H₀", "Two-tailed t-test"],
            ["#FBBF24", "#F87171", "#34D399", BRAND_GRAY],
            self,
        )
        self.play(RevealPValue(ht), run_time=0.8)
        self.play(RevealDecision(ht), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(lbl), FadeOut(ht), FadeOut(ht_info), run_time=0.6)

        # ════════════════════════════════════════════════════════════════
        # 7. PROPS — animated interactions
        # ════════════════════════════════════════════════════════════════
        lbl = section_label("Physical Props", self)

        # Cards deal in one by one
        card_data = [
            (CardSuit.HEARTS,   CardValue.ACE),
            (CardSuit.SPADES,   CardValue.KING),
            (CardSuit.DIAMONDS, CardValue.QUEEN),
            (CardSuit.CLUBS,    CardValue.JACK),
        ]
        cards = VGroup()
        for i, (s, v) in enumerate(card_data):
            c = Card3D(face=CardFace(suit=s, value=v), facing=CardFacing.FACE_DOWN)
            c.scale(0.52)
            cards.add(c)
        cards.arrange(RIGHT, buff=0.4).move_to(UP * 1.2 + LEFT * 1.5)

        # Deal face down first
        self.play(
            LaggedStart(*[FadeIn(c, shift=DOWN * 0.3) for c in cards], lag_ratio=0.15),
            run_time=1.0,
        )
        self.wait(0.3)

        # Coin and urn appear below
        coin = Coin3D()
        coin.scale(0.65).move_to(DOWN * 0.8 + LEFT * 2.5)
        urn = Urn3D()
        for col in ["#F87171", "#F87171", "#60A5FA", "#60A5FA", "#A78BFA"]:
            urn.add_ball(Ball3D(color=col, radius=0.14))
        urn.scale(0.65).move_to(DOWN * 0.8 + RIGHT * 1.5)

        self.play(FadeIn(coin, shift=UP * 0.2), FadeIn(urn, shift=UP * 0.2), run_time=0.7)

        # Flip coin
        self.play(FlipCoin(coin), run_time=0.9)
        self.wait(0.3)

        # Flip cards face up one by one
        self.play(
            LaggedStart(
                *[c.animate.set_opacity(0.3) for c in cards[:3]] + 
                [cards[3].animate.shift(UP * 0.3)],
                lag_ratio=0.1,
            ),
            run_time=0.8,
        )
        self.wait(0.5)
        self.play(FadeOut(VGroup(lbl, cards, coin, urn)), run_time=0.6)

        # ════════════════════════════════════════════════════════════════
        # 8. END CARD with metallic pip install
        # ════════════════════════════════════════════════════════════════
        end_title = Text("statanim", font_size=72, color=WHITE, weight=BOLD)
        end_sub   = Text("Statistics. Animated.", font_size=26, color=BRAND_GRAY)
        end_sub.next_to(end_title, DOWN, buff=0.35)
        div = Line(LEFT*1.8, RIGHT*1.8, stroke_width=0.5, color="#333333")
        div.next_to(end_sub, DOWN, buff=0.3)
        gh   = Text("github.com/rishabhbhartiya/STATANIM", font_size=16, color="#555555")
        pypi = Text("pypi.org/project/statanim", font_size=16, color="#555555")
        gh.next_to(div, DOWN, buff=0.22)
        pypi.next_to(gh, DOWN, buff=0.14)
        end_group = VGroup(end_title, end_sub, div, gh, pypi).shift(DOWN * 1.6)

        self.play(
            LaggedStart(
                FadeIn(end_title, scale=0.88),
                FadeIn(end_sub, shift=UP*0.1),
                lag_ratio=0.25,
            ),
            run_time=0.9,
        )
        self.play(GrowFromCenter(div), FadeIn(gh), FadeIn(pypi), run_time=0.6)
        self.wait(0.4)

        # Metallic install box
        shadow = Rectangle(width=8.6, height=1.35,
            fill_color="#000000", fill_opacity=0.8, stroke_width=0,
        ).shift(UP * 0.56 + RIGHT * 0.05 + DOWN * 0.05)
        outer = Rectangle(width=8.6, height=1.35,
            fill_color="#1C1C1C", fill_opacity=1,
            stroke_color="#666666", stroke_width=1.5,
        ).shift(UP * 0.6)
        inner = Rectangle(width=8.3, height=1.05,
            fill_color="#0D0D0D", fill_opacity=1,
            stroke_color="#444444", stroke_width=0.5,
        ).shift(UP * 0.6)
        shine = Rectangle(width=8.3, height=0.25,
            fill_color=WHITE, fill_opacity=0.05, stroke_width=0,
        ).shift(UP * 1.1)

        install = Text(
            "pip install statanim",
            font="Courier", font_size=44, color=WHITE,
        ).shift(UP * 0.6)

        self.play(FadeIn(shadow), FadeIn(outer), FadeIn(inner), FadeIn(shine), run_time=0.4)
        self.play(AddTextLetterByLetter(install, time_per_char=0.05), run_time=1.2)
        self.wait(3.0)