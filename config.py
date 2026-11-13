"""Central, typed design parameters for the white-painted cedar Adirondack armchair.

An LLM or human author should put user-editable dimensions, material choices,
colors, clearances, and layout values in this module.  Geometry belongs in
``models/starter_model.py`` and drawing-only presentation belongs in
``drawing_annotations.py``.

Prefer values carrying a unit (for example ``12 * INCH``) over bare numbers.
Keep one authoritative value for each design decision and derive related
values from it so later edits cannot silently make the model inconsistent.
"""

import math

from python_cad_tools.units import INCH, to_mm

PROJECT_NAME = "deck-adirondack-chair"


# ── Overall datums and extents ───────────────────────────────────────────────

# The chair is centred on X = 0 and spans exactly -OVERALL_WIDTH/2 .. +OVERALL_WIDTH/2
# (the outer edges of the two armrest planks).  X is width, Y is depth/rear, Z is up.
OVERALL_WIDTH = to_mm(30 * INCH)
OVERALL_HEIGHT = to_mm(36 * INCH)
# Height in Z of the seat surface (top of the forward seat slat) above the ground.
SEAT_TOP_Z = to_mm(15 * INCH)

# Common board thickness used for all slats, planks and rails.
BOARD_THICKNESS = to_mm(0.75 * INCH)


# ── Backrest (slanted slatted back) ──────────────────────────────────────────

# Lean of the back boards away from vertical, degrees (top sits rearward of bottom).
BACK_LEAN_DEG = 15.0
BACK_BOARD_COUNT = 5
BACK_BOARD_WIDTH = to_mm(24 * INCH)  # X span of each horizontal back board
BACK_BOARD_HEIGHT = to_mm(4 * INCH)  # Z height of each board (before leaning)
BACK_BOARD_GAP = to_mm(1 * INCH)  # gap between adjacent boards
# Y centre of the lowest back board (the rear-most region of the seat frame).
BACK_Y_BASE = to_mm(17 * INCH)
# Z centre of the lowest back board, derived so the top board's top corner
# lands exactly on OVERALL_HEIGHT after the lean back angle (which lifts the
# forward top corner of the board's width by half the board thickness).
_LEAN_COS = math.cos(math.radians(BACK_LEAN_DEG))
_LEAN_SIN = math.sin(math.radians(BACK_LEAN_DEG))
BACK_Z_BASE = (
    OVERALL_HEIGHT
    - (BACK_BOARD_COUNT - 1) * (BACK_BOARD_HEIGHT + BACK_BOARD_GAP) * _LEAN_COS
    - (BACK_BOARD_HEIGHT / 2) * _LEAN_COS
    - (BOARD_THICKNESS / 2) * _LEAN_SIN
)


# ── Back support rails ───────────────────────────────────────────────────────

BACK_RAIL_SECTION = to_mm(1.5 * INCH)  # square cross-section of each rail
BACK_RAIL_X = to_mm(11.5 * INCH)  # X offset of each rail centre (behind outer board ends)
BACK_RAIL_TOP_Z = to_mm(34 * INCH)  # top of the lean line near the upper boards
BACK_RAIL_BOT_Z = to_mm(16 * INCH)  # bottom of the lean line at the rear seat frame
BACK_RAIL_TOP_Y = to_mm(23.5 * INCH)  # Y of the lean line top, just behind the upper boards


# ── Seat (slatted, rearward-sloping) ─────────────────────────────────────────

SEAT_SLAT_COUNT = 5
SEAT_WIDTH = to_mm(26 * INCH)  # X span of each transverse seat slat
SEAT_SLAT_DEPTH = to_mm(4 * INCH)  # Y depth of each seat slat
SEAT_SLAT_GAP = to_mm(0.5 * INCH)  # gap between adjacent seat slats
SEAT_SLOPE_DEG = 5.0  # downward slope towards the rear of the seat
SEAT_SLAT_FRONT_Y = to_mm(6 * INCH)  # Y centre of the forward-most seat slat
# Z of the forward seat slat top (the seat surface); SEAT_TOP_Z exactly.
SEAT_FRONT_Z = SEAT_TOP_Z
# Two rails running front-to-back beneath the seat edges.
SEAT_SIDE_RAIL_X = to_mm(12 * INCH)
SEAT_SIDE_RAIL_Y = to_mm(11 * INCH)  # half-length of each side rail (rail length = 2 * this)
SEAT_RAIL_CENTER_Y = to_mm(15 * INCH)  # Y centre of the side rails
SEAT_SIDE_RAIL_HEIGHT = to_mm(2 * INCH)  # Z height of each side rail
SEAT_SIDE_RAIL_Z = to_mm(12.5 * INCH)  # Z centre of each side rail


# ── Armrests (wide flat planks) ──────────────────────────────────────────────

ARM_WIDTH = to_mm(3.5 * INCH)  # X width of each armrest plank
ARM_LENGTH = to_mm(18 * INCH)  # Y length of each armrest plank
ARM_THICKNESS = to_mm(1.5 * INCH)  # Z thickness of each armrest plank
ARM_HEIGHT = to_mm(24.5 * INCH)  # Z of the armrest top above the ground
# X of the armrest outer edge; set to OVERALL_WIDTH / 2 so the pair defines the
# stated 30 in overall width exactly.
ARM_X_OUTER = OVERALL_WIDTH / 2
ARM_CENTER_Y = to_mm(4.5 * INCH)  # Y centre of each armrest plank


# ── Front posts and gusset brackets ──────────────────────────────────────────

