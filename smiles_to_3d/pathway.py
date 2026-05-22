"""
Pure SVG Reaction Pathway Diagram Generator
===========================================
Assembles pre-rendered 3D molecular structure PNGs into publication-quality
reaction pathway diagrams as self-contained SVG files.

Features:
  - Pure SVG output (no HTML wrapper) — directly embeddable in LaTeX
  - Base64-embedded images — fully self-contained, no external dependencies
  - Times New Roman typography — academic standard
  - Style 11 solid arrows + D5 dashed arrows — user-selected from arrow gallery
  - Layered structure (<g> groups): molecules, arrows, labels, annotations
  - Editable in Inkscape / Adobe Illustrator

Arrow conventions:
  - Solid arrows: linear reaction steps (style 11 chevron)
  - Dashed arrows (D5): fragmentation byproducts (S-curve bezier)
    Tail → source molecule, Head → fragment product
"""

import os
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass


# ── SVG Arrow Markers ──────────────────────────────────────────────────────

ARROW_STYLE_11 = """\
    <marker id="arrow-solid" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto">
      <polyline points="0,1.5 6,4.5 0,7.5" fill="none"
                stroke="#2c2c2c" stroke-width="1.6"
                stroke-linecap="round" stroke-linejoin="round"/>
    </marker>"""

ARROW_STYLE_D5 = """\
    <marker id="arrow-dashed" viewBox="0 0 10 10" refX="9" refY="5"
            markerWidth="7" markerHeight="7" orient="auto">
      <polyline points="0,1.5 6,4.5 0,7.5" fill="none"
                stroke="#aaaaaa" stroke-width="1.6"
                stroke-linecap="round" stroke-linejoin="round"/>
    </marker>"""


# ── SVG Builder ───────────────────────────────────────────────────────────

class SVGBuilder:
    """Build SVG documents programmatically."""

    def __init__(self, width: int, height: int, view_box: str = None):
        self.width = width
        self.height = height
        self.view_box = view_box or f"0 0 {width} {height}"
        self._defs: List[str] = [
            ARROW_STYLE_11,
            ARROW_STYLE_D5,
        ]
        self._groups: Dict[str, List[str]] = {
            "background": [],
            "molecules": [],
            "arrows": [],
            "labels": [],
            "annotations": [],
        }

    def add_def(self, element: str):
        self._defs.append(element)

    def add_to(self, group: str, element: str):
        if group not in self._groups:
            self._groups[group] = []
        self._groups[group].append(element)

    def add_image(self, x: float, y: float, w: float, h: float,
                  b64_data: str):
        """Add a base64-embedded PNG image."""
        el = (
            f'    <image x="{x}" y="{y}" width="{w}" height="{h}"\n'
            f'           xlink:href="data:image/png;base64,{b64_data}"/>'
        )
        self._groups["molecules"].append(el)

    def add_text(self, x: float, y: float, text: str,
                 size: int = 16, anchor: str = "middle",
                 italic: bool = True, color: str = "#1a1a1a"):
        """Add a text label."""
        fs = ' font-style="italic"' if italic else ""
        el = (
            f'    <text x="{x}" y="{y}" '
            f'font-family="Times New Roman, serif" '
            f'font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}"{fs}>{text}</text>'
        )
        if size <= 13:
            self._groups["annotations"].append(el)
        else:
            self._groups["labels"].append(el)

    def add_solid_arrow(self, x1: float, y1: float, x2: float, y2: float):
        """Add a solid reaction arrow (style 11)."""
        el = (
            f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="#2c2c2c" stroke-width="1.6" '
            f'marker-end="url(#arrow-solid)"/>'
        )
        self._groups["arrows"].append(el)

    def add_dashed_arrow(self, path_d: str, dash: str = "6,4"):
        """Add a dashed S-curve arrow (style D5)."""
        el = (
            f'    <path d="{path_d}" stroke="#aaaaaa" stroke-width="1.6" '
            f'stroke-dasharray="{dash}" fill="none" '
            f'marker-end="url(#arrow-dashed)"/>'
        )
        self._groups["arrows"].append(el)

    def add_annotation(self, x: float, y: float, text: str,
                       size: int = 13, color: str = "#555555"):
        """Add reaction annotation (e.g. '+HO·' above arrow)."""
        el = (
            f'    <text x="{x}" y="{y}" '
            f'font-family="Times New Roman, serif" '
            f'font-size="{size}" fill="{color}" '
            f'text-anchor="middle" font-style="italic">{text}</text>'
        )
        self._groups["annotations"].append(el)

    def to_svg(self) -> str:
        """Render the complete SVG document."""
        parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'xmlns:xlink="http://www.w3.org/1999/xlink"',
            f'     viewBox="{self.view_box}" width="{self.width}" '
            f'height="{self.height}">',
            '',
            '  <defs>',
        ]
        for d in self._defs:
            parts.append(d)
        parts.append('  </defs>')
        parts.append('')

        # Background
        parts.append(f'  <rect width="{self.width}" height="{self.height}" fill="white"/>')
        parts.append('')

        # Group layers in order
        group_order = ["molecules", "arrows", "labels", "annotations"]
        for gid in group_order:
            if self._groups.get(gid):
                parts.append(f'  <g id="{gid}">')
                for el in self._groups[gid]:
                    parts.append(el)
                parts.append('  </g>')
                parts.append('')

        parts.append('</svg>')
        return '\n'.join(parts)


