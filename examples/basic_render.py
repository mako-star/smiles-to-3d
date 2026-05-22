#!/usr/bin/env python3
"""
Simple example: render a single SMILES string to a 3D ball-and-stick PNG.

Usage:
    python examples/basic_render.py
"""

from smiles_to_3d.render import smiles_to_png, RenderConfig

def main():
    # Configure rendering
    config = RenderConfig(
        width=2400,
        height=1800,
        dpi=300,
        bond_scale=1.2,
    )

    # Render a few example molecules
    molecules = [
        ("HMF", "OCc1ccc(C=O)o1"),
        ("Levoglucosan", "C1[C@@H]2[C@H]([C@@H]([C@H]([C@H](O1)O2)O)O)O"),
        ("Formaldehyde", "C=O"),
    ]

    for name, smiles in molecules:
        print(f"Rendering {name} ({smiles})...")
        try:
            result = smiles_to_png(
                smiles,
                output_path=f"./output/{name}.png",
                config=config,
                keep_sdf=False,
            )
            print(f"  ✓ {result['png']}")
        except Exception as e:
            print(f"  ✗ Failed: {e}")

    print("\nDone. Check the ./output/ directory.")


if __name__ == "__main__":
    import os
    os.makedirs("./output", exist_ok=True)
    main()
