#!/usr/bin/env python3
"""
Batch render: render multiple SMILES strings to 3D PNGs in one run.

Define your molecule list below, then run:
    python scripts/batch_render.py

Requirements:
    pip install rdkit
    PyMOL must be installed and available on PATH
"""

import os
import sys
from smiles_to_3d.render import batch_render, RenderConfig

# ── Define your molecules here ────────────────────────────────────────────
MOLECULES = [
    {"name": "HMF_S1350",      "smiles": "OCc1ccc(C=O)o1"},
    {"name": "C3H5O2_S3400",   "smiles": "[CH2]OC=CO"},
    {"name": "C3HO_S3573",     "smiles": "[CH]=C1[C]O1"},
    {"name": "C2H3O_S2044",    "smiles": "OC=[CH]"},
    {"name": "CH2O_S596",      "smiles": "C=O"},
    {"name": "HO_S3832",       "smiles": "[OH]"},
    {"name": "C2H4O2_S2012",   "smiles": "OC=CO"},
    {"name": "H_S3830",        "smiles": "[H]"},
    {"name": "CH3O_S3359",     "smiles": "[CH2]O"},
    {"name": "C3H6O2_S2140",   "smiles": "OCC=CO"},
]

OUTPUT_DIR = "./pngs"

# ── Rendering configuration ────────────────────────────────────────────────
CONFIG = RenderConfig(
    width=2400,
    height=1800,
    dpi=300,
    bond_scale=1.2,
    stick_radius=0.13,
    sphere_scale=0.25,
    orthographic=True,
    carbon_color="gray55",
    oxygen_color="red",
    hydrogen_color="white",
)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Batch rendering {len(MOLECULES)} molecules...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    results = batch_render(MOLECULES, OUTPUT_DIR, CONFIG)

    success = sum(1 for r in results if r["success"])
    failed = len(results) - success

    print(f"\n{'─'*50}")
    print(f"Results: {success} succeeded, {failed} failed")
    print()

    for r in results:
        status = "✅" if r["success"] else "❌"
        name = r["name"]
        if r["success"]:
            size_kb = os.path.getsize(r["png"]) / 1024
            print(f"  {status} {name:20s}  {size_kb:6.0f} KB  {r['png']}")
        else:
            print(f"  {status} {name:20s}  Error: {r.get('error', 'unknown')}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
