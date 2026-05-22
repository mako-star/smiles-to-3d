"""
Matplotlib Pathway Diagram Composer
====================================
Alternative pipeline: assemble pre-rendered PNGs into pathway diagrams using
Matplotlib (output: PNG/PDF/SVG). Good for batch automation and data-figure
style output.

Usage:
    python -m smiles_to_3d.pathway_mpl spec.yaml --img-dir ./pngs/ --output pathway.pdf

Spec format (YAML):
    main_chain:
      - id: HMF
        png: HMF_S1350_bond1.2.png
        label: "C₆H₆O₃"
        label_cn: "羟甲基糠醛"
        arrow_label: "+H·"
      - id: Intermediate
        png: intermediate.png
        label: "C₃H₅O₂"
    side_fragments:
      - id: C3HO
        png: C3HO_bond1.2.png
        label: "C₃HO"
        attach_to: 0
"""

import argparse
import os
import yaml
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

# ── Default styling ────────────────────────────────────────────────────────

DEFAULTS = {
    "dpi": 300,
    "bg": "#ffffff",
    "main_h_px": 130,
    "side_h_px": 80,
    "arrow_gap": 30,
    "margin_x": 60,
    "main_y": 180,
    "label_dy": 8,
    "side_y_gap": 60,
    "side_row_h": 110,
    "font_main": None,       # Will auto-detect Times New Roman
    "font_cjk": None,        # For Chinese labels (Noto Sans SC)
}

SOLID_COLOR = "#2c2c2c"
DASHED_COLOR = "#888888"
TEXT_COLOR = "#111111"
SUBTEXT_COLOR = "#666666"


def _find_font(font_paths: list, fallback_name: str = "serif"):
    """Try each font path; return the first that exists on disk."""
    for p in font_paths:
        if p and os.path.exists(p):
            return p
    return fallback_name


