"""White-painted cedar Adirondack armchair geometry.

``python-cad`` calls :func:`build_model` with a :class:`BuildContext`; that
entry point returns the project's one ``DesignModel``.  This module builds the
Adirondack armchair from the typed parameters in ``config.py``:

* a rearward-leaning backrest of five broad horizontal boards on two support
  rails,
* a shallow, rearward-sloping seat of five transverse slats on two side rails,
* two wide flat armrest planks resting on two front posts,
* gusset brackets under the arms at the front posts,
* a broad front apron spanning between the front posts,
* two rear legs with splayed-back feet and a low rear brace,
* a matching low footrest (slatted top on four splayed legs) set out
  in front of the chair, painted in the same white finish.

Every part is a single connected solid placed in world coordinates so that
``python-cad validate`` accepts the model and keeps STEP solids in one-to-one
correspondence with physical element ids.
"""

from __future__ import annotations

import math

from build123d import Axis, Location, Polyline, extrude, make_face
from python_cad_tools.context import BuildContext
from python_cad_tools.elements import (
    DesignElement,
    DesignModel,
    Dimensions,
    IfcMapping,
    MaterialSpec,
)
from python_cad_tools.geometry import box
from python_cad_tools.units import mm

import config as cfg

_LEAN_RAD = math.radians(cfg.BACK_LEAN_DEG)
_SIN = math.sin(_LEAN_RAD)
_COS = math.cos(_LEAN_RAD)

_DIMENSIONS = (
    cfg.BACK_BOARD_WIDTH,
    cfg.BOARD_THICKNESS,
    cfg.BACK_BOARD_HEIGHT,
)

_MATERIAL = MaterialSpec(
    id=cfg.MATERIAL_ID,
    name=cfg.MATERIAL_NAME,
    category=cfg.MATERIAL_CATEGORY,
    color_rgb=cfg.MATERIAL_COLOR,
    density_kg_m3=cfg.MATERIAL_DENSITY_KG_M3,
)

_IFC = IfcMapping("IfcBuildingElementProxy", "ELEMENT")

_ID_PREFIX = "deck.adirondack.chair"


def _plain_box(lx: float, ly: float, lz: float, center: tuple[float, float, float]):
    """An axis-aligned box built in place with ``center`` as its mid point."""
    return box(
        mm(lx),
        mm(ly),
        mm(lz),
        origin=(mm(center[0] - lx / 2), mm(center[1] - ly / 2), mm(center[2] - lz / 2)),
    )


def _lean_box(lx: float, ly: float, lz: float, lean_deg: float, center: tuple[float, float, float]):
    """A box leaning ``lean_deg`` about X, built in place with ``center`` as its mid point."""
    solid = box(
        mm(lx),
        mm(ly),
        mm(lz),
        origin=(mm(-lx / 2), mm(-ly / 2), mm(-lz / 2)),
    )
    solid = solid.rotate(Axis.X, lean_deg)
    return solid.moved(Location((center[0], center[1], center[2])))


def _splay_box(lx: float, ly: float, lz: float, splay_deg: float, center: tuple[float, float, float]):
    """A box splaying ``splay_deg`` about Y, built in place with ``center`` as its mid point."""
    solid = box(
        mm(lx),
        mm(ly),
        mm(lz),
        origin=(mm(-lx / 2), mm(-ly / 2), mm(-lz / 2)),
    )
    solid = solid.rotate(Axis.Y, splay_deg)
    return solid.moved(Location((center[0], center[1], center[2])))


def _element(
    element_id: str,
    name: str,
    category: str,
    geometry,
    length_mm: float,
    width_mm: float,
    height_mm: float,
) -> DesignElement:
    """Package one physical solid into a DesignElement with full metadata."""
    return DesignElement(
        id=f"{_ID_PREFIX}.{element_id}",
        name=name,
        category=category,
        geometry=geometry,
        geometry_kind="solid",
        dimensions=Dimensions(length_mm=length_mm, width_mm=width_mm, height_mm=height_mm),
        material=_MATERIAL,
        ifc_mapping=_IFC,
    )


