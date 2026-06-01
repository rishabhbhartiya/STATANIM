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


# ===========================================================================
# Scene 1 — Sample Space
# ===========================================================================

class SampleSpaceScene(Scene):
    """
    The 52-card sample space.

    Visual structure
    ----------------
    - Full 4×13 grid of face-up cards.
    - Title: "The 52-Card Sample Space".
    - Suit labels on the left (♥ ♦ ♣ ♠).
    - Value labels on the top (A 2 3 … K).
    - Hearts row highlighted in red.
    - P(♥) label animates in.
    - Generalises: any single suit has P = 13/52 = 1/4.

    Render:  manim -pql card_probability_scenes.py SampleSpaceScene
    """

    def construct(self):
        self.camera.background_color = BG

        # ── Title ────────────────────────────────────────────────────────
        title = Text(
            "The 52-Card Sample Space",
            font_size = 32,
            color     = GOLD_COL,
        ).to_edge(UP, buff=0.25)
        self.play(Write(title, run_time=1.0))
        self.wait(0.3)

        # ── Build grid ───────────────────────────────────────────────────
        grid, card_map = _make_grid()
        grid.scale(0.88).shift(DOWN * 0.15)
        self.play(
            LaggedStart(
                *[FadeIn(card, scale=0.8) for card in grid],
                lag_ratio = 0.008,
                run_time  = 2.2,
            )
        )
        self.wait(0.4)

        # ── Suit row labels ───────────────────────────────────────────────
        suit_symbols = {
            CardSuit.HEARTS:   ("♥", HEART_COL),
            CardSuit.DIAMONDS: ("♦", DIAMOND_COL),
            CardSuit.CLUBS:    ("♣", CLUB_COL),
            CardSuit.SPADES:   ("♠", SPADE_COL),
        }
        suits = list(CardSuit)
        geo   = GRID_GEO
        row_h = geo.height + 0.08

        # Compute y positions from grid
        sample_cards = [card_map[(s, CardValue.ACE)] for s in suits]
        suit_labels  = VGroup()
        for i, (suit, card) in enumerate(zip(suits, sample_cards)):
            sym, col = suit_symbols[suit]
            lbl = Text(sym, font_size=22, color=col)
            lbl.next_to(card, LEFT, buff=0.18)
            suit_labels.add(lbl)

        self.play(LaggedStart(
            *[FadeIn(l) for l in suit_labels],
            lag_ratio=0.15, run_time=0.8,
        ))

        # Value labels on top
        value_labels = VGroup()
        for value in CardValue:
            sample_card = card_map[(CardSuit.SPADES, value)]
            lbl = Text(value.rank_str, font_size=13, color=LABEL_COL)
            lbl.next_to(sample_card, UP, buff=0.10)
            value_labels.add(lbl)

        self.play(LaggedStart(
            *[FadeIn(l) for l in value_labels],
            lag_ratio=0.04, run_time=0.7,
        ))
        self.wait(0.5)

        # ── n = 52 label ─────────────────────────────────────────────────
        n_label = MathTex(
            r"|S| = 52 \text{ equally likely outcomes}",
            font_size=22, color=LABEL_COL,
        ).to_edge(DOWN, buff=0.28)
        self.play(Write(n_label, run_time=0.7))
        self.wait(0.5)

        # ── Highlight Hearts row ──────────────────────────────────────────
        heart_cards = [card_map[(CardSuit.HEARTS, v)] for v in CardValue]

        heart_box = SurroundingRectangle(
            VGroup(*heart_cards),
            color       = HEART_COL,
            buff        = 0.06,
            stroke_width= 2.2,
            corner_radius=0.06,
        )
        event_lbl = Text(
            "Event A: card is a Heart",
            font_size=22, color=HEART_COL,
        ).next_to(heart_box, RIGHT, buff=0.22)

        self.play(
            _highlight_region(heart_cards, HEART_COL, opacity=0.35),
            Create(heart_box, run_time=0.6),
        )
        self.play(FadeIn(event_lbl))
        self.wait(0.4)

        # P(Heart) label
        p_heart = _p_label(13, 52, color=HEART_COL, font_size=26)
        p_heart.next_to(event_lbl, DOWN, buff=0.18)
        self.play(Write(p_heart, run_time=0.8))
        self.wait(0.5)

        # ── Generalise: any suit ──────────────────────────────────────────
        general = MathTex(
            r"P(\text{any one suit}) = \frac{13}{52} = \frac{1}{4}",
            font_size=24, color=GOLD_COL,
        ).next_to(p_heart, DOWN, buff=0.20)
        self.play(Write(general, run_time=0.8))
        self.wait(2.0)