# ── PNG Loader ────────────────────────────────────────────────────────────

def load_pngs(directory: str, suffix: str = "_bond1.2.png") -> Dict[str, str]:
    """
    Load and base64-encode all PNG files in a directory.

    Args:
        directory: Path to directory containing PNG files
        suffix: Filename suffix to strip from keys

    Returns:
        Dict mapping filename (without suffix) → base64 string
    """
    pngs = {}
    if not os.path.isdir(directory):
        return pngs

    for fn in sorted(os.listdir(directory)):
        if fn.endswith(".png") and not fn.endswith("_hires.png"):
            key = fn.replace(suffix, "")
            filepath = os.path.join(directory, fn)
            with open(filepath, "rb") as f:
                b64str = base64.b64encode(f.read()).decode()
                pngs[key] = b64str

    return pngs


# ── Pathway Layout Spec ───────────────────────────────────────────────────

@dataclass
class PathwaySpec:
    """Specification for a reaction pathway diagram."""
    name: str
    # Main chain nodes: linear sequence of molecules
    main_chain: List[str]   # PNG keys (order matters!)
    # Side fragments: (png_key, attach_to_index, label)
    side_fragments: List[Tuple[str, int, str]] = None
    # Layout geometry
    image_size: int = 150        # Main node image size (px)
    side_image_size: int = 130   # Side fragment image size (px)
    viewbox: Tuple[int, int, int, int] = None  # (x, y, w, h)
    # Labels
    main_labels: Dict[str, str] = None  # png_key → display label
    side_labels: Dict[str, str] = None
    # Annotations (e.g. '+HO·' above arrows)
    arrow_annotations: Dict[int, str] = None  # arrow_index → text
    # Warning note at bottom
    note: str = None

    def __post_init__(self):
        if self.side_fragments is None:
            self.side_fragments = []
        if self.main_labels is None:
            self.main_labels = {}
        if self.side_labels is None:
            self.side_labels = {}
        if self.arrow_annotations is None:
            self.arrow_annotations = {}


# ── Standard Pathway Layouts ──────────────────────────────────────────────