def load_spec(spec_path: str) -> dict:
    """Load a YAML pathway spec."""
    with open(spec_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def compute_layout(spec: dict, img_dir: str):
    """Compute pixel positions for all nodes and arrows."""
    main_chain = spec["main_chain"]
    side_fragments = spec.get("side_fragments", [])
    dpi = spec.get("canvas", {}).get("dpi", DEFAULTS["dpi"])

    # Read first image to get native resolution
    sample = os.path.join(img_dir, main_chain[0]["png"])
    orig_w, orig_h = Image.open(sample).size

    scale_main = DEFAULTS["main_h_px"] / orig_h
    main_w = int(orig_w * scale_main)
    main_h = DEFAULTS["main_h_px"]

    scale_side = DEFAULTS["side_h_px"] / orig_h
    side_w = int(orig_w * scale_side)
    side_h = DEFAULTS["side_h_px"]

    n = len(main_chain)

    # Horizontal spacing
    arrow_slot = main_w + DEFAULTS["arrow_gap"] * 2 + 40
    gap_x = max(arrow_slot, 180)

    total_w = DEFAULTS["margin_x"] * 2 + n * main_w + (n - 1) * gap_x
    canvas_h = (
        DEFAULTS["main_y"] + main_h + DEFAULTS["label_dy"] + 20
        + DEFAULTS["side_y_gap"] + DEFAULTS["side_row_h"] + 40
    )

    # Main chain nodes
    nodes = []
    for i, node in enumerate(main_chain):
        x = DEFAULTS["margin_x"] + i * (main_w + gap_x)
        cx = x + main_w // 2
        cy = DEFAULTS["main_y"] + main_h // 2
        nodes.append({
            "id": node["id"],
            "png": node["png"],
            "label": node.get("label", ""),
            "label_cn": node.get("label_cn", ""),
            "arrow_label": node.get("arrow_label", ""),
            "role": "main",
            "x": x, "y": DEFAULTS["main_y"],
            "w": main_w, "h": main_h,
            "cx": cx, "cy": cy,
            "node_idx": i,
        })

    # Side fragments (group by attach_to)
    from collections import defaultdict
    groups = defaultdict(list)
    for sf in side_fragments:
        groups[sf.get("attach_to", 0)].append(sf)

    side_nodes = []
    side_arrows = []

    for attach_idx, fragments in groups.items():
        if attach_idx >= n:
            continue
        parent = nodes[attach_idx]
        for j, sf in enumerate(fragments):
            ox = parent["x"] + parent["w"] + DEFAULTS["arrow_gap"] + 20 + j * (side_w + 30)
            oy = DEFAULTS["main_y"] - side_h // 2 - 10
            sx = ox + side_w // 2
            sy = oy + side_h // 2

            side_nodes.append({
                "id": sf["id"],
                "png": sf["png"],
                "label": sf.get("label", ""),
                "arrow_label": sf.get("arrow_label", ""),
                "role": "side",
                "x": ox, "y": oy,
                "w": side_w, "h": side_h,
                "cx": sx, "cy": sy,
                "attach_to": attach_idx,
            })

            side_arrows.append({
                "type": "dashed",
                "sx": parent["x"] + parent["w"] + 2,
                "sy": parent["cy"],
                "tx": ox - 2,
                "ty": sy,
                "label": sf.get("arrow_label", ""),
            })

    # Main chain arrows
    main_arrows = []
    for i in range(n - 1):
        L = nodes[i]
        R = nodes[i + 1]
        main_arrows.append({
            "type": "solid",
            "sx": L["x"] + L["w"] + 2,
            "sy": L["cy"],
            "tx": R["x"] - 2,
            "ty": R["cy"],
            "label": L.get("arrow_label", ""),
        })

    all_nodes = nodes + side_nodes
    arrows = main_arrows + side_arrows

    return all_nodes, arrows, int(total_w), int(canvas_h)


def render_pathway(spec: dict, img_dir: str, output_path: str) -> str:
    """Main rendering function."""
    canvas = spec.get("canvas", {})
    dpi = canvas.get("dpi", DEFAULTS["dpi"])
    bg = canvas.get("bg", DEFAULTS["bg"])

    nodes, arrows, cw, ch = compute_layout(spec, img_dir)

    # Convert px → inches
    fig_w = cw / dpi
    fig_h = ch / dpi

    # Font setup
    font_paths = [
        "/home/gakki/.fonts/times.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",
        "/mnt/c/Windows/Fonts/times.ttf",
    ]

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, cw)
    ax.set_ylim(ch, 0)  # y=0 at top
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    # Background
    ax.add_patch(Rectangle((0, 0), cw, ch, color=bg, zorder=0))

    # Draw nodes
    for node in nodes:
        img_path = os.path.join(img_dir, node["png"])
        if not os.path.exists(img_path):
            print(f"  ⚠ Missing: {img_path}")
            continue
        img_arr = np.array(Image.open(img_path).convert("RGBA"))
        ax.imshow(img_arr,
            extent=[node["x"], node["x"] + node["w"],
                    node["y"], node["y"] + node["h"]],
            aspect="auto", zorder=5)

        cx = node["cx"]
        if node["role"] == "main":
            ax.text(cx, node["y"] - 8, node["label"],
                ha="center", va="bottom",
                fontsize=13, color=TEXT_COLOR, zorder=6)
        else:
            ax.text(cx, node["y"] + node["h"] + 5, node["label"],
                ha="center", va="bottom",
                fontsize=11, color=TEXT_COLOR, zorder=6)

    # Draw arrows
    for arrow in arrows:
        if arrow["type"] == "solid":
            ax.annotate("",
                xy=(arrow["tx"], arrow["ty"]),
                xytext=(arrow["sx"], arrow["sy"]),
                arrowprops=dict(
                    arrowstyle="-|>", color=SOLID_COLOR,
                    lw=1.6, shrinkA=0, shrinkB=0, mutation_scale=14,
                ), zorder=10)
            lbl = arrow.get("label", "")
            if lbl:
                ax.text((arrow["sx"] + arrow["tx"]) / 2, arrow["sy"] - 13,
                    lbl, ha="center", va="top",
                    fontsize=11, color="#444444", zorder=11)
        else:
            rad = 0.25
            arr = FancyArrowPatch(
                posA=(arrow["sx"], arrow["sy"]),
                posB=(arrow["tx"], arrow["ty"]),
                connectionstyle=f"arc3,rad={rad}",
                arrowstyle="-|>", mutation_scale=12,
                color=DASHED_COLOR, lw=1.4, linestyle="--",
                shrinkA=0, shrinkB=0, zorder=9,
            )
            ax.add_patch(arr)

    # Save
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight",
                facecolor=bg, edgecolor="none")
    plt.close(fig)

    print(f"✓ Saved: {output_path}  ({cw}×{ch} px @ {dpi} dpi)")
    return output_path


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Compose molecular pathway diagrams (Matplotlib)"
    )
    parser.add_argument("spec", help="YAML topology spec file")
    parser.add_argument("--img-dir", "-i", required=True,
                        help="Directory containing molecular PNG images")
    parser.add_argument("--output", "-o", required=True,
                        help="Output file (PNG/PDF/SVG)")
    parser.add_argument("--dpi", "-d", type=int, default=300)
    args = parser.parse_args()

    spec = load_spec(args.spec)
    spec.setdefault("canvas", {})["dpi"] = args.dpi
    render_pathway(spec, args.img_dir, args.output)


if __name__ == "__main__":
    main()
