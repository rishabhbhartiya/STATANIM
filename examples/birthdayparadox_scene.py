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


# Scene 5 — Birthday Paradox
# ===========================================================================

class BirthdayParadoxScene(Scene):
    """
    Birthday paradox via cards (52 cards = 52 "birthdays").

    Each card represents a unique birthday slot.
    Cards are dealt face-up one at a time.
    The moment a *suit repeats* (same suit as a previous card), the
    collision is flagged — this mimics the birthday collision but
    at suit level so it happens fast and visually.

    A live probability curve P(collision by draw k) is built on the
    right as cards are dealt.

    The classic birthday problem formula is shown alongside.

    Render:  manim -pql card_probability_scenes.py BirthdayParadoxScene
    """

    def construct(self):
        self.camera.background_color = BG

        # ── Title ─────────────────────────────────────────────────────────
        title = Text(
            "The Birthday Paradox",
            font_size=32, color=GOLD_COL,
        ).to_edge(UP, buff=0.22)
        subtitle = Text(
            "Suits as birthday 'categories' — when does the first repeat occur?",
            font_size=17, color=LABEL_COL,
        ).next_to(title, DOWN, buff=0.10)
        self.play(Write(title, run_time=0.7))
        self.play(FadeIn(subtitle, run_time=0.5))
        self.wait(0.3)

        # ── Birthday problem formula panel ────────────────────────────────
        formula_title = MathTex(
            r"\text{Classic: } n \text{ people, } 365 \text{ days}",
            font_size=18, color=LABEL_COL,
        ).move_to([4.2, 1.8, 0])
        formula_p = MathTex(
            r"P(\text{collision}) = 1 - \frac{365!}{(365-n)!\cdot 365^n}",
            font_size=16, color=PURPLE_COL,
        ).next_to(formula_title, DOWN, buff=0.14)
        formula_note = Text(
            "Here: 4 suits instead of 365 days\n— same paradox, faster demo",
            font_size=14, color=LABEL_COL,
        ).next_to(formula_p, DOWN, buff=0.14)

        panel_bg = RoundedRectangle(
            width=3.6, height=2.6,
            corner_radius=0.12,
            fill_color=ManimColor("#101020"),
            fill_opacity=0.85,
            stroke_color=PURPLE_COL,
            stroke_width=1.2,
        ).move_to([4.2, 1.2, 0])
        self.play(FadeIn(panel_bg))
        self.play(
            Write(formula_title, run_time=0.6),
            Write(formula_p, run_time=0.8),
        )
        self.play(FadeIn(formula_note))
        self.wait(0.3)

        # ── Probability curve axes (right lower) ──────────────────────────
        # P(at least one suit repeat in first k draws)
        # For 4 suits: P(collision by draw k) = 1 - 4!/((4-min(k,4))! * 4^k) ... approx
        # We'll compute it exactly using inclusion-exclusion / simulation
        def p_suit_collision(k: int, n_suits: int = 4) -> float:
            """P(at least one repeated suit in k draws)."""
            if k <= 1:
                return 0.0
            # P(no repeat) = n_suits/n_suits * (n_suits-1)/n_suits * ... for min(k,n_suits) draws
            # Once k > n_suits, collision is certain
            if k > n_suits:
                return 1.0
            p_no_repeat = 1.0
            for i in range(k):
                p_no_repeat *= max(0, n_suits - i) / n_suits
            return 1.0 - p_no_repeat

        max_draws = 7
        curve_ox  = 2.2
        curve_oy  = -2.2
        curve_w   = 3.8
        curve_h   = 1.6

        curve_ax_x = Line(
            [curve_ox, curve_oy, 0],
            [curve_ox + curve_w + 0.2, curve_oy, 0],
            color=LABEL_COL, stroke_width=1.2,
        )
        curve_ax_y = Line(
            [curve_ox, curve_oy, 0],
            [curve_ox, curve_oy + curve_h + 0.2, 0],
            color=LABEL_COL, stroke_width=1.2,
        )
        curve_xlabel = Text("draws k", font_size=13, color=LABEL_COL)
        curve_xlabel.next_to(curve_ax_x, RIGHT, buff=0.08)
        curve_ylabel = MathTex(r"P(\text{collision})", font_size=13, color=LABEL_COL)
        curve_ylabel.next_to(curve_ax_y, UP, buff=0.06)

        self.play(
            Create(curve_ax_x), Create(curve_ax_y),
            FadeIn(curve_xlabel), FadeIn(curve_ylabel),
        )

        # Draw x tick labels
        for k in range(1, max_draws + 1):
            px = curve_ox + (k - 1) / (max_draws - 1) * curve_w
            lbl = Text(str(k), font_size=11, color=LABEL_COL)
            lbl.move_to([px, curve_oy - 0.18, 0])
            self.add(lbl)

        # ── Deal cards from shuffled deck ─────────────────────────────────
        seed           = 42
        deck_faces     = standard_deck(shuffle=True, seed=seed)
        n_deal         = 6          # deal at most 6 cards

        slot_geo = CardGeometry(
            width=0.70, height=1.00, thickness=0.010,
            corner_radius=0.05, pip_scale=0.65, label_scale=0.65,
            back_pattern_density=3,
        )
        slot_xs = np.linspace(-5.0, 0.8, n_deal)
        slot_y  = -0.45

        deck_mob = Deck3D(
            cards          = deck_faces[n_deal:],
            geometry       = MINI_GEOMETRY,
            initial_facing = CardFacing.FACE_DOWN,
        ).scale(0.75).move_to([-5.8, slot_y, 0])
        self.play(FadeIn(deck_mob, run_time=0.5))

        seen_suits:   set              = set()
        curve_dots:   List             = []
        curve_lines:  List             = []
        collision_k:  Optional[int]    = None

        k_label = MathTex(r"k = 0", font_size=20, color=LABEL_COL)
        k_label.move_to([-4.5, -1.85, 0])
        self.play(FadeIn(k_label))

        for i in range(n_deal):
            face = deck_faces[i]
            card = Card3D(
                face     = face,
                geometry = slot_geo,
                colors   = CLASSIC_SCHEME,
                facing   = CardFacing.FACE_DOWN,
            ).move_to([slot_xs[i], slot_y, 0])
            self.add(card)

            # Deal arc
            self.play(
                card.deal_anim(
                    target    = np.array([slot_xs[i], slot_y, 0]),
                    run_time  = 0.38,
                    arc_height= 0.7,
                )
            )

            # Flip face-up
            self.play(card.flip_to_face_up(run_time=0.45))

            k = i + 1
            new_k_label = MathTex(rf"k = {k}", font_size=20, color=LABEL_COL)
            new_k_label.move_to(k_label.get_center())
            self.play(Transform(k_label, new_k_label, run_time=0.2))

            # Check for collision
            suit = face.suit
            is_collision = (suit in seen_suits) and (collision_k is None)

            if is_collision:
                collision_k = k
                # Find previous card with same suit
                for prev_i in range(i):
                    if deck_faces[prev_i].suit == suit:
                        # Highlight both
                        self.play(
                            Flash(card, color=HEART_COL, flash_radius=0.5),
                            Flash(card, color=GOLD_COL,  flash_radius=0.7),
                        )
                        collision_banner = Text(
                            f"First repeat: draw {k}  (suit = {suit.symbol})",
                            font_size=20, color=GOLD_COL,
                        ).move_to([0.0, -1.85, 0])
                        self.play(Write(collision_banner, run_time=0.6))
                        break

            seen_suits.add(suit)

            # Update probability curve dot
            p_col = p_suit_collision(k, n_suits=4)
            dot_x = curve_ox + (k - 1) / (max_draws - 1) * curve_w
            dot_y = curve_oy + p_col * curve_h

            dot = Dot([dot_x, dot_y, 0], radius=0.06,
                      color=TEAL_COL if not is_collision else GOLD_COL)
            self.play(FadeIn(dot, scale=1.4, run_time=0.25))
            curve_dots.append((dot_x, dot_y))

            # Connect with line
            if len(curve_dots) >= 2:
                seg = Line(
                    [curve_dots[-2][0], curve_dots[-2][1], 0],
                    [dot_x, dot_y, 0],
                    color=TEAL_COL, stroke_width=2.0,
                )
                self.play(Create(seg, run_time=0.2))

            if is_collision:
                break

        # ── Final annotation ──────────────────────────────────────────────
        if collision_k is not None:
            p_val = p_suit_collision(collision_k, n_suits=4)
            final = MathTex(
                rf"P(\text{{collision by draw }} {collision_k}) = {p_val:.3f}",
                font_size=20, color=GOLD_COL,
            ).to_edge(DOWN, buff=0.18)
        else:
            final = Text(
                "No collision in these 6 draws.",
                font_size=20, color=LABEL_COL,
            ).to_edge(DOWN, buff=0.18)

        self.play(Write(final, run_time=0.8))
        self.wait(2.0)