def _back_boards() -> list[DesignElement]:
    """Five straight-topped horizontal boards leaning back about 15 degrees."""
    pitch = cfg.BACK_BOARD_HEIGHT + cfg.BACK_BOARD_GAP
    elements = []
    for index in range(cfg.BACK_BOARD_COUNT):
        step = (cfg.BACK_BOARD_COUNT - 1 - index) * pitch
        center = (0.0, cfg.BACK_Y_BASE + step * _SIN, cfg.BACK_Z_BASE + step * _COS)
        geometry = _lean_box(*_DIMENSIONS, -cfg.BACK_LEAN_DEG, center)
        elements.append(
            _element(
                f"back.board.{index + 1}",
                f"Back Board {index + 1}",
                "backrest",
                geometry,
                *_DIMENSIONS,
            )
        )
    return elements


def _back_support_rails() -> list[DesignElement]:
    """Two narrow rails behind the outer back-board ends along the back inclination."""
    # Extend the back lean line from the top board down to the rear side frame.
    lean_length = (cfg.BACK_RAIL_TOP_Z - cfg.BACK_RAIL_BOT_Z) / _COS
    bottom_y = cfg.BACK_RAIL_TOP_Y - lean_length * _SIN
    center = (
        (cfg.BACK_RAIL_TOP_Y + bottom_y) / 2,
        (cfg.BACK_RAIL_TOP_Z + cfg.BACK_RAIL_BOT_Z) / 2,
    )
    results = []
    for side, name in ((-1, "left"), (1, "right")):
        geometry = _lean_box(
            cfg.BACK_RAIL_SECTION,
            cfg.BACK_RAIL_SECTION,
            lean_length,
            -cfg.BACK_LEAN_DEG,
            (side * cfg.BACK_RAIL_X, *center),
        )
        results.append(
            _element(
                f"back.support.rail.{name}",
                f"Back Support Rail ({name})",
                "backrest support",
                geometry,
                cfg.BACK_RAIL_SECTION,
                cfg.BACK_RAIL_SECTION,
                lean_length,
            )
        )
    return results


def _seat_slats() -> list[DesignElement]:
    """Five closely spaced transverse seat slats on a shallow rearward slope."""
    pitch = cfg.SEAT_SLAT_DEPTH + cfg.SEAT_SLAT_GAP
    slope_sin = math.sin(math.radians(cfg.SEAT_SLOPE_DEG))
    elements = []
    for index in range(cfg.SEAT_SLAT_COUNT):
        y = cfg.SEAT_SLAT_FRONT_Y + index * pitch
        z = cfg.SEAT_FRONT_Z - cfg.BOARD_THICKNESS / 2 - index * pitch * slope_sin
        geometry = _plain_box(cfg.SEAT_WIDTH, cfg.SEAT_SLAT_DEPTH, cfg.BOARD_THICKNESS, (0.0, y, z))
        elements.append(
            _element(
                f"seat.slat.{index + 1}",
                f"Seat Slat {index + 1}",
                "seat",
                geometry,
                cfg.SEAT_WIDTH,
                cfg.SEAT_SLAT_DEPTH,
                cfg.BOARD_THICKNESS,
            )
        )
    return elements


def _side_seat_rails() -> list[DesignElement]:
    """Two side seat rails running front-to-back beneath the seat edges."""
    rail_ly = 2 * cfg.SEAT_SIDE_RAIL_Y
    results = []
    for side, name in ((-1, "left"), (1, "right")):
        geometry = _plain_box(
            cfg.BACK_RAIL_SECTION,
            rail_ly,
            cfg.SEAT_SIDE_RAIL_HEIGHT,
            (side * cfg.SEAT_SIDE_RAIL_X, cfg.SEAT_RAIL_CENTER_Y, cfg.SEAT_SIDE_RAIL_Z),
        )
        results.append(
            _element(
                f"seat.side.rail.{name}",
                f"Side Seat Rail ({name})",
                "seat",
                geometry,
                cfg.BACK_RAIL_SECTION,
                rail_ly,
                cfg.SEAT_SIDE_RAIL_HEIGHT,
            )
        )
    return results


def _armrests() -> list[DesignElement]:
    """Two long broad flat armrest planks projecting beyond the front posts."""
    arm_z = cfg.ARM_HEIGHT - cfg.ARM_THICKNESS / 2
    results = []
    for side, name in ((-1, "left"), (1, "right")):
        center_x = side * (cfg.ARM_X_OUTER - cfg.ARM_WIDTH / 2)
        geometry = _plain_box(cfg.ARM_WIDTH, cfg.ARM_LENGTH, cfg.ARM_THICKNESS, (center_x, cfg.ARM_CENTER_Y, arm_z))
        results.append(
            _element(
                f"armrest.{name}",
                f"Armrest ({name})",
                "arm",
                geometry,
                cfg.ARM_WIDTH,
                cfg.ARM_LENGTH,
                cfg.ARM_THICKNESS,
            )
        )
    return results