FRONT_POST_THICKNESS = to_mm(1.5 * INCH)  # X section of each front post
FRONT_POST_WIDTH = to_mm(1.5 * INCH)  # Y section of each front post
FRONT_POST_X = to_mm(13 * INCH)  # X centre of each front post
FRONT_POST_Y = to_mm(8 * INCH)  # Y centre of each front post

# Tapered gusset plates under the arms at the front posts.
ARM_BRACKET_THICKNESS = BOARD_THICKNESS
ARM_BRACKET_X = to_mm(12 * INCH)  # X centre of each bracket plate
BRACKET_Z_TOP = ARM_HEIGHT - ARM_THICKNESS  # top edge fits under the armrest underside
BRACKET_Y_FRONT = to_mm(6.5 * INCH)
BRACKET_Y_REAR = to_mm(9.5 * INCH)
BRACKET_Z_FRONT_BOT = to_mm(18 * INCH)
BRACKET_Z_REAR_BOT = to_mm(20 * INCH)


# ── Front apron and lower rear brace ─────────────────────────────────────────

APRON_WIDTH_X = to_mm(24 * INCH)  # X span of the front apron (between the posts)
APRON_DEPTH_Y = to_mm(1.5 * INCH)
APRON_HEIGHT_Z = to_mm(6 * INCH)
APRON_Y = to_mm(7 * INCH)  # Y centre of the apron, just forward of the posts
APRON_Z = to_mm(8 * INCH)  # Z centre of the apron

BRACE_WIDTH_X = to_mm(24 * INCH)  # X span of the low rear brace
BRACE_DEPTH_Y = to_mm(1.5 * INCH)
BRACE_HEIGHT_Z = to_mm(2 * INCH)
BRACE_Y = to_mm(23 * INCH)  # Y centre of the brace at the rear legs
BRACE_Z = to_mm(4 * INCH)  # Z centre of the brace, low beneath the seat


# ── Rear legs (feet splaying backward) ───────────────────────────────────────

REAR_LEG_THICKNESS_X = to_mm(1.5 * INCH)
REAR_LEG_DEPTH_Y = to_mm(1.5 * INCH)
REAR_LEG_X = to_mm(12.5 * INCH)  # X centre of each rear leg
REAR_LEG_TOP_Y = to_mm(20 * INCH)  # Y of the leg top (under the rear seat frame)
REAR_LEG_FOOT_Y = to_mm(26 * INCH)  # Y of the splayed-back foot
REAR_LEG_TOP_Z = to_mm(24 * INCH)  # Z of the leg top above the ground


# ── Footrest (low cedar ottoman) ─────────────────────────────────────────────

# A separate low cedar footrest placed in front of the chair on its negative-Y
# (front) side, a short gap beyond the armrests.  Top planform about 18 in (X)
# by 14 in (Y), height low so it sits near the chair's seat-side rails.
FOOTREST_WIDTH_X = to_mm(18 * INCH)  # X span of the slatted top
FOOTREST_HEIGHT_Z = to_mm(11 * INCH)  # Z of the top surface above the ground
FOOTREST_CENTER_Y = to_mm(-14 * INCH)  # Y centre, just in front of the armrests

# Transverse top slats spanning X, spaced across the Y planform.
FOOT_SLAT_COUNT = 4
FOOT_SLAT_DEPTH = to_mm(3.25 * INCH)  # Y depth of each top slat
FOOT_SLAT_GAP = to_mm(0.25 * INCH)  # gap between adjacent top slats

# Four splayed legs rising from the ground to just under the top edges.
FOOT_LEG_SECTION = to_mm(1.5 * INCH)  # square cross-section of each leg
FOOT_LEG_TOP_X = to_mm(6.5 * INCH)  # X centre of each leg top under a slat end
FOOT_LEG_FOOT_SPLAY_X = to_mm(1.5 * INCH)  # outward X splay of each foot
FOOT_LEG_INSET_Y = to_mm(1.5 * INCH)  # Y inset of the front/rear legs from the edge

# Derived placement values (kept in config so starter_model.py holds no literals).
_foot_total_depth = FOOT_SLAT_COUNT * FOOT_SLAT_DEPTH + (FOOT_SLAT_COUNT - 1) * FOOT_SLAT_GAP
FOOT_TOP_TOTAL_DEPTH = _foot_total_depth  # overall Y depth of the slatted top
FOOT_SLAT_START_Y = FOOTREST_CENTER_Y - _foot_total_depth / 2 + FOOT_SLAT_DEPTH / 2
FOOT_LEG_Z_UNDER = FOOTREST_HEIGHT_Z - BOARD_THICKNESS  # top of legs just under the slats
FOOT_LEG_Y_REAR = FOOTREST_CENTER_Y - _foot_total_depth / 2 + FOOT_LEG_INSET_Y
FOOT_LEG_Y_FRONT = FOOTREST_CENTER_Y + _foot_total_depth / 2 - FOOT_LEG_INSET_Y


# ── White painted cedar material ─────────────────────────────────────────────

# Unified finish for every chair part: the cedar painted a clean off-white.
# Paint only changes the appearance, so the cedar density is unchanged.
MATERIAL_ID = "deck.adirondack.chair.material.white_painted_cedar"
MATERIAL_NAME = "White Painted Cedar"
MATERIAL_CATEGORY = "painted cedar"
MATERIAL_COLOR = (0.95, 0.95, 0.93)  # off-white paint
MATERIAL_DENSITY_KG_M3 = 380.0
