from manim import *
from statanim.props.card import Card3D, Deck3D, CardFacing, standard_deck, CardSuit, CardValue
from statanim.props.coin import Coin3D, FlipCoin

from statanim.props.spinner import Spinner3D, SpinToOutcome
from statanim.props.urn import Urn3D, Ball3D
from statanim.distributions.normal3d import NormalCurve3D
from statanim.core.colors import DARK_THEME


class StatanimIntro(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        # ── 1. Title card ────────────────────────────────────────────────
        title = Text("statanim", font_size=72, color=WHITE)
        subtitle = Text(
            "A Manim extension for animated statistics",
            font_size=28,
            color=GRAY,
        )
        subtitle.next_to(title, DOWN, buff=0.4)
        title_group = VGroup(title, subtitle).move_to(ORIGIN)

        self.add_fixed_in_frame_mobjects(title_group)
        self.play(FadeIn(title_group), run_time=1.2)
        self.wait(1.5)
        self.play(FadeOut(title_group), run_time=0.8)

        # ── 2. Props showcase ────────────────────────────────────────────

        # --- Cards ---
        deck = Deck3D(
            cards=standard_deck(shuffle=True, seed=42),
            initial_facing=CardFacing.FACE_DOWN,
        )
        deck.move_to(LEFT * 4)
        self.play(FadeIn(deck), run_time=0.6)

        targets = [LEFT * 1.5, ORIGIN, RIGHT * 1.5, RIGHT * 3]
        for t in targets:
            self.play(deck.deal_one(target=t, flip=True), run_time=0.4)

        prop_label = Text("props — cards, coins, urns, spinners",
                          font_size=22, color=GRAY)
        prop_label.to_edge(DOWN, buff=0.4)
        self.add_fixed_in_frame_mobjects(prop_label)
        self.play(FadeIn(prop_label), run_time=0.4)
        self.wait(0.8)

        # --- Coin ---
        coin = Coin3D(radius=0.35, thickness=0.08)
        coin.move_to(LEFT * 5)
        self.play(FadeIn(coin), run_time=0.4)
        self.play(FlipCoin(coin), run_time=0.6)

        # --- Spinner ---
        spinner = Spinner3D.uniform(4)
        spinner.move_to(RIGHT * 4.5 + UP * 1)
        self.play(FadeIn(spinner), run_time=0.4)
        self.play(SpinToOutcome(spinner, target_sector=2), run_time=0.8)

        # --- Urn ---
        urn = Urn3D()
        for color in ["#E63946", "#E63946", "#E63946", "#4A90D9", "#4A90D9"]:
            urn.add_ball(Ball3D(color=color, radius=0.15))
        urn.move_to(RIGHT * 5.5 + DOWN * 0.5)
        self.play(FadeIn(urn), run_time=0.6)

        self.wait(1)
        self.play(FadeOut(prop_label))

        # ── 3. Distributions ─────────────────────────────────────────────
        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=0.8,
        )
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[0, 0.5, 0.1],
            x_length=8,
            y_length=4,
        ).shift(DOWN * 0.5)

        curve = NormalCurve3D(mu=0, sigma=1, axes=axes)
        dist_label = Text("distributions — normal, binomial, poisson & more",
                          font_size=22, color=GRAY)
        dist_label.to_edge(DOWN, buff=0.4)

        self.add_fixed_in_frame_mobjects(dist_label)
        self.play(Create(axes), run_time=0.6)
        self.play(curve.animate_curve(), run_time=1.2)
        self.play(FadeIn(dist_label), run_time=0.4)
        self.play(
            FadeIn(curve.shade_region(x_min=-1, x_max=1)),
            run_time=0.8,
        )
        self.wait(0.8)

        # ── 4. Install callout ────────────────────────────────────────────
        self.play(
            *[FadeOut(m) for m in self.mobjects],
            run_time=0.8,
        )
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

        install_line = Text("pip install statanim",
                            font_size=40, color="#534AB7",
                            font="Monospace")

        github_line = Text(
            "github.com/rishabhbhartiya/STATANIM",
            font_size=24, color=GRAY,
        )
        pypi_line = Text(
            "pypi.org/project/statanim",
            font_size=24, color=GRAY,
        )
        github_line.next_to(install_line, DOWN, buff=0.5)
        pypi_line.next_to(github_line, DOWN, buff=0.3)

        footer = VGroup(install_line, github_line, pypi_line).move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(footer)
        self.play(FadeIn(install_line), run_time=0.6)
        self.play(FadeIn(github_line), FadeIn(pypi_line), run_time=0.6)
        self.wait(2)

        # ── 5. End card ───────────────────────────────────────────────────
        self.play(FadeOut(footer), run_time=0.6)

        end_title = Text("statanim", font_size=64, color=WHITE)
        tagline = Text(
            "Statistics. Animated.",
            font_size=32, color=GRAY,
        )
        tagline.next_to(end_title, DOWN, buff=0.4)
        end_group = VGroup(end_title, tagline).move_to(ORIGIN)

        self.add_fixed_in_frame_mobjects(end_group)
        self.play(FadeIn(end_group), run_time=0.8)
        self.wait(2)