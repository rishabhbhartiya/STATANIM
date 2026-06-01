"""
card_probability_scenes.py
===========================
Five self-contained Manim scenes teaching probability concepts
through playing-card visualisations.

Scenes
------
Scene 1  SampleSpaceScene
         The full 52-card sample space laid out as a 4×13 grid.
         Each suit row colour-coded.  P(Heart) annotated live.

Scene 2  ClassicalProbabilityScene
         A single card drawn from the deck.  Three events built
         up one at a time:  P(Red),  P(Ace),  P(Red AND Ace).
         Venn-style shading on the grid shows each event region.

Scene 3  ConditionalProbabilityScene
         Deck split into Red / Black halves on screen.
         P(Ace | Red) derived step-by-step with Bayes box overlay.

Scene 4  HypergeometricScene
         Five cards dealt face-down, then flipped one by one.
         Running count of Hearts.  PMF bar builds in real-time.
         Shows X ~ Hypergeometric(N=52, K=13, n=5).

Scene 5  BirthdayParadoxScene
         Cards represent birthdays (52 weeks of the year).
         Deal cards face-up one at a time.  The moment a suit
         repeats, the collision is highlighted and P(collision)
         is shown as a function of draws so far.

Render examples
---------------
    manim -pql card_probability_scenes.py SampleSpaceScene
    manim -pql card_probability_scenes.py ClassicalProbabilityScene
    manim -pql card_probability_scenes.py ConditionalProbabilityScene
    manim -pql card_probability_scenes.py HypergeometricScene
    manim -pql card_probability_scenes.py BirthdayParadoxScene
    manim -pqh card_probability_scenes.py SampleSpaceScene   # high quality
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import List, Optional

import numpy as np

from manim import (
    Scene,
    VGroup, VMobject, Rectangle, RoundedRectangle,
    Line, DashedLine, Arrow, Dot,
    Text, MathTex,
    ManimColor, WHITE, BLACK, GRAY, DARK_GRAY,
    RED, BLUE, GREEN, YELLOW, GOLD,
    UP, DOWN, LEFT, RIGHT, ORIGIN,
    PI, TAU, DEGREES,
    Write, Create, FadeIn, FadeOut,
    Transform, ReplacementTransform,
    Flash, Indicate, Circumscribe,
    AnimationGroup, Succession, LaggedStart,
    rate_functions,
    interpolate_color,
    SurroundingRectangle,
)

from statanim.props.card import (
    Card3D, Deck3D, CardFace, CardFacing,
    CardSuit, CardValue, CardGeometry, CardColorScheme,
    MINI_GEOMETRY, POKER_GEOMETRY, CLASSIC_SCHEME,
    standard_deck, suit_subset, value_subset,
)

# ---------------------------------------------------------------------------
# Shared colour palette
# ---------------------------------------------------------------------------
BG          = ManimColor("#0C0C14")
HEART_COL   = ManimColor("#C8102E")
DIAMOND_COL = ManimColor("#E05030")
CLUB_COL    = ManimColor("#E8E8E8")
SPADE_COL   = ManimColor("#CCCCDD")
GOLD_COL    = ManimColor("#FFD700")
TEAL_COL    = ManimColor("#1D9D74")
PURPLE_COL  = ManimColor("#7F77DD")
LABEL_COL   = ManimColor("#B0AECE")

SUIT_COLORS = {
    CardSuit.HEARTS:   HEART_COL,
    CardSuit.DIAMONDS: DIAMOND_COL,
    CardSuit.CLUBS:    CLUB_COL,
    CardSuit.SPADES:   SPADE_COL,
}

# ---------------------------------------------------------------------------
# Mini card geometry — compact enough for a 4×13 grid
# ---------------------------------------------------------------------------
GRID_GEO = CardGeometry(
    width=0.50, height=0.72, thickness=0.008,
    corner_radius=0.04, pip_scale=0.55, label_scale=0.55,
    back_pattern_density=3,
)

GRID_SCHEME = CardColorScheme(
    face_bg="#FEFEFE", face_border="#BBBBBB",
    red_suit="#C8102E", black_suit="#111111",
    back_bg="#003580", back_pattern="#0050B0",
    back_border="#002060",
    highlight_ring="#FFD700",
    face_card_bg="#FFF5F5",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _p_label(num: int, denom: int, color=GOLD_COL, font_size: int = 28) -> MathTex:
    """Build a MathTex label  P = num/denom  ≈ decimal"""
    frac    = Fraction(num, denom)
    dec     = num / denom
    raw     = rf"P = \dfrac{{{frac.numerator}}}{{{frac.denominator}}} \approx {dec:.4f}"
    return MathTex(raw, font_size=font_size, color=color)


def _event_label(text: str, color=GOLD_COL, font_size: int = 24) -> Text:
    return Text(text, font_size=font_size, color=color)


def _make_grid(
    suits: list = None,
    values: list = None,
    geo: CardGeometry = GRID_GEO,
    scheme: CardColorScheme = GRID_SCHEME,
    facing: CardFacing = CardFacing.FACE_UP,
) -> tuple[VGroup, dict]:
    """
    Build a 4-row × 13-column grid of Card3D objects.

    Returns (grid_group, card_map) where card_map[(suit, value)] = Card3D.
    """
    suits  = suits  or list(CardSuit)
    values = values or list(CardValue)

    card_map: dict = {}
    grid     = VGroup()

    col_spacing = geo.width  + 0.06
    row_spacing = geo.height + 0.08

    total_w = (len(values) - 1) * col_spacing
    total_h = (len(suits)  - 1) * row_spacing

    for r, suit in enumerate(suits):
        for c, value in enumerate(values):
            face = CardFace(suit=suit, value=value)
            card = Card3D(face=face, geometry=geo, colors=scheme, facing=facing)
            x = -total_w / 2 + c * col_spacing
            y =  total_h / 2 - r * row_spacing
            card.move_to([x, y, 0])
            card_map[(suit, value)] = card
            grid.add(card)

    return grid, card_map


def _highlight_region(
    cards: list,
    color: ManimColor,
    opacity: float = 0.45,
    run_time: float = 0.6,
) -> AnimationGroup:
    """Shade a set of Card3D front faces with a tinted overlay."""
    anims = []
    for card in cards:
        anims.append(
            card.front_face.animate(run_time=run_time)
            .set_fill(color=color, opacity=opacity)
        )
    return AnimationGroup(*anims)


def _unhighlight_region(
    cards: list,
    run_time: float = 0.4,
) -> AnimationGroup:
    """Reset card front face fill to white."""
    anims = []
    for card in cards:
        anims.append(
            card.front_face.animate(run_time=run_time)
            .set_fill(color=ManimColor(GRID_SCHEME.face_bg), opacity=1.0)
        )
    return AnimationGroup(*anims)

# Scene 2 — Classical Probability (three events, grid shading)
# ===========================================================================

class ClassicalProbabilityScene(Scene):
    """
    Three events on the 52-card grid, built one at a time.

    Events
    ------
    A  =  Card is Red          P(A) = 26/52 = 1/2
    B  =  Card is an Ace       P(B) =  4/52 = 1/13
    A∩B = Card is a Red Ace    P(A∩B) = 2/52 = 1/26

    Addition rule:
        P(A∪B) = P(A) + P(B) − P(A∩B) = 26/52 + 4/52 − 2/52 = 28/52

    Render:  manim -pql card_probability_scenes.py ClassicalProbabilityScene
    """

    def construct(self):
        self.camera.background_color = BG

        title = Text(
            "Classical Probability — Three Events",
            font_size=30, color=GOLD_COL,
        ).to_edge(UP, buff=0.20)
        self.play(Write(title, run_time=0.8))

        # Build grid (smaller, left side)
        grid, card_map = _make_grid()
        grid.scale(0.75).to_edge(LEFT, buff=0.45).shift(DOWN * 0.20)
        self.play(
            LaggedStart(
                *[FadeIn(c, scale=0.75) for c in grid],
                lag_ratio=0.006, run_time=1.8,
            )
        )
        self.wait(0.3)

        # ── Right-side formula panel ──────────────────────────────────────
        panel_x = 3.6

        # ─ Event A: Red cards ─────────────────────────────────────────────
        red_suits = [CardSuit.HEARTS, CardSuit.DIAMONDS]
        red_cards = [
            card_map[(s, v)]
            for s in red_suits
            for v in CardValue
        ]
        lbl_a = MathTex(
            r"A = \text{Red card}",
            font_size=24, color=HEART_COL,
        ).move_to([panel_x, 2.0, 0])
        p_a   = _p_label(26, 52, color=HEART_COL, font_size=22)
        p_a.next_to(lbl_a, DOWN, buff=0.12)

        self.play(
            _highlight_region(red_cards, HEART_COL, 0.30),
            FadeIn(lbl_a),
        )
        self.play(Write(p_a, run_time=0.6))
        self.wait(0.5)

        # ─ Event B: Aces ───────────────────────────────────────────────────
        ace_cards = [card_map[(s, CardValue.ACE)] for s in CardSuit]
        lbl_b = MathTex(
            r"B = \text{Ace}",
            font_size=24, color=TEAL_COL,
        ).move_to([panel_x, 0.9, 0])
        p_b   = _p_label(4, 52, color=TEAL_COL, font_size=22)
        p_b.next_to(lbl_b, DOWN, buff=0.12)

        # Add teal border around aces without removing red
        ace_boxes = VGroup(*[
            SurroundingRectangle(c, color=TEAL_COL, buff=0.04,
                                 stroke_width=1.8, corner_radius=0.04)
            for c in ace_cards
        ])
        self.play(
            Create(ace_boxes, run_time=0.6),
            FadeIn(lbl_b),
        )
        self.play(Write(p_b, run_time=0.6))
        self.wait(0.5)

        # ─ Intersection A∩B: Red Aces ─────────────────────────────────────
        red_aces = [
            card_map[(s, CardValue.ACE)]
            for s in red_suits
        ]
        lbl_ab = MathTex(
            r"A \cap B = \text{Red Ace}",
            font_size=24, color=GOLD_COL,
        ).move_to([panel_x, -0.25, 0])
        p_ab   = _p_label(2, 52, color=GOLD_COL, font_size=22)
        p_ab.next_to(lbl_ab, DOWN, buff=0.12)

        self.play(
            _highlight_region(red_aces, GOLD_COL, 0.80),
            *[Indicate(c, color=GOLD_COL, scale_factor=1.25) for c in red_aces],
            FadeIn(lbl_ab),
        )
        self.play(Write(p_ab, run_time=0.6))
        self.wait(0.5)

        # ─ Addition rule ───────────────────────────────────────────────────
        add_rule = MathTex(
            r"P(A \cup B) = \frac{26}{52} + \frac{4}{52} - \frac{2}{52} = \frac{28}{52}",
            font_size=20, color=PURPLE_COL,
        ).move_to([panel_x, -1.55, 0])
        box_rule = SurroundingRectangle(
            add_rule, color=PURPLE_COL, buff=0.12, corner_radius=0.08
        )
        self.play(Write(add_rule, run_time=1.0))
        self.play(Create(box_rule, run_time=0.5))
        self.wait(2.0)