def _front_posts() -> list[DesignElement]:
    """Two front posts rising from the floor to the arm undersides at the front corners."""
    post_height = cfg.ARM_HEIGHT - cfg.ARM_THICKNESS
    results = []
    for side, name in ((-1, "left"), (1, "right")):
        geometry = _plain_box(
            cfg.FRONT_POST_THICKNESS,
            cfg.FRONT_POST_WIDTH,
            post_height,
            (side * cfg.FRONT_POST_X, cfg.FRONT_POST_Y, post_height / 2),
        )
        results.append(
            _element(
                f"front.post.{name}",
                f"Front Post ({name})",
                "structure",
                geometry,
                cfg.FRONT_POST_THICKNESS,
                cfg.FRONT_POST_WIDTH,
                post_height,
            )
        )
    return results


def _arm_brackets() -> list[DesignElement]:
    """Two gusset plates under the arms near the front posts, with a tapered lower profile.

    The tapered profile is swept in the default XY plane (local x = world Z,
    local y = world Y) and then rotated about Y into the vertical arm plane so
    its thin dimension lines up with world X under the armrest.
    """
    results = []
    for sign, name in ((-1, "left"), (1, "right")):
        face = make_face(
            Polyline(
                [
                    (cfg.BRACKET_Z_TOP, cfg.BRACKET_Y_FRONT),
                    (cfg.BRACKET_Z_TOP, cfg.BRACKET_Y_REAR),
                    (cfg.BRACKET_Z_REAR_BOT, cfg.BRACKET_Y_REAR),
                    (cfg.BRACKET_Z_FRONT_BOT, cfg.BRACKET_Y_FRONT),
                ],
                close=True,
            )
        )
        part = extrude(face, amount=cfg.ARM_BRACKET_THICKNESS)
        part = part.rotate(Axis.Y, -90)
        geometry = part.moved(Location((sign * cfg.ARM_BRACKET_X + cfg.ARM_BRACKET_THICKNESS / 2, 0, 0))).solid()
        results.append(
            _element(
                f"arm.bracket.{name}",
                f"Arm Bracket ({name})",
                "bracket",
                geometry,
                cfg.ARM_BRACKET_THICKNESS,
                cfg.BRACKET_Y_REAR - cfg.BRACKET_Y_FRONT,
                cfg.BRACKET_Z_TOP - cfg.BRACKET_Z_FRONT_BOT,
            )
        )
    return results


def _front_apron() -> DesignElement:
    """One broad horizontal front apron spanning between the front posts."""
    geometry = _plain_box(cfg.APRON_WIDTH_X, cfg.APRON_DEPTH_Y, cfg.APRON_HEIGHT_Z, (0.0, cfg.APRON_Y, cfg.APRON_Z))
    return _element(
        "front.apron",
        "Front Apron",
        "fascia",
        geometry,
        cfg.APRON_WIDTH_X,
        cfg.APRON_DEPTH_Y,
        cfg.APRON_HEIGHT_Z,
    )


def _rear_legs() -> list[DesignElement]:
    """Two rear legs whose feet splay backward from the rear seat frame.

    The leg is a vertical box rotated about X so its bottom foot lands rearward
    of its top, giving the backward splay of the reference.
    """
    dy = cfg.REAR_LEG_FOOT_Y - cfg.REAR_LEG_TOP_Y
    leg_angle = math.degrees(math.atan2(dy, cfg.REAR_LEG_TOP_Z))
    leg_length = math.hypot(dy, cfg.REAR_LEG_TOP_Z)
    center = (0.0, (cfg.REAR_LEG_TOP_Y + cfg.REAR_LEG_FOOT_Y) / 2, cfg.REAR_LEG_TOP_Z / 2)
    results = []
    for sign, name in ((-1, "left"), (1, "right")):
        geometry = _lean_box(
            cfg.REAR_LEG_THICKNESS_X,
            cfg.REAR_LEG_DEPTH_Y,
            leg_length,
            leg_angle,
            (sign * cfg.REAR_LEG_X, center[1], center[2]),
        )
        results.append(
            _element(
                f"rear.leg.{name}",
                f"Rear Leg ({name})",
                "structure",
                geometry,
                cfg.REAR_LEG_THICKNESS_X,
                cfg.REAR_LEG_DEPTH_Y,
                leg_length,
            )
        )
    return results