class PathwayLayout:
    """Collection of standard layout algorithms for different topologies."""

    @staticmethod
    def linear_main_chain(
        spec: PathwaySpec,
        builder: SVGBuilder,
        pngs: Dict[str, str],
    ):
        """
        Standard linear main chain layout.
        Nodes → evenly spaced horizontally, arrows between them.
        Side fragments → placed above/below with dashed S-curve arrows.
        """
        n = len(spec.main_chain)
        IMG = spec.image_size
        SIDE = spec.side_image_size

        # Calculate spacing
        arrow_slot = IMG + 40   # Image width + arrow clearance
        gap = max(arrow_slot, 180)

        # Main chain y-position (centered vertically in viewbox)
        vb_h = spec.viewbox[3] if spec.viewbox else 430
        main_y = max(10, (vb_h - IMG) // 2 - 100)

        # Layout main chain nodes
        x_main = [20 + i * (IMG + gap) for i in range(n)]
        arrow_y = main_y + IMG // 2

        # Place molecules
        for i, key in enumerate(spec.main_chain):
            if key not in pngs:
                raise KeyError(f"PNG '{key}' not found. Available: {list(pngs.keys())}")
            builder.add_image(x_main[i], main_y, IMG, IMG, pngs[key])

        # Main chain labels
        for i, key in enumerate(spec.main_chain):
            label = spec.main_labels.get(key, key)
            builder.add_text(x_main[i] + IMG // 2, main_y - 8, label, size=16)

        # Solid arrows between main chain nodes
        for i in range(n - 1):
            x1 = x_main[i] + IMG + 10
            x2 = x_main[i + 1] - 10
            builder.add_solid_arrow(x1, arrow_y, x2, arrow_y)

            # Arrow annotations
            ann = spec.arrow_annotations.get(i, "")
            if ann:
                builder.add_annotation((x1 + x2) // 2, arrow_y - 12, ann, size=13)

        # Side fragments
        for frag_key, attach_idx, label in spec.side_fragments:
            if attach_idx >= n:
                continue
            if frag_key not in pngs:
                continue

            parent_cx = x_main[attach_idx] + IMG // 2
            side_y = main_y + IMG + 60  # Below main chain
            side_x = parent_cx - SIDE // 2

            builder.add_image(side_x, side_y, SIDE, SIDE, pngs[frag_key])
            display_label = spec.side_labels.get(frag_key, label or frag_key)
            builder.add_text(
                side_x + SIDE // 2, side_y - 6,
                display_label, size=14
            )

            # Dashed arrow from parent to fragment
            builder.add_dashed_arrow(
                f"M {parent_cx},{main_y + IMG} "
                f"C {parent_cx + 40},{side_y - 20} "
                f"{side_x + SIDE // 2},{side_y + 10} "
                f"{side_x + SIDE // 2},{side_y - 2}"
            )

        # Note
        if spec.note:
            builder.add_annotation(
                spec.viewbox[2] // 2 if spec.viewbox else 550,
                spec.viewbox[3] - 10 if spec.viewbox else 420,
                spec.note, size=11, color="#999999"
            )

    @staticmethod
    def y_split_topology(
        spec: PathwaySpec,
        builder: SVGBuilder,
        pngs: Dict[str, str],
    ):
        """
        Y-split branching topology (e.g. Cellulose → two intermediates → converge).
        Layout: top centre → split left+right → converge bottom centre.
        """
        raise NotImplementedError(
            "Y-split topology not yet implemented in the public API. "
            "See the gen_pathway_svg.py script for the full implementation."
        )


# ── Main API ──────────────────────────────────────────────────────────────

def generate_pathway_svg(
    png_dir: str,
    spec: PathwaySpec,
    output_path: str,
    layout: str = "linear",
) -> str:
    """
    Generate a self-contained SVG pathway diagram from pre-rendered PNGs.

    Args:
        png_dir: Directory containing pre-rendered molecule PNGs
        spec: Pathway specification (nodes, labels, topology)
        output_path: Where to save the SVG file
        layout: Layout algorithm ('linear' or 'ysplit')

    Returns:
        Path to the generated SVG file

    Example:
        >>> from smiles_to_3d import PathwaySpec, generate_pathway_svg
        >>> spec = PathwaySpec(
        ...     name="HMF → Formaldehyde",
        ...     main_chain=["HMF_S1350", "C3H5O2_S3400", "CH2O_S596"],
        ...     side_fragments=[
        ...         ("C3HO_S3573", 0, "C₃HO"),
        ...         ("C2H3O_S2044", 1, "C₂H₃O"),
        ...     ],
        ...     viewbox=(0, 0, 1100, 430),
        ...     main_labels={
        ...         "HMF_S1350": "HMF",
        ...         "C3H5O2_S3400": "C₃H₅O₂",
        ...         "CH2O_S596": "CH₂O",
        ...     },
        ... )
        >>> generate_pathway_svg("./pngs/", spec, "pathway.svg")
    """
    # Load PNGs
    pngs = load_pngs(png_dir)
    if not pngs:
        raise FileNotFoundError(f"No PNG files found in: {png_dir}")

    # Determine viewbox
    if spec.viewbox:
        vb = spec.viewbox
        w, h = vb[2], vb[3]
        viewbox_str = f"{vb[0]} {vb[1]} {vb[2]} {vb[3]}"
    else:
        w, h = 1100, 430
        viewbox_str = f"0 0 {w} {h}"

    builder = SVGBuilder(w, h, viewbox_str)

    # Route to layout algorithm
    if layout == "linear":
        PathwayLayout.linear_main_chain(spec, builder, pngs)
    elif layout == "ysplit":
        PathwayLayout.y_split_topology(spec, builder, pngs)
    else:
        raise ValueError(f"Unknown layout: {layout}")

    # Write
    svg_content = builder.to_svg()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    return output_path
