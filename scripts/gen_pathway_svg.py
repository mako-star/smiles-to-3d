#!/usr/bin/env python3
"""
Generate pure SVG pathway diagrams from pre-rendered 3D molecule PNGs.
Self-contained, publication-ready, no external dependencies.

Workflow:
  1. Render all molecules with batch_render.py → PNGs in a directory
  2. Define pathway topology (PathwaySpec)
  3. Run this script to assemble SVG

This script is the reference implementation that produced the HMF pathway
figures for the user's publication. It supports linear and Y-split topologies.

Usage:
    python scripts/gen_pathway_svg.py --pathway formaldehyde
    python scripts/gen_pathway_svg.py --all
"""

import os
import sys
import argparse
from smiles_to_3d.pathway import (
    PathwaySpec, generate_pathway_svg, load_pngs, SVGBuilder,
    PathwayLayout,
)


# ── Preset Pathway Definitions ────────────────────────────────────────────
# These are the specific HMF degradation pathways.
# Replace with your own definitions.

PRESETS = {
    "formaldehyde": PathwaySpec(
        name="HMF → Formaldehyde",
        main_chain=["HMF_S1350", "C3H5O2_S3400", "CH2O_S596"],
        side_fragments=[
            ("C3HO_S3573", 0, "C₃HO"),
            ("C2H3O_S2044", 1, "C₂H₃O"),
        ],
        viewbox=(0, 0, 1100, 430),
        main_labels={
            "HMF_S1350": "HMF",
            "C3H5O2_S3400": "C₃H₅O₂",
            "CH2O_S596": "CH₂O",
        },
        arrow_annotations={0: "+C₃HO", 1: "+C₂H₃O"},
    ),
    "glycolaldehyde": PathwaySpec(
        name="HMF → Glycolaldehyde-like",
        main_chain=[
            "HMF_S1350", "C3H5O2_S3400", "C2H3O_S2044", "C2H4O2_S2012"
        ],
        side_fragments=[
            ("C3HO_S3573", 0, "C₃HO"),
            ("CH2O_S596", 1, "CH₂O"),
        ],
        viewbox=(0, 0, 1500, 600),
        main_labels={
            "HMF_S1350": "HMF",
            "C3H5O2_S3400": "C₃H₅O₂",
            "C2H3O_S2044": "C₂H₃O",
            "C2H4O2_S2012": "C₂H₄O₂",
        },
        arrow_annotations={0: "+C₃HO", 1: "+CH₂O", 2: "+HO·"},
    ),
    "hydroxyacetone": PathwaySpec(
        name="HMF → Hydroxyacetone-like",
        main_chain=[
            "HMF_S1350", "C3H5O2_S3400", "CH2O_S596",
            "CH3O_S3359", "C3H6O2_S2140",
        ],
        side_fragments=[
            ("C3HO_S3573", 0, "C₃HO"),
            ("C2H3O_S2044", 2, "C₂H₃O"),
            ("H_S3830", 3, "H·"),
        ],
        viewbox=(0, 0, 1700, 600),
        main_labels={
            "HMF_S1350": "HMF",
            "C3H5O2_S3400": "C₃H₅O₂",
            "CH2O_S596": "CH₂O",
            "CH3O_S3359": "CH₃O",
            "C3H6O2_S2140": "C₃H₆O₂",
        },
        arrow_annotations={0: "+C₃HO", 2: "+H·", 3: "+C₂H₃O"},
        note="⚠ Convergent topology: CH₃O from CH₂O+H·; C₃H₆O₂ from C₂H₃O+CH₃O",
    ),
    "cellulose": PathwaySpec(
        name="Cellulose → HMF (Y-split)",
        main_chain=[
            "C12H22O11", "C6H11O6", "C6H11O5",
            "C6H10O5", "HO", "H",
        ],
        side_fragments=[],
        viewbox=(0, 0, 1200, 750),
        main_labels={
            "C12H22O11": "C₁₂H₂₂O₁₁",
            "C6H11O6": "C₆H₁₁O₆",
            "C6H11O5": "C₆H₁₁O₅",
            "C6H10O5": "LG (C₆H₁₀O₅)",
            "HO": "HO·",
            "H": "H·",
        },
        note="Cellulose → HMF pathway (simplified Y-split topology)",
    ),
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate SVG pathway diagrams from pre-rendered PNGs"
    )
    parser.add_argument("--all", action="store_true",
                        help="Generate all preset pathways")
    parser.add_argument("--pathway", choices=list(PRESETS.keys()),
                        help="Generate a specific preset pathway")
    parser.add_argument("--png-dir", default="./pngs/",
                        help="Directory containing PNG files")
    parser.add_argument("--out-dir", default="./output/",
                        help="Output directory for SVG files")
    parser.add_argument("--list", action="store_true",
                        help="List available preset pathways")
    args = parser.parse_args()

    if args.list:
        print("Available presets:")
        for name, spec in PRESETS.items():
            nodes = len(spec.main_chain)
            sides = len(spec.side_fragments)
            print(f"  {name:20s}  {nodes} nodes + {sides} side fragments")
        return

    if not args.all and not args.pathway:
        parser.print_help()
        sys.exit(1)

    os.makedirs(args.out_dir, exist_ok=True)

    targets = list(PRESETS.keys()) if args.all else [args.pathway]

    for key in targets:
        spec = PRESETS[key]
        out_name = f"pathway_{key}.svg"
        out_path = os.path.join(args.out_dir, out_name)

        print(f"\n{'='*60}")
        print(f"  {spec.name}  ({key})")
        print(f"  Loading PNGs from: {args.png_dir}")

        try:
            result = generate_pathway_svg(args.png_dir, spec, out_path)
            size_kb = os.path.getsize(result) / 1024
            print(f"  ✅ {result}  ({size_kb:.0f} KB)")
        except Exception as e:
            print(f"  ❌ {e}")

    print(f"\nDone. Output in: {args.out_dir}")


if __name__ == "__main__":
    main()