def _lower_brace() -> DesignElement:
    """One narrow horizontal brace joining the rear legs low beneath the seat."""
    geometry = _plain_box(cfg.BRACE_WIDTH_X, cfg.BRACE_DEPTH_Y, cfg.BRACE_HEIGHT_Z, (0.0, cfg.BRACE_Y, cfg.BRACE_Z))
    return _element(
        "lower.brace",
        "Lower Rear Brace",
        "structure",
        geometry,
        cfg.BRACE_WIDTH_X,
        cfg.BRACE_DEPTH_Y,
        cfg.BRACE_HEIGHT_Z,
    )


def _foot_slats() -> list[DesignElement]:
    """Four transverse cedar top slats of the front footrest spanning X."""
    pitch = cfg.FOOT_SLAT_DEPTH + cfg.FOOT_SLAT_GAP
    top_z = cfg.FOOTREST_HEIGHT_Z - cfg.BOARD_THICKNESS / 2
    elements = []
    for index in range(cfg.FOOT_SLAT_COUNT):
        center_y = cfg.FOOT_SLAT_START_Y + index * pitch
        geometry = _plain_box(
            cfg.FOOTREST_WIDTH_X,
            cfg.FOOT_SLAT_DEPTH,
            cfg.BOARD_THICKNESS,
            (0.0, center_y, top_z),
        )
        elements.append(
            _element(
                f"footrest.slat.{index + 1}",
                f"Footrest Slat {index + 1}",
                "footrest",
                geometry,
                cfg.FOOTREST_WIDTH_X,
                cfg.FOOT_SLAT_DEPTH,
                cfg.BOARD_THICKNESS,
            )
        )
    return elements


def _foot_legs() -> list[DesignElement]:
    """Four splayed legs rising from the ground to just under the footrest top.

    Each leg is a vertical box rotated about Y so the foot splays outward in X
    from its top, and the top end sits just beneath the slatted top.
    """
    dx = cfg.FOOT_LEG_FOOT_SPLAY_X
    height = cfg.FOOT_LEG_Z_UNDER
    leg_angle = math.degrees(math.atan2(dx, height))
    leg_length = math.hypot(dx, height)
    results = []
    for side, side_name in ((-1, "left"), (1, "right")):
        # Positive splay_deg sends the foot toward -X; foot outward means the
        # right legs use the negative angle and the left legs the positive one.
        splay_deg = -side * leg_angle
        center_x = side * (cfg.FOOT_LEG_TOP_X + dx / 2)
        for y, y_name in ((cfg.FOOT_LEG_Y_REAR, "rear"), (cfg.FOOT_LEG_Y_FRONT, "front")):
            geometry = _splay_box(
                cfg.FOOT_LEG_SECTION,
                cfg.FOOT_LEG_SECTION,
                leg_length,
                splay_deg,
                (center_x, y, height / 2),
            )
            results.append(
                _element(
                    f"footrest.leg.{y_name}.{side_name}",
                    f"Footrest Leg ({y_name}, {side_name})",
                    "footrest support",
                    geometry,
                    cfg.FOOT_LEG_SECTION,
                    cfg.FOOT_LEG_SECTION,
                    leg_length,
                )
            )
    return results


def build_model(context: BuildContext) -> DesignModel:
    """Compose the single white-painted cedar Adirondack armchair ``DesignModel``."""

    del context
    elements: list[DesignElement] = []
    elements.extend(_back_boards())
    elements.extend(_back_support_rails())
    elements.extend(_seat_slats())
    elements.extend(_side_seat_rails())
    elements.extend(_armrests())
    elements.extend(_front_posts())
    elements.extend(_arm_brackets())
    elements.append(_front_apron())
    elements.extend(_rear_legs())
    elements.append(_lower_brace())

    # Matching low footrest, appended after the chair parts and painted the
    # same white finish as the chair.
    elements.extend(_foot_slats())
    elements.extend(_foot_legs())

    return DesignModel(
        id="deck.adirondack.chair",
        name=cfg.PROJECT_NAME,
        artifact_stem="deck-adirondack-chair",
        elements=elements,
        metadata={
            "design": "white-painted cedar Adirondack armchair",
            "authoring_note": "Painted cedar solids assembled in world coordinates.",
        },
    )
