#!/usr/bin/env python3
"""
Example: assemble pre-rendered PNGs into a self-contained SVG pathway diagram.

Prerequisites:
  1. Render molecule PNGs using basic_render.py (or batch_render)
  2. Place them in a directory (e.g. ./pngs/)
  3. Run this script to generate the pathway SVG

Usage:
    python examples/pathway_demo.py
"""

from smiles_to_3d.pathway import PathwaySpec, generate_pathway_svg


def main():
    # Define the pathway topology
    # This is a simplified HMF → Formaldehyde pathway (3 nodes + 2 side fragments)
    spec = PathwaySpec(
        name="HMF → Formaldehyde Pathway",
        main_chain=[
            "HMF",               # Node 0
            "C3H5O2",            # Node 1
            "CH2O",              # Node 2 (formaldehyde)
        ],
        side_fragments=[
            ("C3HO", 0, "C₃HO"),  # (png_key, attach_to_node_index, label)
            ("C2H3O", 1, "C₂H₃O"),
        ],
        viewbox=(0, 0, 1100, 430),
        main_labels={
            "HMF": "HMF",
            "C3H5O2": "C₃H₅O₂",
            "CH2O": "CH₂O",
        },
        arrow_annotations={
            0: "+C₃HO",
            1: "+C₂H₃O",
        },
    )

    output_path = "./output/pathway_demo.svg"
    print(f"Generating pathway SVG...")
    print(f"  Looking for PNGs in: ./pngs/")
    print(f"  Expected PNG files: HMF_bond1.2.png, C3H5O2_bond1.2.png, etc.")

    try:
        result = generate_pathway_svg("./pngs/", spec, output_path)
        print(f"  ✓ {result}")
    except FileNotFoundError as e:
        print(f"  ⚠ {e}")
        print()
        print("  To use this example, first render the molecules:")
        print("    1. Create a ./pngs/ directory")
        print("    2. Render molecules with basic_render.py")
        print("    3. Rename PNGs to match the keys above (strip _bond1.2 suffix)")


if __name__ == "__main__":
    import os
    os.makedirs("./output", exist_ok=True)
    main()
