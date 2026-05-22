"""
smiles-to-3d: SMILES → 3D Molecular Structure Rendering & Pathway Diagram Toolkit

Convert SMILES strings to publication-quality 3D molecular structure images,
then assemble them into annotated reaction pathway diagrams (SVG / PNG / PPTX).

Core workflow:
  1. SMILES → 3D SDF  (RDKit: EmbedMolecule + MMFF optimization)
  2. 3D SDF → PNG      (PyMOL: orthographic, 2400×1800 @ 300 DPI, ball+stick)
  3. PNGs → SVG        (pure SVG: base64-embedded, Style 11/D5 arrows)

Quick start:
    >>> from smiles_to_3d import smiles_to_png
    >>> result = smiles_to_png("OCc1ccc(C=O)o1", "hmf.png")

    >>> from smiles_to_3d import PathwaySpec, generate_pathway_svg
    >>> spec = PathwaySpec(
    ...     name="My Pathway",
    ...     main_chain=["HMF", "CH2O"],
    ...     viewbox=(0, 0, 800, 400),
    ...     main_labels={"HMF": "HMF", "CH2O": "CH₂O"},
    ... )
    >>> generate_pathway_svg("./pngs/", spec, "pathway.svg")
"""

__version__ = "1.0.0"
__author__ = "mako-star"

# Public API — render pipeline
from smiles_to_3d.render import (
    smiles_to_png,
    smiles_to_sdf,
    sdf_to_png,
    batch_render,
    RenderConfig,
)

# Public API — pathway assembly
from smiles_to_3d.pathway import (
    generate_pathway_svg,
    PathwaySpec,
    SVGBuilder,
    load_pngs,
)
