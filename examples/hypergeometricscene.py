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


# Scene 4 — Hypergeometric Distribution
# ===========================================================================

class HypergeometricScene(Scene):
    """
    X ~ Hypergeometric(N=52, K=13, n=5) — Hearts in 5 draws.

    Visual flow
    -----------
    1. Title and distribution parameters displayed.
    2. Deck stack shown centre-left.
    3. Five cards dealt face-down to a row.
    4. Cards flipped one by one; Heart count tracked live.
    5. PMF bar chart builds in real-time on the right.
    6. After the draw, the observed bar is highlighted.

    Render:  manim -pql card_probability_scenes.py HypergeometricScene
    """

    def construct(self):
        self.camera.background_color = BG

        # ── Title + parameters ────────────────────────────────────────────
        title = Text(
            "Hypergeometric Distribution",
            font_size=30, color=GOLD_COL,
        ).to_edge(UP, buff=0.20)
        params = MathTex(
            r"X \sim \mathrm{Hypergeometric}(N=52,\; K=13,\; n=5)",
            font_size=22, color=LABEL_COL,
        ).next_to(title, DOWN, buff=0.12)
        meaning = Text(
            "X = number of Hearts in 5 draws (without replacement)",
            font_size=17, color=LABEL_COL,
        ).next_to(params, DOWN, buff=0.08)

        self.play(Write(title, run_time=0.7))
        self.play(Write(params, run_time=0.7))
        self.play(FadeIn(meaning, run_time=0.5))
        self.wait(0.4)

        # ── Deck stack ────────────────────────────────────────────────────
        rng          = random.Random(7)
        deck_faces   = standard_deck(shuffle=True, seed=7)
        draw_faces   = deck_faces[:5]

        deck = Deck3D(
            cards          = deck_faces[5:],
            geometry       = MINI_GEOMETRY,
            initial_facing = CardFacing.FACE_DOWN,
        ).scale(0.85).move_to([-4.8, -0.3, 0])
        deck_label = Text("Deck  (52 cards)", font_size=16, color=LABEL_COL)
        deck_label.next_to(deck, DOWN, buff=0.14)

        self.play(FadeIn(deck, run_time=0.6))
        self.play(FadeIn(deck_label))

        # ── Deal row: 5 slots ─────────────────────────────────────────────
        slot_geo = CardGeometry(
            width=0.80, height=1.14, thickness=0.012,
            corner_radius=0.06, pip_scale=0.72, label_scale=0.72,
            back_pattern_density=3,
        )
        slot_x   = np.linspace(-2.0, 2.0, 5)
        slot_y   = -0.30

        # Build face-down cards for the deal
        dealt_cards = []
        for i, face in enumerate(draw_faces):
            card = Card3D(
                face     = face,
                geometry = slot_geo,
                colors   = CLASSIC_SCHEME,
                facing   = CardFacing.FACE_DOWN,
            ).move_to([slot_x[i], slot_y, 0])
            dealt_cards.append(card)

        # Deal animation (arc from deck to slot)
        deal_anims = []
        for i, card in enumerate(dealt_cards):
            self.add(card)
            deal_anims.append(
                card.deal_anim(
                    target    = np.array([slot_x[i], slot_y, 0]),
                    run_time  = 0.4,
                    arc_height= 0.9,
                )
            )
        self.play(LaggedStart(*deal_anims, lag_ratio=0.18))
        self.wait(0.4)

        # ── PMF panel (right side) ────────────────────────────────────────
        # Hypergeometric PMF: P(X=k) = C(K,k)*C(N-K,n-k) / C(N,n)
        from math import comb
        N, K, n = 52, 13, 5
        pmf = {k: comb(K, k) * comb(N-K, n-k) / comb(N, n) for k in range(6)}

        bar_w    = 0.38
        bar_gap  = 0.12
        max_h    = 2.0
        max_p    = max(pmf.values())
        bar_origin_x = 4.0
        bar_origin_y = -1.9

        # Axis
        ax_x = Line(
            [bar_origin_x - 0.2, bar_origin_y, 0],
            [bar_origin_x + (6 * (bar_w + bar_gap)) + 0.1, bar_origin_y, 0],
            color=LABEL_COL, stroke_width=1.4,
        )
        ax_y = Line(
            [bar_origin_x - 0.2, bar_origin_y, 0],
            [bar_origin_x - 0.2, bar_origin_y + max_h + 0.3, 0],
            color=LABEL_COL, stroke_width=1.4,
        )
        ax_title = MathTex(r"P(X=k)", font_size=18, color=LABEL_COL)
        ax_title.move_to([bar_origin_x + 1.5, bar_origin_y + max_h + 0.35, 0])

        self.play(Create(ax_x), Create(ax_y), FadeIn(ax_title))

        # Build bars
        bars: dict = {}
        k_labels: dict = {}
        for k in range(6):
            p   = pmf[k]
            h   = (p / max_p) * max_h
            bx  = bar_origin_x + k * (bar_w + bar_gap)
            bar = Rectangle(
                width=bar_w, height=h,
                fill_color   = ManimColor("#185FA5"),
                fill_opacity = 0.82,
                stroke_width = 0,
            ).move_to([bx, bar_origin_y + h / 2, 0])
            k_lbl = MathTex(str(k), font_size=18, color=LABEL_COL)
            k_lbl.move_to([bx, bar_origin_y - 0.22, 0])
            bars[k]    = bar
            k_labels[k] = k_lbl

        self.play(
            LaggedStart(
                *[FadeIn(l) for l in k_labels.values()],
                lag_ratio=0.1, run_time=0.5,
            )
        )

        # ── Flip cards one by one, build PMF ─────────────────────────────
        heart_count = 0
        count_mob   = MathTex(
            r"\text{Hearts: } 0",
            font_size=24, color=HEART_COL,
        ).move_to([-4.0, -1.85, 0])
        self.play(FadeIn(count_mob))

        for i, card in enumerate(dealt_cards):
            # Flip
            self.play(card.flip_to_face_up(run_time=0.55))
            self.wait(0.15)

            # Check if Heart
            is_heart = draw_faces[i].suit == CardSuit.HEARTS
            if is_heart:
                heart_count += 1
                self.play(Flash(card, color=HEART_COL, flash_radius=0.5))

            # Update counter
            new_count_mob = MathTex(
                rf"\text{{Hearts: }} {heart_count}",
                font_size=24, color=HEART_COL,
            ).move_to(count_mob.get_center())
            self.play(Transform(count_mob, new_count_mob, run_time=0.3))

        # Draw all PMF bars now (after reveal)
        self.play(
            LaggedStart(
                *[Create(bar) for bar in bars.values()],
                lag_ratio=0.08, run_time=1.2,
            )
        )

        # Highlight the observed bar
        obs_bar = bars[heart_count]
        self.play(
            obs_bar.animate.set_fill(color=GOLD_COL, opacity=0.95),
            Indicate(obs_bar, color=GOLD_COL, scale_factor=1.10),
        )

        # Show the PMF value
        p_obs = pmf[heart_count]
        p_obs_lbl = MathTex(
            rf"P(X={heart_count}) = {p_obs:.4f}",
            font_size=20, color=GOLD_COL,
        ).next_to(obs_bar, UP, buff=0.10)
        self.play(Write(p_obs_lbl, run_time=0.6))
        self.wait(2.0)


